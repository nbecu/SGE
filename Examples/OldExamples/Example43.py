import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Simple example of the timeManager


myModel=SGModel(1080,960,"grid")

theFirstGrid=myModel.createGrid("basicGrid",10,10,"hexagonal",Qt.gray)

theSecondGrid=myModel.createGrid("theSecondGrid",4,4,"square",Qt.gray)

myModel.setUpCellValueAndPov("Forester",{"Forest":{"Niv3":Qt.green,"Niv2":Qt.red,"Niv1":Qt.yellow},"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},[theFirstGrid,theSecondGrid],"sea","reasonable")

myModel.setInitialPov("Forester")

theFirstGrid.setForRandom({"Forest":"Niv3"},30)

myModel.newAgent("lac","circleAgent",[theFirstGrid,theSecondGrid])

myModel.setUpCellValueAndPov("Forester",{"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},"lac","sea","reasonable",[theFirstGrid,theSecondGrid])


theFirstLegend=myModel.createLegendAdmin()

myModel.timeManager.addGamePhase("theFirstPhase",0,[],[lambda: myModel.getGameSpace("basicGrid").setForRandom({"Forest":"Niv1"},3)])

myModel.timeManager.addGamePhase("theSecondPhase",1,[],[lambda: myModel.getGameSpace("basicGrid").setForRandom({"Forest":"Niv2"},3)],[lambda: myModel.getTimeManager().verifNumberOfRound(3)])

myModel.timeManager.addGamePhase("theThirdPhase",2,[],[lambda: myModel.getGameSpace("basicGrid").setForRandom({"Forest":"Niv3"},10)],[lambda: myModel.getTimeManager().actualRound ==1])







myModel.show() 

sys.exit(monApp.exec_())
