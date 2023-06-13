from mainClasses.SGSGE import *
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

monApp = QtWidgets.QApplication([])

myModel = SGModel(550, 550, windowTitle="Custom your grid")

# First thing first: define the size of the grid (x, y), the shape of cells, their size, and other parameters
aGrid = myModel.newGrid(10, 10, "square", size=50)
# Then set the value of the cells for a given parameter
# In this example the parameter is landUse, and the values given are 'grass', 'forest' and 'shrub'

# The method setCells() sets the value of all cells
aGrid.setCells("landUse", "grass")
# The method setForX() sets the value of cells which x coordinate match a given value. X=1 corresponds to the first columnn on the left side of the grid
aGrid.setCells_withColumn("landUse", "forest", 1)
aGrid.setCells_withColumn("landUse", "forest", 2)
# The method setRandomCells()sets the value of a number of randomly selected cells on the grid
aGrid.setRandomCells("landUse", "shrub", 10)

myModel.newPov("povLandUse", "landUse", {
               "grass": Qt.green, "shrub": Qt.yellow, "forest": Qt.darkGreen}, [aGrid])

# myModel.launch_withoutMqtt()
myModel.launch()
sys.exit(monApp.exec_())
