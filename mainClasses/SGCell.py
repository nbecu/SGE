from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGEntity import SGEntity
from mainClasses.SGCellView import SGCellView
# from mainClasses.gameAction.SGCreate import *  # Commented to avoid circular import
# from mainClasses.gameAction.SGDelete import *   # Commented to avoid circular import
# from mainClasses.gameAction.SGModify import *   # Commented to avoid circular import
# from mainClasses.gameAction.SGMove import *     # Commented to avoid circular import
# from mainClasses.gameAction.SGActivate import * # Commented to avoid circular import
import random
# from mainClasses.gameAction.SGMove import SGMove
   
#Class who is responsible of the declaration a cell
class SGCell(SGEntity):
    """
    SGCell - Cell model class for grid-based simulations
    
    This class now uses Model-View architecture:
    - Inherits from SGEntity for data and business logic
    - Delegates UI to SGCellView for display and interaction
    """
    
    def __init__(self, classDef, x, y, defaultImage):
        # Initialize the model part
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
        
        # Create and link the view
        self.view = SGCellView(self, classDef.grid)
        self.setView(self.view)
        
        # Type identification attributes
        self.isEntity = True
        self.isCell = True
        self.isAgent = False

    # ============================================================================
    # DEVELOPER METHODS
    # ============================================================================

    #todo obsolete function
    #  Special move() override for cells
    # def move(self, *args, **kwargs):
    #     """Move the cell view and update all agent positions"""
    #     super().move(*args, **kwargs)  # Call parent method
        
    #     # Update position of all agents in this cell
    #     for agent in self.agents:
    #         if hasattr(agent, 'view') and agent.view:
    #             agent.view.updatePositionFromCell()

    # Model-View specific methods
    def getView(self):
        """Get the cell view"""
        return self.view
    
    def setView(self, view):
        """Set the cell view"""
        self.view = view
        if view:
            view.cell_model = self
    
    def updateView(self):
        """Update the cell view"""
        if self.view:
            self.view.update()

    # Cell management methods
    def setDisplay(self, display):
        """Set display state and update view"""
        self.isDisplay = display
        if hasattr(self, 'view') and self.view:
            self.view.update()

    def updateIncomingAgent(self, agent):
        """Update when an agent enters this cell"""
        if agent not in self.agents:
            self.agents.append(agent)

    def removeAgent(self, agent):
        """Remove an agent from this cell"""
        if agent in self.agents:
            self.agents.remove(agent)

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
        return has_isAgent and is_agent

    # Zoom methods
    def zoomIn(self):
        """Zoom in the cell"""
        self.size = round(self.size + 10)
        self.updateView()
    
    def zoomOut(self):
        """Zoom out the cell"""
        self.size = round(self.size - 10)
        self.updateView()
    
    def zoomFit(self):
        """Zoom fit the cell"""
        self.size = self.saveSize
        self.updateView()

    # Coordinate conversion methods
    def convert_coordinates(self, global_pos):
        """Convert global coordinates to cell coordinates"""
        # Implementation depends on specific requirements
        return global_pos

    # Legacy compatibility methods that delegate to view
    def paintEvent(self, event):
        """Paint event - delegates to view"""
        self.view.paintEvent(event)
    
    def getRegion(self):
        """Get region - delegates to view"""
        return self.view.getRegion()
    
    def mousePressEvent(self, event):
        """Mouse press event - delegates to view"""
        self.view.mousePressEvent(event)

    def dropEvent(self, e):
        """Drop event - delegates to view"""
        self.view.dropEvent(e)

    # Model-View specific methods
    def getView(self):
        """Get the cell view"""
        return self.view
    
    def setView(self, view):
        """Set the cell view"""
        self.view = view
        if view:
            view.cell_model = self
    
    def updateView(self):
        """Update the cell view"""
        if self.view:
            self.view.update()

    # ============================================================================
    # MODELER METHODS
    # ============================================================================

    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================

    # (No specific NEW/ADD/SET methods in SGCell - inherited from SGEntity)

    # ============================================================================
    # DELETE METHODS
    # ============================================================================

    def deleteAllAgents(self):
        """Delete all agents in this cell"""
        # Remove all agents from the cell
        agents_to_remove = self.agents.copy()
        for agent in agents_to_remove:
            if hasattr(agent, 'view') and agent.view:
                agent.view.deleteLater()
            self.removeAgent(agent)

    # ============================================================================
    # GET/NB METHODS
    # ============================================================================

    def getId(self):
        """Get cell identifier"""
        return "cell" + str(self.xCoord) + "-" + str(self.yCoord)

    def getAgents(self, specie=None):
        """Get all agents in this cell"""
        if specie is None:
            return self.agents
        
        # Filter by species
        return [agent for agent in self.agents if agent.classDef.entityName == specie]

    def getFirstAgentOfSpecie(self, specie):
        """Get the first agent of a specific species in this cell"""
        for agent in self.agents:
            if agent.classDef.entityName == specie:
                return agent
        return None

    def nbAgents(self, specie=None):
        """Get number of agents in this cell"""
        if specie is None:
            return len(self.agents)
        
        # Count by species
        return len([agent for agent in self.agents if agent.classDef.entityName == specie])

    def getAgentCount(self):
        """Get the number of agents in this cell"""
        return len(self.agents)

    def getNeighborCells(self, condition=None):
        """
        Get all neighboring cells (8-directional: N, NE, E, SE, S, SW, W, NW)
        
        Args:
            condition (callable, optional): A lambda function that takes a Cell as argument 
                and returns True if the cell should be included in neighbors
                
        Returns:
            list: List of neighboring SGCell instances
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
            new_x = self.xCoord + dx
            new_y = self.yCoord + dy
            
            # Check if the new coordinates are within grid bounds
            if (1 <= new_x <= cell_def.grid.columns and 
                1 <= new_y <= cell_def.grid.rows):
                
                neighbor_cell = cell_def.getCell(new_x, new_y)
                
                # Only add valid cells (not None)
                if neighbor_cell is not None:
                    # Apply condition if provided
                    if condition is None or condition(neighbor_cell):
                        neighbors.append(neighbor_cell)
        
        return neighbors

    def getNeighborN(self):
        """Get neighbor to the North"""
        return self.classDef.getCell(self.xCoord, self.yCoord - 1) if self.yCoord > 1 else None

    def getNeighborS(self):
        """Get neighbor to the South"""
        return self.classDef.getCell(self.xCoord, self.yCoord + 1) if self.yCoord < self.classDef.grid.rows else None

    def getNeighborE(self):
        """Get neighbor to the East"""
        return self.classDef.getCell(self.xCoord + 1, self.yCoord) if self.xCoord < self.classDef.grid.columns else None

    def getNeighborW(self):
        """Get neighbor to the West"""
        return self.classDef.getCell(self.xCoord - 1, self.yCoord) if self.xCoord > 1 else None

    # ============================================================================
    # IS/HAS METHODS
    # ============================================================================

    def hasAgent(self, agent):
        """Check if this cell contains a specific agent"""
        return agent in self.agents

    def isEmpty(self, specie=None):
        """Check if this cell is empty"""
        if specie is None:
            return len(self.agents) == 0
        return len([agent for agent in self.agents if agent.classDef.entityName == specie]) == 0


    # ============================================================================
    # DO/DISPLAY METHODS
    # ============================================================================

    # (No specific DO/DISPLAY methods in SGCell - inherited from SGEntity)

    # ============================================================================
    # OTHER MODELER METHODS
    # ============================================================================

    # (No specific OTHER MODELER methods in SGCell - inherited from SGEntity)