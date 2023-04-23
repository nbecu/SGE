from email import feedparser
from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell

# TO BE CONTINUED
# #Class who manage a action to be executed by the model.
# It can handle more than one action, as well as a trigger condition, feedback actions and condition for feedbacks 
class SGModelAction():
    def __init__(self,actions=[],condition=[],feedBacks=[],feedBacksCondition=[]):
        self.actions=actions
        self.condition=condition
        self.feedBacks=feedBacks
        self.feedBacksCondition=feedBacksCondition
        
    #Function to test if the game action could be use
    def isActionAuthorize(self):
        return self.condition()

    
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    def addRestrictions(self,aRestriction):
        self.restrictions.append(aRestriction)
    
    def addFeedback(self,aFeedback):
        self.feedback.append(aFeedback)
        
    def addConditionOfFeedBack(self,aCondition):
        self.conditionOfFeedBack.append(aCondition)
    
    

  
            
    

