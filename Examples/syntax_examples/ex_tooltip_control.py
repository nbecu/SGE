#!/usr/bin/env python3
"""
Example of tooltip control with displayTooltip() method
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(500, 350, windowTitle="Tooltip Control")

# Create simple square grid
Cell = myModel.newCellsOnGrid(5, 5, "square", gap=0, size=50, neighborhood='moore', boundaries='closed')

# Define some attributes for cells
Cell.setEntities("landForm", "plain")
Cell.setRandomEntities("landForm", "mountain", 3)

# Create POV for visualization
Cell.newPov("base", "landForm", {"plain": Qt.green, "mountain": Qt.darkGray})

# Create some agents
Bees = myModel.newAgentSpecies("Bees", "circleAgent", defaultSize=20, defaultColor=QColor.fromRgb(165,42,42), locationInEntity="center")
Bees.newAgentsAtRandom(2, condition=lambda c: c.isValue("landForm", "plain"))

# Phases to test different tooltip types
p2 = myModel.newModelPhase()
p2.addAction(lambda: Cell.displayTooltip('coords'))  # Display coordinates
p2.addAction(lambda: print("Tooltip: Coordinates"))

p3 = myModel.newModelPhase()
p3.addAction(lambda: Cell.displayTooltip('id'))  # Display IDs
p3.addAction(lambda: print("Tooltip: IDs"))

p4 = myModel.newModelPhase()
p4.addAction(lambda: Cell.displayTooltip('none'))  # Explicitly disable
p4.addAction(lambda: print("Tooltip: Explicitly disabled"))

p5 = myModel.newModelPhase()
p5.addAction(lambda: Cell.displayTooltip())  # Return to default
p5.addAction(lambda: print("Tooltip: Back to default"))

myModel.launch()
sys.exit(monApp.exec_())
