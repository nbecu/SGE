import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Example of rework POVS CEll


myModel=SGModel(1080,960,"grid")

theFirstGrid=myModel.createGrid("basicGrid",10,10,"hexagonal")


theFirstGrid.setColor(Qt.green)

myModel.setUpPovOn("Forester",{"Forest":{"Niv3":Qt.green,"Niv2":Qt.red,"Niv1":Qt.yellow},"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},theFirstGrid,"sea","reasonable")

myModel.setUpPovOn("Fireman",{"FireRisk":{"Niv2":Qt.black,"Niv1":Qt.gray}},theFirstGrid)

myModel.setInitialPovGlobal("Forester")

"""
theFirstLegende=myModel.createLegendeForPlayer("theTestLegende",{"basicGrid":{"Basic":{"1":Qt.green}}})

theFirstLegende.addToTheLegende({"basicGrid":{"Basic":{"testDunNomLong":Qt.red}}})

theFirstLegende.addDeleteButton()"""
"""
myModel.newAgent("circleTest","circleAgent",[theFirstGrid])

myModel.setUpPovOn("Basic",{"1":Qt.red,"testDunNomLong":Qt.red},"circleTest","1",[theFirstGrid])


theFirstGrid.addOnXandY("circleTest",1,1)
theFirstGrid.addOnXandY("circleTest",2,2)
theFirstGrid.addOnXandY("circleTest",7,7)
theFirstGrid.addOnXandY("circleTest",4,2)
theFirstGrid.addOnXandY("circleTest",10,9)
theFirstGrid.addOnXandY("circleTest",1,8)

"""


myModel.show() 

sys.exit(monApp.exec_())
