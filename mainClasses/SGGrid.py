from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from SGGameSpace import SGGameSpace

#Class who is responsible of the grid creation
class SGGrid(SGGameSpace):
    def __init__(self,parent,name,rows=8, columns=8,format="square",gap=3,size=32):
        super().__init__(parent,0,12,0,0)
        #Basic initialize
        self.zoom=1
        self.id=name
        self.rows=rows
        self.columns=columns
        self.format=format
        self.gap=gap
        self.size=size
        
        self.startXbase=0
        self.startYbase=12
        
    #Drawing the game board with the cell
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
        #Base of the gameBoard
        if(self.format=="square"):
            #We redefine the minimum size of the widget
            self.setMinimumSize(int(self.rows*self.size+(self.rows+1)*self.gap+1), int(self.columns*self.size+(self.columns+1)*self.gap))
            painter.drawRect(0,0, int(self.rows*self.size+(self.rows+1)*self.gap+1), int(self.columns*self.size+(self.columns+1)*self.gap))
        painter.end()
        
    #Funtion to handle the zoom
    def zoomIn(self):
        self.zoom=self.zoom*1.1
        self.size=round(self.size+(self.zoom*10))
        self.gap=round(self.gap+(self.zoom*1))
        self.update()
    
    def zoomOut(self):
        self.zoom=self.zoom*0.9
        self.size=round(self.size-(self.zoom*10))
        if(self.gap>2):
            self.gap=round(self.gap-(self.zoom*1))
        self.update()
        
    def zoomFit(self):
        self.zoom=1
        self.size=self.saveSize
        self.gap=self.saveGap
        self.update()
        
    #To handle the drag of the grid
    def mouseMoveEvent(self, e):
    
        if e.buttons() != Qt.RightButton:
            return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())

        drag.exec_(Qt.MoveAction)
        
    #Funtion to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        return int(self.rows*self.size+(self.rows+1)*self.gap+1)+20
    
    def getSizeYGlobal(self):
        return int(self.columns*self.size+(self.columns+1)*self.gap)+20
