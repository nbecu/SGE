import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])




myModel=SGModel(1080,960,"grid")

theFirstGrid=myModel.createGrid(10,10,"hexagonal",Qt.gray,name="basicGrid")

myModel.setUpEntityValueAndPov("Forester",{"Forest":{"Niv3":Qt.green,"Niv2":Qt.red,"Niv1":Qt.yellow},"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},[theFirstGrid],"sea","reasonable")

theFirstGrid.setForRandom({"Forest":"Niv3"},30)

# Here are all the possibilities of Agents
myModel.newAgent("lac","circleAgent",[theFirstGrid])
myModel.setUpEntityValueAndPov("Forester",{"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},"lac","sea","reasonable",[theFirstGrid])
myModel.newAgent("lac2","squareAgent",[theFirstGrid])
myModel.setUpEntityValueAndPov("Forester",{"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},"lac2","sea","reasonable",[theFirstGrid])
myModel.newAgent("lac3","ellipseAgent1",[theFirstGrid])
myModel.setUpEntityValueAndPov("Forester",{"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},"lac3","sea","reasonable",[theFirstGrid])
myModel.newAgent("lac4","ellipseAgent2",[theFirstGrid])
myModel.setUpEntityValueAndPov("Forester",{"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},"lac4","sea","reasonable",[theFirstGrid])
myModel.newAgent("lac5","rectAgent1",[theFirstGrid])
myModel.setUpEntityValueAndPov("Forester",{"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},"lac5","sea","reasonable",[theFirstGrid])
myModel.newAgent("lac6","rectAgent2",[theFirstGrid])
myModel.setUpEntityValueAndPov("Forester",{"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},"lac6","sea","reasonable",[theFirstGrid])
myModel.newAgent("lac7","triangleAgent1",[theFirstGrid])
myModel.setUpEntityValueAndPov("Forester",{"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},"lac7","sea","reasonable",[theFirstGrid])
myModel.newAgent("lac8","triangleAgent2",[theFirstGrid])
myModel.setUpEntityValueAndPov("Forester",{"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},"lac8","sea","reasonable",[theFirstGrid])
myModel.newAgent("lac9","arrowAgent1",[theFirstGrid])
myModel.setUpEntityValueAndPov("Forester",{"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},"lac9","sea","reasonable",[theFirstGrid])
myModel.newAgent("lac10","arrowAgent2",[theFirstGrid])
myModel.setUpEntityValueAndPov("Forester",{"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},"lac10","sea","reasonable",[theFirstGrid])



theFirstLegende=myModel.createLegendAdmin()

myModel.iAm("Admin")

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())