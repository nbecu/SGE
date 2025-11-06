from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog, QMessageBox, QDialog, QLabel, QVBoxLayout, QToolTip
from PyQt5.QtGui import QCursor
import random
from mainClasses.SGEntity import SGEntity
from mainClasses.SGCell import SGCell
from mainClasses.SGAgentView import SGAgentView
from mainClasses.gameAction.SGCreate import *
from mainClasses.gameAction.SGDelete import *
from mainClasses.gameAction.SGModify import *
from mainClasses.gameAction.SGMove import *
from mainClasses.gameAction.SGActivate import *
   
#Class who is responsible of the declaration a Agent
class SGAgent(SGEntity):
    """
    SGAgent - Agent class for agent-based simulations
    
    This class now uses Model-View architecture:
    - Inherits from SGEntity for data and business logic
    - Delegates UI to SGAgentView for display and interaction
    """
    
    def __init__(self, cell, size, attributesAndValues, shapeColor, type, defaultImage, popupImage):
        """
        Initialize the agent
        
        Args:
            cell: The cell where the agent is located
            size: Size of the agent
            attributesAndValues: Initial attributes and values
            shapeColor: Shape color
            type: The agent definition class
            defaultImage: Default image for the agent
            popupImage: Popup image for the agent
        """
        super().__init__(type, size, attributesAndValues)
        
        # Type identification attributes
        self.isEntity = True
        self.isCell = False
        self.isAgent = True
        
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
        
        # Save reference size for zoom calculations (like SGCell)
        self.saveSize = size
        
        # Initialize position
        self.getPositionInEntity()
        
        # Initialize attributes
        self.initAttributesAndValuesWith(attributesAndValues)
        
        # View will be created and linked by the factory
        # Don't create view here to avoid duplication

    # ============================================================================
    # DEVELOPER METHODS
    # ============================================================================

    # Model-View specific methods
    def getView(self):
        """Get the agent view"""
        return self.view
    
    def setView(self, view):
        """Set the agent view"""
        self.view = view
        if view:
            view.agent_model = self
    
    def updateView(self):
        """Update the agent view"""
        if self.view:
            self.view.update()


    def getPrivateId(self):
        """Get private ID"""
        return self.privateID

    # Position calculation methods
    def getRandomX(self):        
        maxSize = self.cell.size
        # Use cell coordinates instead of pos()
        startX = self.cell.startXBase + (self.cell.xCoord - 1) * (self.cell.size + self.cell.gap) + self.cell.gap
        if self.type.shape in ["ellipseAgent2","rectAgent2"]: 
            x = random.randint(startX, startX + maxSize - round(self.size/2))
        else:
            x = random.randint(startX, startX + maxSize - self.size)
        return x
    
    def getRandomY(self): 
        maxSize = self.cell.size
        # Use cell coordinates instead of pos()
        startY = self.cell.startYBase + (self.cell.yCoord - 1) * (self.cell.size + self.cell.gap) + self.cell.gap
        if self.type.shape in ["ellipseAgent1","rectAgent1"]: 
            y = random.randint(startY, startY + maxSize - round(self.size/2))
        else:
            y = random.randint(startY, startY + maxSize - self.size)
        return y
    
    def getPositionInEntity(self):
        maxSize = self.cell.size
        # Use cell coordinates instead of pos()
        startX = self.cell.startXBase + (self.cell.xCoord - 1) * (self.cell.size + self.cell.gap) + self.cell.gap
        startY = self.cell.startYBase + (self.cell.yCoord - 1) * (self.cell.size + self.cell.gap) + self.cell.gap
        
        if self.type.locationInEntity == "random":
            self.xCoord = self.getRandomX()
            self.yCoord = self.getRandomY()
            return
        if self.type.locationInEntity == "topRight":
            self.xCoord = startX + maxSize - 10
            self.yCoord = startY + 5
            return
        if self.type.locationInEntity == "topLeft":
            self.xCoord = startX + 5
            self.yCoord = startY + 5
            return
        if self.type.locationInEntity == "bottomLeft":
            self.xCoord = startX + 5
            self.yCoord = startY + maxSize - 10
            return
        if self.type.locationInEntity == "bottomRight":
            self.xCoord = startX + maxSize - 10
            self.yCoord = startY + maxSize - 10
            return
        if self.type.locationInEntity == "center":
            self.xCoord = startX + int(maxSize/2) - int(self.size/2)
            self.yCoord = startY + int(maxSize/2) - int(self.size/2)
            return
        else:
            raise ValueError("Error in entry for locationInEntity")

    # ============================================================================
    # ZOOM METHODS
    # ============================================================================
    
    def updateZoom(self, zoom_factor):
        """
        Update agent zoom based on zoom factor (like SGCell)
        """
        # Calculate zoomed size from reference value
        self.size = round(self.saveSize * zoom_factor)
        self.updateView()
    
    def zoomIn(self, zoomFactor):
        """Zoom in the agent - legacy method for compatibility"""
        self.size = round(self.size + (zoomFactor * 10))
        self.updateView()
    
    def zoomOut(self, zoomFactor):
        """Zoom out the agent - legacy method for compatibility"""
        self.size = round(self.size - (zoomFactor * 10))
        self.updateView()

    # Feedback methods
    def feedback(self, theAction):
        """Apply feedback from a game mechanics action"""
        booleanForFeedback = True
        for anCondition in theAction.conditionOfFeedBack:
            booleanForFeedback = booleanForFeedback and anCondition(self)
        if booleanForFeedback:
            for aFeedback in theAction.feedback:
                aFeedback(self)

    def addPovinMenuBar(self, nameOfPov):
        """Add POV to menu bar"""
        if nameOfPov not in self.model.listOfPovsForMenu:
            self.model.listOfPovsForMenu.append(nameOfPov)
            anAction = QAction(" &" + nameOfPov, self)
            self.model.povMenu.addAction(anAction)
            anAction.triggered.connect(lambda: self.model.displayPov(nameOfPov))

    # ============================================================================
    # MODELER METHODS
    # ============================================================================

    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================

  

    # ============================================================================
    # DELETE METHODS
    # ============================================================================

    # (No delete methods specific to agents in this class)

    # ============================================================================
    # GET/NB METHODS
    # ============================================================================

    def getId(self):
        """Get agent ID"""
        return self.id
    
    def getCoords(self):
        """Get agent coordinates"""
        return self.cell.getCoords()
    
    
    def getCell(self):
        """Get the current cell of the agent"""
        return self.cell
    
    def getCellCoordinates(self):
        """Get the coordinates of the current cell"""
        if self.cell:
            return (self.cell.xCoord, self.cell.yCoord)
        return None
    
    def getAgentsHere(self, agent_type=None):
        """
        Get all agents in the same cell as this agent.

        Args:
            agent_type (str | None): If specified, only agents of this type are returned.

        Returns:
            list[SGAgent]: Agents in the same cell.
        """
        if self.cell is None:
            return []
        
        agents = self.cell.getAgents()
        if agent_type is None:
            return agents
        
        # Filter by type
        return [agent for agent in agents if agent.type.name == agent_type]

    def nbAgentsHere(self, agent_type=None):
        """
        Get the number of agents in the same cell as this agent.

        Args:
            agent_type (str | None): If specified, only agents of this type are counted.

        Returns:
            int: Number of matching agents in the same cell.
        """
        if self.cell is None:
            return 0
        return len(self.getAgentsHere(agent_type))

    def getNeighborCells(self, neighborhood=None):
        """Get neighbor cells"""
        return self.cell.getNeighborCells(condition=neighborhood)
    
    def getNeighborAgents(self, agent_type=None, neighborhood=None):
        """Get neighbor agents"""
        neighborAgents = []        
        neighborAgents = [aCell.agents for aCell in self.getNeighborCells(neighborhood=neighborhood)]
        
        if agent_type:
            return self.filterByType(agent_type, neighborAgents)
        return neighborAgents
    
    def getClosestAgentMatching(self, agent_type, max_distance=1, conditions_on_agent=None, conditions_on_cell=None, return_all=False):
        """
        Find the closest neighboring agent of a given type from this agent's position,
        with optional filtering conditions on the target agent and the target cell.

        This method is a wrapper for SGCell.getClosestAgentMatching().

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
        
        return self.cell.getClosestAgentMatching(
            agent_type=agent_type,
            max_distance=max_distance,
            conditions_on_agent=conditions_on_agent,
            conditions_on_cell=conditions_on_cell,
            return_all=return_all
        )

    def nbNeighborAgents(self, agent_type=None, neighborhood=None):  
        """Get number of neighbor agents"""
        return len(self.getNeighborAgents(agent_type, neighborhood))

    def getNeighborsN(self, agent_type=None):
        """Get neighbor agents to the North"""
        theCell = self.cell.getNeighborN()
        if agent_type:
            return self.filterByType(agent_type, theCell.agents)
        return theCell.agents
    
    def getNeighborsS(self, agent_type=None):
        """Get neighbor agents to the South"""
        theCell = self.cell.getNeighborS()
        if agent_type:
            return self.filterByType(agent_type, theCell.agents)
        return theCell.agents
    
    def getNeighborsE(self, agent_type=None):
        """Get neighbor agents to the East"""
        theCell = self.cell.getNeighborE()
        if agent_type:
            return self.filterByType(agent_type, theCell.agents)
        return theCell.agents
    
    def getNeighborsW(self, agent_type=None):
        """Get neighbor agents to the West"""
        theCell = self.cell.getNeighborW()
        if agent_type:
            return self.filterByType(agent_type, theCell.agents)
        return theCell.agents

    # ============================================================================
    # IS/HAS METHODS
    # ============================================================================

    def isInCell(self, cell):
        """Check if agent is in a specific cell"""
        return self.cell == cell

    def hasAgentsHere(self, specie=None):
        """
        Check if the cell containing this agent has at least one agent.

        Args:
            specie (str | None): If specified, check only for agents of this specie.

        Returns:
            bool: True if at least one matching agent is in the same cell, False otherwise.
        """
        if self.cell is None:
            return False
        return len(self.getAgentsHere(specie)) > 0

    # ============================================================================
    # DO/DISPLAY METHODS
    # ============================================================================

    # @CATEGORY: DO
    def moveTo(self, aDestinationCell):
        """
        Move this agent to a specific cell.
        
        This method handles both initial placement and subsequent movements.
        Use this method for initial agent placement or when moving to a specific cell.
        
        Args:
            aDestinationCell: The cell where the agent should move
            
        Returns:
            self: The agent (for chaining operations)
        """
        if self.cell is None:
            # First placement
            self.cell = aDestinationCell
            self.cell.updateIncomingAgent(self)
            self.getPositionInEntity()  # Update position
            if hasattr(self, 'view') and self.view is not None:
                # Force layout recalculation before positioning
                from PyQt5.QtWidgets import QApplication
                QApplication.processEvents()
                self.view.getPositionInEntity()  # Force view repositioning
                self.view.show()  # Ensure view is visible
                self.updateView()
            return self
        else:
            # Movement from one cell to another
            
            # Check if moving to a different grid
            old_grid = self.cell.type.grid if hasattr(self.cell, 'type') and hasattr(self.cell.type, 'grid') else None
            new_grid = aDestinationCell.type.grid if hasattr(aDestinationCell, 'type') and hasattr(aDestinationCell.type, 'grid') else None
            
            if old_grid != new_grid and hasattr(self, 'view') and self.view is not None:
                # Change the parent of the view to the new grid
                self.view.setParent(new_grid)
            
            # Remove from current cell
            self.cell.removeAgent(self)
            
            # Move to new cell
            self.cell = aDestinationCell
            self.cell.updateIncomingAgent(self)
            
            # Update position and view
            self.getPositionInEntity()
            if hasattr(self, 'view') and self.view is not None:
                # Force layout recalculation before positioning
                from PyQt5.QtWidgets import QApplication
                QApplication.processEvents()
                self.view.getPositionInEntity()  # Force view repositioning
                self.view.show()  # Ensure view is visible
                self.updateView()
            
            return self
    # @CATEGORY: DO
    def moveAgent(self, method='random', target=None, numberOfMovement=1, condition=None):
        """
        Move the agent using predefined movement patterns.
        
        Note: This method requires the agent to already be placed on a cell.
        For initial placement, use moveTo() instead.
        
        Args:
            method (str): Movement method
                - "random" (default)
                - "cell" (default when target is defined)
                    -used with target as numeric ID (int), coordinates (x, y) tuple
                - "direction" (default when target is defined)
                    -used with target as direction string ("up", "down", "left", "right")
            numberOfMovement (int): Number of movements in one action
            condition (callable, optional): Condition function for destination cell validation
            
        Returns:
            self: The agent (for chaining operations)
        """
        if method=='random' and target is not None:
            if isinstance(target, tuple) or isinstance(target, int): method="cell"
            elif target and target.lower() in ["up", "down", "left", "right"]: method="direction"
            else: raise ValueError("Invalid target type for moveAgent()")

        if numberOfMovement > 1: 
            # Repeat the movement numberOfMovement times with numberOfMovement=1 each time
            for i in range(numberOfMovement):
                self.moveAgent(method=method, target=target, numberOfMovement=1, condition=condition)
            return self

        aGrid = self.cell.grid

        if method == "random":
            neighbors = self.cell.getNeighborCells(condition=condition)
            newCell = random.choice(neighbors) if neighbors else None

        elif method == "cell" and target is not None:
            # target can be either a numeric ID or coordinates (x, y)
            if isinstance(target, tuple) and len(target) == 2:
                # target is coordinates (x, y)
                x, y = target
                newCell = self.cell.type.getCell(x, y)
            else:
                # target is a numeric ID
                newCell = aGrid.getCell_withId(target)
            
            if condition is not None and newCell is not None:
                if not condition(newCell):
                    newCell = None

        elif method == "direction" and target is not None:
            # target must be a direction string for direction movement
            if target and target.lower() in ["up", "down", "left", "right"]:
                direction_lower = target.lower()
                if direction_lower == "up":
                    newCell = self.cell.getNeighborN()
                elif direction_lower == "down":
                    newCell = self.cell.getNeighborS()
                elif direction_lower == "left":
                    newCell = self.cell.getNeighborE()
                elif direction_lower == "right":
                    newCell = self.cell.getNeighborW()
                else:
                    newCell = None
        else:
            newCell = None
                
        if condition is not None and newCell is not None:
            if not condition(newCell):
                newCell = None

        if newCell is None:
            pass
        else:
            theAgent = self.moveTo(newCell)
            
        return newCell


    # @CATEGORY: DO
    def moveRandomly(self, numberOfMovement=1, condition=None):
        """
        An agent moves randomly in his direct neighborhood.
        
        Args:
            numberOfMovement (int): number of movement in one action
            condition (lambda function, optional): a condition that the destination cell should respect for the agent to move
        """
        self.moveAgent(method="random", numberOfMovement=numberOfMovement, condition=condition)

    # @CATEGORY: DO
    def moveTowards(self, target, condition=None):
        """
        Move the agent one step towards a target cell or another agent.

        Args:
            target (Agent | Cell | tuple[int,int]): 
                - Another agent object
                - A cell object
                - A tuple (x, y) for target coordinates
            condition (callable, optional): A lambda function that takes a Cell as argument and returns True 
                if the agent can move there.
        """
        # Determine the target cell
        if hasattr(target, 'cell'):  # Target is an agent
            target_cell = target.cell
        elif hasattr(target, 'isCell') and target.isCell:  # Target is a Cell
            target_cell = target
        elif isinstance(target, tuple) and len(target) == 2:  # Coordinates (x, y)
            target_cell = self.cell.type.getCell(target[0], target[1])
        else:
            raise ValueError("Invalid target type for moveTowards()")

        # Get neighbors that satisfy the condition
        neighbors = self.cell.getNeighborCells(condition=condition)
        if not neighbors:
            return  # No possible move

        # Select the neighbor closest to the target cell
        def dist(c1, c2):
            dx = c1.xCoord - c2.xCoord
            dy = c1.yCoord - c2.yCoord
            return (dx*dx + dy*dy) ** 0.5  # Euclidean distance

        best_cell = min(neighbors, key=lambda n: dist(n, target_cell))
        self.moveTo(best_cell)

    # ============================================================================
    # OTHER MODELER METHODS
    # ============================================================================

    def filterByType(self, agent_type, agents): #todo est ce que cette méthode ne devrait pas plutôt etre dans SGExtensions.py ?
        """Filter agents by type"""
        filtered_agents = []
        if len(agents) != 0:
            for aAgent in agents:
                if isinstance(aAgent, list):
                    for agent in aAgent:
                        if agent.type == agent_type or agent.type.name == agent_type:
                            filtered_agents.append(agent)
                elif hasattr(aAgent, 'type'):  # Check if it's an agent
                    if aAgent.type == agent_type or aAgent.type.name == agent_type:
                        filtered_agents.append(aAgent)
        return filtered_agents
                

        

