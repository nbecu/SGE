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
Board = myModel.newCellsOnGrid(9, 9, "square", size=70, gap=1, name="Board",neighborhood="neumann")

# ============================================================================
# Create river (1 deck cell + 3 slots for drafting)
# ============================================================================
River = myModel.newCellsOnGrid(4, 1, "square", size=80, gap=10, name="River")
deck_cell = River.getCell(1, 1)

# ============================================================================
# Create individual player boards (3 cells each, positioned under river)
# ============================================================================
nb_players = 2
PlayerBoards = {}
for i in range(1, nb_players + 1):
    player_board = myModel.newCellsOnGrid(3, 1, "square", size=80, gap=10, name=f"Player{i}Board")
    PlayerBoards[i] = player_board
    # Position player boards
    y_position = 180 + (i - 1) * 140
    player_board.grid.moveToCoords(780, y_position)

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
center_cell = Board.getCell(5, 5)
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
deck_stack.refillAvailableSlots()


# ============================================================================
# Create marker agent
# ============================================================================
Marker = myModel.newAgentType("Marker", "circleAgent", defaultColor=Qt.black,locationInEntity="topRight")
Marker.newPov("default", "owner", {"Player 1": Qt.blue,"Player 2": Qt.red})
Marker.displayPov("default")
Board.setDefaultValue("owner", "")

# ============================================================================
# Create players and distribute initial tiles
# ============================================================================
Players = {}
for i in range(1, nb_players + 1):
    player = myModel.newPlayer(f"Player {i}")
    Players[i] = player
    
    # Set the player as owner of their board
    player_board = PlayerBoards[i]
    player_board.grid.setOwners(player)
    
    # Distribute 3 tiles to each player from deck_stack
    for j in range(1, 4):  # 3 tiles per player
        if not deck_stack.isEmpty():
            tile = deck_stack.topTile()
            tile.moveTo(player_board.getCell(j, 1))
            tile.flip()  # Show front face


# ============================================================================
# Create game actions
# ============================================================================
# Move action: Move tiles from player board to main board
# Conditions:
# 1. Target cell must be empty OR allow biodiv stacking (if tile is biodiv and can stack on existing biodiv tile)
# 2. Can only move to main board
# 3. Can only move from player's individual board
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


# Create move action template (will be copied for each player)
moveActionTemplate = myModel.newMoveAction(
    SeaTile,
    1,
    label="Place Tile",
    conditions=[
        canPlaceTile,  # Target cell must be empty or allow biodiv stacking
        lambda tile, cell: cell.type == Board,  # Can only move to main board
        lambda tile: tile.getGrid().isOwnedBy(myModel.getCurrentPlayer()),  # Can only move from current player's board
        # Check orthogonal adjacency: at least one neighbor must have a SeaTile
        lambda tile, cell: len(cell.getNeighborCells(condition=lambda c: c.hasTile())) > 0
    ],
    action_controler={"directClick": True},
    feedbacks=[lambda aTile: placeMarker(aTile.cell)]
    )
def placeMarker(cell):
    cell.deleteAllAgents()
    cell.newAgentHere(Marker)
    cell.getFirstAgent(Marker).setValue("owner", myModel.getCurrentPlayer().name)

# Create a copy of moveAction for each player (each with a distinct ID)
PlayerMoveActions = {}
for i, player in enumerate(Players.values(), start=1):
    # Create a copy of the action with a new distinct ID
    player_move_action = moveActionTemplate.copy()
    # Add the action to the player
    player.addGameAction(player_move_action)
    PlayerMoveActions[i] = player_move_action

# ============================================================================
# Create pick tile action: Pick a tile from river to player's board
# ============================================================================
def pickTileFromRiver(tile):
    """Pick a tile from river and place it on current player's empty board slot"""    
    # Get the player's board using getGrid_withOwner
    player_grid = myModel.getGrid_withOwner(myModel.getCurrentPlayer())
    if player_grid is None:
        return
    empty_cell = player_grid.getCellType().getEmptyCell()
    tile.moveTo(empty_cell)
    
    
pickTileTemplate = myModel.newActivateAction(
    SeaTile,
    uses_per_round=1,
    method=pickTileFromRiver,
    conditions=[
        lambda tile: tile.cell.type == River,  # Tile must be in river
        lambda tile: tile.isFaceFront()  # Tile must be face front (visible)
    ],
    label="Pick Tile",
    action_controler={"directClick": True}
)

# Add pick tile action to all players
PlayerPickActions = {}
for i, player in enumerate(Players.values(), start=1):
    player_pick_action = pickTileTemplate.copy()
    player.addGameAction(player_pick_action)
    PlayerPickActions[i] = player_pick_action

# ============================================================================
# Create play phases (one Turn phase and one Pick phase for each player)
# ============================================================================

for i in range(1, nb_players + 1):
    # Turn phase: only moveAction is allowed
    myModel.newPlayPhase(f"Player {i} Turn", [Players[i]], authorizedActions=[PlayerMoveActions[i]],
            autoForwardWhenAllActionsUsed=True,message_auto_forward=False)
    # Pick phase: only pickTile is allowed
    myModel.newPlayPhase(f"Player {i} Pick", [Players[i]], authorizedActions=[PlayerPickActions[i]],
            autoForwardWhenAllActionsUsed=True,message_auto_forward=False)
    # Add a model phase to refill the river slots automatically
    myModel.newModelPhase(
        refill_action,
        name="Refill River",
        auto_forward=True,
        message_auto_forward=False
    )
# myModel.setCurrentPlayer("Player 1")


TL = myModel.newTimeLabel(displayPhaseNumber=False,roundNumberFormat="Round {roundNumber}")
TL.moveToCoords(1080, 25)

# Launch the game
myModel.launch()

sys.exit(monApp.exec_())
