import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Try to play with pov and atttributes


myModel=SGModel(800,800,"grid")

aGrid=myModel.createGrid("basicGrid",10,10,"square",Qt.gray,size=80, gap=-2)

aGrid.setValueForCells({"landUse":"grass"})
aGrid.setForX({"landUse":"forest"},1)
aGrid.setForX({"landUse":"forest"},2)
aGrid.setForRandom({"landUse":"shrub"},10)

myModel.setUpPov("povLandUse",{"landUse":{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen}},[aGrid])
myModel.setUpPov("povLandUse2",{"landUse":{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen}},[aGrid])
#should implement -> have a pov that depends on the value of 2 attributes . Ex. if landUse is grass and presenceBush=true than color is brown

myModel.setInitialPovGlobal("povLandUse")


theFirstLegend=myModel.createLegendAdmin()

myModel.iAm("Admin")

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
