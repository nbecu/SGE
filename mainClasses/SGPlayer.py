from mainClasses.SGLegend import SGLegend
from mainClasses.SGControlPanel import SGControlPanel
from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell
from collections import defaultdict

from mainClasses.gameAction.SGDelete import SGDelete
from mainClasses.gameAction.SGModify import SGModify
from mainClasses.gameAction.SGMove import SGMove
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction
from mainClasses.AttributeAndValueFunctionalities import *


import copy


# Class that handle the player
class SGPlayer(AttributeAndValueFunctionalities):
    def __init__(self, theModel, name, actions=[],attributesAndValues=None):
        self.model = theModel
        self.name = name
        self.actions = actions
        self.gameActions = []
        self.remainActions = {}
        self.controlPanel= None
        self.watchers={}
        #Define variables to handle the history 
        self.history={}
        self.history["value"]=defaultdict(list)
        self.initAttributes(attributesAndValues)

    def newControlPanel(self, title=None, showAgentsWithNoAtt=False):
        """
        To create an Player Control Panel (only with the GameActions related elements)

        Args:
        Name (str): name of the Control Panel, displayed

        """
        if title==None: title = (self.name +' actions')
        
        self.controlPanel=SGControlPanel.forPlayer(self,title)
        self.model.gameSpaces[title] = self.controlPanel
        # Realocation of the position thanks to the layout
        newPos = self.model.layoutOfModel.addGameSpace(self.controlPanel)
        self.controlPanel.setStartXBase(newPos[0])
        self.controlPanel.setStartYBase(newPos[1])
        if (self.model.typeOfLayout == "vertical"):
            self.controlPanel.move(self.controlPanel.startXBase, self.controlPanel.startYBase+20 *
                         self.model.layoutOfModel.getNumberOfAnElement(self.controlPanel))
        elif (self.model.typeOfLayout == "horizontal"):
            self.controlPanel.move(self.controlPanel.startXBase+20 *
                         self.model.layoutOfModel.getNumberOfAnElement(self.controlPanel), self.controlPanel.startYBase)
        else:
            pos = self.model.layoutOfModel.foundInLayout(self.controlPanel)
            self.controlPanel.move(self.controlPanel.startXBase+20 *
                         pos[0], self.controlPanel.startYBase+20*pos[1])
        self.model.applyPersonalLayout()
        return self.controlPanel

    # To handle attributesAndValues
    # setter
    def setValue(self,aAttribut,aValue):
        """
        Sets the value of an attribut
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be set
        """
        if aAttribut in self.dictAttributes and self.dictAttributes[aAttribut]==aValue: return False #The attribute has already this value
        self.saveValueInHistory(aAttribut,aValue)
        self.dictAttributes[aAttribut]=aValue
        self.updateWatchersOnAttribute(aAttribut) #This is for watchers on this specific entity
        return True

    def getListOfStepsData(self,startStep=None,endStep=None):
        aList=self.getListOfUntagedStepsData(startStep,endStep)
        return [{**{'playerName': self.name}, **aStepData} for aStepData in aList]


    def addWatcher(self,aIndicator):
        if aIndicator.attribute is None:
            aAtt = 'nb'
        else: aAtt = aIndicator.attribute
        if aAtt not in self.watchers.keys():
            self.watchers[aAtt]=[]
        self.watchers[aAtt].append(aIndicator)

    def updateWatchersOnAttribute(self,aAtt):
        for watcher in self.watchers.get(aAtt,[]):
            watcher.checkAndUpdate()

    def getAttributs(self):
        attributs = []
        for action in self.gameActions:
            if isinstance(action.anObject, SGAgent) and not isinstance(action, SGMove):
                attributs.append(action.anObject.name)
            if (isinstance(action.anObject, SGCell) or action.anObject == SGCell) and isinstance(action, SGModify):  # ! cas des cellules
                key = ''.join(list(action.dictNewValues.keys()))
                attributs.append(key)
        return attributs
    
    def getGameActionsOn(self, anEntityInstance):
        actionsForMenu=[]
        entityDef=anEntityInstance.classDef
        for aGameAction in self.gameActions:
            if isinstance(aGameAction,SGModify) and aGameAction.targetEntDef==entityDef:
                actionsForMenu.append(aGameAction)
        return actionsForMenu
# -----------------------------------------------------------------------------------------
# Definiton of the methods who the modeler will use

    def controlPanel(self):
        # access to the control panel
        return (self.model.controlPanel[self.name])

    def addGameAction(self, aGameAction):
        """
        Add a action to the Player

        Args:
            aGameAction (instance) : myModel.createAction instance
        """
        if isinstance(aGameAction,SGAbstractAction):
            self.gameActions.append(aGameAction)
        return aGameAction

    
