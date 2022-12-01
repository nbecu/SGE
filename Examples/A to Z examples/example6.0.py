import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
monApp=QtWidgets.QApplication([])


myModel=SGModel(800,800, windowTitle="à vous de jouer")

aGrid=myModel.createGrid("the name of the grid",7,10,"square",size=60, gap=2)
aGrid.setValueForCells({"landUse":"grass"})
aGrid.setForX({"landUse":"forest"},1)
aGrid.setForX({"landUse":"forest"},2)
aGrid.setForRandom({"landUse":"shrub"},10)

myModel.setUpPov("povLandUse",{"landUse":{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen}})
myModel.setUpPov("povLandUse2",{"landUse":{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen}})

p1= myModel.createPlayer("farmer")
p1.addGameAction(myModel.createUpdateAction(aGrid.getACell(),2,{"landUse":"grass"}))
myModel.timeManager.addGamePhase("the First Phase",0,p1)


theFirstLegend=myModel.createLegendAdmin()

myModel.iAm("farmer")

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
