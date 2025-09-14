import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(400, 300, windowTitle="Test zoom - Simple grid")

# Create a simple grid
cellDef = myModel.newCellsOnGrid(3, 3, "square", name="TestGrid", size=30, gap=0)
cellDef.setEntities("type", "normal")

# Create a legend
aLegend = myModel.newLegend()
aLegend.moveToCoords(200, 10)

# Create instructions
aTextBox = myModel.newTextBox(
    "Test zoom functionality:\n"
    "Move mouse over the grid and use mouse wheel to zoom in/out.\n"
    "Each grid can have independent zoom levels.",
    title="Zoom Test", sizeY=80
)
aTextBox.moveToCoords(200, 150)

myModel.launch()
sys.exit(monApp.exec_())
