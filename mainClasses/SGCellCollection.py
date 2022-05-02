from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import random


   
#Class who is responsible of the declaration a cell
class SGCellCollection(QtWidgets.QWidget):
    def __init__(self,aList,nameOfPov):
        super().__init__()
        
        self.nameOfPov=nameOfPov
        self.cells=aList
        #Declare the different value that he can take
        self.dictColor={"default":Qt.gray}
        for cellCollection in self.cells:
            for cell in cellCollection:
                cell.changeThePovValue(self.nameOfPov,self.dictColor["default"])
        
        
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
    
    #To set a default color of a POV
    def setColorDefault(self,aColor):
        self.dictColor["default"]=aColor
        for cellCollection in self.cells:
            for cell in cellCollection:
                cell.changeThePovValue(self.nameOfPov,self.dictColor["default"])
    
    #To add a all dict of value for the pov
    def setColorForValues(self,aDict):
        aList=list()
        for key in self.dictColor: 
            aList.append(key)
        for key in aDict: 
            if key not in aList:
                self.dictColor[key]=aDict[key]
                
    #To add a value in the pov through RGB 
    def setColorForValueThroughRGB(self,value,R,G,B):
        self.dictColor[value]=QColor.setRgb(R,G,B)
        
    #To apply to a specific cell a value  
    def setForXandY(self,nameOfValue,aValueX,aValueY):
        self.cells[aValueX][aValueY].changeThePovValue(self.nameOfPov,self.dictColor[nameOfValue])
    
    #To apply to a all row of cell a value
    def setForX(self,nameOfValue,aValueX):
        for cellCollection in self.cells:
            for cell in cellCollection:
                if(cell.x==aValueX):
                    cell.changeThePovValue(self.nameOfPov,self.dictColor[nameOfValue])
    
    #To apply to a all column of cell a value
    def setForY(self,nameOfValue,aValueY):
        for cellCollection in self.cells:
            for cell in cellCollection:
                if(cell.y==aValueY):
                    cell.changeThePovValue(self.nameOfPov,self.dictColor[nameOfValue])
    
    #To apply to some random cell a value
    def setForRandom(self,nameOfValue,numberOfRandom):
        alreadyDone=list()
        while len(alreadyDone)!=numberOfRandom:
            aValueX=random.randint(0, len(self.cells)-1)
            aValueY=random.randint(0, len(self.cells[0])-1)
            if (aValueX,aValueY) not in alreadyDone:
                alreadyDone.append((aValueX,aValueY))
                self.cells[aValueX][aValueY].changeThePovValue(self.nameOfPov,self.dictColor[nameOfValue])
    

        
        
    
        
    