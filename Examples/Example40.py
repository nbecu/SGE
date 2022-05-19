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

theFirstGrid=myModel.createGrid("basicGrid",10,10,"hexagonal",Qt.gray)

theSecondGrid=myModel.createGrid("secondGrid",10,10,"square")


myModel.setUpPovOn("Forester",{"Forest":{"Niv3":Qt.green,"Niv2":Qt.red,"Niv1":Qt.yellow},"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},[theFirstGrid,theSecondGrid],"sea","reasonable")

myModel.setUpPovOn("Fireman",{"FireRisk":{"Niv2":Qt.black,"Niv1":Qt.gray}},[theFirstGrid,theSecondGrid])

myModel.setInitialPovGlobal("Forester")

theFirstGrid.setForRandom({"Forest":"Niv3"},30)






myModel.newAgent("lac","circleAgent",[theFirstGrid])

myModel.setUpPovOn("Forester",{"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},"lac","sea","reasonable",[theFirstGrid])
myModel.setUpPovOn("Fireman",{"FireRisk":{"Niv2":Qt.black,"Niv1":Qt.gray}},"lac","FireRisk","Niv2",[theFirstGrid])


theFirstLegende=myModel.createLegendeAdmin()
theFirstLegende.addDeleteButton()




theSecondLegend=myModel.createLegendeForPlayer("theTestLegende",{"basicGrid":{"Forester":{"Forest":{"Niv3":Qt.green}}}})

theSecondLegend.addToTheLegende({"basicGrid":{"Forester":{"Forest":{"Niv2":Qt.red}}}})

theSecondLegend.addAgentToTheLegend("lac")


theSecondLegend.addDeleteButton()

theFirstGrid.addOnXandY("lac",1,1)
theFirstGrid.addOnXandY("lac",2,2,"deep sea")



myModel.show() 

sys.exit(monApp.exec_())
