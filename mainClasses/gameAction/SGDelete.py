from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

import copy

#Class who manage the game mechanics of delete
class SGDelete(SGAbstractAction):
    def __init__(self,entDef,number,conditions=[],feedBack=[],conditionOfFeedBack=[],nameToDisplay=None,setControllerContextualMenu=False):#,setOnController=True):
        super().__init__(entDef,number,conditions,feedBack,conditionOfFeedBack,nameToDisplay,setControllerContextualMenu)
        self.nameToDisplay=nameToDisplay or f"× delete {self.targetEntDef.entityName}"
        self.actionType="Delete"
        self.addCondition(lambda aTargetEntity: aTargetEntity.classDef == self.targetEntDef and not aTargetEntity.isDeleted())

    def executeAction(self, aTargetEntity):
        self.targetEntDef.deleteEntity(aTargetEntity)

    def generateLegendItems(self,aControlPanel):
        if self.setControllerContextualMenu == False:
            aColor = self.targetEntDef.defaultShapeColor
            return [SGLegendItem(aControlPanel,'symbol',self.nameToDisplay,self.targetEntDef,aColor,gameAction=self)]
