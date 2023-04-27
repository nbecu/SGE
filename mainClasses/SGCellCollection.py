from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from SGCell import SGCell



   
#Class who is responsible of the declaration of cells
class SGCellCollection():
    def __init__(self,parent,rows,columns,format,size,gap,startXBase,startYBase):
        #Basic initialize
        self.grid=parent
        self.rows=rows
        self.columns=columns
        self.format=format
        self.size=size
        self.gap=gap
        self.startXBase=startXBase
        self.startYBase=startYBase
        self.cells={}
        self.watchers={}
        #Initialize the different pov
        self.povs={}
        self.borderPovs={}
        self.borderPovs['selectedBorderPov']={}
        #Initialize of the user interface
        self.initUI()
        
    #Intialize all the cells who will be displayed
    def initUI(self):
        for i in range(self.rows):
            for j in range(self.columns):
                aCell=SGCell(self.grid,self,i%self.rows,j%self.columns,self.format,self.size,self.gap,self.startXBase,self.startYBase)
                self.cells[aCell.getId()]=aCell
       
    #To get all the cells of the collection 
    def getCells(self):
        return self.cells.values()
    
    #To get all the povs of the collection 
    def getPovs(self):
        return {key: value for dict in (self.povs, self.borderPovs) for key, value in dict.items() if "selected" not in key and "borderWidth"not in key}
    
    #To get a cell in particular
    def getCell(self,aName):
        return self.cells[aName]
    
    #To remove a cell in particular
    def removeVisiblityCell(self,aName):
        self.getCell(aName).isDisplay=False
        self.grid.update()
        
    #To get all cells who is displayed
    def getCellsDisplay(self):
        res=[]
        for cell in list(self.cells.values()):
            if cell.isDisplay ==True:
                res.append(cell)
        return res
    
    # test
    def getWatchers(self):
        print(self.watchers)

        
    
        
    