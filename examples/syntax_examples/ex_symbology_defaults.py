"""
Shared aspect example: Apply properties to all symbology values

Demonstrates:
- Using shared_aspect to apply properties to ALL values in a symbology
- DRY principle: no need to repeat properties for each value
- Per-value customization with shared fallback properties
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Shared Aspect Example", width=900, height=400)

# Create grids to show two approaches
grid_1 = myModel.newCellsOnGrid(3, 3, "square", size=50, name="Grid1")
grid_1.setEntities("health", 100)
grid_1.setEntities_randomChoicePerEntity("health", [100, 50, 25])

grid_2 = myModel.newCellsOnGrid(3, 3, "square", size=50, name="Grid2")
grid_2.setEntities("health", 100)
grid_2.setEntities_randomChoicePerEntity("health", [100, 50, 25])

# APPROACH 1: WITHOUT shared aspect (repetitive - shown for comparison)
grid_1.newSymbology("health", {
    100: {"bg": "green", "border": "darkgreen", "size": 2, "style": "solid"},
    50: {"bg": "orange", "border": "darkorange", "size": 2, "style": "solid"},
    25: {"bg": "red", "border": "darkred", "size": 2, "style": "solid"}
}, name="HealthRepetitive")

# APPROACH 2: WITH shared aspect (clean and DRY)
# shared_aspect: border_size, border_color, border_style apply to ALL health values
grid_2.newSymbology("health", {
    100: {"bg": "lightgreen"},
    50: {"bg": "lightyellow"},
    25: {"bg": "lightcoral"}
}, border_size=2, border_color="black", border_style="solid", name="HealthShared")

# Agents with alternative defaults
Sheep = myModel.newAgentType("Sheep", "triangleAgent1")
Sheep.setDefaultValues({"health": lambda: 100})

# Example: Different border style per group
Sheep.newSymbology("health", {
    100: {"bg": "lightgreen"},
    50: {"bg": "lightyellow"},
    25: {"bg": "lightcoral"}
}, border_size=3, border_color="navy", border_style="dashed")

# Create agents to visualize
for i in range(1, 4):
    sheep = Sheep.newAgentAtCoords(i, 1)
    sheep.setValue("health", 100 - (i - 1) * 25)

myModel.launch()
sys.exit(monApp.exec())
