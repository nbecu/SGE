"""
Symbology Syntax with shared_aspect: Three syntax styles + shared properties

Demonstrates:
- How **shared_aspect works with different value syntax styles
- Dict syntax (simple, readable) + shared_aspect
- SGAspect shorthand (one-liner) + shared_aspect
- SGAspect verbose (full control) + shared_aspect
- Comparing: individual border per value vs shared_aspect border

Key insight: Regardless of syntax style, shared_aspect applies the same way!
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from mainClasses.SGAspect import SGAspect

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Symbology Syntax with shared_aspect", width=1200, height=600)

# Create three grids to show each syntax style
grid_1 = myModel.newCellsOnGrid(3, 3, "square", size=50, name="Grid1")
grid_1.setEntities("health", 100)
grid_1.setEntities_randomChoicePerEntity("health", [100, 50, 25])

grid_2 = myModel.newCellsOnGrid(3, 3, "square", size=50, name="Grid2")
grid_2.setEntities("health", 100)
grid_2.setEntities_randomChoicePerEntity("health", [100, 50, 25])

grid_3 = myModel.newCellsOnGrid(3, 3, "square", size=50, name="Grid3")
grid_3.setEntities("health", 100)
grid_3.setEntities_randomChoicePerEntity("health", [100, 50, 25])

# ============================================================================
# SYNTAX 1: Dict syntax + shared_aspect
# ============================================================================
# Most readable: define only what's different per value
# Border properties come from shared_aspect (common to all)
grid_1.newSymbology(
    "health",
    {
        100: {"bg": "green"},           # Only bg color
        50: {"bg": "orange"},           # Only bg color
        25: {"bg": "red"},              # Only bg color
    },
    # shared_aspect: applies to ALL values
    border_size=2,
    border_color="darkgreen",
    text_color="white",
    name="HealthDict"
)

# ============================================================================
# SYNTAX 2: SGAspect shorthand + shared_aspect
# ============================================================================
# Still concise with SGAspect shorthand, plus shared_aspect for common properties
grid_2.newSymbology(
    "health",
    {
        100: SGAspect(bg="green"),      # Only bg color
        50: SGAspect(bg="orange"),      # Only bg color
        25: SGAspect(bg="red"),         # Only bg color
    },
    # shared_aspect: applies to ALL values
    border_size=2,
    border_color="darkorange",
    text_color="white",
    text_size=11,
    name="HealthAspect"
)

# ============================================================================
# SYNTAX 3: SGAspect verbose + shared_aspect
# ============================================================================
# For complex styling where you need full control per value
# Plus shared_aspect for properties common to all values
aspect_100 = SGAspect()
aspect_100.background_color = "lightgreen"

aspect_50 = SGAspect()
aspect_50.background_color = "lightyellow"

aspect_25 = SGAspect()
aspect_25.background_color = "lightcoral"

grid_3.newSymbology(
    "health",
    {
        100: aspect_100,
        50: aspect_50,
        25: aspect_25,
    },
    # shared_aspect: applies to ALL values
    border_size=2,
    border_color="darkred",
    text_color="white",
    text_weight="bold",
    name="HealthVerbose"
)

# ============================================================================
# Add informational labels
# ============================================================================
myModel.newLabel("Dict Syntax", position=(50, 520),
                textStyle_specs="color: darkblue; font-weight: bold; font-size: 12px;")
myModel.newLabel("+ shared_aspect", position=(50, 540),
                textStyle_specs="color: darkgreen; font-size: 10px;")

myModel.newLabel("SGAspect Shorthand", position=(370, 520),
                textStyle_specs="color: darkblue; font-weight: bold; font-size: 12px;")
myModel.newLabel("+ shared_aspect", position=(370, 540),
                textStyle_specs="color: darkgreen; font-size: 10px;")

myModel.newLabel("SGAspect Verbose", position=(700, 520),
                textStyle_specs="color: darkblue; font-weight: bold; font-size: 12px;")
myModel.newLabel("+ shared_aspect", position=(700, 540),
                textStyle_specs="color: darkgreen; font-size: 10px;")

# ============================================================================
# Print explanation
# ============================================================================
print("=" * 80)
print("SYMBOLOGY SYNTAX with shared_aspect")
print("=" * 80)
print("\nKey insight: All three syntax styles work the SAME with shared_aspect!")
print("\nSYNTAX 1 - Dict: Clearest for simple cases")
print("  Cells.newSymbology('health', {100: {'bg': 'green'}, ...},")
print("                     border_size=2, border_color='darkgreen')")
print("  Benefit: Readable, easy to understand")
print("\nSYNTAX 2 - SGAspect Shorthand: Concise and flexible")
print("  Cells.newSymbology('health', {100: SGAspect(bg='green'), ...},")
print("                     border_size=2, border_color='darkorange')")
print("  Benefit: Still short, but more flexible")
print("\nSYNTAX 3 - SGAspect Verbose: Maximum control")
print("  aspect_100 = SGAspect(); aspect_100.background_color = 'green'")
print("  Cells.newSymbology('health', {100: aspect_100, ...},")
print("                     border_size=2, border_color='darkred')")
print("  Benefit: Full control for complex styling")
print("\nCOMMON BENEFIT (all syntaxes):")
print("  ✅ shared_aspect applies border_size, border_color to ALL values")
print("  ✅ Reduces repetition regardless of syntax style chosen")
print("  ✅ Same properties apply whether you use dict, shorthand, or verbose")
print("\nWhen to use each syntax:")
print("  - Dict: Quick prototypes, simple styling")
print("  - Shorthand: Most cases, balance of clarity and flexibility")
print("  - Verbose: Complex styling requiring per-value customization")
print("=" * 80)

myModel.newLegend()
myModel.launch()
sys.exit(monApp.exec())
