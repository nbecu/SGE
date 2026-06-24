"""
Multiple Symbologies with shared_aspect Example

Demonstrates:
- Creating different visual representations for same attribute
- How **shared_aspect applies common properties to ALL values
- Multiple symbologies per attribute (different analytical views)
- Comparing: WITHOUT shared_aspect (repetitive) vs WITH shared_aspect (DRY)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from mainClasses.SGAspect import SGAspect
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Multiple Symbologies - shared_aspect Example", width=1000, height=600)

# Create grids for different approaches
Cells1 = myModel.newCellsOnGrid(3, 3, "square", size=50, name="Grid1")
Cells1.setEntities("health", 100)
Cells1.setEntities_randomChoicePerEntity("health", [100, 50, 25])

Cells2 = myModel.newCellsOnGrid(3, 3, "square", size=50, name="Grid2")
Cells2.setEntities("health", 100)
Cells2.setEntities_randomChoicePerEntity("health", [100, 50, 25])

Cells3 = myModel.newCellsOnGrid(3, 3, "square", size=50, name="Grid3")
Cells3.setEntities("health", 100)
Cells3.setEntities_randomChoicePerEntity("health", [100, 50, 25])

# ============================================================================
# APPROACH 1: WITHOUT shared_aspect (repetitive - each value defines everything)
# ============================================================================
# Problem: border_size and border_color repeated for EVERY value (DRY violation)
Cells1.newSymbology(
    "health",
    {
        100: {"bg": "green", "border": "darkgreen", "size": 2, "style": "solid"},
        50: {"bg": "orange", "border": "darkorange", "size": 2, "style": "solid"},
        25: {"bg": "red", "border": "darkred", "size": 2, "style": "solid"},
    },
    name="HealthRepetitive"
)

# ============================================================================
# APPROACH 2: WITH shared_aspect (clean and DRY)
# ============================================================================
# Solution: Common properties (border_size, border_color, border_style)
# are defined ONCE via **shared_aspect and apply to ALL values
# Each value only needs to define what's DIFFERENT (the background color)
Cells2.newSymbology(
    "health",
    {
        100: {"bg": "green"},        # Only bg color - border comes from shared_aspect
        50: {"bg": "orange"},        # Only bg color - border comes from shared_aspect
        25: {"bg": "red"},           # Only bg color - border comes from shared_aspect
    },
    # These properties apply to ALL 100, 50, 25 values:
    border_size=2,
    border_color="darkgreen",
    border_style="solid",
    name="HealthShared"
)

# ============================================================================
# APPROACH 3: Multiple symbologies with different shared_aspect per theme
# ============================================================================
# Create alternative symbology with DIFFERENT shared aspect (thicker dashed border)
Cells3.newSymbology(
    "health",
    {
        100: {"bg": "lightgreen"},
        50: {"bg": "lightyellow"},
        25: {"bg": "lightcoral"},
    },
    # Different shared_aspect for this alternative theme
    border_size=3,
    border_color="black",
    border_style="dashed",
    text_color="white",
    text_weight="bold",
    name="HealthAlternate"
)

# ============================================================================
# Create agents to show same concept for different entity type
# ============================================================================
Sheep = myModel.newAgentType("Sheep", "triangleAgent1")
Sheep.setDefaultValues({"health": lambda: 100})

# Sheep also use shared_aspect to avoid repetition
Sheep.newSymbology(
    "health",
    {
        100: SGAspect(background_color="lightgreen"),
        50: SGAspect(background_color="lightyellow"),
        25: SGAspect(background_color="lightcoral"),
    },
    border_size=2,
    border_color="darkblue",
    text_color="white",
    name="SheepHealth"
)

# Create an agent to visualize
sheep = Sheep.newAgentAtCoords(Cells1, 2, 2)
sheep.setValue("health", 100)

# ============================================================================
# Add information labels
# ============================================================================
myModel.newLabel("WITHOUT shared_aspect", position=(50, 520),
                textStyle_specs="color: darkred; font-weight: bold; font-size: 12px;")
myModel.newLabel("(Repetitive: border repeated 3x)", position=(50, 540),
                textStyle_specs="color: gray; font-size: 10px;")

myModel.newLabel("WITH shared_aspect", position=(350, 520),
                textStyle_specs="color: darkgreen; font-weight: bold; font-size: 12px;")
myModel.newLabel("(Clean: border defined once)", position=(350, 540),
                textStyle_specs="color: gray; font-size: 10px;")

myModel.newLabel("Multiple Symbologies", position=(650, 520),
                textStyle_specs="color: darkblue; font-weight: bold; font-size: 12px;")
myModel.newLabel("(Different theme with different shared_aspect)", position=(650, 540),
                textStyle_specs="color: gray; font-size: 10px;")

# ============================================================================
# Print explanation
# ============================================================================
print("=" * 70)
print("MULTIPLE SYMBOLOGIES WITH shared_aspect")
print("=" * 70)
print("\nComparing two approaches:")
print("\n❌ APPROACH 1 (WITHOUT shared_aspect):")
print("   border_size=2, border_color=darkgreen repeated for EACH value")
print("   Problem: DRY violation, code is repetitive")
print("\n✅ APPROACH 2 (WITH shared_aspect):")
print("   border_size=2, border_color=darkgreen defined ONCE")
print("   Applies to ALL values (100, 50, 25)")
print("   Benefit: Cleaner code, easier to maintain, DRY principle")
print("\n🎯 APPROACH 3 (Multiple symbologies with different themes):")
print("   Create alternative views with different shared_aspect")
print("   HealthShared: solid border (analysis view)")
print("   HealthAlternate: dashed border (presentation view)")
print("   Users can switch themes using menu")
print("\n" + "=" * 70)

myModel.newLegend()
myModel.launch()
sys.exit(monApp.exec())
