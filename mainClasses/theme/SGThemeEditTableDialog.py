from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from mainClasses.theme.SGThemeCustomEditorDialog import SGThemeCustomEditorDialog
from mainClasses.theme.SGThemeCodeGeneratorDialog import SGThemeCodeGeneratorDialog


class SGThemeEditTableDialog(QDialog):
    """
    Dialog to assign themes to GameSpaces using a table, similar to layout order editor.
    Applies selected themes to listed GameSpaces on OK.
    """

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self._themes = self._discoverPredefinedThemes()
        self._gs_cache = list(self.model.gameSpaces.values())
        self._id_to_gs = {gs.id: gs for gs in self._gs_cache}
        self.setupUI()
        self.populateTable()
    
    def _discoverPredefinedThemes(self):
        """Discover all predefined themes in SGAspect dynamically."""
        from mainClasses.SGAspect import SGAspect
        # Known utility methods that are NOT themes
        excluded_methods = {
            'baseBorder', 'title1', 'title2', 'title3', 
            'text1', 'text2', 'text3', 'success', 'inactive'
        }
        themes = []
        # Inspect all class methods
        for name in dir(SGAspect):
            if name.startswith('_'):
                continue
            attr = getattr(SGAspect, name, None)
            if attr and callable(attr):
                # Exclude known utility methods
                if name in excluded_methods:
                    continue
                # Only consider classmethods (not instance methods)
                # When accessing @classmethod via getattr on the class, Python returns
                # a bound method (type 'method'), not a classmethod object
                # Try calling it without arguments - classmethods work, instance methods need self
                try:
                    # Skip getter methods (they start with 'get' and are instance methods)
                    if name.startswith('get'):
                        continue
                    instance = attr()
                    if isinstance(instance, SGAspect):
                        themes.append(name)
                except TypeError:
                    # Needs arguments (likely an instance method), skip it
                    continue
                except Exception:
                    # Any other error, skip it
                    continue
        return sorted(themes)

    def setupUI(self):
        self.setWindowTitle("Theme Assignment - GameSpaces")
        self.setModal(True)
        self.resize(700, 480)

        layout = QVBoxLayout()

        # Header with instructions and Theme code button
        header_layout = QHBoxLayout()
        instructions = QLabel(
            "Assign a theme to each GameSpace. Leave blank to keep it unchanged."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { padding: 10px; background-color: #f0f0f0; border-radius: 5px; }")
        header_layout.addWidget(instructions, 1)
        
        theme_code_btn = QPushButton("Theme code...")
        theme_code_btn.setToolTip("Generate Python code for custom themes (for developers)")
        theme_code_btn.clicked.connect(self._openThemeCodeGenerator)
        header_layout.addWidget(theme_code_btn)
        
        layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        # No title for the Actions column
        self.table.setHorizontalHeaderLabels(["GameSpace Type", "ID", "Theme", ""]) 
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        # Make actions column fixed and narrow
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 60)
        layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.applyChanges)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def showEvent(self, event):
        """Position the dialog docked to the right of the main window when shown."""
        super().showEvent(event)
        try:
            parent = self.parent() if isinstance(self.parent(), QWidget) else None
            if parent is None and hasattr(self, 'model') and isinstance(self.model, QWidget):
                parent = self.model
            if parent is None:
                return
            # Parent frame geometry is already in global coords
            pg = parent.frameGeometry() if hasattr(parent, 'frameGeometry') else parent.geometry()
            # Compute desired to-the-right position
            target_x = pg.right()
            target_y = pg.top()
            # Fit inside available screen geometry of the parent's screen
            desk = QApplication.desktop()
            try:
                screen_num = desk.screenNumber(parent)
                available = desk.availableGeometry(screen_num)
            except Exception:
                available = desk.availableGeometry()
            w = self.width()
            h = self.height()
            # Adjust if overflowing to the right/bottom
            if target_x + w > available.right():
                target_x = max(available.left(), available.right() - w)
            if target_y + h > available.bottom():
                target_y = max(available.top(), available.bottom() - h)
            self.move(target_x, target_y)
        except Exception:
            pass

    def populateTable(self):
        self.table.setRowCount(len(self._gs_cache))
        # Extend theme list with runtime themes saved in model
        runtime = []
        if hasattr(self.model, '_runtime_themes') and isinstance(self.model._runtime_themes, dict):
            runtime = sorted(list(self.model._runtime_themes.keys()))
        all_themes = [""] + ["custom"] + self._themes + [t for t in runtime if t not in self._themes]
        for row, gs in enumerate(self._gs_cache):
            # Type
            type_item = QTableWidgetItem(gs.__class__.__name__)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            type_item.setBackground(QColor(240, 240, 240))
            self.table.setItem(row, 0, type_item)

            # ID
            id_item = QTableWidgetItem(gs.id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            id_item.setBackground(QColor(240, 240, 240))
            self.table.setItem(row, 1, id_item)

            # Theme combobox
            combo = QComboBox()
            for t in all_themes:
                combo.addItem(t)
            # Pre-select current theme if available
            current = getattr(gs, 'current_theme_name', None)
            overridden = getattr(gs, 'theme_overridden', False)
            if overridden:
                combo.setCurrentText("custom")
            elif current and current in all_themes:
                combo.setCurrentText(current)
            self.table.setCellWidget(row, 2, combo)

            # Actions: always show an Edit button to open the Custom Editor
            action_widget = QWidget()
            h = QHBoxLayout()
            h.setContentsMargins(2, 2, 2, 2)
            h.setAlignment(Qt.AlignLeft)
            btn = QPushButton("Edit…")
            btn.setMaximumHeight(24)
            btn.setFixedWidth(60)
            # Pass the current selected theme in the same row to initialize the editor
            btn.clicked.connect(lambda _, r=row, gsid=gs.id: self.openCustomEditorWithRow(gsid, r))
            h.addWidget(btn)
            action_widget.setLayout(h)
            self.table.setCellWidget(row, 3, action_widget)

    def openCustomEditor(self, gs_id):
        # Backward compatibility (no preset theme)
        self.openCustomEditorWithRow(gs_id, None)

    def openCustomEditorWithRow(self, gs_id, row_index):
        gs = self._id_to_gs.get(gs_id)
        if not gs:
            return
        init_theme = None
        if row_index is not None:
            combo = self.table.cellWidget(row_index, 2)
            if isinstance(combo, QComboBox):
                t = combo.currentText().strip()
                if t and t != "custom":
                    init_theme = t
        editor = SGThemeCustomEditorDialog(self.model, gs, self, init_theme=init_theme)
        editor.exec_()
        # After closing editor, refresh table to reflect new runtime themes and selection
        self.populateTable()

    def accept(self):
        # Apply selected themes and close
        self.applyChanges()
        super().accept()

    def applyChanges(self):
        # Apply selected themes without closing
        for row in range(self.table.rowCount()):
            id_item = self.table.item(row, 1)
            if not id_item:
                continue
            gs_id = id_item.text()
            combo = self.table.cellWidget(row, 2)
            if not combo:
                continue
            theme = combo.currentText().strip()
            # Skip blank and "custom" (custom means keep overridden styles)
            if theme and theme != "custom":
                gs = self._id_to_gs.get(gs_id)
                if gs and hasattr(gs, 'applyTheme'):
                    try:
                        gs.applyTheme(theme)
                    except Exception:
                        pass
        if hasattr(self.model, 'update'):
            self.model.update()

    def _openThemeCodeGenerator(self):
        """Open the Theme Code Generator dialog."""
        dialog = SGThemeCodeGeneratorDialog(self.model, self)
        dialog.exec_()


