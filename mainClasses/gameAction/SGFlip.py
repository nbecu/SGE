from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

# Class who manage the game mechanics of Flipping Tiles
class SGFlip(SGAbstractAction):
    context_menu_icon = "🔄"  # Icon for context menu
    def __init__(self, type, number, conditions=[], feedbacks=[], conditionsOfFeedback=[], label=None, action_controler=None):
        # Set default directClick for Flip
        if action_controler is None:
            action_controler = {}
        if "directClick" not in action_controler:
            action_controler["directClick"] = True  # Default for Flip
        super().__init__(type, number, conditions, feedbacks, conditionsOfFeedback, label=label, action_controler=action_controler)
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
        # Use action_controler["controlPanel"] to determine if action should appear in ControlPanel
        if self.action_controler.get("controlPanel", True):
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

