from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from mainClasses.SGCell import SGCell


# Class who is responsible of the declaration of cells
class SGCellCollection():
    def __init__(self, parent, rows, columns, format, size, gap):
        # Basic initialize
        self.grid = parent
        self.rows = rows
        self.columns = columns
        self.format = format
        self.size = size
        self.gap = gap
        self.cells = {}
        self.watchers = {}
        # Initialize the different pov
        self.povs = {}
        self.borderPovs = {}
        self.borderPovs['selectedBorderPov'] = {}
        # Initialize of the user interface
        self.initUI()

    # Intialize all the cells who will be displayed
    def initUI(self):
        for i in range(1, self.rows + 1):
            for j in range(1, self.columns + 1):
                aCell = SGCell(self.grid, self, i, j,
                               self.format, self.size, self.gap)
                self.cells[aCell.getId()] = aCell

    # To get all the cells of the collection
    def getCells(self):
        return list(self.cells.values())

    # To get all the povs of the collection
    def getPovs(self):
        return {key: value for dict in (self.povs, self.borderPovs) for key, value in dict.items() if "selected" not in key and "borderWidth"not in key}

    # To get a cell in particular
    def getCell(self, aName):
        return self.cells[aName]

    # To remove a cell in particular
    def removeVisiblityCell(self, aName):
        self.getCell(aName).isDisplay = False
        self.grid.update()

    # To get all cells who is displayed
    def getCellsDisplay(self):
        res = []
        for cell in list(self.cells.values()):
            if cell.isDisplay == True:
                res.append(cell)
        return res

    # test
    def getWatchers(self):
        print(self.watchers)
