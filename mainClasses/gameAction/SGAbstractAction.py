from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell

#Class who manage the game mechanics of Update
class SGAbstractAction():
    def __init__(self,anObject,number,conditions=[],feedBacks=[],conditionsOfFeedBack=[]):
        self.anObject=anObject
        self.number=number
        self.numberUsed=0
        self.conditions=conditions
        self.feedbacks=feedBacks
        self.conditionsOfFeedBack=conditionsOfFeedBack            
        
    #Function which increment the number of use
    def incNbUsed(self):
        self.numberUsed += 1


    def perform_with(self,aTargetEntity,aParameterHolder):
        if self.checkAuhorization(aTargetEntity):
            resAction = self.executeAction(aTargetEntity)
            aFeedbackTarget = self.chooseFeedbackTargetAmong([aTargetEntity,aParameterHolder,resAction])
            if self.checkFeedbackAuhorization(aFeedbackTarget):
                resFeedback = self.executeFeedback(aFeedbackTarget)
            self.incNbUsed()
            return resFeedback
        else:
            return False


    #Function to test if the game action could be use
    def checkAuhorization(self,anObject):
        if self.numberUsed >= self.number:
            return False
        res = True 
        for aCondition in self.conditions:
            res = res and aCondition() if aCondition.__code__.co_argcount == 0 else aCondition(anObject)
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
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
        
    def reset(self):
        self.numberUsed=0
    
    def addConditions(self,aCondition):
        # self.Conditions.append(aCondition)
        ConditionList=self.Conditions
        ConditionList.append(aCondition)
        self.Conditions=ConditionList
    
    def addFeedback(self,aFeedback):
        self.feedback.append(aFeedback)
        
    def addConditionOfFeedBack(self,aCondition):
        self.conditionOfFeedBack.append(aCondition)
        
    def getNbRemainingActions(self):
        return self.number-self.numberUsed
        # thePlayer.remainActions[self.name]=remainNumber
    

  
            
    

