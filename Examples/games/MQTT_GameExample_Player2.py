import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *


monApp = QtWidgets.QApplication([])

random.seed(13)
myModel = SGModel(
    900, 900, nb_columns=5, windowTitle="MQTT Example - Player 2", typeOfLayout="grid")

Cell = myModel.newCellsOnGrid(7, 7, "square", size=60, gap=2,name='grid1')
Cell.setEntities("Resource", 2)
Cell.setEntities("ProtectionLevel", "Free")
Cell.setRandomEntities("Resource", 3, 7)
Cell.setRandomEntities("Resource", 1, 3)
Cell.setRandomEntities("Resource", 0, 8)
Cell.setRandomEntities("ProtectionLevel", "Reserve", 1)


Cell.newPov("Resource", "Resource", {3: Qt.darkGreen, 2: Qt.green, 1: Qt.yellow, 0: Qt.white})
Cell.newBorderPov("ProtectionLevel", "ProtectionLevel", {"Reserve": Qt.magenta, "Free": Qt.black})

Workers = myModel.newAgentType("Workers", "triangleAgent1")
Birds = myModel.newAgentType("Birds", "triangleAgent2", defaultColor=Qt.yellow)

aWorker = Workers.newAgentAtCoords(Cell,5,2)


globalLegend = myModel.newLegend("Global Legend", alwaysDisplayDefaultAgentSymbology=True)

Player1 = myModel.newPlayer("Player 1")
Player1.addGameAction(myModel.newCreateAction(Workers, aNumber=20))
Player1.addGameAction(myModel.newDeleteAction(Workers))
Player1.addGameAction(myModel.newModifyAction(Cell, {"Resource": 3}, 3,writeAttributeInLabel=True))
Player1.addGameAction(myModel.newMoveAction(Workers, 5))
Player1ControlPanel = Player1.newControlPanel("Player 1 Actions")

Player2 = myModel.newPlayer("Player 2")
Player2.addGameAction(myModel.newModifyAction(Cell, {"ProtectionLevel": "Reserve"}, 3))
Player2.addGameAction(myModel.newModifyAction(Cell, {"ProtectionLevel": "Free"}))
Player2ControlPanel = Player2.newControlPanel("Actions du Joueur 2")

myModel.newPlayPhase('Phase 1', [Player1,Player2])
myModel.newModelPhase([lambda: Cell.setRandomEntities("Resource",3),lambda: Cell.setRandomEntities("Resource",1,3)])
aModelAction2=myModel.newModelAction(lambda: Cell.setRandomEntities("Resource",3,2,condition=(lambda x: x.value("Resource") not in [0,1] )))
myModel.newModelPhase(aModelAction2)
aModelAction4=myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2))
aModelAction4.addCondition(lambda: myModel.roundNumber()==2)

GameRounds = myModel.newTimeLabel("My Game Time", Qt.white, Qt.black, Qt.red)
myModel.setCurrentPlayer('Player 2')

userSelector=myModel.newUserSelector()

TextBox = myModel.newTextBox(
    title='Début du jeu', textToWrite="Welcome Player 2")

TextBox.addText("A mqtt example", toTheLine=True)

globalScore=myModel.newSimVariable("Global Score",0)
DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.red)
i1 = DashBoard.addIndicator(Cell,"sumAtt",  attribute='Resource',color=Qt.black)
i2 = DashBoard.addIndicator(Cell,"avgAtt",  attribute='Resource',color=Qt.black)
i3 = DashBoard.addIndicatorOnSimVariable(globalScore)
aModelAction4.addFeedback(lambda: globalScore.incValue(5))
myModel.newModelPhase(aModelAction4)


endGameRule = myModel.newEndGameRule(numberRequired=2)
endGameRule.addEndGameCondition_onIndicator(
    i1, "equal", 90, name="Resource equal to 90")
endGameRule.addEndGameCondition_onEntity(Cell.getEntity(1,5), 'Resource', "greater", 2, name="Cell 1-5 Resource is greater than 2",aGrid=Cell.grid)
endGameRule.showEndGameConditions()


# Option 1: Use localhost (default)
# myModel.launch_withMQTT("Instantaneous")

# Option 2: Use online broker (Eclipse Mosquitto)
myModel.launch_withMQTT("Instantaneous", broker_host="test.mosquitto.org")

# Option 3: Use another online broker
# myModel.launch_withMQTT("Instantaneous", broker_host="broker.hivemq.com")

sys.exit(monApp.exec_())
