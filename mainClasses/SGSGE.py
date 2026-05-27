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
from random import randint
import random
from tkinter import simpledialog
import pandas as pd
import ast as ast
import math as math
from math import inf
import copy

# PyQt6 compatibility: restore Qt.color shortcuts removed from the Qt namespace.
# In PyQt5, Qt.red / Qt.black / etc. were direct attributes of Qt.
# In PyQt6, they live under Qt.GlobalColor.red / Qt.GlobalColor.black / etc.
# This block recreates the shortcuts so all modeler code continues to work unchanged.
_GLOBAL_COLORS = [
    'color0', 'color1', 'black', 'white',
    'darkGray', 'gray', 'lightGray',
    'red', 'green', 'blue', 'cyan', 'magenta', 'yellow',
    'darkRed', 'darkGreen', 'darkBlue',
    'darkCyan', 'darkMagenta', 'darkYellow',
    'transparent',
]
for _c in _GLOBAL_COLORS:
    setattr(Qt, _c, getattr(Qt.GlobalColor, _c))

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
    "inf",
    "copy",
    "Path",
    "sys",
]

# Export all SGExtensions helpers in __all__
try:
    __all__ = list(dict.fromkeys(__all__ + list(getattr(_SGExtensions, "__all__", []))))
except Exception:
    pass
