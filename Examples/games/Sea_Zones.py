import sys
import csv
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
# Load tile definitions from CSV
# ============================================================================
csv_path = Path(__file__).parent.parent.parent / "data" / "import" / "sea_zones" / "tiles.csv"
images_dir = Path(__file__).parent.parent.parent / "data" / "import" / "sea_zones"

tile_definitions = []
with open(csv_path, 'r', encoding='utf-8') as f:
    # CSV uses semicolon delimiter
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        # Strip whitespace from keys and values
        row = {k.strip(): v.strip() for k, v in row.items()}
        # Read stack_on column (comma-separated list of tile names that this biodiv tile can stack on)
        stack_on = row.get('stack_on', '').strip()
        stack_on_list = [name.strip() for name in stack_on.split(',') if name.strip()] if stack_on else []
        
        tile_definitions.append({
            'name': row['name'],
            'nb': int(row['nb']),
            'category': row['category'],
            'stack_on': stack_on_list  # List of tile names this biodiv tile can stack on
        })

# ============================================================================
# Create game board (13x13 grid)
# ============================================================================
Board = myModel.newCellsOnGrid(13, 13, "square", size=50, gap=1, name="Board")

# ============================================================================
# Create river (1 deck cell + 3 slots for drafting)
# ============================================================================
River = myModel.newCellsOnGrid(4, 1, "square", size=80, gap=10, name="River")

# ============================================================================
# Create tile type for Sea Zones tiles
# ============================================================================
SeaTile = myModel.newTileType(
    name="SeaTile",
    shape="imageTile",  # Use imageTile to display images
    defaultSize=50,
    positionOnCell="full",
    defaultFace="back",  # Tiles start face down (back visible)
    backColor=QColor('blue')  # Back face: blue
)

# ============================================================================
# Load images and create tile deck
# ============================================================================
# Load all images from directory and create image list with correct quantities
# Note: Port tile is excluded from deck as it's placed directly on board
front_images = []
tile_info = []  # Store tile info (name, category) for each image
port_image = None  # Store port image separately

for tile_def in tile_definitions:
    tile_name = tile_def['name']
    tile_count = tile_def['nb']
    tile_category = tile_def['category']
    
    # Load image for this tile
    image_path = images_dir / f"{tile_name}.jpg"
    if image_path.exists():
        pixmap = QPixmap(str(image_path))
        if not pixmap.isNull():
            # Special handling for port tile: store image but don't add to deck
            if tile_name == "port":
                port_image = pixmap
                # Port tile is placed directly on board, so reduce count by 1 for deck
                tile_count = tile_count - 1
            
            # Add image multiple times according to quantity (if count > 0)
            for i in range(tile_count):
                front_images.append(pixmap)
                tile_info.append({
                    'name': tile_name,
                    'category': tile_category,
                    'stack_on': tile_def.get('stack_on', [])  # Store stack_on information
                })

# Shuffle images and tile_info together to keep them synchronized
combined = list(zip(front_images, tile_info))
random.shuffle(combined)
front_images, tile_info = zip(*combined) if combined else ([], [])
front_images = list(front_images)
tile_info = list(tile_info)

# Create deck stack on first river cell (cell 1,1) using newStackOnCell
deck_cell = River.getCell(1, 1)
deck_stack = SeaTile.newStackOnCell(
    deck_cell,
    count=len(front_images),
    face="back",  # Start face down
    frontImages=front_images  # Front face has the images
)

# Set attributes (tile_name, category, stack_on) for each tile in the stack
deck_tiles = deck_stack.tiles
for i, tile in enumerate(deck_tiles):
    if i < len(tile_info):
        tile.setValue("tile_name", tile_info[i]['name'])
        tile.setValue("category", tile_info[i]['category'])
        tile.setValue("stack_on", tile_info[i].get('stack_on', []))

# ============================================================================
# Place starting port tile at center of board (7, 7)
# ============================================================================
center_cell = Board.getCell(7, 7)

# Create port tile directly at center of board (not from deck)
if port_image:
    port_tile = SeaTile.newTileOnCell(
        center_cell,
        face="front",  # Show port tile face up
        frontImage=port_image
    )
    if port_tile:
        port_tile.setValue("tile_name", "port")
        port_tile.setValue("category", "debut")
        port_tile.view.show()

# ============================================================================
# Set up Open Drafting for river (3 drafting slots: cells 2, 3, 4)
# ============================================================================
river_slots = [River.getCell(2, 1), River.getCell(3, 1), River.getCell(4, 1)]
refill_action = deck_stack.setOpenDrafting(
    slots=river_slots,
    visibleFace="front",  # Tiles show front face when drafted to river
    visibleFaceOfTopTileOfStack="back"  # Top tile of deck shows back
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
# 1. Target cell must be empty OR allow biodiv stacking (if tile is biodiv and can stack on existing tile)
# 2. Can only move to board
# 3. Can only move from river
# 4. Target cell must be orthogonally adjacent to at least one cell with a SeaTile
def canPlaceTile(tile, cell):
    """Check if tile can be placed on cell (empty or biodiv stacking allowed)"""
    # If cell is empty, placement is allowed
    if cell.isEmpty():
        return True
    
    # If cell has a tile, check biodiv stacking rules
    if cell.hasTile(SeaTile):
        # Get the top tile on the cell
        stack = cell.getStack(SeaTile)
        existing_tile = stack.topTile()
        
        if existing_tile is None:
            return True  # No tile found, treat as empty
        
        # Check if the tile to place is biodiv
        tile_category = tile.getValue("category")
        if tile_category != "biodiv":
            return False  # Only biodiv tiles can stack
        
        # Check if this biodiv tile can stack on the existing tile
        stack_on_value = tile.getValue("stack_on")
        if stack_on_value:
            # Handle both list and string formats
            if isinstance(stack_on_value, list):
                stack_on_list = stack_on_value
            elif isinstance(stack_on_value, str):
                # Parse comma-separated string
                stack_on_list = [name.strip() for name in stack_on_value.split(',') if name.strip()]
            else:
                stack_on_list = []
            
            if stack_on_list:
                existing_tile_name = existing_tile.getValue("tile_name")
                return existing_tile_name in stack_on_list
        
    return False

moveAction = myModel.newMoveAction(
    SeaTile,
    label="Place Tile",
    conditions=[
        canPlaceTile,  # Target cell must be empty or allow biodiv stacking
        lambda tile, cell: cell.type == Board,  # Can only move to board
        lambda tile: tile.cell.type == River,  # Can only move from river
        # Check orthogonal adjacency: at least one neighbor must have a SeaTile
        lambda tile, cell: any(
            neighbor.hasTile(SeaTile) 
            for neighbor in cell.getNeighborCells(neighborhood="neumann")
        )
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
