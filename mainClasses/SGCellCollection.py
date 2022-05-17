from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from SGCell import SGCell



   
#Class who is responsible of the declaration of cells
class SGCellCollection():
    def __init__(self,parent,rows,columns,format,size,gap,startXBase,startYBase):
        #Basic initialize
        self.parent=parent
        self.rows=rows
        self.columns=columns
        self.format=format
        self.size=size
        self.gap=gap
        self.startXBase=startXBase
        self.startYBase=startYBase
        self.cells={}
        #Initialize the different pov
        self.povs={}
        #Initialize of the user interface
        self.initUI()
        
    #Intialize all the cells who will be displayed
    def initUI(self):
        for i in range(self.rows):
            for j in range(self.columns):
                aCell=SGCell(self.parent,self,i%self.rows,j%self.columns,self.format,self.size,self.gap,self.startXBase,self.startYBase)
                self.cells[aCell.getId()]=aCell
       
    #To get all the cells of the collection 
    def getCells(self):
        return self.cells
    
    #To get all the povs of the collection 
    def getPovs(self):
        return self.povs
    
    #To get a cell in particular
    def getCell(self,aName):
        return self.cells[aName]
    
    #To remove a cell in particular
    def removeVisiblityCell(self,aName):
        self.getCell(aName).isDisplay=False
        self.parent.update()
    

        
    
        
    