from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

#Class who manage the game mechanics of mooving
class SGMove(SGAbstractAction):
    def __init__(self,entDef,number,conditions=[],feedBack=[],conditionOfFeedBack=[],feedbackAgent=[],conditionOfFeedBackAgent=[],setControllerContextualMenu=False):
        super().__init__(entDef,number,conditions,feedBack,conditionOfFeedBack,setControllerContextualMenu)
        self.name="Move "+str(self.targetEntDef.entityName)
        self.feedbackAgent=feedbackAgent
        self.conditionOfFeedBackAgent=conditionOfFeedBackAgent
        self.addCondition(lambda aTargetEntity: aTargetEntity.classDef == self.targetEntDef)


    def perform_with(self,aTargetEntity,aDestinationEntity=None,serverUpdate=True):
        # The arg aDestinationEntity has a default value set to None, because the method is also defined at the superclass level and it takes only 2 arguments 
        aMovingEntity = aTargetEntity
        if self.checkAuthorization(aMovingEntity):
            aOriginEntity = aMovingEntity.cell
            newCopyOfAgent = self.executeAction(aMovingEntity,aDestinationEntity)
            aMovingEntity = newCopyOfAgent
            if self.feedbacks:
                aFeedbackTarget = self.chooseFeedbackTargetAmong([aMovingEntity,aDestinationEntity,aOriginEntity])
                if self.checkFeedbackAuhorization(aFeedbackTarget):
                    resFeedback = self.executeFeedbacks(aFeedbackTarget)
            self.incNbUsed()
            if serverUpdate: self.updateServer_gameAction_performed(aTargetEntity,aDestinationEntity)
            return aMovingEntity if not self.feedbacks else [aMovingEntity,resFeedback]
        else:
            return False


    def executeAction(self, aMovingEntity,aDestinationEntity):
        newCopyOfAgent = aMovingEntity.moveTo(aDestinationEntity)
        return newCopyOfAgent

    def generateLegendItems(self,aControlPanel):
        if self.setControllerContextualMenu == False:
            aColor = self.targetEntDef.defaultShapeColor
            return [SGLegendItem(aControlPanel,'symbol','move',self.targetEntDef,aColor,gameAction=self)]
        
    def chooseFeedbackTargetAmong(self,aListOfChoices):
        # aListOfChoices -> [aMovingEntity,aDestinationEntity,aOriginEntity,aParameterHolder,resAction]
        return aListOfChoices[0]
