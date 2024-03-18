import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(400,400, windowTitle="Try to debug permanent refresh", typeOfLayout='vertical')

Cell = myModel.newCellsOnGrid(1, 1, "square",gap=10, size=50)

Cell.setEntities("landUse", "grass")
Cell.setEntities_withColumn("landUse", "forest", 1)

Cell.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1")
Sheeps.newAgentAtRandom(Cell)


myModel.launch() 

sys.exit(monApp.exec_())
