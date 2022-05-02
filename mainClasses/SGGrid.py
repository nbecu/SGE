from SGCell import SGCell


from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from mainClasses.SGCellCollection import SGCellCollection

#Class who is responsible of the grid creation
class SGGrid(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setContentsMargins(25, 5, 25, 5)
        
        
        #Basic initialize
        self.zoom=1
        
        #Init the cell who will be used to create all the cellCollection
        self.collectionOfCell=dict()
    
    def initUI(self):
        #Initialize the starting point of the draw of the grid 
        self.startXbase=int((self.width()/2)-int(self.rows*self.size+(self.rows+1)*self.gap+1)/2)
        self.startYbase=int((self.height()/2)- int(self.columns*self.size+(self.columns+1)*self.gap)/2)
        

    #Drawing the game board with the cell
    def paintEvent(self,event):
        if not hasattr(self, 'rows'):
            self.initializeTheGrid()
        self.initUI()
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(Qt.gray, Qt.SolidPattern))
        #Base of the gameBoard
        if(self.format=="square"):
            painter.drawRect(self.startXbase,self.startYbase, int(self.rows*self.size+(self.rows+1)*self.gap+1), int(self.columns*self.size+(self.columns+1)*self.gap))
        elif(self.format=="hexagon") :
            #To have the correct format we pass through the last cell and firstCell of the grid
            firstCell,lastCell=self.getFirstAndLast()
            partSizeOfLast=self.size/3
            theEndOfTheBoard=(self.startYbase+(partSizeOfLast*3)+self.gap*lastCell.y+self.gap+self.size*lastCell.y          -int(self.size*(lastCell.y)/2)    +self.gap*lastCell.y) -(     self.startYbase+self.gap*firstCell.y+self.gap+self.size*firstCell.y                       -int(self.size*(firstCell.y)/2)    +self.gap*firstCell.y) +self.gap*2
            painter.drawRect(self.startXbase,self.startYbase, self.rows*self.size+(self.rows+1)*self.gap+1        +int(self.size/3)+self.gap  , int(theEndOfTheBoard))
        #Drawing each cells

        for cellCollection in self.cells:
            for cell in cellCollection:
                painter.setBrush(QBrush(cell.getColorOfThePovValue(self.actualPov), Qt.SolidPattern))
                if(self.format=="square"):
                    painter.drawRect(int(self.startXbase+self.gap*(cell.x)+self.size*(cell.x)+self.gap) ,int(self.startYbase+self.gap*(cell.y)+self.size*(cell.y)+self.gap), self.size,self.size)
                elif(self.format=="hexagon") :
                    partSize=round(self.size/3)
                    if(cell.y%2==1):
                        points = QPolygon([
                            QPoint(self.startXbase+self.size*cell.x+partSize+self.gap*cell.x+self.gap        +int(self.size/2),     self.startYbase+self.gap*cell.y+self.gap+self.size*cell.y                       -int(self.size*(cell.y)/2)    +self.gap*cell.y),
                            QPoint(self.startXbase+(partSize*2)+self.size*cell.x+self.gap*cell.x+self.gap    +int(self.size/2),     self.startYbase+self.gap*cell.y+self.gap+self.size*cell.y                       -int(self.size*(cell.y)/2)    +self.gap*cell.y),
                            QPoint(self.startXbase+(partSize*3)+self.size*cell.x+self.gap*cell.x+self.gap    +int(self.size/2),     self.startYbase+partSize+self.gap*cell.y+self.gap+self.size*cell.y              -int(self.size*(cell.y)/2)    +self.gap*cell.y),
                            QPoint(self.startXbase+(partSize*3)+self.size*cell.x+self.gap*cell.x+self.gap   +int(self.size/2),      self.startYbase+(partSize*2)+self.gap*cell.y+self.gap+self.size*cell.y           -int(self.size*(cell.y)/2)    +self.gap*cell.y),
                            QPoint(self.startXbase+(partSize*2)+self.size*cell.x+self.gap*cell.x+self.gap    +int(self.size/2),     self.startYbase+(partSize*3)+self.gap*cell.y+self.gap+self.size*cell.y          -int(self.size*(cell.y)/2)    +self.gap*cell.y),
                            QPoint(self.startXbase+partSize+self.size*cell.x+self.gap*cell.x+self.gap        +int(self.size/2),     self.startYbase+(partSize*3)+self.gap*cell.y+self.gap+self.size*cell.y          -int(self.size*(cell.y)/2)    +self.gap*cell.y),
                            QPoint(self.startXbase+self.size*cell.x+self.gap*cell.x+self.gap                 +int(self.size/2),     self.startYbase+(partSize*2)+self.gap*cell.y+self.gap+self.size*cell.y          -int(self.size*(cell.y)/2)    +self.gap*cell.y),
                            QPoint(self.startXbase+self.size*cell.x+self.gap*cell.x+self.gap                 +int(self.size/2),     self.startYbase+partSize+self.gap*cell.y+self.gap+self.size*cell.y              -int(self.size*(cell.y)/2)    +self.gap*cell.y)
                        ])
                    elif(cell.y%2==0):
                        points = QPolygon([
                            QPoint(self.startXbase+self.size*cell.x+partSize+self.gap*cell.x+self.gap,                 self.startYbase+self.gap*cell.y+self.gap+self.size*cell.y                  -int(self.size*(cell.y)/2)    +self.gap*cell.y),
                            QPoint(self.startXbase+(partSize*2)+self.size*cell.x+self.gap*cell.x+self.gap,             self.startYbase+self.gap*cell.y+self.gap+self.size*cell.y                  -int(self.size*(cell.y)/2)    +self.gap*cell.y),
                            QPoint(self.startXbase+(partSize*3)+self.size*cell.x+self.gap*cell.x+self.gap,             self.startYbase+partSize+self.gap*cell.y+self.gap+self.size*cell.y         -int(self.size*(cell.y)/2)    +self.gap*cell.y),
                            QPoint(self.startXbase+(partSize*3)+self.size*cell.x+self.gap*cell.x+self.gap,             self.startYbase+(partSize*2)+self.gap*cell.y+self.gap+self.size*cell.y      -int(self.size*(cell.y)/2)    +self.gap*cell.y),
                            QPoint(self.startXbase+(partSize*2)+self.size*cell.x+self.gap*cell.x+self.gap,             self.startYbase+(partSize*3)+self.gap*cell.y+self.gap+self.size*cell.y     -int(self.size*(cell.y)/2)    +self.gap*cell.y),
                            QPoint(self.startXbase+partSize+self.size*cell.x+self.gap*cell.x+self.gap,                 self.startYbase+(partSize*3)+self.gap*cell.y+self.gap+self.size*cell.y     -int(self.size*(cell.y)/2)    +self.gap*cell.y),
                            QPoint(self.startXbase+self.size*cell.x+self.gap*cell.x+self.gap,                          self.startYbase+(partSize*2)+self.gap*cell.y+self.gap+self.size*cell.y     -int(self.size*(cell.y)/2)    +self.gap*cell.y),
                            QPoint(self.startXbase+self.size*cell.x+self.gap*cell.x+self.gap,                          self.startYbase+partSize+self.gap*cell.y+self.gap+self.size*cell.y         -int(self.size*(cell.y)/2)    +self.gap*cell.y)
                        ])
                    painter.drawPolygon(points)

        painter.end()
    
    #Funtion to handle the zoom
    def zoomIn(self):
        self.zoom=self.zoom*1.1
        self.size=round(self.size+(self.zoom*10))
        self.gap=round(self.gap+(self.zoom*1))
        self.update()
    
    def zoomOut(self):
        self.zoom=self.zoom*0.9
        self.size=round(self.size-(self.zoom*10))
        if(self.gap>2):
            self.gap=round(self.gap-(self.zoom*1))
        self.update()
        
    def zoomFit(self):
        self.zoom=1
        self.size=self.saveSize
        self.gap=self.saveGap
        self.update()
        
    #To handle the drag of the grid
    def mouseMoveEvent(self, e):
    
        if e.buttons() != Qt.RightButton:
            return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())

        drag.exec_(Qt.MoveAction)
        
    #To move the grid
    def move(self,aPostion):
        if(self.format=="square"):
            self.startXbase=aPostion.x()-int((self.rows*self.size+(self.rows+1)*self.gap+1)/2)
            self.startYbase=aPostion.y()-int((self.columns*self.size+(self.columns+1)*self.gap)/2)
        if(self.format=="hexagon"):
            self.startXbase=aPostion.x()-int((self.rows*self.size+(self.rows+1)*self.gap+1)/2)
            self.startYbase=aPostion.y()-int((self.columns*self.size+(self.columns+1)*self.gap)/2)
        self.update()
    
    #Return the first cell and the last cell
    def getFirstAndLast(self):
        lastCell= self.cells[len(self.cells)-1][len(self.cells)-1]
        firstCell = self.cells[0][0]
        return firstCell,lastCell
        
        
    
    
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
    def initializeTheGrid(self,rows=8, columns=8,format="square",gap=3,size=32):
        #Definition of variables
        self.rows = rows
        self.columns = columns
        self.format=format
        self.size = size
        self.gap=gap
        
        
        #Save the original value
        self.saveSize=size
        self.saveGap=gap
        
        #Cells
        #On declare uen lsite deux Dimensions
        a = [0] * self.rows
        for i in range(self.rows):
            a[i] = [0] * self.columns
        self.cells=a
        
        for i in range(self.columns):
            for j in range(self.rows):
                self.cells[j][i]=SGCell(j,i,self.format,self.size,"default")
    
    #To declare a new kind of pov            
    def initANewPovForCell(self,nameOfPov):
        self.collectionOfCell[nameOfPov]=SGCellCollection(self.cells,nameOfPov)
        
    #To get a cells of a kind of pov    
    def getCellsOfPov(self,nameOfPov):
        return self.collectionOfCell[nameOfPov]
    
    #To choose the inital pov when the game start
    def setInitialPov(self,nameOfPov):
        self.actualPov=nameOfPov
        
                
                
        
        
