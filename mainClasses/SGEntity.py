from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import random
from mainClasses.gameAction.SGGameActions import SGGameActions

# Class who is in charged of entities : cells and agents
class SGEntity(QtWidgets.QWidget):
    def __init__(self,parent,classDef,size,shapeColor,attributesAndValues):
        super().__init__(parent)
        self.classDef=classDef
        self.id=self.classDef.nextId()
        self.privateID = self.classDef.entityName+str(self.id)
        self.model=self.classDef.model
        self.shape= self.classDef.shape
        self.size=size
        self.color=shapeColor # Faudra peut etre envisagée de retirer cet attribut. Car la couleur est gérée par la classDef
                               # A moins qu'on l'utilse pour faire flasher l'entité, masi dans ce cas il vaudrait mieux défini un attribut flashColor
        self.borderColor=self.classDef.defaultBorderColor
        self.isDisplay=True
        #Define variables to handle the history 
        self.history={}
        self.history["value"]=[]
        self.watchers={}
        #Set the attributes
        self.initAttributesAndValuesWith(attributesAndValues)
        self.owner="admin"

    
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

    def readColorAndWidthFromBorderPovDef(self,aBorderPovDef,aDefaultColor,aDefaultWidth):
        if aBorderPovDef is None: return {'color':aDefaultColor,'width':aDefaultWidth}
        aAtt=list(aBorderPovDef.keys())[0]
        aDictOfValueAndColorWidth=list(aBorderPovDef.values())[0]
        dictColorAndWidth = aDictOfValueAndColorWidth.get(self.value(aAtt))
        if not isinstance(dictColorAndWidth,dict): raise ValueError('wrong format')
        return dictColorAndWidth

    def getColor(self):
        if self.isDisplay==False: return Qt.transparent
        # replace the search of model name of pov by getCheckedSymbologyNameOfEntity (which look for the symbolgy which is checked for this item in the menu)
        aChoosenPov = self.model.getCheckedSymbologyOfEntity(self.classDef.entityName)
        aPovDef = self.classDef.povShapeColor.get(aChoosenPov) #self.model.nameOfPov
        aDefaultColor= self.classDef.defaultShapeColor
        return self.readColorFromPovDef(aPovDef,aDefaultColor)

    def getBorderColorAndWidth(self):
        if self.isDisplay==False: return Qt.transparent
        aChoosenPov = self.model.getCheckedSymbologyOfEntity(self.classDef.entityName, borderSymbology=True)
        aBorderPovDef = self.classDef.povBorderColorAndWidth.get(aChoosenPov)
        aDefaultColor= self.classDef.defaultBorderColor
        aDefaultWidth=self.classDef.defaultBorderWidth
        return self.readColorAndWidthFromBorderPovDef(aBorderPovDef,aDefaultColor,aDefaultWidth)
    
    #To get the pov
    def getPov(self):
        return self.model.nameOfPov

    def getRandomXY(self):
        x = 0
        maxSize=self.cell.size
        x = random.randint(1,maxSize-1)
        return x

    def updateMqtt(self):
        if self.model.mqttMajType == "Instantaneous":
            SGGameActions.sendMqttMessage(self)

    def addWatcher(self,aIndicator):
        aAtt = aIndicator.attribut
        if aAtt not in self.watchers.keys():
            self.watchers[aAtt]=[]
        self.watchers[aAtt].append(aIndicator)

    def updateWatchersOnAttribute(self,aAtt):
        for watcher in self.watchers.get(aAtt,[]):
            watcher.checkAndUpdate()

    def saveHistoryValue(self):
        if len(self.history["value"])==0:
            self.history["value"].append([0,0,self.dictAttributes]) #correspond à round 0 phase 0
        self.history["value"].append([self.model.timeManager.currentRound,self.model.timeManager.currentPhase,self.dictAttributes])


    def isDeleted(self):
        return not self.isDisplay


    #To handle the attributs and values
    def setValue(self,aAttribut,aValue):
        """
        Sets the value of an attribut
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be set
        """
        # if self.model.round()!=0 and not aAttribut in self.dictAttributes: raise ValueError("Not such an attribute") ## Instrtcuion commented because agentRecreatedWhen Moving need to pass over this condition
        if aAttribut in self.dictAttributes and self.dictAttributes[aAttribut]==aValue: return False #The attribute has already this value
        self.saveHistoryValue()    
        self.dictAttributes[aAttribut]=aValue

        self.classDef.updateWatchersOnAttribute(aAttribut) #This is for watchers on the wole pop of entities
        self.updateWatchersOnAttribute(aAttribut) #This is for watchers on this specific entity
        self.updateMqtt()
        self.update()
        return True

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
        self.setValue(aAttribut,(self.value(aAttribut)+aValue if max is None else min(self.value(aAttribut)+aValue,max)))
        # This method is equivalent to 
        # newValue = self.value(aAttribut)+aValue
        # if max is not None: newValue = min(newValue,max)    
        # self.setValue(aAttribut,newValue)

    def decValue(self,aAttribut,aValue=1,min=None):
        """
        Decrease the value of an attribut with an additional value
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be subtracted to the current value of the attribute
        """       
        self.setValue(aAttribut,(self.value(aAttribut)-aValue if min is None else max(self.value(aAttribut)-aValue,min)))

    def calValue(self,aAttribut,aLambdaFunction):
        # NOT TESTED YET
        if callable(aLambdaFunction):
            currentValue = self.value(aAttribut)
            result = aLambdaFunction(currentValue)
            self.setValue(result)
        else: raise ValueError ('calcValue works with a lambda function')