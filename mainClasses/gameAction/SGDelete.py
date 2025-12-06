from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

import copy

#Class who manage the game mechanics of delete
class SGDelete(SGAbstractAction):
    context_menu_icon = "🗑️ "  # Icon for context menu
    def __init__(self, type, number, conditions=[], feedbacks=[], conditionsOfFeedback=[], label=None, action_controler=None):
        super().__init__(type, number, conditions, feedbacks, conditionsOfFeedback, label=label, action_controler=action_controler)
        self.nameToDisplay=self.nameToDisplay or f"× delete {self.targetType.name}"
        self.actionType="Delete"
        self.addCondition(lambda aTargetEntity: aTargetEntity.type == self.targetType and not aTargetEntity.isDeleted())

    def executeAction(self, aTargetEntity):
        self.targetType.deleteEntity(aTargetEntity)

    def generateLegendItems(self,aControlPanel):
        # Use action_controler["controlPanel"] to determine if action should appear in ControlPanel
        if self.action_controler.get("controlPanel", True):
            aColor = self.targetType.defaultShapeColor
            return [SGLegendItem(aControlPanel,'symbol',self.nameToDisplay,self.targetType,aColor,gameAction=self)]
