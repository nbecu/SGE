"""
Multiple symbologies example: Different visual representations for same attribute

Demonstrates:
- Single symbology with multiple aspects (color + border)
- Multiple different symbologies for one attribute (different visual views)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Multiple Symbologies Example", width=800, height=400)

# Create grid and agents
Cells = myModel.newCellsOnGrid(5, 5, "square", size=50)
Cells.setEntities("health", 100)

Sheep = myModel.newAgentType("Sheep", "triangleAgent1")
Sheep.setDefaultValues({"health": lambda: 100})

# Create health symbology with color and border
Cells.newSymbology(
    "health",
    {
        100: QColor("green"),
        50: QColor("orange"),
        25: QColor("red"),
    },
    border_width=3
)

# Same for Sheep (creates cross-type "Health" group)
Sheep.newSymbology(
    "health",
    {
        100: QColor("lightgreen"),
        50: QColor("yellow"),
        25: QColor("red"),
    },
    border_width=2
)

# Create agents
sheep = Sheep.newAgentAtCoords(Cells, 2, 2)
sheep.setValue("health", 100)

myModel.launch()
sys.exit(monApp.exec())
