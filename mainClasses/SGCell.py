from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGEntity import SGEntity
import random
# from mainClasses.gameAction.SGMove import SGMove
   
#Class who is responsible of the declaration a cell
class SGCell(SGEntity):
    def __init__(self,classDef, x, y,defaultImage):
        super().__init__(classDef.grid,classDef,classDef.defaultsize,attributesAndValues=None)
        #Basic initialize
        self.grid=classDef.grid
        self.xCoord=x
        self.yCoord=y
        self.gap=self.grid.gap
        #Save the basic value for the zoom (temporary)
        self.saveGap=self.gap
        self.saveSize=classDef.defaultsize
        #We place the default pos
        self.startXBase=self.grid.startXBase
        self.startYBase=self.grid.startYBase
        #We allow the drops for the agents
        self.setAcceptDrops(True)
        self.agents=[]

        self.defaultImage=defaultImage

    
        
    def getId(self):
        return "cell"+str(self.xCoord)+"-"+str(self.yCoord)
    
    def paintEvent(self,event):
        painter = QPainter()
        painter.begin(self)
        region=self.getRegion()
        image=self.getImage()
        if self.isDisplay==True:
            if self.defaultImage != None:
                rect,scaledImage = self.rescaleImage(self.defaultImage)
                painter.setClipRegion(region)
                painter.drawPixmap(rect, scaledImage)
            elif image != None:
                rect,scaledImage = self.rescaleImage(image)
                painter.setClipRegion(region)
                painter.drawPixmap(rect, scaledImage)
            else : painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
            penColorAndWidth = self.getBorderColorAndWidth()
            painter.setPen(QPen(penColorAndWidth['color'],penColorAndWidth['width']))
            self.startXBase=self.grid.frameMargin
            self.startYBase=self.grid.frameMargin
            self.startX=int(self.startXBase+(self.xCoord -1)*(self.size+self.gap)+self.gap) 
            self.startY=int(self.startYBase+(self.yCoord -1)*(self.size+self.gap)+self.gap)
            if (self.shape=="hexagonal"):
                self.startY=self.startY+self.size/4
            #Base of the gameBoard
            if(self.shape=="square"):
                painter.drawRect(0,0,self.size,self.size)
                self.setMinimumSize(self.size,self.size+1)
                self.move(self.startX,self.startY)
            elif(self.shape=="hexagonal"):
                self.setMinimumSize(self.size,self.size)
                points = QPolygon([
                    QPoint(int(self.size/2), 0),
                    QPoint(self.size, int(self.size/4)),
                    QPoint(self.size, int(3*self.size/4)),
                    QPoint(int(self.size/2), self.size),
                    QPoint(0, int(3*self.size/4)),
                    QPoint(0, int(self.size/4))              
                ])
                painter.drawPolygon(points)
                if(self.yCoord%2!=0):
                    self.move(self.startX , int(self.startY-self.size/2*self.yCoord +(self.gap/10+self.size/4)*self.yCoord))
                else:
                    self.move((self.startX+int(self.size/2)+int(self.gap/2) ), int(self.startY-self.size/2*self.yCoord +(self.gap/10+self.size/4)*self.yCoord))
                        
        painter.end()
    
    def getRegion(self):
        cellShape=self.classDef.shape
        if cellShape == "square":
            region = QRegion(0,0,self.size,self.size)
        if cellShape =="hexagonal":
            points = QPolygon([
                    QPoint(int(self.size/2), 0),
                    QPoint(self.size, int(self.size/4)),
                    QPoint(self.size, int(3*self.size/4)),
                    QPoint(int(self.size/2), self.size),
                    QPoint(0, int(3*self.size/4)),
                    QPoint(0, int(self.size/4))              
                ])
            region=QRegion(points)
        return region


    #Funtion to handle the zoom
    def zoomIn(self):
        oldSize=self.size
        self.size=self.grid.size
        self.gap=self.grid.gap
        self.update()
    
    def zoomOut(self):
        oldSize=self.size
        self.size=self.grid.size
        self.gap=self.grid.gap
        self.update()
        
    def zoomFit(self):
        self.size=self.grid.size
        self.gap=self.grid.gap
        self.update()

    def convert_coordinates(self, global_pos: QPoint) -> QPoint:
    # Convert global coordinates to local coordinates
        local_pos = self.mapFromGlobal(global_pos)
        return local_pos

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            #Something is selected
            aLegendItem = self.model.getSelectedLegendItem()
            if aLegendItem is None : return #Exit the method

            if aLegendItem.legend.isAdminLegend():
                authorisation= True
            else :
                aLegendItem.gameAction.perform_with(self) #aLegendItem (aParameterHolder) is not send has arg anymore has it is not used and it complicates the updateServer
                return

            if not authorisation : return #Exit the method
        
            #The delete Action
            if aLegendItem.type == 'delete' :
                if authorisation : 
                    #We now check the feedBack of the actions if it have some
                    """if theAction is not None:
                        self.feedBack(theAction)"""
                    if not self.isDeleted() :self.classDef.deleteEntity(self)

            #The Replace cell and change value Action
            elif aLegendItem.isSymbolOnCell():
                if  authorisation :
                    #We now check the feedBack of the actions if it have some
                    if self.isDeleted() : self.classDef.reviveThisCell(self) 
                    self.setValue(aLegendItem.nameOfAttribut,aLegendItem.valueOfAttribut)     

            #For agent creation on cell         
            elif aLegendItem.isSymbolOnAgent() and self.isDisplay:
                if  authorisation :
                    aLegendItem.classDef
                    aDictWithValue ={aLegendItem.nameOfAttribut:aLegendItem.valueOfAttribut}
                    self.newAgentHere(aLegendItem.classDef,aDictWithValue)
        
    def dropEvent(self, e):
        e.acceptProposedAction()
        aAgent=e.source()

        if not isinstance(aAgent,SGEntity):
            return
        
        currentPlayer=self.model.getCurrentPlayer()
        
        if currentPlayer == 'Admin':
            aAgent.moveTo(self)
        
        else :
            moveActions=currentPlayer.getMoveActionsOn(aAgent)

            for aMoveAction in moveActions:
                if aMoveAction.checkAuthorization(aAgent,self):
                    aMoveAction.perform_with(aAgent,self)
                    e.setDropAction(Qt.MoveAction)
                    aAgent.dragging = False

        # Le code ci-dessous est la version précédente de la méthode dropEvent. Il est conservé pour référence
        # e.accept()
        # aAgent=e.source()
        # aActiveLegend = self.model.getSelectedLegend() 
        # aLegendItem = self.model.getSelectedLegendItem()
        # if aActiveLegend is None or aActiveLegend.isAdminLegend(): 
        #     aAgent.moveTo(self)
        # elif aLegendItem is None : None #Exit the method
        # else :
        #     aLegendItem.gameAction.perform_with(aAgent,self)   #aLegendItem (aParameterHolder) is not send has arg anymore has it is not used and it complicates the updateServer
        # e.setDropAction(Qt.MoveAction)
        # aAgent.dragging = False
                            
    # To handle the drag of the grid
    def mouseMoveEvent(self, e): #this method is used to prevent the drag of a cell
        if e.buttons() != Qt.LeftButton:
            return
                                            
    # Function to handle the drag of widget
    def dragEnterEvent(self, e):
        # this is event is called during an agent drag 
        e.accept()
       
    #Apply the feedBack of a gameMechanics
    def feedBack(self, theAction,theAgentForMoveGM=None):
        booleanForFeedback=True
        booleanForFeedbackAgent=True
        for anCondition in theAction.conditionOfFeedBack :
            booleanForFeedback=booleanForFeedback and anCondition(self)
        if booleanForFeedback :
            for aFeedback in  theAction.feedback :
                aFeedback(self)
        if theAgentForMoveGM is not None :
            for anCondition in theAction.conditionOfFeedBackAgent :
                booleanForFeedbackAgent=booleanForFeedbackAgent and anCondition(self,theAgentForMoveGM)
            if booleanForFeedbackAgent :
                for aFeedback in  theAction.feedbackAgent :
                    aFeedback(theAgentForMoveGM)
            
                      
            
    #To handle the arrival of an agent on the cell (this is a private method)
    def updateIncomingAgent(self,anAgent):
        self.agents.append(anAgent)
    
    #To handle the departure of an agent of the cell (this is a private method)
    def updateDepartureAgent(self,anAgent):
        self.agents.remove(anAgent)
        anAgent.cell=None
    


