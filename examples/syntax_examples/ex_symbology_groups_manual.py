"""
Symbology Groups - Manual Theme Example (Phase 3)

Demonstrates:
- Creating thematic visualization groups that combine multiple symbologies
- Unified SGSymbologyGroup supporting both automatic (cross-entity) and manual (thematic) modes
- Easy switching between different analytical perspectives

Two modes of SGSymbologyGroup:
1. AUTOMATIC: Same-named symbologies across different entity types
   - Created automatically when Cell.newSymbology("health") + Agent.newSymbology("health")

2. MANUAL: User-defined groups combining any symbologies by name
   - Created via model.newSymbologyGroup("ThemeName", ["Symbology1", "Symbology2"])
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
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

# Create SGSymbologyGroups (manual mode) - thematic visualization groups
# Each group can combine MULTIPLE symbologies with different names
# This allows creating visualization themes

# Group 1: Show only health
health_only_group = myModel.newSymbologyGroup(
    name="HealthOnly",
    symbology_names=["HealthStatus"]
)

# Group 2: Show only fertility
fertility_only_group = myModel.newSymbologyGroup(
    name="FertilityOnly",
    symbology_names=["FertilityStatus"]
)

# Group 3: Show BOTH health and fertility together (combined theme)
complete_group = myModel.newSymbologyGroup(
    name="CompleteAnalysis",
    symbology_names=["HealthStatus", "FertilityStatus"]
)

# You can manually activate groups like this:
# health_only_group.activate(myModel)
# complete_group.activate(myModel)

print("Three symbology groups are defined (manual mode):")
print("- HealthOnly: Shows only health status")
print("- FertilityOnly: Shows only fertility status")
print("- CompleteAnalysis: Shows BOTH health AND fertility together")
print("")
print("SGSymbologyGroup (manual mode) allows grouping multiple symbologies")
print("to create thematic visualizations.")

myModel.launch()
sys.exit(monApp.exec())
