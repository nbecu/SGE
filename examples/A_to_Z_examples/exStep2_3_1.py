import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(700,600, windowTitle="Adjust the location of the grid")

Cell = myModel.newCellsOnGrid(10, 10, "square", size=40)
Cell.grid.moveToCoords(200,100)
Cell.setEntities("landUse", "grass")
Cell.setEntities_withColumn("landUse", "forest", 1)
Cell.setEntities_withColumn("landUse", "forest", 2)
Cell.setRandomEntities("landUse", "shrub", 10)

Cell.newPov("base","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})

myModel.launch() 

sys.exit(monApp.exec_())
