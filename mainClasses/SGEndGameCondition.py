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
            self.conditionLayout.setContentsMargins(0, 0, 0, 0)
            self.conditionLayout.setSpacing(6)
            # Status/check label (initially hidden)
            self.statusLabel = QtWidgets.QLabel("")
            self.statusLabel.setVisible(False)
            self.statusLabel.setStyleSheet("color: #2e7d32; font-weight: bold;")
            self.conditionLayout.addWidget(self.statusLabel)
            # Main text label
            self.label = QtWidgets.QLabel(self.name)
            # Enable word wrap if text is too long
            if len(self.name) > 50:  # Arbitrary threshold to decide on word wrapping
                self.label.setWordWrap(True)
            else:
                self.label.setWordWrap(False)
            # Do not force background on child label; container handles background in paintEvent
            self.label.setStyleSheet("border: none;")
            self.conditionLayout.addWidget(self.label)

    def updateText(self):
        self.verifStatus()
        if self.checkStatus:
            # Indicate validation with a green check mark label on the left
            color = self.endGameRule.success_aspect.color
            self.statusLabel.setText("✓")
            # Apply green from success aspect if available
            self.statusLabel.setStyleSheet(f"color: {color}; font-weight: bold;")
            self.statusLabel.setVisible(True)
        else:
            self.statusLabel.setVisible(False)
        # Ask parent to update its size from layout
        if hasattr(self.endGameRule, 'updateSizeFromLayout'):
            self.endGameRule.updateSizeFromLayout(self.endGameRule.layout)
        self.endGameRule.update()

    def getUpdatePermission(self):
        if self.endGameRule.displayRefresh == 'instantaneous':
            return True
        if self.endGameRule.displayRefresh == 'withButton':
            return True

    def getSizeXGlobal(self):
        # Prefer layout size if available
        if hasattr(self, 'conditionLayout') and self.conditionLayout:
            self.conditionLayout.activate()
            size_hint = self.conditionLayout.sizeHint()
            if size_hint.isValid():
                return size_hint.width() + 10
        # Fallback: include status label + text label
        width = 0
        if hasattr(self, 'statusLabel') and self.statusLabel:
            sh = self.statusLabel.sizeHint()
            if sh.isValid():
                width += sh.width() + 6
        if hasattr(self, 'label') and self.label:
            sh = self.label.sizeHint()
            if sh.isValid():
                width += sh.width()
        return max(width, 100)
    
    def getSizeYGlobal(self):
        # Prefer layout height if available
        if hasattr(self, 'conditionLayout') and self.conditionLayout:
            self.conditionLayout.activate()
            size_hint = self.conditionLayout.sizeHint()
            if size_hint.isValid():
                return size_hint.height() + 6
        # Fallback
        if hasattr(self, 'label') and self.label:
            sh = self.label.sizeHint()
            if sh.isValid():
                return sh.height() + 6
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