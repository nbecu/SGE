import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Simple example 

myModel=SGModel(1080,960,"grid")

theFirstGrid=myModel.createGrid("basicGrid",10,10,"square",Qt.gray)


myModel.setUpCellValueAndPov("Forester",{"Forest":{"Niv1":Qt.yellow,"Niv2":Qt.blue,"Niv3":Qt.green}},[theFirstGrid],"Forest","Niv2")

myModel.setInitialPov("Forester")

theFirstGrid.setForRandom({"Forest":"Niv3"},42)

theFirstGrid.setValueForCells({"Risk":"high"})

theFirstGrid.setForXandY({"Risk":"low"},2,2)

theFirstGrid.setForX({"Risk":"low"},5)

theFirstGrid.setForY({"Risk":"low"},8)

myModel.setUpPov("Fireman",{"Risk":{"low":Qt.yellow,"high":Qt.red}},[theFirstGrid])


theFirstLegend=myModel.createLegendAdmin()

myModel.show() 

sys.exit(monApp.exec_())