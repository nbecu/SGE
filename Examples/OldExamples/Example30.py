import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Example of 1 item and changing one column and one row

myModel=SGModel(1080,960,"grid")

theFirstGrid=myModel.createGrid("basicGrid",15,10,"hexagonal")

theFirstGrid.setColor(Qt.blue)


myModel.setUpPovOn("Basic",{"1":Qt.green,"2":Qt.red,"3":Qt.black},theFirstGrid)

myModel.setInitialPov("Basic")

theFirstGrid.setForRandom("Basic","2",3)

myModel.show() 

sys.exit(monApp.exec_())