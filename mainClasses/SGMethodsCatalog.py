#!/usr/bin/env python3
"""
SGMethodsCatalog - SGE Methods Catalog Generator
Generates comprehensive catalog of SGE modeler methods for documentation and discovery
"""

import ast
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class MethodInfo:
    """Information about a modeler method"""
    name: str
    signature: str
    description: str
    docstring: str
    category: str
    class_name: str
    parameters: List[Dict[str, str]]
    returns: str
    examples: List[str]
    line_number: int
    parent_classes: List[str] = None

class SGEMethodExtractor:
    """Extracts modeler methods from SGE Python files"""
    
    def __init__(self):
        self.modeler_keywords = ['new', 'get', 'delete', 'set', 'add', 'nb', 'is', 'has', 'do_', 'display']
        # Map keywords to their base categories
        self.keyword_to_category = {
            'new': 'NEW',
            'add': 'ADD', 
            'set': 'SET',
            'delete': 'DELETE',
            'get': 'GET',
            'nb': 'NB',
            'is': 'IS',
            'has': 'HAS',
            'do_': 'DO',
            'display': 'DISPLAY'
        }
    
    def extract_methods_from_file(self, file_path: str) -> Dict[str, List[MethodInfo]]:
        """Extract modeler methods from a Python file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"Error parsing {file_path}: {e}")
            return {}
        
        # Find the main class
        class_name = self._extract_class_name(file_path)
        if not class_name:
            return {}
        
        # Find modeler methods section boundaries
        modeler_section_start, modeler_section_end = self._find_modeler_section(content)
        if modeler_section_start == -1:
            print(f"No MODELER METHODS section found in {file_path}")
            return {}
        
        # Extract methods within modeler section
        methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if method is within modeler section
                if modeler_section_start <= node.lineno <= modeler_section_end:
                    method_info = self._extract_method_info(node, class_name, content)
                    if method_info and self._is_modeler_method(method_info):
                        methods.append(method_info)
        
        return {class_name: methods}
    
    def _find_modeler_section(self, content: str) -> tuple[int, int]:
        """Find the start and end line numbers of the MODELER METHODS section"""
        lines = content.split('\n')
        start_line = -1
        end_line = -1
        
        # Find MODELER METHODS section start
        for i, line in enumerate(lines):
            if '# MODELER METHODS' in line:
                start_line = i + 1  # Convert to 1-based line numbering
                break
        
        if start_line == -1:
            return -1, -1
        
        # Find the end of the modeler section (next major section or end of class)
        for i in range(start_line, len(lines)):
            line = lines[i].strip()
            # Look for next major section (not a subsection)
            if (line.startswith('# ============================================================================') and 
                i > start_line and 
                any(keyword in lines[i+1] for keyword in ['DEVELOPER METHODS', 'INITIALIZATION', 'UI MANAGEMENT', 'ENTITY MANAGEMENT', 'LAYOUT MANAGEMENT', 'GAME FLOW MANAGEMENT', 'UTILITY METHODS'])):
                end_line = i
                break
        
        # If no end found, use end of file
        if end_line == -1:
            end_line = len(lines)
        
        return start_line, end_line
    
    def _extract_class_name(self, file_path: str) -> Optional[str]:
        """Extract class name from file path"""
        filename = os.path.basename(file_path)
        if filename.endswith('.py'):
            # Handle SG classes and special utility classes
            if filename.startswith('SG') or filename == 'AttributeAndValueFunctionalities.py':
                return filename[:-3]  # Remove .py extension
        return None
    
    def _extract_multiple_classes_from_file(self, file_path: str) -> Dict[str, List[MethodInfo]]:
        """Extract methods from multiple classes in the same file (e.g., SGEntityType.py)"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"Error parsing {file_path}: {e}")
            return {}
        
        # Find all classes in the file
        classes_data = {}
        class_inheritance = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                if class_name.startswith('SG'):
                    # Extract parent class information
                    parent_classes = []
                    if node.bases:
                        for base in node.bases:
                            if isinstance(base, ast.Name):
                                parent_classes.append(base.id)
                    class_inheritance[class_name] = parent_classes
                    
                    # Find modeler methods section for this class
                    modeler_section_start, modeler_section_end = self._find_modeler_section_for_class(content, class_name)
                    if modeler_section_start != -1:
                        methods = []
                        for method_node in ast.walk(node):
                            if isinstance(method_node, ast.FunctionDef):
                                if modeler_section_start <= method_node.lineno <= modeler_section_end:
                                    method_info = self._extract_method_info(method_node, class_name, content)
                                    if method_info and self._is_modeler_method(method_info):
                                        methods.append(method_info)
                        
                        if methods:
                            classes_data[class_name] = methods
        
        # Add inheritance information to the data
        for class_name, methods in classes_data.items():
            for method in methods:
                method.parent_classes = class_inheritance.get(class_name, [])
        
        return classes_data
    
    def _find_modeler_section_for_class(self, content: str, class_name: str) -> tuple[int, int]:
        """Find MODELER METHODS section for a specific class"""
        lines = content.split('\n')
        start_line = -1
        end_line = -1
        in_target_class = False
        
        for i, line in enumerate(lines):
            # Check if we're in the target class
            if f"class {class_name}" in line:
                in_target_class = True
                continue
            
            # If we're in the target class and find MODELER METHODS
            if in_target_class and '# MODELER METHODS' in line:
                start_line = i + 1
                break
        
        if start_line == -1:
            return -1, -1
        
        # Find the end of the modeler section
        for i in range(start_line, len(lines)):
            line = lines[i].strip()
            if (line.startswith('# ============================================================================') and 
                i > start_line and 
                any(keyword in lines[i+1] for keyword in ['DEVELOPER METHODS', 'INITIALIZATION', 'UI MANAGEMENT', 'ENTITY MANAGEMENT', 'LAYOUT MANAGEMENT', 'GAME FLOW MANAGEMENT', 'UTILITY METHODS'])):
                end_line = i
                break
        
        if end_line == -1:
            end_line = len(lines)
        
        return start_line, end_line
    
    def _extract_method_info(self, node: ast.FunctionDef, class_name: str, content: str) -> Optional[MethodInfo]:
        """Extract information about a method"""
        method_name = node.name
        
        # Skip private methods and special methods
        if method_name.startswith('_') and not method_name.startswith('__'):
            return None
        
        # Get line number
        line_number = node.lineno
        
        # Extract signature
        signature = self._extract_signature(node, content)
        
        # Extract docstring
        docstring = ast.get_docstring(node) or ""
        
        # Extract description (first line of docstring)
        description = docstring.split('\n')[0].strip() if docstring else ""
        
        # Look for @CATEGORY tag in comments before the method
        category_tag = self._find_category_tag_in_comments(content, line_number)
        
        # Determine category
        category = self._determine_category(method_name, docstring, category_tag)
        
        # Extract parameters
        parameters = self._extract_parameters(node, docstring)
        
        # Extract return info
        returns = self._extract_returns(docstring)
        
        # Extract examples
        examples = self._extract_examples(docstring)
        
        return MethodInfo(
            name=method_name,
            signature=signature,
            description=description,
            docstring=docstring,
            category=category,
            class_name=class_name,
            parameters=parameters,
            returns=returns,
            examples=examples,
            line_number=line_number
        )
    
    def _extract_signature(self, node: ast.FunctionDef, content: str) -> str:
        """Extract method signature from source code"""
        lines = content.split('\n')
        start_line = node.lineno - 1
        
        # Find the complete signature (might span multiple lines)
        signature_lines = []
        current_line = start_line
        
        while current_line < len(lines):
            line = lines[current_line].strip()
            signature_lines.append(line)
            
            # Check if signature is complete (has closing parenthesis)
            if ')' in line and not line.endswith('\\'):
                break
            current_line += 1
        
        return ' '.join(signature_lines)
    
    def _find_category_tag_in_comments(self, content: str, method_line_number: int) -> Optional[str]:
        """Find @CATEGORY tag in comments before a method"""
        lines = content.split('\n')
        method_index = method_line_number - 1  # Convert to 0-based index
        
        # Look in the 5 lines before the method
        for i in range(max(0, method_index - 5), method_index):
            line = lines[i].strip()
            if '@CATEGORY:' in line:
                category = line.split('@CATEGORY:')[1].strip()
                return category.upper()
        
        return None
    
    def _determine_category(self, method_name: str, docstring: str = "", category_tag: Optional[str] = None) -> str:
        """Determine the category of a method based on its name and tags"""
        # First check for explicit category tag in comments
        if category_tag:
            return category_tag
        
        # Then check for explicit category tag in docstring
        if docstring:
            # Look for @CATEGORY tag in docstring
            for line in docstring.split('\n'):
                if '@CATEGORY:' in line:
                    category = line.split('@CATEGORY:')[1].strip()
                    return category.upper()
        
        # Fallback to name-based detection
        method_lower = method_name.lower()
        
        # Check each keyword and return the corresponding base category
        for keyword, base_category in self.keyword_to_category.items():
            if method_lower.startswith(keyword):
                return base_category
        
        return "OTHER MODELER METHODS"
    
    def _extract_parameters(self, node: ast.FunctionDef, docstring: str = "") -> List[Dict[str, str]]:
        """Extract parameter information from function signature and docstring"""
        parameters = []
        
        # Extract parameter info from docstring
        docstring_params = self._parse_docstring_parameters(docstring)
        
        for arg in node.args.args:
            if arg.arg == 'self':
                continue
                
            param_info = {
                'name': arg.arg,
                'type': 'Any',  # Default type
                'description': ''
            }
            
            # Try to get type annotation from function signature
            if arg.annotation:
                param_info['type'] = ast.unparse(arg.annotation)
            
            # Override with information from docstring if available
            if arg.arg in docstring_params:
                docstring_param = docstring_params[arg.arg]
                if docstring_param.get('type'):
                    param_info['type'] = docstring_param['type']
                if docstring_param.get('description'):
                    param_info['description'] = docstring_param['description']
            
            parameters.append(param_info)
        
        return parameters
    
    def _parse_docstring_parameters(self, docstring: str) -> Dict[str, Dict[str, str]]:
        """Parse parameter information from docstring Args: section"""
        if not docstring:
            return {}
        
        parameters = {}
        lines = docstring.split('\n')
        in_args_section = False
        current_param = None
        
        for line in lines:
            line = line.strip()
            
            # Check for Args: section start
            if line.lower().startswith('args:'):
                in_args_section = True
                continue
            
            # Check for other sections that end Args section
            if in_args_section and (line.lower().startswith('returns:') or 
                                  line.lower().startswith('example:') or
                                  line.lower().startswith('note:') or
                                  line.lower().startswith('raises:')):
                break
            
            if in_args_section:
                # Look for parameter definitions (name (type): description)
                if ':' in line and '(' in line and ')' in line:
                    # Extract parameter name, type, and description
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        param_part = parts[0].strip()
                        description = parts[1].strip()
                        
                        # Extract name and type from "name (type)" format
                        if '(' in param_part and ')' in param_part:
                            name_start = param_part.find('(')
                            name = param_part[:name_start].strip()
                            type_start = param_part.find('(') + 1
                            type_end = param_part.find(')')
                            param_type = param_part[type_start:type_end].strip()
                            
                            parameters[name] = {
                                'type': param_type,
                                'description': description
                            }
                            current_param = name
                        else:
                            # Simple name: description format
                            name = param_part.strip()
                            parameters[name] = {
                                'type': 'Any',
                                'description': description
                            }
                            current_param = name
                elif current_param and line:
                    # Continuation of description
                    if current_param in parameters:
                        parameters[current_param]['description'] += ' ' + line
        
        return parameters
    
    def _extract_returns(self, docstring: str) -> str:
        """Extract return information from docstring"""
        if not docstring:
            return ""
        
        # Look for Returns: or Return: section
        lines = docstring.split('\n')
        in_returns_section = False
        return_info = []
        
        for line in lines:
            line = line.strip()
            if line.lower().startswith('returns:') or line.lower().startswith('return:'):
                in_returns_section = True
                # Remove "Returns:" or "Return:" prefix
                if line.lower().startswith('returns:'):
                    return_info.append(line[8:].strip())
                else:
                    return_info.append(line[7:].strip())
            elif in_returns_section:
                # Stop at next section or non-indented line
                if line and not line.startswith(' ') and not line.startswith('\t'):
                    # Check if it's another section
                    if (line.lower().startswith('args:') or 
                        line.lower().startswith('example:') or
                        line.lower().startswith('note:') or
                        line.lower().startswith('raises:')):
                        break
                if line:
                    return_info.append(line)
        
        return ' '.join(return_info).strip()
    
    def _extract_examples(self, docstring: str) -> List[str]:
        """Extract examples from docstring"""
        if not docstring:
            return []
        
        examples = []
        lines = docstring.split('\n')
        in_example_section = False
        current_example = []
        
        for line in lines:
            line = line.strip()
            
            # Check for example section headers
            if (line.lower().startswith('example') or 
                line.lower().startswith('examples') or
                line.lower().startswith('usage') or
                line.startswith('```') or
                line.startswith('>>>')):
                if current_example:
                    examples.append('\n'.join(current_example).strip())
                    current_example = []
                in_example_section = True
                # Skip the header line
                continue
            
            # Check for code blocks
            if line.startswith('```'):
                if current_example:
                    examples.append('\n'.join(current_example).strip())
                    current_example = []
                in_example_section = not in_example_section
                continue
            
            # Collect example content
            if in_example_section:
                current_example.append(line)
            elif line.startswith('>>>') or line.startswith('...'):
                # Python REPL examples
                current_example.append(line)
                in_example_section = True
        
        # Add the last example if exists
        if current_example:
            examples.append('\n'.join(current_example).strip())
        
        return [ex for ex in examples if ex.strip()]
    
    def _is_modeler_method(self, method_info: MethodInfo) -> bool:
        """Check if a method is a modeler method"""
        # Since we're already filtering by section, all methods in the modeler section are modeler methods
        # Just exclude obvious developer methods that might have slipped through
        excluded_methods = ['getView', 'setView', 'updateView', 'setDisplay', 'updateIncomingAgent', 
                           'removeAgent', 'shouldAcceptDropFrom', 'zoomIn', 'zoomOut', 'zoomFit',
                           'convert_coordinates', 'paintEvent', 'getRegion', 'mousePressEvent', 'dropEvent']
        
        return method_info.name not in excluded_methods

