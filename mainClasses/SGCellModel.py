from mainClasses.SGEntityModel import SGEntityModel

class SGCellModel(SGEntityModel):
    """
    Model class for SGCell - contains all data and business logic for cells
    Separated from the view to enable Model-View architecture
    """
    
    def __init__(self, classDef, x, y, defaultImage):
        """
        Initialize the cell model
        
        Args:
            classDef: The cell definition class
            x: X coordinate
            y: Y coordinate
            defaultImage: Default image for the cell
        """
        super().__init__(classDef, classDef.defaultsize, attributesAndValues=None)
        
        # Cell-specific properties
        self.grid = classDef.grid
        self.xCoord = x
        self.yCoord = y
        self.gap = self.grid.gap
        self.saveGap = self.gap
        self.saveSize = classDef.defaultsize
        self.startXBase = self.grid.startXBase
        self.startYBase = self.grid.startYBase
        self.defaultImage = defaultImage
        
        # List of agents in this cell
        self.agents = []
    
    def getId(self):
        """Get cell identifier"""
        return "cell" + str(self.xCoord) + "-" + str(self.yCoord)
    
    def updateIncomingAgent(self, agent):
        """Update when an agent enters this cell"""
        if agent not in self.agents:
            self.agents.append(agent)
    
    def removeAgent(self, agent):
        """Remove an agent from this cell"""
        if agent in self.agents:
            self.agents.remove(agent)
    
    def getAgents(self):
        """Get all agents in this cell"""
        return self.agents.copy()
    
    def getAgentCount(self):
        """Get the number of agents in this cell"""
        return len(self.agents)
    
    def hasAgent(self, agent):
        """Check if this cell contains a specific agent"""
        return agent in self.agents
