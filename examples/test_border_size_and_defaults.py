"""
Demonstrate border_size and **aspect_defaults parameters in newSymbology()

This example shows the purpose and usage of these parameters.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mainClasses.SGSGE import *
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])
myModel = SGModel(windowTitle="Test: border_size and aspect_defaults")

Cells = myModel.newCellsOnGrid(5, 5, "square", size=80)
Cells.setEntities("status", 1)

# ============================================================================
# PATTERN 1: border_size parameter (convenience for common case)
# ============================================================================
print("\n1. PATTERN 1: border_size parameter")
print("   Use case: Add same border to all values")
print("   Example: newSymbology('status', {...}, border_size=2)")
print("   Result: All aspects get border_size=2, border_color=background_color")

Cells.newSymbology(
    "status",
    {
        1: QColor("green"),
        2: QColor("orange"),
        3: QColor("red"),
    },
    border_size=2,  # Applies border to all values
    name="StatusWithBorder"
)

# ============================================================================
# PATTERN 2: **aspect_defaults (flexibility for common defaults)
# ============================================================================
print("\n2. PATTERN 2: **aspect_defaults parameter")
print("   Use case: Apply common SGAspect properties to all values")
print("   Example: newSymbology('status', {...}, text_color='white', text_size=12)")
print("   Result: All aspects get text_color='white', text_size=12 by default")

Cells.newSymbology(
    "status",
    {
        1: SGAspect(background_color="blue"),
        2: SGAspect(background_color="purple"),
        3: SGAspect(background_color="cyan"),
    },
    text_color="white",      # Applied to ALL aspects
    text_size=12,            # Applied to ALL aspects
    text_weight="bold",      # Applied to ALL aspects
    border_color="black",    # Applied to ALL aspects
    border_size=1,           # Applied to ALL aspects
    name="StatusWithDefaults"
)

# ============================================================================
# WHY THESE PARAMETERS?
# ============================================================================
print("\n3. WHY THESE PARAMETERS EXIST:")
print("""
border_size:
  - Convenience for the MOST COMMON case: simple categorical colors with borders
  - Avoids repetition when all values need the same border width
  - Example: status categories (OK, WARNING, ERROR) all need border_size=2

**aspect_defaults:
  - Flexibility to apply common SGAspect properties to all values at once
  - Avoids repetition when values share many properties (text color, size, etc.)
  - Only applies to properties NOT already set in individual aspects
  - Example: all status values should be bold white text

Design Philosophy:
  - "Convention over Configuration" — most common case is easy
  - But still flexible for value-specific customization
  - Pattern 4 (full SGAspect) takes precedence for any property
""")

# ============================================================================
# IMPORTANT: Order of application (Priority)
# ============================================================================
print("\n4. APPLICATION ORDER (Priority - last value wins):")
print("""
1. Individual SGAspect in mapping (highest priority)
   Example: SGAspect(border_color="gold")

2. **aspect_defaults (medium priority)
   Example: border_color="black" in **aspect_defaults

3. border_size parameter (lowest priority for borders)
   Example: border_size=2

If you specify all three, #1 (individual aspect) takes precedence!
""")

# ============================================================================
# PRACTICAL EXAMPLE: Real use case
# ============================================================================
print("\n5. PRACTICAL EXAMPLE:")
print("""
myModel.newSymbology(
    "temperature",
    {
        0: QColor("blue"),      # Cold
        1: QColor("green"),     # Normal
        2: QColor("red"),       # Hot
    },
    border_size=2,              # All temperature values get 2px border
    text_color="white",         # All temperature values get white text
    text_size=10,               # All temperature values get 10px font
    name="Temperature"
)

Result:
  - 0 (blue): background=blue, border=blue (2px), text=white (10px)
  - 1 (green): background=green, border=green (2px), text=white (10px)
  - 2 (red): background=red, border=red (2px), text=white (10px)
""")

myModel.newLegend()
myModel.launch()
sys.exit(monApp.exec())
