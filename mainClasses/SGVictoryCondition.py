from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null
import numpy as np


   
#Class who is responsible of indicator creation 
class SGVictoryCondition(QtWidgets.QWidget):
    def __init__(self,parent,name,method,objective,attribut,value,entity,color):
        super().__init__(parent)
        #Basic initialize
        self.victoryBoard=parent
        self.method=method
        self.objective=objective
        self.value=value
        self.methods=["sumAtt","avgAtt","minAtt","maxAtt","nb","nbWithLess","nbWithMore","nbEqualTo"]
        self.entity=entity
        self.name=name
        self.attribut=attribut
        self.color=color
        self.id=int
        self.checkStatus=False
        self.initUI()
        

    def initUI(self):
        self.conditionLayout = QtWidgets.QHBoxLayout()
        calcValue=self.byMethod()
        self.name=self.setName(calcValue)
        self.label = QtWidgets.QTextEdit(self.name)
        self.label.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.label.setReadOnly(True)
        color = QColor(self.victoryBoard.textColor)
        color_string = f"color: {color.name()};"
        self.label.setStyleSheet(color_string)
        self.conditionLayout.addWidget(self.label)

    def setName(self,calcValue):
        if self.attribut is not None:
            if self.value is not None:
                aName= self.method+' '+self.attribut+" "+self.value+" : "+str(calcValue)
            else:
                aName = self.method+' '+self.attribut+" : "+str(calcValue)
        else:
            aName=self.method+' '+self.entity+" : "+str(calcValue)+'/'+str(self.objective)
        return aName

    def updateText(self):
        newCalc=self.byMethod()
        newText= self.setName(newCalc)
        self.label.setPlainText(newText)
    
    def getUpdatePermission(self):
        if self.victoryBoard.displayRefresh=='instantaneous':
            return True
        if self.victoryBoard.displayRefresh=='withButton':
            return True

    def getSizeXGlobal(self):
        return 150+len(self.name)*5
    
    def byMethod(self):
        calcValue=0.0
        counter=0
        if self.entity=='cell':
            grids=self.victoryBoard.model.getGrids()
            for grid in grids:
                cells=grid.getCells()
                aCell=grid.collectionOfCells.getCell('cell1-1')
                valForMin=aCell.attributs[self.attribut]
                valForMax=aCell.attributs[self.attribut]
                if self.method == "sumAtt" or self.method =='avgAtt':
                    for cell in cells :
                        if cell.isDisplay ==True:
                            calcValue=calcValue+float(cell.attributs[self.attribut])
                    if self.method=='avgAtt':
                        calcValue=round(calcValue/len((cells)),2) #! toutes ou juste visibles ?
                if self.method == "minAtt" or self.method == "maxAtt":
                    if self.method == "minAtt":
                        for cell in cells:
                            if cell.isDisplay ==True:
                                if float(cell.attributs[self.attribut])<valForMin:
                                    calcValue=float(cell.attributs[self.attribut])
                                    valForMin=float(cell.attributs[self.attribut])
                    else:
                        for cell in cells:
                            if cell.isDisplay ==True:
                                if float(cell.attributs[self.attribut])>valForMax:
                                    calcValue=float(cell.attributs[self.attribut])
                                    valForMax=float(cell.attributs[self.attribut])
                if self.method == "nbEqualTo" or  self.method == "nbWithLess" or self.method == "nbWithMore":
                    if self.method == "nbEqualTo":
                        for cell in cells:
                            if cell.isDisplay ==True:
                                if cell.attributs[self.attribut]==self.value:
                                    counter=counter+1
                        calcValue=counter
                    if self.method == "nbWithLess":
                        for cell in cells:
                            if cell.isDisplay ==True:
                                if cell.attributs[self.attribut]<self.value:
                                    counter=counter+1
                        calcValue=counter
                    else:
                        for cell in cells:
                            if cell.isDisplay ==True:
                                if cell.attributs[self.attribut]>self.value:
                                    counter=counter+1
                        calcValue=counter
                if self.method == "nb":
                    for cell in cells:
                        if cell.isDisplay ==True:
                            if cell.attributs[self.attribut]==self.value:
                                counter=counter+1
                    calcValue=counter
                return calcValue

        elif self.entity == 'agent':
            agents=self.victoryBoard.model.getAgents(species=self.entity)
            if self.method =='nb':
                calcValue=len(agents)
                return calcValue
        
        else:
            roundNumber=self.victoryBoard.model.timeManager.getRoundNumber()
            if self.method == 'nb':
                calcValue=roundNumber
                return calcValue
            

    def verifStatus(self):
        calcValue=self.byMethod()
        if calcValue==self.objective:
            self.checkStatus=True



    def getMethods(self):
        print(self.methods)