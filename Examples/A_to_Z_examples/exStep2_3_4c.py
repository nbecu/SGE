import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(700,600, typeOfLayout="enhanced_grid", nb_columns=4, windowTitle="rearrange location of the game spaces using layoutOrder")

Cell = myModel.newCellsOnGrid(10, 10, "square", size=50)
Cell.setEntities("landUse", "grass")
Cell.setEntities_withColumn("landUse", "forest", 1)
Cell.setEntities_withColumn("landUse", "forest", 2)
Cell.setRandomEntities("landUse", "shrub", 10)

Cell.newPov("base","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})

#adds a legend to the grid
Legend=myModel.newLegend()

# You can also set a game space layoutOrder to a number greater than 1 above the previous one.
# In this example, the legend layoutOrder is 2 because it was created second
# And the grid  layoutOrder is 4 because it is set to 4 through the setLayoutOrder method (see below),
# So the layout (set with nb_columns=4) will automatically add a space on the left (no layoutorder 1)
# and a space inbetween the legend and the grid
Cell.setLayoutOrder(4) # This syntax is equivalent to Cell.grid.setLayoutOrder(3)


myModel.launch() 

sys.exit(monApp.exec_())
