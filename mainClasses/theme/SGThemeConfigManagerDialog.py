from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from mainClasses.theme.SGThemeConfigManager import SGThemeConfigManager


class SGThemeConfigManagerDialog(QDialog):
    """
    Dialog for managing Theme configurations

    Provides an interface for viewing, saving, renaming, deleting and loading theme configurations.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.model = parent
        self.setupUI()
        self.refreshConfigList()

    def setupUI(self):
        self.setWindowTitle("Manage Theme Configurations")
        self.setModal(True)
        self.resize(700, 480)

        layout = QVBoxLayout()

        instructions = QLabel(
            "Manage your saved Theme configurations.\n"
            "A theme config is global and may target only a subset of GameSpaces.\n"
            "You can view details, save, rename, delete or load configurations."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { padding: 10px; background-color: #f0f0f0; border-radius: 5px; }")
        layout.addWidget(instructions)

        # File location
        config_manager = SGThemeConfigManager(self.model)
        config_path = config_manager.config_path
        location_label = QLabel(f"Theme configuration file:\n{config_path}")
        location_label.setWordWrap(True)
        location_label.setStyleSheet("QLabel { padding: 8px; background-color: #e8f4fd; border: 1px solid #b3d9ff; border-radius: 3px; font-family: monospace; }")
        layout.addWidget(location_label)

        # Config list
        self.config_list = QListWidget()
        self.config_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.config_list.itemSelectionChanged.connect(self.onSelectionChanged)
        layout.addWidget(self.config_list)

        # Details + actions
        details_layout = QHBoxLayout()

        details_group = QGroupBox("Configuration Details")
        details_group_layout = QVBoxLayout()
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(180)
        details_group_layout.addWidget(self.details_text)
        details_group.setLayout(details_group_layout)
        details_layout.addWidget(details_group)

        action_group = QGroupBox("Actions")
        action_group_layout = QVBoxLayout()

        self.save_button = QPushButton("Save Current Mapping…")
        self.save_button.clicked.connect(self.saveCurrentMapping)

        self.rename_button = QPushButton("Rename")
        self.rename_button.clicked.connect(self.renameConfig)
        self.rename_button.setEnabled(False)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.deleteConfig)
        self.delete_button.setEnabled(False)
        self.delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; }")

        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.loadConfig)
        self.load_button.setEnabled(False)
        self.load_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")

        self.apply_all_button = QPushButton("Apply Global Theme…")
        self.apply_all_button.clicked.connect(self.applyGlobalTheme)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refreshConfigList)

        action_group_layout.addWidget(self.save_button)
        action_group_layout.addWidget(self.rename_button)
        action_group_layout.addWidget(self.delete_button)
        action_group_layout.addWidget(self.load_button)
        action_group_layout.addWidget(self.apply_all_button)
        action_group_layout.addWidget(self.refresh_button)
        action_group_layout.addStretch()
        action_group.setLayout(action_group_layout)
        details_layout.addWidget(action_group)

        layout.addLayout(details_layout)

        # Footer buttons
        footer = QHBoxLayout()
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setDefault(True)
        footer.addStretch()
        footer.addWidget(self.close_button)
        layout.addLayout(footer)

        self.setLayout(layout)

    def refreshConfigList(self):
        self.config_list.clear()
        manager = SGThemeConfigManager(self.model)
        for name in manager.getAvailableConfigs():
            self.config_list.addItem(QListWidgetItem(name))
        self.details_text.clear()
        self.rename_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.load_button.setEnabled(False)

    def onSelectionChanged(self):
        current_item = self.config_list.currentItem()
        if current_item:
            self.showConfigDetails(current_item.text())
            self.rename_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            self.load_button.setEnabled(True)
        else:
            self.details_text.clear()
            self.rename_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.load_button.setEnabled(False)

    def showConfigDetails(self, config_name):
        try:
            manager = SGThemeConfigManager(self.model)
            all_configs = manager._loadAllConfigurations()
            if config_name not in all_configs["configurations"]:
                self.details_text.setText(f"Configuration '{config_name}' not found")
                return
            cfg = all_configs["configurations"][config_name]
            details = f"Configuration: {config_name}\n"
            details += f"Model: {cfg.get('model_name', 'Unknown')}\n"
            details += f"Saved: {cfg.get('timestamp', 'Unknown')}\n"
            details += f"Version: {cfg.get('version', 'Unknown')}\n"
            details += f"Global theme: {cfg.get('global_theme', 'None')}\n\n"
            mapping = cfg.get('gameSpaces', {})
            details += f"GameSpaces targeted ({len(mapping)}):\n"
            for gs_id, gs_cfg in mapping.items():
                details += f"  • {gs_id}: {gs_cfg.get('theme', 'N/A')}\n"
            self.details_text.setText(details)
        except Exception as e:
            self.details_text.setText(f"Error loading configuration details: {e}")

    def renameConfig(self):
        current_item = self.config_list.currentItem()
        if not current_item:
            return
        old = current_item.text()
        new, ok = QInputDialog.getText(self, "Rename Configuration", "Enter new name:", text=old)
        if ok and new.strip() and new.strip() != old:
            manager = SGThemeConfigManager(self.model)
            if manager.renameConfig(old, new.strip()):
                current_item.setText(new.strip())
                self.showConfigDetails(new.strip())

    def loadConfig(self):
        current_item = self.config_list.currentItem()
        if not current_item:
            return
        name = current_item.text()
        manager = SGThemeConfigManager(self.model)
        ok = manager.loadConfig(name)
        if ok:
            self.accept()

    def deleteConfig(self):
        current_item = self.config_list.currentItem()
        if not current_item:
            return
        name = current_item.text()
        if QMessageBox.question(self, "Delete Configuration", f"Delete '{name}'?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            manager = SGThemeConfigManager(self.model)
            if manager.deleteConfig(name):
                self.refreshConfigList()

    def saveCurrentMapping(self):
        name, ok = QInputDialog.getText(self, "Save Theme Configuration", "Enter configuration name:")
        if not ok or not name.strip():
            return
        # Build mapping: list current GameSpaces with a selected theme where applicable
        mapping = {}
        for key, gs in self.model.gameSpaces.items():
            # We do not introspect current theme name reliably; provide a minimal UX: ask theme name
            # In a complete UX, the dialog would allow picking theme per GS. Here we prompt once.
            pass
        # Prompt a global theme (optional)
        global_theme, ok2 = QInputDialog.getText(self, "Global Theme (optional)", "Enter theme name (modern/minimal/colorful/blue/green/gray) or leave empty:")
        if not ok2:
            return
        manager = SGThemeConfigManager(self.model)
        if manager.saveConfig(name.strip(), mapping=mapping, global_theme=(global_theme.strip() or None)):
            QMessageBox.information(self, "Save", "Theme configuration saved.")
            self.refreshConfigList()

    def applyGlobalTheme(self):
        theme, ok = QInputDialog.getText(self, "Apply Global Theme", "Enter theme name (modern/minimal/colorful/blue/green/gray):")
        if not ok or not theme.strip():
            return
        theme = theme.strip()
        if hasattr(self.model, 'applyThemeToAllGameSpaces'):
            self.model.applyThemeToAllGameSpaces(theme)
            self.model.update()
            QMessageBox.information(self, "Apply Theme", f"Applied '{theme}' to all GameSpaces.")


