import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(500,300, windowTitle="Add agents - define default random values of agents")

Cell=myModel.newCellsOnGrid(6,4,"square",gap=2,size=40)

Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)
Cell.newPov("base","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})

# In SGE a "type" of agent is called a species.
# To create a species, it needs : a name and a shape 
Sheeps=myModel.newAgentSpecies("Sheeps","rectAgent1")
# available shapes are "circleAgent","squareAgent", "ellipseAgent1","ellipseAgent2", "rectAgent1","rectAgent2", "triangleAgent1","triangleAgent2", "arrowAgent1","arrowAgent2"

# Default values can initialized randomly
Sheeps.setDefaultValues_randomChoice({"health":["good","bad"],"hunger":["good","bad"]})

#you can also have some attributes set randomy, and others not
# Sheeps.setDefaultValues_randomChoice({"health":"bad","hunger":["good","bad"]})



Sheeps.newAgentsAtRandom(10)

# For each attribute, you need to set up at least one point of view with its colors :
Sheeps.newPov("Health","health",{'good':Qt.blue,'bad':Qt.red})
Sheeps.newPov("Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})


Legend=myModel.newLegend()
myModel.launch() 

sys.exit(monApp.exec_())