import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *


monApp = QtWidgets.QApplication([])


# STEP1 Model

myModel = SGModel(
    1800, 900, x=5, windowTitle="dev project : Rehab Game", typeOfLayout="grid")


# STEP2 Grid and Cells
aGrid = myModel.newGrid(7, 7, "square", size=60, gap=2,
                        name='grid1')  # ,posXY=[20,90]
Cell.setEntities("Resource", 2)
Cell.setEntities("ProtectionLevel", "Free")
Cell.setRandomEntities("Resource", 3, 7)
Cell.setRandomEntities("Resource", 1, 3)

Cell.setRandomEntities("Resource", 0, 8)
Cell.setRandomEntities("ProtectionLevel", "Reserve", 1)


Cell.newPov("Resource", "Resource", {3: Qt.darkGreen, 2: Qt.green, 1: Qt.yellow, 0: Qt.white})
myModel.newBorderPov("ProtectionLevel", "ProtectionLevel", {"Reserve": Qt.magenta, "Free": Qt.black})

# STEP3 Agents
Workers = myModel.newAgentSpecies("Workers", "triangleAgent1", uniqueColor=Qt.black)
Birds = myModel.newAgentSpecies("Birds", "triangleAgent2", uniqueColor=Qt.yellow)
Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1",{"health":{"good","bad"},"hunger":{"good","bad"}})
Sheeps.newPov("Sheeps -> Health","health",{'good':Qt.blue,'bad':Qt.red})
Sheeps.newPov("Sheeps -> Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})
Sheeps.initDefaultAttValue("hunger","bad")

aSecondBird=myModel.newAgentAtCoords(aGrid,Birds,4,5)
aWorker=myModel.newAgentAtCoords(aGrid,Workers,2,2)
aSheep=myModel.newAgentAtCoords(aGrid,Sheeps,3,3)
aSecondSheep=myModel.newAgentAtCoords(aGrid,Sheeps,1,5)
aThirdSheep=myModel.newAgentAtCoords(aGrid,Sheeps,3,5)



# STEP4 Admin Players and GameActions
globalLegend = myModel.newLegend("Global Legend", showAgentsWithNoAtt=True)

Player1 = myModel.newPlayer("Player 1")
createA1=myModel.newCreateAction(Workers, 20)
Player1.addGameAction(createA1)
Player1.addGameAction(myModel.newDeleteAction(Workers, "infinite"))
Player1.addGameAction(myModel.newDeleteAction('Cell', "infinite"))
Player1.addGameAction(myModel.newUpdateAction('Cell', 3, {"Resource": 3}))
Player1.addGameAction(myModel.newMoveAction(Workers, 1))
Player1ControlPanel = Player1.newControlPanel(
    "Player 1 Actions", showAgentsWithNoAtt=True)

Player2 = myModel.newPlayer("Player 2")
Player2.addGameAction(myModel.newCreateAction(Birds,4))
Player2.addGameAction(myModel.newCreateAction(Sheeps,4,{"health":"good"}))
Player2.addGameAction(myModel.newUpdateAction(
    "Cell", 3, {"ProtectionLevel": "Reserve"}))
Player2.addGameAction(myModel.newUpdateAction(
    "Cell", "infinite", {"ProtectionLevel": "Free"}))
Player2ControlPanel = Player2.newControlPanel("Player 2 Actions",showAgentsWithNoAtt=True)

userSelector=myModel.newUserSelector()

# STEP5 Time management
myModel.timeManager.newGamePhase('Phase 1', [Player1, Player2])
myModel.timeManager.newGamePhase('Phase 2', [Player1, Player2])
GameRounds = myModel.newTimeLabel("My Game Time", Qt.white, Qt.black, Qt.black)
myModel.currentPlayer = 'Player 1'


# STEP6 DashBoard and EndGameRule
score1= myModel.newSimVariable(0,"Global Score:")
DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.black)
i1 = DashBoard.addIndicator("sumAtt", 'cell', attribute='Resource',color=Qt.black)
i2 = DashBoard.addIndicator("avgAtt", 'cell', attribute='Resource',color=Qt.black)
i3 = DashBoard.addIndicator("nb","agents",color=Qt.black)
i4 = DashBoard.addIndicator("nb","Workers",color=Qt.black)
i5 = DashBoard.addIndicatorOnSimVariable(score1)
DashBoard.showIndicators()

endGameRule = myModel.newEndGameRule(numberRequired=2)
endGameRule.addEndGameCondition_onIndicator(
    i1, "equal", 90, name="Resource equal to 90")
endGameRule.addEndGameCondition_onEntity(
    "cell1-5", 'Resource', "greater", 2, name="Cell 1-5 Resource is greater than 2",aGrid=aGrid)
endGameRule.showEndGameConditions()

# STEP7 TextBox
TextBox = myModel.newTextBox(
    title='Your game is starting...', textToWrite="Welcome !")

myModel.setCurrentPlayer("Player 1")
myModel.launch()


sys.exit(monApp.exec_())
