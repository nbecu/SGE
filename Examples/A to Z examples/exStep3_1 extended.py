import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1700,800, windowTitle="A simulation/game with agents", typeOfLayout ="grid")

Cell=myModel.newCellsOnGrid(6,6,"square",gap=2)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.setEntities("age",1)
Cell.setRandomEntities("age",2,10)
Cell.setRandomEntities("age",3,10)

Cell.newPov("ICanSeeShrub","landUse",{"grass":QColor.fromRgb(30,190,0),"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})
Cell.newPov("povAge","age",{1:Qt.green,2:QColor.fromRgb(30,190,0),3:QColorConstants.DarkGreen})

# Here, a "type" of agent is called a species.
# To create a species, it needs : a name and a shape 
# You can add a dict of attributs with values (optionnal).
Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1",{"health":{"good","bad"},"hunger":{"good","bad"},"age":{1,2,3}})

# For each attribute, you can set up points of view with colors :
Sheeps.newPov("Health","health",{'good':Qt.blue,'bad':Qt.red})
Sheeps.newPov("Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})
Sheeps.newPov("Age","age",{1:Qt.green,2:QColor.fromRgb(30,190,0),3:QColorConstants.DarkGreen})


# You can now create agents from its species and place them on a particular cell, or random by giving None values and
# give them attributes with values :
m1=Sheeps.newAgentAtCoords(Cell,1,1,{"health":"good","hunger":"bad","age":2})
m2=Sheeps.newAgentAtRandom(Cell)

#You can also edit your agent attribute values like this :
m2.setValue('health','good')
m2.setValue('hunger','good')
m2.setValue('age',3)



Legend=myModel.newLegend(showAgentsWithNoAtt=True)
myModel.launch() 

sys.exit(monApp.exec_())
