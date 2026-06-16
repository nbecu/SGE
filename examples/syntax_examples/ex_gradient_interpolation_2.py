"""
Gradient Interpolation - Multiple Methods (Phase 3, Feature 3)

Demonstrates different interpolation methods:
- linear: Straight line interpolation (uniform transition)
- log: Logarithmic (soft/smooth transition)
- exp: Exponential (fast transition at start)

Switch between methods using: Menu > Symbology > By Type > Cells
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Gradient Interpolation Methods Comparison")

# Create cells with score attribute (0-100)
# Horizontal line to show gradient transitions clearly
Cells = myModel.newCellsOnGrid(12, 1, "square", size=60)
Cells.setEntities("score", 50)

# Set score values from 0 to 100 across the grid
for i, cell in enumerate(Cells.entities):
    score = int((i / (len(Cells.entities) - 1)) * 100) if len(Cells.entities) > 1 else 50
    cell.setValue("score", score)

# Define gradient with 2 key points (0=blue, 100=red)
score_gradient = {
    0: SGAspect(
        background_color=QColor("blue"),
        text_content="{score}",
        text_color="white",
        text_size=11,
        text_weight="bold",
        text_alignment="center"
    ),
    100: SGAspect(
        background_color=QColor("red"),
        text_content="{score}",
        text_color="white",
        text_size=11,
        text_weight="bold",
        text_alignment="center"
    ),
}

# Create symbologies with different interpolation methods
interpolation_methods = ['linear', 'log', 'exp']

for method in interpolation_methods:
    Cells.newSymbology(
        "score",
        score_gradient.copy(),
        name=f"Score{method.capitalize()}",
        interpolation=method
    )

print("Compare interpolation methods using the menu:")
print("Menu > Symbology > By Type > Cells > Score[Linear/Log/Exp]")
print("")
print("Transitions:")
print("- Linear: Uniform blue→purple→red gradient")
print("- Log: Soft transition (more blue at start, gradual change)")
print("- Exp: Fast transition (quick to red, slow at end)")

# Launch
myModel.launch()
sys.exit(monApp.exec())
