from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell

#Class who manage the game mechanics of mooving
class SGMove():
    def __init__(self,anObject,number,dictAttributs,restrictions=[],feedBack=[],conditionOfFeedBack=[],feedbackAgent=[],conditionOfFeedBackAgent=[]):
        self.anObject=anObject
        self.number=number
        self.numberUsed=0
        self.dictAttributs=dictAttributs
        self.restrictions=restrictions
        if isinstance(anObject,SGAgent):
            self.name="Move "+str(anObject.getId())
        elif isinstance(anObject,SGCell):
            self.name="Move "+str(anObject.name)
        self.feedback=feedBack
        self.conditionOfFeedBack=conditionOfFeedBack
        self.feedbackAgent=feedbackAgent
        self.conditionOfFeedBackAgent=conditionOfFeedBackAgent
            
        
    #Function which increment the number of use
    def use(self):
        self.numberUsed= self.numberUsed+1
        
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

    
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    def addRestrictions(self,aRestriction):
        self.restrictions.append(aRestriction)
    
    def addFeedback(self,aFeedback):
        self.feedback.append(aFeedback)
        
    def addConditionOfFeedBack(self,aCondition):
        self.conditionOfFeedBack.append(aCondition)
        
    def addFeedbackAgent(self,aFeedback):
        self.feedbackAgent.append(aFeedback)
        
    def addConditionOfFeedBackAgent(self,aCondition):
        self.conditionOfFeedBackAgent.append(aCondition)
        
    def reset(self):
        self.numberUsed=0