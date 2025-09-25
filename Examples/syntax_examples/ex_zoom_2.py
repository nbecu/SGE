import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(650, 600, windowTitle="Test zoom - two different grids")


# Create a second  grid
SeaCell = myModel.newCellsOnGrid(5 ,6, "square", name="Sea",size=40,gap=5)
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
SeaCell.grid.moveToCoords(20, 50)


# Create a first  grid
LandCell = myModel.newCellsOnGrid(5, 4, "hexagonal", gap=5, size=40,name="Land")
LandCell.setEntities("landForm", "plain")
LandCell.setRandomEntities("landForm", "mountain", 4)
LandCell.newPov("base", "landForm", {"plain": Qt.green, "mountain": Qt.darkGray})

LandCell.grid.moveToCoords(20, 410)

# Create some agents
Cows = myModel.newAgentType("Cows", "rectAgent1", defaultSize=25, defaultColor=Qt.white, locationInEntity="bottomLeft")
Cows.setDefaultValues_randomChoice({
    "health": ["good", "fair", "poor"],
    "hunger": ["full", "hungry", "starving"],
    "age": ["young", "adult", "old"]
})
Cows.newAgentsAtRandom(8, LandCell)


Fishes = myModel.newAgentType("Fish", "triangleAgent1", defaultSize=10, defaultColor=Qt.gray, locationInEntity="center")
Fishes.setDefaultValues_randomChoice({
    "species": ["Salmon", "Tuna", "Cod", "Mackerel"],
    "size": ["small", "medium", "large"],
    "swimming_depth": ["surface", "mid", "deep"]
})
Fishes.newAgentsAtRandom(7, SeaCell)


aLegend = myModel.newLegend()
aLegend.moveToCoords(300, 25)

aTextBox = myModel.newTextBox(
    "Test zoom on the different grids.\n"
    "Move the mouse over the grids and use the mouse wheel to zoom in/out.",
    title="Zoom Instructions", sizeY=100
)
aTextBox.moveToCoords(350, 250)

myModel.launch()
sys.exit(monApp.exec_())
