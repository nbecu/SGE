from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from collections import defaultdict
import random
from mainClasses.AttributeAndValueFunctionalities import *

# Class who is in charged of entities : cells and agents
class SGEntity(QtWidgets.QWidget,AttributeAndValueFunctionalities):
    def __init__(self,parent,classDef,size,attributesAndValues):
        super().__init__(parent)
        self.classDef=classDef
        self.id=self.classDef.nextId()
        self.privateID = self.classDef.entityName+str(self.id)
        self.model=self.classDef.model
        self.shape= self.classDef.shape
        self.size=size
        self.borderColor=self.classDef.defaultBorderColor
        self.isDisplay=True
        #Define variables to handle the history 
        self.history={}
        self.history["value"]=defaultdict(list)
        # self.list_history = []
        self.watchers={}
        #Set the attributes
        self.initAttributesAndValuesWith(attributesAndValues)
        self.owner="admin"

    
    def initAttributesAndValuesWith(self, thisAgentAttributesAndValues):
        self.dictAttributes={}
        if thisAgentAttributesAndValues is None : thisAgentAttributesAndValues={}
        for aAtt, aDefaultValue in self.classDef.attributesDefaultValues.items():
            if not aAtt in thisAgentAttributesAndValues.keys():
                thisAgentAttributesAndValues[aAtt]=aDefaultValue
        for aAtt, valueToSet in thisAgentAttributesAndValues.items():
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

    def readColorAndWidthFromBorderPovDef(self,aBorderPovDef,aDefaultColor,aDefaultWidth):
        if aBorderPovDef is None: return {'color':aDefaultColor,'width':aDefaultWidth}
        aAtt=list(aBorderPovDef.keys())[0]
        aDictOfValueAndColorWidth=list(aBorderPovDef.values())[0]
        dictColorAndWidth = aDictOfValueAndColorWidth.get(self.value(aAtt))
        if not isinstance(dictColorAndWidth,dict): raise ValueError('wrong format')
        return dictColorAndWidth

    def getColor(self):
        if self.isDisplay==False: return Qt.transparent
        aChoosenPov = self.model.getCheckedSymbologyOfEntity(self.classDef.entityName)
        aPovDef = self.classDef.povShapeColor.get(aChoosenPov)
        aDefaultColor= self.classDef.defaultShapeColor
        return self.readColorFromPovDef(aPovDef,aDefaultColor)

    def getBorderColorAndWidth(self):
        if self.isDisplay==False: return Qt.transparent
        aChoosenPov = self.model.getCheckedSymbologyOfEntity(self.classDef.entityName, borderSymbology=True)
        aBorderPovDef = self.classDef.povBorderColorAndWidth.get(aChoosenPov)
        aDefaultColor= self.classDef.defaultBorderColor
        aDefaultWidth=self.classDef.defaultBorderWidth
        return self.readColorAndWidthFromBorderPovDef(aBorderPovDef,aDefaultColor,aDefaultWidth)

    def getRandomXY(self):
        x = 0
        maxSize=self.cell.size
        x = random.randint(1,maxSize-1)
        return x

    def getObjectIdentiferForJsonDumps(self):
        dict ={}
        dict['entityName']=self.classDef.entityName
        dict['id']=self.id
        return dict
    
    def addWatcher(self,aIndicator):
        aAtt = aIndicator.attribute
        if aAtt not in self.watchers.keys():
            self.watchers[aAtt]=[]
        self.watchers[aAtt].append(aIndicator)

    def updateWatchersOnAttribute(self,aAtt):
        for watcher in self.watchers.get(aAtt,[]):
            watcher.checkAndUpdate()

    def getListOfStepsData(self,startStep=None,endStep=None):
        aList=self.getListOfUntagedStepsData(startStep,endStep)
        return [{**{'entityType': self.classDef.entityType(),'entityName': self.classDef.entityName,'id': self.id},**aStepData} for aStepData in aList]

    
    def isDeleted(self):
        return not self.isDisplay

    #To handle the attributs and values
    # Should check how to manage this method with the one of the superclass AttributeAndValueFunctinalities
    def setValue(self,aAttribut,valueToSet):
        """
        Sets the value of an attribut
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be set
        """
        if callable(valueToSet):
            aValue = valueToSet()
        else:
            aValue = valueToSet
        # if self.model.roundNumber()!=0 and not aAttribut in self.dictAttributes: raise ValueError("Not such an attribute") ## Instrtcuion commented because agentRecreatedWhen Moving need to pass over this condition
        if aAttribut in self.dictAttributes and self.dictAttributes[aAttribut]==aValue: return False #The attribute has already this value
        self.dictAttributes[aAttribut]=aValue
        self.saveValueInHistory(aAttribut,aValue)
        self.classDef.updateWatchersOnAttribute(aAttribut) #This is for watchers on the wole pop of entities
        self.updateWatchersOnAttribute(aAttribut) #This is for watchers on this specific entity
        self.update()
        return True

    #To perform action --> Check if this method is used or not
    def doAction(self, aLambdaFunction):
        aLambdaFunction(self)
