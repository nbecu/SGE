import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="Nobody can move my grid")

# You can change the specifications of the grid cells 
# You can choose if the player can move the grid with moveable True/False
aGrid=myModel.createGrid(12,5,"square", size=30, gap=4, moveable=False)
aGrid.setValueForCells("landUse","grass")
aGrid.setForX("landUse","forest",1)
aGrid.setForX("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)

myModel.setUpPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.setUpPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

theFirstLegend=myModel.createLegendAdmin()

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
