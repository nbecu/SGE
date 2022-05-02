from PyQt5 import QtWidgets
from PyQt5.QtSvg import * 
from PyQt5.QtGui import *
from PyQt5.QtCore import *


            
class SGGameSpace(QtWidgets.QWidget):
    def __init__(self,centerCoordonateX,centerCoordonateY,isDraggable,aLayout,backgroudColor=Qt.white):
        super().__init__()
        self.centerCoordonateX = centerCoordonateX
        self.centerCoordonateY = centerCoordonateY
        self.isDraggable = isDraggable
        self.backgroudColor = backgroudColor
        
        