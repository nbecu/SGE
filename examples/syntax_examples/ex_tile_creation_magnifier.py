import sys
from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# Application initialization
monApp = QtWidgets.QApplication([])

# Model creation
myModel = SGModel(1000, 800, windowTitle="Tile Creation with Magnifier Mode")
myModel.displayTimeInWindowTitle()

# ============================================================================
# Create a grid with magnifier mode
# ============================================================================
Board = myModel.newCellsOnGrid(10, 10, "square", size=50, gap=2, name="Board")
# Set magnifier mode for the grid
Board.grid.setZoomMode("magnifier")
# Set initial zoom level (optional, for testing)
Board.grid.setZoomLevel(1.5)

# ============================================================================
# Create tile types
# ============================================================================
# Tile Type 1: Center position
TileCenter = myModel.newTileType(
    name="Tile_Center",
    shape="rectTile",
    defaultSize=40,
    frontColor=QColor("blue"),
    positionOnCell="center"
)

# Tile Type 2: Full position (covers entire cell)
TileFull = myModel.newTileType(
    name="Tile_Full",
    shape="rectTile",
    defaultSize=50,  # Will be adjusted to cell size
    frontColor=QColor("red"),
    positionOnCell="full"
)

# Tile Type 3: TopLeft position
TileTopLeft = myModel.newTileType(
    name="Tile_TopLeft",
    shape="circleTile",
    defaultSize=30,
    frontColor=QColor("green"),
    positionOnCell="topLeft"
)

# ============================================================================
# Create tiles on the board using newTileOnCell()
# This is the method that needs to be tested for magnifier mode
# ============================================================================
# Create center tiles on row 1
for x in range(1, 6):
    cell = Board.getCell(x, 1)
    TileCenter.newTileOnCell(cell)

# Create full tiles on row 2
for x in range(1, 6):
    cell = Board.getCell(x, 2)
    TileFull.newTileOnCell(cell)

# Create topLeft tiles on row 3
for x in range(1, 6):
    cell = Board.getCell(x, 3)
    TileTopLeft.newTileOnCell(cell)

# Create some tiles at specific coordinates using newTileAtCoords()
# This is another method that needs to be tested
TileCenter.newTileAtCoords(Board, 7, 7)
TileFull.newTileAtCoords(Board, 8, 8)
TileTopLeft.newTileAtCoords(Board, 9, 9)

# ============================================================================
# Create a player with actions to test tile creation during gameplay
# ============================================================================
Player1 = myModel.newPlayer("Player 1")

# Create action to create new tiles (for testing creation during gameplay)
createAction = myModel.newCreateAction(
    TileCenter,
    dictAttributes={"test": "value"},
    uses_per_round=5,
    label="Create Center Tile"
)
Player1.addGameAction(createAction)

# Create move action for tiles with directClick (for testing tile movement in magnifier mode)
moveAction = myModel.newMoveAction(
    TileCenter,
    uses_per_round='infinite',
    label="Move Tiles",
    action_controler={"directClick": True}
)
Player1.addGameAction(moveAction)

Player1.newControlPanel("Player 1 Actions", defaultActionSelected=createAction)

# Create a play phase
myModel.newPlayPhase("Player 1 Turn", [Player1])

# Set current player
myModel.setCurrentPlayer("Player 1")

# Launch the game
myModel.launch()

sys.exit(monApp.exec_())
