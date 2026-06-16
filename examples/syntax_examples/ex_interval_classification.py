"""
Interval Classification Example (Phase 3, Feature 4)

Demonstrates:
- Automatic classification into quantile intervals
- Equal-count classification (each class has same number of entities)
- Manual threshold-based classification
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from mainClasses.SGClassifier import SGClassifier
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Interval Classification Example")

# Create cells with pollution attribute (0-100)
Cells = myModel.newCellsOnGrid(8, 8, "square", size=60)
Cells.setEntities("pollution", 50)

# Set pollution values randomly to demonstrate classification
import random
random.seed(42)
for cell in Cells.entities:
    pollution = random.randint(0, 100)
    cell.setValue("pollution", pollution)

# Method 1: Quantile Classification (equal count per class)
print("Classifying with quantile method...")
quantile_mapping = SGClassifier.classify_quantile(
    Cells.entities,
    attribute="pollution",
    num_classes=4
)

Cells.newSymbology(
    "pollution",
    quantile_mapping,
    name="PollutionQuantile"
)

# Method 2: Manual Classification (custom thresholds)
print("Creating manual classification...")
manual_mapping = SGClassifier.classify_manual(
    thresholds=[0, 33, 66, 100],
    colors=[QColor("green"), QColor("yellow"), QColor("red")]
)

# Method 3: Equidistant Classification (equal width intervals)
print("Classifying with equidistant method...")
equidistant_mapping = SGClassifier.classify_equidistant(
    Cells.entities,
    attribute="pollution",
    num_classes=4
)

# By default, quantile classification is active
# To switch between classifications, use the menu:
# Menu > Symbology > By Type > Cells > PollutionQuantile

# Launch
myModel.launch()
sys.exit(monApp.exec())
