from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null, true

from SGGameSpace import SGGameSpace


#Class who is responsible of the Legend creation 
class SGDashBoard(SGGameSpace):
    def __init__(self,parent,title,indicators,displayRefresh='instantaneous',borderColor=Qt.black,backgroundColor=Qt.transparent):
        super().__init__(parent,0,60,0,0,true,backgroundColor)
        self.model=parent
        self.title=title
        self.indicators=indicators
        self.borderColor=borderColor
        self.backgroundColor=backgroundColor
        self.y=0
        self.isDisplay=True
        self.displayRefresh=displayRefresh
        self.initUI()

    def initUI(self):
        self.y=0


    def checkDisplay(self):
        if self.isDisplay:
            return True
        else:
            return False