from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction
from mainClasses.SGTimePhase import *

#Class who manage the game mechanics of mooving
class SGMove(SGAbstractAction):
    context_menu_icon = "⇄"  # Icon for context menu
    def __init__(self,type,number,conditions=[],feedbacks=[],conditionsOfFeedback=[],feedbackAgent=[],conditionOfFeedBackAgent=[],nameToDisplay=None,aNameToDisplay=None,setControllerContextualMenu=False,setOnController=True,action_controler=None):
        # Move uses drag & drop by default (handled separately, not via directClick)
        if action_controler is None:
            action_controler = {}
        # Note: Move actions use drag & drop by default, which is handled separately from directClick
        # directClick remains False by default for Move (drag & drop is independent)
        super().__init__(type,number,conditions,feedbacks,conditionsOfFeedback,nameToDisplay=nameToDisplay,aNameToDisplay=aNameToDisplay,setControllerContextualMenu=setControllerContextualMenu,setOnController=setOnController,action_controler=action_controler)
        self.nameToDisplay = self.nameToDisplay or "⇄ move"
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
            self.savePerformedActionInHistory(aTargetEntity, aMovingEntity, resFeedback, aDestinationEntity)

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
            # For move actions without destination, test only conditions with 0 or 1 parameter
            # Ignore conditions with 2 parameters (they require a destination)
            # This is necessary because super().checkAuthorization() cannot handle 2-parameter conditions
            if not self.canBeUsed():
                return False
            
            res = True
            for aCondition in self.conditions:
                argcount = aCondition.__code__.co_argcount
                if argcount == 0:
                    res = res and aCondition()
                elif argcount == 1:
                    res = res and aCondition(aTargetEntity)
                elif argcount == 2:
                    # Skip conditions with 2 parameters - they require a destination
                    # These will be checked during drop when destination is known
                    continue
                else:
                    raise ValueError("aCondition has an unsupported number of arguments")
            return res

    def executeAction(self, aMovingEntity,aDestinationEntity):
        # Works for both agents and tiles (both have moveTo method)
        movedEntity = aMovingEntity.moveTo(aDestinationEntity)
        return movedEntity
    
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
    
    # ============================================================================
    # EXPORT INTERFACE METHODS - SGMove specific implementations
    # ============================================================================
    
    def savePerformedActionInHistory(self,aTargetEntity, resAction, resFeedback, aDestinationEntity=None):
        """
        Override for SGMove to include destination entity
        """
        if aDestinationEntity is not None:
            # Call parent method first to create the base history entry
            super().savePerformedActionInHistory(aTargetEntity, resAction, resFeedback)
            
            # Add destination entity to the last entry
            last_entry = self.history["performed"][-1]
            last_entry.append(aDestinationEntity)
        else:
            # Fallback to parent method if no destination
            super().savePerformedActionInHistory(aTargetEntity, resAction, resFeedback)
    
    def getFormattedHistory(self):
        """
        Return formatted history with explicit keys for SGMove
        Includes destination_entity information
        """
        # Get base formatted history from parent
        formatted_history = super().getFormattedHistory()
        
        # Add destination_entity to each entry
        for i, entry in enumerate(self.history["performed"]):
            if len(entry) > 9:
                formatted_history[i]["destination_entity"] = entry[9]
            else:
                formatted_history[i]["destination_entity"] = None
        
        return formatted_history
    