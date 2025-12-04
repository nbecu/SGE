from mainClasses.SGLegend import SGLegend
from mainClasses.SGControlPanel import SGControlPanel
from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell
from collections import defaultdict

from mainClasses.gameAction.SGDelete import *
from mainClasses.gameAction.SGModify import *
from mainClasses.gameAction.SGMove import *
from mainClasses.gameAction.SGActivate import *
from mainClasses.gameAction.SGFlip import *
from mainClasses.gameAction.SGAbstractAction import *
from mainClasses.AttributeAndValueFunctionalities import *


import copy


# Class that handle the player
class SGPlayer(AttributeAndValueFunctionalities):
    def __init__(self, theModel, name, actions=[],attributesAndValues=None):
        self.model = theModel
        self.name = name
        self.isAdmin = False
        self.actions = actions
        self.gameActions = []
        self.remainActions = {}
        self.controlPanel= None
        self.watchers={}
        #Define variables to handle the history 
        self.history={}
        self.history["value"]=defaultdict(list)
        self.initAttributes(attributesAndValues)

    def newControlPanel(self, title=None, defaultActionSelected = None):
        """
        To create an Player Control Panel (only with the GameActions related elements)

        Args:
        Name (str): name of the Control Panel, displayed

        """
        if title==None: title = (self.name +' actions')
        
        self.controlPanel=SGControlPanel(self,title,defaultActionSelected=defaultActionSelected)
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
            self.controlPanel.move( self.controlPanel.startXBase + 20 * pos[0],
                                    self.controlPanel.startYBase + 20 * pos[1])
        # self.model.applyAutomaticLayout()
        return self.controlPanel

    # To handle attributesAndValues
    # setter
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
        if aAttribut in self.dictAttributes and self.dictAttributes[aAttribut]==aValue: return False #The attribute has already this value
        self.dictAttributes[aAttribut]=aValue
        self.saveValueInHistory(aAttribut,aValue)
        # self.type.updateWatchersOnAttribute(aAttribut) #This is for watchers on the whole pop of entities
        self.updateWatchersOnAttribute(aAttribut) #This is for watchers on this specific entity
        # self.model.update()
        return True

    def getListOfStepsData(self,startStep=None,endStep=None):
        aList=self.getListOfUntagedStepsData(startStep,endStep)
        return [{**{'playerName': self.name}, **aStepData} for aStepData in aList]

    def getStatsOfGameActions(self):
        stats = []
                
        currentRound = self.model.timeManager.currentRoundNumber
        currentPhase = self.model.timeManager.currentPhaseNumber
        nbPhases = self.model.timeManager.numberOfPhases()

        # D'abord traiter l'étape d'initialisation (0,0)
        step_actions = {
            'player_name': self.name,
            'round': 0,
            'phase': 0,
            'actions_performed': [
                {
                    'action_id': action.id,
                    'action_type': action.getGraphIdentifier(),
                    'usage_count': len([p for p in action.history["performed"] if p[0] == 0 and p[1] == 0])
                }
                for action in self.gameActions
                # if any(p[0] == 0 and p[1] == 0 for p in action.history["performed"])
            ]
        }
        stats.append(step_actions)
        
        # Ensuite parcourir tous les rounds (à partir de 1)
        for round_num in range(1, currentRound + 1):
            # Pour chaque round, parcourir toutes les phases (à partir de 1)
            for phase_num in range(1, nbPhases + 1):
                if round_num == currentRound and phase_num > currentPhase: continue
                step_actions = {
                    'player_name': self.name,
                    'round': round_num,
                    'phase': phase_num,
                    'actions_performed': [
                        {
                            'action_id': action.id,
                            'action_type': action.getGraphIdentifier(),
                            'usage_count': len([p for p in action.history["performed"] if p[0] == round_num and p[1] == phase_num])
                        }
                        for action in self.gameActions
                        # if any(p[0] == round_num and p[1] == phase_num for p in action.history["performed"])
                    ]
                }
                if step_actions['actions_performed']:
                    stats.append(step_actions)
        return stats
        # return [{**{'playerName': self.name}, **aStepData} for aStepData in aList]

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
    
    def getAllGameActionsOn(self, anEntityInstance):
        actionsForMenu=[]
        entityDef=anEntityInstance.type
        for aGameAction in self.gameActions:
            # Check if action type matches and target type matches
            # Note: Need to check targetType for all action types to ensure correct filtering
            if aGameAction.targetType == entityDef:
                if (isinstance(aGameAction, SGModify) or 
                    isinstance(aGameAction, SGActivate) or 
                    isinstance(aGameAction, SGDelete) or
                    isinstance(aGameAction, SGFlip)):
                    actionsForMenu.append(aGameAction)
        return actionsForMenu
    
    def getAuthorizedGameActionsOn(self, anEntityInstance):
        raise ValueError("Not used, to be deleted")
        actions = self.getAllGameActionsOn(anEntityInstance)
        for aAction in actions:
            if isinstance(aAction,SGActivate):
                return
    
    def getMoveActionsOn(self, anEntityInstance):
        entityDef=anEntityInstance.type
        moveActions=[]
        for aGameAction in self.gameActions:
            if isinstance(aGameAction,SGMove):
                moveActions.append(aGameAction)
        return moveActions
    
    def getAuthorizedActionWithDirectClick(self, entity):
        """
        Get the first authorized action with directClick=True for an entity
        
        Args:
            entity: The entity (agent, tile, or cell)
            
        Returns:
            action: The first authorized action with directClick=True, or None
        """
        entityDef = entity.type
        for action in self.gameActions:
            if (hasattr(action, 'action_controler') and 
                action.action_controler.get("directClick") == True and
                action.targetType == entityDef):
                # Check authorization (some actions need destination entity for Move)
                from mainClasses.gameAction.SGMove import SGMove
                if isinstance(action, SGMove):
                    # For Move, we'll check authorization during drop
                    return action
                elif action.checkAuthorization(entity):
                    return action
        return None
    

    def getAuthorizedMoveActionForDrop(self, entity, target_cell):
        """
        Get the authorized move action for a drop event
        
        Args:
            entity: The entity (agent or tile) being dropped
            target_cell: The cell where the entity is being dropped
            
        Returns:
            moveAction: The first authorized move action, or None if none found
        """
        # Get move actions for this entity (agent or tile)
        moveActions = self.getMoveActionsOn(entity)
        
        # Find the first authorized move action
        for aMoveAction in moveActions:
            if aMoveAction.checkAuthorization(entity, target_cell):
                return aMoveAction
                
        return None

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
    
    def addGameActions(self, actions):
        if isinstance(actions,SGAbstractAction):
            self.addGameAction(actions)
        elif isinstance(actions,list):
            for aAction in actions:
                self.addGameAction(aAction)
        else:
            raise ValueError("wrong format")

    def hasActionsToUse(self):
        for action in self.gameActions:
            if action.canBeUsed():
                return True
        return False
    
