from PyQt5 import QtWidgets

from PyQt5.QtGui import *
from PyQt5.QtCore import *


            
class SGGameSpace(QtWidgets.QWidget):
    def __init__(self,parent,startXBase,startYBase,posXInLayout,posYInLayout,isDraggable=True,backgroudColor=Qt.gray,forceDisplay=False):
        super().__init__(parent)
        self.model=parent
        self.posXInLayout=posXInLayout
        self.posYInLayout=posYInLayout
        self.startXBase=startXBase
        self.startYBase=startYBase
        self.isDraggable = isDraggable
        self.backgroudColor = backgroudColor
        self.forceDisplay = forceDisplay
        
    #Funtion to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        pass
    
    def getSizeYGlobal(self):
        pass
    
    #Funtion to handle the zoom
    def zoomIn(self):
        pass
    
    def zoomOut(self):
        pass
    
    #To choose the inital pov when the game start
    def setInitialPov(self,nameOfPov):
        pass
    
    
    #The getter and setter
    def getStartXBase(self):
        return self.startXBase
    
    def getStartYBase(self):
        return self.startYBase
    
    def setStartXBase(self,number):
        self.startXBase = number
    
    def setStartYBase(self,number):
        self.startYBase = number
    
    #Calculate the area
    def areaCalc(self):
        self.area = float(self.width() * self.height())
        return self.area

#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    #Funtion to have the global size of a gameSpace  
    def setDraggability(self,aBoolean):
        self.isDraggable=aBoolean
        
    #Funtion to have the global size of a gameSpace  
    def setColor(self,aColor):
        self.backgroudColor=aColor
        
        
    #Function to change the order in the layout
    def setInPosition(self,x,y):
        x=x-1
        y=y-1
        self.posXInLayout=x
        self.posYInLayout=y
        
    