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
    def __init__(self, theModel, name, actions=[]):
        self.model = theModel
        self.name = name
        self.actions = actions
        self.gameActions = []
        self.remainActions = {}
        self.controlPanel= None
        #self.initAttributes() #! BUG

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

    def getPov(self):
        # Pourquoi un player à une méthode getPov. C'est bizarre et peut etre Obsolete
        thePov = {}
        for action in self.gameActions:
            if (isinstance(action.anObject, SGCell) or action.anObject == SGCell) and isinstance(action, SGUpdate):  # ! cas des cellules
                aPov = self.model.getPovWithAttribut(list(action.dictNewValues.keys())[0])
                if aPov is not None:
                    if aPov in thePov:
                        thePov[aPov].append(action.dictNewValues)
                    else:
                        thePov[aPov] = [action.dictNewValues]
                else:
                    aPov = self.model.getBorderPovWithAttribut(list(action.dictNewValues.keys())[0])
                    if aPov in thePov:
                        thePov[aPov].append(action.dictNewValues)
                    else:
                        thePov[aPov] = [action.dictNewValues]
        return thePov
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

    def getGameActionOn(self, anItem):
        # Verifier si cettte méthode est encore utilisée ou pas
        # Elle est peut etre Obsolete

        # On cell
        if isinstance(anItem, SGCell) or anItem == SGCell:
            for aGameAction in self.gameActions:
                if not isinstance(aGameAction, SGMove):
                    # Creation of Cell
                    if isinstance(aGameAction, SGCreate) and (anItem.isDisplay == False) and self.model.selected[3] in list(aGameAction.dictAttributs.values())[0] and self.model.selected[4] in list(aGameAction.dictAttributs.keys()):
                        return aGameAction
                    # Creation of an agent
                    elif isinstance(aGameAction, SGCreate) and self.model.selected[1] not in ['square', 'hexagonal']:
                        if aGameAction.dictAttributs is not None:
                            if self.model.selected[3] in list(aGameAction.dictAttributs.values())[0] and self.model.selected[4] in list(aGameAction.dictAttributs.keys()):
                                return aGameAction
                        else:
                            if self.model.selected[2] in list(self.model.agentSpecies.keys()):
                                return aGameAction
                    # Update of a Cell
                    elif isinstance(aGameAction, SGUpdate) and (anItem.isDisplay == True) and self.model.selected[1] in ['square', 'hexagonal'] and self.model.selected[3] in list(aGameAction.dictNewValues.values()) and self.model.selected[4] in list(aGameAction.dictNewValues.keys()):
                        return aGameAction
                    # Delete of a Cell
                    elif isinstance(aGameAction, SGDelete) and (anItem.isDisplay == True) and self.model.selected[1] in ['square', 'hexagonal'] and aGameAction.anObject == SGCell: #and self.model.selected[3] in list(anItem.dictAttributes.values()):
                        return aGameAction
        elif isinstance(anItem, SGAgent):
            for aGameAction in self.gameActions:
                if not isinstance(aGameAction, SGMove):
                    # Update of an Angent
                    if isinstance(aGameAction, SGUpdate) and self.model.selected[2].find("Delete ") == -1 and self.model.selected[1] not in ['square', 'hexagonal']:
                        if self.model.selected[3] in list(aGameAction.dictAttributs.values())[0] and self.model.selected[4] in list(aGameAction.dictAttributs.keys()):
                            return aGameAction
                    # Delete of an Agent
                    elif isinstance(aGameAction, SGDelete) and self.model.selected[1] not in ['square', 'hexagonal']:
                        if aGameAction.dictAttValue is not None:
                            if self.model.selected[3] in list(aGameAction.dictAttValue.values())[0] and self.model.selected[4] in list(aGameAction.dictAttValue.keys()):
                                return aGameAction
                        else:
                            if self.model.selected[2].find("Delete ") != -1:
                                # (self.model.selected[2] in list(self.model.agentSpecies.keys())): #Cas des agents sans POV
                                if (self.model.selected[2].split()[1] in list(self.model.agentSpecies.keys())):
                                    return aGameAction

    def getMooveActionOn(self, anItem):
        if isinstance(anItem, SGAgent):
            for aGameAction in self.gameActions:
                if isinstance(aGameAction, SGMove):
                    # Move an Angent
                    if aGameAction.dictAttributs is not None:
                        for att in list(anItem.dictAttributes.keys()):
                            if att in list(aGameAction.dictAttributs.keys()):
                                if (anItem.dictAttributes[att] in list(aGameAction.dictAttributs.values())[0]):
                                    return aGameAction
                    else:
                        if anItem.species in list(self.model.agentSpecies.keys()):
                            return aGameAction
