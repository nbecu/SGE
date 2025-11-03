from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
from mainClasses.layout.SGLayoutConfigManager import SGLayoutConfigManager


class SGLayoutConfigSaveDialog(QDialog):
    """
    Dialog for saving Enhanced Grid Layout configuration
    
    This dialog provides an interface for naming and saving layout configurations.
    """
    
    def __init__(self, parent, available_configs):
        super().__init__(parent)
        self.available_configs = available_configs
        self.setupUI()
        
    def setupUI(self):
        """Setup the user interface"""
        self.setWindowTitle("Save Layout Configuration")
        self.setModal(True)
        self.resize(500, 300)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(2)  # Reduce spacing between widgets
        
        # Instructions
        instructions = QLabel(
            "Save the current Enhanced Grid Layout configuration for future use.\n"
            "This will save all gameSpace positions, layoutOrders, and column settings."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { padding: 0px; background-color: #f0f0f0; border-radius: 5px; }")
        layout.addWidget(instructions)
        
        # File location information
        config_manager = SGLayoutConfigManager(self.parent())
        config_path = config_manager.config_path
        config_dir = os.path.dirname(config_path)
        
        location_label = QLabel(f"Configuration will be saved to:\n{config_dir}")
        location_label.setWordWrap(True)
        location_label.setStyleSheet("QLabel { padding: 8px; background-color: #f0f2f5; border: 1px solid #b3d9ff; border-radius: 3px; font-family: monospace; }")
        layout.addWidget(location_label)
        layout.addSpacing(10)
        # Configuration name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Configuration name:"))
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter configuration name...")
        self.name_input.textChanged.connect(self.onNameChanged)
        # Set focus to the input field
        self.name_input.setFocus()
        name_layout.addWidget(self.name_input)
        
        layout.addLayout(name_layout)
        
        # Existing configurations section
        if self.available_configs:
            existing_label = QLabel("Existing configurations:")
            existing_label.setStyleSheet("QLabel { font-weight: bold; margin-top: 10px; }")
            layout.addWidget(existing_label)
            
            self.existing_list = QListWidget()
            self.existing_list.setMaximumHeight(100)
            for config in self.available_configs:
                self.existing_list.addItem(config)
            
            # Connect double-click to fill name input
            self.existing_list.itemDoubleClicked.connect(self.onExistingConfigSelected)
            
            layout.addWidget(self.existing_list)
        
        # Warning for overwrite
        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
        self.warning_label.hide()
        layout.addWidget(self.warning_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.onSaveClicked)
        self.save_button.setDefault(True)
        self.save_button.setEnabled(False)  # Disabled until name is entered
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def showEvent(self, event):
        """Position the dialog docked to the right of the main window when shown."""
        super().showEvent(event)
        from mainClasses.SGExtensions import position_dialog_to_right
        position_dialog_to_right(self)

    def onNameChanged(self, text):
        """Handle name input changes"""
        text = text.strip()
        if text:
            self.save_button.setEnabled(True)
            
            # Check if name already exists
            if text in self.available_configs:
                self.warning_label.setText(f"Warning: Configuration '{text}' already exists and will be overwritten.")
                self.warning_label.show()
            else:
                self.warning_label.hide()
        else:
            self.save_button.setEnabled(False)
            self.warning_label.hide()
    
    def onExistingConfigSelected(self, item):
        """Handle selection of existing configuration"""
        self.name_input.setText(item.text())
    
    def getConfigName(self):
        """Get the entered configuration name"""
        return self.name_input.text().strip()
    
    def onSaveClicked(self):
        """Handle save button click with validation"""
        config_name = self.getConfigName()
        if config_name:
            self.accept()
        else:
            QMessageBox.warning(self, "Warning", "Please enter a configuration name")
            self.name_input.setFocus()
