import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Simple example of checking the ownership

myModel=SGModel(1080,960,"grid")

theFirstGrid=myModel.createGrid("basicGrid",10,10,"hexagonal",Qt.gray)

theSecondGrid=myModel.createGrid("theSecondGrid",8,10,"square",Qt.gray)

myModel.setUpCellValueAndPov("Forester",{"Forest":{"Niv1":Qt.yellow,"Niv2":Qt.red,"Niv3":Qt.green},"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},[theFirstGrid,theSecondGrid],"sea","reasonable")

myModel.setInitialPovGlobal("Forester")

theFirstGrid.setForRandom({"Forest":"Niv1"},30)

theFirstGrid.setForRandom({"Forest":"Niv2"},4)

anAgentLac=myModel.newAgent("lac","circleAgent",[theFirstGrid,theSecondGrid])

myModel.setUpCellValueAndPov("Forester",{"boat":{"new":Qt.blue,"old":Qt.cyan}},"lac","boat","old",[theFirstGrid,theSecondGrid])


theFirstLegende=myModel.createLegendeAdmin()

thePlayer=myModel.newPlayer("Gertrude")

thePlayer.addGameAction(myModel.createCreateAction(anAgentLac,5,{"boat":["old"]} ))

aGameAction = thePlayer.addGameAction(myModel.createUpdateAction(theFirstGrid.getACell(),3,{"sea":["deep sea"]}))
aGameAction.addRestrictions(lambda aCell : aCell.isMineOrAdmin())
aGameAction.addFeedback(lambda aCell: aCell.getProperty())
thePlayer.addGameAction(myModel.createUpdateAction(theFirstGrid.getACell(),3,{"sea":["reasonable"]},[lambda aCell : aCell.isMine()]))
thePlayer.addGameAction(myModel.createUpdateAction(anAgentLac,2,{"boat":["new"]},[lambda agent : agent.isMineOrAdmin()]))

action=thePlayer.addGameAction(myModel.createMooveAction(anAgentLac,2,{"boat":["new"]},[lambda agent : agent.isMineOrAdmin()],[lambda aCell : aCell.changeValue({"sea": "deep sea"})],[],[lambda agent: agent.changeValue({"boat":"old"})],[lambda aCell,agent : aCell.checkValue({"sea": "deep sea"})]))


myModel.timeManager.addGamePhase("theFirstPhase",0,thePlayer,[lambda: myModel.getGameSpace("basicGrid").setForRandom({"Forest":"Niv3"},10)])

myModel.timeManager.addGamePhase("the7Phase",7,None,[lambda: myModel.getGameSpace("basicGrid").setForRandom({"Forest":"Niv2"},15)])

#Ajout de condition de victoire
myModel.timeManager.addEndGameCondition(lambda: myModel.timeManager.verifNumberOfRound(8))

myModel.iAm("Gertrude")

myModel.launch() 

sys.exit(monApp.exec_())
