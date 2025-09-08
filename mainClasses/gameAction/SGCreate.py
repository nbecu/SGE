from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction
from PyQt5.QtWidgets import QInputDialog




#Class who manage the game mechanics of creation
class SGCreate(SGAbstractAction):
    def __init__(self,entDef,dictAttributs,number,conditions=[],feedBack=[],conditionOfFeedBack=[],nameToDisplay=None,setControllerContextualMenu=False , create_several_at_each_click = False, writeAttributeInLabel=False):
        super().__init__(entDef,number,conditions,feedBack,conditionOfFeedBack,nameToDisplay,setControllerContextualMenu)
        self.dictAttributs=dictAttributs
        if nameToDisplay is None:
            self.nameToDisplay="+"
            if self.dictAttributs is not None:
                textAttributes = ' ('
                for aAtt,aVal in self.dictAttributs.items():
                    if writeAttributeInLabel:
                        textAttributes = textAttributes + f'{aAtt}→{aVal},'
                    else:
                        textAttributes = textAttributes + f'{aVal},'
                textAttributes = textAttributes[:-1]+')'
                self.nameToDisplay += textAttributes
            else:
                self.nameToDisplay += " create"
        else:
            self.nameToDisplay=nameToDisplay
        self.actionType="Create"
        self.addCondition(lambda aTargetEntity: aTargetEntity.classDef.entityType() == 'Cell')
        self.create_several_at_each_click=create_several_at_each_click


    def executeAction(self, aTargetEntity):
        """Create a single entity """
        # in case of agent, we create the agent on the cell using Model-View architecture
        if self.targetEntDef.isAgentDef:
            result = self.targetEntDef.newAgentOnCell(aTargetEntity, self.dictAttributs)
            return result
        # in case of cell, we just revive the cell
        elif self.targetEntDef.isCellDef:
            # Check if this cell is in deletedCells (meaning it was deleted)
            if aTargetEntity in self.targetEntDef.deletedCells:
                self.targetEntDef.reviveThisCell(aTargetEntity)
            else:
                # Check if there's a deleted cell with the same ID
                deleted_cell = None
                for cell in self.targetEntDef.deletedCells:
                    if cell.id == aTargetEntity.id:
                        deleted_cell = cell
                        break
                
                if deleted_cell:
                    self.targetEntDef.reviveThisCell(deleted_cell)
            return aTargetEntity
        else:
            raise ValueError(f"Error in executeAction of SGCreate for {self.targetEntDef.entityName}")

    def perform_with(self, aTargetEntity, serverUpdate=True):
        """Override perform_with to handle multiple agent creation correctly for history tracking"""
        # If not creating multiple agents, use standard behavior
        if not self.create_several_at_each_click:
            return super().perform_with(aTargetEntity, serverUpdate)
        
        # Get number of agents to create
        nbOfAgents = self.numberOfAgentsToCreate()
        
        # Handle case where user cancels or no actions remaining
        if nbOfAgents is None:
            return False
        
        # Execute the action for each agent using standard behavior
        results = []
<<<<<<< HEAD
        for _ in range(nbOfAgents):
=======
        for i in range(nbOfAgents):
>>>>>>> refactor/model-view-separation
            result = super().perform_with(aTargetEntity, serverUpdate)
            if result:
                results.append(result)
        
        # Return the result(s) - single agent or list of agents
<<<<<<< HEAD
        return results[0] if len(results) == 1 else results if results else False
=======
        final_result = results[0] if len(results) == 1 else results if results else False
        return final_result
>>>>>>> refactor/model-view-separation


    def numberOfAgentsToCreate(self):
        max_agents = self.getNbRemainingActions()
        if max_agents <= 0:
            return None  # No actions remaining
        
        # Handle infinite actions case - no upper limit in dialog
        if max_agents == float('inf'):
            number, ok = QInputDialog.getInt(None, f"Create {self.targetEntDef.entityName}", 
                                            "Number to create:", 1, 1)
        else:
            # Finite actions - use the actual limit
            number, ok = QInputDialog.getInt(None, f"Create {self.targetEntDef.entityName}", 
                                            f"Number to create (max: {max_agents}):", 1, 1, max_agents)
        
        if ok:
            return number
        return None  # User cancelled

    def generateLegendItems(self,aControlPanel):
        if self.setControllerContextualMenu == False:
            if self.dictAttributs is None:
                aColor = self.targetEntDef.defaultShapeColor
                return [SGLegendItem(aControlPanel,'symbol',self.nameToDisplay,self.targetEntDef,aColor,gameAction=self)]
            else:
                aList = []
                for aAtt, aValue in self.dictAttributs.items():
                    aColor = self.targetEntDef.getColorOrColorandWidthOfFirstOccurenceOfAttAndValue(aAtt,aValue)
                    
                    #todo Modifs pour MTZC pour que ce soit plus simple
                    aList.append(SGLegendItem(aControlPanel,'symbol',self.nameToDisplay,self.targetEntDef,aColor,aAtt,aValue,gameAction=self))
                return aList


    

