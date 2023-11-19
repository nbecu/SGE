from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell
from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

import copy

#Class who manage the game mechanics of delete
class SGDelete(SGAbstractAction):
    def __init__(self,anObject,number,conditions=[],feedBack=[],conditionOfFeedBack=[]):
        super().__init__(anObject,number,conditions,feedBack,conditionOfFeedBack)
        self.entDef = anObject
        self.name="Delete "+self.entDef.entityName
        self.addCondition(lambda selectedEntity: selectedEntity.classDef == self.entDef)

    def executeAction(self, aTargetEntity):
        self.entDef.deleteEntity(aTargetEntity)

    def generateLegendItems(self,aControlPanel):
        entDef = self.anObject
        aColor = entDef.defaultShapeColor
        return [SGLegendItem(aControlPanel,'symbol','delete',entDef,aColor,gameAction=self)]
