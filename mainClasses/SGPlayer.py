from SGLegende import SGLegende
from SGAgent import SGAgent
from SGCell import SGCell

class SGPlayer():
    def __init__(self,theModel,name,actions=[]):
        self.parent=theModel
        self.name=name
        self.actions=actions
        self.gameActions=[]
        
        self.initLegende()
        
    def initLegende(self):
        self.legende=self.parent.createLegendeForPlayer(self.name+" Legende",{})
            
    
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
    
    def addGameAction(self,aGameAction):
        if isinstance(aGameAction.anObject,SGCell):
            theParent=aGameAction.anObject.parent.id
            aDict={theParent:aGameAction.anObject.theCollection.povs}
        
            self.legende.addToTheLegende(aDict)
            self.gameActions.append(aGameAction)
        elif isinstance(aGameAction.anObject,SGAgent):
            self.legende.addAgentToTheLegend(aGameAction.anObject.name)
            self.gameActions.append(aGameAction)        

        
    
  
            
    

