"""
Aspect Views Example (Phase 3, Feature 6)

Demonstrates:
- Pre-configured views that activate multiple symbologies at once
- Theme-based visualizations
- Easy switching between different analytical perspectives
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from mainClasses.SGAspectSystem import SGAspectView
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Aspect Views Example")

# Create cells with multiple attributes
Cells = myModel.newCellsOnGrid(5, 5, "square", size=80)
Cells.setEntities("health", 50)
Cells.setEntities("fertility", 50)

# Add variability
import random
random.seed(42)
for cell in Cells.entities:
    cell.setValue("health", random.randint(0, 100))
    cell.setValue("fertility", random.randint(0, 100))

# Create multiple symbologies
# Health symbology: Green (healthy) → Red (sick)
health_aspects = {
    75: SGAspect(background_color=QColor("green"), text_content="H:{health}"),
    50: SGAspect(background_color=QColor("yellow"), text_content="H:{health}"),
    25: SGAspect(background_color=QColor("red"), text_content="H:{health}"),
}

# Fertility symbology: Brown (low) → Blue (high)
fertility_aspects = {
    75: SGAspect(background_color=QColor("blue"), text_content="F:{fertility}"),
    50: SGAspect(background_color=QColor("lightblue"), text_content="F:{fertility}"),
    25: SGAspect(background_color=QColor("brown"), text_content="F:{fertility}"),
}

Cells.newSymbology("health", health_aspects, name="HealthStatus")
Cells.newSymbology("fertility", fertility_aspects, name="FertilityStatus")

# Create Aspect Views (pre-configured visualization themes)
health_view = SGAspectView(
    name="HealthMonitor",
    symbology_names=["HealthStatus"],
    description="Shows only health status"
)

fertility_view = SGAspectView(
    name="FertilityMonitor",
    symbology_names=["FertilityStatus"],
    description="Shows only fertility status"
)

# You can manually activate views like this:
# health_view.activate(myModel)

print("Two aspect views are defined:")
print("- HealthMonitor: Shows health status")
print("- FertilityMonitor: Shows fertility status")
print("")
print("Use the menu to switch between symbologies")

myModel.launch()
sys.exit(monApp.exec())
