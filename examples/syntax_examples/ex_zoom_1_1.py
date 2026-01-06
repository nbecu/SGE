import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(600, 500, windowTitle="Test zoom with agents in square grid")

# Create a square grid
squareCell = myModel.newCellsOnGrid(4, 4, "square", name="SquareGrid", size=40, gap=2)
squareCell.setEntities("terrain", "grass")
squareCell.setRandomEntities("terrain", "rock", 3)
squareCell.newPov("base", "terrain", {
    "grass": Qt.green,
    "rock": Qt.darkGray
})

# Position the grid
squareCell.grid.moveToCoords(50, 50)

# Create agents with center location in square grid
SquareAgents = myModel.newAgentType("SquareAgents", "triangleAgent1", defaultSize=12, defaultColor=Qt.red, locationInEntity="center")
SquareAgents.setDefaultValues_randomChoice({
    "health": ["good", "fair", "poor"],
    "hunger": ["full", "hungry", "starving"]
})

# Add agents to the square grid
SquareAgents.newAgentsAtRandom(6, squareCell, condition=lambda c: c.isValue("terrain", "grass"))

# Create a legend
aLegend = myModel.newLegend()
aLegend.moveToCoords(350, 50)

# Create instructions
aTextBox = myModel.newTextBox(
    "Test zoom with agents in square grid:\n"
    "Red agents are positioned at center of square cells.\n"
    "Move mouse over the grid and use mouse wheel to zoom in/out.\n"
    "Check that agents maintain their center position in squares.",
    title="Agents in Squares - Zoom Test")
aTextBox.moveToCoords(350, 200)

myModel.launch()
sys.exit(monApp.exec_())
