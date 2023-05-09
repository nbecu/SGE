import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="About legend (1)")


aGrid=myModel.newGrid(10,10,"square",size=60, gap=2)
aGrid.setValueCell("landUse","grass")
aGrid.setForX("landUse","forest",1)
aGrid.setForX("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)

myModel.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

theFirstLegend=myModel.newLegendAdmin()
# the admin's legend enables to change all the entities without restrictions
# it will be displayed only for an Admin user.
# By default, a model user is an Admin user


myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
