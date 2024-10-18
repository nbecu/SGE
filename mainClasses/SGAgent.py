from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog, QMessageBox
import random
from mainClasses.SGEntity import SGEntity
   
#Class who is responsible of the declaration a Agent
class SGAgent(SGEntity):
    def __init__(self,cell,size,attributesAndValues,shapeColor,classDef,defaultImage):
        aGrid = cell.grid
        super().__init__(aGrid,classDef, size,attributesAndValues)
        self.cell=None
        if cell is not None:
            self.cell = cell
            self.cell.updateIncomingAgent(self)
        else: raise ValueError('This case is not handeled')
        self.getPositionInEntity()
        self.last_selected_option=None
        self.initMenu()
        self.defaultImage=defaultImage
        


    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        region = self.getRegion()
        if self.defaultImage != None:
            rect = QRect(0, 0, self.width(), self.height())
            painter.setClipRegion(region)
            painter.drawPixmap(rect, self.defaultImage)
        else : painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
        agentShape = self.classDef.shape
        x = self.xPos
        y = self.yPos
        if self.isDisplay==True:
            if(agentShape=="circleAgent"):
                self.setGeometry(x,y,self.size+1,self.size+1)
                painter.drawEllipse(0,0,self.size,self.size)
            elif agentShape=="squareAgent":
                self.setGeometry(x,y,self.size+1,self.size+1)
                painter.drawRect(0,0,self.size,self.size)
            elif agentShape=="ellipseAgent1": 
                self.setGeometry(x,y,self.size*2+1,self.size+1)
                painter.drawEllipse(0,0,self.size*2,self.size)
            elif agentShape=="ellipseAgent2": 
                self.setGeometry(x,y,self.size+1,self.size*2+1)
                painter.drawEllipse(0,0,self.size,self.size*2)
            elif agentShape=="rectAgent1": 
                self.setGeometry(x,y,self.size*2+1,self.size+1)
                painter.drawRect(0,0,self.size*2,self.size)
            elif agentShape=="rectAgent2": 
                self.setGeometry(x,y,self.size+1,self.size*2+1)
                painter.drawRect(0,0,self.size,self.size*2)
            elif agentShape=="triangleAgent1": 
                self.setGeometry(x,y,self.size+1,self.size+1)
                points = QPolygon([
                QPoint(round(self.size/2),0),
                QPoint(0,self.size),
                QPoint(self.size,  self.size)
                ])
                painter.drawPolygon(points)
            elif agentShape=="triangleAgent2": 
                self.setGeometry(x,y,self.size+1,self.size+1)
                points = QPolygon([
                QPoint(0,0),
                QPoint(self.size,0),
                QPoint(round(self.size/2),self.size)
                ])
                painter.drawPolygon(points)
            elif agentShape=="arrowAgent1": 
                self.setGeometry(x,y,self.size+1,self.size+1)
                points = QPolygon([
                QPoint(round(self.size/2),0),
                QPoint(0,self.size),
                QPoint(round(self.size/2),round(self.size/3)*2),
                QPoint(self.size,  self.size)
                ])
                painter.drawPolygon(points)
            elif agentShape=="arrowAgent2": 
                self.setGeometry(x,y,self.size+1,self.size+1)
                points = QPolygon([
                QPoint(0,0),
                QPoint(round(self.size/2),round(self.size/3)),
                QPoint(self.size,0),
                QPoint(round(self.size/2),self.size)
                ])
                painter.drawPolygon(points)
            elif agentShape == "hexagonAgent":
                self.setGeometry(x, y, self.size+1, self.size+1)
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
            region = QRegion(0, 0, self.size+1, self.size+1)
        elif agentShape=="ellipseAgent1": 
            region = QRegion(0,0,self.size*2,self.size)
        elif agentShape=="ellipseAgent2": 
            region = QRegion(0,0,self.size,self.size*2)
        elif agentShape=="rectAgent1": 
            region = QRegion(0,0,self.size*2,self.size)
        elif agentShape=="rectAgent2": 
            region = QRegion(0,0,self.size,self.size*2)
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
            
    def initMenu(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)

    # To show a menu
    def show_menu(self, point):
        menu = QMenu(self)
        options=[]

        for anItem in self.classDef.attributesToDisplayInContextualMenu:
            aAtt = anItem['att']
            aLabel = anItem['label']
            aValue = self.value(aAtt)
            text = aLabel  + ": "+str(aValue)
            option = QAction(text, self)
            menu.addAction(option)
        
        if self.classDef.updateMenu:
            if len(self.classDef.attributesToDisplayInUpdateMenu)==1:  
                anItem=self.classDef.attributesToDisplayInUpdateMenu[0]
                aAtt = anItem['att']
                aLabel = anItem['label']
                aValue = self.value(aAtt)
                text="Value - "+aLabel + ": "+str(aValue)
                gearAct = QAction(text, self)
                gearAct.setCheckable(False)
                menu.addAction(gearAct)
                options.append(gearAct)

            if len(self.classDef.attributesToDisplayInUpdateMenu)>1:
                gearMenu=menu.addMenu('Values')
                for anItem in self.classDef.attributesToDisplayInUpdateMenu:
                    aAtt = anItem['att']
                    aLabel = anItem['label'] 
                    aValue = self.value(aAtt)
                    text = aAtt+" " +aLabel+" : "+str(aValue)
                    option = QAction(text, self)
                    option.setCheckable(False) 
                    gearMenu.addAction(option)
                    options.append(option)

        if self.rect().contains(point):
            action=menu.exec_(self.mapToGlobal(point))
            if action in options:
                self.showGearMenu(action.text()) 

    def showGearMenu(self,aText):
        # Get the actions from the player
        player=self.model.getPlayer(self.model.currentPlayer)
        if player == "Admin":
            return
        actions = player.getGameActionsOn(self)
        actionsNames =[action.name for action in actions]
        # Filter the actions by the concerned attribute
        displayedNames=[]
        wordsInText=aText.split()
        att=wordsInText[0]
        for aName in actionsNames:
            wordsInName=aName.split()
            if att in wordsInName:
                displayedNames.append(aName)
        # The first value is the current value
        current_value = self.value(att)
        displayedValues=[aName.split()[-1] for aName in displayedNames]
        default_index = displayedValues.index(current_value) if current_value in displayedValues else 0
        # Dialog box
        action, ok = QInputDialog.getItem(self, 'Change Value','Select a NEW Value for '+att, displayedValues, default_index, False)

        if ok and action:
            self.last_selected_option = action
            self.showPopup(action)
            # now execute Actions
            actionName="UpdateAction "+att+" "+action
            for anAction in actions:
                if anAction.name==actionName:
                    anAction.perform_with(self)

    def showPopup(self, selected_option):
        QMessageBox.information(self, 'Option selected', f'You chose : {selected_option}', QMessageBox.Ok)
        
    def getRandomX(self):        
        maxSize=self.cell.size
        originPoint=self.cell.pos()
        x = random.randint(originPoint.x()+5,originPoint.x()+maxSize-10)
        return x
        
    
    def getRandomY(self): 
        maxSize=self.cell.size
        originPoint=self.cell.pos()
        y = random.randint(originPoint.y()+5,originPoint.y()+maxSize-10)
        return y
    
    def getPositionInEntity(self):
        maxSize=self.cell.size
        originPoint=self.cell.pos()
        if self.classDef.locationInEntity=="random":
            self.xPos=self.getRandomX()
            self.yPos=self.getRandomY()
            return
        if self.classDef.locationInEntity=="topRight":
            self.xPos=originPoint.x()+maxSize-10
            self.yPos=originPoint.y()+5
            return
        if self.classDef.locationInEntity=="topLeft":
            self.xPos=originPoint.x()+5
            self.yPos=originPoint.y()+5
            return
        if self.classDef.locationInEntity=="bottomLeft":
            self.xPos=originPoint.x()+5
            self.yPos=originPoint.y()+maxSize-10
            return
        if self.classDef.locationInEntity=="bottomRight":
            self.xPos=originPoint.x()+maxSize-10
            self.yPos=originPoint.y()+maxSize-10
            return
        if self.classDef.locationInEntity=="center":
            self.xPos=originPoint.x()+int(maxSize/2)-int(self.size/2)
            self.yPos=originPoint.y()+int(maxSize/2)-int(self.size/2)
            return
        else:
            raise ValueError("Error in entry for locationInEntity")

    def isDeleted(self):
        if not self.isDisplay:
            raise ValueError ('An agent which is not displayed is not necessary deleted.') 
        return not self.isDisplay
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
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


    def dropEvent(self, e):
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
        newAgent = SGAgent(aCell, oldAgent.size,oldAgent.dictAttributes,oldAgent.classDef.povShapeColor,oldAgent.classDef,oldAgent.defaultImage)
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

    def moveAgent(self,method="random",direction=None,cellID=None,numberOfMovement=1):
        """
        Model action to move an Agent.

        args:
            method (str): random, cell, cardinal
            direction (str): if cardinal; North, South, West, East
            cellID (str): if cell; cellx-y
            numberOfMouvement (int): number of movement in one action
        """
        for i in range(numberOfMovement):

            if i>0:
                oldAgent=theAgent
                originCell=oldAgent.cell
            else:
                oldAgent=self
                originCell=self.cell

            aGrid=originCell.grid

            if method == "random":
                neighbors=originCell.getNeighborCells(aGrid.rule)
                newCell=random.choice(neighbors)

            if method == "cell" or cellID is not None:
                newCell=aGrid.getCell_withId(cellID)

            if method == "cardinal" or direction is not None:
                if direction =="North":
                    newCell=originCell.getNeighborN()
                if direction =="South":
                    newCell=originCell.getNeighborS()
                if direction =="East":
                    newCell=originCell.getNeighborE()
                if direction =="West":
                    newCell=originCell.getNeighborW()
            
            if newCell is None:
                pass
            else:
                theAgent = self.moveTo(newCell)
        pass
                    
    def getId(self):
        return self.id
    
    def getPrivateId(self):
        return self.privateID 
    
    def getNeighborAgents(self,rule='moore',aSpecies=None):
        neighbors=[]
        if rule=="moore":
            neighborCells=self.cell.getNeighborCells()
        elif rule=='neumann':
            neighborCells=self.cell.getNeighborCells(rule='neumann')
        else:
            print('Error in rule specification')
        
        neighbors=[aCell.agents for aCell in neighborCells]
        
        if aSpecies:
            return self.sortBySpecies(aSpecies,neighbors)
        return neighbors
    
    def sortBySpecies(self,aSpecies,agents):
        sortedAgents=[]
        if len(agents)!=0:
            for aAgent in agents:
                if aAgent.classDef == aSpecies or aAgent.classDef.entityName == aSpecies:
                    aAgent.append(sortedAgents)
        return sortedAgents
    
    def nbNeighborAgents(self,rule='moore',aSpecies=None):  
        if aSpecies:
            return len(self.getNeighborAgentsBySpecies(aSpecies,rule))
        return len(self.getNeighborAgents(rule))

    def getNeighborsN(self,aSpecies=None):
        theCell=self.cell.getNeighborN()
        if aSpecies:
            return self.sortBySpecies(aSpecies,theCell.agents)
        return theCell.agents
    
    def getNeighborsS(self,aSpecies=None):
        theCell=self.cell.getNeighborS()
        if aSpecies:
            return self.sortBySpecies(aSpecies,theCell.agents)
        return theCell.agents
    
    def getNeighborsE(self,aSpecies=None):
        theCell=self.cell.getNeighborE()
        if aSpecies:
            return self.sortBySpecies(aSpecies,theCell.agents)
        return theCell.agents
    
    def getNeighborsW(self,aSpecies=None):
        theCell=self.cell.getNeighborW()
        if aSpecies:
            return self.sortBySpecies(aSpecies,theCell.agents)
        return theCell.agents

    

    
    
                

        

