from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog, QMessageBox, QDialog, QLabel, QVBoxLayout, QToolTip
from PyQt5.QtGui import QCursor

import random
from mainClasses.SGEntity import SGEntity
from mainClasses.SGCell import SGCell
from mainClasses.SGAgentModel import SGAgentModel
from mainClasses.SGAgentView import SGAgentView
from mainClasses.gameAction.SGCreate import *
from mainClasses.gameAction.SGDelete import *
from mainClasses.gameAction.SGModify import *
from mainClasses.gameAction.SGMove import *
from mainClasses.gameAction.SGActivate import *
   
#Class who is responsible of the declaration a Agent
class SGAgent(SGAgentModel):
    """
    SGAgent - Agent class for agent-based simulations
    
    This class now uses Model-View architecture:
    - Inherits from SGAgentModel for data and business logic
    - Delegates UI to SGAgentView for display and interaction
    """
    
    def __init__(self, cell, size, attributesAndValues, shapeColor, classDef, defaultImage, popupImage):
        # Initialize the model part
        super().__init__(cell, size, attributesAndValues, shapeColor, classDef, defaultImage, popupImage)
        
        # View will be created and linked by the factory
        # Don't create view here to avoid duplication
        
        # Initialize attributes
        self.initAttributesAndValuesWith(attributesAndValues)
        
        # Type identification attributes
        self.isEntity = True
        self.isCell = False
        self.isAgent = True

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

    # Model methods that are now inherited from SGAgentModel
    # These are kept for backward compatibility but delegate to the model
    
    def zoomIn(self, zoomFactor):
        """Zoom in - delegates to model"""
        super().zoomIn(zoomFactor)
        self.updateView()
    
    def zoomOut(self, zoomFactor):
        """Zoom out - delegates to model"""
        super().zoomOut(zoomFactor)
        self.updateView()
    
    def getRandomX(self):
        """Get random X - delegates to model"""
        return super().getRandomX()
    
    def getRandomY(self):
        """Get random Y - delegates to model"""
        return super().getRandomY()
    
    def getPositionInEntity(self):
        """Get position in entity - delegates to model"""
        return super().getPositionInEntity()
    
    def isDeleted(self):
        """Check if agent is deleted - delegates to model"""
        return super().isDeleted()

    # New Model-View specific methods
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


            

#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

# TODO: Remove these temporary methods once proper Model-View movement is implemented
# These methods were temporary workarounds before Model-View separation
# def updateAgentByRecreating_it(self):
#     aDestinationCell = self.cell
#     self.cell.updateDepartureAgent(self)
#     self.copyOfAgentAtCoord(aDestinationCell)
#     self.deleteLater()

