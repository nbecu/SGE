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
    
    def __init__(self, cell, size, attributesAndValues, shapeColor, classDef, defaultImage, popupImage):
        """
        Initialize the agent
        
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
        
        # Initialize position
        self.getPositionInEntity()
        
        # Initialize attributes
        self.initAttributesAndValuesWith(attributesAndValues)
        
        # View will be created and linked by the factory
        # Don't create view here to avoid duplication

    # ============================================================================
    # DEVELOPER METHODS
    # ============================================================================

    # Legacy UI method delegation
    def show(self):
        """Show the agent view"""
        if hasattr(self, 'view') and self.view:
            self.view.show()
    
    def hide(self):
        """Hide the agent view"""
        if hasattr(self, 'view') and self.view:
            self.view.hide()
    
    def update(self):
        """Update the agent view"""
        if hasattr(self, 'view') and self.view:
            self.view.update()
    
    def setGeometry(self, *args, **kwargs):
        """Set geometry of the agent view"""
        if hasattr(self, 'view') and self.view:
            self.view.setGeometry(*args, **kwargs)
    
    def move(self, *args, **kwargs):
        """Move the agent view"""
        if hasattr(self, 'view') and self.view:
            self.view.move(*args, **kwargs)
    
    def resize(self, *args, **kwargs):
        """Resize the agent view"""
        if hasattr(self, 'view') and self.view:
            self.view.resize(*args, **kwargs)
    
    def setVisible(self, *args, **kwargs):
        """Set visibility of the agent view"""
        if hasattr(self, 'view') and self.view:
            self.view.setVisible(*args, **kwargs)
    
    def isVisible(self):
        """Check if agent view is visible"""
        if hasattr(self, 'view') and self.view:
            return self.view.isVisible()
        return False
    
    def rect(self):
        """Get rectangle of the agent view"""
        if hasattr(self, 'view') and self.view:
            return self.view.rect()
        return None
    
    def mapToGlobal(self, *args, **kwargs):
        """Map to global coordinates"""
        if hasattr(self, 'view') and self.view:
            return self.view.mapToGlobal(*args, **kwargs)
        return None
    
    def setAcceptDrops(self, *args, **kwargs):
        """Set accept drops"""
        if hasattr(self, 'view') and self.view:
            self.view.setAcceptDrops(*args, **kwargs)
    
    def grab(self):
        """Grab the agent view"""
        if hasattr(self, 'view') and self.view:
            return self.view.grab()
        return None

    # Legacy compatibility methods that delegate to view
    def paintEvent(self, event):
        """Paint event - delegates to view"""
        if hasattr(self, 'view') and self.view:
            self.view.paintEvent(event)
    
    def getRegion(self):
        """Get region - delegates to view"""
        if hasattr(self, 'view') and self.view:
            return self.view.getRegion()
        return None
    
    def mousePressEvent(self, event):
        """Mouse press event - delegates to view"""
        self.view.mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Mouse move event - delegates to view"""
        self.view.mouseMoveEvent(event)

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

    # Position calculation methods
    def getRandomX(self):        
        maxSize = self.cell.size
        # Use cell coordinates instead of pos()
        startX = self.cell.startXBase + (self.cell.xCoord - 1) * (self.cell.size + self.cell.gap) + self.cell.gap
        if self.classDef.shape in ["ellipseAgent2","rectAgent2"]: 
            x = random.randint(startX, startX + maxSize - round(self.size/2))
        else:
            x = random.randint(startX, startX + maxSize - self.size)
        return x
    
    def getRandomY(self): 
        maxSize = self.cell.size
        # Use cell coordinates instead of pos()
        startY = self.cell.startYBase + (self.cell.yCoord - 1) * (self.cell.size + self.cell.gap) + self.cell.gap
        if self.classDef.shape in ["ellipseAgent1","rectAgent1"]: 
            y = random.randint(startY, startY + maxSize - round(self.size/2))
        else:
            y = random.randint(startY, startY + maxSize - self.size)
        return y
    
    def getPositionInEntity(self):
        maxSize = self.cell.size
        # Use cell coordinates instead of pos()
        startX = self.cell.startXBase + (self.cell.xCoord - 1) * (self.cell.size + self.cell.gap) + self.cell.gap
        startY = self.cell.startYBase + (self.cell.yCoord - 1) * (self.cell.size + self.cell.gap) + self.cell.gap
        
        if self.classDef.locationInEntity == "random":
            self.xCoord = self.getRandomX()
            self.yCoord = self.getRandomY()
            return
        if self.classDef.locationInEntity == "topRight":
            self.xCoord = startX + maxSize - 10
            self.yCoord = startY + 5
            return
        if self.classDef.locationInEntity == "topLeft":
            self.xCoord = startX + 5
            self.yCoord = startY + 5
            return
        if self.classDef.locationInEntity == "bottomLeft":
            self.xCoord = startX + 5
            self.yCoord = startY + maxSize - 10
            return
        if self.classDef.locationInEntity == "bottomRight":
            self.xCoord = startX + maxSize - 10
            self.yCoord = startY + maxSize - 10
            return
        if self.classDef.locationInEntity == "center":
            self.xCoord = startX + int(maxSize/2) - int(self.size/2)
            self.yCoord = startY + int(maxSize/2) - int(self.size/2)
            return
        else:
            raise ValueError("Error in entry for locationInEntity")

    # Zoom methods
    def zoomIn(self, zoomFactor):
        """Zoom in the agent"""
        self.size = round(self.size + (zoomFactor * 10))
    
    def zoomOut(self, zoomFactor):
        """Zoom out the agent"""
        self.size = round(self.size - (zoomFactor * 10))

    # Feedback methods
    def feedBack(self, theAction):
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

    def moveTo(self, aDestinationCell):
        """
        Move agent to a new cell using Model-View architecture.
        The model moves, the view updates its position.
        
        Args:
            aDestinationCell: The destination cell
            
        Returns:
            self: The agent (for chaining)
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
            old_grid = self.cell.classDef.grid if hasattr(self.cell, 'classDef') and hasattr(self.cell.classDef, 'grid') else None
            new_grid = aDestinationCell.classDef.grid if hasattr(aDestinationCell, 'classDef') and hasattr(aDestinationCell.classDef, 'grid') else None
            
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

    def moveToCell(self, new_cell): #todo is this method used ? is it a model method ?
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
    
    def getPrivateId(self): #todo this is not a modeler method
        """Get private ID"""
        return self.privateID
    
    def getCell(self):
        """Get the current cell of the agent"""
        return self.cell
    
    def getCellCoordinates(self):
        """Get the coordinates of the current cell"""
        if self.cell:
            return (self.cell.xCoord, self.cell.yCoord)
        return None
    
    def getAgentsHere(self, specie=None):
        """
        Get all agents in the same cell as this agent.

        Args:
            specie (str | None): If specified, only agents of this specie are returned.

        Returns:
            list[SGAgent]: Agents in the same cell.
        """
        if self.cell is None:
            return []
        
        agents = self.cell.getAgents()
        if specie is None:
            return agents
        
        # Filter by species
        return [agent for agent in agents if agent.classDef.entityName == specie]

    def nbAgentsHere(self, specie=None):
        """
        Get the number of agents in the same cell as this agent.

        Args:
            specie (str | None): If specified, only agents of this specie are counted.

        Returns:
            int: Number of matching agents in the same cell.
        """
        if self.cell is None:
            return 0
        return len(self.getAgentsHere(specie))

    def getNeighborCells(self, neighborhood=None):
        """Get neighbor cells"""
        return self.cell.getNeighborCells(condition=neighborhood)
    
    def getNeighborAgents(self, aSpecies=None, neighborhood=None):
        """Get neighbor agents"""
        neighborAgents = []        
        neighborAgents = [aCell.agents for aCell in self.getNeighborCells(neighborhood=neighborhood)]
        
        if aSpecies:
            return self.filterBySpecies(aSpecies, neighborAgents)
        return neighborAgents
    
    def getClosestAgentMatching(self, agentSpecie, max_distance=1, conditions_on_agent=None, conditions_on_cell=None, return_all=False):
        """
        Find the closest neighboring agent of a given species from this agent's position,
        with optional filtering conditions on the target agent and the target cell.

        This method is a wrapper for SGCell.getClosestAgentMatching().

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
        
        return self.cell.getClosestAgentMatching(
            agentSpecie=agentSpecie,
            max_distance=max_distance,
            conditions_on_agent=conditions_on_agent,
            conditions_on_cell=conditions_on_cell,
            return_all=return_all
        )

    def nbNeighborAgents(self, aSpecies=None, neighborhood=None):  
        """Get number of neighbor agents"""
        return len(self.getNeighborAgents(aSpecies, neighborhood))

    def getNeighborsN(self, aSpecies=None):
        """Get neighbors to the North"""
        theCell = self.cell.getNeighborN()
        if aSpecies:
            return self.filterBySpecies(aSpecies, theCell.agents)
        return theCell.agents
    
    def getNeighborsS(self, aSpecies=None):
        """Get neighbors to the South"""
        theCell = self.cell.getNeighborS()
        if aSpecies:
            return self.filterBySpecies(aSpecies, theCell.agents)
        return theCell.agents
    
    def getNeighborsE(self, aSpecies=None):
        """Get neighbors to the East"""
        theCell = self.cell.getNeighborE()
        if aSpecies:
            return self.filterBySpecies(aSpecies, theCell.agents)
        return theCell.agents
    
    def getNeighborsW(self, aSpecies=None):
        """Get neighbors to the West"""
        theCell = self.cell.getNeighborW()
        if aSpecies:
            return self.filterBySpecies(aSpecies, theCell.agents)
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

    def moveAgent(self, method="random", direction=None, cellID=None, numberOfMovement=1, condition=None):
        """
        Move the agent according to the specified method.
        
        Args:
            method (str): random, cell, cardinal
            direction (str): if cardinal; North, South, West, East
            cellID (str): if cell; cellx-y
            numberOfMovement (int): number of movement in one action
            condition (lambda function, optional): a condition that the destination cell should respect for the agent to move
        """
        if numberOfMovement > 1: 
            raise ValueError('SGE currently has an issue with multiple movements at a step of an agent. Do not use numberOfMovement for the time being')
        
        for i in range(numberOfMovement):
            if i > 0:
                oldAgent = theAgent
                originCell = oldAgent.cell
            else:
                oldAgent = self
                originCell = self.cell

            aGrid = originCell.grid

            if method == "random":
                neighbors = originCell.getNeighborCells(condition=condition)
                newCell = random.choice(neighbors) if neighbors else None

            if method == "cell" or cellID is not None:
                # Parse cellID format "cellx-y" to get coordinates
                if cellID and cellID.startswith("cell"):
                    try:
                        coords = cellID[4:].split("-")  # Remove "cell" prefix and split by "-"
                        if len(coords) == 2:
                            x, y = int(coords[0]), int(coords[1])
                            newCell = self.cell.classDef.getCell(x, y)
                        else:
                            newCell = None
                    except (ValueError, IndexError):
                        newCell = None
                else:
                    newCell = aGrid.getCell_withId(cellID)
                
                if condition is not None and newCell is not None:
                    if not condition(newCell):
                        newCell = None

            if method == "cardinal" or direction is not None:
                if direction == "North":
                    newCell = originCell.getNeighborN()
                elif direction == "South":
                    newCell = originCell.getNeighborS()
                elif direction == "East":
                    newCell = originCell.getNeighborE()
                elif direction == "West":
                    newCell = originCell.getNeighborW()
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

    def moveRandomly(self, numberOfMovement=1, condition=None):
        """
        An agent moves randomly in his direct neighborhood.
        
        Args:
            numberOfMovement (int): number of movement in one action
            condition (lambda function, optional): a condition that the destination cell should respect for the agent to move
        """
        self.moveAgent(numberOfMovement=numberOfMovement, condition=condition)

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
            target_cell = self.cell.classDef.getCell(target[0], target[1])
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

    def filterBySpecies(self, aSpecies, agents): #todo est ce que cette méthode ne devrait pas plutôt etre dans SGExtensions.py ?
        """Filter agents by species"""
        filtered_agents = []
        if len(agents) != 0:
            for aAgent in agents:
                if isinstance(aAgent, list):
                    for agent in aAgent:
                        if agent.classDef == aSpecies or agent.classDef.entityName == aSpecies:
                            filtered_agents.append(agent)
                elif hasattr(aAgent, 'classDef'):  # Check if it's an agent
                    if aAgent.classDef == aSpecies or aAgent.classDef.entityName == aSpecies:
                        filtered_agents.append(aAgent)
        return filtered_agents
                

        

