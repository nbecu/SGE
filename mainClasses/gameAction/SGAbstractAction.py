# from mainClasses.SGAgent import SGAgent  # Commented to avoid circular import
from mainClasses.SGCell import SGCell
from mainClasses.SGTimePhase import *
from math import inf
import copy

#Class who manage the game mechanics of Update
class SGAbstractAction():
    IDincr=0
    instances = []
    def __init__(self,type,number,conditions=[],feedBacks=[],conditionsOfFeedBack=[],nameToDisplay=None,setControllerContextualMenu=False,setOnController=True):
        self.id=self.nextId()
        self.__class__.instances.append(self)
        # print('new gameAction: '+str(self.id)) # To test
        from mainClasses.SGModel import SGModel  # Import local pour éviter l'import circulaire
        if isinstance(type, SGModel):
            self.targetType='model'
            self.model=type
        else:
            self.targetType=type
            self.model=self.targetType.model 
        self.number = inf if number in ("infinite", None, inf) else number
        
        self.numberUsed=0
        self.conditions=copy.deepcopy(conditions) #Is is very important to use deepcopy becasue otherwise conditions are copied from one GameAction to another
                                                 # We should check that this does not ahppen as well for feedbacks and conditionsOfFeedback 
        self.feedbacks=copy.deepcopy(feedBacks)
        self.conditionsOfFeedBack=copy.deepcopy(conditionsOfFeedBack) 
        self.setControllerContextualMenu=setControllerContextualMenu
        self.setOnController=copy.deepcopy(setOnController)        
        
        #Define variables to handle the history 
        self.history={}
        self.history["performed"]=[]    

    def nextId(self):
        SGAbstractAction.IDincr +=1
        return SGAbstractAction.IDincr   
    
    #Function which increment the number of use
    def incNbUsed(self):
        self.numberUsed += 1


    def perform_with(self,aTargetEntity,serverUpdate=True): #The arg aParameterHolder has been removed has it is never used and it complicates the updateServer
        # print(f"action {self.name} is performed")
        if self.checkAuthorization(aTargetEntity):
            resAction = self.executeAction(aTargetEntity)
            if self.feedbacks:
                aFeedbackTarget = self.chooseFeedbackTargetAmong([aTargetEntity,resAction]) # Previously Three choices aTargetEntity,aParameterHolder,resAction
                if self.checkFeedbackAuhorization(aFeedbackTarget):
                    resFeedback = self.executeFeedbacks(aFeedbackTarget)
            else : resFeedback = None
            self.incNbUsed()
            self.savePerformedActionInHistory(aTargetEntity, resAction, resFeedback)

            if serverUpdate: self.updateServer_gameAction_performed(aTargetEntity)

            if not self.model.timeManager.isInitialization():
                self.model.timeManager.getCurrentPhase().handleAutoForward()

            #commented because unsued -  return resAction if not self.feedbacks else [resAction,resFeedback]
        # else:
        #     return False

    #Function to test if the game action can be used

    def canBeUsed(self):
        if self.model.timeManager.numberOfPhases()==0:
            return True
        if self.model.timeManager.isInitialization():
            # During initialization, only Admin can use actions
            # Check if currentPlayer is defined before accessing it
            try:
                currentPlayer = self.model.getCurrentPlayer()
                return currentPlayer.isAdmin
            except ValueError:
                # Current player not defined yet, only Admin actions should work
                # This is a temporary state during initialization
                return False
        if isinstance(self.model.timeManager.phases[self.model.phaseNumber()-1],SGModelPhase):#If this is a ModelPhase, as default players can't do actions
            # TODO add a facultative permission 
            return False
        if isinstance(self.model.timeManager.phases[self.model.phaseNumber()-1],SGPlayPhase):#If this is a PlayPhase, as default players can do actions
            player=self.model.getCurrentPlayer()
            if player in self.model.timeManager.phases[self.model.phaseNumber()-1].authorizedPlayers:
                res = True
            else:
                return False
            # TODO add a facultative restriction 
        if self.numberUsed >= self.number:
            return False
        return True
    
    def checkAuthorization(self,aTargetEntity):
        if not self.canBeUsed():
            return False
        res = True
        for aCondition in self.conditions:
            res = res and (aCondition() if aCondition.__code__.co_argcount == 0 else aCondition(aTargetEntity))
        return res

    #Function to test if the action feedback 
    def checkFeedbackAuhorization(self,aFeedbackTarget):
        res = True 
        for aCondition in self.conditionsOfFeedBack:
            res = res and aCondition() if aCondition.__code__.co_argcount == 0 else aCondition(aFeedbackTarget)
        return res
    
    def chooseFeedbackTargetAmong(self,listOfPossibleFedbackTarget):
        return listOfPossibleFedbackTarget[0]


    def executeFeedbacks(self, feddbackTarget):
        listOfRes = []
        for aFeedback in self.feedbacks:
            res = aFeedback() if aFeedback.__code__.co_argcount == 0 else aFeedback(feddbackTarget)
            listOfRes.append(res)
        if not listOfRes: raise ValueError('why is this method called when the list of feedbaks is  empty')
        return res if len(listOfRes) == 1 else listOfRes
   
    def savePerformedActionInHistory(self,aTargetEntity, resAction, resFeedback):
        self.history["performed"].append([self.model.timeManager.currentRoundNumber,
                                          self.model.timeManager.currentPhaseNumber,
                                          self.numberUsed,
                                          aTargetEntity,
                                          resAction,
                                          resFeedback])


    def updateServer_gameAction_performed(self, *args):
        if self.model.mqttMajType == "Instantaneous":
            dict ={}
            dict['class_name']=self.__class__.__name__
            dict['id']=self.id
            dict['method']='perform_with'
            self.model.buildExeMsgAndPublishToBroker('gameAction_performed',dict, *args)
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
        
    def reset(self):
        self.numberUsed=0
    
    def addCondition(self,aCondition):
        self.conditions.append(aCondition)
    
    def addFeedback(self,aFeedback):
        self.feedbacks.append(aFeedback)
        
    def addConditionOfFeedBack(self,aCondition):
        self.conditionsOfFeedBack.append(aCondition)
        
    def getNbRemainingActions(self):
        return self.number-self.numberUsed
        # thePlayer.remainActions[self.name]=remainNumber
    
    def getGraphIdentifier(self):
        """Generate unique identifier for graphs, showing ID only when necessary"""
        if hasattr(self.targetType, 'name'):
            base_name = f"{self.targetType.name}_{self.nameToDisplay}"
        else:
            base_name = f"model_{self.nameToDisplay}"
        
        # Check if there are other actions with the same base name (static method to avoid recursion)
        if self._hasConflictingNames(base_name):
            return f"{base_name}_{self.id}"
        else:
            return base_name
    
    @classmethod
    def _hasConflictingNames(cls, base_name):
        """Static method to check for name conflicts without recursion"""
        count = 0
        for action in cls.instances:
            if hasattr(action, 'targetType') and hasattr(action, 'nameToDisplay'):
                if hasattr(action.targetType, 'name'):
                    action_base = f"{action.targetType.name}_{action.nameToDisplay}"
                else:
                    action_base = f"model_{action.nameToDisplay}"
                
                if action_base == base_name:
                    count += 1
                    if count > 1:  # More than one action with this name
                        return True
        return False
    

  
            
    

