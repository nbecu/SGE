import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Example of a simple

myModel=SGModel(640,480,"horizontal")

theFirstGrid=myModel.createGrid("basicGrid")

theFirstGrid.setColor(Qt.blue)

theSecondGrid=myModel.createGrid("Grid2")

myModel.show() 

sys.exit(monApp.exec_())