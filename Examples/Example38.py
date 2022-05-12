import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Example of Agents


myModel=SGModel(1080,960,"grid")

theFirstGrid=myModel.createGrid("basicGrid",15,10,"hexagonal")


theFirstGrid.setColor(Qt.blue)

myModel.setUpPovOn("Basic",{"1":Qt.green,"testDunNomLong":Qt.red,"3":Qt.red},theFirstGrid)

myModel.setUpPovOn("oui",{"test":Qt.gray,"test2":Qt.black},theFirstGrid)

myModel.setInitialPovGlobal("Basic")

theFirstLegende=myModel.createLegendeForPlayer("theTestLegende",{"basicGrid":{"Basic":{"1":Qt.green}}})

theFirstLegende.addToTheLegende({"basicGrid":{"Basic":{"testDunNomLong":Qt.red}}})

theFirstLegende.addDeleteButton()

#-----------------------------
myModel.listeOfActionForNextTurn.append(SGModel.aTestForTimeManager)

myModel.show() 

sys.exit(monApp.exec_())