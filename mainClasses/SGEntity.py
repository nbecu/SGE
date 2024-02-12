from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import random

#from mainClasses.SGDiagram import SGDiagram
from mainClasses.gameAction.SGGameActions import SGGameActions
from mainClasses.AttributeAndValueFunctionalities import *

# Class who is in charged of entities : cells and agents
class SGEntity(QtWidgets.QWidget,AttributeAndValueFunctionalities):
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
        self.history["value"]={}
        self.list_history = []
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
            self.setListHistory()

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
        raise ValueError('a priori, cette méthode est obsolete')
        return self.model.nameOfPov

    def getRandomXY(self):
        x = 0
        maxSize=self.cell.size
        x = random.randint(1,maxSize-1)
        return x

    def updateMqtt(self):
        if self.model.mqttMajType == "Instantaneous":
            self.model.publishEntitiesState()

    def getObjectIdentiferForJsonDumps(self):
        dict ={}
        dict['entityName']=self.classDef.entityName
        dict['id']=self.id
        return dict
    
    def addWatcher(self,aIndicator):
        aAtt = aIndicator.attribut
        if aAtt not in self.watchers.keys():
            self.watchers[aAtt]=[]
        self.watchers[aAtt].append(aIndicator)

    def updateWatchersOnAttribute(self,aAtt):
        for watcher in self.watchers.get(aAtt,[]):
            watcher.checkAndUpdate()

    def getObjValue(self, obj):
        return obj() if not callable(obj()) else None

    def getHistoryDataJSON(self):
        k = len(self.model.simulationVariables) - 1
        simvariable_dict = {}
        if self.model.simulationVariables[k] and self.model.simulationVariables[k].name:
            simvariable_dict = {'name': self.model.simulationVariables[k].name,
                                'value': self.model.simulationVariables[k].value}
        self.history = {
            'id': self.id,
            'currentPlayer': self.model.currentPlayer,
            'entityDef': self.classDef.entityName if self.classDef.entityName == 'Cell' else 'Agent',
            'entityName': self.classDef.entityName,
            'simVariable': simvariable_dict,
            'round': self.model.timeManager.currentRound,
            'phase': self.model.timeManager.currentPhase,
            'attribut': self.dictAttributes
        }
        history = self.history
        return history
    
    def setSGHistory(self, entDef, currentRound, currentPhase):
        endDef = 'Agent' if entDef != 'Cell' else 'Cell'
        tmpDict = {}
        if self.classDef.attributesDefaultValues:
            #print("self.classDef.attributesDefaultValues : ", self.classDef.attributesDefaultValues.items())
            for key, value in self.classDef.attributesDefaultValues.items():
                tmpDictValue = self.getObjValue(value)
                tmpDict = {key : tmpDictValue}
                #print("tmpDictValue : ", tmpDictValue)
        value = {'value': [currentRound, currentPhase, tmpDict]}
        k = len(self.model.simulationVariables) - 1
        simVariable = self.model.simulationVariables[k] if len(self.model.simulationVariables)>0 and isinstance(self.model.simulationVariables[k], dict)  else {}

        self.history = {
            'id': self.id,
            'currentPlayer': self.model.currentPlayer,
            'entityDef': endDef,
            'entityName': self.classDef.entityName,
            'simVariable': simVariable,
            'round': currentRound,
            'phase': currentPhase,
            'value': value,
            'attribut': self.dictAttributes
        }

        #print("self.cellOfGrids.keys() :: ", self.model.cellOfGrids.keys())

    def setHistoryFormat(self, aAttribute, aValue, dict_value):
        k = len(self.model.simulationVariables) - 1
        simvariable_dict = {}
        if self.model.simulationVariables[k] and self.model.simulationVariables[k].name:
            simvariable_dict = {'name': self.model.simulationVariables[k].name, 'value': self.model.simulationVariables[k].value}
        self.history = {
            'id': self.id,
            'currentPlayer': self.model.currentPlayer,
            'entityDef': self.classDef.entityName if self.classDef.entityName == 'Cell' else 'Agent',
            'entityName': self.classDef.entityName,
            'simVariable': simvariable_dict,
            'round': self.model.timeManager.currentRound,
            'phase': self.model.timeManager.currentPhase,
             aAttribute: aValue,
            'attribut': aAttribute,
            'dict_attribut': self.dictAttributes,
            'value': dict_value
        }



    def saveHistoryValue(self):
        self.setSGHistory(self.classDef.entityName, self.model.timeManager.currentRound,
                          self.model.timeManager.currentPhase)

    def setListHistory(self):
        for aEntity in self.model.getAllEntities():
            h = aEntity.getHistoryDataJSON()
            self.list_history.append(h)

    def getListHistory(self):
        return self.list_history

    def saveValueInHistory(self,aAttribute,aValue):
        #ToDo Tester laquelle de ces deux lignes est la plus rapide
        # if aAttribute not in self.history["value"]:self.history["value"][aAttribute]=[]
        dict_value = {aAttribute: [self.model.timeManager.currentRound, self.model.timeManager.currentPhase, aValue]}
        #print("history :: ", self.history)

        if aValue and 'id' in self.history:
            #print("history :: ", self.history)
            self.setHistoryFormat(aAttribute, aValue, dict_value)



    def isDeleted(self):
        return not self.isDisplay
    #To handle the attributs and values

    # def setValue(self,aAttribut,aValue):
    #     """
    #     Sets the value of an attribut
    #     Args:
    #         aAttribut (str): Name of the attribute
    #         aValue (str): Value to be set
    #     """

    #     if aAttribut in self.dictAttributes and self.dictAttributes[aAttribut]==aValue: return False #The attribute has already this value
    #     self.saveHistoryValue()

    #     self.dictAttributes[aAttribut]=aValue



    # def setValue(self,aAttribut,valueToSet):
    #     """
    #     Sets the value of an attribut
    #     Args:
    #         aAttribut (str): Name of the attribute
    #         aValue (str): Value to be set
    #     """
    #     if callable(valueToSet):
    #         aValue = valueToSet()
    #     else:
    #         aValue = valueToSet
    #     # if self.model.round()!=0 and not aAttribut in self.dictAttributes: raise ValueError("Not such an attribute") ## Instrtcuion commented because agentRecreatedWhen Moving need to pass over this condition
    #     if aAttribut in self.dictAttributes and self.dictAttributes[aAttribut]==aValue: return False #The attribute has already this value
    #     self.saveHistoryValue()    
    #     self.dictAttributes[aAttribut]=aValue
    #     self.classDef.updateWatchersOnAttribute(aAttribut) #This is for watchers on the wole pop of entities
    #     self.updateWatchersOnAttribute(aAttribut) #This is for watchers on this specific entity
    #     self.updateMqtt()
    #     self.update()
    #     return True
