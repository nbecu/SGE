from mainClasses.SGEntityModel import SGEntityModel

class SGAgentModel(SGEntityModel):
    """
    Model class for SGAgent - contains all data and business logic for agents
    Separated from the view to enable Model-View architecture
    """
    
    def __init__(self, cell, size, attributesAndValues, shapeColor, classDef, defaultImage, popupImage):
        """
        Initialize the agent model
        
        Args:
            cell: The cell where the agent is located
            size: Size of the agent
            attributesAndValues: Initial attributes and values
            shapeColor: Shape color
            classDef: The agent definition class
            defaultImage: Default image for the agent
            popupImage: Popup image for the agent
        """
        super().__init__(classDef, size, attributesAndValues)
        
        # Agent-specific properties
        self.cell = None
        if cell is not None:
            self.cell = cell
            self.cell.updateIncomingAgent(self)
        else: 
            raise ValueError('This case is not handled')
            
        self.defaultImage = defaultImage
        self.popupImage = popupImage
        self.last_selected_option = None
    
    def moveToCell(self, new_cell):
        """
        Move agent to a new cell
        
        Args:
            new_cell: The new cell to move to
        """
        if self.cell is not None:
            self.cell.removeAgent(self)
        
        self.cell = new_cell
        if new_cell is not None:
            new_cell.updateIncomingAgent(self)
    
    def getCell(self):
        """Get the current cell of the agent"""
        return self.cell
    
    def getCellCoordinates(self):
        """Get the coordinates of the current cell"""
        if self.cell:
            return (self.cell.xCoord, self.cell.yCoord)
        return None
    
    def isInCell(self, cell):
        """Check if agent is in a specific cell"""
        return self.cell == cell
    
    def getNeighborCells(self):
        """Get neighboring cells"""
        if self.cell:
            return self.cell.getNeighborCells()
        return []
    
    def getClosestAgentMatching(self, agentSpecie, maxDistance=None):
        """Get closest agent matching criteria"""
        if self.cell:
            return self.cell.getClosestAgentMatching(agentSpecie, maxDistance)
        return None
