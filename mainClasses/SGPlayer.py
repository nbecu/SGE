from SGLegende import SGLegende
from SGAgent import SGAgent
from SGCell import SGCell
from gameAction.SGDelete import SGDelete
from gameAction.SGUpdate import SGUpdate
from gameAction.SGCreate import SGCreate
from gameAction.SGMove import SGMove

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
    
    def addGameAction(self,aGameAction):
        if isinstance(aGameAction,SGDelete):
            self.legende.addDeleteButton("Remove",aGameAction.aDictOfAcceptedValue)
            self.gameActions.append(aGameAction)
        elif isinstance(aGameAction.anObject,SGCell):
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
                if not isinstance(aGameAction,SGMove):
                    #Creation of Cell
                    if isinstance(aGameAction,SGCreate) and (anItem.isDisplay==False) and self.parent.selected[3]in list(aGameAction.aDictOfAcceptedValue.values())[0] and self.parent.selected[4]in list(aGameAction.aDictOfAcceptedValue.keys()) : 
                        return aGameAction
                    #Creation of an agent
                    elif isinstance(aGameAction,SGCreate) and self.parent.selected[1] not in ['square','hexagonal'] and self.parent.selected[3]in list(aGameAction.aDictOfAcceptedValue.values())[0] and self.parent.selected[4]in list(aGameAction.aDictOfAcceptedValue.keys()) :
                        return aGameAction 
                    #Update of a Cell
                    elif isinstance(aGameAction,SGUpdate) and self.parent.selected[2].find("Remove ")==-1 and (anItem.isDisplay==True) and self.parent.selected[1] in ['square','hexagonal'] and self.parent.selected[3]in list(aGameAction.aDictOfAcceptedValue.values())[0] and self.parent.selected[4]in list(aGameAction.aDictOfAcceptedValue.keys()) : 
                        return aGameAction
                    #Delete of a Cell
                    elif isinstance(aGameAction,SGDelete) and (anItem.isDisplay==True) and self.parent.selected[1] in ['square','hexagonal'] and self.parent.selected[3]in list(anItem.attributs.values()) : 
                        return aGameAction
        elif isinstance(anItem,SGAgent):
            for aGameAction in self.gameActions :
                if not isinstance(aGameAction,SGMove):
                    #Update of an Angent
                    if isinstance(aGameAction,SGUpdate)and self.parent.selected[2].find("Remove ")==-1 and self.parent.selected[1] not in ['square','hexagonal'] and self.parent.selected[3]in list(aGameAction.aDictOfAcceptedValue.values())[0] and self.parent.selected[4]in list(aGameAction.aDictOfAcceptedValue.keys()) : 
                        return aGameAction
                    #Delete of an Agent
                    elif isinstance(aGameAction,SGDelete) and self.parent.selected[1] not in ['square','hexagonal'] and self.parent.selected[3]in list(aGameAction.aDictOfAcceptedValue.values())[0] and self.parent.selected[4]in list(aGameAction.aDictOfAcceptedValue.keys()) : 
                        return aGameAction
                    
    def getMooveActionOn(self,anItem):
        if isinstance(anItem,SGAgent):
            for aGameAction in self.gameActions :
                if isinstance(aGameAction,SGMove):
                    #Moove an Angent
                    for att in list(anItem.attributs.keys()) :
                        if att in list(aGameAction.aDictOfAcceptedValue.keys()) : 
                            if(anItem.attributs[att] in list(aGameAction.aDictOfAcceptedValue.values())[0]):
                                return aGameAction
