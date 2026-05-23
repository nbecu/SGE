"""
Shared pytest fixtures for SGE tests.
Provides a single QApplication instance for the entire test session.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from PyQt5.QtWidgets import QApplication

collect_ignore_glob = ["manual/*"]


@pytest.fixture(scope="session")
def qt_app():
    """Single QApplication for the full test session."""
    app = QApplication.instance() or QApplication([])
    yield app
