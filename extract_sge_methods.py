#!/usr/bin/env python3
"""
SGE Methods Extractor
Extracts modeler methods from SGE classes and generates structured JSON glossary
"""

import ast
import json
import re
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
    
    def generate_json_glossary(self, methods_data: Dict[str, List[MethodInfo]]) -> str:
        """Generate JSON glossary from extracted methods"""
        glossary = {}
        
        for class_name, methods in methods_data.items():
            class_info = {
                'class_name': class_name,
                'description': f"{class_name} model class for SGE framework",
                'categories': {}
            }
            
            # Group methods by category
            for method in methods:
                category = method.category
                if category not in class_info['categories']:
                    class_info['categories'][category] = []
                
                method_dict = asdict(method)
                class_info['categories'][category].append(method_dict)
            
            glossary[class_name] = class_info
        
        return json.dumps(glossary, indent=2, ensure_ascii=False)

def main():
    """Main function to extract methods from multiple SGE classes"""
    extractor = SGEMethodExtractor()
    
    # List of SGE classes to extract
    sge_classes = [
        "mainClasses/SGCell.py",
        "mainClasses/SGEntity.py", 
        "mainClasses/SGCellType.py",
        "mainClasses/SGEntityType.py"
    ]
    
    all_methods_data = {}
    
    for file_path in sge_classes:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        print(f"Extracting methods from {file_path}...")
        methods_data = extractor.extract_methods_from_file(file_path)
        
        if methods_data:
            all_methods_data.update(methods_data)
        else:
            print(f"No modeler methods found in {file_path}")
    
    if not all_methods_data:
        print("No methods found in any class")
        return
    
    # Generate JSON
    json_glossary = extractor.generate_json_glossary(all_methods_data)
    
    # Save to file
    output_file = "sge_glossary_multi_class.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(json_glossary)
    
    print(f"\nGlossary saved to {output_file}")
    
    # Print summary
    total_methods = 0
    for class_name, methods in all_methods_data.items():
        print(f"\n{class_name}: {len(methods)} modeler methods found")
        total_methods += len(methods)
        for method in methods:
            print(f"  - {method.name} ({method.category})")
    
    print(f"\nTotal: {total_methods} modeler methods across {len(all_methods_data)} classes")

if __name__ == "__main__":
    main()
