from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null
import numpy as np


   
#Class who is responsible of indicator creation 
class SGIndicators(QtWidgets.QWidget):
    def __init__(self,parent,y,name,method,attribut,value,entity,color):
        super().__init__(parent)
        #Basic initialize
        self.dashboard=parent
        self.method=method
        self.value=value
        self.methods=["sumAtt","avAtt","minAtt","maxAtt","nb","nbWithLess","nbWithMore","nbEqualTo"]
        self.entity=entity
        self.name=name
        self.attribut=attribut
        self.calculus=float
        self.y=y
        self.color=color
        self.id=int
        self.byMethod()

    def paintEvent(self, event):
        painter = QPainter() 
        painter.begin(self)
        aFont=QFont("Verdana",10)
        aFont.setUnderline(True)
        painter.setFont(aFont)
        painter.drawText(QRect(15,0,self.dashboard.getSizeXGlobal()-50,20), Qt.AlignLeft, self.name+' : '+str(self.calculus))
        painter.setFont(QFont("Verdana",8))
        painter.drawText(QRect(40,5,self.dashboard.getSizeXGlobal()-50,15), Qt.AlignLeft, self.name+' : '+str(self.calculus))
        painter.end()

    def byMethod(self):
        self.calculus=0.0
        valForMin=9999
        valForMax=0
        counter=0
        temp=[]
        if self.entity=='cell':
            if self.method == "sumAtt":
                grids=self.dashboard.model.getGrids()
                for grid in grids:
                    cells=grid.collectionOfCells.getCells()
                    for cell in cells:
                        for attribut in cell.attributs:
                            if attribut ==self.attribut:
                                self.calculus=self.calculus+float(cell.attributs[attribut])
                return self.calculus
            if self.method == "avAtt":
                grids=self.dashboard.model.getGrids()
                for grid in grids:
                    cells=grid.collectionOfCells.getCells()
                    for cell in cells:
                        for attribut in cell.attributs:
                            if attribut ==self.attribut:
                                temp.append(float(cell.attributs[attribut]))
                self.calculus=np.mean(temp)
                return self.calculus
            
            if self.method == "minAtt":
                grids=self.dashboard.model.getGrids()
                for grid in grids:
                    cells=grid.collectionOfCells.getCells()
                    for cell in cells:
                        for attribut in cell.attributs:
                            if attribut ==self.attribut:
                                if float(cell.attributs[attribut])<valForMin:
                                    self.calculus=float(cell.attributs[attribut])
                                    valForMin=float(cell.attributs[attribut])
                return self.calculus
            
            if self.method == "maxAtt":
                grids=self.dashboard.model.getGrids()
                for grid in grids:
                    cells=grid.collectionOfCells.getCells()
                    for cell in cells:
                        for attribut in cell.attributs:
                            if attribut ==self.attribut:
                                if float(cell.attributs[attribut])>valForMax:
                                    self.calculus=float(cell.attributs[attribut])
                                    valForMax=float(cell.attributs[attribut])
                return self.calculus
            
            if self.method == "nbEqualTo":
                grids=self.dashboard.model.getGrids()
                for grid in grids:
                    cells=grid.collectionOfCells.getCells()
                    for cell in cells:
                        for attribut in cell.attributs:
                            if attribut ==self.attribut:
                                if cell.attributs[attribut]==self.value:
                                    counter=counter+1
                self.calculus=counter
                return self.calculus
            
            if self.method == "nbWithLess":
                grids=self.dashboard.model.getGrids()
                for grid in grids:
                    cells=grid.collectionOfCells.getCells()
                    for cell in cells:
                        for attribut in cell.attributs:
                            if attribut ==self.attribut:
                                if cell.attributs[attribut]<self.value:
                                    counter=counter+1
                self.calculus=counter
                return self.calculus
            
            if self.method == "nbWithMore":
                grids=self.dashboard.model.getGrids()
                for grid in grids:
                    cells=grid.collectionOfCells.getCells()
                    for cell in cells:
                        for attribut in cell.attributs:
                            if attribut ==self.attribut:
                                if cell.attributs[attribut]>self.value:
                                    counter=counter+1
                self.calculus=counter
                return self.calculus
            
            if self.method == "nb":
                grids=self.dashboard.model.getGrids()
                for grid in grids:
                    cells=grid.collectionOfCells.getCells()
                    for cell in cells:
                        for attribut in cell.attributs:
                            if attribut ==self.attribut:
                                if cell.attributs[attribut]==self.value:
                                    counter=counter+1
                self.calculus=counter
                return self.calculus


        if self.entity=='agents':
            agents=self.dashboard.model.getAgents()
        
            

    def getMethods(self):
        print(self.methods)


            

