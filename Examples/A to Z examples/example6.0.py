import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(800,800, windowTitle="Adding a player with game actions")

aGrid=myModel.createGrid(7,10,"square",size=60, gap=2)
aGrid.setValueForCells({"landUse":"grass"})
aGrid.setForX({"landUse":"forest"},1)
aGrid.setForX({"landUse":"forest"},2)
aGrid.setForRandom({"landUse":"shrub"},10)

myModel.setUpPov("povLandUse",{"landUse":{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen}})
myModel.setUpPov("povLandUse2",{"landUse":{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen}})

# You can add a player and give him game actions which he can perform
# The name of the game action indicates the type of the action: cellUpdate, agentMove,...
# For any game action type, you can specify the number of time the action can be used at each turn, usage restrictions, feedbacks that are executed after the action is performed and conditions for applying this feedback 
p1= myModel.createPlayer("farmer")
p1.addGameAction(myModel.createUpdateAction(aGrid.getACell(),2,{"landUse":"grass"}))

# A game phase allow to specify which user can play during the given phase
myModel.timeManager.addGamePhase("the First Phase",0,p1)

#theFirstLegend=myModel.createLegendAdmin()
myModel.iAm("farmer")

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
