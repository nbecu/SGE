from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null
import numpy as np


   
#Class who is responsible of indicator creation 
class SGIndicators(QtWidgets.QWidget):
    def __init__(self,parent,y,indicator,method,methodNumber,value,entity,attribut,color=Qt.black):
        super().__init__(parent)
        #Basic initialize
        self.dashboard=parent
        self.method=method
        self.methodNumber=methodNumber
        self.value=value
        self.methods=["sumAtt","avAtt","minAtt","maxAtt","nb","nbWithLess","nbWithMore","nbEqualTo"]
        self.entity=entity
        self.indicator=indicator
        self.attribut=attribut
        self.calculus=float
        self.y=y
        self.color=color
        self.id=None

    def byMethod(self):
        self.calculus=0.0
        val=9999
        valBis=0
        temp=[]
        if self.entity=='cell':
            if self.method == "sumAtt":
                grids=self.dashboard.model.getGrids()
                for grid in grids:
                    cells=grid.collectionOfCells.getCells()
                    for cell in cells:
                        for attribut in cell.attributs:
                            if attribut ==self.attribut:
                                self.calculus=self.calculus+float(attribut.values())
            if self.method == "avAtt":
                grids=self.dashboard.model.getGrids()
                for grid in grids:
                    cells=grid.collectionOfCells.getCells()
                    for cell in cells:
                        for attribut in cell.attributs:
                            if attribut ==self.attribut:
                                temp.append(float(attribut.values()))
                self.calculus=np.mean(temp)
            if self.method == "minAtt":
                grids=self.dashboard.model.getGrids()
                for grid in grids:
                    cells=grid.collectionOfCells.getCells()
                    for cell in cells:
                        for attribut in cell.attributs:
                            if attribut ==self.attribut:
                                if float(attribut.values)<val:
                                    self.calculus=float(attribut.values)
            
            if self.method == "maxAtt":
                grids=self.dashboard.model.getGrids()
                for grid in grids:
                    cells=grid.collectionOfCells.getCells()
                    for cell in cells:
                        for attribut in cell.attributs:
                            if attribut ==self.attribut:
                                if float(attribut.values)>valBis:
                                    self.calculus=float(attribut.values)
                                


                    """for key in povs:
                        if key is not 'selectedPov':
                            for attribut in key.keys():
                                if attribut == self.attribut:"""





        if self.entity=='agents':
            agents=self.dashboard.model.getAgents()
        
            

    def getMethods(self):
        print(self.methods)


            

