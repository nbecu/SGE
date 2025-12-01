import sys
from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# Application initialization
monApp = QtWidgets.QApplication([])

# Model creation
myModel = SGModel(800, 800, windowTitle="Memory Game")

# Create a 4x4 grid for Memory
Cell = myModel.newCellsOnGrid(4, 4, "square", size=150, gap=5)

# Create a tile type for Memory cards
# Tiles will have two faces: front face (with image/color) and back face (card back)
CardTile = myModel.newTileType(
    name="Card",
    shape="rectTile",
    defaultSize=100,
    defaultColor=QColor("blue"),  # Default color for the front face
    defaultPositionOnCell="center",
    defaultFace="back",            # Default face: back (cards start face down)
    frontColor=QColor("blue"),     # Front face: blue
    backColor=QColor("pink")       # Back face: pink (card back)
)

# Place a tile on each cell, all face down (back) initially
for x in range(2, 4):  # Columns 1 to 4
    for y in range(1, 5):  # Rows 1 to 4
        cell = Cell.getCell(x, y)
        # Create a face-down tile on each cell
        CardTile.newTileOnCell(cell)

# Launch the game
myModel.launch()

sys.exit(monApp.exec_())

