import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(500, 300, windowTitle="numberOfMovement demonstration")

# Create a square grid with closed boundaries and Moore neighborhood
Cell = myModel.newCellsOnGrid(8, 5, "square", gap=0, size=50, neighborhood='moore', boundaries='closed')

Cell.setEntities("landForm", "plain")
Cell.setRandomEntities("landForm", "mountain", 6)
Cell.setRandomEntities("landForm", "lac", 4)
Cell.newPov("base", "landForm", {"plain": Qt.green, "lac": Qt.blue, "mountain": Qt.darkGray})

# Species 1: Turtle - moves slowly (1 movement per turn)
Turtle = myModel.newAgentSpecies("Turtle", "squareAgent", defaultSize=20, locationInEntity="center", defaultColor=Qt.darkGreen)
Turtle.newAgentsAtRandom(1, condition=lambda c: c.isValue("landForm", "plain"))

# Species 2: Rabbit - moves quickly (3 movements per turn)
Rabbit = myModel.newAgentSpecies("Rabbit", "ellipseAgent1", defaultSize=15, locationInEntity="center", defaultColor=Qt.white)
Rabbit.newAgentsAtRandom(1, condition=lambda c: c.isValue("landForm", "plain"))

p1 = myModel.timeManager.newModelPhase()
# Slow turtle
p1.addAction(lambda: Turtle.moveRandomly(numberOfMovement=1, condition=lambda c: c.isValue("landForm", "plain")))
# Fast rabbit
p1.addAction(lambda: Rabbit.moveRandomly(numberOfMovement=3, condition=lambda c: c.isValue("landForm", "plain")))

myModel.launch()
myModel.launch()
sys.exit(monApp.exec_())
