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
        self.resize(650, 420)  # Reduced size for more compact interface

        layout = QVBoxLayout()
        layout.setSpacing(8)  # Reduce spacing between elements

        # Compact instructions
        instructions = QLabel(
            "Manage your saved Theme configurations. Save, rename, delete or apply configurations."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { padding: 6px; background-color: #f0f0f0; border-radius: 3px; font-size: 10pt; }")
        layout.addWidget(instructions)

        # Compact file location
        config_manager = SGThemeConfigManager(self.model)
        config_path = config_manager.config_path
        location_label = QLabel(f"Config file: {config_path}")
        location_label.setWordWrap(True)
        location_label.setStyleSheet("QLabel { padding: 4px; background-color: #e8f4fd; border: 1px solid #b3d9ff; border-radius: 2px; font-family: monospace; font-size: 9pt; }")
        layout.addWidget(location_label)

        # Config list + Actions/Details (side by side)
        list_right_layout = QHBoxLayout()
        
        # Config list (left side)
        list_container = QVBoxLayout()
        list_label = QLabel("Configurations:")
        list_label.setStyleSheet("QLabel { font-weight: bold; }")
        list_container.addWidget(list_label)
        self.config_list = QListWidget()
        self.config_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.config_list.itemSelectionChanged.connect(self.onSelectionChanged)
        list_container.addWidget(self.config_list)
        list_widget = QWidget()
        list_widget.setLayout(list_container)
        list_right_layout.addWidget(list_widget, stretch=1)  # 50% of width

        # Right side: Actions + Details + Apply buttons (vertical)
        right_container = QVBoxLayout()
        right_container.setSpacing(8)
        
        # Actions (top)
        action_group = QGroupBox("Actions")
        action_group_layout = QVBoxLayout()
        action_group_layout.setSpacing(6)  # Reduced spacing

        self.save_button = QPushButton("Save Current Mapping…")
        self.save_button.clicked.connect(self.saveCurrentMapping)

        self.rename_button = QPushButton("Rename")
        self.rename_button.clicked.connect(self.renameConfig)
        self.rename_button.setEnabled(False)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.deleteConfig)
        self.delete_button.setEnabled(False)
        self.delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; }")

        action_group_layout.addWidget(self.save_button)
        action_group_layout.addWidget(self.rename_button)
        action_group_layout.addWidget(self.delete_button)
        action_group.setLayout(action_group_layout)
        right_container.addWidget(action_group)

        # Details (middle)
        details_group = QGroupBox("Configuration Details")
        details_group_layout = QVBoxLayout()
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(100)  # Reduced height
        details_group_layout.addWidget(self.details_text)
        details_group.setLayout(details_group_layout)
        right_container.addWidget(details_group)
        
        # Apply buttons (bottom)
        apply_buttons_layout = QHBoxLayout()
        apply_buttons_layout.setSpacing(6)
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.applyConfig)
        self.apply_button.setEnabled(False)
        self.apply_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        
        self.apply_and_close_button = QPushButton("Apply & Close")
        self.apply_and_close_button.clicked.connect(self.applyConfigAndClose)
        self.apply_and_close_button.setEnabled(False)
        self.apply_and_close_button.setDefault(True)
        
        apply_buttons_layout.addWidget(self.apply_button)
        apply_buttons_layout.addWidget(self.apply_and_close_button)
        right_container.addLayout(apply_buttons_layout)
        
        right_container.addStretch()  # Push all content to top
        
        right_widget = QWidget()
        right_widget.setLayout(right_container)
        list_right_layout.addWidget(right_widget, stretch=1)  # 50% of width

        layout.addLayout(list_right_layout)

        self.setLayout(layout)

    def showEvent(self, event):
        """Position the dialog docked to the right of the main window when shown."""
        super().showEvent(event)
        from mainClasses.SGExtensions import position_dialog_to_right
        position_dialog_to_right(self)

    def refreshConfigList(self):
        self.config_list.clear()
        manager = SGThemeConfigManager(self.model)
        for name in manager.getAvailableConfigs():
            self.config_list.addItem(QListWidgetItem(name))
        self.details_text.clear()
        self.rename_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.apply_button.setEnabled(False)
        self.apply_and_close_button.setEnabled(False)

    def onSelectionChanged(self):
        current_item = self.config_list.currentItem()
        if current_item:
            self.showConfigDetails(current_item.text())
            self.rename_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            self.apply_button.setEnabled(True)
            self.apply_and_close_button.setEnabled(True)
        else:
            self.details_text.clear()
            self.rename_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.apply_button.setEnabled(False)
            self.apply_and_close_button.setEnabled(False)

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

    def applyConfig(self):
        """Apply the selected configuration without closing the dialog"""
        current_item = self.config_list.currentItem()
        if not current_item:
            return
        
        config_name = current_item.text()
        
        try:
            # Load and apply the configuration
            config_manager = SGThemeConfigManager(self.model)
            config_manager.loadConfig(config_name)
            # No confirmation dialog - silently apply
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error applying configuration: {e}")

    def applyConfigAndClose(self):
        """Apply the selected configuration and close the dialog"""
        current_item = self.config_list.currentItem()
        if not current_item:
            return
        
        config_name = current_item.text()
        
        try:
            # Load and apply the configuration
            config_manager = SGThemeConfigManager(self.model)
            success = config_manager.loadConfig(config_name)
            
            if success:
                # Close the dialog after successful apply
                self.accept()
            else:
                QMessageBox.warning(self, "Apply Failed", 
                                   f"Failed to apply configuration '{config_name}'.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error applying configuration: {e}")

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
        
        # Build mapping: collect current GameSpaces with their assigned themes
        mapping = {}
        for key, gs in self.model.gameSpaces.items():
            # Get GameSpace ID (prefer gs.id, fallback to key)
            gs_id = getattr(gs, 'id', None) or key
            
            # Only include GameSpaces that have a theme assigned (not overridden)
            # If theme_overridden is True, the GameSpace has custom styling, not a theme
            if hasattr(gs, 'current_theme_name') and gs.current_theme_name:
                # Check if theme is still valid (not overridden with custom styling)
                if not getattr(gs, 'theme_overridden', True):
                    mapping[str(gs_id)] = {"theme": gs.current_theme_name}
        
        # Save configuration without global_theme (it's not used during loading anyway)
        # global_theme was stored as metadata but never actually applied when loading configurations
        manager = SGThemeConfigManager(self.model)
        if manager.saveConfig(name.strip(), mapping=mapping, global_theme=None):
            count = len(mapping)
            if count > 0:
                msg = f"Theme configuration saved with {count} GameSpace(s)."
            else:
                msg = "Theme configuration saved (no GameSpaces with assigned themes found)."
            QMessageBox.information(self, "Save", msg)
            self.refreshConfigList()


