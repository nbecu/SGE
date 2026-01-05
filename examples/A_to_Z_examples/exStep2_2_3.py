import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(700,600, windowTitle="Define several points of view and define the symbology of the border of the cells")

Cell = myModel.newCellsOnGrid(10, 10, "square", size=50)
Cell.setEntities("landUse", "grass")
Cell.setEntities_withColumn("landUse", "forest", 1)
Cell.setEntities_withColumn("landUse", "forest", 2)
Cell.setRandomEntities("landUse", "shrub", 10)

#a Pov (point of view) allow to specify the symbology (color, shape, etc.) used to display the cells, depending on the value of a given attribute of the cell
#In this example there are two pov:
#The first can see the difference between grass and schrub, the second cannot
Cell.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

#adds a new attribute to the cells
Cell.setEntities("ProtectionLevel", "Free")
Cell.setRandomEntities("ProtectionLevel", "Reserve", 1)
#adds a new pov, to specify the symbology of the border of the cells (a borderPov), depending on the value of a given attribute of the cell
Cell.newBorderPov("ProtectionLevel_1", "ProtectionLevel", {"Reserve": Qt.magenta, "Free": Qt.transparent})
#adds a second border pov
Cell.newBorderPovColorAndWidth("ProtectionLevel_2", "ProtectionLevel", {"Reserve": [Qt.magenta,5], "Free": [Qt.black,1]})

#sets the initial border pov
Cell.displayBorderPov("ProtectionLevel_2")

myModel.launch() 

sys.exit(monApp.exec_())
