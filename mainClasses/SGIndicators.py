from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null
import numpy as np
from mainClasses.SGCell import SGCell
from mainClasses.SGAgent import SGAgent


   
#Class who is responsible of indicator creation 
class SGIndicators(QtWidgets.QWidget):
    def __init__(self,parent,y,name,method,attribut,value,entity,logicOp,color=Qt.blue,isDisplay=True):
        super().__init__(parent)
        #Basic initialize
        self.dashboard=parent
        self.method=method
        self.value=value
        self.methods=["sumAtt","avgAtt","minAtt","maxAtt","nb","nbWithLess","nbWithMore","nbEqualTo","thresoldToLogicOp"]
        self.entity=entity
        self.result=float
        self.name=name
        self.attribut=attribut
        self.y=y
        self.color=color
        self.logicOp=logicOp
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
        color = QColor(self.color)
        color_string = f"color: {color.name()};"
        self.label.setStyleSheet(color_string+"border: none;background-color: lightgray;")
        self.indicatorLayout.addWidget(self.label)

    def setName(self,calcValue):
        if self.value is not None:
            aName= self.method+' '+self.attribut+" "+self.value+" : "+str(calcValue)
        else:
            if self.attribut is not None:
                aName = self.method+' '+self.attribut+" : "+str(calcValue)
            else:
                aName = self.method+' : '+str(calcValue)
        return aName

    def updateText(self):
        newCalc=self.byMethod()
        self.result=newCalc
        newText= self.setName(self.result)
        self.label.setPlainText(newText)
        self.dashboard.model.timeManager.updateEndGame()

    def setResult(self, aValue):
        """Function to configure a score in an Indicator"""
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
        species=self.dashboard.model.getAgentSpecies()
        if self.entity=='cell':
            grids=self.dashboard.model.getGrids()
            for grid in grids:
                cells=grid.getCells()
                aCell=grid.getCell(1,1)
                valForMin=aCell.dictOfAttributs[self.attribut]
                valForMax=aCell.dictOfAttributs[self.attribut]
                if self.method == "sumAtt" or self.method =='avgAtt':
                    for cell in cells :
                        if cell.isDisplay ==True:
                            calcValue=calcValue+float(cell.dictOfAttributs[self.attribut])
                    if self.method=='avgAtt':
                        calcValue=round(calcValue/len((cells)),2) #! toutes ou juste visibles ?
                if self.method == "minAtt" or self.method == "maxAtt":
                    if self.method == "minAtt":
                        for cell in cells:
                            if cell.isDisplay ==True:
                                if float(cell.dictOfAttributs[self.attribut])<valForMin:
                                    calcValue=float(cell.dictOfAttributs[self.attribut])
                                    valForMin=float(cell.dictOfAttributs[self.attribut])
                    else:
                        for cell in cells:
                            if cell.isDisplay ==True:
                                if float(cell.dictOfAttributs[self.attribut])>valForMax:
                                    calcValue=float(cell.dictOfAttributs[self.attribut])
                                    valForMax=float(cell.dictOfAttributs[self.attribut])
                if self.method == "nbEqualTo" or  self.method == "nbWithLess" or self.method == "nbWithMore":
                    if self.method == "nbEqualTo":
                        for cell in cells:
                            if cell.isDisplay ==True:
                                if cell.dictOfAttributs[self.attribut]==self.value:
                                    counter=counter+1
                        calcValue=counter
                    if self.method == "nbWithLess":
                        for cell in cells:
                            if cell.isDisplay ==True:
                                if cell.dictOfAttributs[self.attribut]<self.value:
                                    counter=counter+1
                        calcValue=counter
                    if self.method == "nbWithMore":
                        for cell in cells:
                            if cell.isDisplay ==True:
                                if cell.dictOfAttributs[self.attribut]>self.value:
                                    counter=counter+1
                        calcValue=counter
                if self.method == "nb":
                    for cell in cells:
                        if cell.isDisplay ==True:
                            if cell.dictOfAttributs[self.attribut]==self.value:
                                counter=counter+1
                    calcValue=counter
                return calcValue


        elif self.entity=="agent":
            agents=self.dashboard.model.getAgents()
            if self.method =='nb':
                calcValue=len(agents)
                return calcValue
        
        elif self.entity in [instance.name for instance in species]:
            aSpecies=self.dashboard.model.getAgentSpecie(self.entity)
            agents=self.dashboard.model.getAgents(aSpecies.name)
            if self.method =='nb':
                calcValue=len(agents)
                return calcValue

        
        elif self.entity is None:
            if self.method=="score":
                calcValue=self.value
                if calcValue==None:
                    calcValue=0
                return calcValue
        
        elif isinstance(self.entity,SGAgent) or isinstance(self.entity,SGCell):
            if self.method =="display":
                calcValue=self.entity.dictOfAttributs[self.attribut]
                return calcValue
            if self.method=="thresoldToLogicOp":
                if self.logicOp =="greater":
                    if self.entity.dictOfAttributs[self.attribut]>self.value:
                        calcValue="greater than"+str(self.value)
                        return calcValue
                if self.logicOp =="greater or equal":
                    if self.entity.dictOfAttributs[self.attribut]>=self.value:
                        calcValue="greater than or equal to"+str(self.value)
                        return calcValue
                if self.logicOp =="equal":
                    if self.entity.dictOfAttributs[self.attribut]==self.value:
                        calcValue="equal to"+str(self.value)
                        return calcValue
                if self.logicOp =="less or equal":
                    if self.entity.dictOfAttributs[self.attribut]<=self.value:
                        calcValue="less than or equal to"+str(self.value)
                        return calcValue
                if self.logicOp =="less":
                    if self.entity.dictOfAttributs[self.attribut]<self.value:
                        calcValue="less than"+str(self.value)
                        return calcValue


            

    def getMethods(self):
        print(self.methods)


            

