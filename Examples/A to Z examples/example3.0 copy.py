import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="A board with hexagonal cells")

# You can change the specifications of the grid cells 
# For example you can change the shape of the cells
# As well as the number of cells (in column and in row), the size of a cell, the space in between cells...
aGrid=myModel.createGrid(2,4,"square",size=50, gap=0)
aGrid.setValueForCells({"landUse":"grass"})
aGrid.setForY({"landUse":"forest"},1)
""" aGrid.setForY({"landUse":"forest"},3)
aGrid.setForY({"landUse":"forest"},5) """

myModel.setUpPov("povLandUse",{"landUse":{"grass":Qt.green,"forest":Qt.darkGreen}})
myModel.setUpPov("povLandUse2",{"landUse":{"grass":Qt.green,"forest":Qt.darkGreen}})

theFirstLegend=myModel.createLegendAdmin()

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
