import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(600, 400, windowTitle="Test zoom hexagonal - Focus on hexagonal grid")

# Create a hexagonal grid
hexCell = myModel.newCellsOnGrid(4, 4, "hexagonal", name="HexGrid", size=30, gap=3)
hexCell.setEntities("terrain", "grass")
hexCell.setRandomEntities("terrain", "rock", 3)
hexCell.setRandomEntities("terrain", "water", 2)
hexCell.newPov("base", "terrain", {
    "grass": Qt.green,
    "rock": Qt.darkGray,
    "water": Qt.blue
})

# Position the grid
hexCell.grid.moveToCoords(50, 50)

# Create a legend
aLegend = myModel.newLegend()
aLegend.moveToCoords(350, 50)

# Create instructions
aTextBox = myModel.newTextBox(
    "Test zoom on hexagonal grid:\n"
    "Move mouse over the hexagonal grid and use mouse wheel to zoom in/out.\n"
    "Check that hexagons maintain their shape and positioning.",
    title="Hexagonal Zoom Test", sizeY=100
)
aTextBox.moveToCoords(350, 200)

myModel.launch()
sys.exit(monApp.exec_())
