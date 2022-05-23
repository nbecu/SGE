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

myModel.setInitialPovGlobal("Forester")

theFirstGrid.setForRandom({"Forest":"Niv3"},30)

myModel.newAgent("lac","circleAgent",[theFirstGrid,theSecondGrid])

myModel.setUpCellValueAndPov("Forester",{"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},"lac","sea","reasonable",[theFirstGrid,theSecondGrid])


theFirstLegende=myModel.createLegendeAdmin()

myModel.timeManager.addGamePhase("theOnlyPhase",0,[],[lambda: myModel.getGameSpace("basicGrid").setForRandom({"Forest":"Niv1"},3)])







myModel.show() 

sys.exit(monApp.exec_())
