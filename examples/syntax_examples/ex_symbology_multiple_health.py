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

# APPROACH 2: Advanced - Full control with SGAspect
# Allows different border color and width per value
aspect_100 = SGAspect()
aspect_100.background_color = "lightgreen"
aspect_100.border_color = "darkgreen"
aspect_100.border_size = 3

aspect_50 = SGAspect()
aspect_50.background_color = "yellow"
aspect_50.border_color = "orange"
aspect_50.border_size = 2

aspect_25 = SGAspect()
aspect_25.background_color = "red"
aspect_25.border_color = "darkred"
aspect_25.border_size = 1

Sheep.newSymbology(
    "health",
    {
        100: aspect_100,
        50: aspect_50,
        25: aspect_25,
    }
)

# Create agents
sheep = Sheep.newAgentAtCoords(Cells, 2, 2)
sheep.setValue("health", 100)

myModel.launch()
sys.exit(monApp.exec())
