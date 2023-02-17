import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="About legend (2)")

aGrid=myModel.createGrid(10,10,"square",size=60, gap=2,name='mygrid')
aGrid.setValueForCells({"landUse":"grass"})
aGrid.setForX({"landUse":"forest"},1)
aGrid.setForX({"landUse":"forest"},2)
aGrid.setForRandom({"landUse":"shrub"},10)

myModel.setUpPov("povLandUse",{"landUse":{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen}})
myModel.setUpPov("povLandUse2",{"landUse":{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen}})

theFirstLegend=myModel.createLegendAdmin()
# create a player
myModel.createPlayer("Player 1")
# create a legend for this player, according to the POVs
#Player1Leg=myModel.createLegendForPlayer("Player1Legend",{"mygrid":{'povLandUse':{"grass":Qt.green}}},"Player 1")
#Player1Leg.addDeleteButton('Delete')


# to have the Player 1 view 
myModel.iAm("Player 1")
#myModel.iAm("Admin")

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
