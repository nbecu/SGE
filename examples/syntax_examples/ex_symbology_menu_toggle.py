"""
Test menu structure: GROUPS first, then BY TYPE, with toggle-off support

Demonstrates:
- Menu order: GROUPS section at top, separator, then BY TYPE section
- Toggle-off: clicking a selected radio button again deselects it (returns to default)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Menu Structure Test", width=800, height=400)

# Create grid and agents
Cells = myModel.newCellsOnGrid(3, 3, "square", size=50)
Cells.setEntities("health", 100)
Cells.setEntities_randomChoicePerEntity("health", [100, 50, 25])

Sheep = myModel.newAgentType("Sheep", "triangleAgent1")
Sheep.setDefaultValues({"health": lambda: 100})

Wolves = myModel.newAgentType("Wolves", "circleAgent1")
Wolves.setDefaultValues({"health": lambda: 100})

# Create symbologies for Cell and Sheep (will form a GROUP)
Cells.newSymbology("health", {
    100: {"bg": "green", "border": "darkgreen", "size": 2},
    50: {"bg": "orange", "border": "darkorange", "size": 1},
    25: {"bg": "red", "border": "darkred", "size": 1},
}, name="Health")

Sheep.newSymbology("health", {
    100: {"bg": "lightgreen", "border": "darkgreen", "size": 2},
    50: {"bg": "lightyellow", "border": "orange", "size": 1},
    25: {"bg": "lightcoral", "border": "darkred", "size": 1},
}, name="Health")

# Create symbology only for Wolves (will NOT be a group)
Wolves.newSymbology("health", {
    100: {"bg": "purple", "border": "indigo", "size": 3},
    50: {"bg": "plum", "border": "purple", "size": 2},
    25: {"bg": "thistle", "border": "plum", "size": 1},
}, name="Health")

# Create agents
sheep1 = Sheep.newAgentAtCoords(1, 1)
sheep1.setValue("health", 100)

wolves1 = Wolves.newAgentAtCoords(2, 2)
wolves1.setValue("health", 50)

# Instructions for testing
print("=" * 60)
print("Menu Structure Test Instructions:")
print("=" * 60)
print("\n✓ Menu order should be:")
print("  1. GROUPS section (with 'Health' checkbox)")
print("  2. Separator line")
print("  3. BY TYPE section (Cell, Sheep, Wolves submenus)")
print("\n✓ Test toggle-off:")
print("  1. Open Symbology menu → Cell → Health (select it)")
print("  2. Click on Cell → Health again (should deselect & return to default)")
print("  3. Cells should turn white with black borders (default display)")
print("\n✓ Test GROUPS section:")
print("  1. Check the 'Health' checkbox in GROUPS")
print("  2. Both Cell and Sheep should display Health symbology")
print("  3. Uncheck 'Health' to toggle groups")
print("=" * 60)

myModel.launch()
sys.exit(monApp.exec())
