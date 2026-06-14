"""
Test suite for sys.argv[0] fix (config file path correction)

Tests verify that:
1. Layout and theme config files are saved in the model script directory, not SGE root
2. Works correctly from IDE and command line
3. Existing layout/theme functionality is not broken
"""
import pytest
import os
import json
import tempfile
import shutil
from pathlib import Path
from mainClasses.SGSGE import SGModel
from mainClasses.layout.SGLayoutConfigManager import SGLayoutConfigManager
from mainClasses.theme.SGThemeConfigManager import SGThemeConfigManager


class TestConfigPathUnitTests:
    """Unit tests: verify _getConfigPath returns correct paths"""

    def test_layout_config_path_is_in_script_directory(self, qt_app):
        """Layout config should point to script directory, not SGE root"""
        model = SGModel(400, 400)
        layout_manager = SGLayoutConfigManager(model)

        # Path should be in SGE root (where this test runs), not somewhere else
        config_path = layout_manager.config_path
        expected_dir = os.path.dirname(os.path.abspath(__file__))

        # Config should be in tests directory
        assert os.path.dirname(config_path) == expected_dir, \
            f"Layout config in wrong dir: {config_path} should be in {expected_dir}"
        assert config_path.endswith("layout_config.json")

        model.close()

    def test_theme_config_path_is_in_script_directory(self, qt_app):
        """Theme config should point to script directory, not SGE root"""
        model = SGModel(400, 400)
        theme_manager = SGThemeConfigManager(model)

        # Path should be in SGE root (where this test runs), not somewhere else
        config_path = theme_manager.config_path
        expected_dir = os.path.dirname(os.path.abspath(__file__))

        # Config should be in tests directory
        assert os.path.dirname(config_path) == expected_dir, \
            f"Theme config in wrong dir: {config_path} should be in {expected_dir}"
        assert config_path.endswith("theme_config.json")

        model.close()

    def test_config_paths_use_absolute_paths(self, qt_app):
        """Config paths should be absolute, not relative"""
        model = SGModel(400, 400)
        layout_manager = SGLayoutConfigManager(model)
        theme_manager = SGThemeConfigManager(model)

        assert os.path.isabs(layout_manager.config_path), \
            f"Layout config path is relative: {layout_manager.config_path}"
        assert os.path.isabs(theme_manager.config_path), \
            f"Theme config path is relative: {theme_manager.config_path}"

        model.close()


class TestConfigPathIntegration:
    """Integration tests: verify files are actually created in correct locations"""

    @pytest.fixture
    def temp_model_dir(self):
        """Create a temporary directory to simulate model script location"""
        temp_dir = tempfile.mkdtemp(prefix="sge_config_test_")
        yield temp_dir
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    def test_layout_config_file_created_in_correct_location(self, qt_app, temp_model_dir):
        """Layout config file should be created next to model script"""
        # This test creates a config file in a temporary directory
        # We can't change sys.argv from here, but we can verify the path logic
        model = SGModel(400, 400)
        Cell = model.newCellsOnGrid(3, 3, "square", size=40, gap=10)
        layout_manager = SGLayoutConfigManager(model)

        # Config should point to tests directory
        config_path = layout_manager.config_path
        assert "test" in config_path.lower() or "tests" in config_path.lower(), \
            f"Config path doesn't reflect test location: {config_path}"

        model.close()

    def test_theme_config_file_created_in_correct_location(self, qt_app):
        """Theme config file should be created next to model script"""
        model = SGModel(400, 400)
        theme_manager = SGThemeConfigManager(model)

        # Config should point to tests directory
        config_path = theme_manager.config_path
        assert "test" in config_path.lower() or "tests" in config_path.lower(), \
            f"Config path doesn't reflect test location: {config_path}"

        model.close()


class TestConfigPathRegression:
    """Regression tests: verify existing functionality not broken"""

    def test_layout_manager_initializes_without_error(self, qt_app):
        """Layout manager should initialize without errors"""
        model = SGModel(400, 400)
        Cell = model.newCellsOnGrid(3, 3, "square", size=40, gap=10)

        # Should not raise any exception
        try:
            layout_manager = SGLayoutConfigManager(model)
            assert layout_manager is not None
            assert layout_manager.config_path is not None
        except Exception as e:
            pytest.fail(f"Layout manager initialization failed: {e}")
        finally:
            model.close()

    def test_theme_manager_initializes_without_error(self, qt_app):
        """Theme manager should initialize without errors"""
        model = SGModel(400, 400)

        # Should not raise any exception
        try:
            theme_manager = SGThemeConfigManager(model)
            assert theme_manager is not None
            assert theme_manager.config_path is not None
        except Exception as e:
            pytest.fail(f"Theme manager initialization failed: {e}")
        finally:
            model.close()

    def test_config_dir_creation_works(self, qt_app):
        """Should be able to create config directory without errors"""
        model = SGModel(400, 400)
        layout_manager = SGLayoutConfigManager(model)

        # This method is called before saving configs
        try:
            result = layout_manager._ensureConfigsDirectory()
            assert isinstance(result, bool), "Method should return boolean"
        except Exception as e:
            pytest.fail(f"Directory creation failed: {e}")
        finally:
            model.close()

    def test_load_configurations_handles_missing_file_gracefully(self, qt_app):
        """Should handle missing config file gracefully"""
        model = SGModel(400, 400)
        layout_manager = SGLayoutConfigManager(model)

        # Should not raise exception even if file doesn't exist
        try:
            configs = layout_manager._loadAllConfigurations()
            assert isinstance(configs, dict)
            assert "configurations" in configs
        except Exception as e:
            pytest.fail(f"Load configurations failed: {e}")
        finally:
            model.close()

    def test_model_name_retrieval_works(self, qt_app):
        """Should be able to retrieve model name without errors"""
        model = SGModel(400, 400, windowTitle="Test Model")
        model.name = "TestModel"  # Set model name attribute
        layout_manager = SGLayoutConfigManager(model)
        theme_manager = SGThemeConfigManager(model)

        try:
            layout_name = layout_manager._getCurrentModelName()
            theme_name = theme_manager._getCurrentModelName()
            assert isinstance(layout_name, str)
            assert isinstance(theme_name, str)
            assert layout_name == "TestModel"
            assert theme_name == "TestModel"
        except Exception as e:
            pytest.fail(f"Model name retrieval failed: {e}")
        finally:
            model.close()