# def copyOfAgentAtCoord(self, aCell):
#     oldAgent = self
#     newAgent = SGAgent(aCell, oldAgent.size,oldAgent.dictAttributes,oldAgent.classDef.povShapeColor,oldAgent.classDef,oldAgent.defaultImage,oldAgent.popupImage)
#     self.classDef.IDincr -=1
#     newAgent.id = oldAgent.id
#     newAgent.history = oldAgent.history
#     newAgent.watchers = oldAgent.watchers
#     #apply correction on the watchers on this entity
#     for watchers in list(oldAgent.watchers.values()):
#         for aWatcherOnThisAgent in watchers:
#             aWatcherOnThisAgent.entity=newAgent        
#     newAgent.privateID = oldAgent.privateID
#     newAgent.isDisplay = oldAgent.isDisplay
#     newAgent.classDef.entities.remove(oldAgent)
#     newAgent.classDef.entities.append(newAgent)
#     newAgent.update()
#     newAgent.show()
#     self.update()
#     return newAgent
    

    def moveTo(self, aDestinationCell):
        """
        Move agent to a new cell using Model-View architecture.
        The model moves, the view updates its position.
        
        Args:
            aDestinationCell: The destination cell
            
        Returns:
            self: The agent (for chaining)
        """
        print(f"DEBUG: moveTo called for agent {self.id} to cell {aDestinationCell.id}")
        print(f"DEBUG: Agent current position: ({self.xCoord}, {self.yCoord})")
        print(f"DEBUG: Destination cell position: ({aDestinationCell.xCoord}, {aDestinationCell.yCoord})")
        
        if self.cell is None:
            # First placement
            print(f"DEBUG: First placement of agent {self.id}")
            self.cell = aDestinationCell
            self.cell.updateIncomingAgent(self)
            self.getPositionInEntity()  # Update position
            self.view.getPositionInEntity()  # Force view repositioning
            self.updateView()
            print(f"DEBUG: Agent {self.id} placed at ({self.xCoord}, {self.yCoord})")
            return self
        else:
            # Movement from one cell to another
            print(f"DEBUG: Moving agent {self.id} from cell {self.cell.id} to cell {aDestinationCell.id}")
            # Remove from current cell
            self.cell.removeAgent(self)
            
            # Move to new cell
            self.cell = aDestinationCell
            self.cell.updateIncomingAgent(self)
            
            # Update position and view
            self.getPositionInEntity()
            self.view.getPositionInEntity()  # Force view repositioning
            self.updateView()
            
            print(f"DEBUG: Agent {self.id} moved to ({self.xCoord}, {self.yCoord})")
            return self

    def moveAgent(self,method="random",direction=None,cellID=None,numberOfMovement=1,condition=None):
        """
        An agent moves.

        args:
            method (str): random, cell, cardinal
            direction (str): if cardinal; North, South, West, East
            cellID (str): if cell; cellx-y
            numberOfMovement (int): number of movement in one action
            condition (lambda function, optional): a condition that the destination cell should respect for the agent to move
        """
        if numberOfMovement > 1 : raise ValueError('SGE currently has an issue with multiple movements at a step of an agent. Do not use numberOfMovement for the time being')
        for i in range(numberOfMovement):

            if i>0:
                oldAgent=theAgent
                originCell=oldAgent.cell
            else:
                oldAgent=self
                originCell=self.cell

            aGrid=originCell.grid

            if method == "random":
                neighbors=originCell.getNeighborCells(condition=condition)
                newCell=random.choice(neighbors) if neighbors else None

            if method == "cell" or cellID is not None:
                newCell=aGrid.getCell_withId(cellID)
                
                if condition is not None:
                    if not condition(newCell):
                        newCell = None

            if method == "cardinal" or direction is not None:
                if direction =="North":
                    newCell=originCell.getNeighborN()
                if direction =="South":
                    newCell=originCell.getNeighborS()
                if direction =="East":
                    newCell=originCell.getNeighborE()
                if direction =="West":
                    newCell=originCell.getNeighborW()
                    
                if condition is not None:
                    if not condition(newCell):
                        newCell = None
                

            if newCell is None:
                pass
            else:
                theAgent = self.moveTo(newCell)
        pass
        return newCell

    def moveRandomly(self,numberOfMovement=1,condition=None):
        """
        An agent moves randomly in his direct neighborhood.
        
        args:
            numberOfMovement (int): number of movement in one action
            condition (lambda function, optional): a condition that the destination cell should respect for the agent to move
        """
        self.moveAgent(numberOfMovement=numberOfMovement,condition=condition)

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
        if isinstance(target, SGAgent):  # Target is an agent
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

    def getId(self):
        return self.id
    
    def getPrivateId(self):
        return self.privateID
    
    def getAgentsHere(self, specie=None):
        """
        Get all agents in the same cell as this agent.

        Args:
            specie (str | None): If specified, only agents of this specie are returned.

        Returns:
            list[SGAgent]: Agents in the same cell.
        """
        return super().getAgentsHere(specie)

    def nbAgentsHere(self, specie=None):
        """
        Get the number of agents in the same cell as this agent.

        Args:
            specie (str | None): If specified, only agents of this specie are counted.

        Returns:
            int: Number of matching agents in the same cell.
        """
        return super().nbAgentsHere(specie)

    def hasAgentsHere(self, specie=None):
        """
        Check if the cell containing this agent has at least one agent.

        Args:
            specie (str | None): If specified, check only for agents of this specie.

        Returns:
            bool: True if at least one matching agent is in the same cell, False otherwise.
        """
        return super().hasAgentsHere(specie)
    
    def getNeighborCells(self,neighborhood=None):
        return self.cell.getNeighborCells(neighborhood=neighborhood)
    
    def getNeighborAgents(self,aSpecies=None,neighborhood=None):
                
        neighborAgents=[]        
        neighborAgents=[aCell.agents for aCell in self.getNeighborCells(neighborhood=neighborhood)]
        
        if aSpecies:
            return self.filterBySpecies(aSpecies,neighborAgents)
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

    
    def filterBySpecies(self,aSpecies,agents):
        agents=[]
        if len(agents)!=0:
            for aAgent in agents:
                if isinstance(aAgent,list):
                    for agent in aAgent:
                        if agent.classDef == aSpecies or agent.classDef.entityName == aSpecies:
                            agents.append(agent)
                elif isinstance(aAgent,SGAgent):
                    if aAgent.classDef == aSpecies or aAgent.classDef.entityName == aSpecies:
                        agents.append(aAgent)
        return agents
    
    def nbNeighborAgents(self,aSpecies=None,neighborhood=None):  
        return len(self.getNeighborAgents(aSpecies,neighborhood))

    def getNeighborsN(self,aSpecies=None):
        theCell=self.cell.getNeighborN()
        if aSpecies:
            return self.filterBySpecies(aSpecies,theCell.agents)
        return theCell.agents
    
    def getNeighborsS(self,aSpecies=None):
        theCell=self.cell.getNeighborS()
        if aSpecies:
            return self.filterBySpecies(aSpecies,theCell.agents)
        return theCell.agents
    
    def getNeighborsE(self,aSpecies=None):
        theCell=self.cell.getNeighborE()
        if aSpecies:
            return self.filterBySpecies(aSpecies,theCell.agents)
        return theCell.agents
    
    def getNeighborsW(self,aSpecies=None):
        theCell=self.cell.getNeighborW()
        if aSpecies:
            return self.filterBySpecies(aSpecies,theCell.agents)
        return theCell.agents

    

    
    
                

        

