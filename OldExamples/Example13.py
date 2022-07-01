import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Example of a simple

myModel=SGModel(1080,960,"horizontal")

theFirstGrid=myModel.createGrid("basicGrid",15,10,"hexagonal")

theFirstGrid.setColor(Qt.blue)

theSecondGrid=myModel.createGrid("Grid2",8,1)


theFirstGrid.setInPosition(2,1)

theSecondGrid.setInPosition(1,1)

"""print(theFirstGrid.startXbase)
print(theFirstGrid.startYbase)
print(theSecondGrid.startXbase)
print(theSecondGrid.startYbase)"""

myModel.applyPersonalLayout()   


"""print(theFirstGrid.startXbase)
print(theFirstGrid.startYbase)
print(theSecondGrid.startXbase)
print(theSecondGrid.startYbase)"""


myModel.show() 

sys.exit(monApp.exec_())