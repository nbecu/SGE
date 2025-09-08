#!/usr/bin/env python3
"""
Simple example of displayTooltip() usage
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(400, 300, windowTitle="Tooltips - Simple Example")

# Create hexagonal grid
Cell = myModel.newCellsOnGrid(6, 6, "hexagonal", gap=0, size=40, neighborhood='moore', boundaries='closed')

# Define some attributes
Cell.setEntities("landForm", "plain")
Cell.setRandomEntities("landForm", "mountain", 4)

# Create POV
Cell.newPov("base", "landForm", {"plain": Qt.green, "mountain": Qt.darkGray})


# Create some agents
Bees = myModel.newAgentSpecies("Bees", "circleAgent", defaultSize=10, defaultColor=QColor.fromRgb(165,42,42), locationInEntity="center")
Bees.newAgentsAtRandom(2, condition=lambda c: c.isValue("landForm", "plain"))

Flowers = myModel.newAgentSpecies("Flowers", "squareAgent", defaultSize=8, defaultColor=QColor.fromRgb(255, 192, 203), locationInEntity="bottomRight")
Flowers.newAgentsAtRandom(3, condition=lambda c: c.isValue("landForm", "plain"))


# Single phase to test tooltips
p1 = myModel.newModelPhase()

# Examples display tooltip that have been set by the modeler
Cell.setTooltip("Land Type", "landForm")
Cell.displayTooltip('Land Type') 


# Example with static text for Flowers
Flowers.setTooltip("Flower Info", "Beautiful flower")
Flowers.displayTooltip('Flower Info')

# Example with lambda function for dynamic tooltip
Bees.setTooltip("Position", lambda bee: f"Bee at ({bee.xCoord}, {bee.yCoord})")
Bees.displayTooltip('Position') 


myModel.launch()
sys.exit(monApp.exec_())
