import os
import fnmatch
import time
from pathlib import Path
import threading
from typing import List, Dict, Set, Tuple, Any
import re
import hashlib

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CodebaseIndexer:
    """Class for indexing and monitoring a C++ codebase."""
    
    def __init__(self, project_path: str, parser):
        """
        Initialize the indexer with the project path and a parser.
        
        Args:
            project_path: Root directory of the C++ project
            parser: An instance of CppParser for parsing code
        """
        self.project_path = os.path.abspath(project_path)
        self.parser = parser
        self.files = {}  # Map of file path to file metadata
        self.components = {}  # Map of component name to file paths
        self.functions = {}  # Map of function name to file paths
        self.classes = {}  # Map of class name to file paths
        self.dependencies = {}  # Map of file path to list of dependencies
        self.ui_elements = {}  # Map of UI element to file paths
        self.file_contents = {}  # Cache for file contents
        self.file_hashes = {}  # Map of file path to hash for change detection
        
        # Setup watchdog for file monitoring
        self.observer = None
        self.event_handler = None
        
    def index_codebase(self):
        """Index the entire codebase and set up monitoring."""
        # Clear existing indices
        self.files = {}
        self.components = {}
        self.functions = {}
        self.classes = {}
        self.dependencies = {}
        self.ui_elements = {}
        self.file_contents = {}
        self.file_hashes = {}
        
        # Find all relevant files
        self._find_files()
        
        # Parse each file
        for file_path in self.files:
            self._parse_file(file_path)
            
        # Build dependency graph
        self._build_dependency_graph()
        
        # Set up file monitoring
        self._setup_monitoring()
        
    def _find_files(self):
        """Find all C++, header, and RTF files in the project directory."""
        patterns = ["*.cpp", "*.h", "*.hpp", "*.cc", "*.cxx", "*.rtf"]
        
        for root, _, filenames in os.walk(self.project_path):
            for pattern in patterns:
                for filename in fnmatch.filter(filenames, pattern):
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, self.project_path)
                    
                    # Skip build directories
                    if any(part.startswith(("build", "bin", "obj", ".git")) for part in rel_path.split(os.sep)):
                        continue
                    
                    # Store file metadata
                    self.files[file_path] = {
                        "path": file_path,
                        "name": filename,
                        "extension": os.path.splitext(filename)[1],
                        "modified": os.path.getmtime(file_path),
                        "size": os.path.getsize(file_path)
                    }
    
    def _parse_file(self, file_path: str):
        """Parse a single file and extract metadata."""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
            # Cache content
            self.file_contents[file_path] = content
            
            # Calculate hash for change detection
            self.file_hashes[file_path] = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            # Use the parser to extract metadata
            parsed_data = self.parser.parse_file(file_path, content)
            
            # Update indices with parsed data
            if parsed_data:
                # Update components index
                for component in parsed_data.get('components', []):
                    if component not in self.components:
                        self.components[component] = []
                    self.components[component].append(file_path)
                
                # Update functions index
                for function in parsed_data.get('functions', []):
                    if function not in self.functions:
                        self.functions[function] = []
                    self.functions[function].append(file_path)
                
                # Update classes index
                for class_name in parsed_data.get('classes', []):
                    if class_name not in self.classes:
                        self.classes[class_name] = []
                    self.classes[class_name].append(file_path)
                
                # Update UI elements index
                for ui_element in parsed_data.get('ui_elements', []):
                    if ui_element not in self.ui_elements:
                        self.ui_elements[ui_element] = []
                    self.ui_elements[ui_element].append(file_path)
                
                # Store dependencies for this file
                self.dependencies[file_path] = parsed_data.get('includes', [])
                
        except Exception as e:
            print(f"Error parsing file {file_path}: {str(e)}")
    
    def _build_dependency_graph(self):
        """Build a graph of file dependencies based on includes."""
        # Map include paths to actual file paths
        include_to_file = {}
        
        # First pass: build include to file mapping
        for file_path in self.files:
            filename = os.path.basename(file_path)
            include_to_file[filename] = file_path
            
        # Second pass: resolve includes to actual file paths
        for file_path, includes in self.dependencies.items():
            resolved_includes = []
            
            for include in includes:
                # Handle both "file.h" and <file.h> includes
                include_name = include.strip('"<>')
                include_name = os.path.basename(include_name)
                
                if include_name in include_to_file:
                    resolved_includes.append(include_to_file[include_name])
                else:
                    # Try to find the file in the project
                    for potential_file in self.files:
                        if os.path.basename(potential_file) == include_name:
                            resolved_includes.append(potential_file)
                            break
            
            # Update dependencies with resolved file paths
            self.dependencies[file_path] = resolved_includes
    
    def _setup_monitoring(self):
        """Set up file system monitoring to detect changes in the codebase."""
        if self.observer:
            self.observer.stop()
            
        # Create event handler
        self.event_handler = CodebaseEventHandler(self)
        
        # Create observer
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.project_path, recursive=True)
        
        # Start observer in a separate thread
        self.observer.start()
    
    def get_file_content(self, file_path: str) -> str:
        """Get the content of a file from cache or read it if not cached."""
        if file_path in self.file_contents:
            return self.file_contents[file_path]
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                self.file_contents[file_path] = content
                return content
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return ""
    
    def file_changed(self, file_path: str) -> bool:
        """Check if a file has changed since it was last indexed."""
        if file_path not in self.file_hashes:
            return True
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                new_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
                return new_hash != self.file_hashes[file_path]
        except Exception:
            return True
    
    def update_file(self, file_path: str):
        """Update a single file in the index."""
        if file_path in self.files:
            # Remove file from all indices
            self._remove_file_from_indices(file_path)
            
        # Re-parse the file
        self._parse_file(file_path)
        
        # Update dependency graph
        self._build_dependency_graph()
    
    def _remove_file_from_indices(self, file_path: str):
        """Remove a file from all indices."""
        # Remove from components index
        for component, files in list(self.components.items()):
            if file_path in files:
                files.remove(file_path)
                if not files:
                    del self.components[component]
        
        # Remove from functions index
        for function, files in list(self.functions.items()):
            if file_path in files:
                files.remove(file_path)
                if not files:
                    del self.functions[function]
        
        # Remove from classes index
        for class_name, files in list(self.classes.items()):
            if file_path in files:
                files.remove(file_path)
                if not files:
                    del self.classes[class_name]
        
        # Remove from UI elements index
        for ui_element, files in list(self.ui_elements.items()):
            if file_path in files:
                files.remove(file_path)
                if not files:
                    del self.ui_elements[ui_element]
        
        # Remove from dependencies index
        if file_path in self.dependencies:
            del self.dependencies[file_path]
        
        # Remove from file contents cache
        if file_path in self.file_contents:
            del self.file_contents[file_path]
        
        # Remove from file hashes
        if file_path in self.file_hashes:
            del self.file_hashes[file_path]
            
        # Remove from files index
        if file_path in self.files:
            del self.files[file_path]


