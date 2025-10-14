import json
import os
import sys
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox


class SGThemeConfigManager(QObject):
    """
    Manager for Theme configurations

    Handles saving, loading, and managing theme configurations for SGE models.
    Configurations are saved as JSON files in the application's working directory.
    A configuration is global but may target only a subset of GameSpaces.
    """

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.config_path = self._getConfigPath()

    def _getConfigPath(self):
        """
        Get the path for theme configuration file.

        Returns:
            str: Path to the theme configuration file
        """
        script_dir = os.path.dirname(sys.argv[0]) if sys.argv else os.getcwd()
        if not script_dir:
            script_dir = os.getcwd()
        return os.path.join(script_dir, "theme_config.json")

    def _getCurrentModelName(self):
        """Get the current model name"""
        return getattr(self.model, 'name', 'Unnamed Model')

    def _ensureDirectory(self):
        """Ensure the directory exists"""
        configs_dir = os.path.dirname(self.config_path)
        if not os.path.exists(configs_dir):
            try:
                os.makedirs(configs_dir)
            except OSError as e:
                QMessageBox.critical(None, "Error", f"Failed to create configuration directory: {e}")
                return False
        return True

    def _loadAllConfigurations(self):
        """
        Load all theme configurations from the JSON file.

        Returns:
            dict: {"configurations": {name: data}}
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "configurations" not in data:
                        return {"configurations": {}}
                    return data
            except Exception:
                pass
        return {"configurations": {}}

    def _getCurrentTimestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def saveConfig(self, config_name, mapping=None, global_theme=None):
        """
        Save current Theme configuration.

        Args:
            config_name (str): Name for the configuration
            mapping (dict|None): Optional mapping {gs_id: {"theme": str}}
            global_theme (str|None): Optional global theme name stored as metadata
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._ensureDirectory():
            return False

        try:
            all_configs = self._loadAllConfigurations()

            # Build configuration data
            config_data = {
                "model_name": self._getCurrentModelName(),
                "timestamp": self._getCurrentTimestamp(),
                "version": "1.0",
                "global_theme": global_theme,
                "gameSpaces": mapping or {}
            }

            all_configs["configurations"][config_name] = config_data

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(all_configs, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to save theme configuration: {e}")
            return False

    def loadConfig(self, config_name):
        """
        Load a saved Theme configuration and apply it to listed GameSpaces only.

        Args:
            config_name (str): Name of the configuration to load
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(self.config_path):
            QMessageBox.warning(None, "Warning", f"Configuration file not found: {self.config_path}")
            return False

        try:
            all_configs = self._loadAllConfigurations()
            if config_name not in all_configs["configurations"]:
                QMessageBox.warning(None, "Warning", f"Configuration '{config_name}' not found")
                return False

            config_data = all_configs["configurations"][config_name]
            current_model_name = self._getCurrentModelName()

            if config_data.get("model_name") != current_model_name:
                QMessageBox.warning(None, "Warning", f"Configuration '{config_name}' does not belong to the current model '{current_model_name}'")
                return False

            if not self._validateConfig(config_data):
                return False

            mapping = config_data.get("gameSpaces", {})
            # Apply themes to listed GameSpaces only
            applied_any = False
            for gs_id, gs_cfg in mapping.items():
                theme_name = gs_cfg.get("theme")
                if not theme_name:
                    continue
                # Find GameSpace by id or by name key
                target = self._findGameSpaceByIdOrName(gs_id)
                if target is not None and hasattr(target, 'applyTheme'):
                    try:
                        target.applyTheme(theme_name)
                        applied_any = True
                    except Exception:
                        pass

            if applied_any and hasattr(self.model, 'update'):
                self.model.update()
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to load theme configuration: {e}")
            return False

    def _findGameSpaceByIdOrName(self, key):
        # Try by id property
        for gs in self.model.gameSpaces.values():
            if getattr(gs, 'id', None) == key:
                return gs
        # Try by dict key (name used in gameSpaces mapping)
        if key in self.model.gameSpaces:
            return self.model.gameSpaces[key]
        return None

    def getAvailableConfigs(self):
        """Return list of available config names for the current model"""
        try:
            all_configs = self._loadAllConfigurations()
            current_model_name = self._getCurrentModelName()
            configs = []
            for name, data in all_configs["configurations"].items():
                if data.get("model_name") == current_model_name:
                    configs.append(name)
            return configs
        except Exception:
            return []

    def renameConfig(self, old_name, new_name):
        try:
            all_configs = self._loadAllConfigurations()
            if old_name not in all_configs["configurations"]:
                QMessageBox.warning(None, "Warning", f"Configuration '{old_name}' not found")
                return False
            data = all_configs["configurations"][old_name]
            if data.get("model_name") != self._getCurrentModelName():
                QMessageBox.warning(None, "Warning", f"Configuration '{old_name}' does not belong to current model")
                return False
            if new_name in all_configs["configurations"]:
                QMessageBox.warning(None, "Warning", f"Configuration '{new_name}' already exists")
                return False
            data['timestamp'] = self._getCurrentTimestamp()
            del all_configs["configurations"][old_name]
            all_configs["configurations"][new_name] = data
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(all_configs, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to rename configuration: {e}")
            return False

    def deleteConfig(self, config_name):
        try:
            all_configs = self._loadAllConfigurations()
            if config_name not in all_configs["configurations"]:
                QMessageBox.warning(None, "Warning", f"Configuration '{config_name}' not found")
                return False
            data = all_configs["configurations"][config_name]
            if data.get("model_name") != self._getCurrentModelName():
                QMessageBox.warning(None, "Warning", f"Configuration '{config_name}' does not belong to current model")
                return False
            del all_configs["configurations"][config_name]
            if not all_configs["configurations"]:
                if os.path.exists(self.config_path):
                    os.remove(self.config_path)
            else:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(all_configs, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to delete configuration: {e}")
            return False

    def _validateConfig(self, config_data):
        # Minimal validation (mapping may be empty)
        required_keys = ['model_name', 'gameSpaces']
        for key in required_keys:
            if key not in config_data:
                QMessageBox.critical(None, "Error", f"Invalid configuration: missing '{key}'")
                return False
        return True


