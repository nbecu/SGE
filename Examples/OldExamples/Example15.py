import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Example of a simple

myModel=SGModel(1080,960,"vertical")

theFirstGrid=myModel.createGrid(15,10,"hexagonal")

theFirstGrid.setColor(Qt.blue)

theSecondGrid=myModel.createGrid("Grid2",8,8)

theSecondGrid.setColor(Qt.green)

thedGrid=myModel.createGrid("Grid3",8,12)

theSGrid=myModel.createGrid("Grid4",8,1)


theFirstGrid.setInPosition(1,3)

theSGrid.setInPosition(1,2)

theSecondGrid.setInPosition(1,1)

thedGrid.setInPosition(1,4)


myModel.applyPersonalLayout() 



myModel.show() 

sys.exit(monApp.exec_())