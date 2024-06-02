import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(960,700, windowTitle="A BIG board with hexagonal cells")

# You can change the specifications of the grid cells 
# As well as the number of cells (in column and in row), the size of a cell, the space in between cells...
# You can choose if the player can move the grid with moveable True/False
Cell=myModel.newCellsOnGrid(30,25,"hexagonal",size=20, gap=2, moveable=True)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

myModel.launch() 

sys.exit(monApp.exec_())
