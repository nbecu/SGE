import json
import os
import sys
from pathlib import Path
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject


class SGLayoutConfigManager(QObject):
    """
    Manager for Enhanced Grid Layout configurations
    
    Handles saving, loading, and managing layout configurations for SGE models.
    Configurations are saved as JSON files in the application's working directory.
    """
    
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.config_path = self._getConfigPath()
        self.configs_dir = os.path.dirname(self.config_path)
        
    def _getConfigPath(self):
        """
        Get the path for layout configuration file.
        
        Returns:
            str: Path to the layout configuration file
        """
        # Option A: Save in the application's working directory
        script_dir = os.path.dirname(sys.argv[0]) if sys.argv else os.getcwd()
        
        # If script_dir is empty (when running from IDE), use current working directory
        if not script_dir:
            script_dir = os.getcwd()
            
        return os.path.join(script_dir, "layout_config.json")
    
    def _getCurrentModelName(self):
        """Get the current model name"""
        return getattr(self.model, 'name', 'Unnamed Model')
    
    def _ensureConfigsDirectory(self):
        """Ensure the configurations directory exists"""
        if not os.path.exists(self.configs_dir):
            try:
                os.makedirs(self.configs_dir)
            except OSError as e:
                QMessageBox.critical(None, "Error", 
                                   f"Failed to create configuration directory: {e}")
                return False
        return True
    
    def _loadAllConfigurations(self):
        """
        Load all configurations from the JSON file.
        
        Returns:
            dict: Dictionary containing all configurations
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Ensure the structure is correct
                    if "configurations" not in data:
                        # Migrate old format to new format
                        if "config_name" in data:
                            old_config_name = data.get("config_name", "default")
                            return {"configurations": {old_config_name: data}}
                        else:
                            return {"configurations": {}}
                    return data
            except Exception:
                pass
        
        # Return empty structure if file doesn't exist or is corrupted
        return {"configurations": {}}
    
    def saveConfig(self, config_name):
        """
        Save current Enhanced Grid Layout configuration.
        
        Args:
            config_name (str): Name for the configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._ensureConfigsDirectory():
            return False
            
        if self.model.typeOfLayout != "enhanced_grid":
            QMessageBox.warning(None, "Warning", 
                               "Layout configuration can only be saved for Enhanced Grid Layout")
            return False
        
        try:
            # Load existing configurations
            all_configs = self._loadAllConfigurations()
            
            # Export configuration from Enhanced Grid Layout
            config_data = self.model.layoutOfModel.exportConfiguration()
            
            # Add metadata
            config_data.update({
                "model_name": getattr(self.model, 'name', 'Unnamed Model'),
                "layout_type": self.model.typeOfLayout,
                "timestamp": self._getCurrentTimestamp(),
                "version": "1.0"
            })
            
            # Add this configuration to the collection
            all_configs["configurations"][config_name] = config_data
            
            # Save all configurations to file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(all_configs, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            QMessageBox.critical(None, "Error", 
                               f"Failed to save layout configuration: {e}")
            return False
    
    def loadConfig(self, config_name):
        """
        Load a saved Enhanced Grid Layout configuration.
        
        Args:
            config_name (str): Name of the configuration to load
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.model.typeOfLayout != "enhanced_grid":
            QMessageBox.warning(None, "Warning", 
                               "Layout configuration can only be loaded for Enhanced Grid Layout")
            return False
        
        if not os.path.exists(self.config_path):
            QMessageBox.warning(None, "Warning", 
                               f"Configuration file not found: {self.config_path}")
            return False
        
        try:
            # Load all configurations
            all_configs = self._loadAllConfigurations()
            
            # Check if the requested configuration exists
            if config_name not in all_configs["configurations"]:
                QMessageBox.warning(None, "Warning", 
                                   f"Configuration '{config_name}' not found")
                return False
            
            # Get the specific configuration
            config_data = all_configs["configurations"][config_name]
            current_model_name = self._getCurrentModelName()
            
            # Check if the configuration belongs to the current model
            if config_data.get("model_name") != current_model_name:
                QMessageBox.warning(None, "Warning", 
                                   f"Configuration '{config_name}' does not belong to the current model '{current_model_name}'")
                return False
            
            # Validate configuration
            if not self._validateConfig(config_data):
                return False
            
            # Import configuration to Enhanced Grid Layout
            success = self.model.layoutOfModel.importConfiguration(config_data)
            
            if success:
                # Apply the layout
                self.model.applyAutomaticLayout()
                return True
            else:
                QMessageBox.critical(None, "Error", 
                                   "Failed to apply layout configuration")
                return False
                
        except Exception as e:
            QMessageBox.critical(None, "Error", 
                               f"Failed to load layout configuration: {e}")
            return False
    
    def configExists(self, config_name):
        """
        Check if a configuration exists for the current model.
        
        Args:
            config_name (str): Name of the configuration to check
            
        Returns:
            bool: True if configuration exists, False otherwise
        """
        try:
            all_configs = self._loadAllConfigurations()
            current_model_name = self._getCurrentModelName()
            
            if config_name not in all_configs["configurations"]:
                return False
                
            # Check if the configuration belongs to the current model
            config_data = all_configs["configurations"][config_name]
            return config_data.get("model_name") == current_model_name
        except Exception:
            return False
    
    def getAvailableConfigs(self):
        """
        Get list of available configuration names for the current model.
        
        Returns:
            list: List of configuration names
        """
        configs = []
        
        try:
            all_configs = self._loadAllConfigurations()
            current_model_name = self._getCurrentModelName()
            
            # Filter configurations by model name
            for config_name, config_data in all_configs["configurations"].items():
                if config_data.get("model_name") == current_model_name:
                    configs.append(config_name)
        except Exception:
            pass
        
        return configs
    
    def renameConfig(self, old_name, new_name):
        """
        Rename a saved configuration.
        
        Args:
            old_name (str): Current name of the configuration
            new_name (str): New name for the configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load all configurations
            all_configs = self._loadAllConfigurations()
            
            # Check if the old configuration exists
            if old_name not in all_configs["configurations"]:
                QMessageBox.warning(None, "Warning", 
                                   f"Configuration '{old_name}' not found")
                return False
            
            # Check if the configuration belongs to the current model
            config_data = all_configs["configurations"][old_name]
            current_model_name = self._getCurrentModelName()
            if config_data.get("model_name") != current_model_name:
                QMessageBox.warning(None, "Warning", 
                                   f"Configuration '{old_name}' does not belong to the current model '{current_model_name}'")
                return False
            
            # Check if new name already exists
            if new_name in all_configs["configurations"]:
                QMessageBox.warning(None, "Warning", 
                                   f"Configuration '{new_name}' already exists")
                return False
            
            # Get the configuration data
            config_data = all_configs["configurations"][old_name]
            
            # Update timestamp
            config_data['timestamp'] = self._getCurrentTimestamp()
            
            # Remove old configuration and add with new name
            del all_configs["configurations"][old_name]
            all_configs["configurations"][new_name] = config_data
            
            # Save back to file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(all_configs, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            QMessageBox.critical(None, "Error", 
                               f"Failed to rename configuration: {e}")
            return False
    
    def _validateConfig(self, config_data):
        """
        Validate configuration data.
        
        Args:
            config_data (dict): Configuration data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_keys = ['layout_type', 'num_columns', 'gameSpaces']
        
        for key in required_keys:
            if key not in config_data:
                QMessageBox.critical(None, "Error", 
                                   f"Invalid configuration: missing '{key}'")
                return False
        
        if config_data['layout_type'] != 'enhanced_grid':
            QMessageBox.critical(None, "Error", 
                               "Configuration is not for Enhanced Grid Layout")
            return False
        
        return True
    
    def _getCurrentTimestamp(self):
        """Get current timestamp as string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def deleteConfig(self, config_name):
        """
        Delete a saved configuration.
        
        Args:
            config_name (str): Name of the configuration to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load all configurations
            all_configs = self._loadAllConfigurations()
            
            # Check if the configuration exists
            if config_name not in all_configs["configurations"]:
                QMessageBox.warning(None, "Warning", 
                                   f"Configuration '{config_name}' not found")
                return False
            
            # Check if the configuration belongs to the current model
            config_data = all_configs["configurations"][config_name]
            current_model_name = self._getCurrentModelName()
            if config_data.get("model_name") != current_model_name:
                QMessageBox.warning(None, "Warning", 
                                   f"Configuration '{config_name}' does not belong to the current model '{current_model_name}'")
                return False
            
            # Remove the configuration
            del all_configs["configurations"][config_name]
            
            # If no configurations left, remove the file
            if not all_configs["configurations"]:
                if os.path.exists(self.config_path):
                    os.remove(self.config_path)
            else:
                # Save the updated configurations
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(all_configs, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            QMessageBox.critical(None, "Error", 
                               f"Failed to delete configuration: {e}")
            return False
