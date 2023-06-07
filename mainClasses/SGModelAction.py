from email import feedparser
from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell

# TO BE CONTINUED
# #Class who manage a action to be executed by the model.
# It can handle more than one action, as well as a trigger condition, feedback actions and condition for feedbacks 
class SGModelAction():
    def __init__(self,actions=[],conditions=[],feedBacks=[],feedBacksCondition=[]):
        self.actions=[]
        self.conditions=[]
        self.feedBacks=[]
        self.feedBacksCondition=[]
        if isinstance(actions, list):
            self.actions=actions
        elif callable(actions): 
            self.actions= [actions]
        else:
            raise ValueError("Syntax error of actions")
        self.conditions=[]
        # if isinstance(conditions, list):
        #     self.conditions=conditions
        # elif callable(conditions): 
        #     self.conditions= [conditions]
        # if len(conditions) !=0:
        #     self.conditions = conditions # to be corrected
        #     breakpoint
        # self.testIfCallableAndPutInList(conditions)
        self.feedBacks=feedBacks
        self.feedBacksCondition=feedBacksCondition
        
        
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
            for aAction in self.actions:
                if callable(aAction):
                    aAction()  #this command executes aAction
            
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    def addCondition(self,aCondition):
        if callable(aCondition):
            self.conditions.append(aCondition)
        else:
            breakpoint
        return self

    def addFeedback(self,aFeedback):
        self.feedback.append(aFeedback)
        
    def addConditionOfFeedBack(self,aCondition):
        self.conditionOfFeedBack.append(aCondition)
        
    def setRandomCells(self, att, value,nb):
        self.actions.append((lambda : self.model.grid.setRandomCells(att, value,nb)))
        return self

  
            
    

