from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGEntity import SGEntity
from mainClasses.SGCellView import SGCellView
from mainClasses.SGExtensions import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mainClasses.SGAgent import SGAgent
    from mainClasses.SGStack import SGStack
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
    
    def __init__(self, type, x, y, defaultImage):
        # Initialize the model part
        super().__init__(type, type.defaultsize, attributesAndValues=None)
        
        # Cell-specific properties
        self.grid = type.grid
        self.xCoord = x
        self.yCoord = y
        self.gap = self.grid.gap
        self.saveGap = self.gap
        self.saveSize = type.defaultsize
        self.startXBase = self.grid.startXBase
        self.startYBase = self.grid.startYBase
        self.defaultImage = defaultImage
        
        # List of agents in this cell
        self.agents = []
        
        # List of tiles on this cell (organized by position)
        self.tiles = []  # List of all tiles on this cell
        
        # Initialize attributes from type
        self.initAttributesAndValuesWith({})
        
        # View will be created and linked by the factory (SGEntityFactory.newCellWithModelView)
        # Don't create view here to avoid duplication
        # The factory will call setView() to link the view
        
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
    
    # ============================================================================
    # TILE MANAGEMENT METHODS
    # ============================================================================
    
    def addTile(self, tile):
        """Add a tile to this cell"""
        if tile not in self.tiles:
            self.tiles.append(tile)
            # Update tile positions when cell moves
            if hasattr(self, 'view') and self.view:
                if hasattr(tile, 'view') and tile.view:
                    tile.view.updatePositionFromCell()
                # Update positions of all tiles in the same stack (for offset mode)
                # Only update if tile has all required attributes (might be in initialization)
                if (hasattr(tile, 'type') and hasattr(tile.type, 'stackRenderMode') and 
                    hasattr(tile, 'position') and hasattr(tile, 'layer')):
                    stack = self.getStack(tile.type)
                    for stack_tile in stack.tiles:
                        if hasattr(stack_tile, 'view') and stack_tile.view:
                            stack_tile.view.updatePositionFromCell()
    
    def removeTile(self, tile):
        """Remove a tile from this cell"""
        if tile in self.tiles:
            self.tiles.remove(tile)
            # Update positions of remaining tiles in the same stack (for offset mode)
            # Only update if tile has position attribute (might be in initialization)
            if hasattr(tile, 'type') and hasattr(tile.type, 'stackRenderMode') and hasattr(tile, 'position'):
                stack = self.getStack(tile.type)
                for stack_tile in stack.tiles:
                    if hasattr(stack_tile, 'view') and stack_tile.view:
                        stack_tile.view.updatePositionFromCell()


    def shouldAcceptDropFrom(self, entity):
        """
        Check if this cell should accept drops from the given entity
        
        Args:
            entity: The entity attempting to be dropped
            
        Returns:
            bool: True if the drop should be accepted, False otherwise
        """
        # Accept agents and tiles
        has_isAgent = hasattr(entity, 'isAgent')
        is_agent = entity.isAgent if has_isAgent else False
        has_isTile = hasattr(entity, 'isTile')
        is_tile = entity.isTile if has_isTile else False
        return (has_isAgent and is_agent) or (has_isTile and is_tile)

    # ============================================================================
    # ZOOM METHODS
    # ============================================================================
    
    def zoomIn(self):
        """Zoom in the cell - legacy method for compatibility"""
        self.size = round(self.size + 10)
        self.updateView()
    
    def zoomOut(self):
        """Zoom out the cell - legacy method for compatibility"""
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

    def __MODELER_METHODS__NEW__(self):
        pass

    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================

    #Create agents on the cell
    def newAgentHere(self, agent_type,adictAttributes=None):
        """
        Create a new Agent from the associated agent type.

        Args:
            agent_type (instance) : the type of your agent
            adictAttributes (dict, optional): a dict of attributes to set the values

        Return:
            a new agent
            
        Example:
            # Create a sheep agent with default attributes
            sheep = cell.newAgentHere(sheepType)
            
            # Create a sheep agent with custom attributes
            sheep = cell.newAgentHere(sheepType, {"health": "good", "age": 2})"""
        return agent_type.newAgentOnCell(self,adictAttributes)
		

    def __MODELER_METHODS__DELETE__(self):
        pass

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

    def __MODELER_METHODS__GET__(self):
        pass

    # ============================================================================
    # GET/NB METHODS
    # ============================================================================

    def getId(self):
        """Get cell identifier using numeric ID consistent with cellIdFromCoords"""
        return self.xCoord + (self.grid.columns * (self.yCoord - 1))
    
    def getCoords(self):
        """Get cell coordinates"""
        return (self.xCoord, self.yCoord)

    def getAgents(self, type_name=None):
        """
        Get all agents in this cell.
        
        Args:
            type_name (str or SGAgentDef, optional): The name of the type or SGAgentDef object.
                If None, returns all agents in the cell.
                
        Returns:
            list[SGAgent]: List of agents of the specified type, or all agents if type_name is None
            
        Example:
            # Get all agents in the cell
            all_agents = cell.getAgents()
            
            # Get only sheep agents
            sheep_agents = cell.getAgents("Sheeps")
            
            # Get agents using agent type object
            sheep_agents = cell.getAgents(sheepType)
        """
        if type_name is None:
            return self.agents[:]
        
        # Filter by type
        typeName = normalize_type_name(type_name)
        return [agent for agent in self.agents if agent.type.name == typeName]

    def getOldestAgent(self, type_name=None):
        """
        Get the oldest agent in this cell (agent with the smallest id).
        
        Args:
            type_name (str or SGAgentDef, optional): The name of the type or SGAgentDef object.
                If None, searches among all agents in the cell.
                
        Returns:
            SGAgent or None: The oldest agent (smallest id) of the specified type, 
            or None if no agent is found
            
        Example:
            # Get oldest agent among all agents
            oldest = cell.getOldestAgent()
            
            # Get oldest agent of a specific type
            oldest_sheep = cell.getOldestAgent("Sheeps")
        """
        if not self.agents:
            return None
        
        if type_name is None:
            # Return agent with smallest id among all agents
            return min(self.agents, key=lambda agent: agent.id)
        
        # Filter by type
        typeName = normalize_type_name(type_name)
        agents_of_type = [agent for agent in self.agents if agent.type.name == typeName]
        
        if not agents_of_type:
            return None
        
        return min(agents_of_type, key=lambda agent: agent.id)

    def getYoungestAgent(self, type_name=None):
        """
        Get the youngest agent in this cell (agent with the largest id).
        
        Args:
            type_name (str or SGAgentDef, optional): The name of the type or SGAgentDef object.
                If None, searches among all agents in the cell.
                
        Returns:
            SGAgent or None: The youngest agent (largest id) of the specified type, 
            or None if no agent is found
            
        Example:
            # Get youngest agent among all agents
            youngest = cell.getYoungestAgent()
            
            # Get youngest agent of a specific type
            youngest_sheep = cell.getYoungestAgent("Sheeps")
        """
        if not self.agents:
            return None
        
        if type_name is None:
            # Return agent with largest id among all agents
            return max(self.agents, key=lambda agent: agent.id)
        
        # Filter by type
        typeName = normalize_type_name(type_name)
        agents_of_type = [agent for agent in self.agents if agent.type.name == typeName]
        
        if not agents_of_type:
            return None
        
        return max(agents_of_type, key=lambda agent: agent.id)

    def getFirstAgent(self, type_name=None):
        """
        Get the first agent in this cell.
        
        Args:
            type_name (str or SGAgentDef, optional): The agent type name or SGAgentDef object.
                If None, returns the first agent in the cell (regardless of type).
                
        Returns:
            SGAgent or None: The first agent of the specified type (or first agent if type_name is None), 
            or None if no agent is found
            
        Example:
            # Get first agent among all agents
            first = cell.getFirstAgent()
            
            # Get first agent of a specific type
            first_sheep = cell.getFirstAgent("Sheeps")
        """
        if type_name is None:
            # Return first agent in the cell (or None if empty)
            return self.agents[0] if self.agents else None
        
        # Filter by type
        typeName = normalize_type_name(type_name)
        for agent in self.agents:
            if agent.type.name == typeName:
                return agent
        return None
    
    
    def getRandomAgent(self, type_name=None):
        """
        Get a random agent from this cell.
        
        Args:
            type_name (str or SGAgentDef, optional): The agent type name or SGAgentDef object.
                If None, returns a random agent from all agents in the cell.
                
        Returns:
            SGAgent or None: A random agent of the specified type (or random agent if type_name is None), 
            or None if no agent is found
            
        Example:
            # Get random agent among all agents
            random_agent = cell.getRandomAgent()
            
            # Get random agent of a specific type
            random_sheep = cell.getRandomAgent("Sheeps")
        """
        import random
        
        if type_name is None:
            # Return random agent from all agents
            return random.choice(self.agents) if self.agents else None
        
        # Filter by type
        typeName = normalize_type_name(type_name)
        agents_of_type = [agent for agent in self.agents if agent.type.name == typeName]
        
        if not agents_of_type:
            return None
        
        return random.choice(agents_of_type)


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
            
        Example:
            # Get all neighboring cells
            neighbors = cell.getNeighborCells()
            
            # Get only forest cells
            forest_neighbors = cell.getNeighborCells(condition=lambda c: c.getValue("terrain") == "forest")
            
            # Get neighbors using Moore neighborhood
            moore_neighbors = cell.getNeighborCells(neighborhood="moore")
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
                        aCell = self.type.getCell(ii, jj)
                    elif neighborhood == "neumann":
                        if (ii == self.xCoord or jj == self.yCoord) and not (ii == self.xCoord and jj == self.yCoord):
                            aCell = self.type.getCell(ii, jj)
                    else:
                        raise ValueError(f"Invalid neighborhood type: {neighborhood}")
                elif cellShape == "hexagonal":
                    #NOTE: The hexagonal grid is "Pointy-top hex grid with even-r offset".
                    if neighborhood == "moore":
                        # For hexagonal Moore: 6 neighbors (not 8 like square)
                        # First determine the hexagonal neighbor pattern
                        if self.yCoord % 2 == 0:  # Even row
                            valid_neighbors = [(-1,0), (0,-1), (1,-1), (1,0), (1,1), (0,1)]
                            # (-1,0) - left
                            # (0,-1) - top-left
                            # (1,-1) - top-right
                            # (1,0) - right
                            # (1,1) - bottom-right
                            # (0,1) - bottom-left

                        else:  # Odd row
                            valid_neighbors = [(-1,0), (-1,-1), (0,-1), (1,0), (0,1), (-1,1)]
                            # (-1,0) - left
                            # (-1,-1) - top-left
                            # (0,-1) - top-right
                            # (1,0) - right
                            # (0,1) - bottom-left
                            # (-1,1) - bottom-right

                        # Check if this is a valid hexagonal neighbor
                        dx = i - self.xCoord
                        dy = j - self.yCoord
                        
                        if (dx, dy) in valid_neighbors:
                            # Apply boundary conditions
                            if boundary_condition == "open":
                                # Simple toroidal wrap-around for hexagonal grids
                                ii = ((i - 1) % columns) + 1
                                jj = ((j - 1) % rows) + 1
                                aCell = self.type.getCell(ii, jj)
                            else:  # closed boundaries
                                if i < 1 or i > columns or j < 1 or j > rows:
                                    continue
                                aCell = self.type.getCell(i, j)
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
                            aCell = self.type.getCell(ii, jj)
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

    def getCellsInRow(self, condition=None):
        """
        Get all cells in the same row as the current cell.
        
        Args:
            condition (callable, optional): A function that takes a cell and returns True 
                if the cell should be included. If None, all cells in the row are returned.
        
        Returns:
            list[SGCell]: List of cells in the same row (including self), optionally filtered by condition.
        
        Examples:
            # Get all cells in the same row
            row_cells = cell.getCellsInRow()
            
            # Get only cells with tiles in the same row
            row_cells_with_tiles = cell.getCellsInRow(condition=lambda c: c.hasTile())
        """
        return self.type.getEntities_withRow(self.yCoord, condition=condition)

    def getCellsInColumn(self, condition=None):
        """
        Get all cells in the same column as the current cell.
        
        Args:
            condition (callable, optional): A function that takes a cell and returns True 
                if the cell should be included. If None, all cells in the column are returned.
        
        Returns:
            list[SGCell]: List of cells in the same column (including self), optionally filtered by condition.
        
        Examples:
            # Get all cells in the same column
            column_cells = cell.getCellsInColumn()
            
            # Get only cells with tiles in the same column
            column_cells_with_tiles = cell.getCellsInColumn(condition=lambda c: c.hasTile())
        """
        return self.type.getEntities_withColumn(self.xCoord, condition=condition)

    def getNeighborN(self):
        #todo this method could be delegate to grid (SGGrid). For example SGCellDef.getEntities_withRow delegates to it.
        """Get neighbor to the North"""
        return self.type.getCell(self.xCoord, self.yCoord - 1) if self.yCoord > 1 else None

    def getNeighborS(self):
        #todo this method could be delegate to grid (SGGrid). For example SGCellDef.getEntities_withRow delegates to it.
        """Get neighbor to the South"""
        return self.type.getCell(self.xCoord, self.yCoord + 1) if self.yCoord < self.type.grid.rows else None

    def getNeighborE(self):
        #todo this method could be delegate to grid (SGGrid). For example SGCellDef.getEntities_withColumn delegates to it.
        """Get neighbor to the East"""
        return self.type.getCell(self.xCoord + 1, self.yCoord) if self.xCoord < self.type.grid.columns else None

    def getNeighborW(self):
        #todo this method could be delegate to grid (SGGrid). For example SGCellDef.getEntities_withColumn delegates to it.
        """Get neighbor to the West"""
        return self.type.getCell(self.xCoord - 1, self.yCoord) if self.xCoord > 1 else None

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

                neighbor = self.type.getCell(nx, ny)
                if neighbor is not None:
                    if all(cond(neighbor) for cond in conditions):
                        results.append(neighbor)

        return results

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


    def getClosestAgentMatching(self, agent_type, max_distance=1, conditions_on_agent=None, conditions_on_cell=None, return_all=False):
        """
        Find the closest neighboring cell within a given radius that contains at least one agent 
        of a given type and meets optional conditions on both the agent and the cell.

        Args:
            agent_type (str | SGAgentDef): 
                The type of the agent to search for.
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

        # Step 2: Keep only cells that have agents of the given type
        matching_cells = [cell for cell in matching_cells if cell.hasAgents(agent_type)]

        # Step 3: If there are agent conditions, filter cells that have at least one matching agent
        if conditions_on_agent:
            matching_cells = [
                cell for cell in matching_cells 
                if any(all(cond(agent) for cond in conditions_on_agent) for agent in cell.getAgents(agent_type))
            ]

        # Step 4: If no cells remain, return None
        if not matching_cells:
            return None

        # Step 5: Find the closest cell by distance
        closest_cell = min(matching_cells, key=lambda cell: self.distanceTo(cell))

        # Step 6: Return agent(s) on the closest cell
        matching_agents = closest_cell.getAgents(agent_type)
        if conditions_on_agent:
            matching_agents = [agent for agent in matching_agents if all(cond(agent) for cond in conditions_on_agent)]

        if not matching_agents:
            return None

        if return_all:
            return matching_agents
        else:
            return random.choice(matching_agents)
			
			
    def getTilesHere(self):
        """Get all tiles on this cell"""
        return self.tiles.copy()
    
    def getTiles(self, tileType=None):
        """
        Get all tiles on this cell, optionally filtered by type
        
        Args:
            tileType: Optional tile type to filter by
            
        Returns:
            list: List of tiles
        """
        if tileType is None:
            return self.tiles.copy()
        else:
            return [tile for tile in self.tiles if tile.type == tileType]
    
    def getTilesAtPosition(self, position, tileType=None):
        """
        Get all tiles at a specific position on this cell, optionally filtered by type
        
        Args:
            position: Position on the cell ("center", "topLeft", "topRight", "bottomLeft", "bottomRight", "full")
            tileType: Optional tile type to filter by
            
        Returns:
            list: List of tiles at the specified position
        """
        tiles_at_pos = [tile for tile in self.tiles if tile.position == position]
        
        if tileType is not None:
            tiles_at_pos = [tile for tile in tiles_at_pos if tile.type == tileType]
        
        return tiles_at_pos

    def getFirstTile(self, tileType=None):
        """
        Get the first tile in this cell.
        
        Args:
            tileType: Optional tile type to filter by
            
        Returns:
            SGTile or None: The first tile of the specified type (or first tile if tileType is None), 
            or None if no tile is found
            
        Example:
            # Get first tile among all tiles
            first = cell.getFirstTile()
            
            # Get first tile of a specific type
            first_card = cell.getFirstTile(CardType)
        """
        if tileType is None:
            # Return first tile in the cell (or None if empty)
            return self.tiles[0] if self.tiles else None
        
        # Filter by type
        for tile in self.tiles:
            if tile.type == tileType:
                return tile
        return None

    def getRandomTile(self, tileType):
        """
        Get a random tile of the given type from this cell
        
        Args:
            tileType: The tile type to get
            
        Returns:
            SGTile or None: A random tile of this type, or None if not found
        """
        import random
        tiles_of_type = [tile for tile in self.tiles if tile.type == tileType]
        if not tiles_of_type:
            return None
        return random.choice(tiles_of_type)
            

    def getStack(self, tileType):
        """
        Get the stack of tiles for a specific type
        
        The position is determined by the tileType's positionOnCell attribute.
        All tiles of the same type are always at the same position.
        
        Args:
            tileType: The tile type to identify the stack
            
        Returns:
            SGStack: A Stack object representing all tiles of this type
        """
        from mainClasses.SGStack import SGStack
        return SGStack(self, tileType)		
			

    def __MODELER_METHODS__IS__(self):
        pass

    # ============================================================================
    # IS/HAS METHODS
    # ============================================================================

    def hasAgent(self, agent: 'SGAgent') -> bool:
        """
        Check if this cell contains a specific agent
        
        Args:
            agent (SGAgent): The agent to check for
            
        Returns:
            bool: True if the agent is in this cell, False otherwise
        """
        return agent in self.agents
    
    def hasAgents(self, type_name=None):
        """
        Check if this cell contains agents of a specific type.
        
        Args:
            type_name (str or SGAgentDef, optional): The agent type name or SGAgentDef object.
                If None, checks if cell contains any agents.
                
        Returns:
            bool: True if the cell contains agents of the specified type, False otherwise
        """
        type_name = normalize_type_name(type_name)
        return self.nbAgents(type_name) > 0

    def hasTile(self, tileType=None, condition=None):
        """
        Check if this cell contains a tile matching the criteria
        
        Args:
            tileType: The tile type to check for. If None, checks if cell has any tile.
            condition: Optional callable function that takes a tile and returns True if it should be included.
                       The condition is applied in addition to the tileType check.
            
        Returns:
            bool: True if cell has a tile matching the criteria
            
        Example:
            # Check if cell has any tile
            cell.hasTile()
            
            # Check if cell has a tile of specific type
            cell.hasTile(SeaTile)
            
            # Check if cell has a tile matching a condition
            cell.hasTile(condition=lambda tile: tile.getValue("category") == "biodiv")
            
            # Check if cell has a tile of specific type matching a condition
            cell.hasTile(SeaTile, condition=lambda tile: tile.isFaceFront())
        """
        if tileType is None and condition is None:
            return len(self.tiles) > 0
        
        for tile in self.tiles:
            # Check tile type if specified
            if tileType is not None and tile.type != tileType:
                continue
            
            # Check condition if specified
            if condition is not None and not condition(tile):
                continue
            
            return True
        
        return False   
         
    def hasTiles(self, tileType=None):
        """
        Check if this cell contains tiles of a specific type.
        
        Args:
            tileType (str or SGTileType, optional): The tile type name or SGTileType object.
                If None, checks if cell contains any tiles.
                
        Returns:
            bool: True if the cell contains tiles of the specified type, False otherwise
        """
        return self.nbTiles(tileType) > 0

    def isEmpty(self, type_name=None):
        """
        Check if this cell is empty of agents and tiles of a specific type.
        
        Args:
            type_name (str, SGAgentDef, or SGTileType, optional): The agent type name, SGAgentDef object, or SGTileType object.
                If None, checks if cell is completely empty (no agents and no tiles).
                If provided, checks if cell is empty of both agents and tiles of that type.
                
        Returns:
            bool: True if the cell is empty of agents and tiles (of the specified type if provided), False otherwise
        """
        if type_name is None:
            # Check if completely empty (no agents and no tiles at all)
            return not self.hasAgents() and not self.hasTiles()
        else:
            # Check both agents and tiles of the specified type
            # Normalize for agents (handles SGAgentType and string names)
            normalized_agent_type = normalize_type_name(type_name)
            has_agents_of_type = self.hasAgents(normalized_agent_type)
            
            # For tiles, check if type_name matches any tile type
            # type_name could be an SGTileType object or a string name
            has_tiles_of_type = False
            if hasattr(type_name, 'isTileType') and type_name.isTileType:
                # It's an SGTileType object
                has_tiles_of_type = self.hasTiles(type_name)
            elif isinstance(type_name, str):
                # It's a string, check if any tile has this type name
                has_tiles_of_type = any(tile.type.name == type_name for tile in self.tiles)
            else:
                # Try to normalize and check by name (could be SGAgentType that we want to check as tile type name)
                normalized_name = normalize_type_name(type_name) if hasattr(type_name, 'name') else str(type_name)
                has_tiles_of_type = any(tile.type.name == normalized_name for tile in self.tiles)
            
            return not has_agents_of_type and not has_tiles_of_type


    def __MODELER_METHODS__DO_DISPLAY__(self):
        pass

    # ============================================================================
    # DO/DISPLAY METHODS
    # ============================================================================

    # (No specific DO/DISPLAY methods in SGCell - inherited from SGEntity)

    def __MODELER_METHODS__METRIC__(self):
        pass

    # ============================================================================
    # METRIC METHODS
    # ============================================================================

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

    def nbAgents(self, type_name=None):
        """
        Get the number of agents in this cell.
        
        Args:
            type_name (str or SGAgentDef, optional): The agent type name or SGAgentDef object.
                If None, returns total count of all agents.
                
        Returns:
            int: Number of agents of the specified type, or total count if type_name is None
        """
        if type_name is None:
            return len(self.agents)
        
        type_name = normalize_type_name(type_name)
        # Count by type
        return len(self.getAgents(type_name))


    def nbTiles(self, tileType=None):
        """
        Count tiles on this cell, optionally filtered by type
        
        Args:
            tileType: Optional tile type to filter by
            
        Returns:
            int: Number of tiles
        """
        if tileType is None:
            return len(self.tiles)
        else:
            return len([tile for tile in self.tiles if tile.type == tileType])
    			    

    def __MODELER_METHODS__OTHER__(self):
        pass

    # ============================================================================
    # OTHER MODELER METHODS
    # ============================================================================

    # (No specific OTHER MODELER methods in SGCell - inherited from SGEntity)