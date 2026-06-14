"""
Example: Window Auto-Resize Feature

Demonstrates the new autoResize parameter that automatically sizes
the window to fit its content instead of using fixed dimensions.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

# Create a model with autoResize=True
# The window will automatically size to fit the content
myModel = SGModel(autoResize=True, windowTitle="Auto-Resize Example")

# Create a small grid
Cell = myModel.newCellsOnGrid(5, 5, "square", size=50, gap=2)
Cell.setEntities("landUse", "grass")

# Add a simple control panel
Player1 = myModel.newPlayer("Player 1")
Player1ControlPanel = Player1.newControlPanel("Controls")

# The window will now be sized to fit the grid and controls
# rather than forcing a fixed 1800x900 size
myModel.launch()

sys.exit(monApp.exec())
