from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

# Class who manage the game mechanics of Flipping Tiles
class SGFlip(SGAbstractAction):
    def __init__(self, type, number, conditions=[], feedbacks=[], conditionsOfFeedback=[], nameToDisplay=None, setControllerContextualMenu=False, setOnController=True):
        super().__init__(type, number, conditions, feedbacks, conditionsOfFeedback, nameToDisplay, setControllerContextualMenu, setOnController)
        self.nameToDisplay = nameToDisplay or "🔄 Flip"  # Default name with emoji
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
        print('note : flip execution')
        if hasattr(aTargetEntity, 'flip'):
            aTargetEntity.flip()
        return aTargetEntity
    
    def generateLegendItems(self, aControlPanel):
        """Generate legend items for the flip action"""
        if self.setControllerContextualMenu == False:
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

