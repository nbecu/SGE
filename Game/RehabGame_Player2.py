import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGSGE import *


monApp = QtWidgets.QApplication([])



myModel = SGModel(
    900, 900, x=5, windowTitle="dev project : Rehab Game", typeOfLayout="grid")


Cell = myModel.newCellsOnGrid(7, 7, "square", size=60, gap=2,
                        name='grid1')  # ,posXY=[20,90]
Cell.setEntities("Resource", "2")
Cell.setEntities("ProtectionLevel", "Free")
Cell.setRandomEntities("Resource", "3", 7)
Cell.setRandomEntities("Resource", "1", 3)

Cell.setRandomEntities("Resource", "0", 8)
Cell.setRandomEntities("ProtectionLevel", "Reserve", 1)


Cell.newPov("Resource", "Resource", {
               "3": Qt.darkGreen, "2": Qt.green, "1": Qt.yellow, "0": Qt.white})
Cell.newBorderPov("ProtectionLevel", "ProtectionLevel", {
                     "Reserve": Qt.magenta, "Free": Qt.black})

Workers = myModel.newAgentSpecies(
    "Workers", "triangleAgent1", uniqueColor=Qt.black)
Birds = myModel.newAgentSpecies(
    "Birds", "triangleAgent2", uniqueColor=Qt.yellow)


globalLegend = myModel.newLegend("Global Legend", showAgentsWithNoAtt=True)

Player1 = myModel.newPlayer("Player 1")
Player1.addGameAction(myModel.newCreateAction(Workers, 20))
Player1.addGameAction(myModel.newDeleteAction(Workers, "infinite"))
Player1.addGameAction(myModel.newUpdateAction('Cell', 3, {"Resource": "3"}))
Player1.addGameAction(myModel.newMoveAction(Workers, 1))
Player1ControlPanel = Player1.newControlPanel(
    "Player 1 Actions", showAgentsWithNoAtt=True)

Player2 = myModel.newPlayer("Player 2")
Player2.addGameAction(myModel.newUpdateAction(
    "Cell", 3, {"ProtectionLevel": "Reserve"}))
Player2.addGameAction(myModel.newUpdateAction(
    "Cell", "infinite", {"ProtectionLevel": "Free"}))
Player2ControlPanel = Player2.newControlPanel("Actions du Joueur 2")

myModel.timeManager.newGamePhase('Phase 1', [Player1, Player2])
myModel.timeManager.newGamePhase('Phase 2', [Player1, Player2])
GameRounds = myModel.newTimeLabel("My Game Time", Qt.white, Qt.black, Qt.red)
myModel.setCurrentPlayer('Player 2')

userSelector=myModel.newUserSelector()

TextBox = myModel.newTextBox(
    title='Début du jeu', textToWrite="Bonjour et bienvenue dans RehabGame !")

TextBox.addText("J'espère que vous allez bien!!!", toTheLine=True)

DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.red)
i1 = DashBoard.addIndicator("sumAtt", 'Cell', attribute='Resource',color=Qt.black)
i2 = DashBoard.addIndicator("avgAtt", 'Cell', attribute='Resource',color=Qt.black)
DashBoard.showIndicators()

userSelector = myModel.newUserSelector()

endGameRule = myModel.newEndGameRule(numberRequired=2)
endGameRule.addEndGameCondition_onIndicator(
    i1, "equal", 90, name="Resource equal to 90")
endGameRule.addEndGameCondition_onEntity(
    "cell1-5", 'Resource', "greater", 2, name="Cell 1-5 Resource is greater than 2",aGrid=aGrid)
endGameRule.showEndGameConditions()


myModel.launch_withMQTT() # https://mosquitto.org/download/

sys.exit(monApp.exec_())
