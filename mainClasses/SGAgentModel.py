from mainClasses.SGEntityModel import SGEntityModel
import random
from mainClasses.SGCell import SGCell
from PyQt5.QtWidgets import QAction

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
        
        # Initialize position
        self.getPositionInEntity()
    
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

    # Position and movement methods
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

    # Movement methods
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
                newCell = aGrid.getCell_withId(cellID)
                
                if condition is not None:
                    if not condition(newCell):
                        newCell = None

            if method == "cardinal" or direction is not None:
                if direction == "North":
                    newCell = originCell.getNeighborN()
                if direction == "South":
                    newCell = originCell.getNeighborS()
                if direction == "East":
                    newCell = originCell.getNeighborE()
                if direction == "West":
                    newCell = originCell.getNeighborW()
                    
                if condition is not None:
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
        elif isinstance(target, SGCell):  # Target is a Cell
            target_cell = target
        elif isinstance(target, tuple) and len(target) == 2:  # Coordinates (x, y)
            target_cell = self.cell.grid.getCell(target)
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

    def moveTo(self, new_cell):
        """Move to a new cell and return the agent"""
        self.moveToCell(new_cell)
        return self

    # Information methods
    def getId(self):
        """Get agent ID"""
        return self.id
    
    def getPrivateId(self):
        """Get private ID"""
        return self.privateID
    
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
    
    def getNeighborCells(self, neighborhood=None):
        """Get neighbor cells"""
        return self.cell.getNeighborCells(neighborhood=neighborhood)
    
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

    def filterBySpecies(self, aSpecies, agents):
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
