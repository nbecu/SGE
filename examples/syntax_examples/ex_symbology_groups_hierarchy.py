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
from mainClasses.SGAspectSystem import SGAspectResolver
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Symbology Groups Example")

# Create multiple entity types
Cells = myModel.newCellsOnGrid(3, 3, "square", size=60)
Cells.setEntities("fertility", 0)

Sheep = myModel.newAgentType("Sheep", "triangleAgent1")
Sheep.setDefaultValues({"fertility": lambda: 50})

Cows = myModel.newAgentType("Cows", "squareAgent")
Cows.setDefaultValues({"fertility": lambda: 75})

# Define "Fertility" symbology for each type
# All use auto-derived name "Fertility"
# This automatically creates a cross-entity group!

print("=" * 60)
print("Creating symbologies...")
print("=" * 60)

Cells.newSymbology(
    "fertility",
    {0: QColor("brown"), 1: QColor("green")},
)
print("Cells.newSymbology('fertility', ...) >> auto-name: 'Fertility'")

Sheep.newSymbology(
    "fertility",
    {0: QColor("gray"), 50: QColor("white"), 100: QColor("black")},
)
print("Sheep.newSymbology('fertility', ...) >> auto-name: 'Fertility'")

Cows.newSymbology(
    "fertility",
    {0: QColor("gray"), 50: QColor("brown"), 100: QColor("black")},
)
print("Cows.newSymbology('fertility', ...) >> auto-name: 'Fertility'")

# Check automatic group creation
print("\n" + "=" * 60)
print("Automatic group created!")
print("=" * 60)

fertility_group = SGAspectResolver.get_symbology_group(myModel, "Fertility")
if fertility_group:
    print(f"Group name: {fertility_group.name}")
    print(f"Entity types in group: {fertility_group.get_all_entity_types()}")
    for type_name in fertility_group.get_all_entity_types():
        symb = fertility_group.get_symbology_for_type(type_name)
        print(f"  - {type_name}: {len(symb.mapping)} value(s) mapped")

# Create agent instances to visualize symbologies
print("\n" + "=" * 60)
print("Creating agent instances...")
print("=" * 60)

# Create Sheep with varying fertility (note: grid coordinates start at 1, not 0)
sheep1 = Sheep.newAgentAtCoords(1, 1)
sheep1.setValue("fertility", 0)

sheep2 = Sheep.newAgentAtCoords(2, 1)
sheep2.setValue("fertility", 50)

sheep3 = Sheep.newAgentAtCoords(3, 1)
sheep3.setValue("fertility", 100)

print(f"[OK] Created 3 Sheep with fertility: {sheep1.value('fertility')}, {sheep2.value('fertility')}, {sheep3.value('fertility')}")

# Create Cows with varying fertility
cow1 = Cows.newAgentAtCoords(1, 3)
cow1.setValue("fertility", 0)

cow2 = Cows.newAgentAtCoords(2, 3)
cow2.setValue("fertility", 50)

cow3 = Cows.newAgentAtCoords(3, 3)
cow3.setValue("fertility", 100)

print(f"[OK] Created 3 Cows with fertility: {cow1.value('fertility')}, {cow2.value('fertility')}, {cow3.value('fertility')}")

# Demonstrate hierarchical resolution
print("\n" + "=" * 60)
print("Hierarchical Resolution: Entity > Type > Default")
print("=" * 60)

cell = Cells.getCell(1, 1)
cell.setValue("fertility", 0)

# Type-level resolution (no instance override)
color = SGAspectResolver.resolve_color(cell, "Fertility", "fertility", QColor("black"))
print(f"Cell(1,1) fertility=0 >> Type resolution >> {color.name()}")

# Instance override
cell.setInstanceSymbology("Fertility", "fertility", {0: QColor("purple"), 1: QColor("cyan")})
color_override = SGAspectResolver.resolve_color(cell, "Fertility", "fertility", QColor("black"))
print(f"After instance override >> {color_override.name()}")

# Launch
myModel.launch()
sys.exit(monApp.exec())
