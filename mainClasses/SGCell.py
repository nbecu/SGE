from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *


   
#Class who is responsible of the declaration a cell
class SGCell(QtWidgets.QWidget):
    def __init__(self,parent,x,y,format,size,gap,startXBase,startYBase):
        super().__init__(parent)
        self.x=x
        self.y=y
        self.format=format
        self.size=size
        self.gap=gap
        self.startXBase=int(startXBase+self.gap*(x)+self.size*(x)+self.gap) 
        self.startYBase=int(startYBase+self.gap*(y)+self.size*(y)+self.gap)
        
        
        
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
        #Base of the gameBoard
        if(self.format=="square"):
            painter.drawRect(0,0,self.size,self.size)
            self.move(self.startXBase,self.startYBase)
        painter.end()
        
    def getId(self):
        return "cell"+str(self.x)+str(self.y)
    

       
        
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
    

        
    
        
    