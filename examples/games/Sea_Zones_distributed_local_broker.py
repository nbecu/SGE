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
myModel = SGModel(1200, 850, windowTitle="Sea Zones")
myModel.displayTimeInWindowTitle()

# ============================================================================
# Distributed Game Configuration - MUST BE CALLED BEFORE ANY RANDOM OPERATIONS
# ============================================================================
# Enable distributed multiplayer game mode
# This will:
# 1. Open dialog to connect to MQTT broker and synchronize seed
# 2. Seed is synchronized and applied immediately after this call
# 3. Player selection happens later when the game window opens

myModel.enableDistributedGame(num_players=(2,4))
nb_players = myModel.getConnectedInstancesCount(default=4) 

# The seed is synchronized and applied automatically by enableDistributedGame()

# ============================================================================
# Paths configuration
# ============================================================================
csv_path = Path(__file__).parent.parent.parent / "data" / "import" / "sea_zones" / "tiles.csv"
images_dir = Path(__file__).parent.parent.parent / "data" / "import" / "sea_zones"

# ============================================================================
# Create game board (13x13 grid)
# ============================================================================
Board = myModel.newCellsOnGrid(13, 13, "square", size=50, gap=1, name="Board",neighborhood="neumann",defaultCellColor=Qt.transparent)
Board.grid.setBackgroundImage(QPixmap(f"{images_dir}/fond_plateau.png"))

# ============================================================================
# Create river (1 deck cell + 3 slots for drafting)
# ============================================================================
River = myModel.newCellsOnGrid(4, 1, "square", size=80, gap=10, name="River")
deck_cell = River.getCell(1, 1)
River.grid.moveToCoords(700, 25)

# ============================================================================
# Create individual player boards (3 cells each, positioned under river)
# ============================================================================

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
    backImage=QPixmap(f"{images_dir}/dos_tuile.png"),
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
        'points_bonus_biodiversity': ('attribute', 'points_bonus_biodiversity', 'int'),
        'points_from_adjacent_tile': ('attribute', 'points_from_adjacent_tile', 'int'),
        'points_if_no_adjacent': ('attribute', 'points_if_no_adjacent', 'int'),
        'adjacent_tile_for_bonus': ('attribute', 'adjacent_tile_for_bonus', 'list'),
        'points_in_line': ('attribute', 'points_in_line', 'int'),
        'tile_in_line_for_bonus': ('attribute', 'tile_in_line_for_bonus', 'list'),
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
# Function to adjust magnifier to show all tiles + one row of empty cells on each side
# ============================================================================
def adjustMagnifyToCoverAllTiles(aTile = None):
    """Adjust magnifier to show all tiles on Board + one row of empty cells on each side"""

    # Get all cells with tiles on the Board
    cells_with_tiles = Board.getEntities(condition=lambda c: c.hasTile())
    
    if not cells_with_tiles:
        # No tiles, do nothing
        return
    
    # Calculate bounding box of cells with tiles
    min_x = min(cell.xCoord for cell in cells_with_tiles)
    max_x = max(cell.xCoord for cell in cells_with_tiles)
    min_y = min(cell.yCoord for cell in cells_with_tiles)
    max_y = max(cell.yCoord for cell in cells_with_tiles)
    
    # If the tile placed is not in the peripheral box, do nothing
    if aTile is not None:
        if not (aTile.cell.xCoord in [min_x, max_x] or aTile.cell.yCoord in [min_y, max_y]):
            return
    
    # Extend by one row on each side (with bounds checking)
    margin = 1
    min_x_extended = max(1, min_x - margin)
    max_x_extended = min(Board.grid.columns, max_x + margin)
    min_y_extended = max(1, min_y - margin)
    max_y_extended = min(Board.grid.rows, max_y + margin)
    
    # Get corner cells for the extended area
    cell_min = Board.getCell(min_x_extended, min_y_extended)
    cell_max = Board.getCell(max_x_extended, max_y_extended)
    
    # Set magnifier to show the extended area
    Board.grid.setMagnifierOnArea(cell_min, cell_max)

# Set initial magnifier view (tile at 7,7 -> magnify area from 6,6 to 8,8)
adjustMagnifyToCoverAllTiles()

