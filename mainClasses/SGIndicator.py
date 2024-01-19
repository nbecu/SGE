from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null
# import numpy as np
from mainClasses.SGCell import SGCell
from mainClasses.SGAgent import SGAgent
from mainClasses.SGSimulationVariable import SGSimulationVariable


   
#Class who is responsible of indicator creation 
class SGIndicator(QtWidgets.QWidget):
    def __init__(self,parent,name,method,attribute,value,listOfEntDef,logicOp,color=Qt.blue,displayRefresh="instantaneous",isDisplay=True):
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
        if self.method == "simVar": self.simVar=listOfEntDef  
        self.result=float
        self.name=name
        self.attribute=attribute
        self.posY = self.dashboard.posYOfItems
        self.dashboard.posYOfItems += 1
        self.color=color
        self.logicOp=logicOp
        self.isDisplay=isDisplay
        self.displayRefresh=displayRefresh
        self.memory=[]
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
        self.label.setStyleSheet(color_string+"border: none;background-color: transparent;")
        self.indicatorLayout.addWidget(self.label)

    def setName(self):
        if self.name is not None:
            self.name = self.name + ' : '
            return 
        if self.method in ["nbWithLess","nbWithMore","nbEqualTo"]:
            aName= 'nb '+self.attribute+ ' '+self.method[2:]+" "+self.value+" : "
        elif self.attribute is not None:
                aName = self.method+' '+self.attribute+" : "
        elif self.method == 'nb':
            aName = self.method+' '+self.strOfEntitiesName()+' : '
        elif self.method == "separator":
            aName = ""
        else:
            aName = self.method+' : '
        self.name = aName

    def strOfEntitiesName(self):
        return ",".join([entDef.entityName for entDef in self.listOfEntDef])

    def checkAndUpdate(self):
        if self.getUpdatePermission():
            self.updateText()
        
    def updateText(self):
        newCalc=self.byMethod()
        self.result=newCalc
        newText= self.name + str(self.result)
        self.label.setPlainText(newText)
        self.dashboard.model.timeManager.updateEndGame()
    
    def updateTextByValue(self,aValue):
        self.result=aValue
        newText=self.name + str(self.result)
        self.label.setPlainText(newText)
        self.dashboard.model.timeManager.updateEndGame()
    
    def updateByMqtt(self,newValue):
        self.result=newValue
        newText= self.name + str(newValue)
        self.label.setPlainText(newText)
        self.dashboard.model.timeManager.updateEndGame()

    def setResult(self, aValue): #this is a private method
        """Function to configure a score in an Indicator"""
        self.result=aValue
        self.label.setPlainText(self.name + str(self.result))
        if isinstance(self.listOfEntDef,SGSimulationVariable):
            self.listOfEntDef.value=aValue
    
    def getUpdatePermission(self):
        if self.displayRefresh=='instantaneous':
            return True
        if self.displayRefresh=='withButton':
            return True
        if self.displayRefresh=='atSpecifiedPhases':  # TODO redescnedre d'un niveau le la condition 'displayRefresh' -->  self.displayRefresh
            # 'atSpecifiedPhases' a dict with type of conditions and specified value 
                # phaseName   (str or list of str)
                # phaseNumber (int or list of int)
                # lambdaTestOnPhaseNumber (a lambda function with syntax [ phaseNumber : test with phaseNumber])
                # roundNumber (int or list of int)
                # lambdaTestOnRound   (a lambda function with syntax [ roundNumber : test with roundNumber]=

                # Ex de la façon de coder le lambdaTestOnRound
                #     for typeCondition,specifiedValue in atSpecifiedPhases.items()
                #         if typeCondition == 'lambdaTestOnRound' :
                #             testResult = specifiedValue(self.model.roundNumber)
                #             return testResult

            self.userSetttingsOnPhaseToUpdate

    def getSizeXGlobal(self):
        return 150+len(self.name)*5
    
    def getListOfEntities(self):
        return [j for i in [entDef.entities for entDef in self.listOfEntDef] for j in i]  #This list comprehension expression concatenates the list of entities of all specified EntDef    
    
    def byMethod(self):
        calcValue=0.0
        counter=0
        
        if self.method =='nb':
            if self.attribute is not None and self.value is not None:
                listEntities = self.getListOfEntities()
                filteredList=[entity for entity in listEntities if entity.value(self.attribute)==self.value]
                return len(filteredList)
            else:
                listEntities = self.getListOfEntities()
                return len(listEntities)
        
        elif self.method in ["sumAtt","avgAtt","minAtt","maxAtt","nbWithLess","nbWithMore","nbEqualTo"]:
            listEntities = self.getListOfEntities()
            listOfValues = [aEnt.value(self.attribute) for aEnt in listEntities]
            if self.method == 'sumAtt': return sum(listOfValues)
            if self.method == 'avgAtt': return round(sum(listOfValues) / len(listOfValues),2)
            if self.method == 'minAtt': return min(listOfValues)
            if self.method == 'maxAtt': return max(listOfValues)
            if self.method == 'nbWithLess': return len([x for x in listOfValues if x < self.value])
            if self.method == 'nbWithMore': return len([x for x in listOfValues if x > self.value])
            if self.method == 'nbEqualTo': return len([x for x in listOfValues if x == self.value])

        elif self.method=="simVar":
            return self.simVar.value
        
        elif self.method =="display":
            return self.entity.value(self.attribute)
        elif self.method=="separator":
            return "---------------"
        elif self.method=="thresoldToLogicOp":
            # les indicator greater, greater or equal ect.. doivent etre codés comme les autres method
            if self.logicOp =="greater":
                if self.entity.value(self.attribute) > self.threshold:
                    calcValue="greater than"+str(self.threshold)
                    return calcValue
            if self.logicOp =="greater or equal":
                if self.entity.value(self.attribute)>=self.threshold:
                    calcValue="greater than or equal to"+str(self.threshold)
                    return calcValue
            if self.logicOp =="equal":
                if self.entity.value(self.attribute)==self.threshold:
                    calcValue="equal to"+str(self.threshold)
                    return calcValue
            if self.logicOp =="less or equal":
                if self.entity.value(self.attribute)<=self.threshold:
                    calcValue="less than or equal to"+str(self.threshold)
                    return calcValue
            if self.logicOp =="less":
                if self.entity.value(self.attribute)<self.threshold:
                    calcValue="less than"+str(self.threshold)
                    return calcValue   

    def getMethods(self):
        print(self.methods)


            

