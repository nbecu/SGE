from mainClasses.SGPlayer import SGPlayer
from mainClasses.gameAction.SGCreate import SGCreate
from mainClasses.gameAction.SGDelete import SGDelete
from mainClasses.gameAction.SGModify import SGModify
from mainClasses.gameAction.SGMove import SGMove
from mainClasses.gameAction.SGActivate import SGActivate
from mainClasses.gameAction.SGFlip import SGFlip

class SGAdminPlayer(SGPlayer):
    def __init__(self, model):
        super().__init__(model, "Admin")
        self.isAdmin = True
        # Don't create actions yet - wait for entities to be defined
        # self._createAllGameActions()  # Will be called later
    
    def createAllGameActions(self):
        """Public method to create all gameActions - should be called after all entities are defined"""
        self._createAllGameActions()
    
    def _createAllGameActions(self):
        """Automatically creates all possible gameActions for Admin based on discovered attributes and values"""
        # Get all entities from the model
        allEntityTypes = self.model.getEntityTypes()
        
        # Create actions for each entity type
        for entityDef in allEntityTypes:
            # Create action
            createAction = SGCreate(entityDef, None, 'infinite')
            self.gameActions.append(createAction)
            
            # Delete action
            deleteAction = SGDelete(entityDef, 'infinite')
            self.gameActions.append(deleteAction)
            
            # Modify actions based on discovered attributes and values
            self._createModifyActionsForEntity(entityDef)
            
            # Move action (for agents and tiles)
            if hasattr(entityDef, 'grid'):  # This is a CellDef
                continue
            elif entityDef.isAgentType:  # This is an AgentDef
                moveAction = SGMove(entityDef, 'infinite')
                self.gameActions.append(moveAction)
            elif entityDef.isTileType:  # This is a TileDef
                # Move action for tiles
                moveAction = SGMove(entityDef, 'infinite')
                self.gameActions.append(moveAction)
                # Flip action for tiles
                flipAction = SGFlip(entityDef, 'infinite')
                self.gameActions.append(flipAction)
        
        # Activation actions on the model
        activateAction = SGActivate(self.model, None, 'infinite')
        self.gameActions.append(activateAction)
    
    def _createModifyActionsForEntity(self, entityDef):
        """Creates ModifyActions for an entity based on discovered attributes and values"""
        # Use the new method from SGEntityType
        discoveredAttrs = entityDef.discoverAttributesAndValues()
        
        # Create ModifyActions for each attribute-value combination
        for attribute, possibleValues in discoveredAttrs.items():
            if not possibleValues or (len(possibleValues) == 1 and None in possibleValues):
                # No known values or only None - create dynamic ModifyAction
                dynamicAction = self.model.newModifyActionWithDialog(entityDef, attribute, 'infinite')
                self.gameActions.append(dynamicAction)
            else:
                # Create specific ModifyActions for each known value
                for value in possibleValues:
                    if value is not None:  # Skip None values
                        modifyAction = self.model.newModifyAction(entityDef, {attribute: value}, 'infinite')
                        self.gameActions.append(modifyAction)
    
    def getMoveActionsOn(self, entity):
        """Returns all move actions for a given entity"""
        return [action for action in self.gameActions if isinstance(action, SGMove)]
    
    def getModifyActionsForEntity(self, entityDef, attribute=None, value=None):
        """Returns ModifyActions for a specific entity, optionally filtered by attribute and value"""
        modifyActions = [action for action in self.gameActions if isinstance(action, (SGModify, type(self.model.newModifyActionWithDialog(entityDef, "test", 1))))]
        
        if attribute is not None:
            modifyActions = [action for action in modifyActions 
                           if (isinstance(action, SGModify) and attribute in action.dictAttributs) or
                              (hasattr(action, 'dynamicAttribute') and action.dynamicAttribute == attribute)]
            
        if value is not None and attribute is not None:
            modifyActions = [action for action in modifyActions 
                           if isinstance(action, SGModify) and action.dictAttributs.get(attribute) == value]
            
        return modifyActions
    
    def hasActionFor(self, actionType, entityDef=None):
        """Checks if Admin has an action of a certain type"""
        if actionType == 'move':
            return any(isinstance(action, SGMove) for action in self.gameActions)
        elif actionType == 'create':
            return any(isinstance(action, SGCreate) for action in self.gameActions)
        elif actionType == 'delete':
            return any(isinstance(action, SGDelete) for action in self.gameActions)
        elif actionType == 'modify':
            return any(isinstance(action, (SGModify, type(self.model.newModifyActionWithDialog(entityDef, "test", 1)))) for action in self.gameActions)
        return False