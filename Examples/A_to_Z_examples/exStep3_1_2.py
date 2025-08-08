import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(500,300, windowTitle="Add agents - other shape and other methods to add agents")

Cell=myModel.newCellsOnGrid(6,4,"square",gap=2,size=40)

Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)
Cell.newPov("base","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})

# In SGE a "type" of agent is called a species.
# To create a species, it needs : a name and a shape 
Sheeps=myModel.newAgentSpecies("Sheeps","circleAgent",defaultSize=10)
# available shapes are "circleAgent","squareAgent", "ellipseAgent1","ellipseAgent2", "rectAgent1","rectAgent2", "triangleAgent1","triangleAgent2", "arrowAgent1","arrowAgent2"

# Alternative ways to add agents
Sheeps.newAgentAtRandom()
Sheeps.newAgentsAtRandom(5)

aRandomCell = Cell.getRandomEntity()
Sheeps.newAgentOnCell(aRandomCell)

aRandomCell = Cell.getRandomEntity_withValue('landUse','shrub')
Sheeps.newAgentOnCell(aRandomCell)

aRandomCell = Cell.getRandomEntity_withValue('landUse','grass')
Sheeps.newAgentsOnCell(4, aRandomCell)

#This advance syntax uses lambda functin to specify a condition on the cell to be picked randomly
Sheeps.newAgentAtRandom(condition = lambda aCell: aCell.value('landUse')=='forest' and aCell.yCoord <= 2)


Legend=myModel.newLegend()

myModel.launch() 
sys.exit(monApp.exec_())
