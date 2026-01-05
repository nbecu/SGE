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
myModel = SGModel(800, 600, windowTitle="Tile Stack Example", nb_columns=2)
myModel.displayTimeInWindowTitle()

# ============================================================================
# Example: Stack demonstration
# ============================================================================

# Create a 4x1 grid
River = myModel.newCellsOnGrid(4, 1, "square", size=80, gap=5, name="River")

textBox = myModel.newTextBox(width=300, height=200, title="log")

# Create a 4x4 grid (empty)
Boardgame = myModel.newCellsOnGrid(4, 4, "square", size=80, gap=5, name="Boardgame")

# Create a single tile type
Tile = myModel.newTileType(
    name="Tile",
    shape="rectTile",
    defaultSize=80,
    positionOnCell="full",
    frontColor=QColor("blue"),
    backColor=QColor("blue"),
    stackRendering={"mode": "topOnly", "showCounter": True, "counterPosition": "topLeft"}
)

# Load images for random assignment
images_dir = Path(__file__).parent.parent.parent / "images"
images = myModel.loadImagesFromDirectory(images_dir)


# Create a stack of 30 tiles with random images on the back face
stack = Tile.newStackOnCell(River.getCell(1, 1), 30, backImages=images)


# Create a player with actions
Player1 = myModel.newPlayer("Player 1")
# Player1.newFlipAction(Tile, label="🔄 Flip",action_controler={"directClick":True})
Player1.newMoveAction(Tile, label="➡️ Move",action_controler={"directClick":True},
conditions = [
    lambda tile: tile.cell != River.getCell(1, 1),
    lambda tile,cell: cell.isEmpty(),
    lambda tile,cell: cell.type == Boardgame
    ])
# Player1.newControlPanel("Player 1 Actions")

# Set up Open Drafting
refill_action = stack.setOpenDrafting(
    slots=[River.getCell(2,1), River.getCell(3,1), River.getCell(4,1)],
    visibleFace="back",  # Tiles will show front face after being moved to slots
    visibleFaceOfTopTileOfStack="back"  # Top tile of stack shows back 
)
refill_action.addFeedback(lambda: textBox.addText(f"{stack.getLastSlotsFilled()} river slot(s) have been filled"))

# Create a model phase to refill the river slots
modelPhase = myModel.newModelPhase(refill_action,name="Move Tiles on River",auto_forward=True,message_auto_forward=False)


# Create a play phase
myModel.newPlayPhase("Player 1 Turn", [Player1])
myModel.setCurrentPlayer("Player 1")

# Launch the game
myModel.launch()

sys.exit(monApp.exec_())

