import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Example of a simple

myModel=SGModel(1080,960,"grid")

theFirstGrid=myModel.createGrid("basicGrid",15,10,"hexagonal")

theFirstGrid.setColor(Qt.blue)

theSecondGrid=myModel.createGrid("Grid2",8,8)

theSecondGrid.setColor(Qt.green)

thedGrid=myModel.createGrid("Grid3",8,12)

theSGrid=myModel.createGrid("Grid4",8,1)


"""theFirstGrid.setInPosition(3,1)

theSGrid.setInPosition(2,1)

theSecondGrid.setInPosition(1,1)

thedGrid.setInPosition(4,1)


myModel.applyPersonalLayout()"""



myModel.show() 

sys.exit(monApp.exec_())