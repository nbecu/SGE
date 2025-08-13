from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGEntity import SGEntity
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
        e.accept()
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
        return self.hasAgents(specie)
    
    def hasAgents(self,specie=None):
        return self.nbAgents(specie) == 0

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
    def getNeighborCells(self, neighborhood=None,condition = None):
        """
        Get the neighboring cells of the current cell.

        Args:
            neighborhood ("moore", "neumann", optional):
                Type of neighborhood to use.
                - "moore": Includes diagonals (8 neighbors for square grid, 6 for hexagonal grid).
                - "neumann": Only orthogonal neighbors (4 neighbors for square grid; 3 or 4 for hexagonal grid depending on orientation).
                Defaults to the grid's `neighborhood` attribute.
            condition (lambda function, optional): a condition that cells must respect to be return by this method 

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
            [aCell for aCell in neighbors if condition(aCell)]


    # def getNeighborCells(self,neighborhood = None, boundaries=None):
    #     if neighborhood is None : neighborhood = self.grid.neighborhood
    #     boundary_condition = boundaries if boundaries is not None else self.grid.boundary_condition
    #     neighbors = []
    #     rows = self.grid.rows
    #     columns = self.grid.columns
    #     for i in range(self.xCoord - 1, self.xCoord + 2):
    #         for j in range(self.yCoord - 1, self.yCoord + 2):
    #             # Skip the cell itself
    #             if i == self.xCoord and j == self.yCoord:
    #                 continue
    #             # Handle boundary conditions
    #             if boundary_condition == "open":  # wrap-around (toroidal)
    #                 ii = i % columns   # X axis = column index
    #                 jj = j % rows      # Y axis = row index
    #             elif boundary_condition == "closed":  # no wrap-around
    #                 if i < 0 or i >= columns or j < 0 or j >= rows:
    #                     continue
    #                 ii, jj = i, j
    #             else:
    #                 raise ValueError(f"Invalid boundary condition: {boundary_condition}")

    #             # Determine neighbors according to neighborhood type
    #             if neighborhood == "moore":
    #                 c = self.classDef.getCell(ii, jj)
    #             elif neighborhood == "neumann":
    #                 # Neighbor if aligned horizontally or vertically, but not the cell itself
    #                 if (ii == self.xCoord or jj == self.yCoord) and not (ii == self.xCoord and jj == self.yCoord):
    #                     c = self.classDef.getCell(ii, jj)
    #                 else:
    #                     c = None
    #             else:
    #                 raise ValueError(f"Invalid neighborhood type: {neighborhood}")

    #             if c is not None:
    #                 neighbors.append(c)


        # for i in range(self.xCoord - 1, self.xCoord + 2):
        #     for j in range(self.yCoord - 1, self.yCoord + 2):
        #         if i == self.xCoord and j == self.yCoord:
        #             continue
        #         # Apply boundary condition
        #         x, y = i, j
        #         if boundary_condition == 'closed':
        #             x = i % cols
        #             y = j % rows
        #         # Skip if out of bounds and boundary is open
        #         if boundary_condition == 'open':
        #             if x < 0 or x >= cols or y < 0 or y >= rows:
        #                 continue
        #         # Apply neighborhood rule
        #         if neighborhood == "moore":
        #             c = self.classDef.getCell(x, y)
        #         elif neighborhood == "neumann":
        #             if (x == self.xCoord or y == self.yCoord) and (x != self.xCoord or y != self.yCoord):
        #                 c = self.classDef.getCell(x, y)
        #             else:
        #                 c = None
        #         else:
        #             print('Error in neighborhood specification')
        #             return []

        #         if c is not None:
        #             neighbors.append(c)
        # for i in range(self.xCoord - 1, self.xCoord + 2):
        #     for j in range(self.yCoord - 1, self.yCoord + 2):
        #         if i == self.xCoord and j == self.yCoord:
        #             continue
        #         if neighborhood =="moore":
        #             c = self.classDef.getCell(i, j)
        #         elif neighborhood =='neumann':
        #             if (i == self.xCoord or j == self.yCoord) and (i != self.xCoord or j != self.yCoord):
        #                 c = self.classDef.getCell(i,j)
        #             else:
        #                 c = None
        #         else:
        #             print('Error in neighborhood specification')
        #             break
        #         if c is not None:
        #             neighbors.append(c)
        return neighbors
        
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