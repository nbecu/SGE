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
print("Creating tiles with stacking functionality...")

# Create a 4x2 grid (small grid as requested)
Grid = myModel.newCellsOnGrid(4, 2, "square", size=120, gap=5, name="StackGrid")

# Create a tile type for stacking demonstration
Tile = myModel.newTileType(
    name="Tile",
    shape="rectTile",
    defaultSize=50,
    positionOnCell="center",
    frontColor=QColor("blue"),
    defaultFace="front"
)

# Load images for frontImage (random assignment)
# Simple helper method for modelers
images_dir = Path(__file__).parent.parent.parent / "images"
images = myModel.loadImagesFromDirectory(images_dir)


# Get some cells to work with
cell_1_1 = Grid.getCell(1, 1)
cell_2_1 = Grid.getCell(2, 1)
cell_3_1 = Grid.getCell(3, 1)
cell_4_1 = Grid.getCell(4, 1)

# ============================================================================
# Example: Create stacks of different sizes
# ============================================================================
print("\n=== Creating stacks ===")

# Cell (1,1): Empty stack (no tiles)
print(f"Cell (1,1): Empty stack")
stack_1_1 = cell_1_1.getStack(Tile)
print(f"  - isEmpty(): {stack_1_1.isEmpty()}")
print(f"  - size(): {stack_1_1.size()}")

# Cell (2,1): Stack with 1 tile
print(f"\nCell (2,1): Stack with 1 tile")
tile1 = Tile.newTileOnCell(cell_2_1, face="front", frontImage=random.choice(images))
stack_2_1 = cell_2_1.getStack(Tile)
print(f"  - size(): {stack_2_1.size()}")
print(f"  - topTile() layer: {stack_2_1.topTile().layer if stack_2_1.topTile() else None}")

# Cell (3,1): Stack with 3 tiles
print(f"\nCell (3,1): Stack with 3 tiles")
tile2 = Tile.newTileOnCell(cell_3_1, face="front", frontImage=random.choice(images))
tile3 = Tile.newTileOnCell(cell_3_1, face="front", frontImage=random.choice(images))
tile4 = Tile.newTileOnCell(cell_3_1, face="front", frontImage=random.choice(images))
stack_3_1 = cell_3_1.getStack(Tile)
print(f"  - size(): {stack_3_1.size()}")
print(f"  - maxLayer(): {stack_3_1.maxLayer()}")
print(f"  - topTile() layer: {stack_3_1.topTile().layer}")
print(f"  - bottomTile() layer: {stack_3_1.bottomTile().layer}")

# Cell (4,1): Stack with 5 tiles
print(f"\nCell (4,1): Stack with 5 tiles")
for i in range(5):
    Tile.newTileOnCell(cell_4_1, face="front", frontImage=random.choice(images))
stack_4_1 = cell_4_1.getStack(Tile)
print(f"  - size(): {stack_4_1.size()}")
print(f"  - maxLayer(): {stack_4_1.maxLayer()}")

print("\n=== Stack examples completed! ===")

# Create a player to interact with tiles
Player1 = myModel.newPlayer("Player 1")

# Add Flip action to test tile flipping
flipAction = myModel.newFlipAction(Tile, label="🔄 Flip Tile",action_controler={"directClick":True})
Player1.addGameAction(flipAction)

# Add Move action to test tile movement
moveAction = myModel.newMoveAction(Tile, label="➡️ Move Tile",action_controler={"directClick":True})
Player1.addGameAction(moveAction)

Player1.newControlPanel("Player 1 Actions")

# Create a play phase
myModel.newPlayPhase("Player 1 Turn", [Player1])

# Set current player
myModel.setCurrentPlayer("Player 1")


# Create a textBox to explain the model
textBox = myModel.newTextBox(shrinked=False,
    width=350,
    height=200,
    title="Stack Functionality",
    textToWrite="""This model demonstrates stack (piling) functionality for tiles.

• Cell (1,1): Empty stack
• Cell (2,1): Stack with 1 tile
• Cell (3,1): Stack with 3 tiles
• Cell (4,1): Stack with 5 tiles

Use Flip and Move actions to interact with tiles. Stacks automatically manage layers during movements.""",
    titleAlignment='center'
)
textBox.moveToCoords(30, 320)

# Launch the game
myModel.launch()

sys.exit(monApp.exec_())
