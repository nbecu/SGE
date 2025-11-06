from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

import copy

#Class who manage the game mechanics of delete
class SGDelete(SGAbstractAction):
    def __init__(self,type,number,conditions=[],feedbacks=[],conditionsOfFeedback=[],nameToDisplay=None,setControllerContextualMenu=False):#,setOnController=True):
        super().__init__(type,number,conditions,feedbacks,conditionsOfFeedback,nameToDisplay,setControllerContextualMenu)
        self.nameToDisplay=nameToDisplay or f"× delete {self.targetType.name}"
        self.actionType="Delete"
        self.addCondition(lambda aTargetEntity: aTargetEntity.type == self.targetType and not aTargetEntity.isDeleted())

    def executeAction(self, aTargetEntity):
        self.targetType.deleteEntity(aTargetEntity)

    def generateLegendItems(self,aControlPanel):
        if self.setControllerContextualMenu == False:
            aColor = self.targetType.defaultShapeColor
            return [SGLegendItem(aControlPanel,'symbol',self.nameToDisplay,self.targetType,aColor,gameAction=self)]
