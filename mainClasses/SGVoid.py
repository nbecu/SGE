from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from mainClasses.SGGameSpace import SGGameSpace


# Class who is responsible of the void creation in interface for layout management
class SGVoid(SGGameSpace):
    def __init__(self, parent, name, sizeX=200, sizeY=200):
        super().__init__(parent, 0, 0, 0, 0, False, Qt.transparent)
        # Basic initialize
        self.id = name
        self.sizeX = sizeX
        self.sizeY = sizeY

    # Funtion to have the global size of a gameSpace

    def getSizeXGlobal(self):
        return self.sizeX

    def getSizeYGlobal(self):
        return self.sizeY

    # Funtion to handle the zoom
    def zoomIn(self):
        return True

    def zoomOut(self):
        return True

    # To choose the inital pov
    def displayPov(self, nameOfPov):
        return True
