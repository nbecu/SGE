from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
from PyQt5.QtWidgets import QProgressBar

from mainClasses.SGGameSpace import SGGameSpace


class SGProgressGauge(SGGameSpace):
    def __init__(self, parent, simVar, title, maximum, minimum, borderColor=Qt.black, backgroundColor=Qt.lightGray):
        super().__init__(parent, 0, 60, 0, 0, true, backgroundColor)
        self.title = title
        self.id = title
        self.model = parent
        self.simVar = simVar
        self.maximum=maximum
        self.minimum=minimum
        self.borderColor = borderColor
        self.backgroundColor = backgroundColor
        self.simVar.addWatcher(self)  # Ajout de l'observateur
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
        # self.progress_bar.setFormat(f"{int(self.simVar.value)}")
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.progress_bar)
        self.setLayout(self.layout)
        self.setWindowTitle(self.title)
        self.progress_bar.setValue(int(self.getMappedValue(str(self.simVar.value))))
        self.resize(300, 150)
        self.show()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QBrush(self.backgroundColor, Qt.SolidPattern))
        painter.setPen(QPen(self.borderColor, 1))
        # Draw the corner of the Legend
        self.setMinimumSize(self.getSizeXGlobal()+3,
                            self.getSizeYGlobal()+3)
        painter.drawRect(0, 0, self.getSizeXGlobal(),
                            self.getSizeYGlobal())
        painter.end()


    def checkAndUpdate(self):
        self.updateProgressBar()

    def updateProgressBar(self):
        newValue = self.simVar.value
        mappedValue = self.getMappedValue(str(newValue))
        # mappedValue = self.mapValue(newValue)
        self.progress_bar.setValue(int(mappedValue))
        # self.progress_bar.setFormat(f"{newValue}")
        self.checkThresholds(newValue)

    def setThresholdValue(self, thresholdValue, aLambdaFunctionForCrossingUp=None, aLambdaFunctionForCrossingDown=None):
        self.thresholds[thresholdValue] = [aLambdaFunctionForCrossingUp, aLambdaFunctionForCrossingDown]

    def checkThresholds(self, newValue):
        for threshold, (crossUp, crossDown) in self.thresholds.items():
            if newValue >= int(threshold) and (self.previousValue is None or self.previousValue < int(threshold)):
                if crossUp:
                    crossUp()
            elif newValue < int(threshold) and (self.previousValue is None or self.previousValue >= int(threshold)):
                if crossDown:
                    crossDown()
        self.previousValue = newValue

    def setDictOfMappedValues(self,aDictOfMappedValues):
        self.dictOfMappedValues = aDictOfMappedValues

    def getMappedValue(self, key):
        value = self.dictOfMappedValues.get(key)
        if value is not None: return value
        else: return 0 

    def mapValueOld(self, value):
        if self.minimum < 0:
            return (value - self.minimum) * (self.maximum / self.valueRange)
        return value

    def mapValue(self, value):
        return (value - self.minimum) * 100 / self.valueRange

     # *Functions to have the global size of a gameSpace
    def getSizeXGlobal(self):
        return 300

    def getSizeYGlobal(self):
        return 150

