import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGModel import SGModel
from mainClasses.SGExtensions import *
from mainClasses.SGCellModel import SGCellModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtCore import QPoint
from random import randint
import random
from tkinter import simpledialog
import pandas as pd
import ast as ast
import math as math
from math import inf
import copy

# Helpers available to modelers when importing * from this module
def copyValue(source_att, target_att):
    """Construit une action (callable) qui copiera la valeur d'un attribut vers un autre sur une entité.

    Usage côté front-end:
        Cells.newModelAction(copyValue("bufferState", "state"))
    """
    def _action(aEntity):
        aEntity.copyValue(source_att, target_att)
    return _action