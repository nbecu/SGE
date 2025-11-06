from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
from mainClasses.layout.SGLayoutConfigManager import SGLayoutConfigManager


class SGLayoutConfigManagerDialog(QDialog):
    """
    Dialog for managing Enhanced Grid Layout configurations
    
    This dialog provides an interface for viewing, renaming, and deleting saved configurations.
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        self.model = parent
        self.setupUI()
        self.refreshConfigList()
        
    def setupUI(self):
        """Setup the user interface"""
        self.setWindowTitle("Manage Layout Configurations")
        self.setModal(True)
        self.resize(600, 400)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Manage your saved Enhanced Grid Layout configurations.\n"
            "You can view details, rename, delete or load configurations."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { padding: 10px; background-color: #f0f0f0; border-radius: 5px; }")
        layout.addWidget(instructions)
        
        # File location information
        config_manager = SGLayoutConfigManager(self.model)
        config_path = config_manager.config_path
        config_dir = os.path.dirname(config_path)
        
        location_label = QLabel(f"Configuration file location:\n{config_path}")
        location_label.setWordWrap(True)
        location_label.setStyleSheet("QLabel { padding: 8px; background-color: #e8f4fd; border: 1px solid #b3d9ff; border-radius: 3px; font-family: monospace; }")
        layout.addWidget(location_label)
        
        # Configuration list
        self.config_list = QListWidget()
        self.config_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.config_list.itemSelectionChanged.connect(self.onSelectionChanged)
        layout.addWidget(self.config_list)
        
        # Configuration details
        details_layout = QHBoxLayout()
        
        # Details panel
        details_panel = QGroupBox("Configuration Details")
        details_panel_layout = QVBoxLayout()
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        details_panel_layout.addWidget(self.details_text)
        
        details_panel.setLayout(details_panel_layout)
        details_layout.addWidget(details_panel)
        
        # Action buttons
        button_panel = QGroupBox("Actions")
        button_panel_layout = QVBoxLayout()
        
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
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refreshConfigList)
        
        button_panel_layout.addWidget(self.rename_button)
        button_panel_layout.addWidget(self.delete_button)
        button_panel_layout.addWidget(self.load_button)
        button_panel_layout.addWidget(self.refresh_button)
        button_panel_layout.addStretch()
        
        button_panel.setLayout(button_panel_layout)
        details_layout.addWidget(button_panel)
        
        layout.addLayout(details_layout)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setDefault(True)
        
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def showEvent(self, event):
        """Position the dialog docked to the right of the main window when shown."""
        super().showEvent(event)
        from mainClasses.SGExtensions import position_dialog_to_right
        position_dialog_to_right(self)

    def refreshConfigList(self):
        """Refresh the list of available configurations"""
        self.config_list.clear()
        
        # Get available configurations
        config_manager = SGLayoutConfigManager(self.model)
        configs = config_manager.getAvailableConfigs()
        
        # Ensure configs is a list of strings
        if isinstance(configs, list):
            for config_name in configs:
                if isinstance(config_name, str) and config_name.strip():
                    item = QListWidgetItem(config_name.strip())
                    self.config_list.addItem(item)
        
        # Clear details
        self.details_text.clear()
        self.rename_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.load_button.setEnabled(False)
    
    def onSelectionChanged(self):
        """Handle selection change in configuration list"""
        current_item = self.config_list.currentItem()
        
        if current_item:
            config_name = current_item.text()
            self.showConfigDetails(config_name)
            self.rename_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            self.load_button.setEnabled(True)
        else:
            self.details_text.clear()
            self.rename_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.load_button.setEnabled(False)
    
    def showConfigDetails(self, config_name):
        """Show details for the selected configuration"""
        try:
            # Load configuration file to show details
            config_manager = SGLayoutConfigManager(self.model)
            all_configs = config_manager._loadAllConfigurations()
            
            # Get the specific configuration
            if config_name not in all_configs["configurations"]:
                self.details_text.setText(f"Configuration '{config_name}' not found")
                return
            
            config_data = all_configs["configurations"][config_name]
            
            # Format details
            details = f"Configuration: {config_name}\n"
            details += f"Model: {config_data.get('model_name', 'Unknown')}\n"
            details += f"Layout Type: {config_data.get('layout_type', 'Unknown')}\n"
            details += f"Columns: {config_data.get('num_columns', 'Unknown')}\n"
            details += f"Saved: {config_data.get('timestamp', 'Unknown')}\n"
            details += f"Version: {config_data.get('version', 'Unknown')}\n\n"
            
            # GameSpaces details
            gameSpaces = config_data.get('gameSpaces', {})
            details += f"GameSpaces ({len(gameSpaces)}):\n"
            for gs_id, gs_config in gameSpaces.items():
                position_type = gs_config.get('position_type', 'Unknown')
                layoutOrder = gs_config.get('layoutOrder', 'None')
                details += f"  • {gs_id}: {position_type} (Order: {layoutOrder})\n"
            
            self.details_text.setText(details)
            
        except Exception as e:
            self.details_text.setText(f"Error loading configuration details: {e}")
    
    def renameConfig(self):
        """Rename the selected configuration"""
        current_item = self.config_list.currentItem()
        if not current_item:
            return
        
        old_name = current_item.text()
        
        # Get new name from user
        new_name, ok = QInputDialog.getText(self, "Rename Configuration", 
                                          "Enter new name:", text=old_name)
        
        if ok and new_name.strip() and new_name.strip() != old_name:
            try:
                # Update the configuration name in the JSON file
                config_manager = SGLayoutConfigManager(self.model)
                success = config_manager.renameConfig(old_name, new_name.strip())
                
                if success:
                    QMessageBox.information(self, "Rename Configuration", 
                                           f"Configuration renamed from '{old_name}' to '{new_name.strip()}' successfully.")
                    
                    # Update the list item
                    current_item.setText(new_name.strip())
                    
                    # Refresh details
                    self.showConfigDetails(new_name.strip())
                else:
                    QMessageBox.warning(self, "Rename Failed", 
                                       "Failed to rename the configuration.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error renaming configuration: {e}")
    
    def loadConfig(self):
        """Load the selected configuration"""
        current_item = self.config_list.currentItem()
        if not current_item:
            return
        
        config_name = current_item.text()
        
        try:
            # Load the configuration
            config_manager = SGLayoutConfigManager(self.model)
            success = config_manager.loadConfig(config_name)
            
            if success:
                # Close the dialog after successful load (no confirmation needed)
                self.accept()
            else:
                QMessageBox.warning(self, "Load Failed", 
                                   f"Failed to load configuration '{config_name}'.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading configuration: {e}")
    
    def deleteConfig(self):
        """Delete the selected configuration"""
        current_item = self.config_list.currentItem()
        if not current_item:
            return
        
        config_name = current_item.text()
        
        # Confirm deletion
        reply = QMessageBox.question(self, "Delete Configuration", 
                                   f"Are you sure you want to delete configuration '{config_name}'?\n"
                                   f"This action cannot be undone.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                config_manager = SGLayoutConfigManager(self.model)
                success = config_manager.deleteConfig(config_name)
                
                if success:
                    self.refreshConfigList()
                else:
                    QMessageBox.critical(self, "Error", 
                                       f"Failed to delete configuration '{config_name}'.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Error deleting configuration: {e}")
