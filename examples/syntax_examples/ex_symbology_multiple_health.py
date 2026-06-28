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

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Multiple Symbologies - Same Grid Example",nb_columns=2)

myModel.newLabel("Switch symbology in menu: HealthSimple | HealthDetailed | HealthPastels", position=(20, 20),
                textStyle_specs="color: gray; font-size: 10px;")
# ============================================================================
# Create ONE grid with health values (will be visualized 3 different ways)
# ============================================================================
Cells = myModel.newCellsOnGrid(5, 5, "square", size=60)
Cells.setEntities("health", 100)
Cells.setLayoutOrder(3)

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
# NOTE: First symbology (HealthSimple) is auto-displayed automatically
# No need to call displaySymbology() - it happens in newSymbology()!
# ============================================================================

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


leg=myModel.newLegend()
leg.setLayoutOrder(4)

myModel.launch()
sys.exit(monApp.exec())
