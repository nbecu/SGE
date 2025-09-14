import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(600, 500, windowTitle="Test zoom with random positioned agents")

# Create a square grid
squareCell = myModel.newCellsOnGrid(4, 4, "square", name="SquareGrid", size=50, gap=5)
squareCell.setEntities("terrain", "grass")
squareCell.setRandomEntities("terrain", "rock", 3)
squareCell.newPov("base", "terrain", {
    "grass": Qt.green,
    "rock": Qt.darkGray
})

# Position the grid
squareCell.grid.moveToCoords(50, 50)

# Create agents with random location
RandomAgents = myModel.newAgentSpecies("RandomAgents", "triangleAgent1", defaultSize=10, defaultColor=Qt.red, locationInEntity="random")
RandomAgents.setDefaultValues_randomChoice({
    "health": ["good", "fair", "poor"],
    "hunger": ["full", "hungry", "starving"]
})

# Add more agents to better see the random positioning
RandomAgents.newAgentsAtRandom(8, squareCell, condition=lambda c: c.isValue("terrain", "grass"))

# Create a legend
aLegend = myModel.newLegend()
aLegend.moveToCoords(350, 50)

# Create instructions
aTextBox = myModel.newTextBox(
    "Test zoom with random positioned agents:\n"
    "Red agents are positioned randomly within their cells.\n"
    "Move mouse over the grid and use mouse wheel to zoom in/out.\n"
    "Check that agents maintain their random relative positions.",
    title="Random Agent Zoom Test", sizeY=100
)
aTextBox.moveToCoords(350, 200)

myModel.launch()
sys.exit(monApp.exec_())
