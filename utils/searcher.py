import re
import os
from typing import List, Dict, Any, Set
import difflib

class CodebaseSearcher:
    """Search engine for the indexed codebase."""
    
    def __init__(self, indexer):
        """
        Initialize the searcher with an indexer.
        
        Args:
            indexer: An instance of CodebaseIndexer with indexed codebase
        """
        self.indexer = indexer
    
    def search(self, query: str, search_type: str, case_sensitive: bool = False, 
               file_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search the codebase based on query and search type.
        
        Args:
            query: Search query string
            search_type: Type of search (component, function, class, dependency, ui_element)
            case_sensitive: Whether the search should be case sensitive
            file_types: List of file extensions to include in search
            
        Returns:
            List of dictionaries containing search results
        """
        if not query:
            return []
            
        # Filter file types if specified
        if file_types:
            file_filter = lambda f: any(f.endswith(f".{ft}") for ft in file_types)
        else:
            file_filter = lambda f: True
            
        # Adjust query for case sensitivity
        if not case_sensitive:
            search_query = query.lower()
        else:
            search_query = query
            
        results = []
        
        # Search based on type
        if search_type == "component":
            results = self._search_components(search_query, case_sensitive, file_filter)
        elif search_type == "function":
            results = self._search_functions(search_query, case_sensitive, file_filter)
        elif search_type == "class":
            results = self._search_classes(search_query, case_sensitive, file_filter)
        elif search_type == "dependency":
            results = self._search_dependencies(search_query, case_sensitive, file_filter)
        elif search_type == "ui element":
            results = self._search_ui_elements(search_query, case_sensitive, file_filter)
        else:
            # Default to full text search
            results = self._full_text_search(search_query, case_sensitive, file_filter)
            
        return results
        
    def regex_search(self, pattern: str, case_sensitive: bool = False, 
                    file_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search the codebase using regular expressions.
        
        Args:
            pattern: Regular expression pattern
            case_sensitive: Whether the search should be case sensitive
            file_types: List of file extensions to include in search
            
        Returns:
            List of dictionaries containing search results
        """
        if not pattern:
            return []
            
        # Filter file types if specified
        if file_types:
            file_filter = lambda f: any(f.endswith(f".{ft}") for ft in file_types)
        else:
            file_filter = lambda f: True
            
        results = []
        
        try:
            # Compile regex pattern
            if case_sensitive:
                regex = re.compile(pattern)
            else:
                regex = re.compile(pattern, re.IGNORECASE)
                
            # Search through all files
            for file_path, file_info in self.indexer.files.items():
                if not file_filter(file_path):
                    continue
                    
                content = self.indexer.get_file_content(file_path)
                
                # Find all matches
                for i, line in enumerate(content.splitlines(), 1):
                    for match in regex.finditer(line):
                        results.append({
                            'file': file_path,
                            'line': i,
                            'match': line.strip(),
                            'relevance': 1.0,  # All regex matches are equally relevant
                            'start': match.start(),
                            'end': match.end()
                        })
        except re.error:
            # Return empty list if regex is invalid
            return []
            
        return results
    
    def _search_components(self, query: str, case_sensitive: bool, file_filter) -> List[Dict[str, Any]]:
        """Search for components in the indexed codebase."""
        results = []
        
        # Search through indexed components
        for component, files in self.indexer.components.items():
            component_match = component if case_sensitive else component.lower()
            
            # Check for matches
            if query in component_match:
                relevance = self._calculate_relevance(query, component)
                
                for file_path in files:
                    if not file_filter(file_path):
                        continue
                        
                    # Find specific line where component is mentioned
                    line_number, line_text = self._find_in_file(file_path, component)
                    
                    results.append({
                        'file': file_path,
                        'line': line_number,
                        'match': line_text,
                        'relevance': relevance
                    })
        
        # Also search file contents for component names
        text_results = self._full_text_search(query, case_sensitive, file_filter)
        
        # Combine and deduplicate results
        seen_files = {r['file'] for r in results}
        for result in text_results:
            if result['file'] not in seen_files:
                results.append(result)
                seen_files.add(result['file'])
        
        return results
    
    def _search_functions(self, query: str, case_sensitive: bool, file_filter) -> List[Dict[str, Any]]:
        """Search for functions in the indexed codebase."""
        results = []
        
        # Search through indexed functions
        for function, files in self.indexer.functions.items():
            function_match = function if case_sensitive else function.lower()
            
            # Check for matches
            if query in function_match:
                relevance = self._calculate_relevance(query, function)
                
                for file_path in files:
                    if not file_filter(file_path):
                        continue
                        
                    # Find specific line where function is defined
                    line_number, line_text = self._find_in_file(file_path, function)
                    
                    results.append({
                        'file': file_path,
                        'line': line_number,
                        'match': line_text,
                        'relevance': relevance
                    })
        
        return results
    
    def _search_classes(self, query: str, case_sensitive: bool, file_filter) -> List[Dict[str, Any]]:
        """Search for classes in the indexed codebase."""
        results = []
        
        # Search through indexed classes
        for class_name, files in self.indexer.classes.items():
            class_match = class_name if case_sensitive else class_name.lower()
            
            # Check for matches
            if query in class_match:
                relevance = self._calculate_relevance(query, class_name)
                
                for file_path in files:
                    if not file_filter(file_path):
                        continue
                        
                    # Find specific line where class is defined
                    line_number, line_text = self._find_in_file(file_path, f"class {class_name}")
                    
                    results.append({
                        'file': file_path,
                        'line': line_number,
                        'match': line_text,
                        'relevance': relevance
                    })
        
        return results
    
    def _search_dependencies(self, query: str, case_sensitive: bool, file_filter) -> List[Dict[str, Any]]:
        """Search for dependencies in the indexed codebase."""
        results = []
        
        # Create a set to track processed files
        processed_files = set()
        
        # Search through all files
        for file_path, deps in self.indexer.dependencies.items():
            if not file_filter(file_path):
                continue
                
            file_name = os.path.basename(file_path)
            file_match = file_name if case_sensitive else file_name.lower()
            
            # Check if query matches the file name
            if query in file_match and file_path not in processed_files:
                relevance = self._calculate_relevance(query, file_name)
                processed_files.add(file_path)
                
                # Find all files that depend on this file
                dependent_files = []
                for dep_file, dep_list in self.indexer.dependencies.items():
                    if file_path in dep_list:
                        dependent_files.append(dep_file)
                
                # Add result for the file itself
                results.append({
                    'file': file_path,
                    'line': 1,  # Header line
                    'match': f"File with {len(dependent_files)} dependents",
                    'relevance': relevance,
                    'dependent_files': dependent_files
                })
                
                # Add results for dependent files
                for dep_file in dependent_files:
                    if not file_filter(dep_file) or dep_file in processed_files:
                        continue
                        
                    # Find the include line
                    line_number, line_text = self._find_include_in_file(dep_file, file_name)
                    
                    if line_number > 0:
                        results.append({
                            'file': dep_file,
                            'line': line_number,
                            'match': line_text,
                            'relevance': relevance * 0.9  # Slightly lower relevance
                        })
                        processed_files.add(dep_file)
            
            # Check if query matches any of the dependencies
            for dep in deps:
                dep_name = os.path.basename(dep) if isinstance(dep, str) else dep
                dep_match = dep_name if case_sensitive else dep_name.lower()
                
                if query in dep_match and file_path not in processed_files:
                    relevance = self._calculate_relevance(query, dep_name)
                    
                    # Find the include line
                    line_number, line_text = self._find_include_in_file(file_path, dep_name)
                    
                    if line_number > 0:
                        results.append({
                            'file': file_path,
                            'line': line_number,
                            'match': line_text,
                            'relevance': relevance
                        })
                        processed_files.add(file_path)
        
        return results
    
    def _search_ui_elements(self, query: str, case_sensitive: bool, file_filter) -> List[Dict[str, Any]]:
        """Search for UI elements in the indexed codebase."""
        results = []
        
        # Search through indexed UI elements
        for ui_element, files in self.indexer.ui_elements.items():
            ui_match = ui_element if case_sensitive else ui_element.lower()
            
            # Check for matches
            if query in ui_match:
                relevance = self._calculate_relevance(query, ui_element)
                
                for file_path in files:
                    if not file_filter(file_path):
                        continue
                        
                    # Find specific line where UI element is mentioned
                    line_number, line_text = self._find_in_file(file_path, ui_element)
                    
                    results.append({
                        'file': file_path,
                        'line': line_number,
                        'match': line_text,
                        'relevance': relevance
                    })
        
        # Also search file contents for UI element names
        text_results = self._full_text_search(query, case_sensitive, file_filter)
        
        # Combine and deduplicate results
        seen_files = {r['file'] for r in results}
        for result in text_results:
            if result['file'] not in seen_files:
                results.append(result)
                seen_files.add(result['file'])
        
        return results
    
    def _full_text_search(self, query: str, case_sensitive: bool, file_filter) -> List[Dict[str, Any]]:
        """Search for query in the full text of files."""
        results = []
        
        # Search through all files
        for file_path in self.indexer.files:
            if not file_filter(file_path):
                continue
                
            content = self.indexer.get_file_content(file_path)
            
            # Convert content to lowercase if not case sensitive
            if not case_sensitive:
                search_content = content.lower()
            else:
                search_content = content
            
            # Check if the query appears in the content
            if query in search_content:
                # Find all occurrences
                lines = content.splitlines()
                search_lines = search_content.splitlines()
                
                for i, (line, search_line) in enumerate(zip(lines, search_lines), 1):
                    if query in search_line:
                        # Calculate relevance based on how well the query matches the line
                        relevance = self._calculate_text_relevance(query, line)
                        
                        results.append({
                            'file': file_path,
                            'line': i,
                            'match': line.strip(),
                            'relevance': relevance
                        })
        
        return results
    
    def _calculate_relevance(self, query: str, target: str) -> float:
        """Calculate relevance score for a match based on how well the query matches the target."""
        # Normalize strings
        query_norm = query.lower()
        target_norm = target.lower()
        
        # Exact match gets highest relevance
        if query_norm == target_norm:
            return 1.0
        
        # Calculate string similarity using difflib
        similarity = difflib.SequenceMatcher(None, query_norm, target_norm).ratio()
        
        # Adjust relevance based on whether the query is a substring of the target
        if query_norm in target_norm:
            # Prefix match (starts with) gets higher relevance
            if target_norm.startswith(query_norm):
                return 0.9
            # Word boundary match gets medium-high relevance
            elif f" {query_norm}" in target_norm or target_norm.endswith(query_norm):
                return 0.8
            # Substring match gets medium relevance
            else:
                return 0.7
        
        # Partial match based on similarity
        return max(0.3, similarity)
    
    def _calculate_text_relevance(self, query: str, line: str) -> float:
        """Calculate relevance score for a text search match."""
        # Normalize strings
        query_norm = query.lower()
        line_norm = line.lower()
        
        # Calculate string similarity
        similarity = difflib.SequenceMatcher(None, query_norm, line_norm).ratio()
        
        # Count occurrences of the query in the line
        occurrences = line_norm.count(query_norm)
        
        # Adjust relevance based on occurrences and similarity
        if occurrences > 1:
            return min(1.0, 0.6 + (occurrences * 0.1) + (similarity * 0.3))
        else:
            return min(1.0, 0.5 + (similarity * 0.5))
    
    def _find_in_file(self, file_path: str, search_text: str) -> tuple:
        """Find a specific text in a file and return line number and text."""
        content = self.indexer.get_file_content(file_path)
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            if search_text in line:
                return i, line.strip()
        
        return 1, ""  # Default to first line if not found
    
    def _find_include_in_file(self, file_path: str, include_name: str) -> tuple:
        """Find a specific include directive in a file."""
        content = self.indexer.get_file_content(file_path)
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            if "#include" in line and include_name in line:
                return i, line.strip()
        
        return 0, ""  # Not found
    
    def find_related_components(self, file_path: str) -> List[Dict[str, Any]]:
        """Find components related to the given file."""
        if not file_path or file_path not in self.indexer.files:
            return []
            
        related = []
        
        # Find dependencies
        if file_path in self.indexer.dependencies:
            for dep in self.indexer.dependencies[file_path]:
                related.append({
                    'file': dep,
                    'relationship': 'dependency'
                })
        
        # Find dependents (files that include this file)
        for dep_file, deps in self.indexer.dependencies.items():
            if file_path in deps:
                related.append({
                    'file': dep_file,
                    'relationship': 'dependent'
                })
        
        # Find files with similar components
        file_components = set()
        for comp, files in self.indexer.components.items():
            if file_path in files:
                file_components.add(comp)
        
        if file_components:
            for comp in file_components:
                for comp_file in self.indexer.components.get(comp, []):
                    if comp_file != file_path:
                        related.append({
                            'file': comp_file,
                            'relationship': f'shares component: {comp}'
                        })
        
        # Find files with similar classes
        file_classes = set()
        for cls, files in self.indexer.classes.items():
            if file_path in files:
                file_classes.add(cls)
        
        if file_classes:
            for cls in file_classes:
                for cls_file in self.indexer.classes.get(cls, []):
                    if cls_file != file_path:
                        related.append({
                            'file': cls_file,
                            'relationship': f'shares class: {cls}'
                        })
        
        # Remove duplicates while preserving order
        seen = set()
        deduped = []
        for item in related:
            key = item['file']
            if key not in seen:
                seen.add(key)
                deduped.append(item)
        
        return deduped
    
    def find_usage_examples(self, file_path: str, max_examples: int = 5) -> List[Dict[str, Any]]:
        """Find usage examples for components defined in the given file."""
        if not file_path or file_path not in self.indexer.files:
            return []
            
        examples = []
        
        # Find components defined in this file
        file_components = set()
        for comp, files in self.indexer.components.items():
            if file_path in files:
                file_components.add(comp)
        
        # Find classes defined in this file
        file_classes = set()
        for cls, files in self.indexer.classes.items():
            if file_path in files:
                file_classes.add(cls)
        
        # Get usage examples for components
        for comp in file_components:
            for comp_file in self.indexer.components.get(comp, []):
                if comp_file != file_path:
                    content = self.indexer.get_file_content(comp_file)
                    
                    # Extract a snippet around the component usage
                    snippet = self._extract_code_snippet(content, comp)
                    
                    if snippet:
                        examples.append({
                            'file': comp_file,
                            'code': snippet,
                            'type': 'component',
                            'name': comp
                        })
                        
                        if len(examples) >= max_examples:
                            return examples
        
        # Get usage examples for classes
        for cls in file_classes:
            for cls_file in self.indexer.classes.get(cls, []):
                if cls_file != file_path:
                    content = self.indexer.get_file_content(cls_file)
                    
                    # Extract a snippet around the class usage
                    snippet = self._extract_code_snippet(content, cls)
                    
                    if snippet:
                        examples.append({
                            'file': cls_file,
                            'code': snippet,
                            'type': 'class',
                            'name': cls
                        })
                        
                        if len(examples) >= max_examples:
                            return examples
        
        return examples
    
    def _extract_code_snippet(self, content: str, search_text: str, context_lines: int = 5) -> str:
        """Extract a code snippet around a search text with context lines."""
        lines = content.splitlines()
        
        for i, line in enumerate(lines):
            if search_text in line:
                # Determine start and end lines for the snippet
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                
                # Extract the snippet
                return "\n".join(lines[start:end])
        
        return ""
