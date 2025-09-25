from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction
from mainClasses.SGTimePhase import *

#Class who manage the game mechanics of mooving
class SGMove(SGAbstractAction):
    def __init__(self,type,number,conditions=[],feedbacks=[],conditionsOfFeedback=[],feedbackAgent=[],conditionOfFeedBackAgent=[],nameToDisplay=None,setControllerContextualMenu=False,setOnController=True):
        super().__init__(type,number,conditions,feedbacks,conditionsOfFeedback,nameToDisplay,setControllerContextualMenu,setOnController)
        self.nameToDisplay = nameToDisplay or "⇄ move"
        self.actionType="Move"
        self.feedbackAgent=feedbackAgent
        self.conditionOfFeedBackAgent=conditionOfFeedBackAgent
        self.addCondition(lambda aTargetEntity: aTargetEntity.type == self.targetType)

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
            else : resFeedback = None
            self.incNbUsed()
            self.savePerformedActionInHistory(aTargetEntity, aMovingEntity, resFeedback)

            if serverUpdate: self.updateServer_gameAction_performed(aTargetEntity,aDestinationEntity)

            if not self.model.timeManager.isInitialization():
                self.model.timeManager.getCurrentPhase().handleAutoForward()
            #commented because unsued - return aMovingEntity if not self.feedbacks else [aMovingEntity,resFeedback]
        # else:
        #     return False

    def checkAuthorization(self,aTargetEntity,aDestinationEntity=None):
        if aDestinationEntity is not None:
            # Use the generic canBeUsed() method 
            if not self.canBeUsed():
                return False
            
            # Only handle the specific logic for move actions with destination
            res = True
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
            # For move actions without destination, use the standard authorization
            return super().checkAuthorization(aTargetEntity)

    def executeAction(self, aMovingEntity,aDestinationEntity):
        newCopyOfAgent = aMovingEntity.moveTo(aDestinationEntity)
        return newCopyOfAgent
    
    def executeFeedbacks(self, feedbackTarget):
        listOfRes = []
        for aFeedback in self.feedbacks:
            res = aFeedback() if aFeedback.__code__.co_argcount == 0 else aFeedback(feedbackTarget)
            listOfRes.append(res)
        if not listOfRes: raise ValueError('why is this method called when the list of feedbaks is  empty')
        return res if len(listOfRes) == 1 else listOfRes

    def generateLegendItems(self,aControlPanel):
        if self.setControllerContextualMenu == False:
            aColor = self.targetType.defaultShapeColor
            return [SGLegendItem(aControlPanel,'symbol',self.nameToDisplay,self.targetType,aColor,gameAction=self)]
        
    def chooseFeedbackTargetAmong(self,aListOfChoices):
        # aListOfChoices -> [aMovingEntity,aDestinationEntity,aOriginEntity,aParameterHolder,resAction]
        return aListOfChoices[0]
