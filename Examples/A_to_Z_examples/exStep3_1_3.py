import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(500,300, windowTitle="Add agents - define attributes and values of agents")

Cell=myModel.newCellsOnGrid(6,4,"square",gap=2,size=40)

Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)
Cell.newPov("base","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})

# To create a type of agents, it needs : a name and a shape 
Sheeps=myModel.newAgentType("Sheeps","circleAgent",defaultSize=10)
# available shapes are "circleAgent","squareAgent", "ellipseAgent1","ellipseAgent2", "rectAgent1","rectAgent2", "triangleAgent1","triangleAgent2", "arrowAgent1","arrowAgent2"

# You can set up the attributes and values of the agents when creating them
Sheeps.newAgentsAtRandom(7,{"health":"bad","hunger":"bad"})

#newAgentOnCell(self, aCell, attributesAndValues=None, image=None, popupImage=None):
aCellOfForest = Cell.getRandomEntity_withValue('landUse','forest')
Sheeps.newAgentOnCell(aCellOfForest, {"health":"good","hunger":"good"})

# For each attribute, you need to set up at least one point of view with its colors :
Sheeps.newPov("Health","health",{'good':Qt.blue,'bad':Qt.red})
Sheeps.newPov("Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})

# values can be set and/or modified after the creation of the agent
aSheep = Sheeps.newAgentAtCoords(3,3)
aSheep.setValues({"health":"good","hunger":"bad"})

#You can also edit your agent attribute values like this :
# aSheep.setValue('health','good')
# aSheep.setValue('hunger','bad')


Legend=myModel.newLegend()
myModel.launch() 

sys.exit(monApp.exec_())
