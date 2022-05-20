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
        painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
        self.setGeometry(0,0,self.size+1,self.size+1)
        if(self.format=="circleAgent"):
            painter.drawEllipse(0,0,self.size,self.size)
        if self.parent.format=="square":
            self.move(round(self.size/2),round(self.size/2))
        else :
            self.move(round(self.parent.size/3),round(self.parent.size/3))
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
        for aVal in list(self.theCollection.povs[self.parent.parent.parent.nameOfPov].keys()): 
            if aVal in list(self.attributs.keys()):
                return self.theCollection.povs[self.getPov()][aVal][self.attributs[aVal]]

           
    #To get the pov
    def getPov(self):
        return self.parent.parent.parent.nameOfPov
    
    #Set parent
    def setParent(self,parent):
        self.parent=parent
        self.theCollection=parent.collectionOfAgents
        
    #To handle the selection of an element int the legend
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            #Something is selected
            if self.parent.parent.parent.selected[0]!=None :
                #The delete Action
                if self.parent.parent.parent.selected[2]== "delete":
                    for i in reversed(range(len(self.parent.collectionOfAgents.agents))):
                        if self.parent.collectionOfAgents.agents[i] == self :
                            self.parent.collectionOfAgents.agents[i].deleteLater()
                            del self.parent.collectionOfAgents.agents[i]
                    self.update()

#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use


    def setUpAgentValue(self,aDictOfValue):
        for anAttribut in aDictOfValue:
            if anAttribut in list(self.theCollection.povs[self.parent.parent.parent.nameOfPov].keys()):
                for aVal in list(self.theCollection.povs[self.parent.parent.parent.nameOfPov].keys()):
                    self.attributs[aVal]=[]
                for aVal in list(self.theCollection.povs[self.parent.parent.parent.nameOfPov].keys()):
                    del self.attributs[aVal]
                self.attributs[anAttribut]=aDictOfValue[anAttribut]
    

        
    
        
    