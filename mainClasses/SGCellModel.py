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
        
        # Initialize attributes from classDef
        self.initAttributesAndValuesWith({})
    
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

    def shouldAcceptDropFrom(self, entity):
        """
        Check if this cell should accept drops from the given entity
        
        Args:
            entity: The entity attempting to be dropped
            
        Returns:
            bool: True if the drop should be accepted, False otherwise
        """
        # Only accept agents, not all entities
        has_isAgent = hasattr(entity, 'isAgent')
        is_agent = entity.isAgent if has_isAgent else False
        print(f"DEBUG: Entity {entity.id} - has isAgent: {has_isAgent}, isAgent: {is_agent}")
        return has_isAgent and is_agent

    def getNeighborCells(self, condition=None):
        """
        Get all neighboring cells (8-directional: N, NE, E, SE, S, SW, W, NW)
        
        Args:
            condition (callable, optional): A lambda function that takes a Cell as argument 
                and returns True if the cell should be included in neighbors
                
        Returns:
            list: List of neighboring SGCellModel instances
        """
        neighbors = []
        
        # Get the cell definition to access the grid
        cell_def = self.classDef
        
        # Check all 8 directions
        directions = [
            (-1, -1), (-1, 0), (-1, 1),  # NW, N, NE
            (0, -1),           (0, 1),    # W,     E
            (1, -1),  (1, 0),  (1, 1)    # SW, S, SE
        ]
        
        for dx, dy in directions:
            neighbor_x = self.xCoord + dx
            neighbor_y = self.yCoord + dy
            
            # Check if the neighbor coordinates are within grid bounds
            if (1 <= neighbor_x <= cell_def.grid.columns and 
                1 <= neighbor_y <= cell_def.grid.rows):
                
                # Get the neighbor cell
                neighbor_cell = cell_def.getCell(neighbor_x, neighbor_y)
                if neighbor_cell is not None:
                    # Apply condition if provided
                    if condition is None or condition(neighbor_cell):
                        neighbors.append(neighbor_cell)
        
        return neighbors

    def getNeighborN(self):
        """Get neighbor cell to the North"""
        if self.yCoord > 1:
            return self.classDef.getCell(self.xCoord, self.yCoord - 1)
        return None
    
    def getNeighborS(self):
        """Get neighbor cell to the South"""
        if self.yCoord < self.classDef.grid.rows:
            return self.classDef.getCell(self.xCoord, self.yCoord + 1)
        return None
    
    def getNeighborE(self):
        """Get neighbor cell to the East"""
        if self.xCoord < self.classDef.grid.columns:
            return self.classDef.getCell(self.xCoord + 1, self.yCoord)
        return None
    
    def getNeighborW(self):
        """Get neighbor cell to the West"""
        if self.xCoord > 1:
            return self.classDef.getCell(self.xCoord - 1, self.yCoord)
        return None
