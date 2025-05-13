import os
import streamlit as st
import pandas as pd
import tempfile
import time
from pathlib import Path
import re
import subprocess

from utils.indexer import CodebaseIndexer
from utils.searcher import CodebaseSearcher
from utils.visualizer import DependencyVisualizer
from utils.parser import CppParser

# Set page configuration
st.set_page_config(
    page_title="C++ Codebase Search Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'indexer' not in st.session_state:
    st.session_state.indexer = None
if 'searcher' not in st.session_state:
    st.session_state.searcher = None
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = None
if 'indexed' not in st.session_state:
    st.session_state.indexed = False
if 'selected_file' not in st.session_state:
    st.session_state.selected_file = None

def main():
    st.title("C++ Codebase Search Tool")
    
    # Sidebar for project selection and indexing
    with st.sidebar:
        st.header("Project Configuration")
        
        # Project directory selection
        st.subheader("Select Project Directory")
        project_path = st.text_input("Project path", placeholder="/path/to/codebase")
        
        if st.button("Index Codebase", disabled=not project_path):
            with st.spinner("Indexing codebase... This might take a while."):
                try:
                    # Create parser, indexer, searcher, and visualizer
                    parser = CppParser()
                    indexer = CodebaseIndexer(project_path, parser)
                    st.session_state.indexer = indexer
                    
                    # Index the codebase
                    indexer.index_codebase()
                    
                    # Create searcher and visualizer
                    st.session_state.searcher = CodebaseSearcher(indexer)
                    st.session_state.visualizer = DependencyVisualizer(indexer)
                    
                    st.session_state.indexed = True
                    st.success(f"Successfully indexed {len(indexer.files)} files!")
                except Exception as e:
                    st.error(f"Error indexing codebase: {str(e)}")

        # Re-index option
        if st.session_state.indexed:
            if st.button("Re-index Codebase"):
                with st.spinner("Re-indexing codebase..."):
                    st.session_state.indexer.index_codebase()
                    st.success("Codebase re-indexed successfully!")
    
    # Main content area - only show if indexed
    if not st.session_state.indexed:
        st.info("Please select a project directory and index the codebase to begin.")
        return
    
    # Search interface
    st.header("Search")
    
    # Search options
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input("Search Query", placeholder="Enter component name, function, class, etc.")
    
    with col2:
        search_type = st.selectbox(
            "Search Type",
            ["Component", "Function", "Class", "Dependency", "UI Element", "Regex"]
        )
    
    # Additional filters based on search type
    show_filters = st.checkbox("Show advanced filters")
    
    if show_filters:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            file_type_filter = st.multiselect(
                "File Types",
                ["cpp", "h", "hpp", "rtf", "cc", "cxx"],
                default=["cpp", "h", "hpp", "rtf", "cc", "cxx"]
            )
        
        with col2:
            case_sensitive = st.checkbox("Case Sensitive", value=False)
        
        with col3:
            context_lines = st.slider("Context Lines", 0, 10, 3)
    else:
        file_type_filter = ["cpp", "h", "hpp", "rtf", "cc", "cxx"]
        case_sensitive = False
        context_lines = 3
    
    # Execute search when button is clicked
    if st.button("Search", disabled=not search_query):
        with st.spinner("Searching..."):
            try:
                if search_type == "Regex":
                    search_results = st.session_state.searcher.regex_search(
                        search_query, 
                        case_sensitive=case_sensitive,
                        file_types=file_type_filter
                    )
                else:
                    search_results = st.session_state.searcher.search(
                        search_query, 
                        search_type.lower(), 
                        case_sensitive=case_sensitive,
                        file_types=file_type_filter
                    )
                
                # Display results
                if search_results:
                    st.success(f"Found {len(search_results)} results.")
                    
                    # Create results dataframe
                    results_data = []
                    for result in search_results:
                        results_data.append({
                            "File": os.path.relpath(result["file"], project_path),
                            "Line": result.get("line", "N/A"),
                            "Match": result.get("match", ""),
                            "Relevance": round(result.get("relevance", 0), 2),
                            "Full Path": result["file"]
                        })
                    
                    results_df = pd.DataFrame(results_data)
                    
                    # Sort by relevance
                    results_df = results_df.sort_values("Relevance", ascending=False)
                    
                    # Display clickable results
                    st.subheader("Search Results")
                    
                    # Use AgGrid for better table interaction
                    results_table = st.dataframe(
                        results_df[["File", "Line", "Match", "Relevance"]],
                        use_container_width=True,
                        height=300
                    )
                    
                    # File selection
                    selected_indices = st.multiselect(
                        "Select file(s) to view",
                        options=list(range(len(results_df))),
                        format_func=lambda x: f"{results_df.iloc[x]['File']} (Line: {results_df.iloc[x]['Line']})"
                    )
                    
                    if selected_indices:
                        selected_index = selected_indices[0]  # Take the first selected file
                        selected_file = results_df.iloc[selected_index]["Full Path"]
                        selected_line = results_df.iloc[selected_index]["Line"]
                        
                        st.session_state.selected_file = selected_file
                        
                        # Display file content with syntax highlighting
                        display_file_content(selected_file, int(selected_line) if selected_line != "N/A" else 0, context_lines)
                        
                        # Display dependencies and component info if applicable
                        if search_type in ["Component", "Class", "Dependency"]:
                            st.subheader("Dependencies and Relationships")
                            
                            # Generate and display dependency graph
                            if st.session_state.visualizer:
                                graph_html = st.session_state.visualizer.generate_dependency_graph(selected_file)
                                st.components.v1.html(graph_html, height=500)
                                
                                # Show related components
                                related_files = st.session_state.searcher.find_related_components(selected_file)
                                
                                if related_files:
                                    st.subheader("Related Components")
                                    
                                    related_data = []
                                    for related in related_files:
                                        related_data.append({
                                            "File": os.path.relpath(related["file"], project_path),
                                            "Relationship": related["relationship"],
                                            "Full Path": related["file"]
                                        })
                                    
                                    st.dataframe(
                                        pd.DataFrame(related_data)[["File", "Relationship"]],
                                        use_container_width=True
                                    )
                                    
                                    # Usage examples
                                    usage_examples = st.session_state.searcher.find_usage_examples(selected_file)
                                    
                                    if usage_examples:
                                        st.subheader("Usage Examples")
                                        
                                        for i, example in enumerate(usage_examples):
                                            with st.expander(f"Example {i+1} - {os.path.relpath(example['file'], project_path)}"):
                                                st.code(example["code"], language="cpp")
                else:
                    st.warning("No results found. Try a different search query.")
            except Exception as e:
                st.error(f"Error during search: {str(e)}")
                
    # Option to open file in external editor
    if st.session_state.selected_file and os.path.exists(st.session_state.selected_file):
        st.sidebar.subheader("File Actions")
        
        editor_command = st.sidebar.text_input("Editor Command", value="code")
        
        if st.sidebar.button("Open in External Editor"):
            try:
                # Open the file in the specified editor
                subprocess.Popen([editor_command, st.session_state.selected_file])
                st.sidebar.success(f"Opening {os.path.basename(st.session_state.selected_file)} in {editor_command}")
            except Exception as e:
                st.sidebar.error(f"Failed to open file: {str(e)}")

def display_file_content(file_path, line_number=0, context_lines=3):
    """Display file content with syntax highlighting and context lines."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.readlines()
        
        file_extension = os.path.splitext(file_path)[1].lower()
        language = "cpp"  # Default language
        
        if file_extension in ['.h', '.hpp', '.cpp', '.cc', '.cxx']:
            language = "cpp"
        elif file_extension == '.rtf':
            language = "text"
        
        # Determine range of lines to show
        start_line = max(0, line_number - context_lines - 1)
        end_line = min(len(content), line_number + context_lines)
        
        # Show the file name and extract some lines
        st.subheader(f"File Preview: {os.path.basename(file_path)}")
        
        # First show location info
        st.info(f"Showing lines {start_line+1}-{end_line} from {file_path}")
        
        # Extract relevant lines
        code_snippet = ''.join(content[start_line:end_line])
        
        # Display with syntax highlighting
        st.code(code_snippet, language=language)
        
        # Add an option to show the full file
        if st.checkbox("Show Full File"):
            full_content = ''.join(content)
            st.code(full_content, language=language)
            
    except Exception as e:
        st.error(f"Error displaying file content: {str(e)}")

if __name__ == "__main__":
    main()
