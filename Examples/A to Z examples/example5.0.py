import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1080,960,"About agents (2)")

theFirstGrid=myModel.createGrid(10,10,"hexagonal",Qt.gray, name="basicGrid")
myModel.setUpEntityValueAndPov("Forester",{"Forest":{"Niv1":Qt.yellow,"Niv2":Qt.red,"Niv3":Qt.green},"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},[theFirstGrid],"sea","reasonable")
myModel.setInitialPov("Forester")

theFirstGrid.setForRandom({"Forest":"Niv1"},30)
theFirstGrid.setForRandom({"Forest":"Niv2"},4)

anAgentLac=myModel.newAgent("lac","circleAgent",[theFirstGrid])
myModel.setUpEntityValueAndPov("Forester",{"boat":{"new":Qt.blue,"old":Qt.cyan}},"lac","boat","old",[theFirstGrid])
theFirstLegend=myModel.createLegendAdmin()

# Agents can be also placed by a player
# After calling your player and set time à 0
thePlayer=myModel.createPlayer("Player1")
myModel.timeManager.addGamePhase("theFirstPhase",thePlayer)

# you can create a GameAction for your player to interact with the grid
# it also permits to give interaction between cell and agents like here : if you place a certain agent on a certain type of cell, the cell updates to a new status
numberofAction=7
thePlayer.addGameAction(myModel.createCreateAction(anAgentLac,numberofAction,{"boat":["old"]},[lambda aCell: aCell.checkValue({"sea":"reasonable"})]  ,  [lambda aCell: aCell.changeValue({"sea": "deep sea"})]  , [lambda aCell: aCell.parent.getCellFromCoordinates(1,1).checkValue({"sea":"reasonable"}) ]))

myModel.iAm("Player1")
myModel.show() 

sys.exit(monApp.exec_())