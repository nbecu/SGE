from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell
from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

#Class who manage the game mechanics of mooving
class SGMove(SGAbstractAction):
    def __init__(self,anObject,number,conditions=[],feedBack=[],conditionOfFeedBack=[],feedbackAgent=[],conditionOfFeedBackAgent=[]):
        super().__init__(anObject,number,conditions,feedBack,conditionOfFeedBack)
        self.name="Move "+str(anObject.entityName)
        self.feedbackAgent=feedbackAgent
        self.conditionOfFeedBackAgent=conditionOfFeedBackAgent
            
    def executeAction(self, aTargetEntity):
        aTargetEntity.moveTo()

    def generateLegendItems(self,aControlPanel):
        entDef = self.anObject
        aColor = entDef.defaultShapeColor
        return [SGLegendItem(aControlPanel,'symbol','move',entDef,aColor,gameAction=self)]