# ============================================================================
# Place end tile in the last 10 tiles of the stack 
# ============================================================================
ending_tile = SeaTile.getEntities_withValue("tile_name", "maree_basse")[0]
# Position the ending tile at a random layer between 1 and 10
target_layer = random.randint(1, 10)
# target_layer = random.randint(50, 51)
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
Marker = myModel.newAgentType("Marker", "circleAgent", defaultSize=13,defaultColor=Qt.black,locationInEntity="topRight")
# Marker.newPov("default", "owner", {"Player 1": Qt.blue,"Player 2": Qt.red})
Marker.newPov("default", "owner", {
    "Player 1":QPixmap(f"{images_dir}/jeton_bleu.png"),
    "Player 2": QPixmap(f"{images_dir}/jeton_rouge.png"),
    "Player 3": QPixmap(f"{images_dir}/jeton_jaune.png"),
    "Player 4": QPixmap(f"{images_dir}/jeton_vert.png")})

Marker.displayPov("default")
Board.setDefaultValue("owner", "")

# ============================================================================
# Score calculation constants
# ============================================================================
points_biodiv_stack = {1:1, 2:2, 3:4, 4:7, 5:11, 6:12, 7:13, 8:14}
points_eoliennes = {0:0, 1:2, 2:3, 3:4}  # nb_max_eoliennes -> points

# ============================================================================
# Score calculation function
# ============================================================================
def calculateScores():
    """Calculate scores for all players based on tiles on the board"""
    # Initialize scores to 0
    for player in Players.values():
        player.setValue("score", 0)
    
    # Iterate through all cells on the board that have tiles
    for cell in Board.getEntities(condition=lambda c: c.hasTile() and c.getFirstTile().isNotValue("tile_name", "port")):
        # Get the owner of this cell (from marker)
        owner_name = cell.getFirstAgent().getValue("owner")
        if not owner_name or owner_name not in myModel.players:
            print(f'this never happens 11 {owner_name}')
            continue
        
        # Get the player object
        player = myModel.players[owner_name]
        
        # Get the stack and top tile
        stack = cell.getStack(SeaTile)
        if stack.isEmpty():
            print(f'this never happens 22 {owner_name}')
            continue
        
        top_tile = stack.topTile()
        category = top_tile.getValue("category")
        tile_name = top_tile.getValue("tile_name")
        stack_height = stack.size()
        
        cell_score = 0
        
        # 1. If category is "biodiv"
        if category == "biodiv":
            cell_score += points_biodiv_stack[stack_height]
            cell_score += top_tile.getValue("points_bonus_biodiversity")
        
        # 2. If category is "act_humaine"
        elif category == "act_humaine":
            # d) Special case: association_nature (score = max stack height of neighbors)
            if tile_name == "association_nature":
                neighbors_with_tiles = cell.getNeighborCells(condition=lambda c: c.hasTile(condition=lambda tile: tile.isValue("category","biodiv")))
                if neighbors_with_tiles:
                    cell_score = max(neighbor.getStack(SeaTile).size() for neighbor in neighbors_with_tiles)
            
            # e) Special case: eoliennes
            elif tile_name == "eoliennes":
                # Get neighbors with "cables" top tile
                cables_neighbors = cell.getNeighborCells(
                    condition=lambda c: c.hasTile() and
                    c.getStack(SeaTile).topTile().isValue("tile_name", "cables")
                )
                
                if not cables_neighbors:
                    cell_score = 0
                else:
                    # For each cables cell, count neighbors with "eoliennes"
                    nb_max_eoliennes = max(
                        len(cables_cell.getNeighborCells(
                            condition=lambda c: c.hasTile() and
                            c.getStack(SeaTile).topTile().isValue("tile_name", "eoliennes")
                        ))
                        for cables_cell in cables_neighbors
                    )
                    cell_score = points_eoliennes.get(nb_max_eoliennes)
            
            # For other act_humaine tiles, calculate normal points
            else:
                # a) Points from adjacent tiles
                adjacent_tile_list = top_tile.getValue("adjacent_tile_for_bonus")
                points_from_adjacent = top_tile.getValue("points_from_adjacent_tile")
                has_matching_adjacent = False
                
                if adjacent_tile_list:
                    # Check each neighbor and add points for each match
                    for neighbor in cell.getNeighborCells(condition=lambda c: c.hasTile()):
                        neighbor_tile_name = neighbor.getStack(SeaTile).topTile().getValue("tile_name")
                        if neighbor_tile_name in adjacent_tile_list:
                            cell_score += points_from_adjacent
                            has_matching_adjacent = True
                
                # b) Points if no adjacent matching tile
                if not has_matching_adjacent:
                    cell_score += top_tile.getValue("points_if_no_adjacent")
                
                # c) Points in line (row or column)
                points_in_line = top_tile.getValue("points_in_line")
                tile_in_line_list = top_tile.getValue("tile_in_line_for_bonus")
                
                if points_in_line and tile_in_line_list:
                    # Count cells in same row with matching tiles
                    row_cells = Board.getEntities_withRow(cell.yCoord)
                    nbCellsInRowCorresponding = sum(
                        1 for row_cell in row_cells
                        if row_cell.hasTile() and not row_cell.getStack(SeaTile).isEmpty() and
                        row_cell.getStack(SeaTile).topTile().getValue("tile_name") in tile_in_line_list
                    )
                    
                    # Count cells in same column with matching tiles
                    col_cells = Board.getEntities_withColumn(cell.xCoord)
                    nbCellsInColumnCorresponding = sum(
                        1 for col_cell in col_cells
                        if col_cell.hasTile() and not col_cell.getStack(SeaTile).isEmpty() and
                        col_cell.getStack(SeaTile).topTile().getValue("tile_name") in tile_in_line_list
                    )
                    
                    # Take max and multiply by points_in_line
                    cell_score += max(nbCellsInRowCorresponding, nbCellsInColumnCorresponding) * points_in_line
        
        # Add cell score to player's total score
        player.incValue("score", cell_score)


