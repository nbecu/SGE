from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog, QMessageBox, QDialog, QLabel, QVBoxLayout, QToolTip
from PyQt5.QtGui import QCursor

import random
from mainClasses.SGEntity import SGEntity
from mainClasses.SGCell import SGCell
   
#Class who is responsible of the declaration a Agent
class SGAgent(SGEntity):
    def __init__(self,cell,size,attributesAndValues,shapeColor,classDef,defaultImage,popupImage):
        aGrid = cell.grid
        super().__init__(aGrid,classDef, size,attributesAndValues)
        self.cell=None
        if cell is not None:
            self.cell = cell
            self.cell.updateIncomingAgent(self)
        else: raise ValueError('This case is not handeled')
        self.getPositionInEntity()
        self.last_selected_option=None

        self.defaultImage=defaultImage
        self.popupImage=popupImage
        self.dragging = False
        


    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        region = self.getRegion()
        painter.setClipRegion(region)
        image = self.defaultImage if self.defaultImage is not None else self.getImage()
        if image is not None:
            if image.width() ==0 or image.height == 0 : raise ValueError(f'Image size is not valid for {self.privateID}')
            rect, scaledImage = self.rescaleImage(image)
            painter.drawPixmap(rect, scaledImage)
        else :
            painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
        penColorAndWidth = self.getBorderColorAndWidth()
        painter.setPen(QPen(penColorAndWidth['color'],penColorAndWidth['width']))
        agentShape = self.classDef.shape
        x = self.xCoord
        y = self.yCoord
        if self.isDisplay==True:
            if(agentShape=="circleAgent"):
                self.setGeometry(x,y,self.size,self.size)
                painter.drawEllipse(0,0,self.size,self.size)
            elif agentShape=="squareAgent":
                self.setGeometry(x,y,self.size,self.size)
                painter.drawRect(0,0,self.size,self.size)
            elif agentShape=="ellipseAgent1": 
                self.setGeometry(x,y,self.size,round(self.size/2))
                painter.drawEllipse(0,0,self.size,round(self.size/2))
            elif agentShape=="ellipseAgent2": 
                self.setGeometry(x,y,round(self.size/2),self.size)
                painter.drawEllipse(0,0,round(self.size/2),self.size)
            elif agentShape=="rectAgent1": 
                self.setGeometry(x,y,self.size,round(self.size/2))
                painter.drawRect(0,0,self.size,round(self.size/2))
            elif agentShape=="rectAgent2": 
                self.setGeometry(x,y,round(self.size/2),self.size)
                painter.drawRect(0,0,round(self.size/2),self.size)
            elif agentShape=="triangleAgent1": 
                self.setGeometry(x,y,self.size,self.size)
                points = QPolygon([
                QPoint(round(self.size/2),0),
                QPoint(0,self.size),
                QPoint(self.size,  self.size)
                ])
                painter.drawPolygon(points)
            elif agentShape=="triangleAgent2": 
                self.setGeometry(x,y,self.size,self.size)
                points = QPolygon([
                QPoint(0,0),
                QPoint(self.size,0),
                QPoint(round(self.size/2),self.size)
                ])
                painter.drawPolygon(points)
            elif agentShape=="arrowAgent1": 
                self.setGeometry(x,y,self.size,self.size)
                points = QPolygon([
                QPoint(round(self.size/2),0),
                QPoint(0,self.size),
                QPoint(round(self.size/2),round(self.size/3)*2),
                QPoint(self.size,  self.size)
                ])
                painter.drawPolygon(points)
            elif agentShape=="arrowAgent2": 
                self.setGeometry(x,y,self.size,self.size)
                points = QPolygon([
                QPoint(0,0),
                QPoint(round(self.size/2),round(self.size/3)),
                QPoint(self.size,0),
                QPoint(round(self.size/2),self.size)
                ])
                painter.drawPolygon(points)
            elif agentShape == "hexagonAgent":
                self.setGeometry(x, y, self.size, self.size)
                side = self.size / 2
                height = round(side * (3 ** 0.5))+10  # Hauteur de l'hexagone équilatéral
                points = QPolygon([
                    QPoint(round(self.size/2), 0),                # Sommet supérieur
                    QPoint(self.size, round(height/4)),           # Coin supérieur droit
                    QPoint(self.size, round(3*height/4)),         # Coin inférieur droit
                    QPoint(round(self.size/2), height),           # Sommet inférieur
                    QPoint(0, round(3*height/4)),                 # Coin inférieur gauche
                    QPoint(0, round(height/4))                    # Coin supérieur gauche
                ])
                painter.drawPolygon(points)
            self.show()
            painter.end()
    
    def getRegion(self):
        agentShape=self.classDef.shape
        if(agentShape=="circleAgent"):
            region = QRegion(0, 0, self.size, self.size, QRegion.Ellipse)
        elif agentShape=="squareAgent":
            region = QRegion(0, 0, self.size, self.size)
        elif agentShape=="ellipseAgent1": 
            region = QRegion(0,0,self.size,round(self.size/2))
        elif agentShape=="ellipseAgent2": 
            region = QRegion(0,0,round(self.size/2),self.size)
        elif agentShape=="rectAgent1": 
            region = QRegion(0,0,self.size,round(self.size/2))
        elif agentShape=="rectAgent2": 
            region = QRegion(0,0,round(self.size/2),self.size)
        elif agentShape=="triangleAgent1": 
            points = QPolygon([
            QPoint(round(self.size/2),0),
            QPoint(0,self.size),
            QPoint(self.size,  self.size)
            ])
            region = QRegion(points)
        elif agentShape=="triangleAgent2": 
            points = QPolygon([
            QPoint(0,0),
            QPoint(self.size,0),
            QPoint(round(self.size/2),self.size)
            ])
            region = QRegion(points)
        elif agentShape=="arrowAgent1": 
            points = QPolygon([
            QPoint(round(self.size/2),0),
            QPoint(0,self.size),
            QPoint(round(self.size/2),round(self.size/3)*2),
            QPoint(self.size,  self.size)
            ])
            region = QRegion(points)
        elif agentShape=="arrowAgent2": 
            points = QPolygon([
            QPoint(0,0),
            QPoint(round(self.size/2),round(self.size/3)),
            QPoint(self.size,0),
            QPoint(round(self.size/2),self.size)
            ])
            region = QRegion(points)
        elif agentShape == "hexagonAgent":  
            side = self.size / 2
            height = round(side * (3 ** 0.5))+10  
            points = QPolygon([
                QPoint(round(self.size/2), 0),        
                QPoint(self.size, round(height/4)),           
                QPoint(self.size, round(3*height/4)),    
                QPoint(round(self.size/2), height),        
                QPoint(0, round(3*height/4)),              
                QPoint(0, round(height/4))                   
            ])
            region = QRegion(points)
        return region
   
   
   #Funtion to handle the zoomIn
    def zoomIn(self,zoomFactor):
        self.size=round(self.size+(zoomFactor*10))
        self.update()

    #Funtion to handle the zoomOut
    def zoomOut(self,zoomFactor):
        self.size=round(self.size-(zoomFactor*10))
        self.update()
            
    def getRandomX(self):        
        maxSize=self.cell.size
        originPoint=self.cell.pos()
        if self.classDef.shape in ["ellipseAgent2","rectAgent2"]: 
            x = random.randint(originPoint.x(),originPoint.x()+maxSize-round(self.size/2))
        else:
            x = random.randint(originPoint.x(),originPoint.x()+maxSize-self.size)
        return x
        
    
    def getRandomY(self): 
        maxSize=self.cell.size
        originPoint=self.cell.pos()
        if self.classDef.shape in ["ellipseAgent1","rectAgent1"]: 
            y = random.randint(originPoint.y(),originPoint.y()+maxSize-round(self.size/2))
        else:
            y = random.randint(originPoint.y(),originPoint.y()+maxSize-self.size)
        return y
    
    def getPositionInEntity(self):
        maxSize=self.cell.size
        originPoint=self.cell.pos()
        if self.classDef.locationInEntity=="random":
            self.xCoord=self.getRandomX()
            self.yCoord=self.getRandomY()
            return
        if self.classDef.locationInEntity=="topRight":
            self.xCoord=originPoint.x()+maxSize-10
            self.yCoord=originPoint.y()+5
            return
        if self.classDef.locationInEntity=="topLeft":
            self.xCoord=originPoint.x()+5
            self.yCoord=originPoint.y()+5
            return
        if self.classDef.locationInEntity=="bottomLeft":
            self.xCoord=originPoint.x()+5
            self.yCoord=originPoint.y()+maxSize-10
            return
        if self.classDef.locationInEntity=="bottomRight":
            self.xCoord=originPoint.x()+maxSize-10
            self.yCoord=originPoint.y()+maxSize-10
            return
        if self.classDef.locationInEntity=="center":
            self.xCoord=originPoint.x()+int(maxSize/2)-int(self.size/2)
            self.yCoord=originPoint.y()+int(maxSize/2)-int(self.size/2)
            return
        else:
            raise ValueError("Error in entry for locationInEntity")

    def isDeleted(self):
        if not self.isDisplay:
            raise ValueError ('An agent which is not displayed is not necessary deleted.') 
        return not self.isDisplay
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            #Something is selected
            aLegendItem = self.model.getSelectedLegendItem()
            if aLegendItem is None : return #Exit the method

            if aLegendItem.legend.isAdminLegend():
                authorisation= True
            else :
                from mainClasses.gameAction.SGMove import SGMove
                if isinstance(aLegendItem.gameAction,SGMove): return
                aLegendItem.gameAction.perform_with(self)  #aLegendItem (aParameterHolder) is not send has arg anymore has it is not used and it complicates the updateServer
                return
            if not authorisation : return #Exit the method

            #The delete Action
            if aLegendItem.type == 'delete' :
                if authorisation : 
                    self.classDef.deleteEntity(self)

            #The  change value on agent
            elif aLegendItem.isSymbolOnAgent() :
                if  authorisation :
                    self.setValue(aLegendItem.nameOfAttribut,aLegendItem.valueOfAttribut)     
                    # self.update()


            
    #To handle the drag of the agent
    def mouseMoveEvent(self, e):
    
        if e.buttons() != Qt.LeftButton:
            return
        authorisation = True
        if authorisation:
            mimeData = QMimeData()
            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(e.pos() - self.rect().topLeft())
            drag.exec_(Qt.CopyAction | Qt.MoveAction)

    def dragEnterEvent(self,e):
        e.accept()
        self.setAcceptDrops(True)


    def dropEvent(self, e):
        raise ValueError("This function shouldn't be used")
        #TODO If this function is not used, delete it.
        e.accept()
        theDroppedAgent=e.source()
        aActiveLegend = self.cell.model.getSelectedLegend() 
        aLegendItem = self.cell.model.getSelectedLegendItem()
        if aActiveLegend.isAdminLegend(): 
            theDroppedAgent.moveTo(self.cell)
        elif aLegendItem is None : None #Exit the method
        else :
            aLegendItem.gameAction.perform_with(theDroppedAgent,self.cell)   #aLegendItem (aParameterHolder) is not send has arg anymore has it is not used and it complicates the updateServer
        e.setDropAction(Qt.MoveAction)
        self.dragging = False

    def enterEvent(self, event):
        if self.dragging:
            return

        if self.popupImage:
            # Convertir l'image en HTML pour ToolTip
            image_html = f"<img src='{self.popupImage}' style='max-width: 200px; max-height: 200px;'>"
            QToolTip.showText(QCursor.pos(), image_html, self)

    def leaveEvent(self, event):
        QToolTip.hideText()
                        
    #Apply the feedBack of a gameMechanics
    def feedBack(self, theAction):
        booleanForFeedback=True
        for anCondition in theAction.conditionOfFeedBack :
            booleanForFeedback=booleanForFeedback and anCondition(self)
        if booleanForFeedback :
            for aFeedback in  theAction.feedback :
                aFeedback(self)

    def addPovinMenuBar(self,nameOfPov):
        if nameOfPov not in self.model.listOfPovsForMenu :
            self.model.listOfPovsForMenu.append(nameOfPov)
            anAction=QAction(" &"+nameOfPov, self)
            self.model.povMenu.addAction(anAction)
            anAction.triggered.connect(lambda: self.model.displayPov(nameOfPov))


            

