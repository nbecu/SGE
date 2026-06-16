"""
Groups and hierarchy example: Cross-entity-type symbology groups

Demonstrates:
- Automatic group creation when multiple types share same-named symbology
- Hierarchical resolution (Entity overrides > Type defaults > global)
- Querying groups
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Symbology Groups Example")

# Create multiple entity types
Cells = myModel.newCellsOnGrid(3, 3, "square", size=60)
Cells.setEntities("fertility", 0)

# Add variability to show symbology visually
Cells.setEntities_randomChoicePerEntity("fertility", [0, 1])

Sheep = myModel.newAgentType("Sheep", "triangleAgent1")
Sheep.setDefaultValues({"fertility": lambda: 50})

Cows = myModel.newAgentType("Cows", "squareAgent")
Cows.setDefaultValues({"fertility": lambda: 75})

# Define "Fertility" symbology for each type
# All use auto-derived name "Fertility"
# This automatically creates a cross-entity group!

Cells.newSymbology(
    "fertility",
    {0: QColor("brown"), 1: QColor("green")},
)

Sheep.newSymbology(
    "fertility",
    {0: QColor("gray"), 50: QColor("white"), 100: QColor("black")},
)

Cows.newSymbology(
    "fertility",
    {0: QColor("gray"), 50: QColor("brown"), 100: QColor("black")},
)

# Create agent instances to visualize symbologies
# Create Sheep with varying fertility (note: grid coordinates start at 1, not 0)
sheep1 = Sheep.newAgentAtCoords(1, 1)
sheep1.setValue("fertility", 0)

sheep2 = Sheep.newAgentAtCoords(2, 1)
sheep2.setValue("fertility", 50)

sheep3 = Sheep.newAgentAtCoords(3, 1)
sheep3.setValue("fertility", 100)

# Create Cows with varying fertility
cow1 = Cows.newAgentAtCoords(1, 3)
cow1.setValue("fertility", 0)

cow2 = Cows.newAgentAtCoords(2, 3)
cow2.setValue("fertility", 50)

cow3 = Cows.newAgentAtCoords(3, 3)
cow3.setValue("fertility", 100)

# Demonstrate instance symbology override
cell = Cells.getCell(1, 1)
cell.setValue("fertility", 0)

# Apply instance override to this specific cell
cell.setInstanceSymbology("Fertility", "fertility", {0: QColor("purple"), 1: QColor("cyan")})

# Create legend to visualize symbologies
# Question: Do instance symbologies appear in the legend?
legend = myModel.newLegend()

# Launch
myModel.launch()
sys.exit(monApp.exec())
