from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null
# import numpy as np
from mainClasses.SGCell import SGCell
from mainClasses.SGAgent import SGAgent
from mainClasses.SGSimulationVariables import SGSimulationVariables


   
#Class who is responsible of indicator creation 
class SGIndicators(QtWidgets.QWidget):
    def __init__(self,parent,y,name,method,attribut,value,listOfEntDef,logicOp,color=Qt.blue,isDisplay=True):
        super().__init__(parent)
        #Basic initialize
        self.dashboard=parent
        self.method=method
        if self.method=="thresoldToLogicOp":
            self.threshold= value
        else : 
            self.value=value
        self.methods=["sumAtt","avgAtt","minAtt","maxAtt","nb","nbWithLess","nbWithMore","nbEqualTo","thresoldToLogicOp"]
        self.listOfEntDef=listOfEntDef
        if self.method in ["display", "thresoldToLogicOp"]: self.entity=listOfEntDef  
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
        self.setName()
        self.label = QtWidgets.QTextEdit(self.name + str(calcValue))
        self.label.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.label.setReadOnly(True)
        color = QColor(self.color)
        color_string = f"color: {color.name()};"
        self.label.setStyleSheet(color_string+"border: none;background-color: lightgray;")
        self.indicatorLayout.addWidget(self.label)

    def setName(self):
        if self.name is not None:
            self.name = self.name + ' : '
            return 
        if self.method in ["nbWithLess","nbWithMore","nbEqualTo"]:
        # if self.value is not None and self.attribut is not None:
            aName= 'nb '+self.attribut+ ' '+self.method[2:]+" "+self.value+" : "
        elif self.attribut is not None:
                aName = self.method+' '+self.attribut+" : "
        elif self.method == 'nb':
            aName = self.method+' '+self.entity+' : '
        else:
            aName = self.method+' : '
        self.name = aName


    def updateText(self):
        newCalc=self.byMethod()
        self.result=newCalc
        newText= self.name + str(self.result)
        self.label.setPlainText(newText)
        self.dashboard.model.timeManager.updateEndGame()
    
    def updateByMqtt(self,newValue):
        self.result=newValue
        newText= self.name + str(newValue)
        self.label.setPlainText(newText)
        self.dashboard.model.timeManager.updateEndGame()

    def setResult(self, aValue):
        """Function to configure a score in an Indicator"""
        self.result=aValue
        self.label.setPlainText(self.name + str(self.result))
        if isinstance(self.entity,SGSimulationVariables):
            self.entity.value=aValue
    
    def getUpdatePermission(self):
        if self.dashboard.displayRefresh=='instantaneous':
            return True
        if self.dashboard.displayRefresh=='withButton':
            return True

    def getSizeXGlobal(self):
        return 150+len(self.name)*5
    
    def getListOfEntities(self):
        return [j for i in [entDef.entities for entDef in self.listOfEntDef] for j in i]  #This list comprehension expression concatenates the list of entities of all specified EntDef    
    def byMethod(self):
        calcValue=0.0
        counter=0
        listEntities = self.getListOfEntities()
        
        if self.method =='nb': return len(listEntities)
        
        elif self.method in ["sumAtt","avgAtt","minAtt","maxAtt","nbWithLess","nbWithMore","nbEqualTo"]:
            listOfValues = [aEnt.value(self.attribut) for aEnt in listEntities]
            if self.method == 'sumAtt': return sum(listOfValues)
            if self.method == 'avgAtt': return round(sum(listOfValues) / len(listOfValues),2)
            if self.method == 'minAtt': return min(listOfValues)
            if self.method == 'maxAtt': return max(listOfValues)
            if self.method == 'nbWithLess': return len([x for x in listOfValues if x < self.value])
            if self.method == 'nbWithMore': return len([x for x in listOfValues if x > self.value])
            if self.method == 'nbEqualTo': return len([x for x in listOfValues if x == self.value])

        elif self.method=="score":
            calcValue=self.value
            return 0 if self.value is None else self.value
        
        elif self.method =="display":
            return self.entity.value(self.attribut)
        elif self.method=="thresoldToLogicOp":
            # les indicator greater, greater or equal ect.. doivent etre codés comme les autres method
            if self.logicOp =="greater":
                if self.entity.value(self.attribut) > self.threshold:
                    calcValue="greater than"+str(self.threshold)
                    return calcValue
            if self.logicOp =="greater or equal":
                if self.entity.value(self.attribut)>=self.threshold:
                    calcValue="greater than or equal to"+str(self.threshold)
                    return calcValue
            if self.logicOp =="equal":
                if self.entity.value(self.attribut)==self.threshold:
                    calcValue="equal to"+str(self.threshold)
                    return calcValue
            if self.logicOp =="less or equal":
                if self.entity.value(self.attribut)<=self.threshold:
                    calcValue="less than or equal to"+str(self.threshold)
                    return calcValue
            if self.logicOp =="less":
                if self.entity.value(self.attribut)<self.threshold:
                    calcValue="less than"+str(self.threshold)
                    return calcValue

            

    def getMethods(self):
        print(self.methods)


            

