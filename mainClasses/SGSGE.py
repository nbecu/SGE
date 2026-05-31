import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGModel import SGModel
from mainClasses.SGExtensions import *
import mainClasses.SGExtensions as _SGExtensions
from mainClasses.SGCell import SGCell
from mainClasses.SGBotPlayer import SGBotPlayer
from PyQt6 import QtWidgets
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import QInputDialog
from PyQt6.QtCore import QPoint

# Initialize light theme for all SGE applications (especially important for frozen executables)
def _init_sge_light_theme():
    try:
        app = QtWidgets.QApplication.instance()
        if app is not None:
            # Try setColorScheme first (Qt 6.5+)
            try:
                app.styleHints().setColorScheme(Qt.ColorScheme.Light)
            except Exception:
                pass

            # Set Fusion style
            app.setStyle("Fusion")

            # Apply light palette manually (fallback for systems where setColorScheme doesn't work)
            from PyQt6.QtGui import QPalette, QColor
            palette = QPalette()
            # Light colors
            palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
            palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
            app.setPalette(palette)
    except Exception:
        pass

_init_sge_light_theme()

from random import randint
import random
from tkinter import simpledialog
import pandas as pd
import ast as ast
import math as math
from math import inf
import copy

# Public API for modelers importing * from this module
__all__ = [
    "SGModel",
    "SGCell",
    "SGBotPlayer",
    "SGColors",
    "QtWidgets",
    "Qt",
    "QColor",
    "QPixmap",
    "QInputDialog",
    "QPoint",
    "random",
    "randint",
    "pd",
    "ast",
    "math",
    "inf",
    "copy",
    "Path",
    "sys",
    "simpledialog",
]

# Export all SGExtensions helpers in __all__
try:
    __all__ = list(dict.fromkeys(__all__ + list(getattr(_SGExtensions, "__all__", []))))
except Exception:
    pass
