from PyQt5 import QtWidgets

from PyQt5.QtGui import *
from PyQt5.QtCore import *


            
class SGGameSpace(QtWidgets.QWidget):
    def __init__(self,parent,startXbase,startYbase,posXInLayout,posYInLayout,isDraggable=False,backgroudColor=Qt.gray):
        super().__init__(parent)
        self.posXInLayout=posXInLayout
        self.posYInLayout=posYInLayout
        self.startXbase=startXbase
        self.startYbase=startYbase
        self.isDraggable = isDraggable
        self.backgroudColor = backgroudColor
        
    #Funtion to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        pass
    
    def getSizeYGlobal(self):
        pass
    
    
    
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
        
    