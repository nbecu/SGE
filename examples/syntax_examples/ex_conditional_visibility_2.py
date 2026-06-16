"""
Conditional Aspect Application with Fallback Example (Phase 3, Feature 5)

Demonstrates:
- Applying different aspects based on attribute values
- Using apply_if conditions to control aspect application
- Fallback to default symbology when no conditions match
- In this example, aspect_poor is omitted to show fallback behavior
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

Cells.setDefaultSymbology(
    background_color=QColor("lightgray"),
    border_size=0
)

# Set wealth values to create interesting pattern
import random
random.seed(42)
for cell in Cells.entities:
    wealth = random.randint(0, 100)
    cell.setValue("wealth", wealth)

# Define aspects with apply_if conditions
# Note: aspect_poor is intentionally omitted to test fallback behavior
aspect_rich = SGAspect(
    background_color=QColor("gold"),
    text_content="Rich: {wealth}",
    text_color="black",
    text_size=12,
    apply_if="{wealth} >= 70"
)

aspect_poor = SGAspect(
    background_color=QColor("gray"),
    text_content="Poor: {wealth}",
    text_color="white",
    text_size=12,
    apply_if="{wealth} < 30"
)

aspect_normal = SGAspect(
    background_color=QColor("lightblue"),
    text_content="Normal: {wealth}",
    text_color="black",
    text_size=12,
    apply_if="{wealth} >= 30"
)

# Create symbology with conditional aspects
Cells.newSymbology(
    "wealth",
    {
        70: aspect_rich,
        # 30: aspect_poor,
        0: aspect_normal,
    }
)

# Launch
print("The grid demonstrates conditional aspect application with fallback:")
print("- Gold cells: apply_if '{wealth} >= 70'")
print("- Blue cells: apply_if '{wealth} >= 30'")
print("- Unmatched cells (wealth < 30): display default symbology (lightgray)")
print("Note: aspect_poor is not in the symbology, so those cells fall back to default")
myModel.launch()
sys.exit(monApp.exec())
