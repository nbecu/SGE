from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction
from mainClasses.SGTimePhase import SGTimePhase,SGModelPhase

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
        if self.checkAuthorization(aMovingEntity,aDestinationEntity):
            aOriginEntity = aMovingEntity.cell
            newCopyOfAgent = self.executeAction(aMovingEntity,aDestinationEntity)
            aMovingEntity = newCopyOfAgent
            if self.feedbacks:
                aFeedbackTarget = self.chooseFeedbackTargetAmong([aMovingEntity,aDestinationEntity,aOriginEntity])
                if self.checkFeedbackAuhorization(aFeedbackTarget):
                    resFeedback = self.executeFeedbacks(aFeedbackTarget)
            self.incNbUsed()
            self.savePerformedActionInHistory(aTargetEntity, aMovingEntity, resFeedback)

            if serverUpdate: self.updateServer_gameAction_performed(aTargetEntity,aDestinationEntity)
            return aMovingEntity if not self.feedbacks else [aMovingEntity,resFeedback]
        else:
            return False

    def checkAuthorization(self,aTargetEntity,aDestinationEntity=None):
        if aDestinationEntity is not None:
            res = True
            if len(self.model.timeManager.phases)==0:
                return True
            if isinstance(self.model.timeManager.phases[self.model.phaseNumber()-1],SGModelPhase):#If this is a ModelPhase, as default players can't do actions
                return False
            if isinstance(self.model.timeManager.phases[self.model.phaseNumber()-1],SGTimePhase):#If this is a TimePhase, as default players can do actions
                player=self.model.getPlayer(self.model.currentPlayer)
                if player in self.model.timeManager.phases[self.model.phaseNumber()-1].authorizedPlayers:
                    res = True
                else:
                    return False
            if self.numberUsed >= self.number:
                return False
            for aCondition in self.conditions:
                if aCondition.__code__.co_argcount == 0:
                    res = res and aCondition()
                elif aCondition.__code__.co_argcount == 1:
                    res = res and aCondition(aTargetEntity)
                elif aCondition.__code__.co_argcount == 2:
                    res = res and aCondition(aTargetEntity, aDestinationEntity)
                else:
                    raise ValueError("aCondition has an unsupported number of arguments")
            return res
        else:
            super().checkAuthorization(aTargetEntity)

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
