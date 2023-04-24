from SGLegend import SGLegend
from SGAgent import SGAgent
from SGCell import SGCell
from SGControlPanel import SGControlPanel
from gameAction.SGDelete import SGDelete
from gameAction.SGUpdate import SGUpdate
from gameAction.SGCreate import SGCreate
from gameAction.SGMove import SGMove

import copy


#Class that handle the player
class SGPlayer():
    def __init__(self,theModel,name,actions=[]):
        self.model=theModel
        self.name=name
        self.actions=actions
        self.gameActions=[]
        
        
    def initControlPanel(self):
        self.ControlPanel=self.model.newPlayerControlPanel(self.name,{},self.name)
            
    def newControlPanel(self,name=None,actionsItems=[]):
        ControlPanel=SGControlPanel(self.model,self,name,actionsItems)
        self.model.ControlPanel=ControlPanel
        self.model.gameSpaces[name]=ControlPanel
        #Realocation of the position thanks to the layout
        newPos=self.model.layoutOfModel.addGameSpace(ControlPanel)
        ControlPanel.setStartXBase(newPos[0])
        ControlPanel.setStartYBase(newPos[1])
        if(self.model.typeOfLayout=="vertical"):
            ControlPanel.move(ControlPanel.startXBase,ControlPanel.startYBase+20*self.model.layoutOfModel.getNumberOfAnElement(ControlPanel))
        elif(self.model.typeOfLayout=="horizontal"):
            ControlPanel.move(ControlPanel.startXBase+20*self.model.layoutOfModel.getNumberOfAnElement(ControlPanel),ControlPanel.startYBase)    
        else:
            pos=self.model.layoutOfModel.foundInLayout(ControlPanel)
            ControlPanel.move(ControlPanel.startXBase+20*pos[0],ControlPanel.startYBase+20*pos[1])

        self.model.applyPersonalLayout()
        return ControlPanel
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
    
    def addGameAction(self,aGameAction):
        """NOT TESTED"""
        if isinstance(aGameAction,SGDelete):
            self.Legend.addDeleteButton("Remove",aGameAction.aDictOfAcceptedValue)
            self.gameActions.append(aGameAction)
        elif isinstance(aGameAction.anObject,SGCell):
            theParent=aGameAction.anObject.parent.id
            aDict={theParent:aGameAction.anObject.theCollection.povs}
            self.Legend.addToTheLegend(aDict,aGameAction.aDictOfAcceptedValue)
            self.gameActions.append(aGameAction)
        elif isinstance(aGameAction.anObject,SGAgent):
            self.Legend.addAgentToTheLegend(aGameAction.anObject.name,aGameAction.aDictOfAcceptedValue)
            self.gameActions.append(aGameAction)   
        return aGameAction
    
    def getGameActionOn(self,anItem):
        """NOT TESTED"""
        #On cell
        if isinstance(anItem,SGCell):
            for aGameAction in self.gameActions :
                if not isinstance(aGameAction,SGMove):
                    #Creation of Cell
                    if isinstance(aGameAction,SGCreate) and (anItem.isDisplay==False) and self.model.selected[3]in list(aGameAction.aDictOfAcceptedValue.values())[0] and self.model.selected[4]in list(aGameAction.aDictOfAcceptedValue.keys()) : 
                        return aGameAction
                    #Creation of an agent
                    elif isinstance(aGameAction,SGCreate) and self.model.selected[1] not in ['square','hexagonal'] and self.model.selected[3]in list(aGameAction.aDictOfAcceptedValue.values())[0] and self.model.selected[4]in list(aGameAction.aDictOfAcceptedValue.keys()) :
                        return aGameAction 
                    #Update of a Cell
                    elif isinstance(aGameAction,SGUpdate) and self.model.selected[2].find("Remove ")==-1 and (anItem.isDisplay==True) and self.model.selected[1] in ['square','hexagonal'] and self.model.selected[3]in list(aGameAction.aDictOfAcceptedValue.values())[0] and self.model.selected[4]in list(aGameAction.aDictOfAcceptedValue.keys()) : 
                        return aGameAction
                    #Delete of a Cell
                    elif isinstance(aGameAction,SGDelete) and (anItem.isDisplay==True) and self.model.selected[1] in ['square','hexagonal'] and self.model.selected[3]in list(anItem.attributs.values()) : 
                        return aGameAction
        elif isinstance(anItem,SGAgent):
            for aGameAction in self.gameActions :
                if not isinstance(aGameAction,SGMove):
                    #Update of an Angent
                    if isinstance(aGameAction,SGUpdate)and self.model.selected[2].find("Remove ")==-1 and self.model.selected[1] not in ['square','hexagonal'] and self.model.selected[3]in list(aGameAction.aDictOfAcceptedValue.values())[0] and self.model.selected[4]in list(aGameAction.aDictOfAcceptedValue.keys()) : 
                        return aGameAction
                    #Delete of an Agent
                    elif isinstance(aGameAction,SGDelete) and self.model.selected[1] not in ['square','hexagonal'] and self.model.selected[3]in list(aGameAction.aDictOfAcceptedValue.values())[0] and self.model.selected[4]in list(aGameAction.aDictOfAcceptedValue.keys()) : 
                        return aGameAction
                    
    def getMooveActionOn(self,anItem):
        """NOT TESTED"""
        if isinstance(anItem,SGAgent):
            for aGameAction in self.gameActions :
                if isinstance(aGameAction,SGMove):
                    #Moove an Angent
                    for att in list(anItem.attributs.keys()) :
                        if att in list(aGameAction.aDictOfAcceptedValue.keys()) : 
                            if(anItem.attributs[att] in list(aGameAction.aDictOfAcceptedValue.values())[0]):
                                return aGameAction
