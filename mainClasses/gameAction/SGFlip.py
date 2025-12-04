from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

# Class who manage the game mechanics of Flipping Tiles
class SGFlip(SGAbstractAction):
    def __init__(self, type, number, conditions=[], feedbacks=[], conditionsOfFeedback=[], nameToDisplay=None, aNameToDisplay=None, setControllerContextualMenu=False, setOnController=True, interaction_modes=None):
        # Set default directClick for Flip
        if interaction_modes is None:
            interaction_modes = {}
        # Backward compatibility: convert autoTrigger="click" to directClick=True
        if "autoTrigger" in interaction_modes:
            if interaction_modes["autoTrigger"] == "click":
                interaction_modes["directClick"] = True
        elif "directClick" not in interaction_modes:
            interaction_modes["directClick"] = True  # Default for Flip
        super().__init__(type, number, conditions, feedbacks, conditionsOfFeedback, nameToDisplay=nameToDisplay, aNameToDisplay=aNameToDisplay, setControllerContextualMenu=setControllerContextualMenu, setOnController=setOnController, interaction_modes=interaction_modes)
        self.nameToDisplay = self.nameToDisplay or "🔄 Flip"  # Default name with emoji
        self.actionType = "Flip"
        self.addCondition(lambda aTargetEntity: aTargetEntity.type == self.targetType)
        self.addCondition(lambda aTargetEntity: hasattr(aTargetEntity, 'isTile') and aTargetEntity.isTile)
        self.addCondition(lambda aTargetEntity: not aTargetEntity.isDeleted())
    
    def executeAction(self, aTargetEntity):
        """
        Execute the flip action on a tile
        
        Args:
            aTargetEntity: The tile to flip
            
        Returns:
            The tile after flipping
        """
        if hasattr(aTargetEntity, 'flip'):
            aTargetEntity.flip()
        return aTargetEntity
    
    def generateLegendItems(self, aControlPanel):
        """Generate legend items for the flip action"""
        # Use setOnController (controlPanel) to determine if action should appear in ControlPanel
        # setControllerContextualMenu only controls context menu, not ControlPanel
        if self.setOnController:
            aColor = self.targetType.defaultShapeColor
            return [SGLegendItem(aControlPanel, 'symbol', self.nameToDisplay, self.targetType, aColor, gameAction=self)]
        return None
    
    # ============================================================================
    # EXPORT INTERFACE METHODS - SGFlip specific implementations
    # ============================================================================
    
    def getActionDetails(self):
        """
        Specific details for SGFlip
        """
        details = super().getActionDetails()
        details["action_type"] = "Flip"
        return details
    
    def _getSpecificActionInfo(self):
        """
        Get specific flip information
        """
        return "Flip: Turn tile to show other face"

