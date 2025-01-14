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
        self.simVar = simVar
        self.maximum=maximum
        self.minimum=minimum
        self.borderColor = borderColor
        self.backgroundColor = backgroundColor
        self.simVar.addWatcher(self)  # Ajout de l'observateur
        self.valueRange = maximum - minimum
        self.init_ui()
    
    def init_ui(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.title_label = QtWidgets.QLabel(self.title, self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(self.minimum)
        self.progress_bar.setMaximum(self.maximum)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.progress_bar)
        self.setLayout(self.layout)
        self.setWindowTitle(self.title)
        self.resize(300, 150)


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
        mappedValue = self.mapValue(newValue)
        self.progress_bar.setValue(int(mappedValue))
        self.progress_bar.setFormat(f"{newValue}")

    def mapValue(self, value):
        if self.minimum < 0:
            return (value - self.minimum) * (self.maximum / self.valueRange)
        return value


    # *Functions to have the global size of a gameSpace
    def getSizeXGlobal(self):
        return 300

    def getSizeYGlobal(self):
        return 150
        
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
        mappedValue = self.mapValue(newValue)
        self.progress_bar.setValue(int(mappedValue))
        self.progress_bar.setFormat(f"{newValue}")

    def mapValue(self, value):
        if self.minimum < 0:
            return (value - self.minimum) * (self.maximum / self.valueRange)
        return value


    # *Functions to have the global size of a gameSpace
    def getSizeXGlobal(self):
        return 300

    def getSizeYGlobal(self):
        return 150
