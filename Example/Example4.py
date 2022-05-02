import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Example of a simple square grid with a multipov pov 

myModel=SGModel(640,480)

myModel.Grid.initializeTheGrid(10,10,"square")

myModel.Grid.initANewPovForCell("Basic")

cellsBasic=myModel.Grid.getCellsOfPov("Basic")

cellsBasic.setColorDefault(Qt.red)

myModel.Grid.initANewPovForCell("grass")

cellsGrass=myModel.Grid.getCellsOfPov("grass")

cellsGrass.setColorDefault(Qt.green)

myModel.Grid.setInitialPov("Basic")

myModel.show() 

sys.exit(monApp.exec_())