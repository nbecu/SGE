from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

import copy

#Class who manage the game mechanics of delete
class SGDelete(SGAbstractAction):
    def __init__(self,type,number,conditions=[],feedbacks=[],conditionsOfFeedback=[],nameToDisplay=None,aNameToDisplay=None,setControllerContextualMenu=False,setOnController=True,interaction_modes=None):#,setOnController=True):
        super().__init__(type,number,conditions,feedbacks,conditionsOfFeedback,nameToDisplay=nameToDisplay,aNameToDisplay=aNameToDisplay,setControllerContextualMenu=setControllerContextualMenu,setOnController=setOnController,interaction_modes=interaction_modes)
        self.nameToDisplay=self.nameToDisplay or f"× delete {self.targetType.name}"
        self.actionType="Delete"
        self.addCondition(lambda aTargetEntity: aTargetEntity.type == self.targetType and not aTargetEntity.isDeleted())

    def executeAction(self, aTargetEntity):
        self.targetType.deleteEntity(aTargetEntity)

    def generateLegendItems(self,aControlPanel):
        # Use setOnController (controlPanel) to determine if action should appear in ControlPanel
        # setControllerContextualMenu only controls context menu, not ControlPanel
        if self.setOnController:
            aColor = self.targetType.defaultShapeColor
            return [SGLegendItem(aControlPanel,'symbol',self.nameToDisplay,self.targetType,aColor,gameAction=self)]
