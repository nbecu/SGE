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

theFirstGrid=myModel.createGrid("basicGrid",10,10,"hexagonal")


theFirstGrid.setColor(Qt.green)

myModel.setUpPovOn("Basic",{"Forest":{"Niv3":Qt.green,"Niv2":Qt.red,"Niv1":Qt.black}},theFirstGrid)

myModel.setUpPovOn("oui",{"test":Qt.gray,"test2":Qt.black},theFirstGrid)

myModel.setInitialPov("Basic")

theFirstLegend=myModel.createLegendForPlayer("theTestLegend",{"basicGrid":{"Basic":{"1":Qt.green}}})

theFirstLegend.addToTheLegend({"basicGrid":{"Basic":{"testDunNomLong":Qt.red}}})

theFirstLegend.addDeleteButton()

myModel.newAgent("circleTest","circleAgent",[theFirstGrid])

myModel.setUpPovOn("Basic",{"1":Qt.red,"testDunNomLong":Qt.red},"circleTest","1",[theFirstGrid])


theFirstGrid.addOnXandY("circleTest",1,1)
theFirstGrid.addOnXandY("circleTest",2,2)
theFirstGrid.addOnXandY("circleTest",7,7)
theFirstGrid.addOnXandY("circleTest",4,2)
theFirstGrid.addOnXandY("circleTest",10,9)
theFirstGrid.addOnXandY("circleTest",1,8)




myModel.show() 

sys.exit(monApp.exec_())
