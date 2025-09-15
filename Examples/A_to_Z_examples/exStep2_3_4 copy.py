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
Cell.grid.setLayoutOrder(3)  # Set grid as second in layout
# Legend.setLayoutOrder(1)      # Set legend as first in layout

print(f"Grid layoutOrder set to: {Cell.grid.layoutOrder}")
print(f"Legend layoutOrder set to: {Legend.layoutOrder}")

myModel.launch() 

sys.exit(monApp.exec_())
