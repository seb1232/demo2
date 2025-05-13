import re
import os
from typing import Dict, List, Set, Any, Optional, Tuple
import subprocess
import tempfile
from pathlib import Path
import platform

class CppParser:
    """Parser for C++ code that extracts components, functions, classes, etc."""
    
    def __init__(self):
        """Initialize the C++ parser."""
        # Regex patterns for parsing
        self.include_pattern = re.compile(r'#include\s+["<](.*)[">]')
        self.class_pattern = re.compile(r'class\s+(\w+)(?:\s*:\s*(?:public|protected|private)\s+(\w+))?')
        self.function_pattern = re.compile(r'(\w+)\s+(\w+)\s*\([^)]*\)')
        self.ui_element_pattern = re.compile(r'(Button|CheckBox|ComboBox|Dialog|Label|ListView|Menu|ProgressBar|RadioButton|ScrollBar|Slider|Spinner|TabControl|TextBox|ToolBar|TreeView|Window)')
        self.component_keywords = [
            'widget', 'component', 'control', 'view', 'panel', 'dialog', 'window', 'form',
            'button', 'checkbox', 'radio', 'slider', 'menu', 'toolbar', 'label', 'textbox',
            'listview', 'treeview', 'combobox', 'container', 'scroll', 'tab', 'grid', 'image'
        ]
        
        # Try to detect if libclang is available
        self.has_libclang = self._check_libclang()
        
    def _check_libclang(self) -> bool:
        """Check if libclang is available for more accurate parsing."""
        try:
            import clang.cindex
            return True
        except ImportError:
            return False
    
    def parse_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Parse a file and extract metadata.
        
        Args:
            file_path: Path to the file
            content: Content of the file
            
        Returns:
            Dictionary containing extracted metadata:
            - includes: List of included files
            - classes: List of classes defined
            - functions: List of functions defined
            - components: List of UI components
            - ui_elements: List of UI elements
        """
        # Parse using libclang if available
        if self.has_libclang and file_path.endswith(('.cpp', '.h', '.hpp', '.cc', '.cxx')):
            try:
                return self._parse_with_libclang(file_path, content)
            except Exception as e:
                print(f"Libclang parsing failed for {file_path}: {str(e)}")
                # Fall back to regex parsing
        
        # Use regex parsing as fallback or for RTF files
        return self._parse_with_regex(file_path, content)
    
    def _parse_with_regex(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse C++ code using regular expressions."""
        result = {
            'includes': [],
            'classes': [],
            'functions': [],
            'components': [],
            'ui_elements': []
        }
        
        # Extract includes
        includes = self.include_pattern.findall(content)
        result['includes'] = includes
        
        # Only parse C++ files for code structures
        if file_path.endswith(('.cpp', '.h', '.hpp', '.cc', '.cxx')):
            # Extract classes
            classes = self.class_pattern.findall(content)
            result['classes'] = [class_name for class_name, _ in classes]
            
            # Extract inheritance relationships
            for class_name, parent in classes:
                if parent and parent not in result['classes']:
                    result['classes'].append(parent)
            
            # Extract functions
            functions = self.function_pattern.findall(content)
            result['functions'] = [f"{return_type} {func_name}" for return_type, func_name in functions]
            
            # Extract UI elements
            ui_elements = self.ui_element_pattern.findall(content)
            result['ui_elements'] = list(set(ui_elements))
            
            # Look for component patterns
            for keyword in self.component_keywords:
                if re.search(fr'\b{keyword}\b', content, re.IGNORECASE):
                    if keyword not in result['components']:
                        result['components'].append(keyword)
            
            # Special case for action buttons (common in UI code)
            if re.search(r'\baction\s*button\b', content, re.IGNORECASE):
                if 'action button' not in result['components']:
                    result['components'].append('action button')
        
        return result
    
    def _parse_with_libclang(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse C++ code using libclang for more accurate results."""
        try:
            import clang.cindex
            from clang.cindex import CursorKind
            
            result = {
                'includes': [],
                'classes': [],
                'functions': [],
                'components': [],
                'ui_elements': []
            }
            
            # Write content to a temporary file to avoid encoding issues
            with tempfile.NamedTemporaryFile(suffix='.cpp', delete=False) as temp_file:
                temp_path = temp_file.name
                temp_file.write(content.encode('utf-8'))
            
            try:
                # Initialize libclang
                index = clang.cindex.Index.create()
                
                # Parse the file
                tu = index.parse(temp_path)
                
                # Process the abstract syntax tree
                for cursor in tu.cursor.walk_preorder():
                    # Get includes
                    if cursor.kind == CursorKind.INCLUSION_DIRECTIVE:
                        included_file = cursor.displayname
                        result['includes'].append(included_file)
                    
                    # Get classes
                    elif cursor.kind == CursorKind.CLASS_DECL:
                        class_name = cursor.spelling
                        if class_name:
                            result['classes'].append(class_name)
                    
                    # Get functions
                    elif cursor.kind == CursorKind.FUNCTION_DECL:
                        func_name = cursor.spelling
                        if func_name:
                            # Get return type and function name
                            result_type = cursor.result_type.spelling
                            result['functions'].append(f"{result_type} {func_name}")
                
                # Look for UI elements and components using regex
                # (libclang doesn't help much with identifying UI-specific patterns)
                ui_elements = self.ui_element_pattern.findall(content)
                result['ui_elements'] = list(set(ui_elements))
                
                for keyword in self.component_keywords:
                    if re.search(fr'\b{keyword}\b', content, re.IGNORECASE):
                        if keyword not in result['components']:
                            result['components'].append(keyword)
                
                # Special case for action buttons
                if re.search(r'\baction\s*button\b', content, re.IGNORECASE):
                    if 'action button' not in result['components']:
                        result['components'].append('action button')
                
            finally:
                # Clean up temporary file
                os.unlink(temp_path)
            
            return result
            
        except ImportError:
            # Fall back to regex parsing if import fails
            return self._parse_with_regex(file_path, content)
        except Exception as e:
            print(f"Error in libclang parsing: {str(e)}")
            return self._parse_with_regex(file_path, content)
