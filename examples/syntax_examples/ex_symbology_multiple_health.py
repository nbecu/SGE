"""
Multiple symbologies example: Different visual representations for same attribute (CASE 2)

Demonstrates:
- Multiple symbologies for one attribute
- Explicit naming required (name= parameter)
- Combining different aspects (color + border)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Multiple Symbologies Example", width=800, height=400)

# Create grid
Cells = myModel.newCellsOnGrid(5, 5, "square", size=50)
Cells.setEntities("health", 100)

# CASE 2: Multiple symbologies for "health" attribute
# Each needs explicit name

# Version 1: Color-based (name="HealthColor")
Cells.newSymbology(
    "health",
    {
        100: QColor("green"),
        50: QColor("orange"),
        25: QColor("red"),
    },
    name="HealthColor"  # EXPLICIT name required
)

print("Created 'HealthColor' symbology")

# Version 2: Border-based (name="HealthBorder")
Cells.newSymbology(
    "health",
    {
        100: {"color": QColor("darkgreen"), "width": 3},
        50: {"color": QColor("orange"), "width": 2},
        25: {"color": QColor("red"), "width": 1},
    },
    symbol_type="border",
    name="HealthBorder"  # EXPLICIT name required
)

print("Created 'HealthBorder' symbology")

print(f"\nModel symbologies: {list(myModel.symbologies.keys())}")

# What happens if we forget the name?
print("\n--- Attempting to create 2nd auto-derived 'Health' ---")
try:
    Cells.newSymbology("health", {100: QColor("blue")})
    print("[ERROR] Should have failed!")
except ValueError as e:
    print(f"[EXPECTED] Got error: {str(e)[:60]}...")

# Different entity type CAN use same auto-derived name!
Sheep = myModel.newAgentType("Sheep", "triangleAgent1")
Sheep.setDefaultValues({"health": lambda: 100})

Sheep.newSymbology(
    "health",
    {
        100: QColor("green"),
        50: QColor("orange"),
        25: QColor("red"),
    }
    # No name= needed! Auto-derived "Health" is OK for different type
)

print("\nDifferent entity type (Sheep) can use auto-derived 'Health'")
print(f"Groups now: {list(myModel.symbology_groups.keys())}")
print(f"'Health' group types: {myModel.symbology_groups['Health'].get_all_entity_types()}")

# Create some sheep
sheep = Sheep.newAgentAtCoords(Cells, 3, 3)
sheep.setValue("health", 100)

myModel.launch()
sys.exit(monApp.exec())
