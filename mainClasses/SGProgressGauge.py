from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
from PyQt5.QtWidgets import QMenu, QAction

from mainClasses.SGGameSpace import SGGameSpace


class SGProgressGauge(SGGameSpace):
    def __init__(self, parent, simVar, title, maximum, minimum, borderColor=Qt.black, backgroundColor=Qt.lightGray):
        super().__init__(parent, 0, 60, 0, 0, true, backgroundColor)
        self.title = title
        self.simVar = simVar
        self.maximum=maximum
        self.minimum=minimum
        self.borderColor = borderColor
        self.backgroundColor = backgroundColor
        