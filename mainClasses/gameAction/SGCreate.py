from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction
from PyQt5.QtWidgets import QInputDialog




#Class who manage the game mechanics of creation
class SGCreate(SGAbstractAction):
    def __init__(self,type,dictAttributs,number,conditions=[],feedbacks=[],conditionsOfFeedback=[],nameToDisplay=None,setControllerContextualMenu=False , create_several_at_each_click = False, writeAttributeInLabel=False):
        super().__init__(type,number,conditions,feedbacks,conditionsOfFeedback,nameToDisplay,setControllerContextualMenu)
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
        self.addCondition(lambda aTargetEntity: aTargetEntity.type.category() == 'Cell')
        self.create_several_at_each_click=create_several_at_each_click


    def executeAction(self, aTargetEntity):
        """Create a single entity """
        # in case of agent, we create the agent on the cell using Model-View architecture
        if self.targetType.isAgentType:
            result = self.targetType.newAgentOnCell(aTargetEntity, self.dictAttributs)
            return result
        # in case of cell, we just revive the cell
        elif self.targetType.isCellType:
            # Check if this cell is in deletedCells (meaning it was deleted)
            if aTargetEntity in self.targetType.deletedCells:
                self.targetType.reviveThisCell(aTargetEntity)
            else:
                # Check if there's a deleted cell with the same ID
                deleted_cell = None
                for cell in self.targetType.deletedCells:
                    if cell.id == aTargetEntity.id:
                        deleted_cell = cell
                        break
                
                if deleted_cell:
                    self.targetType.reviveThisCell(deleted_cell)
            return aTargetEntity
        else:
            raise ValueError(f"Error in executeAction of SGCreate for {self.targetType.name}")

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
        for _ in range(nbOfAgents):
            result = super().perform_with(aTargetEntity, serverUpdate)
            if result:
                results.append(result)
        
        # Return the result(s) - single agent or list of agents
        return results[0] if len(results) == 1 else results if results else False


    def numberOfAgentsToCreate(self):
        max_agents = self.getNbRemainingActions()
        if max_agents <= 0:
            return None  # No actions remaining
        
        # Handle infinite actions case - no upper limit in dialog
        if max_agents == float('inf'):
            number, ok = QInputDialog.getInt(None, f"Create {self.targetType.name}", 
                                            "Number to create:", 1, 1)
        else:
            # Finite actions - use the actual limit
            number, ok = QInputDialog.getInt(None, f"Create {self.targetType.name}", 
                                            f"Number to create (max: {max_agents}):", 1, 1, max_agents)
        
        if ok:
            return number
        return None  # User cancelled

    def generateLegendItems(self,aControlPanel):
        if self.setControllerContextualMenu == False:
            if self.dictAttributs is None:
                aColor = self.targetType.defaultShapeColor
                return [SGLegendItem(aControlPanel,'symbol',self.nameToDisplay,self.targetType,aColor,gameAction=self)]
            else:
                aList = []
                for aAtt, aValue in self.dictAttributs.items():
                    aColor = self.targetType.getColorOrColorandWidthOfFirstOccurenceOfAttAndValue(aAtt,aValue)
                    
                    #todo Modifs pour MTZC pour que ce soit plus simple
                    aList.append(SGLegendItem(aControlPanel,'symbol',self.nameToDisplay,self.targetType,aColor,aAtt,aValue,gameAction=self))
                return aList
    
    # ============================================================================
    # EXPORT INTERFACE METHODS - SGCreate specific implementations
    # ============================================================================
    
    def getActionDetails(self):
        """
        Specific details for SGCreate
        """
        details = super().getActionDetails()
        details["attributes_to_set"] = self.dictAttributs
        details["create_several"] = getattr(self, 'create_several_at_each_click', False)
        return details
    
    def _getSpecificActionInfo(self):
        """
        Get specific creation information
        """
        if self.dictAttributs:
            attr_str = ", ".join([f"{k}={v}" for k, v in self.dictAttributs.items()])
            return f"Create: {attr_str}"
        else:
            return "Create: default attributes"

