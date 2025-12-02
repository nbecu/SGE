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
myModel.displayTimeInWindowTitle()

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

# Place a tile on each cell, alternating face up/down

for x in range(1, 5):  # Columns 1 to 4
    for y in range(1, 5):  # Rows 1 to 4
        cell = Cell.getCell(x, y)
        # Create a tile, alternating between front and back face
        face = "front" if random.random() < 0.5 else "back"
        CardTile.newTileOnCell(cell, face=face)

# Create a player to test game actions
Player1 = myModel.newPlayer("Player 1")

# Add Flip action to test tile flipping
flipAction = myModel.newFlipAction(CardTile, aNumber='infinite', nameToDisplay="🔄 Flip Card")
Player1.addGameAction(flipAction)
Player1.newControlPanel("Player 1 Actions")

# Create a play phase
myModel.newPlayPhase("Player 1 Turn", [Player1])

# Set current player
myModel.setCurrentPlayer("Player 1")

myModel.displayAdminControlPanel()

myModel.newUserSelector()

# Launch the game
myModel.launch()

sys.exit(monApp.exec_())

