import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(700,600, windowTitle="Step 2 (1) : Create your grid", typeOfLayout='vertical')

# First thing first: define the size of the grid (x, y), the shape of cells, their size, and other parameters
Cell = myModel.newGrid(10, 10, "square", size=50)

# Then set the value of the cells for a given parameter
# In this example the parameter is landUse, and the values given are 'grass', 'forest' and 'shrub'
# The method setEntities() sets the value of all cells
Cell.setEntities("landUse", "grass")
# The method setForX() sets the value of cells which x coordinate match a given value. X=1 corresponds to the first columnn on the left side of the grid
Cell.setEntities_withColumn("landUse", "forest", 1)
Cell.setEntities_withColumn("landUse", "forest", 2)
# The method setRandomEntities()sets the value of a number of randomly selected cells on the grid
Cell.setRandomEntities("landUse", "shrub", 10)

#Pov (point of view), allow to specify different ways to view the state of the cells
#A pov allow to define the color displayed for a certain value of a given attribute of the cell
#In this example there are two pov:
#The first can see the difference between grass and schrub, the second cannot
Cell.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

myModel.launch() 

sys.exit(monApp.exec_())
