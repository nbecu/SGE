"""
Comprehensive Animations Example (Phase 3, Feature 7)

Demonstrates all three animation types:
- Pulse: Smooth opacity fade in/out
- Flash: Quick on/off toggle
- Rotate: Continuous spinning rotation

Each animation type is shown in a separate row.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Complete Animations Example")

# Create a 3x5 grid for demonstrations
Cells = myModel.newCellsOnGrid(5, 3, "square", size=80)
Cells.setEntities("animation_type", "pulse")

# Row 1: Pulse animations (opacity fade)
pulse_aspect = SGAspect(
    background_color=QColor("red"),
    text_content="PULSE",
    text_color="white",
    text_size=11,
    animation="pulse",
    animation_duration=1.5,
    legend_label="Pulse (fade)"
)

# Row 2: Flash animations (on/off toggle)
flash_aspect = SGAspect(
    background_color=QColor("orange"),
    text_content="FLASH",
    text_color="white",
    text_size=11,
    animation="flash",
    animation_duration=0.8,
    legend_label="Flash (blink)"
)

# Row 3: Rotate animations (spinning)
rotate_aspect = SGAspect(
    background_color=QColor("blue"),
    text_content="ROTATE",
    text_color="white",
    text_size=11,
    animation="rotate",
    animation_duration=2.0,
    legend_label="Rotate (spin)"
)

# Create symbology mapping animation type to aspect
Cells.newSymbology(
    "animation_type",
    {
        "pulse": pulse_aspect,
        "flash": flash_aspect,
        "rotate": rotate_aspect,
    }
)

# Set each row to a different animation type
cell_list = list(Cells.entities)
# Row 1 (5 cells): pulse
for i in range(0, 5):
    cell_list[i].setValue("animation_type", "pulse")

# Row 2 (5 cells): flash
for i in range(5, 10):
    cell_list[i].setValue("animation_type", "flash")

# Row 3 (5 cells): rotate
for i in range(10, 15):
    cell_list[i].setValue("animation_type", "rotate")

# Add legend to show animation types
myModel.newLegend()

print("Animation Types Demo:")
print("- Row 1 (Red):    PULSE - Smooth opacity fade in/out")
print("- Row 2 (Orange): FLASH - Quick on/off blink toggle")
print("- Row 3 (Blue):   ROTATE - Continuous spinning rotation")
print("")
print("Animations are auto-registered when entities are rendered.")

myModel.launch()
sys.exit(monApp.exec())
