import random
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGAgent import SGAgent


from PyQt5.QtWidgets import QAction

import copy

# Class who is responsible of the grid creation


class SGGrid(SGGameSpace):
    def __init__(self, parent, name, rows=8, columns=8, format="square", gap=3, size=30, aColor=None, moveable=True):
        super().__init__(parent, 0, 60, 0, 0)
        # Basic initialize
        self.zoom = 1
        # self.parent=parent
        self.model = parent
        self.id = name
        self.rows = rows
        self.columns = columns
        self.format = format
        self.gap = gap
        self.size = size
        self.moveable = moveable
        self.rule = 'moore'

        self.currentPOV = {'Cell': {}, 'Agent': {}}

        self.saveGap = gap
        self.saveSize = size

        self.startXBase = 0
        self.startYBase = 0
        random.seed(self.model.randomSeed)

        if aColor != "None":
            self.setColor(aColor)

        # We initialize the user interface related to the grid
        self.initUI()

    # Initialize the user interface
    def initUI(self):
        # Init the cellCollection
        self.myCollectionOfCells = self.model.newCellCollection(self,self.columns, self.rows, self.format, self.size, self.gap)

    # Drawing the game board with the cell

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
        # Base of the gameBoard
        if (self.format == "square"):
            # We redefine the minimum size of the widget
            self.setMinimumSize(int(self.columns*self.size+(self.columns+1) *
                                self.gap+1)+3, int(self.rows*self.size+(self.rows+1)*self.gap)+3)
            painter.drawRect(0, 0, int(self.columns*self.size+(self.columns+1)
                             * self.gap+1), int(self.rows*self.size+(self.rows+1)*self.gap))
        elif (self.format == "hexagonal"):
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
        if (self.format == "square"):
            return int(self.columns*self.size+(self.columns+1)*self.gap+1)
        if (self.format == "hexagonal"):
            return int(self.columns*self.size+(self.columns+1)*self.gap+1) + int(self.size/2)

    def getSizeYGlobal(self):
        if (self.format == "square"):
            return int(self.rows*self.size+(self.rows+1)*self.gap)
        if (self.format == "hexagonal"):
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

    # Return the cell at specified coordinates
    def getCell(self, x, y):
        """
        Return a cell with column and row number.
        args:
            x (int): column number
            y (int): row number
        """
        if x < 1 or x > self.columns or y < 1 or y > self.rows:
            return None
        return self.getCell_withId(self,"cell"+str(x)+'-'+str(y))

   # Return the cells at a specified column
    def getCells_withColumn(self, columnNumber):
        """
        Return the cells at a specified column.
        args:
            columnNumber (int): column number
        """
        litsOfCells = []
        for i in range(1, self.rows + 1):
            litsOfCells.append(self.getCell(columnNumber, i))
        return litsOfCells

  # Return the cells at a specified row
    def getCells_withRow(self, rowNumber):
        """
        Return the cells at a specified column.
        args:
            rowNumber (int): row number
        """
        litsOfCells = []
        for i in range(1, self.rows + 1):
            litsOfCells.append(self.getCell(i, rowNumber))
        return litsOfCells

# to get all cells with a certain value
    def getCells_withValue(self, att, val):
        litsOfCells = []
        for cell in list(self.collectionOfCells.cells.values()):
            if att in cell.attributs:
                if val == cell.attributs[att]:
                    litsOfCells.append(cell)
        return litsOfCells

