#!/usr/bin/env python3
"""
SGExeBuilder - SGE Executable Builder
Creates standalone Windows executables from SGE models using PyInstaller

USAGE EXAMPLES:

1. Basic usage:
   from mainClasses.SGExeBuilder import SGExeBuilder
   builder = SGExeBuilder()
   builder.build_exe("examples/games/morpion_game.py")

2. With custom options:
   builder.build_exe(
       model_path="examples/games/mon_jeu.py",
       output_name="MonJeu",
       icon="mon_jeu/icone.ico"
   )

3. Batch export:
   models = ["game1.py", "game2.py", "game3.py"]
   for model in models:
       builder.build_exe(model)
"""

import os
import json
import subprocess
import shutil
from typing import Optional, List, Dict, Any
from pathlib import Path

class SGExeBuilder:
    """
    SGE Executable Builder
    
    Creates standalone Windows executables from SGE models using PyInstaller.
    Automatically includes all SGE dependencies and resources.
    """
    
    def __init__(self):
        """Initialize the SGE executable builder"""
        self.sge_dependencies = self._get_sge_dependencies()
        self.default_icon = "icon/icon_dashboards.png"
        self.default_resources = [
            ('mainClasses', 'mainClasses'),
            ('icon', 'icon'),
            ('images', 'images'),
        ]
    
    def build_exe(self, model_path: str, output_name: Optional[str] = None, 
                  icon: Optional[str] = None, clean: bool = True) -> str:
        """
        Build executable from SGE model
        
        Args:
            model_path (str): Path to the SGE model Python file
            output_name (str, optional): Name for the executable (without .exe)
            icon (str, optional): Path to custom icon file
            clean (bool): Whether to clean build directory before building
            
        Returns:
            str: Path to the generated executable
            
        Raises:
            FileNotFoundError: If model_path doesn't exist
            subprocess.CalledProcessError: If PyInstaller fails
        """
        # Validate model path
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Determine output name
        if output_name is None:
            output_name = self._extract_name_from_path(model_path)
        
        # Determine icon
        if icon is None:
            icon = self.default_icon
        
        print(f"Building executable for {model_path}...")
        print(f"Output name: {output_name}")
        print(f"Icon: {icon}")
        
        # Generate .spec file
        spec_file = self._generate_spec_file(model_path, output_name, icon)
        print(f"Generated spec file: {spec_file}")
        
        # Build executable with PyInstaller
        exe_path = self._run_pyinstaller(spec_file, clean)
        
        print(f"✓ Executable created: {exe_path}")
        return exe_path
    
    def _extract_name_from_path(self, model_path: str) -> str:
        """Extract executable name from model path"""
        filename = os.path.basename(model_path)
        name = os.path.splitext(filename)[0]
        # Convert to PascalCase
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def _generate_spec_file(self, model_path: str, output_name: str, icon: str) -> str:
        """Generate PyInstaller .spec file"""
        spec_content = self._get_spec_template()
        
        # Replace placeholders
        spec_content = spec_content.replace('{{MODEL_PATH}}', model_path)
        spec_content = spec_content.replace('{{OUTPUT_NAME}}', output_name)
        spec_content = spec_content.replace('{{ICON_PATH}}', icon)
        
        # Add SGE dependencies
        hidden_imports = self._format_hidden_imports()
        spec_content = spec_content.replace('{{HIDDEN_IMPORTS}}', hidden_imports)
        
        # Add resources
        datas = self._format_datas()
        spec_content = spec_content.replace('{{DATAS}}', datas)
        
        # Write spec file
        spec_filename = f"{output_name}.spec"
        with open(spec_filename, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        return spec_filename
    
    def _get_spec_template(self) -> str:
        """Get PyInstaller spec file template"""
        return '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{{MODEL_PATH}}'],
    pathex=[],
    binaries=[],
    datas={{DATAS}},
    hiddenimports={{HIDDEN_IMPORTS}},
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{{OUTPUT_NAME}}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{{ICON_PATH}}',
)
'''
    
    def _format_hidden_imports(self) -> str:
        """Format hidden imports for spec file"""
        imports = []
        for dep in self.sge_dependencies:
            imports.append(f"        '{dep}',")
        
        return "[\n" + "\n".join(imports) + "\n    ]"
    
    def _format_datas(self) -> str:
        """Format datas for spec file"""
        datas = []
        for src, dst in self.default_resources:
            if os.path.exists(src):
                datas.append(f"        ('{src}', '{dst}'),")
        
        return "[\n" + "\n".join(datas) + "\n    ]"
    
    def _run_pyinstaller(self, spec_file: str, clean: bool = True) -> str:
        """Run PyInstaller with the spec file"""
        cmd = ["pyinstaller", spec_file]
        
        if clean:
            cmd.append("--clean")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("PyInstaller output:")
            print(result.stdout)
            
            if result.stderr:
                print("PyInstaller warnings:")
                print(result.stderr)
                
        except subprocess.CalledProcessError as e:
            print(f"PyInstaller failed with return code {e.returncode}")
            print(f"Error output: {e.stderr}")
            raise
        
        # Return path to executable
        output_name = os.path.splitext(spec_file)[0]
        exe_path = os.path.join("dist", f"{output_name}.exe")
        
        if not os.path.exists(exe_path):
            raise FileNotFoundError(f"Executable not found: {exe_path}")
        
        return exe_path
    
    def _get_sge_dependencies(self) -> List[str]:
        """Get all SGE dependencies from pyproject.toml and known requirements"""
        dependencies = [
            # PyQt5 modules
            'PyQt5.QtCore',
            'PyQt5.QtGui', 
            'PyQt5.QtWidgets',
            'PyQt5.QtSvg',
            'PyQt5.QtPrintSupport',
            'PyQt5.QtOpenGL',
            'PyQt5.QtNetwork',
            'PyQt5.QtMultimedia',
            'PyQt5.QtTest',
            'PyQt5.QtXml',
            'PyQt5.QtXmlPatterns',
            'PyQt5.QtHelp',
            'PyQt5.QtDesigner',
            'PyQt5.QtSql',
            
            # Core Python modules
            'logging.config',
            'logging.handlers',
            
            # Data processing
            'numpy',
            'pandas',
            'openpyxl',
            'pyparsing',
            'tzdata',
            
            # Visualization
            'matplotlib',
            'matplotlib.backends.backend_qt5agg',
            'matplotlib.backends.backend_qtagg',
            'matplotlib.backends.backend_agg',
            'matplotlib.backends.backend_tkagg',
            'matplotlib.backends.backend_webagg',
            'matplotlib.backends.backend_pdf',
            'matplotlib.backends.backend_svg',
            'matplotlib.backends.backend_ps',
            'matplotlib.backends.backend_eps',
            'matplotlib.backends.backend_pgf',
            'matplotlib.backends.backend_cairo',
            'matplotlib.backends.backend_gdk',
            'matplotlib.backends.backend_gtk3agg',
            'matplotlib.backends.backend_gtk3cairo',
            'matplotlib.backends.backend_gtkagg',
            'matplotlib.backends.backend_gtkcairo',
            'matplotlib.backends.backend_gtk',
            'matplotlib.backends.backend_macosx',
            'matplotlib.backends.backend_qt4agg',
            'matplotlib.backends.backend_qt4cairo',
            'matplotlib.backends.backend_qt5cairo',
            'matplotlib.backends.backend_template',
            'matplotlib.backends.backend_webagg_core',
            'matplotlib.backends.backend_webagg_server',
            'matplotlib.backends.backend_webagg_server_fastapi',
            'matplotlib.backends.backend_webagg_server_flask',
            'matplotlib.backends.backend_webagg_server_starlette',
            
            # Database
            'sqlalchemy',
            'sqlalchemy.orm',
            'sqlalchemy.ext',
            'sqlalchemy.ext.declarative',
            'sqlalchemy.pool',
            'sqlalchemy.engine',
            'sqlalchemy.dialects',
            'sqlalchemy.dialects.sqlite',
            
            # Communication
            'paho.mqtt',
            'paho.mqtt.client',
            'paho.mqtt.publish',
            'paho.mqtt.subscribe',
            
            # System
            'screeninfo',
            'screeninfo.get_monitors',
            'screeninfo.screeninfo',
            
            # Data structures
            'pyrsistent',
        ]
        
        return dependencies
    
    def add_custom_resources(self, resources: List[tuple]):
        """
        Add custom resources to include in the executable
        
        Args:
            resources (List[tuple]): List of (source_path, destination_path) tuples
        """
        self.default_resources.extend(resources)
    
    def add_custom_dependencies(self, dependencies: List[str]):
        """
        Add custom dependencies to include in the executable
        
        Args:
            dependencies (List[str]): List of module names to include
        """
        self.sge_dependencies.extend(dependencies)
    
    def clean_build_files(self):
        """Clean PyInstaller build files"""
        dirs_to_clean = ['build', 'dist']
        files_to_clean = ['*.spec']
        
        for dir_name in dirs_to_clean:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
                print(f"Cleaned directory: {dir_name}")
        
        # Clean spec files
        for spec_file in Path('.').glob('*.spec'):
            spec_file.unlink()
            print(f"Cleaned file: {spec_file}")
    
    def get_build_info(self) -> Dict[str, Any]:
        """Get information about the build configuration"""
        return {
            'dependencies_count': len(self.sge_dependencies),
            'resources_count': len(self.default_resources),
            'default_icon': self.default_icon,
            'dependencies': self.sge_dependencies,
            'resources': self.default_resources
        }

# Example usage
if __name__ == "__main__":
    builder = SGExeBuilder()
    
    # Build morpion game executable
    try:
        exe_path = builder.build_exe("examples/games/morpion_game.py")
        print(f"Success! Executable created: {exe_path}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Show build info
    info = builder.get_build_info()
    print(f"\nBuild info:")
    print(f"Dependencies: {info['dependencies_count']}")
    print(f"Resources: {info['resources_count']}")
