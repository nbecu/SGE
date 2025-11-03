from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class SGThemeCodeGeneratorDialog(QDialog):
    """
    Dialog to generate Python code for a custom theme.
    
    Allows developers to export a custom theme as Python code that can be
    added to SGAspect.py to make it a predefined theme.
    """

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Generate Theme Code")
        self.resize(800, 600)
        self._buildUI()

    def _buildUI(self):
        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel(
            "Select a custom theme to generate Python code.\n"
            "The generated code can be copied and added to SGAspect.py to make it a predefined theme."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { padding: 10px; background-color: #f0f0f0; border-radius: 5px; }")
        layout.addWidget(instructions)

        # Theme selection
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Custom theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.currentTextChanged.connect(self._onThemeSelected)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # Code display
        code_label = QLabel("Generated Python code:")
        code_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(code_label)

        self.code_text = QTextEdit()
        self.code_text.setReadOnly(True)
        self.code_text.setFont(QFont("Consolas", 10))
        self.code_text.setStyleSheet("QTextEdit { background-color: #f8f8f8; border: 1px solid #ccc; }")
        layout.addWidget(self.code_text)

        # Buttons
        button_layout = QHBoxLayout()
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self._onCopy)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)

        button_layout.addStretch()
        button_layout.addWidget(copy_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Populate theme list
        self._populateThemes()

    def _populateThemes(self):
        """Populate the combo box with available custom themes."""
        self.theme_combo.clear()
        self.theme_combo.addItem("")  # Empty option
        
        # Get custom themes from model
        if hasattr(self.model, '_runtime_themes') and isinstance(self.model._runtime_themes, dict):
            custom_themes = sorted([name for name in self.model._runtime_themes.keys()])
            for theme_name in custom_themes:
                self.theme_combo.addItem(theme_name)
        
        # Also check for custom themes in theme_config.json
        try:
            from mainClasses.theme.SGThemeConfigManager import SGThemeConfigManager
            manager = SGThemeConfigManager(self.model)
            # TODO: Load custom themes from theme_config.json if they're stored there
        except Exception:
            pass

    def _onThemeSelected(self, theme_name):
        """Generate code when a theme is selected."""
        if not theme_name:
            self.code_text.clear()
            return
        
        if not hasattr(self.model, '_runtime_themes') or theme_name not in self.model._runtime_themes:
            self.code_text.setPlainText(f"# Theme '{theme_name}' not found in custom themes.")
            return
        
        theme_spec = self.model._runtime_themes[theme_name]
        code = self._generateCode(theme_name, theme_spec)
        self.code_text.setPlainText(code)

    def _generateCode(self, theme_name, theme_spec):
        """Generate Python code for the theme."""
        base = theme_spec.get('base', {})
        text_aspects = theme_spec.get('text_aspects', {})
        
        # Method name: convert theme_name to valid Python method name
        method_name = theme_name.lower().replace(' ', '_').replace('-', '_')
        # Remove special characters
        method_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in method_name)
        
        lines = []
        lines.append(f"    @classmethod")
        lines.append(f"    def {method_name}(cls):")
        
        # Description
        description = f'Theme: {theme_name}'
        lines.append(f'        """{description}"""')
        
        lines.append(f"        instance = cls()")
        lines.append("")
        
        # Base properties - order matches existing themes
        if base.get('background_color'):
            color_str = self._formatColor(base['background_color'])
            lines.append(f"        instance.background_color = {color_str}")
        if base.get('border_color'):
            color_str = self._formatColor(base['border_color'])
            lines.append(f"        instance.border_color = {color_str}")
        if base.get('border_size') is not None:
            lines.append(f"        instance.border_size = {base['border_size']}")
        if base.get('border_style'):
            lines.append(f"        instance.border_style = {repr(base['border_style'])}")
        if base.get('color'):
            color_str = self._formatColor(base['color'])
            lines.append(f"        instance.color = {color_str}")
        if base.get('font'):
            lines.append(f"        instance.font = {repr(base['font'])}")
        if base.get('size') is not None:
            lines.append(f"        instance.size = {base['size']}")
        if base.get('font_weight'):
            lines.append(f"        instance.font_weight = {repr(base['font_weight'])}")
        if base.get('border_radius') is not None:
            lines.append(f"        instance.border_radius = {base['border_radius']}")
        if base.get('padding') is not None:
            lines.append(f"        instance.padding = {base['padding']}")
        if base.get('background_image'):
            lines.append(f"        instance.background_image = {repr(base['background_image'])}")
        
        # Text aspects
        if text_aspects:
            lines.append("        # Add text_aspects structure for differentiated text styling")
            lines.append("        instance._text_aspects = {")
            
            aspect_keys = ['title1', 'title2', 'title3', 'text1', 'text2', 'text3']
            for key in aspect_keys:
                if key in text_aspects and text_aspects[key]:
                    spec = text_aspects[key]
                    # Only include non-None, non-empty values
                    props = []
                    if spec.get('color'):
                        color_str = self._formatColor(spec['color'])
                        props.append(f"'color': {color_str}")
                    if spec.get('font'):
                        props.append(f"'font': {repr(spec['font'])}")
                    if spec.get('size') is not None:
                        props.append(f"'size': {spec['size']}")
                    if spec.get('font_weight'):
                        props.append(f"'font_weight': {repr(spec['font_weight'])}")
                    if spec.get('font_style'):
                        props.append(f"'font_style': {repr(spec['font_style'])}")
                    if spec.get('text_decoration'):
                        props.append(f"'text_decoration': {repr(spec['text_decoration'])}")
                    if spec.get('alignment'):
                        props.append(f"'alignment': {repr(spec['alignment'])}")
                    
                    if props:
                        # Format with proper indentation
                        props_str = ", ".join(props)
                        lines.append(f"            '{key}': {{{props_str}}},")
            
            lines.append("        }")
        
        lines.append("        return instance")
        lines.append("")
        
        return "\n".join(lines)

    def _formatColor(self, color):
        """Format color value for Python code."""
        if color is None:
            return "None"
        if isinstance(color, str):
            # If it's already a valid Python string representation, return it
            if color.startswith("'") or color.startswith('"'):
                return color
            # Otherwise, quote it
            return repr(color)
        # For QColor or other types, convert to string representation
        return repr(str(color))

    def _onCopy(self):
        """Copy generated code to clipboard."""
        text = self.code_text.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            QMessageBox.information(self, "Copied", "Code copied to clipboard!")
        else:
            QMessageBox.warning(self, "No Code", "No code to copy. Please select a theme first.")