# to get all cells not having a certain value
    def getCells_withValueNot(self, att, val):
        litsOfCells = []
        for cell in list(self.collectionOfCells.cells.values()):
            if att in cell.attributs:
                if val != cell.attributs[att]:
                    litsOfCells.append(cell)
        return litsOfCells

  # Return a random cell
    def getRandomCell(self, condition=None, listOfEntitiesToPickFrom=None):
        """
        Return a random cell.
        """
        if listOfEntitiesToPickFrom == None:
            listOfEntitiesToPickFrom = self.getCells()
        if condition == None:
            listOfEntities = listOfEntitiesToPickFrom
        else:
            listOfEntities = []
            for aEntity in listOfEntitiesToPickFrom:
                if aEntity.testCondition(condition):
                    listOfEntities.append(aEntity)
        if listOfEntities == []:
            return False
        else:
            return random.choice(listOfEntities)

   # Return a random cell with a certain value
    def getRandomCell_withValue(self, att, val, condition=None):
        """
        Return a random cell.
        """
        return self.getRandomCell(condition=condition, listOfEntitiesToPickFrom=self.getCells_withValue(att, val))

        # if condition == None:
        #     listOfCells = self.getCells_withValue(att,val)
        # else:
        #     listOfCells =[]
        #     for aCell in self.getCells_withValue(att,val):
        #         if aCell.testCondition(condition):
        #              listOfCells.append(aCell)
        # return random.choice(listOfCells)

  # Return a random cell not having a certain value
    def getRandomCell_withValueNot(self, att, val, condition=None):
        """
        Return a random cell.
        """
        return self.getRandomCell(condition=condition, listOfEntitiesToPickFrom=self.getCells_withValueNot(att, val))

    def getRandomCells(self, aNumber, condition=None, listOfEntitiesToPickFrom=None):
        """
        Return a specified number of random cells.
        args:
            aNumber (int): a number of cells to be randomly selected
        """
        if listOfEntitiesToPickFrom == None:
            listOfEntitiesToPickFrom = self.getCells()
        if condition == None:
            listOfEntities = listOfEntitiesToPickFrom
        else:
            listOfEntities = []
            for aEntity in listOfEntitiesToPickFrom:
                if aEntity.testCondition(condition):
                    listOfEntities.append(aEntity)
        if len(listOfEntities) < aNumber:
            return listOfEntities
        else:
            return random.sample(listOfEntities, aNumber)

  # Return random cells
    # def getRandomCells(self,aNumber, condition=None):
    #     """
    #     Return a specified number of random cells.
    #     args:
    #         aNumber (int): a number of cells to be randomly selected
    #     """
    #     if condition == None:
    #         listOfCells = self.getCells()
    #     else:
    #         listOfCells =[]
    #         for aCell in self.getCells():
    #             if aCell.testCondition(condition):
    #                  listOfCells.append(aCell)
    #     if listOfCells == []:
    #         return []
    #     else:
    #         return random.sample(listOfCells,aNumber)

    # Return random cells with a certain value
    def getRandomCells_withValue(self, aNumber, att, val, condition=None):
        """
        Return a specified number of random cells.
        args:
            aNumber (int): a number of cells to be randomly selected
        """
        return self.getRandomCells(aNumber, condition=condition, listOfEntitiesToPickFrom=self.getCells_withValue(att, val))

    # Return random cells not having a certain value
    def getRandomCells_withValueNot(self, aNumber, att, val, condition=None):
        """
        Return a specified number of random cells.
        args:
            aNumber (int): a number of cells to be randomly selected
        """
        return self.getRandomCells(aNumber, condition=condition, listOfEntitiesToPickFrom=self.getCells_withValueNot(att, val))
        # if condition == None:
        #     listOfCells = self.getCells_withValueNot(att,val)
        # else:
        #     listOfCells =[]
        #     for aCell in self.getCells_withValueNot(att,val):
        #         if aCell.testCondition(condition):
        #              listOfCells.append(aCell)
        # if listOfCells == []:
        #     return []
        # else:
        #     return random.sample(listOfCells,aNumber)