class SGMethodsCatalog:
    """
    SGE Methods Catalog Generator
    
    Generates comprehensive catalog of SGE modeler methods for documentation and discovery.
    Supports multiple output formats: JSON, HTML, and integration with SGE framework.
    """
    
    def __init__(self):
        self.extractor = SGEMethodExtractor()
        self.catalog_data = {}
    
    def generate_catalog(self, classes: List[str] = None) -> Dict[str, Any]:
        """
        Generate methods catalog for specified SGE classes
        
        Args:
            classes (List[str], optional): List of class file paths to process.
                If None, processes all SGE classes in mainClasses/
                
        Returns:
            Dict[str, Any]: Complete catalog data
        """
        if classes is None:
            classes = self._get_all_sge_classes()
        
        all_methods_data = {}
        
        for file_path in classes:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue
                
            print(f"Extracting methods from {file_path}...")
            
            # Try multiple classes extraction first (for files like SGEntityType.py)
            methods_data = self.extractor._extract_multiple_classes_from_file(file_path)
            
            # If no multiple classes found, try single class extraction
            if not methods_data:
                methods_data = self.extractor.extract_methods_from_file(file_path)
            
            if methods_data:
                all_methods_data.update(methods_data)
            else:
                print(f"No modeler methods found in {file_path}")
        
        self.catalog_data = self._generate_catalog_structure(all_methods_data)
        return self.catalog_data
    
    def _get_all_sge_classes(self) -> List[str]:
        """Get all SGE class files from mainClasses directory"""
        main_classes_dir = "mainClasses"
        sge_classes = []
        
        if os.path.exists(main_classes_dir):
            for filename in os.listdir(main_classes_dir):
                if filename.startswith('SG') and filename.endswith('.py'):
                    sge_classes.append(os.path.join(main_classes_dir, filename))
        
        return sge_classes
    
    def _generate_catalog_structure(self, methods_data: Dict[str, List[MethodInfo]]) -> Dict[str, Any]:
        """Generate structured catalog from extracted methods"""
        catalog = {
            "metadata": {
                "title": "SGE Methods Catalog",
                "description": "Comprehensive catalog of SGE modeler methods",
                "version": "1.0.0",
                "generated_date": "2024-12-19",
                "total_classes": len(methods_data),
                "total_methods": sum(len(methods) for methods in methods_data.values())
            },
            "classes": {},
            "inheritance": {}
        }
        
        # Build inheritance information first
        inheritance = {}
        for class_name, methods in methods_data.items():
            if methods and hasattr(methods[0], 'parent_classes'):
                inheritance[class_name] = methods[0].parent_classes
        
        catalog["inheritance"] = inheritance
        
        # Generate classes with inherited methods
        for class_name, methods in methods_data.items():
            class_info = {
                "class_name": class_name,
                "description": f"{class_name} model class for SGE framework",
                "total_methods": len(methods),
                "categories": {}
            }
            
            # Group methods by category
            for method in methods:
                category = method.category
                if category not in class_info['categories']:
                    class_info['categories'][category] = []
                
                method_dict = asdict(method)
                class_info['categories'][category].append(method_dict)
            
            # Add inherited methods to this class
            inherited_methods = self._get_inherited_methods(class_name, methods_data, inheritance)
            for inherited_method in inherited_methods:
                category = inherited_method.get('category', 'OTHER MODELER METHODS')
                if category not in class_info['categories']:
                    class_info['categories'][category] = []
                
                # Check for duplicates before adding
                method_name = inherited_method.get('name')
                existing_methods = class_info['categories'][category]
                is_duplicate = any(method.get('name') == method_name for method in existing_methods)
                
                if not is_duplicate:
                    class_info['categories'][category].append(inherited_method)
            
            # Update total methods count
            class_info['total_methods'] = sum(len(methods) for methods in class_info['categories'].values())
            
            catalog["classes"][class_name] = class_info
        
        # Update total methods in metadata
        catalog["metadata"]["total_methods"] = sum(
            class_info.get('total_methods', 0) 
            for class_info in catalog["classes"].values()
        )
        
        return catalog
    
    def save_to_json(self, filename: str = "sge_methods_catalog.json") -> str:
        """
        Save catalog to JSON file
        
        Args:
            filename (str): Output filename
            
        Returns:
            str: Path to saved file
        """
        if not self.catalog_data:
            raise ValueError("No catalog data. Call generate_catalog() first.")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.catalog_data, f, indent=2, ensure_ascii=False)
        
        print(f"Catalog saved to {filename}")
        return filename
    
    def generate_html(self, output_file: str = "sge_methods_catalog.html") -> str:
        """
        Generate HTML catalog for web browsing
        
        Args:
            output_file (str): Output HTML filename
            
        Returns:
            str: Path to generated HTML file
        """
        if not self.catalog_data:
            raise ValueError("No catalog data. Call generate_catalog() first.")
        
        html_content = self._generate_html_content()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML catalog saved to {output_file}")
        return output_file
    
    def _generate_html_content(self) -> str:
        """Generate HTML content for the catalog"""
        metadata = self.catalog_data.get("metadata", {})
        classes = self.catalog_data.get("classes", {})
        inheritance = self.catalog_data.get("inheritance", {})
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata.get('title', 'SGE Methods Catalog')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f8f9fa; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        
        .main-container {{ display: flex; min-height: calc(100vh - 120px); }}
        
        .sidebar {{ width: 300px; background-color: white; padding: 20px; box-shadow: 2px 0 5px rgba(0,0,0,0.1); }}
        .content {{ flex: 1; padding: 20px; overflow-y: auto; }}
        
        .classes-section {{ margin-bottom: 25px; }}
        .classes-list {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .class-link {{ display: inline-block; padding: 8px 16px; background-color: #3498db; color: white; text-decoration: none; border-radius: 20px; font-size: 0.9em; transition: background-color 0.3s; }}
        .class-link:hover {{ background-color: #2980b9; }}
        
        .search-section {{ margin-bottom: 25px; }}
        .search-box {{ width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 1em; box-sizing: border-box; }}
        .search-box:focus {{ outline: none; border-color: #3498db; }}
        
        .filters-section {{ margin-bottom: 25px; }}
        .filters-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
        .filter-group {{ }}
        .filter-group label {{ display: block; margin-bottom: 5px; font-weight: bold; color: #2c3e50; font-size: 0.9em; }}
        .filter-select {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px; font-size: 0.9em; box-sizing: border-box; }}
        
        .class-section {{ background-color: white; margin-bottom: 25px; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .class-section h2 {{ color: #2c3e50; margin-top: 0; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        
        .category-section {{ margin: 25px 0; }}
        .category-section h3 {{ color: #34495e; margin-bottom: 15px; font-size: 1.2em; }}
        
        .method-card {{ border: 1px solid #e0e0e0; margin: 15px 0; padding: 20px; border-radius: 8px; background-color: #fafafa; transition: box-shadow 0.3s; }}
        .method-card:hover {{ box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .method-card h4 {{ color: #2c3e50; margin-top: 0; font-size: 1.3em; }}
        .method-signature {{ font-family: 'Courier New', monospace; background-color: #2c3e50; color: #ecf0f1; padding: 10px; border-radius: 5px; margin: 10px 0; font-size: 0.9em; }}
        .examples {{ background-color: #e8f5e8; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #27ae60; }}
        .examples pre {{ margin: 0; font-family: 'Courier New', monospace; font-size: 0.9em; }}
        
        .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .stat-item {{ text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
        .stat-label {{ color: #7f8c8d; font-size: 0.9em; }}
        
        @media (max-width: 768px) {{
            .main-container {{ flex-direction: column; }}
            .sidebar {{ width: 100%; }}
            .filters-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{metadata.get('title', 'SGE Methods Catalog')}</h1>
        <p>{metadata.get('description', '')}</p>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{metadata.get('total_methods', 0)}</div>
                <div class="stat-label">Methods</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{metadata.get('total_classes', 0)}</div>
                <div class="stat-label">Classes</div>
            </div>
        </div>
    </div>
    
    <div class="main-container">
        <div class="sidebar">
            <div class="classes-section">
                <h3>Classes</h3>
                <div class="classes-list">
"""
        
        for class_name in classes.keys():
            html += f'                    <a href="#{class_name}" class="class-link">{class_name}</a>\n'
        
        html += """
                </div>
            </div>
            
            <div class="search-section">
                <h3>Search</h3>
                <input type="text" class="search-box" id="search-box" placeholder="Search methods...">
            </div>
            
            <div class="filters-section">
                <h3>Filters</h3>
                <div class="filters-grid">
                    <div class="filter-group">
                        <label>Class</label>
                        <select class="filter-select" id="class-filter">
                            <option value="all">All Classes</option>
"""
        
        for class_name in classes.keys():
            html += f'                            <option value="{class_name}">{class_name}</option>\n'
        
        html += """
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label>Category</label>
                        <select class="filter-select" id="category-filter">
                            <option value="all">All Categories</option>
                            <option value="NEW">NEW</option>
                            <option value="ADD">ADD</option>
                            <option value="SET">SET</option>
                            <option value="DELETE">DELETE</option>
                            <option value="GET">GET</option>
                            <option value="NB">NB</option>
                            <option value="IS">IS</option>
                            <option value="HAS">HAS</option>
                            <option value="DO">DO</option>
                            <option value="DISPLAY">DISPLAY</option>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label>Examples</label>
                        <select class="filter-select" id="examples-filter">
                            <option value="all">All Methods</option>
                            <option value="with-examples">With Examples</option>
                            <option value="without-examples">Without Examples</option>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label>Parameters</label>
                        <select class="filter-select" id="parameters-filter">
                            <option value="all">All Methods</option>
                            <option value="with-params">With Parameters</option>
                            <option value="without-params">Without Parameters</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="content">
"""
        
        # Build complete inheritance chain
        complete_inheritance = self._build_inheritance_chain(class_name, inheritance)
        
        for class_name, class_info in classes.items():
            html += f"""
        <div class="class-section" id="{class_name}">
            <h2>{class_name}</h2>
            <p>{class_info.get('description', '')} - {class_info.get('total_methods', 0)} methods</p>
"""
            
            # Add inheritance information
            if class_name in inheritance and inheritance[class_name]:
                parent_classes = inheritance[class_name]
                html += f'            <p><strong>Inherits from:</strong> {", ".join(parent_classes)}</p>\n'
            
            # Use methods directly from class_info (already includes inherited methods)
            all_methods_by_category = class_info.get('categories', {})
            
            # Display methods by category (including inherited methods)
            for category, methods in all_methods_by_category.items():
                html += f"""
            <div class="category-section">
                <h3>{category} Methods</h3>
"""
                
                for method in methods:
                    has_examples = "with-examples" if method.get('examples') else "without-examples"
                    has_params = "with-params" if method.get('parameters') else "without-params"
                    
                    # Check if this is an inherited method
                    original_class = method.get('original_class')
                    if original_class and original_class != class_name:
                        method_title = f"{method['name']} <span style=\"color: #7f8c8d; font-size: 0.8em;\">(from {original_class})</span>"
                    else:
                        method_title = method['name']
                    
                    html += f"""
                <div class="method-card" data-category="{category}" data-class="{class_name}" data-examples="{has_examples}" data-parameters="{has_params}">
                    <h4>{method_title}</h4>
                    <div class="method-signature">{method['signature']}</div>
                    <p><strong>Description:</strong> {method['description']}</p>
"""
                    
                    if method.get('parameters'):
                        html += "<p><strong>Parameters:</strong></p><ul>"
                        for param in method['parameters']:
                            html += f"<li>{param['name']}: {param['type']}</li>"
                        html += "</ul>"
                    
                    if method.get('returns'):
                        html += f"<p><strong>Returns:</strong> {method['returns']}</p>"
                    
                    if method.get('examples'):
                        html += "<div class='examples'><strong>Examples:</strong><pre>"
                        for example in method['examples']:
                            html += f"{example}\n"
                        html += "</pre></div>"
                    
                    html += "</div>"
                
                html += "</div>"
            
            html += "</div>"
        
        html += """
        </div>
    </div>
    
    <script>
        // Apply all filters
        function applyFilters() {
            const searchQuery = document.getElementById('search-box').value.toLowerCase();
            const classFilter = document.getElementById('class-filter').value;
            const categoryFilter = document.getElementById('category-filter').value;
            const examplesFilter = document.getElementById('examples-filter').value;
            const parametersFilter = document.getElementById('parameters-filter').value;
            
            const methodCards = document.querySelectorAll('.method-card');
            const categorySections = document.querySelectorAll('.category-section');
            
            // First, hide all method cards based on filters
            methodCards.forEach(card => {
                let show = true;
                
                // Search filter
                if (searchQuery && !card.textContent.toLowerCase().includes(searchQuery)) {
                    show = false;
                }
                
                // Class filter
                if (classFilter !== 'all' && card.dataset.class !== classFilter) {
                    show = false;
                }
                
                // Category filter
                if (categoryFilter !== 'all' && card.dataset.category !== categoryFilter) {
                    show = false;
                }
                
                // Examples filter
                if (examplesFilter !== 'all' && card.dataset.examples !== examplesFilter) {
                    show = false;
                }
                
                // Parameters filter
                if (parametersFilter !== 'all' && card.dataset.parameters !== parametersFilter) {
                    show = false;
                }
                
                card.style.display = show ? 'block' : 'none';
            });
            
            // Then, hide category sections that have no visible methods
            categorySections.forEach(section => {
                const visibleMethods = section.querySelectorAll('.method-card[style*="block"], .method-card:not([style*="none"])');
                const hasVisibleMethods = Array.from(visibleMethods).some(card => 
                    card.style.display !== 'none' && 
                    (card.style.display === 'block' || !card.style.display)
                );
                
                section.style.display = hasVisibleMethods ? 'block' : 'none';
            });
            
            // Also filter inherited methods by category
            const inheritedSections = document.querySelectorAll('.category-section h3');
            inheritedSections.forEach(header => {
                if (header.textContent.includes('INHERITED')) {
                    const section = header.parentElement;
                    const inheritedMethods = section.querySelectorAll('.method-card');
                    let hasVisibleInheritedMethods = false;
                    
                    inheritedMethods.forEach(method => {
                        const methodCategory = method.dataset.category;
                        let showInherited = true;
                        
                        // Apply category filter to inherited methods
                        if (categoryFilter !== 'all' && methodCategory !== categoryFilter) {
                            showInherited = false;
                        }
                        
                        // Apply other filters
                        if (showInherited) {
                            const searchQuery = document.getElementById('search-box').value.toLowerCase();
                            const classFilter = document.getElementById('class-filter').value;
                            const examplesFilter = document.getElementById('examples-filter').value;
                            const parametersFilter = document.getElementById('parameters-filter').value;
                            
                            if (searchQuery && !method.textContent.toLowerCase().includes(searchQuery)) {
                                showInherited = false;
                            }
                            
                            if (classFilter !== 'all' && method.dataset.class !== classFilter) {
                                showInherited = false;
                            }
                            
                            if (examplesFilter !== 'all' && method.dataset.examples !== examplesFilter) {
                                showInherited = false;
                            }
                            
                            if (parametersFilter !== 'all' && method.dataset.parameters !== parametersFilter) {
                                showInherited = false;
                            }
                        }
                        
                        method.style.display = showInherited ? 'block' : 'none';
                        if (showInherited) {
                            hasVisibleInheritedMethods = true;
                        }
                    });
                    
                    section.style.display = hasVisibleInheritedMethods ? 'block' : 'none';
                }
            });
            
            // Also hide class sections that have no visible categories
            const classSections = document.querySelectorAll('.class-section');
            classSections.forEach(classSection => {
                const visibleCategories = classSection.querySelectorAll('.category-section[style*="block"], .category-section:not([style*="none"])');
                const hasVisibleCategories = Array.from(visibleCategories).some(section => 
                    section.style.display !== 'none' && 
                    (section.style.display === 'block' || !section.style.display)
                );
                
                classSection.style.display = hasVisibleCategories ? 'block' : 'none';
            });
        }
        
        // Add event listeners to all filters
        document.getElementById('search-box').addEventListener('input', applyFilters);
        document.getElementById('class-filter').addEventListener('change', applyFilters);
        document.getElementById('category-filter').addEventListener('change', applyFilters);
        document.getElementById('examples-filter').addEventListener('change', applyFilters);
        document.getElementById('parameters-filter').addEventListener('change', applyFilters);
    </script>
</body>
</html>
"""
        
        return html
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the catalog"""
        if not self.catalog_data:
            return {}
        
        metadata = self.catalog_data.get("metadata", {})
        classes = self.catalog_data.get("classes", {})
        
        summary = {
            "total_classes": metadata.get("total_classes", 0),
            "total_methods": metadata.get("total_methods", 0),
            "classes": {}
        }
        
        for class_name, class_info in classes.items():
            summary["classes"][class_name] = {
                "total_methods": class_info.get("total_methods", 0),
                "categories": {cat: len(methods) for cat, methods in class_info.get("categories", {}).items()}
            }
        
        return summary
    
    def _get_inherited_methods(self, class_name: str, classes: Dict, inheritance: Dict) -> List[Dict]:
        """Get methods inherited by a class from its parent classes (recursively)"""
        inherited_methods = []
        visited_classes = set()  # Prevent infinite loops
        
        def _get_methods_recursively(current_class: str, depth: int = 0):
            if current_class in visited_classes or depth > 10:  # Safety limit
                return
            
            visited_classes.add(current_class)
            
            # Get direct parent classes
            if current_class not in inheritance:
                return
            
            parent_classes = inheritance[current_class]
            for parent_class in parent_classes:
                # Check if parent class is in the catalog
                if parent_class in classes:
                    parent_class_info = classes[parent_class]
                    for category, methods in parent_class_info.get('categories', {}).items():
                        for method in methods:
                            # Add parent class info to the method
                            method_copy = method.copy()
                            method_copy['original_class'] = parent_class
                            inherited_methods.append(method_copy)
                else:
                    # Parent class not in catalog, try to extract from file
                    inherited_from_file = self._extract_inherited_methods_from_file(parent_class)
                    for method in inherited_from_file:
                        method['original_class'] = parent_class
                    inherited_methods.extend(inherited_from_file)
                
                # Recursively get methods from parent's parents
                _get_methods_recursively(parent_class, depth + 1)
        
        _get_methods_recursively(class_name)
        return inherited_methods
    
    def _extract_inherited_methods_from_file(self, parent_class_name: str) -> List[Dict]:
        """Extract methods from a parent class file that's not in the main catalog"""
        inherited_methods = []
        
        # Map class names to their file paths
        class_file_map = {
            'AttributeAndValueFunctionalities': 'mainClasses/AttributeAndValueFunctionalities.py',
            'SGEntity': 'mainClasses/SGEntity.py'
        }
        
        if parent_class_name not in class_file_map:
            return inherited_methods
        
        file_path = class_file_map[parent_class_name]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the file
            tree = ast.parse(content)
            
            # Find the class
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == parent_class_name:
                    # Find modeler methods section for this class
                    modeler_section_start, modeler_section_end = self.extractor._find_modeler_section_for_class(content, parent_class_name)
                    if modeler_section_start != -1:
                        # Extract methods from this class
                        for method_node in ast.walk(node):
                            if isinstance(method_node, ast.FunctionDef):
                                if modeler_section_start <= method_node.lineno <= modeler_section_end:
                                    method_info = self.extractor._extract_method_info(method_node, parent_class_name, content)
                                    if method_info and self.extractor._is_modeler_method(method_info):
                                        method_dict = asdict(method_info)
                                        method_dict['original_class'] = parent_class_name
                                        inherited_methods.append(method_dict)
                    break
                    
        except Exception as e:
            print(f"Error extracting inherited methods from {file_path}: {e}")
        
        return inherited_methods
    
    def _build_inheritance_chain(self, class_name: str, inheritance: Dict) -> Dict[str, List[str]]:
        """Build complete inheritance chain for all classes"""
        complete_inheritance = {}
        visited = set()
        
        def _build_chain_recursively(current_class: str, depth: int = 0):
            if current_class in visited or depth > 10:
                return
            
            visited.add(current_class)
            
            if current_class not in complete_inheritance:
                complete_inheritance[current_class] = []
            
            # Get direct parents
            if current_class in inheritance:
                direct_parents = inheritance[current_class] or []
                complete_inheritance[current_class].extend(direct_parents)
                
                # Recursively add parents of parents
                for parent in direct_parents:
                    _build_chain_recursively(parent, depth + 1)
                    if parent in complete_inheritance:
                        complete_inheritance[current_class].extend(complete_inheritance[parent])
        
        # Build chain for all classes
        for cls in inheritance.keys():
            _build_chain_recursively(cls)
        
        return complete_inheritance
    
    def identify_and_tag_ambiguous_methods(self):
        """Identify methods that need category tags and optionally add them"""
        print("\n=== IDENTIFICATION OF AMBIGUOUS METHODS ===")
        
        # Methods that should be in SET but are currently in OTHER
        set_methods_ambiguous = [
            'incValue', 'decValue', 'calcValue', 'copyValue'
        ]
        
        # Methods that should be in GET but are currently in OTHER
        get_methods_ambiguous = [
            'value'  # if it exists
        ]
        
        # Methods that should be in IS but are currently in OTHER
        is_methods_ambiguous = [
            'isValue', 'isNotValue'
        ]
        
        # Methods that should be in DO but are currently in OTHER
        do_methods_ambiguous = [
            'moveTo', 'moveAgent', 'moveRandomly', 'moveTowards'
        ]
        
        ambiguous_methods = {
            'SET': set_methods_ambiguous,
            'GET': get_methods_ambiguous,
            'IS': is_methods_ambiguous,
            'DO': do_methods_ambiguous
        }
        
        print("Methods identified as ambiguous:")
        for category, methods in ambiguous_methods.items():
            if methods:
                print(f"  {category}: {', '.join(methods)}")
        
        print("\nTo add tags, use:")
        print("catalog.add_category_tags_to_methods()")
        
        return ambiguous_methods
    
    def add_category_tags_to_methods(self, dry_run=True, target_classes=None):
        """Add category tags to ambiguous methods in source files
        
        Args:
            dry_run (bool): If True, only show what would be modified without making changes
            target_classes (list): List of class names to process. If None, process all classes.
        """
        print(f"\n=== ADDING CATEGORY TAGS (dry_run={dry_run}) ===")
        
        ambiguous_methods = self.identify_and_tag_ambiguous_methods()
        
        # Files to process
        all_files = [
            "mainClasses/AttributeAndValueFunctionalities.py",
            "mainClasses/SGCell.py",
            "mainClasses/SGAgent.py",
            "mainClasses/SGEntityType.py"
        ]
        
        # Filter files based on target_classes
        if target_classes:
            files_to_process = []
            for file_path in all_files:
                # Extract class name from file path
                filename = os.path.basename(file_path)
                class_name = filename.replace('.py', '')
                if class_name in target_classes:
                    files_to_process.append(file_path)
        else:
            files_to_process = all_files
        
        for file_path in files_to_process:
            if not os.path.exists(file_path):
                continue
                
            print(f"\nProcessing {file_path}...")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            modified = False
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                # Look for method definitions
                if line.strip().startswith('def ') and '(' in line:
                    method_name = line.split('def ')[1].split('(')[0].strip()
                    
                    # Check if this method is ambiguous
                    target_category = None
                    for category, methods in ambiguous_methods.items():
                        if method_name in methods:
                            target_category = category
                            break
                    
                    if target_category:
                        # Check if tag already exists (look in previous lines and docstring)
                        existing_tag = self._find_existing_category_tag(lines, i)
                        
                        if existing_tag:
                            if existing_tag == target_category:
                                print(f"  ✓ {method_name}: tag {target_category} already present")
                            else:
                                print(f"  ⚠ {method_name}: existing tag {existing_tag}, would be changed to {target_category}")
                                if not dry_run:
                                    # Replace existing tag
                                    self._replace_existing_tag(lines, i, target_category)
                                    modified = True
                        else:
                            # Add new tag
                            tag_line = f"    # @CATEGORY: {target_category}"
                            lines.insert(i, tag_line)
                            modified = True
                            print(f"  + {method_name}: adding tag {target_category}")
            
            # Save if modified and not in dry_run
            if modified and not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                print(f"  → File {file_path} modified")
            elif modified:
                print(f"  → File {file_path} would be modified (dry_run)")
    
    def _find_existing_category_tag(self, lines, method_line_index):
        """Find existing @CATEGORY tag for a method"""
        # Look in previous lines (comments before method)
        for i in range(max(0, method_line_index - 5), method_line_index):
            line = lines[i].strip()
            if '@CATEGORY:' in line:
                return line.split('@CATEGORY:')[1].strip().upper()
        
        # Look in docstring (next few lines after method definition)
        for i in range(method_line_index + 1, min(len(lines), method_line_index + 10)):
            line = lines[i].strip()
            if '@CATEGORY:' in line:
                return line.split('@CATEGORY:')[1].strip().upper()
            # Stop at first non-comment, non-empty line (end of docstring)
            if line and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                break
        
        return None
    
    def _replace_existing_tag(self, lines, method_line_index, new_category):
        """Replace existing @CATEGORY tag with new one"""
        # Look in previous lines
        for i in range(max(0, method_line_index - 5), method_line_index):
            if '@CATEGORY:' in lines[i]:
                lines[i] = lines[i].replace(lines[i].split('@CATEGORY:')[1].strip(), new_category)
                return
        
        # Look in docstring
        for i in range(method_line_index + 1, min(len(lines), method_line_index + 10)):
            if '@CATEGORY:' in lines[i]:
                lines[i] = lines[i].replace(lines[i].split('@CATEGORY:')[1].strip(), new_category)
                return
    
    def _get_inherited_methods(self, class_name: str, methods_data: Dict[str, List[MethodInfo]], inheritance: Dict) -> List[Dict]:
        """Get methods inherited from parent classes"""
        inherited_methods = []
        visited_classes = set()
        
        def _get_methods_recursively(current_class: str, depth: int = 0):
            if current_class in visited_classes or depth > 10:
                return
                
            visited_classes.add(current_class)
            
            # Get direct parent classes
            parent_classes = inheritance.get(current_class, []) or []
            
            # For SGAgent and SGCell, add AttributeAndValueFunctionalities explicitly
            if current_class in ['SGAgent', 'SGCell']:
                if 'AttributeAndValueFunctionalities' not in parent_classes:
                    parent_classes = parent_classes + ['AttributeAndValueFunctionalities']
            
            for parent_class in parent_classes:
                # If parent class is in our catalog, use its methods
                if parent_class in methods_data:
                    for method in methods_data[parent_class]:
                        method_dict = asdict(method)
                        method_dict['original_class'] = parent_class
                        inherited_methods.append(method_dict)
                else:
                    # Extract methods from parent class file
                    parent_methods = self._extract_inherited_methods_from_file(parent_class)
                    for method_dict in parent_methods:
                        method_dict['original_class'] = parent_class
                        inherited_methods.append(method_dict)
                
                # Recursively get methods from parent's parents
                _get_methods_recursively(parent_class, depth + 1)
        
        _get_methods_recursively(class_name)
        return inherited_methods
    
    def _extract_inherited_methods_from_file(self, parent_class_name: str) -> List[Dict]:
        """Extract methods from parent class files that are not in the main catalog"""
        inherited_methods = []
        
        # Map class names to their file paths
        class_to_file = {
            'AttributeAndValueFunctionalities': 'mainClasses/AttributeAndValueFunctionalities.py',
            'SGEntity': 'mainClasses/SGEntity.py'
        }
        
        file_path = class_to_file.get(parent_class_name)
        if not file_path or not os.path.exists(file_path):
            return inherited_methods
        
        try:
            methods_data = self.extractor.extract_methods_from_file(file_path)
            
            if parent_class_name in methods_data:
                for method in methods_data[parent_class_name]:
                    method_dict = asdict(method)
                    inherited_methods.append(method_dict)
                    
        except Exception as e:
            print(f"Error extracting inherited methods from {file_path}: {e}")
        
        return inherited_methods
    
    def generate_snippets(self, output_file: str = "sge_methods_snippets.json") -> str:
        """
        Generate VS Code/Cursor snippets from the catalog
        
        Args:
            output_file (str): Output snippets filename
            
        Returns:
            str: Path to generated snippets file
        """
        if not self.catalog_data:
            raise ValueError("No catalog data. Call generate_catalog() first.")
        
        snippets = {}
        classes = self.catalog_data.get("classes", {})
        
        for class_name, class_info in classes.items():
            for category, methods in class_info.get("categories", {}).items():
                for method in methods:
                    snippet_key = f"{class_name}.{method['name']}"
                    snippet_body = self._generate_snippet_body(method, class_name)
                    
                    snippets[snippet_key] = {
                        "prefix": f"{class_name.lower()}.{method['name']}",
                        "body": snippet_body,
                        "description": method.get("description", ""),
                        "scope": "python"
                    }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(snippets, f, indent=2, ensure_ascii=False)
        
        print(f"Snippets saved to {output_file}")
        return output_file
    
    def _generate_snippet_body(self, method: Dict[str, Any], class_name: str) -> List[str]:
        """Generate snippet body for a method"""
        method_name = method['name']
        parameters = method.get('parameters', [])
        
        # Generate snippet based on method type and parameters
        if method_name.startswith('new'):
            return self._generate_new_method_snippet(method_name, parameters, class_name)
        elif method_name.startswith('get'):
            return self._generate_get_method_snippet(method_name, parameters, class_name)
        elif method_name.startswith('set'):
            return self._generate_set_method_snippet(method_name, parameters, class_name)
        elif method_name.startswith('delete'):
            return self._generate_delete_method_snippet(method_name, parameters, class_name)
        elif method_name.startswith('nb'):
            return self._generate_nb_method_snippet(method_name, parameters, class_name)
        elif method_name.startswith('is') or method_name.startswith('has'):
            return self._generate_boolean_method_snippet(method_name, parameters, class_name)
        else:
            return self._generate_generic_method_snippet(method_name, parameters, class_name)
    
    def _generate_new_method_snippet(self, method_name: str, parameters: List[Dict], class_name: str) -> List[str]:
        """Generate snippet for new methods"""
        if class_name == "SGCell" and method_name == "newAgentHere":
            return [
                "${1:agent} = ${2:cell}.newAgentHere(${3:agent_type}${4:, adictAttributes=${5:None}})"
            ]
        elif class_name in ["SGEntityType", "SGCellType", "SGAgentType"] and method_name.startswith("new"):
            return [
                "${1:entity} = ${2:entity_type}.${method_name}(${3:})"
            ]
        else:
            return [
                f"${{1:result}} = ${{2:instance}}.{method_name}(${{3:}})"
            ]
    
    def _generate_get_method_snippet(self, method_name: str, parameters: List[Dict], class_name: str) -> List[str]:
        """Generate snippet for get methods"""
        if not parameters:
            return [
                f"${{1:result}} = ${{2:instance}}.{method_name}()"
            ]
        else:
            param_placeholders = []
            for i, param in enumerate(parameters, start=3):
                param_placeholders.append(f"${{{i}:{param['name']}}}")
            
            return [
                f"${{1:result}} = ${{2:instance}}.{method_name}({', '.join(param_placeholders)})"
            ]
    
    def _generate_set_method_snippet(self, method_name: str, parameters: List[Dict], class_name: str) -> List[str]:
        """Generate snippet for set methods"""
        if len(parameters) >= 2:
            return [
                f"${{1:instance}}.{method_name}(${{2:{parameters[0]['name']}}}, ${{3:{parameters[1]['name']}}})"
            ]
        else:
            return [
                f"${{1:instance}}.{method_name}(${{2:value}})"
            ]
    
    def _generate_delete_method_snippet(self, method_name: str, parameters: List[Dict], class_name: str) -> List[str]:
        """Generate snippet for delete methods"""
        if not parameters:
            return [
                f"${{1:instance}}.{method_name}()"
            ]
        else:
            return [
                f"${{1:instance}}.{method_name}(${{2:{parameters[0]['name']}}})"
            ]
    
    def _generate_nb_method_snippet(self, method_name: str, parameters: List[Dict], class_name: str) -> List[str]:
        """Generate snippet for nb methods"""
        if not parameters:
            return [
                f"${{1:count}} = ${{2:instance}}.{method_name}()"
            ]
        else:
            return [
                f"${{1:count}} = ${{2:instance}}.{method_name}(${{3:{parameters[0]['name']}}})"
            ]
    
    def _generate_boolean_method_snippet(self, method_name: str, parameters: List[Dict], class_name: str) -> List[str]:
        """Generate snippet for boolean methods (is/has)"""
        if not parameters:
            return [
                f"if ${{1:instance}}.{method_name}():",
                "    ${2:pass}"
            ]
        else:
            return [
                f"if ${{1:instance}}.{method_name}(${{2:{parameters[0]['name']}}}):",
                "    ${3:pass}"
            ]
    
    def _generate_generic_method_snippet(self, method_name: str, parameters: List[Dict], class_name: str) -> List[str]:
        """Generate generic snippet for other methods"""
        if not parameters:
            return [
                f"${{1:result}} = ${{2:instance}}.{method_name}()"
            ]
        else:
            param_placeholders = []
            for i, param in enumerate(parameters, start=3):
                param_placeholders.append(f"${{{i}:{param['name']}}}")
            
            return [
                f"${{1:result}} = ${{2:instance}}.{method_name}({', '.join(param_placeholders)})"
            ]

# Example usage
if __name__ == "__main__":
    catalog = SGMethodsCatalog()
    
    # Generate catalog for specific classes
    classes = [
        "mainClasses/SGCell.py",
        "mainClasses/SGEntity.py",
        "mainClasses/SGEntityType.py",  # SGCellType and  SGAgenType and defined in SGEntityType.py
        "mainClasses/SGAgent.py",
        # "mainClasses/AttributeAndValueFunctionalities.py"
    ]
    
    catalog.generate_catalog(classes)
    
    # Save to JSON
    catalog.save_to_json("sge_methods_catalog.json")
    
    # Generate HTML
    catalog.generate_html("sge_methods_catalog.html")
    
    # Generate snippets
    catalog.generate_snippets("sge_methods_snippets.json")
    
    # Print summary
    summary = catalog.get_summary()
    print(f"\nCatalog Summary:")
    print(f"Total classes: {summary['total_classes']}")
    print(f"Total methods: {summary['total_methods']}")
    
    for class_name, info in summary["classes"].items():
        print(f"\n{class_name}: {info['total_methods']} methods")
        for category, count in info["categories"].items():
            print(f"  {category}: {count} methods")
    
    # Uncomment the following line to run the tagging script
    # catalog.identify_and_tag_ambiguous_methods()
