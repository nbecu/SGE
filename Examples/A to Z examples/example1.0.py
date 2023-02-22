import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1530,830, windowTitle="About pov (3)")

aGrid=myModel.createGrid(10,10,"square",Qt.gray,size=75)
aGrid.setValueForCells({"landUse":"grass"})
aGrid.setForX({"landUse":"forest"},1)
aGrid.setForX({"landUse":"forest"},2)
aGrid.setForRandom({"landUse":"shrub"},10)

#Pov (point of view), allow to specify different ways to view the state of the cells
#A pov allow to define the color displayed for a certain value of a given attribute of the cell
#In this example there are two pov: povLandUse and povLandUse2
# The first can see the difference between grass and schrub, the second cannot
myModel.setUpPov("ICanSeeSchrub",{"landUse":{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen}},[aGrid])
myModel.setUpPov("ICantSeeSchrub",{"landUse":{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen}},[aGrid])

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
