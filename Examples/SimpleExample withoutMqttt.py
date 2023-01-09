import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1080,960,"grid")

theSecondGrid=myModel.createGrid(10,10,"square",Qt.gray)

theFirstGrid=myModel.createGrid(10,10,"hexagonal",Qt.gray)

myModel.setUpEntityValueAndPov("Forester",{"Forest":{"Niv3":Qt.green,"Niv2":Qt.red,"Niv1":Qt.yellow}},[theFirstGrid],"Forest","Niv1")

myModel.setUpEntityValueAndPov("Forester",{"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},[theSecondGrid],"sea","reasonable")

myModel.setInitialPov("Forester")

theFirstGrid.setForRandom({"Forest":"Niv3"},30)

theFirstLegend=myModel.createLegendAdmin()

myModel.iAm("Admin")
 
myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
