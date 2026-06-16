"""
Gradient Interpolation - Multiple Color Stops (Phase 3, Feature 3)

Demonstrates:
- Linear gradient with multiple color stops (5 points)
- You can define 2+ points at any values in the range
- Automatic color interpolation between defined points
- Gradient applied to temperature attribute
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Gradient Interpolation - Multiple Color Stops")

# Create cells with temperature attribute (0-100)
Cells = myModel.newCellsOnGrid(6, 6, "square", size=70)
Cells.setEntities("temperature", 50)

# Set temperature gradient across the grid
for cell in Cells.entities:
    # Cold on left (x=1), hot on right (x=6)
    temperature = int((cell.xCoord - 1) / 5 * 100)
    cell.setValue("temperature", temperature)

# Define gradient with 5 key points
# Temperature: 0°C = Dark Blue, 25°C = Light Blue, 50°C = Green, 75°C = Orange, 100°C = Red
temperature_gradient = {
    0: SGAspect(
        background_color=QColor("darkblue"),
        text_content="{temperature}°C",
        text_color="white",
        text_size=12,
        text_weight="bold"
    ),
    25: SGAspect(
        background_color=QColor("lightblue"),
        text_content="{temperature}°C",
        text_color="white",
        text_size=12,
        text_weight="bold"
    ),
    50: SGAspect(
        background_color=QColor("lime"),
        text_content="{temperature}°C",
        text_color="white",
        text_size=12,
        text_weight="bold"
    ),
    75: SGAspect(
        background_color=QColor("orange"),
        text_content="{temperature}°C",
        text_color="white",
        text_size=12,
        text_weight="bold"
    ),
    100: SGAspect(
        background_color=QColor("red"),
        text_content="{temperature}°C",
        text_color="white",
        text_size=12,
        text_weight="bold"
    ),
}

# Create gradient symbology (linear interpolation is default)
Cells.newSymbologyGradient(
    "temperature",
    temperature_gradient,
    name="TemperatureGradient"
)

myModel.newLegend()

# Launch
myModel.launch()
sys.exit(monApp.exec())
