import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(700,600, typeOfLayout="enhanced_grid", x=2, windowTitle="rearrange location of the game spaces using layoutOrder")

Cell = myModel.newCellsOnGrid(10, 10, "square", size=50)
Cell.setEntities("landUse", "grass")
Cell.setEntities_withColumn("landUse", "forest", 1)
Cell.setEntities_withColumn("landUse", "forest", 2)
Cell.setRandomEntities("landUse", "shrub", 10)

Cell.newPov("base","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})

#adds a legend to the grid
Legend=myModel.newLegend()

# Set layoutOrder for the grid using the setLayoutOrder method
# Cell.grid.setLayoutOrder(2)  # Set grid as second in layout
# Legend.setLayoutOrder(1)      # Set legend as first in layout

# It also works with the grid layoutOrder set to 3, because SGE will automatically readjust the gameSpaces layoutOrder starting from 1. 
# With the automatic readjustment, the grid layoutOrder will be 1, and the legend layoutOrder will be 2.
Cell.setLayoutOrder(3) # This syntax is equivalent to Cell.grid.setLayoutOrder(3)


myModel.launch() 

sys.exit(monApp.exec_())
