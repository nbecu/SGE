from email import feedparser
from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell


class SGCreate():
    def __init__(self,anObject,number,aDictOfAcceptedValue,restrictions=[],feedBack=[],conditionOfFeedBack=[]):
        self.anObject=anObject
        self.number=number
        self.numberUsed=0
        self.aDictOfAcceptedValue=aDictOfAcceptedValue
        self.restrictions=restrictions
        if isinstance(anObject,SGAgent):
            self.name=anObject.getId()
        elif isinstance(anObject,SGCell):
            self.name=anObject.parent
        self.feedback=feedBack
        self.conditionOfFeedBack=conditionOfFeedBack
            
        
    #Function which increment the number of use
    def use(self):
        self.numberUsed= self.numberUsed+1
        
    def getAuthorize(self,anObject):
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
        
    def reset(self):
        self.numberUsed=0
        
    

  
            
    

