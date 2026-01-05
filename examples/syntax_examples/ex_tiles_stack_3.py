import sys
import random
from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# Application initialization
monApp = QtWidgets.QApplication([])

# Model creation
myModel = SGModel(800, 600, windowTitle="Tile Stack Examples")
myModel.displayTimeInWindowTitle()

# ============================================================================
# Example: Stack functionality demonstration
# ============================================================================

# Create a 4x2 grid (small grid as requested)
Grid = myModel.newCellsOnGrid(4, 2, "square", size=120, gap=5, name="StackGrid")

# Create tile types for different stack rendering modes and offset amounts demonstration
Tile_offset_small = myModel.newTileType(
    name="Tile_offset_small",
    shape="rectTile",
    defaultSize=50,
    positionOnCell="center",
    frontColor=QColor("blue"),
    backColor=QColor("blue"),
    defaultFace="front",
    stackRendering={"mode": "offset", "offset": 2, "maxVisible": 10, "showCounter": True, "counterPosition": "topLeft"}  # Small offset (2px), counter topLeft
)

Tile_offset_default = myModel.newTileType(
    name="Tile_offset_default",
    shape="rectTile",
    defaultSize=50,
    positionOnCell="center",
    frontColor=QColor("cyan"),
    backColor=QColor("cyan"),
    defaultFace="front",
    stackRendering={"mode": "offset", "offset": 3, "showCounter": True, "counterPosition": "bottomLeft"}  # Default offset (3px), counter bottomLeft
)

Tile_offset_large = myModel.newTileType(
    name="Tile_offset_large",
    shape="rectTile",
    defaultSize=50,
    positionOnCell="center",
    frontColor=QColor("magenta"),
    backColor=QColor("magenta"),
    defaultFace="front",
    stackRendering={"mode": "offset", "offset": 6, "showCounter": True, "counterPosition": "center"}  # Large offset (6px), counter center
)

Tile_topOnly = myModel.newTileType(
    name="Tile_topOnly",
    shape="rectTile",
    defaultSize=50,
    positionOnCell="center",
    frontColor=QColor("green"),
    backColor=QColor("green"),
    defaultFace="front",
    stackRendering={"mode": "topOnly", "showCounter": True, "counterPosition": "topRight"}  # Only top tile visible, counter topRight
)

# Load images for frontImage (random assignment)
# Simple helper method for modelers
images_dir = Path(__file__).parent.parent.parent / "images"
images = myModel.loadImagesFromDirectory(images_dir)


# Get some cells to work with
cell_1_1 = Grid.getCell(1, 1)  # Offset mode - small offset (2px)
cell_2_1 = Grid.getCell(2, 1)  # Offset mode - default offset (3px)
cell_3_1 = Grid.getCell(3, 1)  # Offset mode - large offset (6px)
cell_4_1 = Grid.getCell(4, 1)  # TopOnly mode

# ============================================================================
# Example: Create stacks with different offset amounts
# ============================================================================

# Cell (1,1): Offset mode - small offset (2 pixels) - 10 tiles (all visible)
for i in range(10):
    Tile_offset_small.newTileOnCell(cell_1_1, face="front", frontImage=random.choice(images))

# Cell (2,1): Offset mode - default offset (3 pixels) - 10 tiles (only top 5 visible)
for i in range(10):
    Tile_offset_default.newTileOnCell(cell_2_1, face="front", frontImage=random.choice(images))

# Cell (3,1): Offset mode - large offset (6 pixels) - 10 tiles (only top 5 visible)
for i in range(10):
    Tile_offset_large.newTileOnCell(cell_3_1, face="front", frontImage=random.choice(images))

# Cell (4,1): TopOnly mode - 10 tiles (only top tile visible)
for i in range(10):
    Tile_topOnly.newTileOnCell(cell_4_1, face="front", frontImage=random.choice(images))

# Create a player to interact with tiles
Player1 = myModel.newPlayer("Player 1")

# Add Flip action to test tile flipping (for all tile types)
flipAction_offset_small = myModel.newFlipAction(Tile_offset_small, label="🔄 Flip Tile (offset 2px)",action_controler={"directClick":True})
flipAction_offset_default = myModel.newFlipAction(Tile_offset_default, label="🔄 Flip Tile (offset 3px)",action_controler={"directClick":True})
flipAction_offset_large = myModel.newFlipAction(Tile_offset_large, label="🔄 Flip Tile (offset 6px)",action_controler={"directClick":True})
flipAction_topOnly = myModel.newFlipAction(Tile_topOnly, label="🔄 Flip Tile (topOnly)",action_controler={"directClick":True})
Player1.addGameAction(flipAction_offset_small)
Player1.addGameAction(flipAction_offset_default)
Player1.addGameAction(flipAction_offset_large)
Player1.addGameAction(flipAction_topOnly)

# Add Move action to test tile movement (for all tile types)
moveAction_offset_small = myModel.newMoveAction(Tile_offset_small, label="➡️ Move Tile (offset 2px)",action_controler={"directClick":True})
moveAction_offset_default = myModel.newMoveAction(Tile_offset_default, label="➡️ Move Tile (offset 3px)",action_controler={"directClick":True})
moveAction_offset_large = myModel.newMoveAction(Tile_offset_large, label="➡️ Move Tile (offset 6px)",action_controler={"directClick":True})
moveAction_topOnly = myModel.newMoveAction(Tile_topOnly, label="➡️ Move Tile (topOnly)",action_controler={"directClick":True})
Player1.addGameAction(moveAction_offset_small)
Player1.addGameAction(moveAction_offset_default)
Player1.addGameAction(moveAction_offset_large)
Player1.addGameAction(moveAction_topOnly)

Player1.newControlPanel("Player 1 Actions")

# Create a play phase
myModel.newPlayPhase("Player 1 Turn", [Player1])

# Set current player
myModel.setCurrentPlayer("Player 1")


# Create a textBox to explain the model
textBox = myModel.newTextBox(shrinked=False,
    width=450,
    height=280,
    title="Stack Offset Amount Configuration",
    textToWrite="""This model demonstrates configurable offset amounts and counter positions for offset rendering mode.

• Cell (1,1): OFFSET mode - small offset (2px)
  10 tiles with minimal spacing (all 10 visible, maxVisible=10).
  Counter positioned at topLeft.

• Cell (2,1): OFFSET mode - default offset (3px)
  10 tiles with standard spacing (only top 5 visible, maxVisible=5).
  Counter positioned at bottomLeft.

• Cell (3,1): OFFSET mode - large offset (6px)
  10 tiles with larger spacing (only top 5 visible, maxVisible=5).
  Counter positioned at center of the tile.

• Cell (4,1): TOPONLY mode - 10 tiles
  Only the top tile is visible (others hidden).
  Counter positioned at topRight.

Use Flip and Move actions to interact with tiles. 
Notice how different offset amounts and counter positions affect the visual display.""",
    titleAlignment='center'
)
textBox.moveToCoords(30, 320)

# Launch the game
myModel.launch()

sys.exit(monApp.exec_())

