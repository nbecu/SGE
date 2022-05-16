from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from mainClasses.SGAgentCollection import SGAgentCollection


   
#Class who is responsible of the declaration a Agent
class SGAgent(QtWidgets.QWidget):
    def __init__(self,parent,name,format,size):
        super().__init__(parent)
        #Basic initialize
        self.parent=parent
        if(parent!=None):
            self.theCollection=parent.collectionOfAgents
        else:
            self.theCollection=SGAgentCollection(None)
        self.name=name
        self.format=format
        self.size=size
        #We place the default pos
        self.startXBase=0
        self.startYBase=0
        #We init the dict of Attribute
        self.attributs={}
        
        

        
        
        
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(Qt.blue, Qt.SolidPattern))
        if(self.format=="circleAgent"):
            self.setMinimumSize(self.size+1,self.size+1)
            painter.drawEllipse(0,0,self.size,self.size)
        if self.parent.format=="square":
            self.move(4,4)
        else :
            self.move(8,8)
        painter.end()
    
    def getId(self):
        return "agent"+str(self.name)
    

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
    
    #Set parent
    def setParent(self,parent):
        self.parent=parent
        self.theCollection=parent.collectionOfAgents

#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
    

        
    
        
    