class CodebaseEventHandler(FileSystemEventHandler):
    """Watchdog event handler for monitoring codebase changes."""
    
    def __init__(self, indexer):
        """Initialize the event handler with an indexer."""
        self.indexer = indexer
        self.last_update_time = time.time()
        self.update_debounce = 2.0  # seconds
        
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory and self._should_process_file(event.src_path):
            self._debounced_update(event.src_path)
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory and self._should_process_file(event.src_path):
            self._debounced_update(event.src_path)
    
    def on_deleted(self, event):
        """Handle file deletion events."""
        if not event.is_directory and event.src_path in self.indexer.files:
            self.indexer._remove_file_from_indices(event.src_path)
    
    def _should_process_file(self, file_path: str) -> bool:
        """Check if a file should be processed based on its extension."""
        extensions = ['.cpp', '.h', '.hpp', '.cc', '.cxx', '.rtf']
        return any(file_path.endswith(ext) for ext in extensions)
    
    def _debounced_update(self, file_path: str):
        """Update the file index after a debounce period."""
        current_time = time.time()
        
        # Only process updates after the debounce period
        if current_time - self.last_update_time >= self.update_debounce:
            self.last_update_time = current_time
            
            # Check if the file has changed
            if self.indexer.file_changed(file_path):
                self.indexer.update_file(file_path)
