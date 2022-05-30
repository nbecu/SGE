from SGLegende import SGLegende
from SGAgent import SGAgent
from SGCell import SGCell
from gameAction.SGDelete import SGDelete
from gameAction.SGUpdate import SGUpdate
from gameAction.SGCreate import SGCreate

import copy

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
    
    def addGameAction(self,aGameAction,aDictOfAcceptedValue={}):
        if isinstance(aGameAction.anObject,SGCell):
            theParent=aGameAction.anObject.parent.id
            aDict={theParent:aGameAction.anObject.theCollection.povs}
            self.legende.addToTheLegende(aDict,aGameAction.aDictOfAcceptedValue)
            self.gameActions.append(aGameAction)
        elif isinstance(aGameAction.anObject,SGAgent):
            self.legende.addAgentToTheLegend(aGameAction.anObject.name,aGameAction.aDictOfAcceptedValue)
            self.gameActions.append(aGameAction)   
        return aGameAction
    
    def getGameActionOn(self,anItem):
        #On cell
        if isinstance(anItem,SGCell):
            for aGameAction in self.gameActions :
                #Creation of Cell
                if isinstance(aGameAction,SGCreate) and (anItem.isDisplay==False) and self.parent.selected[3]in list(aGameAction.aDictOfAcceptedValue.values())[0] and self.parent.selected[4]in list(aGameAction.aDictOfAcceptedValue.keys()) : 
                    return aGameAction
                #Creation of an agent
                elif isinstance(aGameAction,SGCreate) and self.parent.selected[1] not in ['square','hexagonal'] and self.parent.selected[3]in list(aGameAction.aDictOfAcceptedValue.values())[0] and self.parent.selected[4]in list(aGameAction.aDictOfAcceptedValue.keys()) :
                    return aGameAction 
                #Update
                #Delete
                #Else
                
        elif isinstance(anItem,SGAgent):
            #Update
            #Delete
            #Else
            return None

                 

        
    
  
            
    

