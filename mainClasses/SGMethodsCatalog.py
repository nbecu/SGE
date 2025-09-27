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
        if filename.startswith('SG') and filename.endswith('.py'):
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
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                if class_name.startswith('SG'):
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
        
        # Determine category
        category = self._determine_category(method_name)
        
        # Extract parameters
        parameters = self._extract_parameters(node)
        
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
    
    def _determine_category(self, method_name: str) -> str:
        """Determine the category of a method based on its name"""
        method_lower = method_name.lower()
        
        # Check each keyword and return the corresponding base category
        for keyword, base_category in self.keyword_to_category.items():
            if method_lower.startswith(keyword):
                return base_category
        
        return "OTHER MODELER METHODS"
    
    def _extract_parameters(self, node: ast.FunctionDef) -> List[Dict[str, str]]:
        """Extract parameter information"""
        parameters = []
        
        for arg in node.args.args:
            if arg.arg == 'self':
                continue
                
            param_info = {
                'name': arg.arg,
                'type': 'Any',  # Default type
                'description': ''
            }
            
            # Try to get type annotation
            if arg.annotation:
                param_info['type'] = ast.unparse(arg.annotation)
            
            parameters.append(param_info)
        
        return parameters
    
    def _extract_returns(self, docstring: str) -> str:
        """Extract return information from docstring"""
        if not docstring:
            return ""
        
        # Look for Returns: section
        lines = docstring.split('\n')
        in_returns_section = False
        return_info = []
        
        for line in lines:
            line = line.strip()
            if line.lower().startswith('returns:'):
                in_returns_section = True
                return_info.append(line[8:].strip())  # Remove "Returns:"
            elif in_returns_section:
                if line and not line.startswith(' '):
                    break
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
            "classes": {}
        }
        
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
            
            catalog["classes"][class_name] = class_info
        
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
        
        for class_name, class_info in classes.items():
            html += f"""
        <div class="class-section" id="{class_name}">
            <h2>{class_name}</h2>
            <p>{class_info.get('description', '')} - {class_info.get('total_methods', 0)} methods</p>
"""
            
            for category, methods in class_info.get('categories', {}).items():
                html += f"""
            <div class="category-section">
                <h3>{category} Methods</h3>
"""
                
                for method in methods:
                    has_examples = "with-examples" if method.get('examples') else "without-examples"
                    has_params = "with-params" if method.get('parameters') else "without-params"
                    html += f"""
                <div class="method-card" data-category="{category}" data-class="{class_name}" data-examples="{has_examples}" data-parameters="{has_params}">
                    <h4>{method['name']}</h4>
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
        "mainClasses/SGEntityType.py"  # SGCellType is defined in SGEntityType.py
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
