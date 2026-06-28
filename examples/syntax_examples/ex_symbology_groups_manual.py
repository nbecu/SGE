"""
Symbology Groups - Manual Theme Example (Phase 3)

Demonstrates:
- Creating thematic visualization groups that combine multiple symbologies
- Manual mode: User-defined groups combining any symbologies by name
- Easy switching between different analytical perspectives
- How to activate groups to change visualization theme

SGSymbologyGroup (manual mode):
- Allows grouping multiple DIFFERENT symbologies into a single "theme"
- Useful for switching between analytical perspectives
- Example: "Economic View" groups [Wealth, Trade, Production] symbologies together
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Symbology Groups - Manual Themes", width=1000, height=700)

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

# ============================================================================
# Create multiple symbologies for different analytical perspectives
# ============================================================================

# Health symbology: Green (healthy) → Red (sick)
Cells.newSymbology("health",
                {   75: SGAspect(background_color=QColor("green"), text_content="H:{health}"),
                    50: SGAspect(background_color=QColor("yellow"), text_content="H:{health}"),
                    25: SGAspect(background_color=QColor("red"), text_content="H:{health}"),
                },
                name="HealthStatus")

# Fertility symbology: Brown (low) → Blue (high)
Cells.newSymbology("fertility",
                {
                    75: SGAspect(background_color=QColor("blue"), text_content="F:{fertility}"),
                    50: SGAspect(background_color=QColor("lightblue"), text_content="F:{fertility}"),
                    25: SGAspect(background_color=QColor("brown"), text_content="F:{fertility}"),
                },
                name="FertilityStatus")

# ============================================================================
# Create SGSymbologyGroups (manual mode) - thematic visualization themes
# Each group combines MULTIPLE symbologies with different names
# This allows switching visualization perspective with a single activation
# ============================================================================

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
# This is the power of groups: activate multiple symbologies at once
complete_group = myModel.newSymbologyGroup(
    name="CompleteAnalysis",
    symbology_names=["HealthStatus", "FertilityStatus"]
)

# ============================================================================
# ACTIVATE the first group by default to show the visualization
# ============================================================================
# This is the KEY DIFFERENCE from before - groups are now ACTIVE!
print("Activating HealthOnly group...")
health_only_group.activate(myModel)

# Add information labels
myModel.newLabel("Use menu to switch: HealthOnly | FertilityOnly | CompleteAnalysis", position=(20, 20),
                textStyle_specs="color: gray; font-size: 10px;")

# ============================================================================
# Add a way to switch groups (using control panel menu)
# ============================================================================
myModel.newLegend()

print("\nSYMBOLOGY GROUPS (Manual Themes) - ACTIVE!")
print("=" * 60)
print("\nCurrently active: HealthOnly (shows only health status)")
print("\nYou can switch themes using the menu bar:")
print("  - HealthOnly: Analyze cell health")
print("  - FertilityOnly: Analyze cell fertility")
print("  - CompleteAnalysis: See both attributes together")
print("\nWhat makes groups powerful:")
print("  - Define a 'theme' ONCE (HealthOnly, CompleteAnalysis, etc.)")
print("  - Activate it ONCE with group.activate(model)")
print("  - All symbologies in the group activate together")
print("  - Users can switch themes instantly from the menu")
print("\nCompare with manual approach:")
print("  - WITHOUT groups: activate each symbology one-by-one")
print("  - WITH groups: activate entire 'theme' in one call")
print("=" * 60)

myModel.launch()
sys.exit(monApp.exec())
