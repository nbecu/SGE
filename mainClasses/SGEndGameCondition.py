from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null
import numpy as np

from SGIndicators import SGIndicators
from SGAgent import SGAgent
from SGCell import SGCell


   
#Class who is responsible of indicator creation 
class SGEndGameCondition(QtWidgets.QWidget):
    def __init__(self,parent,name,entity,method,objective,attribut,color,calcType,isDisplay):
        super().__init__(parent)
        #Basic initialize
        self.endGameRule=parent
        self.method=method
        self.objective=objective
        self.calcType=calcType
        self.entity=entity
        self.name=name
        self.attribut=attribut
        self.color=color
        self.id=int
        self.checkStatus=False
        self.isDisplay=isDisplay
        self.initUI()
        

    def initUI(self):
        if self.isDisplay:
            self.conditionLayout = QtWidgets.QHBoxLayout()
            self.name='test' #self.setName()
            self.label = QtWidgets.QTextEdit(self.name)
            self.label.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.label.setReadOnly(True)
            color = QColor(self.endGameRule.textColor)
            color_string = f"color: {color.name()};"
            self.label.setStyleSheet(color_string)
            self.conditionLayout.addWidget(self.label)

    def setName(self):
        if self.attribut is not None:
            aName = self.entity + self.method+' '+self.attribut
        else:
            aName=self.method+' '+self.entity+" : "+str()+'/'+str(self.objective)
        return aName

    def updateText(self):
        """newCalc=self.byMethod()
        newText= self.setName(newCalc)
        self.label.setPlainText(newText)"""
        self.verifStatus()
        if self.checkStatus:
            color = QColor(Qt.green)
            color_string = f"color: {color.name()};"
            self.label.setStyleSheet(color_string)
    
    def getUpdatePermission(self):
        if self.endGameRule.displayRefresh=='instantaneous':
            return True
        if self.endGameRule.displayRefresh=='withButton':
            return True

    def getSizeXGlobal(self):
        return 150+len(self.name)*5
    
    def byCalcType(self):
        if self.calcType=='onIndicator':
            if isinstance(self.entity,SGIndicators):
                valueToCheck=self.entity.result
                if self.logicalTests(valueToCheck,self.method,self.objective):
                    self.checkStatus=True
                    return
            else :
                print('Error, not an Indicator')
                return
        if self.calcType=='onEntity':
            if isinstance(self.entity,SGCell):
                valueToCheck=self.entity.attributs[self.attribut]
                if type(valueToCheck)==str:
                    valueToCheck=int(valueToCheck)
                if self.logicalTests(valueToCheck,self.method,self.objective):
                    self.checkStatus=True
                    return
            if isinstance(self.entity,SGAgent):
                print("To be implemented...")
        if self.calcType=="onGameRound":
            valueToCheck=self.endGameRule.model.timeManager.getRoundNumber()
            if self.logicalTests(valueToCheck,self.method,self.objective):
                self.checkStatus=True
                return




    def logicalTests(self,valueToCheck,logicalTest,objective):
        if logicalTest == 'equal':
            if valueToCheck == objective:
                return True
        elif logicalTest == 'greater':
            if valueToCheck>objective:
                return True
        elif logicalTest == 'less':
            if valueToCheck<objective:
                return True
        elif logicalTest == 'greater or equal':
            if valueToCheck>=objective:
                return True
        elif logicalTest == 'less or equal':
            if valueToCheck<=objective:
                return True
        return False
     
    def verifStatus(self):
        self.byCalcType()
