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
        
        self.saveGap=gap
        self.saveSize=size
        
        self.startXBase=startXBase
        self.startYBase=startYBase

        
        
        
    def paintEvent(self,event):
        self.startX=int(self.startXBase+self.gap*(self.x)+self.size*(self.x)+self.gap) 
        self.startY=startXBase=int(self.startYBase+self.gap*(self.y)+self.size*(self.y)+self.gap)
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
        #Base of the gameBoard
        if(self.format=="square"):
            painter.drawRect(0,0,self.size,self.size)
            self.setMinimumSize(self.size,self.size)
            self.move(self.startX,self.startY)
        elif(self.format=="hexagonal"):
            self.setMinimumSize(self.size,self.size)
            points = QPolygon([
               QPoint(int(self.size/2),  0),
               QPoint(self.size,  int(self.size/3)),
               QPoint(self.size,  int((self.size/3)*2)),
               QPoint(int(self.size/2), self.size),
               QPoint(0,  (int((self.size/3)*2))),
               QPoint(0,  int(self.size/3))
            ])
            painter.drawPolygon(points)
            if(self.y%2==1):
                self.move((self.startX+int(self.size/2)+int(self.gap/2) ), (self.startY-int(self.size/2)+self.gap    -int(self.size/2)*(self.y-1) +self.gap*(self.y-1)) )
            else:
                self.move(self.startX,(self.startY-int(self.size/2)*self.y +self.gap*self.y))
        painter.end()
        
    def getId(self):
        return "cell"+str(self.x)+str(self.y)
    

    #Funtion to handle the zoom
    def zoomIn(self):
        self.size=self.parent.size
        self.gap=self.parent.gap
        self.update()
    
    def zoomOut(self):
        self.size=self.parent.size
        self.gap=self.parent.gap
        self.update()
        
    def zoomFit(self):
        self.size=self.parent.size
        self.gap=self.parent.gap
        self.update()
        
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
    

        
    
        
    