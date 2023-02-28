import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="A simulation/game with one agent")

aGrid=myModel.createGrid(10,10,"square",size=60, gap=2)
aGrid.setValueForCells({"landUse":"grass"})
aGrid.setForX({"landUse":"forest"},1)
aGrid.setForX({"landUse":"forest"},2)
aGrid.setForRandom({"landUse":"shrub"},10)

myModel.setUpPov("povLandUse",{"landUse":{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen}})

# On top of the cells, you can add agents
# An agent has a location which is the cell on which it is placed. 
# An agent can move (or be moved) to another location.
# As for a cell, the modeller can specify attributes and values for each atttribute, as well as pov
myModel.newAgent("sheep","arrowAgent1",[aGrid])
myModel.setUpEntityValueAndPov("povLandUse",{"health":{"good":Qt.blue}},"sheep")

aGrid.addOnXandY("sheep",4,2) 
theFirstLegend=myModel.createLegendAdmin()

myModel.iAm("Admin")

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
