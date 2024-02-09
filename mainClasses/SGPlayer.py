from mainClasses.SGLegend import SGLegend
from mainClasses.SGControlPanel import SGControlPanel
from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell

from mainClasses.gameAction.SGDelete import SGDelete
from mainClasses.gameAction.SGUpdate import SGUpdate
from mainClasses.gameAction.SGCreate import SGCreate
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
        # self.saveHistoryValue()    
        self.dictAttributes[aAttribut]=aValue
        self.updateWatchersOnAttribute(aAttribut) #This is for watchers on this specific entity
        return True

    def addWatcher(self,aIndicator):
        if aIndicator.attribut is None:
            aAtt = 'nb'
        else: aAtt = aIndicator.attribut
        if aAtt not in self.watchers.keys():
            self.watchers[aAtt]=[]
        self.watchers[aAtt].append(aIndicator)

    def updateWatchersOnAttribute(self,aAtt):
        for watcher in self.watchers.get(aAtt,[]):
            watcher.checkAndUpdate()

    def newControlPanelOLD(self, Name=None, showAgentsWithNoAtt=False):
        #OBSOLETE
        """
        To create an Player Control Panel (only with the GameActions related elements)

        Args:
        Name (str): name of the Control Panel, displayed

        """
        #define defaultName if none defined
        if Name==None:
             Name= (self.name +' actions')
        # Creation
        # We harvest all the case value
        elements = {}
        AgentPOVs = self.model.getAgentPOVs()
        for anElement in self.model.getGrids():
            elements[anElement.id] = {}
            elements[anElement.id]['cells'] = anElement.getValuesForLegend()
            elements[anElement.id]['agents'] = {}
        for grid in elements:
            elements[grid]['agents'].update(AgentPOVs)
        agents = self.model.getAllAgents()
        goodKeys = self.getAttributs()
        thePov = self.getPov()
        actions = self.gameActions
        deleteButtons = []
        for aAction in actions:
            if isinstance(aAction, SGDelete):
                deleteButtons.append(str(aAction.name))
        playerElements = {}
        newDict = {}
        for grid_key, grid_value in elements.items():
            playerElements[grid_key] = {'cells': {}, 'agents': {}}
            for cell_key, cell_value in grid_value['cells'].items():
                for aPov, aDict in thePov.items():
                    for dictElement in aDict:
                        for testAtt, testVal in dictElement.items():
                            if cell_key in goodKeys or cell_key == aPov:  # ! watch out any bug here
                                if aPov in playerElements[grid_key]['cells']:
                                    if testAtt in playerElements[grid_key]['cells'][aPov]:
                                        lastValue = playerElements[grid_key]['cells'][aPov][testAtt]
                                        playerElements[grid_key]['cells'][aPov][testAtt] = {
                                            lastValue: 0, testVal: 0}
                                else:
                                    playerElements[grid_key]['cells'][aPov] = {
                                        testAtt: testVal}
            for agent_key, agent_value in grid_value['agents'].items():
                if agent_key in goodKeys:
                    playerElements[grid_key]['agents'][agent_key] = agent_value
        playerElements["deleteButtons"] = deleteButtons
        aLegend = SGLegend(self.model, Name, playerElements, #Un controlPanel ne doit pas etre une instance de Legend, Il faut faire une classe fille de Legend, spécifique pour ControlPanel
                           self.name, agents, showAgentsWithNoAtt, legendType="player")
        self.model.gameSpaces[Name] = aLegend
        self.controlPanel=aLegend
        # Realocation of the position thanks to the layout
        newPos = self.model.layoutOfModel.addGameSpace(aLegend)
        aLegend.setStartXBase(newPos[0])
        aLegend.setStartYBase(newPos[1])
        if (self.model.typeOfLayout == "vertical"):
            aLegend.move(aLegend.startXBase, aLegend.startYBase+20 *
                         self.model.layoutOfModel.getNumberOfAnElement(aLegend))
        elif (self.model.typeOfLayout == "horizontal"):
            aLegend.move(aLegend.startXBase+20 *
                         self.model.layoutOfModel.getNumberOfAnElement(aLegend), aLegend.startYBase)
        else:
            pos = self.model.layoutOfModel.foundInLayout(aLegend)
            aLegend.move(aLegend.startXBase+20 *
                         pos[0], aLegend.startYBase+20*pos[1])
        self.model.applyPersonalLayout()
        return aLegend

    def getAttributs(self):
        attributs = []
        for action in self.gameActions:
            # and not isinstance (action,SGDelete) #! cas des agents sans attributs
            if isinstance(action.anObject, SGAgent) and not isinstance(action, SGMove):
                attributs.append(action.anObject.name)
            if (isinstance(action.anObject, SGCell) or action.anObject == SGCell) and isinstance(action, SGUpdate):  # ! cas des cellules
                key = ''.join(list(action.dictNewValues.keys()))
                attributs.append(key)
        return attributs
    
    def getGameActionsOn(self, anEntityInstance):
        actionsForMenu=[]
        entityDef=anEntityInstance.classDef
        for aGameAction in self.gameActions:
            if isinstance(aGameAction,SGUpdate) and aGameAction.targetEntDef==entityDef:
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
            # isinstance() checks that a gameAction is a instance of SGAbstractAction or of one of its subclasses (SGMove, SGUpdate...)
            self.gameActions.append(aGameAction)
        return aGameAction

    
