"""
Simple example: Basic symbology with auto-derived names (CASE 1)

Demonstrates the most common use case:
- One symbology per attribute
- Auto-derived names (health -> Health)
- Simple, intuitive API
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

# Create model
myModel = SGModel(windowTitle="Health Symbology Example", width=600, height=400)

# Create grid with cells
Cells = myModel.newCellsOnGrid(5, 5, "square", size=50)
Cells.setEntities("health", 100)  # All cells start with health=100

# Define health symbology (auto-derived name: "Health")
Cells.newSymbology(
    "health",
    {
        100: QColor("green"),   # Full health = green
        75: QColor("yellow"),   # Medium = yellow
        50: QColor("orange"),   # Low = orange
        25: QColor("red"),      # Critical = red
    }
)

print("Created 'Health' symbology for Cells")
print(f"Model symbologies: {list(myModel.symbologies.keys())}")
print(f"Model groups: {list(myModel.symbology_groups.keys())}")

# Create some agents with health attribute
Sheep = myModel.newAgentType("Sheep", "triangleAgent1")
Sheep.setDefaultValues({"health": lambda: 100})

# Agents also use health - automatically creates group!
Sheep.newSymbology(
    "health",
    {
        100: QColor("green"),
        75: QColor("yellow"),
        50: QColor("orange"),
        25: QColor("red"),
    }
)

print("\nCreated 'Health' symbology for Sheep")
print(f"Now 'Health' is a cross-entity-type group!")
print(f"Group contains: {myModel.symbology_groups['Health'].get_all_entity_types()}")

# Create some sheep
for i in range(1, 4):
    sheep = Sheep.newAgentAtCoords(Cells, i, 1)
    sheep.setValue("health", 100 - (i * 25))  # Vary health

# Launch
myModel.launch()
sys.exit(monApp.exec())
