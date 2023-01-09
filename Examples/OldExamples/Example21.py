import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Example of a simple

myModel=SGModel(1080,960,"grid")

theFirstGrid=myModel.createGrid(15,10,"hexagonal")

theFirstGrid.setColor(Qt.blue)

theFirstVoid=myModel.createVoid("void1")

theSecondGrid=myModel.createGrid("Grid2",8,8)

theSecondGrid.setColor(Qt.green)

myModel.show() 

sys.exit(monApp.exec_())