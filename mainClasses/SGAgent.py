from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *


   
#Class who is responsible of the declaration a Agent
class SGAgent(QtWidgets.QWidget):
    def __init__(self,parent,theCollection,format,size,number):
        super().__init__(parent)
        #Basic initialize
        self.parent=parent
        self.theCollection=theCollection
        self.number=number
        self.format=format
        self.size=size
        #We place the default pos
        self.startXBase=0
        self.startYBase=0
        #We init the dict of Attribute
        self.attributs={}
        
        

        
        
        
    def paintEvent(self,event):
        self.startX=int(self.startXBase+self.parent.gap*(self.parent.x)+self.parent.size*(self.parent.x)+self.parent.gap) 
        self.startY=int(self.startYBase+self.parent.gap*(self.parent.y)+self.parent.size*(self.parent.y)+self.parent.gap)
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
        if(self.format=="circleAgent"):
            self.setMinimumSize(self.size+2,self.size+2)
            painter.drawEllipse(self.startX, self.startY, self.size, self.size)
            self.move(10,10)
        painter.end()
        
    def getId(self):
        return "agent"+str(self.number)
    

    #Funtion to handle the zoom
    def zoomIn(self):
        #To be reworked
        return True
    
    def zoomOut(self):
        #To be reworked
        return True
        
    def zoomFit(self):
        #To be reworked
        return True
        
    #To manage the attribute system of an Agent
    def getColor(self):
        if self.parent.parent.parent.nameOfPov=="default" :
            return self.theCollection.povs["default"]
        else :
            return self.theCollection.povs[self.parent.parent.parent.nameOfPov][self.attributs[self.parent.parent.parent.nameOfPov]]
        

    
    
    
        
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
    

        
    
        
    