from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell
import copy

#Class who manage the game mechanics of Update
class SGAbstractAction():
    IDincr=0
    instances = []
    def __init__(self,entDef,number,conditions=[],feedBacks=[],conditionsOfFeedBack=[]):
        self.id=self.nextId()
        self.__class__.instances.append(self)
        print('new gameAction: '+str(self.id)) # To test
        self.targetEntDef=entDef
        self.model=self.targetEntDef.model 
        self.number=number
        self.numberUsed=0
        self.conditions=copy.deepcopy(conditions) #Is is very important to use deepcopy becasue otherwise conditions are copied from one GameAction to another
                                                 # We should check that this does not ahppen as well for feedbacks and conditionsOfFeedback 
        self.feedbacks=feedBacks
        self.conditionsOfFeedBack=conditionsOfFeedBack            

    def nextId(self):
        SGAbstractAction.IDincr +=1
        return SGAbstractAction.IDincr   
    
    #Function which increment the number of use
    def incNbUsed(self):
        self.numberUsed += 1


    def perform_with(self,aTargetEntity,serverUpdate=True): #The arg aParameterHolder has been removed has it is never used and it complicates the updateServer
        if self.checkAuhorization(aTargetEntity):
            resAction = self.executeAction(aTargetEntity)
            aFeedbackTarget = self.chooseFeedbackTargetAmong([aTargetEntity,resAction]) # Previously Three choices aTargetEntity,aParameterHolder,resAction
            if self.checkFeedbackAuhorization(aFeedbackTarget):
                resFeedback = self.executeFeedback(aFeedbackTarget)
            self.incNbUsed()
            if serverUpdate: self.updateServer_gameAction_performed(aTargetEntity)
            return resFeedback
        else:
            return False

    #Function to test if the game action could be use
    def checkAuhorization(self,aTargetEntity):
        if self.numberUsed >= self.number:
            return False
        res = True 
        for aCondition in self.conditions:
            res = res and (aCondition() if aCondition.__code__.co_argcount == 0 else aCondition(aTargetEntity))
        return res

    #Function to test if the game action could be use
    def checkFeedbackAuhorization(self,aFeedbackTarget):
        res = True 
        for aCondition in self.conditionsOfFeedBack:
            res = res and aCondition() if aCondition.__code__.co_argcount == 0 else aCondition(aFeedbackTarget)
        return res
    
    def chooseFeedbackTargetAmong(self,listOfPossibleFedbackTarget):
        return listOfPossibleFedbackTarget[0]


    def executeFeedback(self, feddbackTarget):
        if callable(feddbackTarget):
            return feddbackTarget()     
        else:
            return False    
    
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
        self.feedback.append(aFeedback)
        
    def addConditionOfFeedBack(self,aCondition):
        self.conditionOfFeedBack.append(aCondition)
        
    def getNbRemainingActions(self):
        return self.number-self.numberUsed
        # thePlayer.remainActions[self.name]=remainNumber
    

  
            
    

