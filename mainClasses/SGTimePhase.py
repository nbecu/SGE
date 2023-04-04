
#Class who define a gaming phase
class SGTimePhase():
    def __init__(self,name,activePlayer=None,modelActions=[],conditionOfTrigger=[]):
        self.name=name
        self.activePlayer=activePlayer
        self.modelActions=modelActions
        self.conditionOfTrigger=conditionOfTrigger
        

        
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    def setActivePlayers(self,activePlayer):
        self.activePlayer=activePlayer
    
    def setNextStepAction(self,nextStepAction):
        self.nextStepAction=nextStepAction
        
    def setModelActions(self,anAction):
        self.modelActions.append(anAction)
        
    def setConditionOfTrigger(self,conditionOfTrigger):
        self.conditionOfTrigger=conditionOfTrigger
        
    def addConditionOfTrigger(self,aConditionOfTrigger):
            self.conditionOfTrigger.append(aConditionOfTrigger)
    
    
  
            
    