#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    def updateAgentByRecreating_it(self):
        aDestinationCell = self.cell
        self.cell.updateDepartureAgent(self)
        self.copyOfAgentAtCoord(aDestinationCell)
        self.deleteLater()

    # To copy an Agent to make a move
    def copyOfAgentAtCoord(self, aCell):
        oldAgent = self
        newAgent = SGAgent(aCell, oldAgent.size,oldAgent.dictAttributes,oldAgent.classDef.povShapeColor,oldAgent.classDef,oldAgent.defaultImage,oldAgent.popupImage)
        self.classDef.IDincr -=1
        newAgent.id = oldAgent.id
        newAgent.history = oldAgent.history
        newAgent.watchers = oldAgent.watchers
        #apply correction on the watchers on this entity
        for watchers in list(oldAgent.watchers.values()):
            for aWatcherOnThisAgent in watchers:
                aWatcherOnThisAgent.entity=newAgent        
        newAgent.privateID = oldAgent.privateID
        newAgent.isDisplay = oldAgent.isDisplay
        newAgent.classDef.entities.remove(oldAgent)
        newAgent.classDef.entities.append(newAgent)
        newAgent.update()
        newAgent.show()
        self.update()
        return newAgent
    

    def moveTo(self, aDestinationCell):
        if self.cell is None:
            self.cell = aDestinationCell
            self.cell.updateIncomingAgent(self)
            self.update()
            theAgent= self
        else :
            self.cell.updateDepartureAgent(self)
            theAgent= self.copyOfAgentAtCoord(aDestinationCell)
            self.deleteLater()
        return theAgent

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
        if self.cell is None:
            return []
        return self.cell.getAgents(specie)

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
        return self.cell.nbAgents(specie)

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
        return self.cell.hasAgents(specie)
    
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

    

    
    
                

        

