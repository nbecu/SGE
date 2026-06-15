"""
Border customization example: Simplified dict syntax

Demonstrates:
- Easy-to-use dict syntax for border customization
- Different border colors and widths per value
- Different border styles (solid, dashed, etc)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Border Customization Example", width=800, height=400)

# Create grid and agent type
Cells = myModel.newCellsOnGrid(5, 5, "square", size=50, gap=5)
Cells.setEntities("health", 100)

# Add variability to visualize different border styles
Cells.setEntities_randomChoicePerEntity("health", [100, 75, 50, 25])
Sheep = myModel.newAgentType("Sheep", "triangleAgent1")
Sheep.setDefaultValues({"health": lambda: 100})

# SIMPLE SYNTAX: Dict with border customization keys
# Keys: bg (background), border (color), size (width), style (solid/dashed/etc)
Cells.newSymbology("health", {
    100: {"bg": "green", "border": "darkgreen", "size": 4, "style": "solid"},
    75: {"bg": "yellow", "border": "blue", "size": 4, "style": "solid"},
    50: {"bg": "orange", "border": "darkorange", "size": 2, "style": "dashed"},
    25: {"bg": "red", "border": "white", "size": 2, "style": "dashed"},
})

# Same for Sheep (creates cross-type "Health" group)
Sheep.newSymbology("health", {
    100: {"bg": "lightgreen", "border": "darkgreen", "size": 4},
    75: {"bg": "lightyellow", "border": "gold", "size": 4},
    50: {"bg": "lightsalmon", "border": "orangered", "size": 2},
    25: {"bg": "lightcoral", "border": "red", "size": 2},
})

# Create agents with varying health
sheep1 = Sheep.newAgentAtCoords(1, 1)
sheep1.setValue("health", 100)

sheep2 = Sheep.newAgentAtCoords(2, 1)
sheep2.setValue("health", 50)

sheep3 = Sheep.newAgentAtCoords(3, 1)
sheep3.setValue("health", 25)

myModel.launch()
sys.exit(monApp.exec())
