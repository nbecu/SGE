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
Cell.grid.setLayoutOrder(2)  # Set grid as second in layout
Legend.setLayoutOrder(1)      # Set legend as first in layout

# How layoutOrder translates to columns:
# - layoutOrder 1 → Column 0 (leftmost)
# - layoutOrder 2 → Column 1 (rightmost, with 2 columns total)
# In case there would be a third gameSpace set at layoutOrder 3, it would be placed in Column 0, because the layoutOrder would be 3 % 2 = 1.

myModel.launch() 

sys.exit(monApp.exec_())
