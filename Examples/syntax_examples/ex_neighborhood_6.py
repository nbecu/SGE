import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(500, 300, windowTitle="MoveTowards demonstration")

# Grid with open boundaries
Cell = myModel.newCellsOnGrid(8, 5, "square", gap=0, size=50, neighborhood='moore', boundaries='closed')

Cell.setEntities("landForm", "plain")
Cell.setRandomEntities("landForm", "mountain", 6)
Cell.setRandomEntities("landForm", "lac", 4)
Cell.newPov("base", "landForm", {"plain": Qt.green, "lac": Qt.blue, "mountain": Qt.darkGray})

# Sheep (random movement, only on plains)
Sheep = myModel.newAgentSpecies("Sheep", "ellipseAgent1", defaultSize=20, locationInEntity="center", defaultColor=Qt.white)
Sheep.newAgentsAtRandom(1, condition=lambda c: c.isValue("landForm", "plain"))

# Wolf (hunts the sheep)
Wolf = myModel.newAgentSpecies("Wolf", "triangleAgent2", defaultSize=20, locationInEntity="center", defaultColor=Qt.red)
Wolf.newAgentsAtRandom(1, condition=lambda c: c.isValue("landForm", "plain"))

p1 = myModel.newModelPhase()

# Sheep moves randomly on plains
p1.addAction(lambda: Sheep.moveRandomly(condition=lambda c: c.isValue("landForm", "plain")))

# Wolf moves towards the sheep
def wolf_hunt():
    wolf = Wolf.getEntities()[0]
    sheep = Sheep.getEntities()[0]
    wolf.moveTowards(sheep, condition=lambda c: c.isValue("landForm", "plain"))

p1.addAction(wolf_hunt)

myModel.launch()
sys.exit(monApp.exec_())