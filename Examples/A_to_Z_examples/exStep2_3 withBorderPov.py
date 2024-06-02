import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(600,400, windowTitle="A board with hexagonal cells")

# You can change the specifications of the grid cells 
# For example you can change the shape of the cells
Cell=myModel.newCellsOnGrid(10,10,"square",size=30)

Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})


Cell.setEntities("ProtectionLevel", "Free")
Cell.setRandomEntities("ProtectionLevel", "Reserve", 1)
Cell.newBorderPov("ProtectionLevel", "ProtectionLevel", {"Reserve": Qt.magenta, "Free": Qt.black})
Cell.newBorderPovColorAndWidth("ProtectionLevel2", "ProtectionLevel", {"Reserve": [Qt.magenta,4], "Free": [Qt.transparent,1]})

myModel.launch() 

sys.exit(monApp.exec_())
