from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import random

# Class who is in charged of entities : cells and agents
class SGEntity(QtWidgets.QWidget):
    def __init__(self,parent,shape,defaultsize,me,uniqueColor=Qt.white):
        super().__init__(parent)
        self.me=me
        self.dictOfAttributs={}
        self.shape=shape
        self.isDisplay=True
        self.owner="admin"
        self.size=defaultsize
        self.color=uniqueColor

    

        
    def getColor(self):
        if self.isDisplay==False:
            return Qt.transparent
        grid=self.grid
        if self.model.nameOfPov in self.model.cellCollection[grid.id]["ColorPOV"].keys():
            self.model.cellCollection[grid.id]["ColorPOV"]['selectedPov']=self.model.cellCollection[grid.id]["ColorPOV"][self.getPov()]
            for aVal in list(self.model.cellCollection[grid.id]["ColorPOV"][self.model.nameOfPov].keys()):
                if aVal in list(self.model.cellCollection[grid.id]["ColorPOV"][self.model.nameOfPov].keys()):
                    self.color=self.model.cellCollection[grid.id]["ColorPOV"][self.getPov()][aVal][self.dictOfAttributs[aVal]]
                    return self.model.cellCollection[grid.id]["ColorPOV"][self.getPov()][aVal][self.dictOfAttributs[aVal]]
        
        else:
            if self.model.cellCollection[grid.id]["ColorPOV"]['selectedPov'] is not None:
                for aVal in list(self.model.cellCollection[grid.id]["ColorPOV"]['selectedPov'].keys()):
                    if aVal in list(self.model.cellCollection[grid.id]["ColorPOV"]['selectedPov'].keys()):
                        self.color=self.model.cellCollection[grid.id]["ColorPOV"]['selectedPov'][aVal][self.dictOfAttributs[aVal]]
                        return self.model.cellCollection[grid.id]["ColorPOV"]['selectedPov'][aVal][self.dictOfAttributs[aVal]]
            else: 
                self.color=Qt.white
                return Qt.white
                
    
    def getBorderColor(self):
        if self.isDisplay==False:
            return Qt.transparent
        if self.me == 'agent':
            self.borderColor=Qt.black
            return Qt.black
        if self.me == 'cell':
            grid=self.grid
            if self.grid.model.nameOfPov in self.model.cellCollection[grid.id]["BorderPOV"].keys():
                self.model.cellCollection[grid.id]["BorderPOV"]['selectedBorderPov']=self.model.cellCollection[grid.id]["BorderPOV"][self.getPov()]
                for aVal in list(self.model.cellCollection[grid.id]["BorderPOV"][self.grid.model.nameOfPov].keys()):
                    if aVal in list(self.model.cellCollection[grid.id]["BorderPOV"][self.grid.model.nameOfPov].keys()):
                        self.borderColor=self.model.cellCollection[grid.id]["BorderPOV"][self.getPov()][aVal][self.dictOfAttributs[aVal]]
                        return self.model.cellCollection[grid.id]["BorderPOV"][self.getPov()][aVal][self.dictOfAttributs[aVal]]
            
            else:
                self.borderColor=Qt.black
                return Qt.black
    
    def getBorderWidth(self):
        if self.me == 'agent':
            return int(1)
        if self.me == 'cell':
            grid=self.grid
            if self.model.cellCollection[grid.id]["BorderPOV"] is not None and self.grid.model.nameOfPov in self.model.cellCollection[grid.id]["BorderPOV"].keys():
                    return int(self.model.cellCollection[grid.id]["BorderPOV"]["BorderWidth"])
            return int(1)
    
    #To get the pov
    def getPov(self):
        return self.model.nameOfPov

    def getRandomXY(self):
        x = 0
        maxSize=self.cell.size
        x = random.randint(1,maxSize-1)
        return x

    #To handle the attributs and values
    def setValue(self,aAttribut,aValue):
        """
        Sets the value of an attribut
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be set
        """       
        self.dictOfAttributs[aAttribut]=aValue

    def value(self,att):
        """
        Return the value of a cell Attribut
        Args:
            att (str): Name of the attribute
        """
        return self.dictOfAttributs[att]
    
    def incValue(self,aAttribut,aValue=1,max=None):
        """
        Increase the value of an attribut with an additional value
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be added to the current value of the attribute
        """       
        self.dictOfAttributs[aAttribut]= (self.value(aAttribut)+aValue if max is None else min(self.value(aAttribut)+aValue,max))

    def decValue(self,aAttribut,aValue=1,min=None):
        """
        Decrease the value of an attribut with an additional value
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be subtracted to the current value of the attribute
        """       
        self.dictOfAttributs[aAttribut]= (self.value(aAttribut)-aValue if min is None else max(self.value(aAttribut)-aValue,min))
