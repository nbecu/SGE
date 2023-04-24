from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null
import numpy as np


   
#Class who is responsible of indicator creation 
class SGIndicators():
    def __init__(self,parent,y,name,method,attribut,value,entity,color):
        # super().__init__(parent)
        #Basic initialize
        self.dashboard=parent
        self.method=method
        self.value=value
        self.methods=["sumAtt","avgAtt","minAtt","maxAtt","nb","nbWithLess","nbWithMore","nbEqualTo"]
        self.entity=entity
        self.calculus=0.0
        self.name=name
        self.attribut=attribut
        self.y=y
        self.color=color
        self.id=int
        self.initUI()
        

    def initUI(self):
        self.indicatorLayout = QtWidgets.QHBoxLayout()
        self.name=self.setName()
        self.label = QtWidgets.QLabel(self.name)
        self.indicatorLayout.addWidget(self.label)

    def setName(self):
        self.calculus=self.byMethod()
        if self.name is None and self.value is not None:
            self.name= self.method+' '+self.attribut+" "+self.value+" : "+str(self.calculus)
        elif self.name is None:
            self.name = self.method+' '+self.attribut+" : "+str(self.calculus)
        return self.name

    """def paintEvent(self, event):
        painter = QPainter() 
        painter.begin(self)
        aFont=QFont("Verdana",10)
        painter.setFont(aFont)
        painter.drawText(QRect(10,0,self.getSizeXGlobal(),20), Qt.AlignLeft, self.name)
        painter.end()"""

    def getSizeXGlobal(self):
        return 150+len(self.name)*5
    
    def byMethod(self):
        self.calculus=0.0
        counter=0
        if self.entity=='cell':
            grids=self.dashboard.model.getGrids()
            for grid in grids:
                cells=grid.getCells()
                aCell=grid.collectionOfCells.getCell('cell1-1')
                valForMin=aCell.attributs[self.attribut]
                valForMax=aCell.attributs[self.attribut]
                if self.method == "sumAtt" or self.method =='avgAtt':
                    for cell in cells:
                        self.calculus=self.calculus+float(cell.attributs[self.attribut])
                    if self.method=='avgAtt':
                        self.calculus=self.calculus/len((cells))
                    return self.calculus
                if self.method == "minAtt" or self.method == "maxAtt":
                    if self.method == "minAtt":
                        for cell in cells:
                            if float(cell.attributs[self.attribut])<valForMin:
                                self.calculus=float(cell.attributs[self.attribut])
                                valForMin=float(cell.attributs[self.attribut])
                        return self.calculus
                    else:
                        for cell in cells:
                            if float(cell.attributs[self.attribut])>valForMax:
                                self.calculus=float(cell.attributs[self.attribut])
                                valForMax=float(cell.attributs[self.attribut])
                        return self.calculus
                if self.method == "nbEqualTo" or  self.method == "nbWithLess" or self.method == "nbWithMore":
                    if self.method == "nbEqualTo":
                        for cell in cells:
                            if cell.attributs[self.attribut]==self.value:
                                counter=counter+1
                        self.calculus=counter
                        return self.calculus
                    if self.method == "nbWithLess":
                        for cell in cells:
                            if cell.attributs[self.attribut]<self.value:
                                counter=counter+1
                        self.calculus=counter
                        return self.calculus
                    else:
                        for cell in cells:
                            if cell.attributs[self.attribut]>self.value:
                                counter=counter+1
                        self.calculus=counter
                        return self.calculus
                if self.method == "nb":
                    for cell in cells:
                        if cell.attributs[self.attribut]==self.value:
                            counter=counter+1
                    self.calculus=counter
                    return self.calculus


        else:
            agents=self.dashboard.model.getAgents(species=self.entity)
            if self.method =='nb':
                self.calculus=len(agents)
                return self.calculus
        
            

    def getMethods(self):
        print(self.methods)


            

