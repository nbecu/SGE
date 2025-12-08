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

myModel.newTextBox(width=300, height=200, chronologicalOrder=False, title="log")

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
    stackRendering={"mode": "topOnly", "showCounter": True}
)

# Load images for frontImage (random assignment)
images_dir = Path(__file__).parent.parent.parent / "images"
images = myModel.loadImagesFromDirectory(images_dir)


# Create a stack of 30 tiles with random images
stackLocation = River.getCell(1, 1)
for i in range(30):
    Tile.newTileOnCell(stackLocation, backImage=random.choice(images))
stack = stackLocation.getStack(Tile)


# Create a player with actions
Player1 = myModel.newPlayer("Player 1")
Player1.newFlipAction(Tile, label="🔄 Flip",action_controler={"directClick":True})
Player1.newMoveAction(Tile, label="➡️ Move",action_controler={"directClick":True},
conditions = [
    lambda tile,cell: cell.isEmpty(),
    lambda tile,cell: cell.type == Boardgame
    ])
# Player1.newControlPanel("Player 1 Actions")

#create a model phase to move the tiles on the empty cells of the river
modelPhase = myModel.newModelPhase(name="Move Tiles on River",auto_forward=True,message_auto_forward=False)
fillRiver2 = myModel.newModelAction(lambda: stack.topTile().moveTo(River.getCell(2,1)),lambda: River.getCell(2,1).isEmpty(),lambda:River.getCell(2,1).getFirstTile().flip())
fillRiver3 = myModel.newModelAction(lambda: stack.topTile().moveTo(River.getCell(3,1)),lambda: River.getCell(3,1).isEmpty(),lambda:River.getCell(3,1).getFirstTile().flip())
fillRiver4 = myModel.newModelAction(lambda: stack.topTile().moveTo(River.getCell(4,1)),lambda: River.getCell(4,1).isEmpty(),lambda:River.getCell(4,1).getFirstTile().flip())
modelPhase.addActions(fillRiver2, fillRiver3, fillRiver4)


# Create a play phase
myModel.newPlayPhase("Player 1 Turn", [Player1])
myModel.setCurrentPlayer("Player 1")

# Launch the game
myModel.launch()

sys.exit(monApp.exec_())

