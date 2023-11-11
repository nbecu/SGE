from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import random

# Class who is in charged of entities : cells and agents
class SGEntity(QtWidgets.QWidget):
    def __init__(self,parent,classDef, size,shapeColor,attributesAndValues):
        super().__init__(parent)
        self.classDef=classDef
        self.id=self.classDef.nextId()
        self.privateID = self.classDef.entityName+str(self.id)
        self.model=self.classDef.model
        self.shape= self.classDef.shape
        self.size=size
        self.color=shapeColor
        self.borderColor=self.classDef.defaultBorderColor
        self.isDisplay=True
        self.initAttributesAndValuesWith(attributesAndValues)
        self.owner="admin"
        #We define variables to handle the history 
        self.history={}
        self.history["value"]=[]
    
    def initAttributesAndValuesWith(self, thisAgentAttributesAndValues):
        self.dictAttributes={}
        if thisAgentAttributesAndValues is None : thisAgentAttributesAndValues={}
        for aAtt in self.classDef.attributesPossibleValues.keys():
            if aAtt in thisAgentAttributesAndValues.keys():
                valueToSet = thisAgentAttributesAndValues[aAtt]
            elif aAtt in self.classDef.attributesDefaultValues.keys():
                valueToSet = self.classDef.attributesDefaultValues[aAtt]
            else: valueToSet = None
            if callable(valueToSet):
                self.setValue(aAtt,valueToSet())
            else:
                self.setValue(aAtt,valueToSet)



    def getRandomAttributValue(self,aAgentSpecies,aAtt):
        if aAgentSpecies.dictAttributes is not None:
            values = list(aAgentSpecies.dictAttributes[aAtt])
            number=len(values)
            aRandomValue=random.randint(0,number-1)          
        return aRandomValue


    def readColorFromPovDef(self,aPovDef,aDefaultColor):
        if aPovDef is None: return aDefaultColor
        aAtt=list(aPovDef.keys())[0]
        aDictOfValueAndColor=list(aPovDef.values())[0]
        aColor = aDictOfValueAndColor.get(self.value(aAtt))
        return aColor if aColor is not None else aDefaultColor

    def getColor(self):
        if self.isDisplay==False: return Qt.transparent
        # replace the search of model name of pov by getCheckedSymbologyNameOfEntity (which look for the symbolgy which is checked for this item in the menu)
        aChoosenPov = self.model.getCheckedSymbologyNameOfEntity(self.classDef.entityName)
        aPovDef = self.classDef.povShapeColor.get(aChoosenPov) #self.model.nameOfPov
        aDefaultColor= self.classDef.defaultShapeColor
        return self.readColorFromPovDef(aPovDef,aDefaultColor)
      
    
    def getBorderColor(self):
        if self.isDisplay==False: return Qt.transparent
        aPovDef = self.classDef.povBorderColor.get(self.model.nameOfPov)
        aDefaultColor= self.classDef.defaultBorderColor
        return self.readColorFromPovDef(aPovDef,aDefaultColor)

    
    def getBorderWidth(self):
        # if self.me == 'agent':
        #     return int(1)
        # if self.me == 'cell':
        #     grid=self.grid
        #     if self.model.cellCollection[grid.id]["BorderPOV"] is not None and self.grid.model.nameOfPov in self.model.cellCollection[grid.id]["BorderPOV"].keys():
        #             return int(self.model.cellCollection[grid.id]["BorderPOV"]["BorderWidth"])
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
        self.dictAttributes[aAttribut]=aValue

    def value(self,att):
        """
        Return the value of a cell Attribut
        Args:
            att (str): Name of the attribute
        """
        return self.dictAttributes[att]
    
    def incValue(self,aAttribut,aValue=1,max=None):
        """
        Increase the value of an attribut with an additional value
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be added to the current value of the attribute
        """       
        self.dictAttributes[aAttribut]= (self.value(aAttribut)+aValue if max is None else min(self.value(aAttribut)+aValue,max))

    def decValue(self,aAttribut,aValue=1,min=None):
        """
        Decrease the value of an attribut with an additional value
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be subtracted to the current value of the attribute
        """       
        self.dictAttributes[aAttribut]= (self.value(aAttribut)-aValue if min is None else max(self.value(aAttribut)-aValue,min))
