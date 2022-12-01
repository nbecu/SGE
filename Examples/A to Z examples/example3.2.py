import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
monApp=QtWidgets.QApplication([])
#removed the default values : grid and initialPov


myModel=SGModel(860,700, windowTitle="à vous de jouer")

aGrid=myModel.createGrid("the name of the grid",10,10,"hexagonal",size=30, gap=2)
aGrid.setValueForCells({"landUse":"grass"})
aGrid.setForX({"landUse":"forest"},1)
aGrid.setForX({"landUse":"forest"},2)
aGrid.setForRandom({"landUse":"shrub"},10)

myModel.setUpPov("povLandUse",{"landUse":{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen}})
myModel.setUpPov("povLandUse2",{"landUse":{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen}})


theFirstLegend=myModel.createLegendAdmin()
# the admin's legend enables to change all the entities without restrictions
# it will be displayed only for an Admin user.
# By default, a model user is an Admin user
# To specify another status add the instruction -> myModel.iAm("Name of the player")
# To come back to Admin user status, type the instruction -> myModel.iAm("Admin")

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
