import sys
from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# Application initialization
monApp = QtWidgets.QApplication([])

# Model creation
myModel = SGModel(1000, 800, windowTitle="Memory Game - Examples of newTilesWithImages")
myModel.displayTimeInWindowTitle()

# ============================================================================
# Example 1: Memory game with pairs (classic Memory game)
# ============================================================================
print("Example 1: Creating Memory game with pairs...")

# Create a 4x4 grid for Memory
Cell1 = myModel.newCellsOnGrid(4, 4, "square", size=70, gap=5, name="MemoryPairs")

# Create a tile type for Memory cards
# Note: defaultColor not specified - will automatically use backColor (violet) for legends/ControlPanels
# since defaultFace="back"
CardTile1 = myModel.newTileType(
    name="Card1_Pair",
    shape="imageTile",
    defaultSize=65,
    positionOnCell="center",
    defaultFace="back",
    backColor=QColor('violet')
)

# Get all cells for the Memory game
cells1 = [Cell1.getCell(x, y) for x in range(1, 5) for y in range(1, 5)]

# Create tiles with image pairs (8 pairs = 16 tiles)
# Uses images from the main images/ directory
images_dir = Path(__file__).parent.parent.parent / "images"
CardTile1.newTilesWithImages(
    cells=cells1,
    images_directory=images_dir,
    num_images=8,      # 8 unique images
    repetitions=2,     # Each image appears twice (pairs) = 16 tiles total
    shuffle=True,
    face="back"
)

# ============================================================================
# Example 2: Triplets (each image appears 3 times)
# ============================================================================
print("Example 2: Creating tiles with triplets...")

# Create a 3x5 grid for triplets (5 images × 3 = 15 tiles)
Cell2 = myModel.newCellsOnGrid(3, 5, "square", size=70, gap=5, name="Triplets")

# Example with explicit defaultColor: legends will show lightblue (custom color)
# even though tiles show lightgreen on the back face
CardTile2 = myModel.newTileType(
    name="Card2_Triplet",
    shape="imageTile",
    defaultSize=65,
    colorForLegend=QColor("lightblue"),  # Explicit colorForLegend for custom legend color
    positionOnCell="center",
    defaultFace="back",
    backColor=QColor('lightgreen')  # Actual tile back color
)

cells2 = [Cell2.getCell(x, y) for x in range(1, 4) for y in range(1, 6)]

# Create tiles with triplets (5 images × 3 = 15 tiles)
CardTile2.newTilesWithImages(
    cells=cells2,
    images_directory=images_dir,
    num_images=5,      # 5 unique images
    repetitions=3,     # Each image appears three times (triplets) = 15 tiles total
    shuffle=True,
    face="back"
)

# ============================================================================
# Example 3: Singlets (each image appears once)
# ============================================================================
print("Example 3: Creating tiles with singlets...")

# Create a 4x3 grid for singlets (12 cells)
Cell3 = myModel.newCellsOnGrid(4, 3, "square", size=70, gap=5, name="Singlets")

# Example with explicit defaultColor and defaultFace="front"
# Since defaultFace="front" and frontColor not specified, frontColor will use defaultColor (lightyellow)
# Legends will show lightyellow (matches the visible face)
CardTile3 = myModel.newTileType(
    name="Card3_Singlet",
    shape="imageTile",
    defaultSize=65,
    colorForLegend=QColor("lightyellow"),  # Used as frontColor fallback and for legends
    positionOnCell="center",
    defaultFace="front",  # Start face up for singlets
    backColor=QColor('orange')
)

cells3 = [Cell3.getCell(x, y) for x in range(1, 5) for y in range(1, 4)]

# Create tiles with singlets (each image appears once)
# Use 12 images to match the 12 cells available
CardTile3.newTilesWithImages(
    cells=cells3,
    images_directory=images_dir,
    num_images=12,     # Use 12 images to match the 12 cells
    repetitions=1,     # Each image appears once (singlets)
    shuffle=True,
    face="front"       # Start face up
)

# ============================================================================
# Example 4: Four repetitions (each image appears 4 times)
# ============================================================================
print("Example 4: Creating tiles with four repetitions...")

# Create a 4x4 grid for four repetitions (4 images × 4 repetitions = 16 tiles)
Cell4 = myModel.newCellsOnGrid(4, 4, "square", size=70, gap=5, name="FourRepetitions")

# Example with explicit defaultColor: legends will show lavender (custom color)
# even though tiles show purple on the back face
CardTile4 = myModel.newTileType(
    name="Card4_FourRepetitions",
    shape="imageTile",
    defaultSize=60,
    colorForLegend=QColor("lavender"),  # Explicit colorForLegend for custom legend color
    positionOnCell="center",
    defaultFace="back",
    backColor=QColor('purple')  # Actual tile back color
)

cells4 = [Cell4.getCell(x, y) for x in range(1, 5) for y in range(1, 5)]  # 4x4 = 16 cells

# Create tiles with four repetitions (4 images × 4 repetitions = 16 tiles total)
CardTile4.newTilesWithImages(
    cells=cells4,
    images_directory=images_dir,
    num_images=4,      # 4 unique images
    repetitions=4,    # Each image appears four times = 16 tiles total
    shuffle=True,
    face="back"
)

# Create a player to test game actions
Player1 = myModel.newPlayer("Player 1")

# Add Flip action for all tile types
flipAction1 = myModel.newFlipAction(CardTile1, label="🔄 Flip Pair Cards")
flipAction2 = myModel.newFlipAction(CardTile2, label="🔄 Flip Triplet Cards")
flipAction3 = myModel.newFlipAction(CardTile3, label="🔄 Flip Singlet Cards")
flipAction4 = myModel.newFlipAction(CardTile4, label="🔄 Flip Custom Cards")

Player1.addGameAction(flipAction1)
Player1.addGameAction(flipAction2)
Player1.addGameAction(flipAction3)
Player1.addGameAction(flipAction4)
Player1.newControlPanel("Player 1 Actions",defaultActionSelected=flipAction1)

# Create a play phase
myModel.newPlayPhase("Player 1 Turn", [Player1])

# Set current player
myModel.setCurrentPlayer("Player 1")

myModel.applyLayoutConfig("ex_tiles_with_images")
# Launch the game
myModel.launch()

sys.exit(monApp.exec_())

