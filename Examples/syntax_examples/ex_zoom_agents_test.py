import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(500, 400, windowTitle="Test zoom with agents in square grid")

# Create a square grid with agents
squareCell = myModel.newCellsOnGrid(3, 3, "square", name="SquareGrid", size=40, gap=5)
squareCell.setEntities("terrain", "grass")
squareCell.setRandomEntities("terrain", "rock", 2)
squareCell.newPov("base", "terrain", {
    "grass": Qt.green,
    "rock": Qt.darkGray
})

# Position the grid
squareCell.grid.moveToCoords(50, 50)

# Create agents
Animals = myModel.newAgentSpecies("Animals", "triangleAgent1", defaultSize=10, defaultColor=Qt.white, locationInEntity="center")
Animals.setDefaultValues_randomChoice({
    "health": ["good", "fair", "poor"],
    "hunger": ["full", "hungry", "starving"],
    "age": ["young", "adult", "old"]
})

# Add agents to the grid
Animals.newAgentsAtRandom(5, squareCell, condition=lambda c: c.isValue("terrain", "grass"))

# Create a legend
aLegend = myModel.newLegend()
aLegend.moveToCoords(300, 50)

# Create instructions
aTextBox = myModel.newTextBox(
    "Test zoom with agents in square grid:\n"
    "Move mouse over the grid and use mouse wheel to zoom in/out.\n"
    "Check that agents scale and position correctly with zoom.",
    title="Agent Zoom Test", sizeY=100
)
aTextBox.moveToCoords(300, 200)

myModel.launch()
sys.exit(monApp.exec_())
