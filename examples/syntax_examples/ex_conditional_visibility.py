"""
Conditional Visibility Example (Phase 3, Feature 5)

Demonstrates:
- Hiding cells based on attribute values
- Showing only high-value cells
- Dynamic visibility based on conditions
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Conditional Visibility Example")

# Create cells with wealth attribute (0-100)
Cells = myModel.newCellsOnGrid(6, 6, "square", size=70)
Cells.setEntities("wealth", 50)

# Set wealth values to create interesting pattern
import random
random.seed(42)
for cell in Cells.entities:
    wealth = random.randint(0, 100)
    cell.setValue("wealth", wealth)

# Define aspects with visibility conditions
aspect_rich = SGAspect(
    background_color=QColor("gold"),
    text_content="Rich: {wealth}",
    text_color="black",
    text_size=12,
    visible_if="{wealth} >= 70"  # Only visible if wealth >= 70
)

aspect_poor = SGAspect(
    background_color=QColor("gray"),
    text_content="Poor: {wealth}",
    text_color="white",
    text_size=12,
    visible_if="{wealth} < 30"  # Only visible if wealth < 30
)

aspect_normal = SGAspect(
    background_color=QColor("lightblue"),
    text_content="Normal: {wealth}",
    text_color="black",
    text_size=12,
    visible_if="{wealth} >= 30"  # Show all others
)

# Create symbology with visibility conditions
Cells.newSymbology(
    "wealth",
    {
        70: aspect_rich,
        30: aspect_poor,
        0: aspect_normal,
    }
)

# Launch
print("The grid shows cells with visibility conditions:")
print("- Gold cells: wealth >= 70 (visible)")
print("- Gray cells: wealth < 30 (visible)")
print("- Blue cells: 30-70 wealth (visible)")
print("- Other cells: hidden due to visibility conditions")
myModel.launch()
sys.exit(monApp.exec())
