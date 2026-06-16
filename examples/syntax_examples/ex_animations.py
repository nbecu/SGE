"""
Animations Example (Phase 3, Feature 7)

Demonstrates:
- Pulsing animations for important cells
- Flashing animations for alerts
- Real-time animation cycles
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from mainClasses.SGAnimation import SGAnimationManager
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Animations Example")

# Create cells
Cells = myModel.newCellsOnGrid(5, 5, "square", size=80)
Cells.setEntities("status", 0)

# Define status levels
# Status 2: High priority (pulsing red)
# Status 1: Normal (yellow)
# Status 0: Low (gray)

aspect_high = SGAspect(
    background_color=QColor("red"),
    text_content="HIGH",
    text_color="white",
    text_size=12,
    animation="pulse",
    animation_duration=1.0,
    animation_intensity=0.5
)

aspect_normal = SGAspect(
    background_color=QColor("yellow"),
    text_content="NORMAL",
    text_color="black",
    text_size=12
)

aspect_low = SGAspect(
    background_color=QColor("lightgray"),
    text_content="LOW",
    text_color="black",
    text_size=12
)

Cells.newSymbology(
    "status",
    {
        2: aspect_high,
        1: aspect_normal,
        0: aspect_low,
    }
)

# Set some cells to high priority (will pulse)
for i, cell in enumerate(Cells.entities):
    if i % 3 == 0:
        cell.setValue("status", 2)  # High - pulsing
    elif i % 3 == 1:
        cell.setValue("status", 1)  # Normal - yellow
    else:
        cell.setValue("status", 0)  # Low - gray

# Register animations for high-priority cells
manager = SGAnimationManager.global_manager()
for cell in Cells.entities:
    if cell.value("status") == 2:
        manager.add_animation(cell.privateID, "pulse", duration=1.0)

print("Red cells (high priority) are pulsing")
print("Yellow cells are normal")
print("Gray cells are low priority")
print("")
print("Watch the red cells pulse - this uses real-time animations")

myModel.launch()
sys.exit(monApp.exec())
