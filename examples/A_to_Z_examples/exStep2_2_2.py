import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(windowTitle="Define multiple symbologies and define the initial symbology")

Cell = myModel.newCellsOnGrid(10, 10, "square", size=50)
Cell.setEntities("landUse", "grass")
Cell.setEntities_withColumn("landUse", "forest", 1)
Cell.setEntities_withColumn("landUse", "forest", 2)
Cell.setRandomEntities("landUse", "shrub", 10)

# Symbology allows to specify the visual representation (color, shape, etc.) of cells based on attribute values
# In this example there are two symbologies for the same attribute:
# The first can see the difference between grass and shrub, the second cannot
Cell.newSymbology("landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen}, name="ICanSeeShrub")
Cell.newSymbology("landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen}, name="ICantSeeShrub")
    
#You can change the initial symbology displayed with the instruction displaySymbology()
Cell.displaySymbology("ICantSeeShrub")
#If you don't set the initial symbology, the first declared symbology will be the initial one
#You can change symbology during the simulation through the toolbar of the window (symbology icon)

myModel.launch() 

sys.exit(monApp.exec())
