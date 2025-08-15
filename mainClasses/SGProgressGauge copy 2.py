from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
from PyQt5.QtWidgets import QProgressBar

from mainClasses.SGGameSpace import SGGameSpace

class SGProgressGauge(SGGameSpace):
    def __init__(self, parent, simVar, title, maximum, minimum, 
                 borderColor=Qt.black, backgroundColor=Qt.lightGray,
                 orientation="horizontal", colorRanges=None):
        super().__init__(parent, 0, 60, 0, 0, True, backgroundColor)
        self.title = title
        self.id = title
        self.model = parent
        self.simVar = simVar
        self.maximum = maximum
        self.minimum = minimum
        self.borderColor = borderColor
        self.backgroundColor = backgroundColor
        self.orientation = orientation
        self.colorRanges = colorRanges or []
        self.simVar.addWatcher(self)
        self.valueRange = maximum - minimum
        self.thresholds = {}
        self.previousValue = self.simVar.value
        self.dictOfMappedValues = {}
        self.init_ui()

    def init_ui(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.title_label = QtWidgets.QLabel(self.title, self)
        self.title_label.setAlignment(Qt.AlignCenter)
        font = self.title_label.font()
        font.setPointSize(font.pointSize() + 3)
        self.title_label.setFont(font)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(self.minimum)
        self.progress_bar.setMaximum(self.maximum)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setFormat(f"{int(self.simVar.value)}")

        if self.orientation.lower() == "vertical":
            self.progress_bar.setOrientation(Qt.Vertical)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.progress_bar)
        self.setLayout(self.layout)

        self.updateProgressBar()
        self.resize(300, 150)
        self.show()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(self.backgroundColor, Qt.SolidPattern))
        painter.setPen(QPen(self.borderColor, 1))
        self.setMinimumSize(self.getSizeXGlobal() + 3, self.getSizeYGlobal() + 3)
        painter.drawRect(0, 0, self.getSizeXGlobal(), self.getSizeYGlobal())

    def checkAndUpdate(self):
        self.updateProgressBar()


    def updateProgressBar(self):
        newValue = self.simVar.value
        mappedValue = self.getMappedValue(str(newValue))
        self.progress_bar.setValue(int(mappedValue))
        self.progress_bar.setFormat(f"{newValue}")

        # Changement de couleur selon plage
        for min_val, max_val, color in self.colorRanges:
            if min_val <= newValue <= max_val:
                self.progress_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")
                break

        self.checkThresholds(newValue)


    def mapValue(self, value):
        """Convertit une valeur de simulation en [0,100]"""
        if self.dictOfMappedValues:
            return self.dictOfMappedValues.get(str(value), 0)
        # Mapping linéaire auto
        return ((value - self.minimum) / self.valueRange) * 100

    def setThresholdValue(self, thresholdValue, aLambdaFunctionForCrossingUp=None, aLambdaFunctionForCrossingDown=None):
        self.thresholds[thresholdValue] = [aLambdaFunctionForCrossingUp, aLambdaFunctionForCrossingDown]

    def checkThresholds(self, newValue):
        for threshold, (crossUp, crossDown) in self.thresholds.items():
            if newValue >= threshold and (self.previousValue is None or self.previousValue < threshold):
                if crossUp: crossUp()
            elif newValue < threshold and (self.previousValue is None or self.previousValue >= threshold):
                if crossDown: crossDown()
        self.previousValue = newValue

    def setDictOfMappedValues(self, aDictOfMappedValues):
        self.dictOfMappedValues = aDictOfMappedValues

    def getSizeXGlobal(self):
        return 300

    def getSizeYGlobal(self):
        return 150
