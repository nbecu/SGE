"""
PyInstaller runtime hook for SGE theme initialization.
This runs at exe startup, before any user code executes.
"""

import sys

# Apply light theme as early as possible, before any UI is created
def apply_sge_theme():
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt

        # Wait for QApplication to be created (with timeout)
        app = None
        for attempt in range(100):
            app = QApplication.instance()
            if app is not None:
                break
            # Brief sleep to allow app creation
            import time
            time.sleep(0.01)

        if app is not None:
            # Apply light color scheme
            app.styleHints().setColorScheme(Qt.ColorScheme.Light)
            # Apply Fusion style
            app.setStyle("Fusion")
    except Exception:
        pass

# Run at startup
apply_sge_theme()