# ============================================================================
# Create players and distribute initial tiles
# ============================================================================
Players = {}
for i in range(1, nb_players + 1):
    player = myModel.newPlayer(f"Player {i}")
    Players[i] = player
    player.setValue("score", 0)  # Initialize score to 0
    
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
# Configure player board visibility (for distributed mode)
# ============================================================================
# Player selection happens automatically in initAfterOpening() when window opens
# Visibility is configured automatically when player is selected
if myModel.isDistributed():
    for i in range(1, nb_players + 1):
        player_board = PlayerBoards[i]
        player = Players[i]
        player_board.grid.setVisibilityForPlayers(player.name)

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
        lambda tile, cell: len(cell.getNeighborCells(condition=lambda c: c.hasTile())) > 0,
        # Check that placing a tile would not exceed horizontal range of 7 across entire grid
        lambda tile, cell: cell.getMaxRangeOfCells_horizontally(condition=lambda c: c.hasTile(), includingSelf=True) <= 7,
        # Check that placing a tile would not exceed vertical range of 7 across entire grid
        lambda tile, cell: cell.getMaxRangeOfCells_vertically(condition=lambda c: c.hasTile(), includingSelf=True) <= 7
    ],
    action_controler={"directClick": True},
    feedbacks=[
        lambda aTile: placeMarker(aTile.cell),
        lambda aTile: adjustMagnifyToCoverAllTiles(aTile)
    ]
    )
def placeMarker(cell):
    cell.deleteAllAgents()
    cell.newAgentHere(Marker)
    cell.getFirstAgent(Marker).setValue("owner", myModel.getCurrentPlayer().name)
    # Recalculate scores after placing a tile
    calculateScores()

# Create a copy of moveAction for each player (each with a distinct ID)
PlayerMoveActions = {}
for i, player in enumerate(Players.values(), start=1):
    # Create a copy of the action with a new distinct ID
    player_move_action = moveActionTemplate.copy()
    # Add the action to the player
    player.addGameAction(player_move_action)
    PlayerMoveActions[i] = player_move_action

# ============================================================================
# Create score dashboard
# ============================================================================
scoreDashboard = myModel.newDashBoard()
for player in Players.values():
    scoreDashboard.addIndicatorOnEntity(player, "score",title= f'Score of {player.name}')
scoreDashboard.moveToCoords(520, 700)

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
        lambda tile: tile.isFaceFront(),  # Tile must be face front (visible)
        lambda tile: tile != ending_tile # Tile must not be the ending tile
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

endGameRule =myModel.newEndGameRule(title='The game ends when')
# Add an end game condition with trigger delay
# delay_rounds: number of remaining rounds after the condition is met (here 1 complete round)
# final_phase: 'last phase' to end at the last phase of the round
endGameRule.addEndGameCondition_onLambda(
    lambda: ending_tile.isFaceFront(), 
    name='the tile  "low tide"  is drawn',
    delay_rounds=1,  # 1 round remaining after the condition is met
    # final_phase='last phase'  # End at the last phase of the round
    final_phase= (myModel.timeManager.numberOfPhases() -2)
)
endGameRule.displayEndGameConditions()
endGameRule.moveToCoords(0, 750)
endGameRule.setEndGameDisplay(
    mode='highlight + banner',
    countdown_display_mode='rounds_only',
    banner_position='bottom',
    banner_text='The game is over',
    animation_enabled=True,
    animation_duration=4)

# Launch the game
myModel.launch()

sys.exit(monApp.exec_())
