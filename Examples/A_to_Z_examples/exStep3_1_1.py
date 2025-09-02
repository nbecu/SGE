import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(500,300, windowTitle="Add agents to your simulation/game")

Cell=myModel.newCellsOnGrid(6,4,"square",gap=2,size=40)

Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)
Cell.newPov("base","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})

# In SGE a "type" of agent is called a species.
# To create a species, it needs : a name and a shape 
Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1")
# available shapes are "circleAgent","squareAgent", "ellipseAgent1","ellipseAgent2", "rectAgent1","rectAgent2", "triangleAgent1","triangleAgent2", "arrowAgent1","arrowAgent2"

# You can now create agents from the species you created and and place them at specific coordinates
agent1, view1 = Sheeps.newAgentAtCoordsWithModelView(xCoord=4,yCoord=1)

# The method allows you to write newAgentAtCoords(2,1), eventhough xCoord and yCoord are not the first arguments
agent2, view2 = Sheeps.newAgentAtCoordsWithModelView(1,2)

# you can also create multiple agents at once using newAgentsAtCoords()
agents3 = Sheeps.newAgentsAtCoordsWithModelView(3,(5,4))



Legend=myModel.newLegend()
myModel.displayAdminControlPanel()

myModel.launch() 
sys.exit(monApp.exec_())
