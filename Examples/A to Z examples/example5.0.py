import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Simple example

myModel=SGModel(1080,960,"grid")

theFirstGrid=myModel.createGrid(10,10,"hexagonal",Qt.gray, name="basicGrid")

theSecondGrid=myModel.createGrid(4,4,"square",Qt.gray)

#testLabel= myModel.createGameActionController()

myModel.setUpEntityValueAndPov("Forester",{"Forest":{"Niv1":Qt.yellow,"Niv2":Qt.red,"Niv3":Qt.green},"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},[theFirstGrid,theSecondGrid],"sea","reasonable")

myModel.setInitialPov("Forester")

theFirstGrid.setForRandom({"Forest":"Niv1"},30)

theFirstGrid.setForRandom({"Forest":"Niv2"},4)

anAgentLac=myModel.newAgent("lac","circleAgent",[theFirstGrid,theSecondGrid])

myModel.setUpEntityValueAndPov("Forester",{"boat":{"new":Qt.blue,"old":Qt.cyan}},"lac","boat","old",[theFirstGrid,theSecondGrid])

theFirstLegend=myModel.createLegendAdmin()

thePlayer=myModel.createPlayer("Gertrude")

# A game action is a rule to interact wit hthe grid, here only two agents can be placed
# it also permits to give interaction between cell and agents like here : if you place a certain agent on a certain type of cell, the cell updates to a new status
numberofAction=2
thePlayer.addGameAction(myModel.createCreateAction(anAgentLac,numberofAction,{"boat":["old"]},[lambda aCell: aCell.checkValue({"sea":"reasonable"})]  ,  [lambda aCell: aCell.changeValue({"sea": "deep sea"})]  , [lambda aCell: aCell.parent.getCellFromCoordinates(1,1).checkValue({"sea":"reasonable"}) ]))
myModel.timeManager.addGamePhase("theFirstPhase",0,thePlayer,[lambda: myModel.getGameSpace("basicGrid").setForRandom({"Forest":"Niv1"},3)])

thePlayer.addGameAction(myModel.createDeleteAction(anAgentLac,1,))

myModel.iAm("Gertrude")
myModel.show() 

sys.exit(monApp.exec_())