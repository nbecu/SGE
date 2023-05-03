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
                    
    def newControlPanel(self,name=None):
        ControlPanel=SGControlPanel(self.model,self,name)
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
    

    def newLegendPlayer(self,Name,showAgents=False):
        """
        To create an Player Legend (only with the GameActions related elements)
        
        Args:
        Name (str): name of the Legend

        """
        #Creation
        #We harvest all the case value
        elements={}
        AgentPOVs=self.model.getAgentPOVs()
        for anElement in self.model.getGrids() :
            elements[anElement.id]={}
            elements[anElement.id]['cells']=anElement.getValuesForLegend()
            elements[anElement.id]['agents']={}
        for grid in elements:
            elements[grid]['agents'].update(AgentPOVs)
        agents=self.model.getAgents()
        goodKeys=self.getAttributs()
        actions=self.gameActions
        for aAction in actions:
            if isinstance(aAction.anObject,SGAgent):
                goodKeys.append(str(aAction.anObject))
        playerElements = {}  
        for grid_key, grid_value in elements.items():  
            playerElements[grid_key] = {}  
            for cell_key, cell_value in grid_value['cells'].items(): 
                if cell_key in goodKeys: 
                    playerElements[grid_key]['cells'] = {cell_key: cell_value}  
            for agent_key, agent_value in grid_value['agents'].items(): 
                if agent_key in goodKeys:  
                    playerElements[grid_key]['agents'] = {agent_key: agent_value} 
        aLegend = SGLegend(self.model,Name,playerElements,self.name,agents,showAgents)
        self.model.gameSpaces[Name]=aLegend
        #Realocation of the position thanks to the layout
        newPos=self.model.layoutOfModel.addGameSpace(aLegend)
        aLegend.setStartXBase(newPos[0])
        aLegend.setStartYBase(newPos[1])
        if(self.model.typeOfLayout=="vertical"):
            aLegend.move(aLegend.startXBase,aLegend.startYBase+20*self.model.layoutOfModel.getNumberOfAnElement(aLegend))
        elif(self.model.typeOfLayout=="horizontal"):
            aLegend.move(aLegend.startXBase+20*self.model.layoutOfModel.getNumberOfAnElement(aLegend),aLegend.startYBase)    
        else:
            pos=self.model.layoutOfModel.foundInLayout(aLegend)
            aLegend.move(aLegend.startXBase+20*pos[0],aLegend.startYBase+20*pos[1])
        self.model.applyPersonalLayout()
        return aLegend
    
    def getAttributs(self):
        attributs=[]
        for action in self.gameActions:
            if isinstance(action.anObject,SGAgent) and not isinstance(action,SGMove):
                attributs.append(action.anObject.name)
        return attributs
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
    
    def addGameAction(self,aGameAction):
        if isinstance(aGameAction,SGDelete):
            #self.ControlPanel.addDeleteButton("Remove",aGameAction.dictAttributs)
            self.gameActions.append(aGameAction)
        if isinstance(aGameAction,SGCreate):
            self.gameActions.append(aGameAction)
        if isinstance(aGameAction,SGUpdate):
            self.gameActions.append(aGameAction)
        if isinstance(aGameAction,SGMove):
            self.gameActions.append(aGameAction)
        """elif isinstance(aGameAction.anObject,SGCell):
            theGrid=aGameAction.anObject.grid.id
            aDict={theGrid:aGameAction.anObject.theCollection.povs}
            self.Legend.addToTheLegend(aDict,aGameAction.dictAttributs)
            self.gameActions.append(aGameAction)
        elif isinstance(aGameAction.anObject,SGAgent):
            self.Legend.addAgentToTheLegend(aGameAction.anObject.name,aGameAction.dictAttributs)
            self.gameActions.append(aGameAction)   """
        return aGameAction
    
    def getGameActionOn(self,anItem):
        """NOT TESTED"""
        #On cell
        if isinstance(anItem,SGCell):
            for aGameAction in self.gameActions :
                print(self.gameActions)
                print(aGameAction)
                if not isinstance(aGameAction,SGMove):
                    #Creation of Cell
                    if isinstance(aGameAction,SGCreate) and (anItem.isDisplay==False) and self.model.selected[3]in list(aGameAction.dictAttributs.values())[0] and self.model.selected[4]in list(aGameAction.dictAttributs.keys()) : 
                        return aGameAction
                    #Creation of an agent
                    elif isinstance(aGameAction,SGCreate) and self.model.selected[1] not in ['square','hexagonal']:
                        if aGameAction.dictAttributs is not None:
                            if self.model.selected[3]in list(aGameAction.dictAttributs.values())[0] and self.model.selected[4]in list(aGameAction.dictAttributs.keys()) :
                                return aGameAction
                        else: 
                            if self.model.selected[2] in list(self.model.agentSpecies.keys()):
                                return aGameAction
                    #Update of a Cell
                    elif isinstance(aGameAction,SGUpdate) and (anItem.isDisplay==True) and self.model.selected[1] in ['square','hexagonal'] and self.model.selected[3]in list(aGameAction.dictNewValues.values())[0] and self.model.selected[4]in list(aGameAction.dictNewValues.keys()) : 
                        return aGameAction
                    #Delete of a Cell
                    elif isinstance(aGameAction,SGDelete) and (anItem.isDisplay==True) and self.model.selected[1] in ['square','hexagonal'] and self.model.selected[3]in list(anItem.attributs.values()) : 
                        return aGameAction
        elif isinstance(anItem,SGAgent):
            for aGameAction in self.gameActions :
                if not isinstance(aGameAction,SGMove):
                    #Update of an Angent
                    if isinstance(aGameAction,SGUpdate)and self.model.selected[2].find("Remove ")==-1 and self.model.selected[1] not in ['square','hexagonal'] and self.model.selected[3]in list(aGameAction.dictAttributs.values())[0] and self.model.selected[4]in list(aGameAction.dictAttributs.keys()) : 
                        return aGameAction
                    #Delete of an Agent
                    elif isinstance(aGameAction,SGDelete) and self.model.selected[1] not in ['square','hexagonal'] and self.model.selected[3]in list(aGameAction.dictAttributs.values())[0] and self.model.selected[4]in list(aGameAction.dictAttributs.keys()) : 
                        return aGameAction
                    
    def getMooveActionOn(self,anItem):
        """NOT TESTED"""
        if isinstance(anItem,SGAgent):
            for aGameAction in self.gameActions :
                if isinstance(aGameAction,SGMove):
                    #Moove an Angent
                    for att in list(anItem.attributs.keys()) :
                        if att in list(aGameAction.dictAttributs.keys()) : 
                            if(anItem.attributs[att] in list(aGameAction.dictAttributs.values())[0]):
                                return aGameAction
