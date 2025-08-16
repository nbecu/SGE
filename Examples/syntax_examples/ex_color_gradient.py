import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(400,400, windowTitle="A simulation/game with agents", typeOfLayout ="grid")

Cell=myModel.newCellsOnGrid(6,6,"square", size = 40 , gap=2)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("base","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})


# health and hunger default values are initialized with random integer values
Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1")
Sheeps.setDefaultValues({"health":(lambda: random.randint(0,10)*10),"hunger":(lambda: random.randint(0,10)*10)})

# generate a color gradient corresponding to the range of values that can be taken by the entities
aDict = generate_color_gradient(
    Qt.red, Qt.blue,
    mapping={"values": list(range(0, 110, 10)), "value_min": 0, "value_max": 100},
    as_dict=True
)
Sheeps.newPov("Health", "health", aDict)

aDict = generate_color_gradient(
    Qt.yellow, QColor.fromRgb(1,80,32),
    mapping={"values": list(range(0, 110, 10)), "value_min": 0, "value_max": 100},
    as_dict=True
)
Sheeps.newPov("Hunger","hunger",aDict)

m1=Sheeps.newAgentAtCoords(Cell,1,1,{"health":70,"hunger":20})
Sheeps.newAgentsAtRandom(10,Cell)
Sheeps.getEntity(2).setValue('health',90)
Sheeps.getEntity(2).setValue('hunger',90)


Legend=myModel.newLegend()

myModel.launch() 
sys.exit(monApp.exec_())
