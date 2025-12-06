import sys
import random
from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor, QPixmap

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# Application initialization
monApp = QtWidgets.QApplication([])

# Model creation
myModel = SGModel(1000, 800, windowTitle="Tile Positioning Examples")
myModel.displayTimeInWindowTitle()

# ============================================================================
# Example: Different tile positions on a single grid
# ============================================================================
print("Creating tiles with different positioning options...")

# Create a single 5x5 grid
Grid = myModel.newCellsOnGrid(5, 5, "square", size=100, gap=5, name="PositioningGrid")

# Create different tile types, each with a different position
# Each tile type will be placed on different cells to demonstrate positioning

# Tile Type 1: Center position (default)
TileCenter = myModel.newTileType(
    name="Tile_Center",
    shape="rectTile",
    defaultSize=40,
    frontColor=QColor("blue")
    # defaultPositionOnCell="center" is the default, so no need to specify it
)

# Tile Type 2: TopLeft position
TileTopLeft = myModel.newTileType(
    name="Tile_TopLeft",
    shape="circleTile",
    defaultSize=35,
    frontColor=QColor("red"),
    defaultPositionOnCell="topLeft"
)

# Tile Type 3: TopRight position
TileTopRight = myModel.newTileType(
    name="Tile_TopRight",
    shape="rectTile",
    defaultSize=35,
    frontColor=QColor("green"),
    defaultPositionOnCell="topRight"
)

# Tile Type 4: BottomLeft position
TileBottomLeft = myModel.newTileType(
    name="Tile_BottomLeft",
    shape="circleTile",
    defaultSize=35,
    frontColor=QColor("yellow"),
    defaultPositionOnCell="bottomLeft"
)

# Tile Type 5: BottomRight position
TileBottomRight = myModel.newTileType(
    name="Tile_BottomRight",
    shape="rectTile",
    defaultSize=35,
    frontColor=QColor("magenta"),
    defaultPositionOnCell="bottomRight"
)

# Tile Type 6: Full position (covers entire cell)
TileFull = myModel.newTileType(
    name="Tile_Full",
    shape="rectTile",
    defaultSize=100,  # Will be adjusted to cell size
    frontColor=QColor("cyan"),
    defaultPositionOnCell="full"
)

# Load images for backImage (random assignment)
# Simple helper method for modelers
images_dir = Path(__file__).parent.parent.parent / "images"
images = myModel.loadImagesFromDirectory(images_dir)

# Place tiles on different cells to demonstrate each position
# Row 1: Center tiles
for x in range(1, 6):
    cell = Grid.getCell(x, 1)
    # Assign random backImage
    TileCenter.newTileOnCell(cell, backImage=random.choice(images))

# Row 2: TopLeft tiles
for x in range(1, 6):
    cell = Grid.getCell(x, 2)
    # Assign random backImage
    TileTopLeft.newTileOnCell(cell, backImage=random.choice(images))

# Row 3: TopRight tiles
for x in range(1, 6):
    cell = Grid.getCell(x, 3)
    # Assign random backImage
    TileTopRight.newTileOnCell(cell, backImage=random.choice(images))

# Row 4: BottomLeft tiles
for x in range(1, 6):
    cell = Grid.getCell(x, 4)
    # Assign random backImage
    TileBottomLeft.newTileOnCell(cell, backImage=random.choice(images))

# Row 5: BottomRight tiles
for x in range(1, 6):
    cell = Grid.getCell(x, 5)
    # Assign random backImage
    TileBottomRight.newTileOnCell(cell, backImage=random.choice(images))

# Add a full tile on cell (3, 3) to show it covers the entire cell
# This will overlap with the TopRight tile, showing the full positioning
cell_full = Grid.getCell(3, 3)
TileFull.newTileOnCell(cell_full, backImage=random.choice(images))

# Create a player to test game actions
Player1 = myModel.newPlayer("Player 1")

# Add Flip action for all tile types to test the two-face system
# Note: Now uses label (consistent with other action methods)
flipActionCenter = myModel.newFlipAction(TileCenter, aNumber='infinite', label="🔄 Flip Center Tiles")
flipActionTopLeft = myModel.newFlipAction(TileTopLeft, aNumber='infinite', label="🔄 Flip TopLeft Tiles")
flipActionTopRight = myModel.newFlipAction(TileTopRight, aNumber='infinite', label="🔄 Flip TopRight Tiles")
flipActionBottomLeft = myModel.newFlipAction(TileBottomLeft, aNumber='infinite', label="🔄 Flip BottomLeft Tiles")
flipActionBottomRight = myModel.newFlipAction(TileBottomRight, aNumber='infinite', label="🔄 Flip BottomRight Tiles")
flipActionFull = myModel.newFlipAction(TileFull, aNumber='infinite', label="🔄 Flip Full Tile")

# Add Move action for all tile types to test tile movement
# Note: newMoveAction uses 'label' (not 'nameToDisplay' like newFlipAction)
moveActionCenter = myModel.newMoveAction(TileCenter, aNumber='infinite', label="↔️ Move Center Tiles",action_controler={"directClick":True, "controlPanel":False})
moveActionTopLeft = myModel.newMoveAction(TileTopLeft, aNumber='infinite', label="↔️ Move TopLeft Tiles",action_controler={"directClick":True, "controlPanel":False})
moveActionTopRight = myModel.newMoveAction(TileTopRight, aNumber='infinite', label="↔️ Move TopRight Tiles",action_controler={"directClick":True, "controlPanel":False})
moveActionBottomLeft = myModel.newMoveAction(TileBottomLeft, aNumber='infinite', label="↔️ Move BottomLeft Tiles",action_controler={"directClick":True, "controlPanel":False})
moveActionBottomRight = myModel.newMoveAction(TileBottomRight, aNumber='infinite', label="↔️ Move BottomRight Tiles",action_controler={"directClick":True, "controlPanel":False})
moveActionFull = myModel.newMoveAction(TileFull, aNumber='infinite', label="↔️ Move Full Tile",action_controler={"directClick":True, "controlPanel":False})

Player1.addGameAction(flipActionCenter)
Player1.addGameAction(flipActionTopLeft)
Player1.addGameAction(flipActionTopRight)
Player1.addGameAction(flipActionBottomLeft)
Player1.addGameAction(flipActionBottomRight)
Player1.addGameAction(flipActionFull)

Player1.addGameAction(moveActionCenter)
Player1.addGameAction(moveActionTopLeft)
Player1.addGameAction(moveActionTopRight)
Player1.addGameAction(moveActionBottomLeft)
Player1.addGameAction(moveActionBottomRight)
Player1.addGameAction(moveActionFull)

Player1.newControlPanel("Player 1 Actions", defaultActionSelected=flipActionCenter)

# Create a play phase
myModel.newPlayPhase("Player 1 Turn", [Player1])

# Set current player
myModel.setCurrentPlayer("Player 1")

# Launch the game
myModel.launch()

sys.exit(monApp.exec_())

