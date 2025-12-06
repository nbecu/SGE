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
# Tiles will have two faces: front face (with image) and back face (card back)
# Note: defaultColor is determined dynamically from defaultFace
# Since defaultFace="back", defaultColor will automatically use backColor for legends/ControlPanels
CardTile = myModel.newTileType(
    name="Card",
    shape="imageTile",  # Use imageTile to display images
    defaultSize=100,
    defaultPositionOnCell="center",
    defaultFace="back",            # Default face: back (cards start face down)
    backColor=QColor('violet')  # Back face: violet (card back) - defaultColor will use this dynamically
)

# Get all cells for the Memory game
cells = [Cell.getCell(x, y) for x in range(1, 5) for y in range(1, 5)]

# Create tiles with image pairs automatically
# This method handles: loading images, creating pairs, shuffling, and placing tiles
images_dir = Path(__file__).parent.parent.parent / "images" / "memory"
CardTile.newTilesWithImages(
    cells=cells,
    images_directory=images_dir,
    num_images=8,      # 8 unique images
    repetitions=2,     # Each image appears twice (pairs) = 16 tiles total
    shuffle=True,
    face="back"
)

# Create a player to test game actions
Player1 = myModel.newPlayer("Player 1")

# Add Flip action to test tile flipping
flipAction = myModel.newFlipAction(CardTile, label="🔄 Flip Card")
Player1.addGameAction(flipAction)
Player1.newControlPanel("Player 1 Actions")

# Create a play phase
myModel.newPlayPhase("Player 1 Turn", [Player1])

# Set current player
myModel.setCurrentPlayer("Player 1")

# myModel.displayAdminControlPanel()
# myModel.newUserSelector()

# Launch the game
myModel.launch()

sys.exit(monApp.exec_())

