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
        from mainClasses.gameAction.SGCreate import SGCreate
        
        for aGameAction in self.gameActions:
            # Special handling for CreateActions: they target cells but create agents/tiles
            if isinstance(aGameAction, SGCreate):
                # For CreateActions, check that entity is a cell
                if anEntityInstance.type.isCellType:
                    actionsForMenu.append(aGameAction)
            # For all other actions, check that targetType matches entity type
            elif aGameAction.targetType == entityDef:
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
        from mainClasses.gameAction.SGMove import SGMove
        from mainClasses.gameAction.SGCreate import SGCreate
        
        for action in self.gameActions:
            if (hasattr(action, 'action_controler') and 
                action.action_controler.get("directClick") == True):
                
                # Check if action can be used (player authorization check)
                can_use = action.canBeUsed()
                
                # Special handling for CreateActions: they target cells but create agents/tiles
                if isinstance(action, SGCreate):
                    # For CreateActions, check that entity is a cell and action is authorized
                    if entity.type.isCellType and action.checkAuthorization(entity):
                        return action
                # For all other actions, check that targetType matches entity type
                elif action.targetType == entityDef:
                    # Check authorization (some actions need destination entity for Move)
                    if isinstance(action, SGMove):
                        # For Move, we should also check canBeUsed before returning
                        if can_use:
                            return action
                    elif action.checkAuthorization(entity):
                        return action
        
        return None
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

# ============================================================================
# MODELER METHODS
# ============================================================================
    def __MODELER_METHODS__(self):
        pass

