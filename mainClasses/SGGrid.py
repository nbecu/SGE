from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGModel import *

# Class who is responsible of the grid creation
class SGGrid(SGGameSpace):
    def __init__(self, parent, name, columns=10, rows=10,cellShape="square", gap=3, size=30, aColor=None, moveable=True, backGroundImage=None):
        super().__init__(parent, 0, 60, 0, 0)
        # Basic initialize
        self.zoom = 1
        self.model = parent
        self.id = name
        self.columns = columns
        self.rows = rows
        self.cellShape = cellShape
        self.gap = gap
        self.size = size
        self.moveable = moveable
        self.rule = 'moore'
        self.countPaintEvent=0
        self.frameMargin = 8

        self.currentPOV = {'Cell': {}, 'Agent': {}}

        self.saveGap = gap
        self.saveSize = size

        self.startXBase = 0
        self.startYBase = 0

        if aColor != "None":
            self.setColor(aColor)
        self.backgroundImage=backGroundImage
    
    # Drawing the game board with the cell
    def paintEvent(self, event): 
        self.countPaintEvent += 1
        painter = QPainter()
        painter.begin(self)
        if self.backgroundImage != None:
            rect = QRect(0, 0, self.width(), self.height())
            painter.drawPixmap(rect, self.backgroundImage)

        else:
            painter.setBrush(QBrush(self.backgroundColor, Qt.SolidPattern))
        # Base of the gameBoard
        if (self.cellShape == "square"):
            # We redefine the minimum size of the widget
            self.setMinimumSize(int(self.columns*self.size+(self.columns+1) * self.gap+1)+2*self.frameMargin,
                                int(self.rows*self.size+(self.rows+1)*self.gap)+1+2*self.frameMargin)
            painter.drawRect(0,0,self.minimumWidth()-1,self.minimumHeight()-1)
        elif (self.cellShape == "hexagonal"):
            self.setMinimumSize(int(self.columns*self.size+(self.columns+1)*self.gap+1+self.size/2+1.5*self.frameMargin),  int(self.size*0.75*self.rows + (self.gap * (self.rows + 1)) + self.size/4 + 2*self.frameMargin))
            painter.drawRect(0, 0,self.minimumWidth()-1,self.minimumHeight()-1)
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
        self.gap = round(self.gap-(self.zoom*1))
        for cell in self.getCells():
            cell.zoomOut()
            newX=cell.x()
            newY=cell.y()
            for agent in cell.getAgents():
                agent.zoomOut(self.zoom)
        self.update()
        for cell in self.getCells():
            for agent in cell.getAgents(): 
                agent.moveAgent("cell",cellID=agent.cell.id)               
        

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

# -----------------------------------------------------------------------------------------
# Definiton of the methods who the modeler will use

    # Return all the cells
    def getCells(self):
        return self.model.getCells(self)

    # Return the cell
    def getCell_withId(self, aCellID):
        return self.model.getCell(self,aCellID)

    def cellIdFromCoords(self,x,y):
        if x < 0 or y < 0 : return None
        return x + (self.columns * (y -1))
    

    def getCell_withCoords(self,x,y):
        return self.getCell_withId(self.cellIdFromCoords(x,y))

   # Return the cells at a specified column
    def getCells_withColumn(self, columnNumber):
        """
        Return the cells at a specified column.
        args:
            columnNumber (int): column number
        """
        return [ cell for cell in self.model.getCells(self) if cell.xPos== columnNumber]
        

  # Return the cells at a specified row
    def getCells_withRow(self, rowNumber):
        """
        Return the cells at a specified column.
        args:
            rowNumber (int): row number
        """
        return [ cell for cell in self.model.getCells(self) if cell.yPos== rowNumber]

    
