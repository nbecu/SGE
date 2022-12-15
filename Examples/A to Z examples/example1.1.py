import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(830,830)

aGrid=myModel.createGrid(10,10,"square",Qt.gray,size=75)
aGrid.setValueForCells({"landUse":"grass"})
aGrid.setForX({"landUse":"forest"},1)
aGrid.setForX({"landUse":"forest"},2)
aGrid.setForRandom({"landUse":"shrub"},10)

#Pov (point of view), allow to specify different ways to view the state of the cells
#A pov allow to define the color displayed for a certain value of a given attribute of the cell
#In this example there are two pov: povLandUse and povLandUse2
myModel.setUpPov("povLandUse",{"landUse":{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen}},[aGrid])
myModel.setUpPov("povLandUse2",{"landUse":{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen}},[aGrid])
#should implement -> have a pov that depends on the value of 2 attributes . Ex. if landUse is grass and presenceBush=true than color is brown

#You can change the initial pov displayed with the instruction setInitialPov()
myModel.setInitialPov("povLandUse2")

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
