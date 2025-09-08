#!/usr/bin/env python3
"""
Simple example of displayTooltip() usage
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(500, 500, windowTitle="Tooltips - Simple Example")

# Create a first  grid
LandCell = myModel.newCellsOnGrid(6, 6, "hexagonal", gap=0, size=40,name="Land")
LandCell.setEntities("landForm", "plain")
LandCell.setRandomEntities("landForm", "mountain", 4)
LandCell.newPov("base", "landForm", {"plain": Qt.green, "mountain": Qt.darkGray})

# Create a second  grid
SeaCell = myModel.newCellsOnGrid(5 ,3, "square", name="Sea",size=40)
SeaCell.setEntities("seascape", "pelagic")
SeaCell.setEntities_withColumn("seascape", "abyssal", 1)
SeaCell.setEntities_withColumn("seascape", "abyssal", 2)
SeaCell.setEntities_withColumn("seascape", "littoral", 5)
SeaCell.setRandomEntities("seascape", "seamount", 3,condition=lambda c: c.isValue("seascape", "pelagic"))
SeaCell.newPov("base", "seascape", {
    "pelagic": QColor.fromRgb(173, 216, 230),  # Qt.lightBlue
    "abyssal": QColor.fromRgb(0, 0, 139),      # Qt.darkBlue
    "littoral": QColor.fromRgb(238, 214, 171), # Approximation for "sandy" color 
    "seamount": QColor.fromRgb(139, 69, 19)    # Qt.brown
})

SeaCell.grid.moveToCoords(50, 300)

# Create some agents
Cows = myModel.newAgentSpecies("Cows", "rectAgent1", defaultSize=25, defaultColor=Qt.white, locationInEntity="bottomLeft")
Cows.setDefaultValues_randomChoice({
    "health": ["good", "fair", "poor"],
    "hunger": ["full", "hungry", "starving"],
    "age": ["young", "adult", "old"]
})
Cows.newAgentsAtRandom(5, LandCell, condition=lambda c: c.isValue("landForm", "plain"))

Fishes = myModel.newAgentSpecies("Fish", "ellipseAgent1", defaultSize=20, defaultColor=Qt.gray)
Fishes.setDefaultValues_randomChoice({
    "species": ["Salmon", "Tuna", "Cod", "Mackerel"],
    "size": ["small", "medium", "large"],
    "swimming_depth": ["surface", "mid", "deep"]
})
Fishes.newAgentsAtRandom(4, SeaCell, condition=lambda c: c.isNotValue("seascape", "littoral"))

aLegend = myModel.newLegend()
aLegend.moveToCoords(300, 25)


LandCell.displayTooltip('coords')  # Display coordinates (x, y)
Fishes.displayTooltip('id')  # Display numeric IDs

# Test custom tooltips with setTooltip()
LandCell.setTooltip("Land Type", "landForm")  # Display landForm attribute
LandCell.setTooltip("Position", lambda cell: f"(column:{cell.yCoord}, row:{cell.xCoord})")  # Custom format

SeaCell.setTooltip("Sea Type", "seascape")  # Display seascape attribute
SeaCell.setTooltip("Environment", lambda cell: f"{cell.value('seascape')} zone")  # Custom description

Cows.setTooltip("Health", "health")  # Display health attribute
Cows.setTooltip("Hunger", "hunger")  # Display hunger attribute
Cows.setTooltip("Status", lambda cow: f"Health: {cow.value('health')}, Hunger: {cow.value('hunger')}")  # Combined status

Fishes.setTooltip("Species", "species")  # Display species attribute
Fishes.setTooltip("Size", "size")  # Display size attribute
Fishes.setTooltip("Info", lambda fish: f"{fish.value('species')} ({fish.value('size')}) in {fish.cell.value('seascape')}")  # Combined info


myModel.launch()
sys.exit(monApp.exec_())
