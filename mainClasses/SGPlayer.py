from SGLegend import SGLegend
from SGAgent import SGAgent
from SGCell import SGCell

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
        thePov=self.getPov()
        actions=self.gameActions
        deleteButtons=[]
        for aAction in actions:
            if isinstance(aAction,SGDelete):
                deleteButtons.append(str(aAction.name))
        playerElements = {}  
        for grid_key, grid_value in elements.items():  
            playerElements[grid_key] = {'cells': {}, 'agents': {}}
            for cell_key, cell_value in grid_value['cells'].items():
                for aPov, aDict in thePov.items():
                    for testAtt, testVal in aDict.items():
                        if cell_key in goodKeys:
                            newDict={testAtt:testVal}
                            playerElements[grid_key]['cells'][aPov]=newDict
            for agent_key, agent_value in grid_value['agents'].items():
                if agent_key in goodKeys:
                    playerElements[grid_key]['agents'][agent_key] = agent_value
        playerElements["deleteButtons"]=deleteButtons
        aLegend = SGLegend(self.model,Name,playerElements,self.name,agents,showAgents,legendType="player")
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
            if isinstance(action.anObject,SGAgent) and not isinstance(action,SGMove) :#and not isinstance (action,SGDelete) #! cas des agents sans attributs
                attributs.append(action.anObject.name)
            if (isinstance(action.anObject,SGCell) or action.anObject == SGCell) and isinstance(action,SGUpdate): #! cas des cellules
                print(action.name)
                print(action.dictNewValues)
                key=''.join(list(action.dictNewValues.keys()))
                print(key)
                attributs.append(key)
        return attributs
    
    def getPov(self):
        thePov={}
        for action in self.gameActions:
            if (isinstance(action.anObject,SGCell) or action.anObject == SGCell) and isinstance(action,SGUpdate): #! cas des cellules
                aPov=self.model.getPovWithAttribut(list(action.dictNewValues.keys())[0])
                thePov[aPov]=action.dictNewValues
                if aPov is None:
                    aBorderPov=self.model.getBorderPovWithAttribut(list(action.dictNewValues.keys())[0])
                    thePov[aBorderPov]=action.dictNewValues
        return thePov
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
        return aGameAction
    
    def getGameActionOn(self,anItem):
        #On cell
        if isinstance(anItem,SGCell) or anItem==SGCell:
            for aGameAction in self.gameActions :
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
                    elif isinstance(aGameAction,SGDelete) and self.model.selected[1] not in ['square','hexagonal'] :
                        if aGameAction.dictAttValue is not None:
                            if self.model.selected[3]in list(aGameAction.dictAttValue.values())[0] and self.model.selected[4]in list(aGameAction.dictAttValue.keys()) : 
                                return aGameAction
                        else: 
                            if self.model.selected[2].split()[1] in list(self.model.agentSpecies.keys()): #Cas des agents sans POV
                                return aGameAction
                    
    def getMooveActionOn(self,anItem):
        if isinstance(anItem,SGAgent):
            for aGameAction in self.gameActions :
                if isinstance(aGameAction,SGMove):
                    # Move an Angent
                    if aGameAction.dictAttributs is not None:
                        for att in list(anItem.dictOfAttributs.keys()) :
                            if att in list(aGameAction.dictAttributs.keys()) : 
                                if(anItem.dictOfAttributs[att] in list(aGameAction.dictAttributs.values())[0]):
                                    return aGameAction
                    else:
                        if anItem.species in list(self.model.agentSpecies.keys()):
                            return aGameAction
