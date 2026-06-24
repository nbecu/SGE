"""
Automatic Symbology Groups - Cross-Entity Type Example (Phase 3)

Demonstrates:
- AUTOMATIC group creation when multiple entity types share same-named symbology
- How one group can coordinate different symbology definitions across entity types
- Each entity type has its own visual style, but they're grouped under one name
- Querying and understanding automatic groups

KEY CONCEPT - Automatic Groups:
When you create same-named symbologies on different entity types,
they automatically form a GROUP that can be activated together.

Example:
  Cell.newSymbology("fertility", {...})     ← Cells show fertility as colors
  Sheep.newSymbology("fertility", {...})    ← Sheep show fertility as colors
  Cows.newSymbology("fertility", {...})     ← Cows show fertility as colors
  → Automatically creates group "Fertility" spanning all 3 types!

Benefit:
  - Users see the SAME ATTRIBUTE across different entity types
  - Each type has appropriate visualization for its values
  - Switching the group activates all three symbologies at once
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Automatic Symbology Groups - Fertility Attribute", width=1000, height=700)

# ============================================================================
# Create multiple entity types with the SAME ATTRIBUTE
# ============================================================================

# Cell type with fertility ranging 0-1
Cells = myModel.newCellsOnGrid(3, 3, "square", size=60)
Cells.setEntities("fertility", 0)
Cells.setEntities_randomChoicePerEntity("fertility", [0, 1])

# Sheep type with fertility ranging 0-100
Sheep = myModel.newAgentType("Sheep", "triangleAgent1")
Sheep.setDefaultValues({"fertility": lambda: 50})

# Cows type with fertility ranging 0-100
Cows = myModel.newAgentType("Cows", "squareAgent")
Cows.setDefaultValues({"fertility": lambda: 75})

# ============================================================================
# Define same-named symbologies for EACH type
# (All use auto-derived name "Fertility" - this creates the automatic group!)
# ============================================================================

# Cells show fertility as: brown (sterile) → green (fertile)
Cells.newSymbology(
    "fertility",
    {0: QColor("brown"), 1: QColor("green")},
    # name auto-derived as "Fertility" → auto-group created
)

# Sheep show fertility as grayscale: gray (sterile) → white (fertile) → black (super fertile)
Sheep.newSymbology(
    "fertility",
    {0: QColor("gray"), 50: QColor("white"), 100: QColor("black")},
    # name auto-derived as "Fertility" → adds to same auto-group
)

# Cows show fertility as: gray (sterile) → brown → very dark (super fertile)
Cows.newSymbology(
    "fertility",
    {0: QColor("gray"), 50: QColor("brown"), 100: QColor("darkred")},
    # name auto-derived as "Fertility" → adds to same auto-group
)

# ============================================================================
# Create agent instances to visualize cross-entity symbologies
# ============================================================================

# Create Sheep with varying fertility
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

# Apply an instance override to show hierarchy
# Cell at (1,1) has special symbology (not the type's default)
cell = Cells.getCell(1, 1)
cell.setValue("fertility", 0)
cell.setInstanceSymbology("Fertility", "fertility", {0: QColor("purple"), 1: QColor("cyan")})

# ============================================================================
# Add informational labels
# ============================================================================
myModel.newLabel("AUTOMATIC GROUPS Example", position=(50, 650),
                textStyle_specs="color: darkblue; font-weight: bold; font-size: 14px;")
myModel.newLabel("Look at the Fertility symbology in the menu:", position=(50, 670),
                textStyle_specs="color: gray; font-size: 10px;")
myModel.newLabel("Cells (brown-green) | Sheep (gray-white-black) | Cows (gray-brown-red)", position=(50, 685),
                textStyle_specs="color: gray; font-size: 10px;")

# ============================================================================
# Create legend to visualize symbologies
# ============================================================================
legend = myModel.newLegend()

# ============================================================================
# Print information
# ============================================================================
print("=" * 70)
print("AUTOMATIC SYMBOLOGY GROUPS - Cross-Entity Type Example")
print("=" * 70)
print("\nHow automatic groups work:")
print("  1. You define symbology 'Fertility' for Cells")
print("  2. You define symbology 'Fertility' for Sheep (same name!)")
print("  3. You define symbology 'Fertility' for Cows (same name!)")
print("  → Automatically creates group 'Fertility' spanning all 3 types")
print("\nWhat you see:")
print("  - Cells: Fertility as brown (0) → green (1)")
print("  - Sheep: Fertility as gray (0) → white (50) → black (100)")
print("  - Cows: Fertility as gray (0) → brown (50) → red (100)")
print("\nKey insight:")
print("  - ONE attribute (fertility) visualized across entity types")
print("  - Each type shows fertility in its own way")
print("  - BUT they're coordinated in one 'Fertility' group")
print("  - Users can activate/deactivate the whole group")
print("\nCompare: Automatic vs Manual groups")
print("  - AUTOMATIC: Same-named symbologies → auto-grouped")
print("  - MANUAL: Different-named symbologies → user-grouped (see ex_symbology_groups_manual.py)")
print("=" * 70)

myModel.launch()
sys.exit(monApp.exec())
