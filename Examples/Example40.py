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


theFirstGrid.setColor(Qt.gray)

myModel.setUpPovOn("Forester",{"Forest":{"Niv3":Qt.green,"Niv2":Qt.red,"Niv1":Qt.yellow},"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},theFirstGrid,"sea","reasonable")

myModel.setUpPovOn("Fireman",{"FireRisk":{"Niv2":Qt.black,"Niv1":Qt.gray}},theFirstGrid)

theFirstGrid.setForRandom("Forester",{"Forest":"Niv3"},30)
myModel.setInitialPovGlobal("Forester")


theFirstLegende=myModel.createLegendeAdmin()
theFirstLegende.addDeleteButton()



theSecondLegend=myModel.createLegendeForPlayer("theTestLegende",{"basicGrid":{"Forester":{"Forest":{"Niv3":Qt.green}}}})

theSecondLegend.addToTheLegende({"basicGrid":{"Forester":{"Forest":{"Niv2":Qt.red}}}})

theSecondLegend.addDeleteButton()


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
