

class SGTimePhase():
    def __init__(self,name,orderNumber,activePlayer=None,nextStepAction=[],conditionOfTrigger=[]):
        self.name=name
        self.orderNumber=orderNumber
        self.activePlayer=activePlayer
        self.nextStepAction=nextStepAction
        self.conditionOfTrigger=conditionOfTrigger
        

        
    
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    def setActivePlayers(self,activePlayer):
        self.activePlayer=activePlayer
        

        
    def setNextStepAction(self,nextStepAction):
        self.nextStepAction=nextStepAction
        
    def addNextStepAction(self,anAction):
        self.nextStepAction.append(anAction)
        
    def setConditionOfTrigger(self,conditionOfTrigger):
        self.conditionOfTrigger=conditionOfTrigger
        
    def addConditionOfTrigger(self,aConditionOfTrigger):
            self.conditionOfTrigger.append(aConditionOfTrigger)
    
    
  
            
    

