"""
Test SGControlPanel with all 4 symbology types to verify no regressions.

This tests:
- newSymbology() for nominal/discrete
- newSymbologyGradient() for gradients
- newSymbologyClassified() for classifications
- newSymbologyRule() for rule-based

With ControlPanel and Legend to ensure integration works.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mainClasses.SGSGE import *
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Test: Symbologies + ControlPanel + Legend")

# Create grid
Cells = myModel.newCellsOnGrid(5, 5, "square", size=80)
Cells.setEntities("health", 50)
Cells.setEntities("temperature", 20)
Cells.setEntities("status", 1)

# Random values
import random
random.seed(42)
for cell in Cells.entities:
    cell.setValue("health", random.randint(0, 100))
    cell.setValue("temperature", random.randint(10, 40))
    cell.setValue("status", random.choice([1, 2, 3]))

# Test 1: Nominal symbology
Cells.newSymbology(
    "status",
    {
        1: SGAspect(background_color=QColor("green"), text_content="OK", legend_label="Status OK"),
        2: SGAspect(background_color=QColor("orange"), text_content="WARN", legend_label="Status Warning"),
        3: SGAspect(background_color=QColor("red"), text_content="ERROR", legend_label="Status Error"),
    },
    name="StatusSymbology"
)

# Test 2: Gradient symbology
Cells.newSymbologyGradient(
    "health",
    {0: SGAspect(background_color="red"), 100: SGAspect(background_color="green")},
    interpolation="linear",
    name="HealthGradient"
)

# Test 3: Classification symbology
Cells.newSymbologyClassified(
    "temperature",
    {10: SGAspect(background_color="blue"), 25: SGAspect(background_color="orange"), 40: SGAspect(background_color="red")},
    name="TempClassified"
)

# Test 4: Rule-based symbology
def rule(e):
    h = e.value("health")
    if h > 75:
        return SGAspect(background_color="darkgreen", legend_label="Excellent")
    elif h > 50:
        return SGAspect(background_color="lightgreen", legend_label="Good")
    else:
        return SGAspect(background_color="orange", legend_label="Poor")

Cells.newSymbologyRule("health_rule", rule, name="HealthRule")

# Add legend
myModel.newLegend()

# Add control panel
myModel.displayAdminControlPanel()

print("OK - All symbologies created successfully")
print("OK - Legend created")
print("OK - ControlPanel displayed")
print("Ready for launch - verify menu system and legend work")

myModel.launch()
sys.exit(monApp.exec())
