"""
Example: Auto-Resize Smart Default

Shows how SGModel now auto-enables resize when width/height are not specified.
This is a cleaner API for simple models.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

# SIMPLE: Just specify what you want - window sizes automatically!
myModel = SGModel(windowTitle="Auto-Resize Smart Default")

# Create content
Cell = myModel.newCellsOnGrid(3, 3, "square", size=60, gap=3)
Cell.setEntities("landUse", "grass")

Player1 = myModel.newPlayer("Player 1")
Player1ControlPanel = Player1.newControlPanel("Player Controls")

# The window will be sized to perfectly fit the grid and controls
myModel.launch()

sys.exit(monApp.exec())
