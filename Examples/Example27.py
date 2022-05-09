import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Example of 2 item with pov and change one pov

myModel=SGModel(1080,960,"grid")

theFirstGrid=myModel.createGrid("basicGrid",15,10,"hexagonal")

theFirstGrid.setColor(Qt.blue)

theSecondGrid=myModel.createGrid("Grid",8,6,"square")

myModel.setUpPovOn("Basic",{"1":Qt.green,"2":Qt.red},theFirstGrid,"2")

myModel.setUpPovOn("SecondBasic",{"1":Qt.blue,"2":Qt.black},theFirstGrid,"2")

myModel.setUpPovOn("Basic",{"1":Qt.gray,"2":Qt.red},theSecondGrid,"2")

myModel.setUpPovOn("SecondBasic",{"1":Qt.red,"2":Qt.black},theSecondGrid,"2")

myModel.setInitialPovGlobal("SecondBasic")

myModel.setInitialPovOn("Basic",theSecondGrid)

myModel.show() 

sys.exit(monApp.exec_())