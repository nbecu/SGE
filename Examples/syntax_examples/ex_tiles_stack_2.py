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

# Create tile types for different stack rendering modes demonstration
TileA_topOnly_noCounter = myModel.newTileType(
    name="Tile_topOnly_noCounter",
    defaultSize=50,
    frontColor=QColor("blue"),
    backColor=QColor("blue"),
    stackRendering={"mode": "topOnly", "showCounter": False}  # TopOnly without counter
)

TileB_topOnly_withCounter = myModel.newTileType(
    name="Tile_topOnly_withCounter",
    defaultSize=50,
    frontColor=QColor("green"),
    backColor=QColor("green"),
    stackRendering={"mode": "topOnly", "showCounter": True}  # TopOnly with counter (default position: topRight)
)

TileC_offset_noCounter = myModel.newTileType(
    name="Tile_offset_noCounter",
    defaultSize=50,
    frontColor=QColor("cyan"),
    backColor=QColor("cyan"),
    stackRendering={"mode": "offset", "showCounter": False}  # Offset without counter
)

TileD_offset_withCounter = myModel.newTileType(
    name="Tile_offset_withCounter",
    defaultSize=50,
    frontColor=QColor("magenta"),
    backColor=QColor("magenta"),
    stackRendering={"mode": "offset", "showCounter": True, "maxVisible": 7, "counterPosition": "bottomLeft"}  # Offset with counter at bottomLeft, maxVisible=7
)

# Load images for frontImage (random assignment)
# Simple helper method for modelers
images_dir = Path(__file__).parent.parent.parent / "images"
images = myModel.loadImagesFromDirectory(images_dir)


# Get some cells to work with
cell_1_1 = Grid.getCell(1, 1)  # TopOnly without counter
cell_2_1 = Grid.getCell(2, 1)  # TopOnly with counter
cell_3_1 = Grid.getCell(3, 1)  # Offset without counter
cell_4_1 = Grid.getCell(4, 1)  # Offset with counter and many tiles

# ============================================================================
# Example: Create stacks with different rendering modes
# ============================================================================

# Cell (1,1): TopOnly mode without counter - 3 tiles
for i in range(3):
    TileA_topOnly_noCounter.newTileOnCell(cell_1_1, face="front", frontImage=random.choice(images))

# Cell (2,1): TopOnly mode with counter - 3 tiles
for i in range(3):
    TileB_topOnly_withCounter.newTileOnCell(cell_2_1, face="front", frontImage=random.choice(images))

# Cell (3,1): Offset mode without counter - 3 tiles
for i in range(3):
    TileC_offset_noCounter.newTileOnCell(cell_3_1, face="front", frontImage=random.choice(images))

# Cell (4,1): Offset mode with counter - many tiles (only top 7 visible)
for i in range(15):
    TileD_offset_withCounter.newTileOnCell(cell_4_1, face="front", frontImage=random.choice(images))

# Create a player to interact with tiles
Player1 = myModel.newPlayer("Player 1")

# Add Flip action to test tile flipping (for all tile types)
Player1.newFlipAction(TileA_topOnly_noCounter, label="🔄 Flip Tile (topOnly)",action_controler={"directClick":True})
Player1.newFlipAction(TileB_topOnly_withCounter, label="🔄 Flip Tile (topOnly+counter)",action_controler={"directClick":True})
Player1.newFlipAction(TileC_offset_noCounter, label="🔄 Flip Tile (offset)",action_controler={"directClick":True})
Player1.newFlipAction(TileD_offset_withCounter, label="🔄 Flip Tile (offset+counter)",action_controler={"directClick":True})

# Add Move action to test tile movement (for all tile types)
Player1.newMoveAction(TileA_topOnly_noCounter, label="➡️ Move Tile (topOnly)",action_controler={"directClick":True})
Player1.newMoveAction(TileB_topOnly_withCounter, label="➡️ Move Tile (topOnly+counter)",action_controler={"directClick":True})
Player1.newMoveAction(TileC_offset_noCounter, label="➡️ Move Tile (offset)",action_controler={"directClick":True})
Player1.newMoveAction(TileD_offset_withCounter, label="➡️ Move Tile (offset+counter)",action_controler={"directClick":True})

Player1.newControlPanel("Player 1 Actions")

# Create a play phase
myModel.newPlayPhase("Player 1 Turn", [Player1])

# Set current player
myModel.setCurrentPlayer("Player 1")


# Create a textBox to explain the model
textBox = myModel.newTextBox(shrinked=False,
    width=400,
    height=250,
    title="Stack Rendering Modes",
    textToWrite="""This model demonstrates different stack rendering modes for tiles.

• Cell (1,1): TOPONLY mode without counter - 3 tiles
  Only the top tile is visible (others hidden), no counter displayed.

• Cell (2,1): TOPONLY mode with counter - 3 tiles
  Only the top tile is visible with a counter at topRight (default position) showing stack size.

• Cell (3,1): OFFSET mode without counter - 3 tiles
  Tiles are displayed with slight offsets showing edges, no counter.

• Cell (4,1): OFFSET mode with counter - 15 tiles
  Tiles with offsets and a counter at bottomLeft showing stack size.
  Only top 7 tiles visible (maxVisible=7).

Use Flip and Move actions to interact with tiles. Stacks automatically manage layers during movements.""",
    titleAlignment='center'
)
textBox.moveToCoords(30, 320)

# Launch the game
myModel.launch()

sys.exit(monApp.exec_())