#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use  
    
    #To get all of a kind of agent on a cell 
    def getAgents(self,specie=None):
        if specie != None:
            return self.getAgentsOfSpecie(specie)
        return  self.agents[:]
    
    def nbAgents(self,specie=None): 
        if specie != None:
            listAgts = self.getAgentsOfSpecie(specie)
        else: listAgts = self.getAgents()
        return  len(listAgts)
 
    def isEmpty(self,specie=None):
        return not self.hasAgents(specie)
    
    def hasAgents(self,specie=None):
        return self.nbAgents(specie) > 0

    #To get all agents on the grid of a particular type
    def getAgentsOfSpecie(self,nameOfSpecie):
        from mainClasses.SGEntityDef import SGAgentDef # Import local pour éviter l'import circulaire
        if isinstance(nameOfSpecie,SGAgentDef): nameOfSpecie = nameOfSpecie.entityName
        return [aAgt for aAgt in self.agents if aAgt.classDef.entityName == nameOfSpecie]
    
    #To get the agent of a particular type
    def getFirstAgentOfSpecie(self,nameOfSpecie):
        agents = self.getAgentsOfSpecie(nameOfSpecie)
        if not agents:
            return None
        else: return agents[0]
        
    
    #To get the neighbor cells
    def getNeighborCells(self, condition = None, neighborhood=None):
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

                # Determine neighbors according to neighborhood type
                if neighborhood == "moore":
                    c = self.classDef.getCell(ii, jj)
                elif neighborhood == "neumann":
                    if (ii == self.xCoord or jj == self.yCoord) and not (ii == self.xCoord and jj == self.yCoord):
                        c = self.classDef.getCell(ii, jj)
                    else:
                        c = None
                else:
                    raise ValueError(f"Invalid neighborhood type: {neighborhood}")

                if c is not None:
                    neighbors.append(c)

        if condition is None:
            return neighbors
        else:
            return [aCell for aCell in neighbors if condition(aCell)]
        

    def getNeighborCells_inRadius(self, max_distance=1, conditions=None, neighborhood=None):
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


    #To get the neighbor cell at cardinal
    def getNeighborN(self):
        return self.classDef.getCell(self.xCoord,self.yCoord-1)
    def getNeighborS(self):
        return self.classDef.getCell(self.xCoord,self.yCoord+1)
    def getNeighborE(self):
        return self.classDef.getCell(self.xCoord+1,self.yCoord)
    def getNeighborW(self):
        return self.classDef.getCell(self.xCoord-1,self.yCoordPos)        
            
    #Delete all agents on the cell
    def deleteAllAgents(self):
        for agt in self.agents[:]:
            agt.classDef.deleteEntity(agt)
        self.update()

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