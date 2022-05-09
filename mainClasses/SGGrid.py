import random
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from SGGameSpace import SGGameSpace
from SGCellCollection import SGCellCollection

#Class who is responsible of the grid creation
class SGGrid(SGGameSpace):
    def __init__(self,parent,name,rows=8, columns=8,format="square",gap=3,size=32):
        super().__init__(parent,0,60,0,0)
        #Basic initialize
        self.zoom=1
        self.id=name
        self.rows=rows
        self.columns=columns
        self.format=format
        self.gap=gap
        self.size=size
        
        self.saveGap=gap
        self.saveSize=size
        
        self.startXBase=0
        self.startYBase=0
        
        #We initialize the user interface related to the grid
        self.initUI()
       
    #Initialize the user interface
    def initUI(self): 
        #Init the cellCollection
        self.collectionOfCells=SGCellCollection(self,self.columns,self.rows,self.format,self.size,self.gap,self.startXBase,self.startYBase)
        
        
    #Drawing the game board with the cell
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
        #Base of the gameBoard
        if(self.format=="square"):
            #We redefine the minimum size of the widget
            self.setMinimumSize(int(self.columns*self.size+(self.columns+1)*self.gap+1), int(self.rows*self.size+(self.rows+1)*self.gap))
            painter.drawRect(0,0, int(self.columns*self.size+(self.columns+1)*self.gap+1), int(self.rows*self.size+(self.rows+1)*self.gap))
        elif(self.format=="hexagonal"):
            self.setMinimumSize(int(self.columns*self.size+(self.columns+1)*self.gap+1)+int(self.size/2),         int((self.rows+1)*(self.size/3)*2) +self.gap*2)
            painter.drawRect(0,0, int(self.columns*self.size+(self.columns+1)*self.gap+1)+int(self.size/2),       int((self.rows+1)*(self.size/3)*2) +self.gap*2) 
        painter.end()
        
    #Funtion to handle the zoom
    def zoomIn(self):
        self.zoom=self.zoom*1.1
        self.gap=round(self.gap+(self.zoom*1))
        self.size=round(self.size+(self.zoom*10))
        for cell in self.collectionOfCells.getCells() :
            self.collectionOfCells.getCell(cell).zoomIn() 
        self.update()
    
    def zoomOut(self):
        self.zoom=self.zoom*0.9
        self.size=round(self.size-(self.zoom*10))
        if(self.gap>2 and self.format=="square"):
            self.gap=round(self.gap-(self.zoom*1))
            for cell in self.collectionOfCells.getCells():
                self.collectionOfCells.getCell(cell).zoomOut()
        else:
            self.gap=round(self.gap-(self.zoom*1))
            for cell in self.collectionOfCells.getCells():
                self.collectionOfCells.getCell(cell).zoomOut()
        for cell in self.collectionOfCells.getCells() :
            self.collectionOfCells.getCell(cell).zoomOut() 
        self.update()
        
    #To handle the drag of the grid
    def mouseMoveEvent(self, e):
    
        if e.buttons() != Qt.LeftButton:
            return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())

        drag.exec_(Qt.MoveAction)
        
    #Funtion to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        if(self.format=="square"):
            return int(self.columns*self.size+(self.columns+1)*self.gap+1)
        if(self.format=="hexagonal"):
            return int(self.columns*self.size+(self.columns+1)*self.gap+1) +int(self.size/2)
    
    def getSizeYGlobal(self):
        if(self.format=="square"):
            return int(self.rows*self.size+(self.rows+1)*self.gap)
        if(self.format=="hexagonal"):
            return int((self.rows+1)*(self.size/3)*2) +self.gap*2
        
        
    #To choose the inital pov
    def setInitialPov(self,nameOfPov):
        self.collectionOfCells.nameOfPov=nameOfPov
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    #Retourne la cellule demande de la grille
    def getCell(self,aName):
        return self.collectionOfCells.getCell(aName)
    
#To handle POV and placing on cell
    #To define a value for all cells
    def setValueForCells(self,nameOfPov,aValue):
        for aCell in self.collectionOfCells.getCells():
            aCell.attributs[nameOfPov]=aValue
            
    #To apply to a specific cell a value  
    def setForXandY(self,nameOfPov,nameOfValue,aValueX,aValueY):
        self.collectionOfCells.getCell("cell"+str(aValueX-1)+str(aValueY-1)).attributs[nameOfPov]=nameOfValue
    
    #To apply to a all row of cell a value
    def setForX(self,nameOfPov,nameOfValue,aValueX):
        for y in range(self.rows):
            self.collectionOfCells.getCell("cell"+str(aValueX-1)+str(y)).attributs[nameOfPov]=nameOfValue
    
    #To apply to a all column of cell a value
    def setForY(self,nameOfPov,nameOfValue,aValueY):
        for x in range(self.columns):
            self.collectionOfCells.getCell("cell"+str(x)+str(aValueY)).attributs[nameOfPov]=nameOfValue
    
    #To apply to some random cell a value
    def setForRandom(self,nameOfPov,nameOfValue,numberOfRandom):
        alreadyDone=list()
        while len(alreadyDone)!=numberOfRandom:
            aValueX=random.randint(0, self.columns-1)
            aValueY=random.randint(0, self.rows-1)
            if (aValueX,aValueY) not in alreadyDone:
                alreadyDone.append((aValueX,aValueY))
                self.collectionOfCells.getCell("cell"+str(aValueX)+str(aValueY)).attributs[nameOfPov]=nameOfValue
  
            
    

