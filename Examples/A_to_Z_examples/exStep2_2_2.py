import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(700,600, windowTitle="Define several points of view and define the initial symbology")

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

#You can change the initial pov displayed with the instruction displayPov()
Cell.displayPov("ICantSeeShrub")
#If you don't set the initial pov, the first declared pov will be the initial one
#You can change POV during the simulation through the toolbar of the window (symbology icon)

myModel.launch() 

sys.exit(monApp.exec_())
