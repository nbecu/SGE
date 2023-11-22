from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell
from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

#Class who manage the game mechanics of mooving
class SGMove(SGAbstractAction):
    def __init__(self,entDef,number,conditions=[],feedBack=[],conditionOfFeedBack=[],feedbackAgent=[],conditionOfFeedBackAgent=[]):
        super().__init__(entDef,number,conditions,feedBack,conditionOfFeedBack)
        self.name="Move "+str(self.targetEntDef.entityName)
        self.feedbackAgent=feedbackAgent
        self.conditionOfFeedBackAgent=conditionOfFeedBackAgent
        self.addCondition(lambda aTargetEntity: aTargetEntity.classDef == self.targetEntDef)


    def perform_with(self,aTargetEntity,aDestinationEntity=None,serverUpdate=True):
        # The arg aDestinationEntity has a default value set to None, because the method is also defined at the superclass level and it takes only 2 arguments 
         #The arg aParameterHolder has been removed has it is never used and it complicates the updateServer
        aMovingEntity = aTargetEntity
        if self.checkAuhorization(aMovingEntity):
            aOriginEntity = aMovingEntity.cell
            resAction = self.executeAction(aMovingEntity,aDestinationEntity)
            aFeedbackTarget = self.chooseFeedbackTargetAmong([aMovingEntity,aDestinationEntity,aOriginEntity,resAction]) # Previously Five choices. The choice aParameterHolder, has been removed
            if self.checkFeedbackAuhorization(aFeedbackTarget):
                resFeedback = self.executeFeedback(aFeedbackTarget)
            self.incNbUsed()
            if serverUpdate: self.updateServer_gameAction_performed(aTargetEntity,aDestinationEntity)
            return resFeedback
        else:
            return False

    def executeAction(self, aMovingEntity,aDestinationEntity):
        aMovingEntity.moveTo2(aDestinationEntity)

    def generateLegendItems(self,aControlPanel):
        aColor = self.targetEntDef.defaultShapeColor
        return [SGLegendItem(aControlPanel,'symbol','move',self.targetEntDef,aColor,gameAction=self)]
    
    def chooseFeedbackTargetAmong(self,aListOfChoices):
        # aListOfChoices -> [aMovingEntity,aDestinationEntity,aOriginEntity,aParameterHolder,resAction]
        # The choice aParameterHolder   has been removed
        return aListOfChoices[0]
