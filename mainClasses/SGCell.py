from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *


   
#Class who is responsible of the declaration a cell
class SGCell(QtWidgets.QWidget):
    def __init__(self,parent,theCollection,x,y,format,size,gap,startXBase,startYBase):
        super().__init__(parent)
        #Basic initialize
        self.parent=parent
        self.theCollection=theCollection
        self.x=x
        self.y=y
        self.format=format
        self.size=size
        self.gap=gap
        #Save the basic value for the zoom ( temporary)
        self.saveGap=gap
        self.saveSize=size
        #We place the default pos
        self.startXBase=startXBase
        self.startYBase=startYBase
        self.isDisplay=True
        #We init the dict of Attribute
        self.attributs={}
        
        

        
        
        
    def paintEvent(self,event):
        self.startX=int(self.startXBase+self.gap*(self.x)+self.size*(self.x)+self.gap) 
        self.startY=startXBase=int(self.startYBase+self.gap*(self.y)+self.size*(self.y)+self.gap)
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
        if self.isDisplay==False:
            painter.setPen(QPen(Qt.transparent,1));
        else :
            painter.setPen(QPen(Qt.black,1));
        #Base of the gameBoard
        if(self.format=="square"):
            painter.drawRect(0,0,self.size,self.size)
            self.setMinimumSize(self.size,self.size+1)
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
        
    #To manage the attribute system of a cell
    def getColor(self):
        if self.isDisplay==False:
            return Qt.transparent
        if self.parent.parent.nameOfPov=="default" :
            return self.theCollection.povs["default"]
        else :
            return self.theCollection.povs[self.parent.parent.nameOfPov][self.attributs[self.parent.parent.nameOfPov]]
        
    #To handle the selection of an element int the legend
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            #Something is selected
            if self.parent.parent.selected[0]!=None :
                #The delete Action
                if self.parent.parent.selected[2]== "delete":
                    self.parent.collectionOfCells.removeVisiblityCell(self.getId())
                    self.update()
                #The Replace cell and change value Action
                elif self.parent.parent.selected[1]== "square" or self.parent.parent.selected[1]=="hexagonal":
                    self.isDisplay=True
                    self.attributs[self.parent.parent.nameOfPov]=self.parent.parent.selected[2]
                    self.update()
        self.parent.parent.update()
    
    
    
        
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
    

        
    
        
    