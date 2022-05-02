from PyQt5 import QtWidgets
from PyQt5.QtSvg import * 
from PyQt5.QtGui import *
from PyQt5.QtCore import *


            
class SGLayout(QtWidgets.QWidget):
    def __init__(self,type="vertical"):
        super().__init__()
        self.type = type
        self.maxRow=1
        self.minRow=1
        
        