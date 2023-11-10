import random
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGModel import *
from PyQt5.QtWidgets import QAction
import copy

# Class who is responsible of the grid creation


class SGGrid(SGGameSpace):
    def __init__(self, parent, name, columns=10, rows=10,cellShape="square", gap=3, size=30, aColor=None, moveable=True):
        super().__init__(parent, 0, 60, 0, 0)
        # Basic initialize
        self.zoom = 1
        # self.parent=parent
        self.model = parent
        self.id = name
        self.columns = columns
        self.rows = rows
        self.cellShape = cellShape
        self.gap = gap
        self.size = size
        self.moveable = moveable
        self.rule = 'moore'

        self.currentPOV = {'Cell': {}, 'Agent': {}}

        self.saveGap = gap
        self.saveSize = size

        self.startXBase = 0
        self.startYBase = 0
        # random.seed(self.model.randomSeed)

        if aColor != "None":
            self.setColor(aColor)

        # We initialize the user interface related to the grid
        self.initCells()

    # Initialize the user interface
    def initCells(self):
        # Init the CellDef and Cells
        self.cellDef = self.model.newCellsFromGrid(self)

    # Drawing the game board with the cell
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
        # Base of the gameBoard
        if (self.cellShape == "square"):
            # We redefine the minimum size of the widget
            self.setMinimumSize(int(self.columns*self.size+(self.columns+1) *
                                self.gap+1)+3, int(self.rows*self.size+(self.rows+1)*self.gap)+3)
            painter.drawRect(0, 0, int(self.columns*self.size+(self.columns+1)
                             * self.gap+1), int(self.rows*self.size+(self.rows+1)*self.gap))
        elif (self.cellShape == "hexagonal"):
            self.setMinimumSize(int(self.columns*self.size+(self.columns+1)*self.gap+1)+int(
                self.size/2)+3,  int(self.size*0.75*self.rows + (self.gap * (self.rows + 1)) + self.size/4 + 3))
            painter.drawRect(0, 0, int(self.columns*self.size+(self.columns+1)*self.gap+1)+int(
                self.size/2),  int(self.size*0.75*self.rows + (self.gap * (self.rows + 1)) + self.size/4))
        painter.end()

    # Funtion to handle the zoom
    def zoomIn(self):
        self.zoom = self.zoom*1.1
        self.gap = round(self.gap+(self.zoom*1))
        self.size = round(self.size+(self.zoom*10))
        for cell in list(self.getCells()):
            cell.zoomIn()
            for agent in cell.getAgents():
                agent.zoomIn(self.zoom)
        self.update()

    def zoomOut(self):
        self.zoom = self.zoom*0.9
        self.size = round(self.size-(self.zoom*10))

        
        # if (self.gap > 2 and self.format == "square"):
        self.gap = round(self.gap-(self.zoom*1))
        for cell in self.getCells():
            cell.zoomOut()
        # else:
        #     self.gap = round(self.gap-(self.zoom*1))
        #     for cell in self.getCells():
        #         cell.zoomOut()
        # for cell in self.getCells():
        #     cell.zoomOut()
        for agent in cell.getAgents():
            agent.zoomOut(self.zoom)
        self.update()

    # To handle the drag of the grid
    def mouseMoveEvent(self, e):

        if self.moveable == False:
            return
        if e.buttons() != Qt.LeftButton:
            return

        # To get the clic position in GameSpace
        def getPos(e):
            clic = QMouseEvent.windowPos(e)
            xclic = int(clic.x())
            yclic = int(clic.y())
            return xclic, yclic

        # To get the coordinate of the grid upleft corner in GameSpace
        def getCPos(self):
            left = self.x()
            up = self.y()
            return left, up

        # To convert the upleft corner to center coordinates
        def toCenter(self, left, up):
            xC = int(left+(self.columns/2*self.size) +
                     ((self.columns+1)/2*self.gap))
            yC = int(up+(self.rows/2*self.size)+((self.rows+1)/2*self.gap))
            return xC, yC

        mimeData = QMimeData()
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.pos())

        xclic, yclic = getPos(e)
        left, up = getCPos(self)
        xC, yC = toCenter(self, left, up)

        drag.exec_(Qt.MoveAction)

        leftf, upf = getCPos(self)
        xCorr = xclic-xC
        yCorr = yclic-yC

        newX = leftf-xCorr
        newY = upf-yCorr

        self.move(newX, newY)

    # Funtion to have the global size of a gameSpace

    def getSizeXGlobal(self):
        if (self.cellShape == "square"):
            return int(self.columns*self.size+(self.columns+1)*self.gap+1)
        if (self.cellShape == "hexagonal"):
            return int(self.columns*self.size+(self.columns+1)*self.gap+1) + int(self.size/2)

    def getSizeYGlobal(self):
        if (self.cellShape == "square"):
            return int(self.rows*self.size+(self.rows+1)*self.gap)
        if (self.cellShape == "hexagonal"):
            return int((self.rows+1)*(self.size/3)*2) + self.gap*2

    # To get all the values possible for Legend

    def getValuesForLegend(self):
        return self.model.getCellPovs(self)

    # Agent function
    # To get all agents on the grid of a particular type
    def getAgentsOfType(self, aType):
        """OBSOLETE"""
        theList = []
        for aCell in self.collectionOfCells.cells:
            for anAgent in self.collectionOfCells.getCell(aCell).getAgentsOfType(aType):
                theList.append(anAgent)
        return theList

    # To initialise current POV

    def initCurrentPOV(self):
        """OBSOLETE"""
        for aCell in self.getCells():
            listcles = list(aCell.theCollection.povs.keys())
            self.currentPOV['Cell'] = aCell.theCollection.povs[listcles[0]]

        for animal, sub_dict in self.model.AgentSpecies.items():
            self.currentPOV['Agent'][animal] = sub_dict['POV'][list(
                sub_dict['POV'].keys())[0]]

        print(self.currentPOV)

    # To get the current POV

    def getCurrentPOV(self):
        """"
        OBSOLETE
        Get the actual POV displayed by the model for a grid        
        """
        for animal, sub_dict in self.model.AgentSpecies.items():
            for pov in sub_dict['POV'].items():
                if self.model.nameOfPov == pov:
                    self.currentPOV['Agent'][animal] = pov
        for aCell in self.getCells():
            for pov in aCell.theCollection.povs:
                if self.model.nameOfPov == pov:
                    self.currentPOV['Cell'] = aCell.theCollection.povs[pov]

        print(self.currentPOV)
        return self.currentPOV
    
    def removeVisiblityCell(self,aCellID):
        self.getCell_withId(self,aCellID).isDisplay = False
        self.update()

