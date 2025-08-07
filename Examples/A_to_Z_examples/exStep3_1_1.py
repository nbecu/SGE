import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(500,300, windowTitle="A simulation/game with agents", typeOfLayout ="grid")

Cell=myModel.newCellsOnGrid(6,4,"square",gap=2,size=40)

Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)
Cell.newPov("base","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})

# In SGE a "type" of agent is called a species.
# To create a species, it needs : a name and a shape 
# Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1")
Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1")
            #  ("circleAgent","squareAgent", "ellipseAgent1","ellipseAgent2", "rectAgent1","rectAgent2", "triangleAgent1","triangleAgent2", "arrowAgent1","arrowAgent2")
# You can add a dict of attributs with values (optionnal).
# Sheeps.setDefaultValues({"health":{"good","bad"},"hunger":{"good","bad"}})
#todo le système de defaultValues ne fonctionne pas pour un choix entre plusieurs valeurs 

# You can now create agents from its species and place them on a particular cell, or random by giving None values and
m2=Sheeps.newAgentsAtCoords(100,Cell,1,1)

m2=Sheeps.newAgentsAtCoords(100,Cell,6,4)



# For each attribute, you can set up points of view with colors :
# Sheeps.newPov("Health","health",{'good':Qt.blue,'bad':Qt.red})
# Sheeps.newPov("Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})

# # give them attributes with values :
# m1=Sheeps.newAgentAtCoords(Cell,3,3,{"health":"good","hunger":"bad"})

#You can also edit your agent attribute values like this :
# m2.setValue('health','good')
# m2.setValue('hunger','good')



Legend=myModel.newLegend(showAgentsWithNoAtt=True)
myModel.launch() 

sys.exit(monApp.exec_())
