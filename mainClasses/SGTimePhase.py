
#Class who define a gaming phase
class SGTimePhase():
    def __init__(self,name,activePlayer=None,modelActions=[]):
        self.name=name
        self.activePlayer=activePlayer
        self.modelActions=modelActions
        

        
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    def setActivePlayers(self,activePlayer):
        self.activePlayer=activePlayer
    
    def setNextStepAction(self,nextStepAction):
        self.nextStepAction=nextStepAction
        
    def setModelActions(self,anAction):
        self.modelActions.append(anAction)
    
    
  
            
    

