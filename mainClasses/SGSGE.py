import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGModel import SGModel
from mainClasses.SGCell import SGCell
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import random
