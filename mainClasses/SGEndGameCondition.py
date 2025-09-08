from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from mainClasses.SGIndicator import SGIndicator
from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell


# Class who is responsible of indicator creation
class SGEndGameCondition(QtWidgets.QWidget):
    def __init__(self, parent, name, entity, method, objective, attribut, color, calcType, isDisplay):
        super().__init__(parent)
        # Basic initialize
        self.endGameRule = parent
        self.method = method
        self.objective = objective
        self.calcType = calcType
        self.entity = entity
        self.name = name
        self.attribut = attribut
        self.color = color
        self.id = int
        self.checkStatus = False
        self.isDisplay = isDisplay
        self.initUI()

    def initUI(self):
        if self.isDisplay:
            self.conditionLayout = QtWidgets.QHBoxLayout()
            # Use QLabel instead of QTextEdit for more appropriate sizing
            self.label = QtWidgets.QLabel(self.name)
            # Enable word wrap if text is too long
            if len(self.name) > 50:  # Arbitrary threshold to decide on word wrapping
                self.label.setWordWrap(True)
            else:
                self.label.setWordWrap(False)
            color = self.endGameRule.title1_aspect.color
            color_string = f"color: {color};"
            self.label.setStyleSheet(
                color_string+"border: none;background-color: lightgray;")
            self.conditionLayout.addWidget(self.label)

    def updateText(self):
        self.verifStatus()
        if self.checkStatus:
            # Use success theme instead of hardcoded color
            color = self.endGameRule.success_aspect.color
            color_string = f"color: {color};"
            self.label.setStyleSheet(
                color_string+"border: none;background-color: lightgray;")

    def getUpdatePermission(self):
        if self.endGameRule.displayRefresh == 'instantaneous':
            return True
        if self.endGameRule.displayRefresh == 'withButton':
            return True

    def getSizeXGlobal(self):
        # Calculate more appropriate size based on actual content
        if hasattr(self, 'label') and self.label:
            # Use size suggested by QLabel
            size_hint = self.label.sizeHint()
            if size_hint.isValid():
                return size_hint.width() + 20  # Add small margin
        # Fallback: calculation based on text length
        return min(len(self.name) * 8 + 20, 200)  # Limit maximum size
    
    def getSizeYGlobal(self):
        # Calculate appropriate height
        if hasattr(self, 'label') and self.label:
            # Use size suggested by QLabel
            size_hint = self.label.sizeHint()
            if size_hint.isValid():
                return size_hint.height() + 10  # Add small margin
        # Fallback: standard height for one line of text
        return 25

    def byCalcType(self):
        if self.calcType == 'onIndicator':
            if isinstance(self.entity, SGIndicator):
                valueToCheck = self.entity.result
                if self.logicalTests(valueToCheck, self.method, self.objective):
                    self.checkStatus = True
                    return
            else:
                print('Error, not an Indicator')
                return
        if self.calcType == 'onEntity':
            if isinstance(self.entity, SGCell):
                valueToCheck = self.entity.dictAttributes[self.attribut]
                if type(valueToCheck) == str:
                    valueToCheck = int(valueToCheck)
                if self.logicalTests(valueToCheck, self.method, self.objective):
                    self.checkStatus = True
                    return
            if isinstance(self.entity, SGAgent):
                print("To be implemented...")
        if self.calcType == "onGameRound":
            valueToCheck = self.endGameRule.model.timeManager.currentRoundNumber
            if self.logicalTests(valueToCheck, self.method, self.objective):
                self.checkStatus = True
                return
        if self.calcType == "onLambda":
            if callable(self.method):
                if self.method():
                    self.checkStatus = True
                    return
            else:
                print("Error, method is not callable")
                return

    def logicalTests(self, valueToCheck, logicalTest, objective):
        if logicalTest == 'equal':
            if valueToCheck == objective:
                return True
        elif logicalTest == 'greater':
            if valueToCheck > objective:
                return True
        elif logicalTest == 'less':
            if valueToCheck < objective:
                return True
        elif logicalTest == 'greater or equal':
            if valueToCheck >= objective:
                return True
        elif logicalTest == 'less or equal':
            if valueToCheck <= objective:
                return True
        return False

    def verifStatus(self):
        self.byCalcType()