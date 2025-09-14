import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(600, 500, windowTitle="Test zoom with agents in hexagonal grid")

# Create a hexagonal grid
hexCell = myModel.newCellsOnGrid(4, 4, "hexagonal", name="HexGrid", size=40, gap=0)
hexCell.setEntities("terrain", "grass")
hexCell.setRandomEntities("terrain", "rock", 3)
hexCell.newPov("base", "terrain", {
    "grass": Qt.green,
    "rock": Qt.darkGray
})

# Position the grid
hexCell.grid.moveToCoords(50, 50)

# Create agents with center location in hexagonal grid
HexAgents = myModel.newAgentSpecies("HexAgents", "triangleAgent1", defaultSize=12, defaultColor=Qt.red, locationInEntity="center")
HexAgents.setDefaultValues_randomChoice({
    "health": ["good", "fair", "poor"],
    "hunger": ["full", "hungry", "starving"]
})

# Add agents to the hexagonal grid
HexAgents.newAgentsAtRandom(6, hexCell, condition=lambda c: c.isValue("terrain", "grass"))

# Create a legend
aLegend = myModel.newLegend()
aLegend.moveToCoords(350, 50)

# Create instructions
aTextBox = myModel.newTextBox(
    "Test zoom with agents in hexagonal grid:\n"
    "Red agents are positioned at center of hexagonal cells.\n"
    "Move mouse over the grid and use mouse wheel to zoom in/out.\n"
    "Check that agents maintain their center position in hexagons.",
    title="Hexagonal Agent Zoom Test", sizeY=100
)
aTextBox.moveToCoords(350, 200)

myModel.launch()
sys.exit(monApp.exec_())
