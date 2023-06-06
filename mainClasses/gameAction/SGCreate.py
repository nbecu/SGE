from email import feedparser
from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell

#Class who manage the game mechanics of creation
class SGCreate():
    def __init__(self,anObject,number,dictAttributs,restrictions=[],feedBack=[],conditionOfFeedBack=[]):
        self.anObject=anObject
        self.number=number
        self.numberUsed=0
        self.dictAttributs=dictAttributs
        self.name="CreateAction "+str(anObject.name)
        self.restrictions=restrictions
        self.feedback=feedBack
        self.conditionOfFeedBack=conditionOfFeedBack

        
    #Function which increment the number of use
    def use(self):
        self.numberUsed= self.numberUsed+1
        
    #Function to test if the game action could be use
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
        
    def reset(self):
        self.numberUsed=0

    def addRestrictions(self,aRestriction):
        self.restrictions.append(aRestriction)
    
    def addFeedback(self,aFeedback):
        self.feedback.append(aFeedback)
        
    def addConditionOfFeedBack(self,aCondition):
        self.conditionOfFeedBack.append(aCondition)

    def getnumberUsed(self):
        return self.numberUsed
    
    def getRemainActionNumber(self,thePlayer):
        remainNumber=self.number-self.numberUsed
        thePlayer.remainActions[self.name]=remainNumber
        
    

  
            
    

