import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Example of zoomToFit


myModel=SGModel(1080,960,"grid")

"""theFirstGrid=myModel.createGrid("basicGrid",15,10,"hexagonal")

theFirstGrid=myModel.createGrid("2",15,10,"hexagonal")

theFirstGrid=myModel.createGrid("3",15,10,"hexagonal")

theFirstGrid=myModel.createGrid("4",15,10,"hexagonal")

theFirstGrid=myModel.createGrid("5",15,10,"hexagonal")"""

theFirstGrid=myModel.createGrid("basicGrid",4,4,"square",3,10)

myModel.show() 

sys.exit(monApp.exec_())