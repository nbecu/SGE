import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1700,800, windowTitle="A simulation/game with agents", typeOfLayout ="grid")

aGrid=myModel.newGrid(6,6,"square")
aGrid.setCells("landUse","grass")
aGrid.setCells_withColumn("landUse","forest",1)
aGrid.setCells_withColumn("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)

myModel.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

# Here, a "type" of agent is called a species.
# To create a species, it needs : a name and a shape 
# You can add a dict of attributs with values (optionnal).
Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1",{"health":{"good","bad"},"hunger":{"good","bad"}},2)

# For each attribute, you can set up points of view with colors :
Sheeps.newPov("Sheeps -> Health","health",{'good':Qt.blue,'bad':Qt.red})
Sheeps.newPov("Sheeps -> Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})

# You can now create agents from its species and place them on a particular cell, or random by giving None values and
# give them attributes with values :
m1=myModel.placeAgent(myModel.getCell(aGrid,"cell1-1"),Sheeps,{"health":"good","hunger":"bad"})
#m1=myModel.newAgent(aGrid,Sheeps,1,1,aDictofAttributs={"health":"good","hunger":"bad"})
#m2=myModel.newAgent(aGrid,Sheeps,None,None)

#You can also edit your agent attribute values like this :
#m2.setValueAgent('health','good')
#m2.setValueAgent('hunger','good')

myModel.launch() 

sys.exit(monApp.exec_())
