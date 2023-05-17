from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null, true

from SGGameSpace import SGGameSpace

class SGVictoryBoard(SGGameSpace):

    def __init__(self, parent, title, conditions, displayRefresh='instantaneous',borderColor=Qt.black,backgroundColor=Qt.darkGray,layout="vertical"):
        super().__init__(parent,0,60,0,0,true,backgroundColor)
        self.model=parent
        self.id=title
        self.displayRefresh=displayRefresh
        self.isDisplay=True
        self.borderColor=borderColor
        self.backgroundColor=backgroundColor
        if layout=='vertical':
            self.layout=QtWidgets.QVBoxLayout()
        elif layout=='horizontal':
            self.layout=QtWidgets.QHBoxLayout()
        self.initUI()


    def initUI(self):
        layout=self.layout

        title=QtWidgets.QLabel(self.id)
        font = QFont()
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        self.setLayout(layout)
        self.show()

    def paintEvent(self,event):
        if self.checkDisplay():
            painter = QPainter() 
            painter.begin(self)
            painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
            painter.setPen(QPen(self.borderColor,1))
            #Draw the corner of the DB
            self.setMinimumSize(self.getSizeXGlobal()+10, self.getSizeYGlobal()+10)
            painter.drawRect(0,0,self.getSizeXGlobal(), self.getSizeYGlobal())     


            painter.end()
            

    def checkDisplay(self):
        if self.isDisplay:
            return True
        else:
            return False
        
    # *Functions to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        return 150
        
    def getSizeYGlobal(self):
        return 50

    def mouseMoveEvent(self, e):
    
        if e.buttons() != Qt.LeftButton:
            return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())

        drag.exec_(Qt.MoveAction)