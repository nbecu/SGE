from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

import copy

#Class who manage the game mechanics of delete
class SGDelete(SGAbstractAction):
    def __init__(self,entDef,number,conditions=[],feedBack=[],conditionOfFeedBack=[]):
        super().__init__(entDef,number,conditions,feedBack,conditionOfFeedBack)
        self.name="Delete "+self.targetEntDef.entityName
        self.addCondition(lambda aTargetEntity: aTargetEntity.classDef == self.targetEntDef and not aTargetEntity.isDeleted())

    def executeAction(self, aTargetEntity):
        self.targetEntDef.deleteEntity(aTargetEntity)

    def generateLegendItems(self,aControlPanel):
        aColor = self.targetEntDef.defaultShapeColor
        return [SGLegendItem(aControlPanel,'symbol','delete',self.targetEntDef,aColor,gameAction=self)]
