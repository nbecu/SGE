import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Simple example of applying attributs to cell before set up the povs

myModel=SGModel(1080,960,"grid")

#For the grid
theFirstGrid=myModel.createGrid("basicGrid",10,10,"hexagonal",Qt.gray)

theFirstGrid.setValueForCells({"Forest":"Niv1"})

theFirstGrid.setForXandY({"Forest":"Niv2"},2,2)

theFirstGrid.setForX({"Forest":"Niv2"},1)

theFirstGrid.setForY({"Forest":"Niv2"},1)

theFirstGrid.setForRandom({"Forest":"Niv3"},3)

myModel.setUpPov("Forester",{"Forest":{"Niv3":Qt.green,"Niv2":Qt.red,"Niv1":Qt.yellow},"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},[theFirstGrid])

myModel.setInitialPovGlobal("Forester")

#For the Agent
anAgentLac=myModel.newAgent("lac","circleAgent",[theFirstGrid])

theFirstGrid.setValueForModelAgents("lac",{"boat":"new"})

myModel.setUpPov("Forester",{"boat":{"new":Qt.blue,"old":Qt.cyan}},"lac",[theFirstGrid])

theFirstGrid.addOnXandY("lac",1,1)

theFirstLegend=myModel.createLegendAdmin()

myModel.timeManager.addGamePhase("theFirstPhase",0,None,[lambda: myModel.getGameSpace("basicGrid").setForRandom({"Forest":"Niv1"},3)])

myModel.iAm("Admin")

myModel.launch()  

sys.exit(monApp.exec_())
