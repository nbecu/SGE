from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *


   
#Class who is responsible of the declaration a cell
class SGCell(QtWidgets.QWidget):
    def __init__(self,parent,x,y,format,size,gap,startXBase,startYBase):
        super().__init__(parent)
        self.parent=parent
        self.x=x
        self.y=y
        self.format=format
        self.size=size
        self.gap=gap
        self.startXBase=int(startXBase+self.gap*(x)+self.size*(x)+self.gap) 
        self.startYBase=startXBase=int(startYBase+self.gap*(y)+self.size*(y)+self.gap)
        
        
        
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
        #Base of the gameBoard
        if(self.format=="square"):
            painter.drawRect(0,0,self.size,self.size)
            self.move(self.startXBase,self.startYBase)
        elif(self.format=="hexagonal"):
            points = QPolygon([
               QPoint(int(self.size/2),  0),
               QPoint(self.size,  int(self.size/3)),
               QPoint(self.size,  int((self.size/3)*2)),
               QPoint(int(self.size/2), self.size),
               QPoint(0,  int((self.size/3)*2)),
               QPoint(0,  int(self.size/3))
            ])
            painter.drawPolygon(points)
            if(self.y%2==1):
                self.move(self.startXBase+int(self.size/2)+int(self.gap/2),self.startYBase-int(self.size/2)+self.gap    -int(self.size/2)*(self.y-1) +self.gap*(self.y-1) )
            else:
                self.move(self.startXBase,self.startYBase-int(self.size/2)*self.y +self.gap*self.y)
        painter.end()
        
    def getId(self):
        return "cell"+str(self.x)+str(self.y)
    

       
        
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
    

        
    
        
    