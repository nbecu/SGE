import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Example of POV

myModel=SGModel(1080,960,"grid")

theFirstGrid=myModel.createGrid("basicGrid",15,10,"hexagonal")

theFirstGrid.setColor(Qt.blue)

myModel.show() 

sys.exit(monApp.exec_())