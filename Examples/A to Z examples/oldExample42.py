import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Example to test drag and drop of agents


myModel=SGModel(1080,960,"grid")

aGrid=myModel.createGrid(10,10,"square",Qt.gray)

myModel.setUpEntityValueAndPov("Forester",{"Forest":{"Niv3":Qt.green,"Niv2":Qt.red,"Niv1":Qt.yellow},"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},[aGrid],"sea","reasonable")

myModel.setInitialPov("Forester")

aGrid.setForRandom({"Forest":"Niv3"},30)

myModel.newAgent("lac","circleAgent",[aGrid])

myModel.setUpEntityValueAndPov("Forester",{"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},"lac","sea","reasonable",[aGrid])


theFirstLegend=myModel.createLegendAdmin()

myModel.show() 

sys.exit(monApp.exec_())