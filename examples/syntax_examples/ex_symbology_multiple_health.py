"""
Multiple symbologies example: Different visual representations for same attribute

Demonstrates:
- Simple symbology with border_width (border uses same color as background)
- Advanced symbology with SGAspect (separate border color per value)
- Multiple different symbologies for one attribute (different visual views)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from mainClasses.SGAspect import SGAspect
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Multiple Symbologies Example", width=800, height=400)

# Create grid and agents
Cells = myModel.newCellsOnGrid(5, 5, "square", size=50)
Cells.setEntities("health", 100)

# Add variability: randomly assign different health values
Cells.setEntities_randomChoicePerEntity("health", [100, 50, 25])

Sheep = myModel.newAgentType("Sheep", "triangleAgent1")
Sheep.setDefaultValues({"health": lambda: 100})

# APPROACH 1: Simple border (border color = background color)
# Useful when you want consistent styling with same color for background and border
Cells.newSymbology(
    "health",
    {
        100: QColor("green"),
        50: QColor("orange"),
        25: QColor("red"),
    },
    border_width=3
)

# APPROACH 2: SGAspect shorthand (one-liner per value)
# Allows different border color and width per value
Sheep.newSymbology(
    "health",
    {
        100: SGAspect(bg="lightgreen", border="darkgreen", size=3),
        50: SGAspect(bg="yellow", border="orange", size=2),
        25: SGAspect(bg="red", border="darkred", size=1),
    }
)

# APPROACH 3: Alternative symbology with explicit name
# Demonstrates multiple symbologies for the same attribute
# Use dict shorthand syntax for cleaner code
Cells.newSymbology(
    "health",
    {
        100: {"bg": "lightblue", "border": "darkblue", "size": 2, "style": "dashed"},
        50: {"bg": "lightcyan", "border": "cyan", "size": 1, "style": "dashed"},
        25: {"bg": "lightgray", "border": "gray", "size": 1},
    },
    name="HealthAlternate"
)

Sheep.newSymbology(
    "health",
    {
        100: {"bg": "lightblue", "border": "darkblue", "size": 2},
        50: {"bg": "lightcyan", "border": "cyan", "size": 1},
        25: {"bg": "lightgray", "border": "gray", "size": 1},
    },
    name="HealthAlternate"
)

# Create agents
sheep = Sheep.newAgentAtCoords(Cells, 2, 2)
sheep.setValue("health", 100)

myModel.launch()
sys.exit(monApp.exec())
