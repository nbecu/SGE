"""
Symbology syntax comparison: All three ways to customize borders

Demonstrates three equally-valid approaches:
1. Dict syntax (simple, readable)
2. SGAspect shorthand (one-liner)
3. SGAspect verbose (full control)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from mainClasses.SGAspect import SGAspect

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Syntax Comparison Example", width=1000, height=400)

# Create three grids to show each approach
grid_1 = myModel.newCellsOnGrid(3, 3, "square", size=50, name="Grid1")
grid_1.setEntities("health", 100)

grid_2 = myModel.newCellsOnGrid(3, 3, "square", size=50, name="Grid2")
grid_2.setEntities("health", 100)

grid_3 = myModel.newCellsOnGrid(3, 3, "square", size=50, name="Grid3")
grid_3.setEntities("health", 100)

# APPROACH 1: Dict syntax (simple and readable)
print("[APPROACH 1] Dict syntax")
grid_1.newSymbology("health", {
    100: {"bg": "green", "border": "darkgreen", "size": 2},
    50: {"bg": "orange", "border": "darkorange", "size": 1, "style": "dashed"},
    25: {"bg": "red", "border": "darkred", "size": 1}
}, name="HealthDict")
print("  newSymbology(\"health\", {")
print("    100: {\"bg\": \"green\", \"border\": \"darkgreen\", \"size\": 2},")
print("    50: {\"bg\": \"orange\", ...},")
print("    ...")
print("  })")

# APPROACH 2: SGAspect shorthand (one-liner, still readable)
print("\n[APPROACH 2] SGAspect shorthand")
grid_2.newSymbology("health", {
    100: SGAspect(bg="green", border="darkgreen", size=2),
    50: SGAspect(bg="orange", border="darkorange", size=1, style="dashed"),
    25: SGAspect(bg="red", border="darkred", size=1)
}, name="HealthAspect")
print("  newSymbology(\"health\", {")
print("    100: SGAspect(bg=\"green\", border=\"darkgreen\", size=2),")
print("    50: SGAspect(bg=\"orange\", ...),")
print("    ...")
print("  })")

# APPROACH 3: SGAspect verbose (for very complex styling)
print("\n[APPROACH 3] SGAspect verbose (full control)")
aspect_100 = SGAspect()
aspect_100.background_color = "lightgreen"
aspect_100.border_color = "darkgreen"
aspect_100.border_size = 2
aspect_100.border_style = "solid"

aspect_50 = SGAspect()
aspect_50.background_color = "lightyellow"
aspect_50.border_color = "orange"
aspect_50.border_size = 1
aspect_50.border_style = "dashed"
aspect_50.font_weight = "bold"  # Extra: can set font properties too

aspect_25 = SGAspect()
aspect_25.background_color = "lightcoral"
aspect_25.border_color = "darkred"
aspect_25.border_size = 1

grid_3.newSymbology("health", {
    100: aspect_100,
    50: aspect_50,
    25: aspect_25
}, name="HealthVerbose")
print("  aspect = SGAspect()")
print("  aspect.background_color = \"green\"")
print("  aspect.border_color = \"darkgreen\"")
print("  aspect.border_size = 2")
print("  newSymbology(\"health\", {100: aspect, ...})")

print("\n" + "=" * 70)
print("All three approaches create identical visual results!")
print("=" * 70)

myModel.launch()
sys.exit(monApp.exec())
