import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(850, 600, windowTitle="zoomMode - magnifier or resize",nb_columns=2)
# adminControlPanel = myModel.displayAdminControlPanel() 

# Create a second grid with magnifier mode
SeaCell = myModel.newCellsOnGrid(8 ,6, "square", name="Sea",size=40,gap=4)
SeaCell.grid.setBackgroundColor(Qt.orange)
SeaCell.grid.setBorderColor(Qt.pink)
SeaCell.grid.setBorderSize(10)
SeaCell.grid.setBorderStyle('solid')
# SeaCell.grid.setBorderRadius(20)
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


# Create a first  grid
LandCell = myModel.newCellsOnGrid(7, 6, "hexagonal", gap=5, size=40,name="Land", zoomMode="resize")
LandCell.grid.setBorderColor(Qt.red)
LandCell.grid.setBorderSize(6)
LandCell.grid.setBorderStyle('solid')
LandCell.grid.setBorderRadius(20)
LandCell.setEntities("landForm", "plain")
LandCell.setRandomEntities("landForm", "mountain", 4)
LandCell.newPov("base", "landForm", {"plain": Qt.green, "mountain": Qt.darkGray})


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
    "type": ["Salmon", "Tuna", "Cod", "Mackerel"],
    "size": ["small", "medium", "large"],
    "swimming_depth": ["surface", "mid", "deep"]
})
Fishes.newAgentsAtRandom(7, SeaCell)


# aLegend = myModel.newLegend()

# TextBox for Magnifier mode (Sea grid)
magnifierTextBox = myModel.newTextBox(
    "Mode Magnifier (Sea grid) :\n"
    "- La taille de la grid reste fixe\n"
    "- Le zoom agrandit le contenu à l'intérieur\n"
    "- Molette de la souris : zoom centré sur la position de la souris\n"
    "- Shift + Clic gauche + glisser : pan (déplacer la vue)\n"
    "- Permet d'explorer une grande grid dans un espace limité",
    title="Mode Magnifier", height=140,width=300
)
magnifierTextBox.moveToCoords(20, 350)

# TextBox for Resize mode (Land grid)
resizeTextBox = myModel.newTextBox(
    "Mode Resize (Land grid) :\n"
    "- La taille de la grid change avec le zoom\n"
    "- Le zoom agrandit/réduit toute la grid\n"
    "- Molette de la souris : zoom centré sur la position de la souris\n"
    "- La grid occupe plus ou moins d'espace selon le zoom\n"
    "- Mode par défaut, adapté aux petites grids",
    title="Mode Resize", height=140,width=300
)
resizeTextBox.moveToCoords(400, 400)

myModel.launch()
sys.exit(monApp.exec_())