# To handle POV and placing on cell
    # To define a value for all cells


    def setCells(self, aAttribute, aValue):
        """
        Set the value of attribut value of all cells

        Args:
            aAttribute (str): Name of the attribute to set
            aValue (str): Value to set the attribute to
        """
        for aCell in self.getCells():
            aCell.setValue(aAttribute, aValue)

    # OLD METHOD
    # def setValueCells(self,aAttribut,aValue):
    #     """
    #     Applies the same attribut value (and color) for all the cells

    #     Args:
    #         aAttribut (str): Name of the attribute to set
    #         aValue (str): Value to set the attribute to
    #     """
    #     aDictWithValue={aAttribut:aValue}
    #     for aCell in list(self.getCells()):
    #         for aVal in list(aDictWithValue.keys()) :
    #             if len(aCell.theCollection.povs) !=0:
    #                 if aVal in list(aCell.theCollection.povs[self.model.nameOfPov].keys()) :
    #                         for anAttribute in list(aCell.theCollection.povs[self.model.nameOfPov].keys()):
    #                             aCell.attributs.pop(anAttribute,None)

    #         aCell.attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]

    def setCell(self, aAttribute, aValue, aValueX, aValueY):
        """
        set the value of attribute value for a specific cell

        Args:
            aAttribute (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
            aValueX (int): a column number
            aValueY (int): a row number
        """
        self.getCell(aValueX, aValueY).setValue(aAttribute, aValue)

     # OLD METHOD
   # #To apply to a specific cell a value
    # def setForXandY(self,aAttribut,aValue,aValueX,aValueY):
    #     """
    #     set the value of attribut value for a specific cell

    #     Args:
    #         aAttribut (str): Name of the attribute to set.
    #         aValue (str): Value to set the attribute to
    #         aValueX (int): a row number
    #         aValueY (int): a column number

    #     """
    #     aDictWithValue={aAttribut:aValue}
    #     for aVal in list(aDictWithValue.keys()) :
    #         if len(self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(aValueY-1)).theCollection.povs) !=0:
    #             if aVal in list(self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(aValueY-1)).theCollection.povs[self.model.nameOfPov].keys()) :
    #                 for anAttribute in list(self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(aValueY-1)).theCollection.povs[self.model.nameOfPov].keys()):
    #                     self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(aValueY-1)).attributs.pop(anAttribute,None)
    #     self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(aValueY-1)).attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]

    # set the value of attribut to all cells in a specified column
    def setCells_withColumn(self, aAttribute, aValue, aColumnNumber):
        """
        Set the value of attribut to all cells in a specified column

        Args:
            aAttribute (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
            aColumnNumber (int): a column number

        """
        for aCell in self.getCells_withColumn(aColumnNumber):
            aCell.setValue(aAttribute, aValue)

    # set the value of attribut to all cells in a specified row
    def setCells_withRow(self, aAttribute, aValue, aRowNumber):
        """
        Set the value of attribut to all cells in a specified row

        Args:
            aAttribute (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
            aRowNumber (int): a row number

        """
        for aCell in self.getCells_withRow(aRowNumber):
            aCell.setValue(aAttribute, aValue)

    # OLD METHOD
    #   def setCells_withColumn(self,aAttribut,aValue,aValueX):
    #     """
    #     Set the value of attribut of cells in a specific column

    #     Args:
    #         aAttribut (str): Name of the attribute to set.
    #         aValue (str): Value to set the attribute to
    #         aValueX (int): a column number

    #     """
    #     aDictWithValue={aAttribut:aValue}
    #     for y in range(self.rows):
    #         if len(self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(y)).theCollection.povs) !=0:
    #             for aVal in list(aDictWithValue.keys()) :
    #                 if aVal in list(self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(y)).theCollection.povs[self.model.nameOfPov].keys()) :
    #                     for anAttribute in list(self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(y)).theCollection.povs[self.model.nameOfPov].keys()):
    #                         self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(y)).attributs.pop(anAttribute,None)
    #         self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(y)).attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]

    # To apply to a all column of cell a value
    # def setCells_withRow(self,aAttribut,aValue,aValueY):
    #     """
    #     Set the value of attribut of cells in a specific row

    #     Args:
    #         aAttribut (str): Name of the attribute to set.
    #         aValue (str): Value to set the attribute to
    #         aValueY (int): a row number

    #     """
    #     aDictWithValue={aAttribut:aValue}
    #     for x in range(self.columns):
    #         for aVal in list(aDictWithValue.keys()) :
    #             if len(self.collectionOfCells.getCell("cell"+str(x)+"-"+str(aValueY-1)).theCollection.povs) !=0:
    #                 if aVal in list(self.collectionOfCells.getCell("cell"+str(x)+"-"+str(aValueY-1)).theCollection.povs[self.model.nameOfPov].keys()) :
    #                     for anAttribute in list(self.collectionOfCells.getCell("cell"+str(x)+"-"+str(aValueY-1)).theCollection.povs[self.model.nameOfPov].keys()):
    #                         self.collectionOfCells.getCell("cell"+str(x)+"-"+str(aValueY-1)).attributs.pop(anAttribute,None)
    #         self.collectionOfCells.getCell("cell"+str(x)+"-"+str(aValueY-1)).attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]

    # To apply a value to a random cell
    def setRandomCell(self, aAttribute, aValue, condition=None):
        """
        Apply a value to a random cell

        Args:
            aAttribute (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
        """
        self.getRandomCell(condition=condition).setValue(aAttribute, aValue)

    # To apply a value to a random cell with a certain value
    def setRandomCell_withValue(self, aAttribut, aValue, conditionAtt, conditionVal, condition=None):
        """
        To apply a value to a random cell with a certain value

        Args:
            aAttribut (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
        """
        self.getRandomCell_withValue(
            conditionAtt, conditionVal, condition).setValue(aAttribut, aValue)

   # To apply a value to a random cell not having a certain value
    def setRandomCell_withValueNot(self, aAttribut, aValue, conditionAtt, conditionVal, condition=None):
        """
       To apply a value to a random cell not having a certain value

        Args:
            aAttribut (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
        """
        self.getRandomCell_withValueNot(
            conditionAtt, conditionVal, condition).setValue(aAttribut, aValue)

    # To apply a value to some random cell
    def setRandomCells(self, aAttribute, aValue, numberOfCells, condition=None):
        """
        Applies the same attribut value for a random number of cells

        Args:
            aAttribute (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
            numberOfCells (int): number of cells
        """
        aList = self.getRandomCells(numberOfCells, condition)
        if aList == []:
            return False
        for aCell in aList:
            aCell.setValue(aAttribute, aValue)

    # To apply a value to some random cells with a certain value
    def setRandomCells_withValue(self, aAttribut, aValue, numberOfCells, conditionAtt, conditionVal, condition=None):
        """
        To apply a value to some random cells with a certain value

        Args:
            aAttribut (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
            numberOfCells (int): number of cells
        """
        for aCell in self.getRandomCells_withValue(numberOfCells, conditionAtt, conditionVal, condition):
            aCell.setValue(aAttribut, aValue)

   # To apply a value to some random cells noty having a certain value
    def setRandomCells_withValueNot(self, aAttribut, aValue, numberOfCells, conditionAtt, conditionVal, condition=None):
        """
        To apply a value to some random cells noty having a certain value

        Args:
            aAttribut (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
            numberOfCells (int): number of cells
        """
        for aCell in self.getRandomCells_withValueNot(numberOfCells, conditionAtt, conditionVal, condition):
            aCell.setValue(aAttribut, aValue)

    # OLD METHOD
