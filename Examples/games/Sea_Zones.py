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
myModel = SGModel(1200, 900, windowTitle="Sea Zones")
myModel.displayTimeInWindowTitle()

# ============================================================================
# Paths configuration
# ============================================================================
csv_path = Path(__file__).parent.parent.parent / "data" / "import" / "sea_zones" / "tiles.csv"
images_dir = Path(__file__).parent.parent.parent / "data" / "import" / "sea_zones"

# ============================================================================
# Create game board (13x13 grid)
# ============================================================================
Board = myModel.newCellsOnGrid(13, 13, "square", size=50, gap=1, name="Board",neighborhood="neumann")

# ============================================================================
# Create river (1 deck cell + 3 slots for drafting)
# ============================================================================
River = myModel.newCellsOnGrid(4, 1, "square", size=80, gap=10, name="River")
deck_cell = River.getCell(1, 1)

# ============================================================================
# Create tile type for Sea Zones tiles
# ============================================================================
SeaTile = myModel.newTileType(
    name="SeaTile",
    shape="imageTile",  # Use imageTile to display images
    defaultSize=80,
    positionOnCell="full",
    defaultFace="back",  # Tiles start face down (back visible)
    backColor=QColor('blue'),  # Back face: blue
    stackRendering={"mode": "topOnly", "showCounter": True, "counterPosition": "center"}
)
SeaTile.setTooltip('name','tile_name')

# ============================================================================
# Create tile deck from CSV
# ============================================================================
# Create deck stack from CSV using newStackOnCellFromCSV
# This method handles image loading, attribute assignment, and quantity automatically
deck_stack = SeaTile.newStackOnCellFromCSV(
    deck_cell,
    csv_file={'path': csv_path, 'delimiter': ';'},
    columns_mapping={
        'name': ('attribute', 'tile_name'),
        'category': ('attribute', 'category'),
        'stack_on': ('attribute', 'stack_on', 'list'),  # Parse as comma-separated list
        'image': 'frontImage',  # Map 'image' column to frontImage
        'bonus_point': ('attribute', 'bonus_point', 'int'),  # Parse as integer
        'nb': 'quantity'
        },
    image_dir=images_dir,
    shuffle=True
)

# ============================================================================
# Place starting port tile at center of board (7, 7)
# ============================================================================
center_cell = Board.getCell(7, 7)
port_tile = SeaTile.getEntities_withValue("tile_name", "port")[0]
port_tile.moveTo(center_cell)
port_tile.flip()  # Show port tile face up

# ============================================================================
# Place end tile in the last 10 tiles of the stack 
# ============================================================================
ending_tile = SeaTile.getEntities_withValue("tile_name", "maree_basse")[0]
# Position the ending tile at a random layer between 1 and 10
target_layer = random.randint(1, 10)
deck_stack.setTileAtLayer(ending_tile, target_layer)

# ============================================================================
# Set up Open Drafting for river (3 drafting slots: cells 2, 3, 4)
# ============================================================================
river_slots = [River.getCell(2, 1), River.getCell(3, 1), River.getCell(4, 1)]
refill_action = deck_stack.setOpenDrafting(
    slots=river_slots,
    visibleFace="front",  # Tiles show front face when drafted to river
)

# Create a model phase to refill the river slots automatically
myModel.newModelPhase(
    refill_action,
    name="Refill River",
    auto_forward=True,
    message_auto_forward=False
)

# ============================================================================
# Create player and game actions
# ============================================================================
Player1 = myModel.newPlayer("Player 1")

# Move action: Move tiles from river to board
# Conditions:
# 1. Target cell must be empty OR allow biodiv stacking (if tile is biodiv and can stack on existing biodiv tile)
# 2. Can only move to board
# 3. Can only move from river
# 4. Target cell must be orthogonally adjacent to at least one cell with a SeaTile
def canPlaceTile(tile, cell):
    """Check if tile can be placed on cell (empty or biodiv stacking allowed)"""
    # Empty cell: placement always allowed
    if cell.isEmpty():
        return True
   
    # Only biodiv tiles can stack on other biodiv tiles
    top_tile = cell.getStack(SeaTile).topTile()
    if tile.getValue("category") != "biodiv" or top_tile.getValue("category") != "biodiv":
        return False

    # Check if this biodiv tile can stack on the biodiv top_tile
    return top_tile.getValue("tile_name") in tile.getValue("stack_on")

moveAction = myModel.newMoveAction(
    SeaTile,
    label="Place Tile",
    conditions=[
        canPlaceTile,  # Target cell must be empty or allow biodiv stacking
        lambda tile, cell: cell.type == Board,  # Can only move to board
        lambda tile: tile.cell.type == River,  # Can only move from river
        # Check orthogonal adjacency: at least one neighbor must have a SeaTile
        lambda tile, cell: len(cell.getNeighborCells(condition=lambda c: c.hasTile())) > 0
    ]
)
Player1.addGameAction(moveAction)

Player1.newControlPanel("Player 1 Actions")

# ============================================================================
# Create play phase
# ============================================================================
myModel.newPlayPhase("Player 1 Turn", [Player1])
myModel.setCurrentPlayer("Player 1")

# Launch the game
myModel.launch()

sys.exit(monApp.exec_())