# -----------------------------------------------------------------------------------------
# Definiton of the methods who the modeler will use

    # Return all the cells
    def getCells(self):
        return self.model.getCells(self)

    # Return the cell
    def getCell_withId(self, aGrid, aCellID):
        return self.model.getCell(self,aCellID)

    def getFirstCell(self):
        return self.getCell_withId("cell1-1")


   # Return the cells at a specified column
    def getCells_withColumn(self, columnNumber):
        """
        Return the cells at a specified column.
        args:
            columnNumber (int): column number
        """
        return [ cell for cell in self.model.getCells(self) if cell.x== columnNumber]
        

  # Return the cells at a specified row
    def getCells_withRow(self, rowNumber):
        """
        Return the cells at a specified column.
        args:
            rowNumber (int): row number
        """
        return [ cell for cell in self.model.getCells(self) if cell.y== rowNumber]



    # To define a value for all Agents
    def setValueForAgents(self, typeOfAgent, aDictWithValue):
        """NOT TESTED"""
        for aCell in self.getCells():
            for anAgent in aCell.getAgentsOfType(typeOfAgent):
                for aVal in list(aDictWithValue.keys()):
                    if aVal in list(anAgent.theCollection.povs[self.model.nameOfPov].keys()):
                        for anAttribute in list(anAgent.theCollection.povs[self.model.nameOfPov].keys()):
                            anAgent.attributs.pop(anAttribute, None)
                anAgent.attributs[list(aDictWithValue.keys())[
                    0]] = aDictWithValue[list(aDictWithValue.keys())[0]]

    # To define a value for the model of an Agent
    def setValueForModelAgents(self, typeOfAgent, aDictWithValue):
        """NOT TESTED"""
        anAgent = self.collectionOfAcceptAgent[typeOfAgent]
        # On cherche la pov et on suppr les valeur deja existante de la pov
        for aPov in list(anAgent.theCollection.povs.keys()):
            if list(aDictWithValue.keys())[0] in list(anAgent.theCollection.povs[aPov].keys()):
                for anAttribut in list(anAgent.theCollection.povs[aPov].keys()):
                    anAgent.attributs.pop(anAttribut, None)
        anAgent.attributs[list(aDictWithValue.keys())[
            0]] = aDictWithValue[list(aDictWithValue.keys())[0]]

    # To define a value for all Agents of a cell
    def setValueAgentsOnCell(self, typeOfAgent, aDictWithValue, aCellId):
        """NOT TESTED"""
        aCell = self.getCell_withId(aCellId)
        for anAgent in aCell.collectionOfAgents.agents:
            if anAgent.format == typeOfAgent:
                # On cherche la pov et on suppr les valeur deja existante de la pov
                for aPov in list(anAgent.theCollection.povs.keys()):
                    if list(aDictWithValue.keys())[0] in list(anAgent.theCollection.povs[aPov].keys()):
                        for anAttribut in list(anAgent.theCollection.povs[aPov].keys()):
                            anAgent.attributs.pop(anAttribut, None)
                anAgent.attributs[list(aDictWithValue.keys())[
                    0]] = aDictWithValue[list(aDictWithValue.keys())[0]]

    # To change the value of an unique agent on a cell
    def setForAnAgentOfCell(self, typeOfAgent, aDictWithValue, aCellId):
        """NOT TESTED"""
        aCell = self.getCell_withId(aCellId)
        for anAgent in aCell.collectionOfAgents.agents:
            if anAgent.name == typeOfAgent:
                # On cherche la pov et on suppr les valeur deja existante de la pov
                for aPov in list(anAgent.theCollection.povs.keys()):

                    if list(aDictWithValue.keys())[0] in list(anAgent.theCollection.povs[aPov].keys()):
                        for anAttribut in list(anAgent.theCollection.povs[aPov].keys()):
                            if anAttribut == list(aDictWithValue.keys())[0]:
                                if anAgent.attributs[anAttribut] == list(aDictWithValue.values())[0]:
                                    continue
                                else:
                                    anAgent.attributs.pop(anAttribut, None)
                                    anAgent.attributs[list(aDictWithValue.keys())[
                                        0]] = aDictWithValue[list(aDictWithValue.keys())[0]]
                                    return True
                            else:
                                anAgent.attributs.pop(anAttribut, None)
                                anAgent.attributs[list(aDictWithValue.keys())[
                                    0]] = aDictWithValue[list(aDictWithValue.keys())[0]]
                                return True
        return False

    # To grow all attributs of cells of one type
    def makeEvolve(self, listOfAttributsToMakeEvolve):
        """NOT TESTED"""
        for aCell in self.getCells():
            for anAttribut in listOfAttributsToMakeEvolve:
                if anAttribut in list(aCell.attributs.keys()):
                    for aPov in aCell.theCollection.povs:
                        found = list(aCell.theCollection.povs[aPov][anAttribut].keys()).index(
                            aCell.attributs[anAttribut])
                        if found != -1 and found+1 != len(aCell.theCollection.povs[aPov][anAttribut]):
                            if len(self.history["value"]) == 0:
                                self.history["value"].append(
                                    [0, 0, self.attributs])
                            aCell.attributs[anAttribut] = list(
                                aCell.theCollection.povs[aPov][anAttribut].keys())[found+1]
                            # self.history["value"].append([self.parent.parent.parent.timeManager.actualRound,self.parent.parent.parent.actualPhase,self.attributs])

    # To decrease all attributs of cells of one type
    def makeDecrease(self, listOfAttributsToMakeDecrease):
        """NOT TESTED"""
        for aCell in self.getCells():
            for anAttribut in listOfAttributsToMakeDecrease:
                if anAttribut in list(aCell.attributs.keys()):
                    for aPov in aCell.theCollection.povs:
                        found = list(aCell.theCollection.povs[aPov][anAttribut].keys()).index(
                            aCell.attributs[anAttribut])
                        if found != -1 and found != 0:
                            if len(self.history["value"]) == 0:
                                self.history["value"].append(
                                    [0, 0, self.attributs])
                            aCell.attributs[anAttribut] = list(
                                aCell.theCollection.povs[aPov][anAttribut].keys())[found-1]
                            # self.history["value"].append([self.parent.parent.parent.timeManger.actualRound,self.parent.parent.parent.actualPhase,self.attributs])

    # to get all cells who respect certain value
    def nbCells_withValue(self, att, value):
        return len(self.getEntities_withValue(att, value))

    # To return all agent of a type in neighborhood
    def getNeighborAgent(self, x, y, agentName, typeNeighbor="moore", rangeNeighbor=1):
        """NOT TESTED"""
        x = x-1
        y = y-1
        result = []
        for cell in self.getCell_withId("cell"+str(x)+"-"+str(y)).getNeighborCell(typeNeighbor, rangeNeighbor):
            for agent in cell.getAgentsOfType(agentName):
                result.append(agent)
        return result

    # To return if a type of agent is in neighborhood
    def haveAgentInNeighborhood(self, x, y, agentName, typeNeighbor="moore", rangeNeighbor=1):
        """NOT TESTED"""
        return len(self.getNeighborAgent(x, y, agentName, typeNeighbor, rangeNeighbor)) >= 1

    # To return all agent in neighborhood
    def getNeighborAllAgent(self, x, y, typeNeighbor="moore", rangeNeighbor=1):
        """NOT TESTED"""
        x = x-1
        y = y-1
        result = []
        for cell in self.getCell_withId("cell"+str(x)+"-"+str(y)).getNeighborCell(typeNeighbor, rangeNeighbor):
            for agentName in list(self.collectionOfAcceptAgent.keys()):
                for agent in cell.getAgentsOfType(agentName):
                    result.append(agent)
        return result

    # To return all agent of a type in neighborhood
    def getNeighborAgentThroughCell(self, aCell, agentName, typeNeighbor="moore", rangeNeighbor=1):
        """NOT TESTED"""
        x = aCell.x
        y = aCell.y
        result = []
        for cell in self.getCell_withId("cell"+str(x)+"-"+str(y)).getNeighborCell(typeNeighbor, rangeNeighbor):
            for agent in cell.getAgentsOfType(agentName):
                result.append(agent)
        return result

    # To return if a type of agent is in neighborhood through a cell
    def haveAgentInNeighborhoodThroughCell(self, aCell, agentName, typeNeighbor="moore", rangeNeighbor=1):
        """NOT TESTED"""
        return len(self.getNeighborAgentThroughCell(aCell, agentName, typeNeighbor, rangeNeighbor)) >= 1

    # To return all agent in neighborhood through a cell
    def getNeighborAllAgentThroughCell(self, aCell, typeNeighbor="moore", rangeNeighbor=1):
        """NOT TESTED"""
        x = aCell.x
        y = aCell.y
        result = []
        for cell in self.getCell_withId("cell"+str(x)+"-"+str(y)).getNeighborCell(typeNeighbor, rangeNeighbor):
            for agentName in list(self.collectionOfAcceptAgent.keys()):
                for agent in cell.getAgentsOfType(agentName):
                    result.append(agent)
        return result

    # To check if the grid have agent
    def haveAgents(self):
        """NOT TESTED"""
        for cell in self.getCells():
            if len(cell.collectionOfAgents.agents) != 0:
                return True
        return False

    def cellsDo(self, aLambdaFunction):
        for aCell in self.getCells():
            aCell.doAction(aLambdaFunction)
