from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null
import numpy as np


   
#Class who is responsible of indicator creation 
class SGIndicators(QtWidgets.QWidget):
    def __init__(self,parent,y,name,method,attribut,value,entity,color,isDisplay):
        super().__init__(parent)
        #Basic initialize
        self.dashboard=parent
        self.method=method
        self.value=value
        self.methods=["sumAtt","avgAtt","minAtt","maxAtt","nb","nbWithLess","nbWithMore","nbEqualTo"]
        self.entity=entity
        self.result=float
        self.name=name
        self.attribut=attribut
        self.y=y
        self.color=color
        self.id=int
        self.isDisplay=isDisplay
        self.initUI()
        

    def initUI(self):
        self.indicatorLayout = QtWidgets.QHBoxLayout()
        calcValue=self.byMethod()
        self.result=calcValue
        self.name=self.setName(calcValue)
        self.label = QtWidgets.QTextEdit(self.name)
        self.label.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.label.setReadOnly(True)
        color = QColor(self.dashboard.textColor)
        color_string = f"color: {color.name()};"
        self.label.setStyleSheet(color_string+"border: none;background-color: lightgray;")
        self.indicatorLayout.addWidget(self.label)

    def setName(self,aResult):
        if self.value is not None:
            aName= self.method+' '+self.attribut+" "+self.value+" : "+str(aResult)
        else:
            aName = self.method+' '+self.attribut+" : "+str(aResult)
        return aName

    def updateText(self):
        newCalc=self.byMethod()
        self.result=newCalc
        newText= self.setName(self.result)
        self.label.setPlainText(newText)

    def setResult(self,aValue):
        self.result=aValue
        newText= self.setName(self.result)
        self.label.setPlainText(newText)
    
    def getUpdatePermission(self):
        if self.dashboard.displayRefresh=='instantaneous':
            return True
        if self.dashboard.displayRefresh=='withButton':
            return True

    def getSizeXGlobal(self):
        return 150+len(self.name)*5
    
    def byMethod(self):
        calcValue=0.0
        counter=0
        if self.entity=='cell':
            grids=self.dashboard.model.getGrids()
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


        else:
            agents=self.dashboard.model.getAgents(species=self.entity)
            if self.method =='nb':
                calcValue=len(agents)
                return calcValue
        
            

    def getMethods(self):
        print(self.methods)


            

