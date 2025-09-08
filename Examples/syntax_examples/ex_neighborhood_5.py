import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(400, 260, windowTitle="Open boundaries - move only on water")

Cell = myModel.newCellsOnGrid(7, 4, "square", size=50, neighborhood='moore', boundaries='open')

Cell.setEntities("landForm", "plain")
Cell.setRandomEntities("landForm", "lac", 6)
Cell.setEntities_withColumn("landForm", "mountain", 1)
Cell.newPov("base", "landForm", {"plain": Qt.green, "lac": Qt.blue, "mountain": Qt.darkGray})

Fish = myModel.newAgentSpecies("Fish", "rectAgent1", defaultSize=20, locationInEntity="center")
Fish.newAgentsAtRandom(1, condition=lambda c: c.isValue("landForm", "lac"))


p1 = myModel.newModelPhase()
# Fish can wrap-around but only move on water
p1.addAction(lambda: Fish.moveRandomly(condition=lambda cell: cell.isValue("landForm", "lac")))

myModel.launch()
sys.exit(monApp.exec_())
