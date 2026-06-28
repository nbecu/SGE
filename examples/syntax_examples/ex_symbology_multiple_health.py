"""
Multiple Symbologies Example - Same Grid, Different Views

Demonstrates:
- Creating multiple different symbologies for the same attribute
- Same grid can be visualized in different ways
- Switch between views using menu (each symbology shows different aspects)
- Use shared_aspect to reduce repetition in symbology definitions
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Multiple Symbologies - Same Grid Example", width=900, height=700)

# ============================================================================
# Create ONE grid with health values (will be visualized 3 different ways)
# ============================================================================
Cells = myModel.newCellsOnGrid(5, 5, "square", size=60)
Cells.setEntities("health", 100)

# Set random health values to show symbology variation
import random
random.seed(42)
for cell in Cells.entities:
    cell.setValue("health", random.choice([100, 75, 50, 25]))

# ============================================================================
# SYMBOLOGY 1: Simple categorical view (green-yellow-orange-red)
# Shows health in classic stoplight colors
# ============================================================================
Cells.newSymbology(
    "health",
    {
        100: {"bg": "green"},
        75: {"bg": "yellow"},
        50: {"bg": "orange"},
        25: {"bg": "red"},
    },
    text_color="white",
    text_weight="bold",
    name="HealthSimple"
)

# ============================================================================
# SYMBOLOGY 2: Detailed view with borders (shows DRY benefit of shared_aspect)
# Same colors but with borders to emphasize values
# ============================================================================
Cells.newSymbology(
    "health",
    {
        100: {"bg": "green"},
        75: {"bg": "yellow"},
        50: {"bg": "orange"},
        25: {"bg": "red"},
    },
    # shared_aspect: border applied to ALL values
    border_size=2,
    border_color="black",
    text_color="white",
    text_weight="bold",
    name="HealthDetailed"
)

# ============================================================================
# SYMBOLOGY 3: Pastels view (softer colors, different theme)
# Alternative visualization for presentation or aesthetics
# ============================================================================
Cells.newSymbology(
    "health",
    {
        100: {"bg": "lightgreen"},
        75: {"bg": "lightyellow"},
        50: {"bg": "lightcoral"},
        25: {"bg": "salmon"},
    },
    border_size=1,
    border_color="gray",
    text_color="darkgray",
    name="HealthPastels"
)

# ============================================================================
# Display the first symbology by default
# ============================================================================
Cells.displaySymbology("HealthSimple")

# ============================================================================
# Add agents to show same concept works for other entity types
# ============================================================================
Sheep = myModel.newAgentType("Sheep", "triangleAgent1")
Sheep.setDefaultValues({"health": lambda: 100})

# Sheep can have their own health symbologies too
Sheep.newSymbology(
    "health",
    {
        100: QColor("darkgreen"),
        75: QColor("olive"),
        50: QColor("darkorange"),
        25: QColor("darkred"),
    },
    text_color="white",
    name="SheepHealth"
)

# Create some sheep with varying health
for i in range(1, 4):
    sheep = Sheep.newAgentAtCoords(Cells, i, 1)
    sheep.setValue("health", 100 - (i * 25))

# ============================================================================
# Add information labels
# ============================================================================
myModel.newLabel("SAME GRID - THREE DIFFERENT SYMBOLOGIES", position=(50, 650),
                textStyle_specs="color: darkblue; font-weight: bold; font-size: 13px;")
myModel.newLabel("Switch views in menu: HealthSimple | HealthDetailed | HealthPastels", position=(50, 670),
                textStyle_specs="color: gray; font-size: 10px;")

# ============================================================================
# Print explanation
# ============================================================================
print("=" * 70)
print("MULTIPLE SYMBOLOGIES - SAME GRID, DIFFERENT VIEWS")
print("=" * 70)
print("\nThis example shows 3 different symbologies for the SAME health attribute:")
print("\n1. HealthSimple: Clean stoplight colors (green-yellow-orange-red)")
print("   Best for: quick understanding of health status")
print("\n2. HealthDetailed: Colors WITH borders (emphasizes values)")
print("   Best for: detailed analysis, seeing every cell clearly")
print("   Demonstrates shared_aspect: border applied to ALL values once")
print("\n3. HealthPastels: Softer colors (alternative presentation)")
print("   Best for: presentations, aesthetics, different audience")
print("\nSwitch between views using the menu WITHOUT recreating data.")
print("Same data, different perspectives — that's the power of multiple symbologies!")
print("\nKey insight:")
print("  - shared_aspect reduces repetition (border defined once, applies to all)")
print("  - Multiple symbologies allow flexibility without code duplication")
print("=" * 70)

myModel.newLegend()
myModel.launch()
sys.exit(monApp.exec())
