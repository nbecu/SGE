"""
Dynamic Text Content Example (Phase 3, Feature 2)

Demonstrates:
- Static text display on cells
- Dynamic text with attribute substitution {health}
- Mixed expressions: "Health: {health}/100"
- Text formatting (color, size, alignment)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Dynamic Text Content Example")

# Create cells with health attribute
Cells = myModel.newCellsOnGrid(4, 4, "square", size=80)
Cells.setEntities("health", 50)

# Add variability to show text changes
Cells.setEntities_randomChoicePerEntity("health", [25, 50, 75])

# Define health symbology with dynamic text
health_aspect_healthy = SGAspect(
    background_color="green",
    text_content="{health}",
    text_color="white",
    text_size=10,
    # text_weight="bold",
    text_alignment="bottom"
)

health_aspect_normal = SGAspect(
    background_color="yellow",
    text_content="{health}",
    text_color="black",
    text_size=16,
    text_weight="bold",
    text_alignment="center"
)

health_aspect_low = SGAspect(
    background_color="red",
    text_content="{health}",
    text_color="white",
    text_size=16,
    text_weight="bold",
    text_alignment="center"
)

Cells.newSymbology(
    "health",
    {
        75: health_aspect_healthy,
        50: health_aspect_normal,
        25: health_aspect_low,
    }
)

# Create agent type to show text on agents
Sheep = myModel.newAgentType("Sheep", "triangleAgent1")
Sheep.setDefaultValues({"energy": lambda: 80})

# Add agents with dynamic text
sheep1 = Sheep.newAgentAtCoords(1, 1)
sheep1.setValue("energy", 100)

sheep2 = Sheep.newAgentAtCoords(2, 2)
sheep2.setValue("energy", 50)

sheep3 = Sheep.newAgentAtCoords(3, 3)
sheep3.setValue("energy", 30)

# Define energy symbology for agents with dynamic text
energy_aspect_high = SGAspect(
    background_color="lightgreen",
    text_content="E:{energy}",
    text_color="black",
    text_size=12,
    text_alignment="center"
)

energy_aspect_low = SGAspect(
    background_color="orange",
    text_content="E:{energy}",
    text_color="black",
    text_size=12,
    text_alignment="center"
)

Sheep.newSymbology(
    "energy",
    {
        75: energy_aspect_high,
        50: energy_aspect_low,
    }
)

# Launch and display
myModel.launch()
sys.exit(monApp.exec())
