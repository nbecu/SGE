

class SGTimePhase():
    def __init__(self,name,orderNumber,activePlayers="all",nextStepAction=[],conditionOfTrigger=[]):
        self.name=name
        self.orderNumber=orderNumber
        self.activePlayers=activePlayers
        self.nextStepAction=nextStepAction
        self.conditionOfTrigger=conditionOfTrigger
        

        
    
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    def setActivePlayers(self,activePlayers):
        self.activePlayers=activePlayers
        

        
    def setNextStepAction(self,nextStepAction):
        self.nextStepAction=nextStepAction
        
    def addNextStepAction(self,nextStepAction):
        for anAction in nextStepAction:
            self.activePlayers.append(anAction)
        
    def setConditionOfTrigger(self,conditionOfTrigger):
        self.conditionOfTrigger=conditionOfTrigger
        
    def addConditionOfTrigger(self,conditionOfTrigger):
        for aCondition in conditionOfTrigger:
            self.activePlayers.append(aCondition)
    
    
  
            
    