#    def setRandomCells(self,aAttribut,aValue,numberOfRandom):
#         """
#         Applies the same attribut value (and color) for a random number of cells

#         Args:
#             aAttribut (str): Name of the attribute to set.
#             aValue (str): Value to set the attribute to
#             numberOfRandom (int): number of cells
#         """
#         aDictWithValue={aAttribut:aValue}
#         alreadyDone=list()
#         while len(alreadyDone)!=numberOfRandom:
#             aValueX=random.randint(0, self.columns-1)
#             aValueY=random.randint(0, self.rows-1)
#             if (aValueX,aValueY) not in alreadyDone:
#                 alreadyDone.append((aValueX,aValueY))
#                 for aVal in list(aDictWithValue.keys()) :
#                     if len(self.collectionOfCells.getCell("cell"+str(aValueX)+"-"+str(aValueY)).theCollection.povs) !=0:
#                         if aVal in list(self.collectionOfCells.getCell("cell"+str(aValueX)+"-"+str(aValueY)).theCollection.povs[self.model.nameOfPov].keys()) :
#                             for anAttribute in list(self.collectionOfCells.getCell("cell"+str(aValueX)+"-"+str(aValueY)).theCollection.povs[self.model.nameOfPov].keys()):
#                                 self.collectionOfCells.getCell("cell"+str(aValueX)+"-"+str(aValueY)).attributs.pop(anAttribute,None)
#                 self.collectionOfCells.getCell("cell"+str(aValueX)+"-"+str(aValueY)).attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]

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
    def getCellOfValue(self, aDictValueForAgent):
        """NOT TESTED"""
        result = []
        for cell in list(self.collectionOfCells.cells.values()):
            aKey = list(aDictValueForAgent.keys())[0]
            if aKey in cell.attributs:
                if aDictValueForAgent[aKey] == cell.attributs[aKey]:
                    result.append(cell)
        return result

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
