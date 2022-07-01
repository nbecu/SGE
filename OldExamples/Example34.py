import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Example of add a legende personalise


myModel=SGModel(1080,960,"grid")

theFirstGrid=myModel.createGrid("basicGrid",15,10,"hexagonal")

theFirstGrid2=myModel.createGrid("qs",15,10,"hexagonal")
theFirstGrid3=myModel.createGrid("ds",15,10,"hexagonal")
theFirstGrid4=myModel.createGrid("dqs",15,10,"hexagonal")

theFirstGrid.setColor(Qt.blue)

myModel.setUpPovOn("Basic",{"1":Qt.green,"testDunNomLong":Qt.red,"3":Qt.red},theFirstGrid,"2")

myModel.setUpPovOn("oui",{"test":Qt.gray,"test2":Qt.black},theFirstGrid,"2")

myModel.setUpPovOn("Basic",{"1":Qt.green,"testDunNomLong":Qt.red,"3":Qt.red},theFirstGrid2,"2")

myModel.setUpPovOn("oui",{"test":Qt.gray,"test2":Qt.black},theFirstGrid2,"2")

myModel.setUpPovOn("Basic",{"1":Qt.green,"testDunNomLong":Qt.red,"3":Qt.red},theFirstGrid3,"2")

myModel.setUpPovOn("oui",{"test":Qt.gray,"test2":Qt.black},theFirstGrid3,"2")

myModel.setUpPovOn("Basic",{"1":Qt.green,"testDunNomLong":Qt.red,"3":Qt.red},theFirstGrid4,"2")

myModel.setUpPovOn("oui",{"test":Qt.gray,"test2":Qt.black},theFirstGrid4,"2")

theFirstGrid.setInPosition(1,1)

theFirstGrid2.setInPosition(1,3)

theFirstGrid3.setInPosition(2,1)

theFirstGrid4.setInPosition(2,2)









myModel.setInitialPovGlobal("Basic")

theFirstLegende=myModel.createLegendeForPlayer("theTestLegende",{"basicGrid":{"Basic":{"1":Qt.green}}})

theFirstLegende.setInPosition(1,2)

myModel.applyPersonalLayout() 

myModel.show() 

sys.exit(monApp.exec_())