# ============================================================================
# NEW/ADD METHODS
# ============================================================================
    def __MODELER_METHODS__NEW__(self):
        pass
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

    def newActivateAction(self, object_type=None, method=None, uses_per_round='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[], label=None, action_controler=None):
        """
        Create a new ActivateAction and automatically add it to this player.
        
        This is a convenience method that creates the action via the model and automatically
        adds it to the player's gameActions list.
        
        Args:
            object_type: the model itself or a type of entity (agentType, cellType or name of the entity type)
            method (lambda function): the method to activate
            uses_per_round (int): number of uses per round, could use "infinite"
            conditions (list of lambda functions): conditions on the activating entity
            feedbacks (list of lambda functions): feedbacks to execute after activation
            conditionsOfFeedback (list of lambda functions): conditions for feedback execution
            label (str): label to display for this action in the interface
            action_controler (dict): Interaction modes configuration (controlPanel, contextMenu, button, directClick)
                - controlPanel: bool (default True)
                - contextMenu: bool (default False)
                - button: bool (default False) - whether to create a button
                - buttonPosition: tuple (optional) - coordinates of the button. If button=True but buttonPosition is not specified, a default position (50, 50) will be used.
                - directClick: bool (default False)
        
        Returns:
            SGActivate: The created activate action (already added to player)
        """
        # Create the action via the model
        action = self.model.newActivateAction(
            object_type=object_type,
            method=method,
            uses_per_round=uses_per_round,
            conditions=conditions,
            feedbacks=feedbacks,
            conditionsOfFeedback=conditionsOfFeedback,
            label=label,
            action_controler=action_controler
        )
        # Automatically add it to this player
        self.addGameAction(action)
        return action

    def newCreateAction(self, entity_type, dictAttributes=None, uses_per_round='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[], label=None, create_several_at_each_click=False, writeAttributeInLabel=False, action_controler=None):
        """
        Create a new CreateAction and automatically add it to this player.
        
        This is a convenience method that creates the action via the model and automatically
        adds it to the player's gameActions list.
        
        Args:
            entity_type: a type of entity (agentType, cellType or name of the entity type)
            uses_per_round (int): number of uses per round, could use "infinite"
            dictAttributes (dict): attribute with value concerned, could be None
            conditions (list): conditions that must be met
            feedbacks (list): actions to execute after creation
            conditionsOfFeedback (list): conditions for feedback execution
            label (str): custom label to display
            create_several_at_each_click (bool): whether to create several entities at each click
            writeAttributeInLabel (bool): whether to show attribute in label
            action_controler (dict): Interaction modes configuration (controlPanel, contextMenu, directClick)
        
        Returns:
            SGCreate: The created create action (already added to player)
        """
        action = self.model.newCreateAction(
            entity_type=entity_type,
            dictAttributes=dictAttributes,
            uses_per_round=uses_per_round,
            conditions=conditions,
            feedbacks=feedbacks,
            conditionsOfFeedback=conditionsOfFeedback,
            label=label,
            create_several_at_each_click=create_several_at_each_click,
            writeAttributeInLabel=writeAttributeInLabel,
            action_controler=action_controler
        )
        self.addGameAction(action)
        return action

    def newModifyAction(self, entity_type, dictAttributes={}, uses_per_round='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[], label=None, writeAttributeInLabel=False, action_controler=None):
        """
        Create a new ModifyAction and automatically add it to this player.
        
        This is a convenience method that creates the action via the model and automatically
        adds it to the player's gameActions list.
        
        Args:
            entity_type: a type of entity (agentType, cellType or name of the entity type)
            uses_per_round (int): number of uses per round, could use "infinite"
            dictAttributes (dict): attribute with value concerned, could be None
            conditions (list): conditions that must be met
            feedbacks (list): actions to execute after modification
            conditionsOfFeedback (list): conditions for feedback execution
            label (str): custom label to display
            writeAttributeInLabel (bool): whether to show attribute in label
            action_controler (dict): Interaction modes configuration (controlPanel, contextMenu, directClick)
        
        Returns:
            SGModify: The created modify action (already added to player)
        """
        action = self.model.newModifyAction(
            entity_type=entity_type,
            dictAttributes=dictAttributes,
            uses_per_round=uses_per_round,
            conditions=conditions,
            feedbacks=feedbacks,
            conditionsOfFeedback=conditionsOfFeedback,
            label=label,
            writeAttributeInLabel=writeAttributeInLabel,
            action_controler=action_controler
        )
        self.addGameAction(action)
        return action

    def newModifyActionWithDialog(self, entity_type, attribute, uses_per_round='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[], label=None, writeAttributeInLabel=False, action_controler=None):
        """
        Create a new ModifyActionWithDialog and automatically add it to this player.
        
        This is a convenience method that creates the action via the model and automatically
        adds it to the player's gameActions list. The action opens a dialog to ask for the value to use.
        
        Args:
            entity_type: a type of entity (agentType, cellType or name of the entity type)
            attribute (str): the attribute to modify
            uses_per_round (int): number of uses per round, could use "infinite"
            conditions (list): conditions that must be met
            feedbacks (list): actions to execute after modification
            conditionsOfFeedback (list): conditions for feedback execution
            label (str): custom label to display
            writeAttributeInLabel (bool): whether to show attribute in label
            action_controler (dict): Interaction modes configuration (controlPanel, contextMenu, directClick)
        
        Returns:
            SGModifyActionWithDialog: The created modify action with dialog (already added to player)
        """
        action = self.model.newModifyActionWithDialog(
            entity_type=entity_type,
            attribute=attribute,
            uses_per_round=uses_per_round,
            conditions=conditions,
            feedbacks=feedbacks,
            conditionsOfFeedback=conditionsOfFeedback,
            label=label,
            writeAttributeInLabel=writeAttributeInLabel,
            action_controler=action_controler
        )
        self.addGameAction(action)
        return action

    def newDeleteAction(self, entity_type, uses_per_round='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[], label=None, action_controler=None):
        """
        Create a new DeleteAction and automatically add it to this player.
        
        This is a convenience method that creates the action via the model and automatically
        adds it to the player's gameActions list.
        
        Args:
            entity_type: a type of entity (agentType, cellType or name of the entity type)
            uses_per_round (int): number of uses per round, could use "infinite"
            conditions (list): conditions that must be met
            feedbacks (list): actions to execute after deletion
            conditionsOfFeedback (list): conditions for feedback execution
            label (str): custom label to display
            action_controler (dict): Interaction modes configuration (controlPanel, contextMenu, directClick)
        
        Returns:
            SGDelete: The created delete action (already added to player)
        """
        action = self.model.newDeleteAction(
            entity_type=entity_type,
            uses_per_round=uses_per_round,
            conditions=conditions,
            feedbacks=feedbacks,
            conditionsOfFeedback=conditionsOfFeedback,
            label=label,
            action_controler=action_controler
        )
        self.addGameAction(action)
        return action

    def newMoveAction(self, agent_type, uses_per_round='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[], feedbacksAgent=[], conditionsOfFeedBackAgent=[], label=None, action_controler=None):
        """
        Create a new MoveAction and automatically add it to this player.
        
        This is a convenience method that creates the action via the model and automatically
        adds it to the player's gameActions list.
        
        Args:
            agent_type: a type of agent (agentType or name of the agent type)
            uses_per_round (int): number of uses per round, could use "infinite"
            conditions (list of lambda functions): conditions on the moving Entity
            feedbacks (list): feedback actions
            conditionsOfFeedback (list): conditions for feedback execution
            feedbacksAgent (list): agent feedback actions
            conditionsOfFeedBackAgent (list): conditions for agent feedback execution
            label (str): custom label to display
            action_controler (dict): Interaction modes configuration (controlPanel, contextMenu, directClick)
        
        Returns:
            SGMove: The created move action (already added to player)
        """
        action = self.model.newMoveAction(
            agent_type=agent_type,
            uses_per_round=uses_per_round,
            conditions=conditions,
            feedbacks=feedbacks,
            conditionsOfFeedback=conditionsOfFeedback,
            feedbacksAgent=feedbacksAgent,
            conditionsOfFeedBackAgent=conditionsOfFeedBackAgent,
            label=label,
            action_controler=action_controler
        )
        self.addGameAction(action)
        return action

    def newFlipAction(self, tile_type, uses_per_round='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[], label=None, action_controler=None):
        """
        Create a new FlipAction and automatically add it to this player.
        
        This is a convenience method that creates the action via the model and automatically
        adds it to the player's gameActions list.
        
        Args:
            tile_type: The tile type (SGTileType) to flip
            uses_per_round: Number of times the action can be used per round (default: 'infinite')
            conditions: List of conditions that must be met
            feedbacks: List of feedback actions
            conditionsOfFeedback: List of conditions for feedbacks
            label: Custom label to display (default: "🔄 Flip")
            action_controler (dict): Interaction modes configuration (controlPanel, contextMenu, directClick)
        
        Returns:
            SGFlip: The created flip action (already added to player)
        """
        action = self.model.newFlipAction(
            tile_type=tile_type,
            uses_per_round=uses_per_round,
            conditions=conditions,
            feedbacks=feedbacks,
            conditionsOfFeedback=conditionsOfFeedback,
            label=label,
            action_controler=action_controler
        )
        self.addGameAction(action)
        return action



  
# ============================================================================
# GET/NB METHODS
# ============================================================================
    def __MODELER_METHODS__GET__(self):
        pass  
    
    # @CATEGORY: GET
    def controlPanel(self):
        # access to the control panel
        return (self.model.controlPanel[self.name])




    # ============================================================================
    # IS/HAS METHODS
    # ============================================================================
    def __MODELER_METHODS__IS__(self):
        pass

    def hasActionsToUse(self):
        for action in self.gameActions:
            if action.canBeUsed():
                return True
        return False
    
