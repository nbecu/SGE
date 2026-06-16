"""
Gradient Interpolation Example (Phase 3, Feature 3)

Demonstrates:
- Linear gradient from cold (blue) to hot (red) colors
- Automatic color interpolation between defined points
- Gradient applied to temperature attribute
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Gradient Interpolation Example")

# Create cells with temperature attribute (0-100)
Cells = myModel.newCellsOnGrid(6, 6, "square", size=70)
Cells.setEntities("temperature", 50)

# Set temperature gradient across the grid
for cell in Cells.entities:
    # Cold on left (x=1), hot on right (x=6)
    temperature = int((cell.xCoord - 1) / 5 * 100)
    cell.setValue("temperature", temperature)

# Define gradient with 3 key points
# Temperature 0°C = Blue, 50°C = Green, 100°C = Red
temperature_gradient = {
    0: SGAspect(
        background_color=QColor("blue"),
        text_content="{temperature}°C",
        text_color="white",
        text_size=12,
        text_weight="bold"
    ),
    50: SGAspect(
        background_color=QColor("green"),
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

# Create symbology with linear gradient interpolation
Cells.newSymbology(
    "temperature",
    temperature_gradient,
    name="TemperatureGradient",
    interpolation="linear"
)

# Launch
myModel.launch()
sys.exit(monApp.exec())
