from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGEntity import SGEntity
from mainClasses.SGCellView import SGCellView
from mainClasses.SGExtensions import *
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

    #Create agents on the cell
    def newAgentHere(self, aAgentSpecies,adictAttributes=None):
        """
        Create a new Agent in the associated species.

        Args:
            aAgentSpecies (instance) : the species of your agent
            adictAttributes to set the values

        Return:
            a new agent"""
        return aAgentSpecies.newAgentOnCell(self,adictAttributes)
		

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
        return f"cell{self.xCoord}-{self.yCoord}"
    
    def getCoords(self):
        """Get cell coordinates"""
        return (self.xCoord, self.yCoord)

    def getAgents(self, nameOfSpecie=None):
        """
        Get all agents in this cell.
        
        Args:
            nameOfSpecie (str or SGAgentDef, optional): The species name or SGAgentDef object.
                If None, returns all agents in the cell.
                
        Returns:
            list[SGAgent]: List of agents of the specified species, or all agents if nameOfSpecie is None
        """
        if nameOfSpecie is None:
            return self.agents[:]
        
        # Filter by species
        nameOfSpecie = normalize_species_name(nameOfSpecie)
        return [agent for agent in self.agents if agent.classDef.entityName == nameOfSpecie]

    def getFirstAgentOfSpecie(self, nameOfSpecie):
        """
        Get the first agent of a specific species in this cell.
        
        Args:
            nameOfSpecie (str or SGAgentDef): The species name or SGAgentDef object
            
        Returns:
            SGAgent or None: The first agent of the specified species, or None if not found
        """
        nameOfSpecie = normalize_species_name(nameOfSpecie)
        for agent in self.agents:
            if agent.classDef.entityName == nameOfSpecie:
                return agent
        return None

    def nbAgents(self, nameOfSpecie=None):
        """
        Get the number of agents in this cell.
        
        Args:
            nameOfSpecie (str or SGAgentDef, optional): The species name or SGAgentDef object.
                If None, returns total count of all agents.
                
        Returns:
            int: Number of agents of the specified species, or total count if nameOfSpecie is None
        """
        if nameOfSpecie is None:
            return len(self.agents)
        
        nameOfSpecie = normalize_species_name(nameOfSpecie)
        # Count by species
        return len(self.getAgents(nameOfSpecie))


    def getNeighborCells(self, condition=None, neighborhood=None):
        #todo this method could be delegate to grid (SGGrid). For example SGCellDef.getEntities_withColumn and SGCellDef.getEntities_withRow are delegated to it.
        """
        Get the neighboring cells of the current cell.

        Args:
            condition (lambda function, optional): a condition that cells must respect to be return by this method 
            neighborhood ("moore", "neumann", optional):
                Type of neighborhood to use.
                - "moore": Includes diagonals (8 neighbors for square grid, 6 for hexagonal grid).
                - "neumann": Only orthogonal neighbors (4 neighbors for square grid; 3 or 4 for hexagonal grid depending on orientation).
                Defaults to the grid's `neighborhood` attribute.

        Returns:
            list: A list of neighboring cells (may be fewer if `boundary_condition` is "closed" and the cell is on an edge, or if a condition is defined).

        Notes:
            - Boundary handling depends on `self.grid.boundary_condition`:
                * "open" : Toroidal wrap-around (grid edges connect).
                * "closed": Finite boundaries (no wrap-around).
            - Coordinates in this grid are 1-indexed.
            - For "neumann" neighborhood, only horizontal and vertical neighbors are considered.
        """
        if neighborhood is None:
            neighborhood = self.grid.neighborhood
        boundary_condition = self.grid.boundary_condition
        cellShape = self.grid.cellShape

        rows = self.grid.rows
        columns = self.grid.columns
        neighbors = []

        for i in range(self.xCoord - 1, self.xCoord + 2):
            for j in range(self.yCoord - 1, self.yCoord + 2):
                # Skip the cell itself
                if i == self.xCoord and j == self.yCoord:
                    continue

                # Handle boundary conditions
                if boundary_condition == "open":  # wrap-around (toroidal)
                    ii = ((i - 1) % columns) + 1  # keep 1-indexed wrap
                    jj = ((j - 1) % rows) + 1
                elif boundary_condition == "closed":  # no wrap-around
                    if i < 1 or i > columns or j < 1 or j > rows:
                        continue
                    ii, jj = i, j
                else:
                    raise ValueError(f"Invalid boundary condition: {boundary_condition}")

                # Determine neighbors according to neighborhood type and cell shape
                aCell = None
                if cellShape == "square":
                    if neighborhood == "moore":
                        aCell = self.classDef.getCell(ii, jj)
                    elif neighborhood == "neumann":
                        if (ii == self.xCoord or jj == self.yCoord) and not (ii == self.xCoord and jj == self.yCoord):
                            aCell = self.classDef.getCell(ii, jj)
                    else:
                        raise ValueError(f"Invalid neighborhood type: {neighborhood}")
                elif cellShape == "hexagonal":
                    if neighborhood == "moore":
                        # For hexagonal Moore: 6 neighbors (not 8 like square)
                        # Hexagonal neighbors are determined by the offset pattern
                        dx = ii - self.xCoord
                        dy = jj - self.yCoord
                        # Hexagonal Moore neighbors: 6 directions (not 8)
                        # Pattern: (-1,-1), (-1,0), (0,-1), (0,1), (1,0), (1,1) for even rows
                        # Pattern: (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0) for odd rows
                        if self.yCoord % 2 == 0:  # Even row
                            valid_neighbors = [(-1,-1), (-1,0), (0,-1), (0,1), (1,0), (1,1)]
                        else:  # Odd row
                            valid_neighbors = [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)]
                        
                        if (dx, dy) in valid_neighbors:
                            aCell = self.classDef.getCell(ii, jj)
                    elif neighborhood == "neumann":
                        # For hexagonal Neumann: 3 neighbors (orthogonal only)
                        dx = ii - self.xCoord
                        dy = jj - self.yCoord
                        # Hexagonal Neumann: only orthogonal neighbors
                        if self.yCoord % 2 == 0:  # Even row
                            valid_neighbors = [(-1,0), (0,-1), (0,1)]
                        else:  # Odd row
                            valid_neighbors = [(-1,0), (0,-1), (0,1)]
                        
                        if (dx, dy) in valid_neighbors:
                            aCell = self.classDef.getCell(ii, jj)
                    else:
                        raise ValueError(f"Invalid neighborhood type: {neighborhood}")
                else:
                    raise ValueError(f"Invalid cell shape: {cellShape}")

                if aCell is not None:
                    neighbors.append(aCell)

        if condition is None:
            return neighbors
        else:
            return [aCell for aCell in neighbors if condition(aCell)]

    def getNeighborN(self):
        #todo this method could be delegate to grid (SGGrid). For example SGCellDef.getEntities_withRow delegates to it.
        """Get neighbor to the North"""
        return self.classDef.getCell(self.xCoord, self.yCoord - 1) if self.yCoord > 1 else None

    def getNeighborS(self):
        #todo this method could be delegate to grid (SGGrid). For example SGCellDef.getEntities_withRow delegates to it.
        """Get neighbor to the South"""
        return self.classDef.getCell(self.xCoord, self.yCoord + 1) if self.yCoord < self.classDef.grid.rows else None

    def getNeighborE(self):
        #todo this method could be delegate to grid (SGGrid). For example SGCellDef.getEntities_withColumn delegates to it.
        """Get neighbor to the East"""
        return self.classDef.getCell(self.xCoord + 1, self.yCoord) if self.xCoord < self.classDef.grid.columns else None

    def getNeighborW(self):
        #todo this method could be delegate to grid (SGGrid). For example SGCellDef.getEntities_withColumn delegates to it.
        """Get neighbor to the West"""
        return self.classDef.getCell(self.xCoord - 1, self.yCoord) if self.xCoord > 1 else None

    def getNeighborCells_inRadius(self, max_distance=1, conditions=None, neighborhood=None):
        #todo this method could be delegate to grid (SGGrid). For example SGCellDef.getEntities_withRow delegates to it.
        """
        Get all neighbor cells within a given radius according to the grid's neighborhood type.

        Args:
            max_distance (int, optional): 
                Maximum distance (radius) from the current cell to search for neighbors. Defaults to 1.
            conditions (list[callable] | None, optional): 
                A list of lambda functions, each taking a Cell as argument and returning True 
                if the cell should be included. All conditions must be satisfied. 
                If None or empty, all valid neighbors are returned.
            neighborhood ("moore", "neumann", optional):
                Type of neighborhood to use.
                - "moore": Includes diagonals (8 neighbors for square grid, 6 for hexagonal grid).
                - "neumann": Only orthogonal neighbors (4 neighbors for square grid; 3 or 4 for hexagonal grid depending on orientation).
                Defaults to the grid's `neighborhood` attribute.

        Returns:
            list[SGCell]: List of matching neighbor cells (excluding self).
        """
        grid = self.grid
        if neighborhood is None:
            neighborhood = grid.neighborhood  # "moore" or "neumann"
        boundary_condition = grid.boundary_condition

        if conditions is None:
            conditions = []
        elif not isinstance(conditions, (list, tuple)):
            conditions = [conditions]  # Allow a single callable to be passed

        results = []
        for dx in range(-max_distance, max_distance + 1):
            for dy in range(-max_distance, max_distance + 1):
                # Skip self
                if dx == 0 and dy == 0:
                    continue

                # Apply neighborhood rules
                if neighborhood == "neumann" and abs(dx) + abs(dy) > max_distance:
                    continue  # Neumann: only orthogonal moves allowed within radius

                if neighborhood == "moore" and max(abs(dx), abs(dy)) > max_distance:
                    continue  # Moore: Chebyshev distance rule

                nx = self.xCoord + dx
                ny = self.yCoord + dy

                # Handle closed boundaries
                if boundary_condition == "closed":
                    if nx < 1 or nx > grid.columns or ny < 1 or ny > grid.rows:
                        continue

                # Handle open boundaries (wrap-around)
                if boundary_condition == "open":
                    nx = ((nx - 1) % grid.columns) + 1
                    ny = ((ny - 1) % grid.rows) + 1

                neighbor = self.classDef.getCell(nx, ny)
                if neighbor is not None:
                    if all(cond(neighbor) for cond in conditions):
                        results.append(neighbor)

        return results



    def distanceTo(self, otherCell):
        #todo this method could be delegate to grid (SGGrid). For example SGCellDef.getEntities_withRow delegates to it.
        """
        Compute Euclidean distance to another cell.

        Args:
            otherCell (SGCell): The target cell.

        Returns:
            float: Euclidean distance between the two cells.
        """
        dx = self.xCoord - otherCell.xCoord
        dy = self.yCoord - otherCell.yCoord
        return (dx * dx + dy * dy) ** 0.5


    def getClosestNeighborMatching(self, max_distance=1, conditions=None, neighborhood=None):
        """
        Get the closest cell within a given radius that matches all given conditions.

        Args:
            max_distance (int, optional): 
                Maximum distance (radius) from the current cell to search for neighbors. Defaults to 1.
            conditions (list[callable] | callable | None, optional): 
                A list of lambda functions (or a single lambda) that each take a Cell as argument 
                and return True if the cell should be considered valid.
                All conditions must be satisfied.
            neighborhood ("moore", "neumann", optional):
                Type of neighborhood to use.
                Defaults to the grid's `neighborhood` attribute.

        Returns:
            SGCell | None: The closest matching cell, or None if no match found.
        """
        # Normalize conditions to always be a list
        if conditions is None:
            conditions = []
        elif not isinstance(conditions, (list, tuple)):
            conditions = [conditions]

        # Get all matching cells within the specified radius
        matching_cells = self.getNeighborCells_inRadius(
            max_distance=max_distance,
            conditions=conditions,
            neighborhood=neighborhood
        )

        if not matching_cells:
            return None

        # Return the cell with the smallest distance to self
        return min(matching_cells, key=lambda cell: self.distanceTo(cell))


    def getClosestAgentMatching(self, agentSpecie, max_distance=1, conditions_on_agent=None, conditions_on_cell=None, return_all=False):
        """
        Find the closest neighboring cell within a given radius that contains at least one agent 
        of a given species and meets optional conditions on both the agent and the cell.

        Args:
            agentSpecie (str | SGAgentDef): 
                The species of the agent to search for.
            max_distance (int, optional): 
                Maximum search radius. Defaults to 1.
            conditions_on_agent (list[callable], optional): 
                A list of lambda functions that each take an agent as argument and return True if valid.
                All conditions must be satisfied for the agent to be valid.
            conditions_on_cell (list[callable], optional): 
                A list of lambda functions that each take a cell as argument and return True if valid.
                All conditions must be satisfied for the cell to be valid.
            return_all (bool, optional):
                If True, returns all matching agents on the closest cell. 
                If False (default), returns one random matching agent.

        Returns:
            SGAgent | list[SGAgent] | None:
                - If return_all=False → a single agent (randomly chosen) that matches the conditions.
                - If return_all=True → a list of matching agents.
                - None if no match found.
        """
        # Step 1: Get neighbor cells that match cell conditions
        matching_cells = self.getNeighborCells_inRadius(
            max_distance=max_distance,
            conditions=conditions_on_cell
        )

        # Step 2: Keep only cells that have agents of the given species
        matching_cells = [cell for cell in matching_cells if cell.hasAgents(agentSpecie)]

        # Step 3: If there are agent conditions, filter cells that have at least one matching agent
        if conditions_on_agent:
            def agent_satisfies_conditions(agent):
                return all(cond(agent) for cond in conditions_on_agent)
            matching_cells = [
                cell for cell in matching_cells 
                if any(agent_satisfies_conditions(agent) for agent in cell.getAgents(agentSpecie))
            ]

        # Step 4: If no cells remain, return None
        if not matching_cells:
            return None

        # Step 5: Find the closest cell by distance
        closest_cell = min(matching_cells, key=lambda cell: self.distanceTo(cell))

        # Step 6: Return agent(s) on the closest cell
        matching_agents = closest_cell.getAgents(agentSpecie)
        if conditions_on_agent:
            matching_agents = [agent for agent in matching_agents if all(cond(agent) for cond in conditions_on_agent)]

        if not matching_agents:
            return None

        if return_all:
            return matching_agents
        else:
            return random.choice(matching_agents)
			
			
			
			
    # ============================================================================
    # IS/HAS METHODS
    # ============================================================================

    def hasAgent(self, agent):
        """Check if this cell contains a specific agent"""
        return agent in self.agents
    
    def hasAgents(self, nameOfSpecie=None):
        """
        Check if this cell contains agents of a specific species.
        
        Args:
            nameOfSpecie (str or SGAgentDef, optional): The species name or SGAgentDef object.
                If None, checks if cell contains any agents.
                
        Returns:
            bool: True if the cell contains agents of the specified species, False otherwise
        """
        nameOfSpecie = normalize_species_name(nameOfSpecie)
        return self.nbAgents(nameOfSpecie) > 0

    def isEmpty(self, nameOfSpecie=None):
        """
        Check if this cell is empty of agents of a specific species.
        
        Args:
            nameOfSpecie (str or SGAgentDef, optional): The species name or SGAgentDef object.
                If None, checks if cell is completely empty.
                
        Returns:
            bool: True if the cell is empty of the specified species, False otherwise
        """
        nameOfSpecie = normalize_species_name(nameOfSpecie)
        return not self.hasAgents(nameOfSpecie)

    


    # ============================================================================
    # DO/DISPLAY METHODS
    # ============================================================================

    # (No specific DO/DISPLAY methods in SGCell - inherited from SGEntity)

    # ============================================================================
    # OTHER MODELER METHODS
    # ============================================================================

    # (No specific OTHER MODELER methods in SGCell - inherited from SGEntity)