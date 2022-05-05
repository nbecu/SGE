import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Example of a simple

myModel=SGModel(1080,960,"Grid")

theFirstGrid=myModel.createGrid("basicGrid",15,10,"hexagonal")

theFirstGrid.setColor(Qt.blue)

theSecondGrid=myModel.createGrid("Grid2",8,1)

thedGrid=myModel.createGrid("Grid3",8,1)

theSGrid=myModel.createGrid("Grid4",8,1)


"""theFirstGrid.setInPosition(1,1)

theSecondGrid.setInPosition(1,2)"""


"""
myModel.applyPersonalLayout()  """ 



myModel.show() 

sys.exit(monApp.exec_())