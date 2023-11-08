from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell
import copy

#Class who manage the game mechanics of delete
class SGDelete():
    def __init__(self,anObject,number,dictAttValue,aListOfrestrictions=[],feedBack=[],conditionOfFeedBack=[]):
        self.anObject=anObject
        self.number=number
        self.numberUsed=0
        self.dictAttValue=dictAttValue
        if anObject == SGCell:
            entName="Cell"
        else:
            entName=anObject.species
        self.name="Delete "+entName
        self.restrictions=copy.deepcopy(aListOfrestrictions)
        self.feedback=feedBack
        self.conditionOfFeedBack=conditionOfFeedBack
        self.addRestrictions(lambda selectedEntity: selectedEntity.species == entName)
        
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
        restrictionList=self.restrictions
        restrictionList.append(aRestriction)
        self.restrictions=restrictionList
    
    def addFeedback(self,aFeedback):
        self.feedback.append(aFeedback)
        
    def addConditionOfFeedBack(self,aCondition):
        self.conditionOfFeedBack.append(aCondition)
    
    def getRemainActionNumber(self,thePlayer):
        remainNumber=self.number-self.numberUsed
        thePlayer.remainActions[self.name]=remainNumber