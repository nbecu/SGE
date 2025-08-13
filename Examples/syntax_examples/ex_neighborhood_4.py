import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(500, 350, windowTitle="Neighborhood Hexagonal grid - moore (6 neighbors) - closed boundaries")

# Hexagonal grid: neighborhood='moore' => 6 neighbors
Cell = myModel.newCellsOnGrid(8, 5, "hexagonal", gap=0, size=40, neighborhood='moore', boundaries='closed')

Cell.setEntities("landForm", "plain")
Cell.setRandomEntities("landForm", "mountain", 6)
Cell.setRandomEntities("landForm", "lac", 4)
Cell.newPov("base", "landForm", {"plain": Qt.green, "lac": Qt.blue, "mountain": Qt.darkGray})

Bees = myModel.newAgentSpecies("Bees", "circleAgent", defaultSize=10, defaultColor=QColor.fromRgb(165,42,42), locationInEntity="random")
Bees.newAgentsAtRandom(1, condition=lambda c: c.isValue("landForm", "plain"))

p1 = myModel.timeManager.newModelPhase()
p1.addAction(lambda: Bees.moveRandomly(condition=lambda cell: cell.isValue("landForm", "plain")))

myModel.launch()
sys.exit(monApp.exec_())
