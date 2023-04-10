import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(960,700, windowTitle="A BIG board with hexagonal cells")

# You can change the specifications of the grid cells 
# As well as the number of cells (in column and in row), the size of a cell, the space in between cells...
aGrid=myModel.newGrid(30,15,"hexagonal",size=20, gap=2)
aGrid.setValueCell("landUse","grass")
aGrid.setForX("landUse","forest",1)
aGrid.setForX("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)

myModel.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

theFirstLegend=myModel.newLegendAdmin()

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
