from email import feedparser
from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell

# TO BE CONTINUED
# #Class who manage a action to be executed by the model.
# It can handle more than one action, as well as a trigger condition, feedback actions and condition for feedbacks 
class SGModelAction():
    def __init__(self,actions=[],conditions=[],feedbacks=[],feedbacksCondition=[]):
        self.actions=[]
        self.conditions=[]
        self.feedbacks=[]
        self.feedbacksCondition=[]
        if isinstance(actions, list):
            self.actions=actions
        elif callable(actions): 
            self.actions= [actions]
        else:
            raise ValueError("Syntax error of actions")
        if isinstance(conditions, list):
            self.conditions=conditions
        elif callable(conditions): 
            self.conditions= [conditions]
        # if len(conditions) !=0:
        #     self.conditions = conditions # to be corrected
        #     breakpoint
        # self.testIfCallableAndPutInList(conditions)
        self.feedbacks=feedbacks
        self.feedbacksCondition=feedbacksCondition
        
        
    #Function to test if the game action could be use
    def getAuthorize(self,anObject):
        """NOT TESTED"""
        returnValue=True
        #We check each condition 
        for aCond in self.restrictions:
            returnValue=returnValue and aCond(anObject)
        if self.numberUsed+1>self.number:
            returnValue=False
        return returnValue

    def testIfCallableAndPutInList(self,anObject):
        if isinstance(anObject, list):
            aList=anObject
        elif callable(anObject): 
            aList = [anObject]
        else:
            raise ValueError("Syntax error of actions")
        return aList

    def testConditions(self):
        res = True 
        for aCondition in self.conditions:
            res = res and aCondition()
        return res
    
    def execute(self):
        if self.testConditions():
            allActionsDone = True
            for aAction in self.actions:
                if callable(aAction):
                    test = aAction()  #this command executes aAction
                    if test == False:
                        allActionsDone = False
                else:
                    raise ValueError("Syntax error of actions")
            if allActionsDone:
                for aFeedbackAction in self.feedbacks:
                    aFeedbackAction.execute()
                
 
            
            
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    def addCondition(self,aCondition):
        if callable(aCondition):
            self.conditions = self.conditions + [aCondition]
        else:
            breakpoint
        return self

    def addFeedback(self,aFeedback):
        if isinstance(aFeedback,SGModelAction):
            self.feedbacks = self.feedbacks + [aFeedback]
        elif callable(aFeedback):
            self.feedbacks = self.feedbacks + [ self.model.newModelAction(aFeedback)]
        else:
            raise ValueError("Syntax error of feedback")
        
    # def addConditionOfFeedBack(self,aCondition):
    #     self.conditionOfFeedBack.append(aCondition)
        
    def setRandomCells(self, att, value,nb):
        self.actions = self.actions + [lambda : self.model.grid.setRandomCells(att, value,nb)]
        return self

  
            
    

