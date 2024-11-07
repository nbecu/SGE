from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

#Class who manage the game mechanics of Activation
class SGActivate(SGAbstractAction):
    def __init__(self,entDef,method,number,conditions=[],feedBack=[],conditionOfFeedBack=[],setControllerContextualMenu=False):
        super().__init__(entDef,number,conditions,feedBack,conditionOfFeedBack,setControllerContextualMenu)
        self.name="ActivateAction "+ entDef.name
        self.addCondition(lambda aTargetEntity: aTargetEntity.classDef == self.targetEntDef)
        self.addCondition(lambda aTargetEntity: not aTargetEntity.isDeleted())
        self.method=method
    

    def executeAction(self,aTargetEntity):
        self.method(aTargetEntity)
        return aTargetEntity

    def generateLegendItems(self,aControlPanel):
        if self.setControllerContextualMenu == False:
            aColor = self.targetEntDef.defaultShapeColor
            return [SGLegendItem(aControlPanel,'symbol','activate',self.targetEntDef,aColor,gameAction=self)]