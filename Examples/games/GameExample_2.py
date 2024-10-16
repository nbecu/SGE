import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *


monApp = QtWidgets.QApplication([])


# STEP1 Model

myModel = SGModel(
    1800, 900, x=5, windowTitle="dev project : Rehab Game", typeOfLayout="grid")


# STEP2 Grid and Cells
Cell = myModel.newCellsOnGrid(7, 7, "square", size=60, gap=2,name='grid1')
Cell.setEntities("Resource", 2)
Cell.setEntities("ProtectionLevel", "Free")
Cell.setRandomEntities("Resource", 3, 7)
Cell.setRandomEntities("Resource", 1, 3)

Cell.setRandomEntities("Resource", 0, 8)
Cell.setRandomEntities("ProtectionLevel", "Reserve", 1)


Cell.newPov("Resource", "Resource", {3: Qt.darkGreen, 2: Qt.green, 1: Qt.yellow, 0: Qt.white})
Cell.newBorderPov("ProtectionLevel", "ProtectionLevel", {"Reserve": Qt.magenta, "Free": Qt.black})

# STEP3 Agents
Workers = myModel.newAgentSpecies("Workers", "triangleAgent1", defaultColor=Qt.gray)
Birds = myModel.newAgentSpecies("Birds", "triangleAgent2", defaultColor=Qt.yellow)
Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1")
Sheeps.setDefaultValues({"health":(lambda: random.choice(["good","bad"])),"hunger":(lambda: random.choice(["good","bad"]))})
Sheeps.newPov("Health","health",{'good':Qt.blue,'bad':Qt.red})
Sheeps.newPov("Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})
Sheeps.setDefaultValue("hunger","bad")

aSecondBird=Birds.newAgentAtCoords(Cell,4,5)
aWorker=Workers.newAgentAtCoords(Cell,2,2)
aSheep=Sheeps.newAgentAtCoords(Cell,3,3)
aSecondSheep=Sheeps.newAgentAtCoords(Cell,1,5)
aThirdSheep=Sheeps.newAgentAtCoords(Cell,3,5)



# STEP4 Admin Players and GameActions
globalLegend = myModel.newLegend("Global Legend", showAgentsWithNoAtt=True)

Player1 = myModel.newPlayer("Player 1")
createA1=myModel.newCreateAction(Workers, aNumber=20)
Player1.addGameAction(createA1)
Player1.addGameAction(myModel.newDeleteAction(Workers, "infinite"))
Player1.addGameAction(myModel.newDeleteAction('Cell', "infinite"))
Player1.addGameAction(myModel.newUpdateAction('Cell', {"Resource": 3}, 3))
Player1.addGameAction(myModel.newMoveAction(Workers, 1))
Player1ControlPanel = Player1.newControlPanel(
    "Player 1 Actions", showAgentsWithNoAtt=True)

Player2 = myModel.newPlayer("Player 2")
Player2.addGameAction(myModel.newCreateAction(Birds,aNumber=4))
Player2.addGameAction(myModel.newCreateAction(Sheeps,{"health":"good"},4))
Player2.addGameAction(myModel.newUpdateAction(
    "Cell", {"ProtectionLevel": "Reserve"}, 3))
Player2.addGameAction(myModel.newUpdateAction(
    "Cell", {"ProtectionLevel": "Free"}))
Player2ControlPanel = Player2.newControlPanel("Player 2 Actions",showAgentsWithNoAtt=True)

userSelector=myModel.newUserSelector()

# STEP5 Time management
myModel.timeManager.newGamePhase('Phase 1', [Player1, Player2])
myModel.timeManager.newGamePhase('Phase 2', [Player1, Player2])
GameRounds = myModel.newTimeLabel("My Game Time", Qt.white, Qt.black, Qt.black)
myModel.setCurrentPlayer('Player 1')


# STEP6 DashBoard and EndGameRule
score1= myModel.newSimVariable("Global Score",0)
DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.black)
i1 = DashBoard.addIndicator(Cell,"sumAtt", attribute='Resource',color=Qt.black)
i2 = DashBoard.addIndicator(Cell,"avgAtt", attribute='Resource',color=Qt.black)
i3 = DashBoard.addIndicator([Workers,Birds,Sheeps],"nb",color=Qt.black)
i4 = DashBoard.addIndicator(Workers,"nb",color=Qt.black)
i5 = DashBoard.addIndicatorOnSimVariable(score1)

endGameRule = myModel.newEndGameRule(numberRequired=2)
endGameRule.addEndGameCondition_onIndicator(
    i1, "equal", 90, name="Resource equal to 90")
endGameRule.addEndGameCondition_onEntity(
    Cell.getEntity(1,5), 'Resource', "greater", 2, name="Cell 1-5 Resource is greater than 2",aGrid=Cell.grid)
endGameRule.showEndGameConditions()

# STEP7 TextBox
TextBox = myModel.newTextBox(
    title='Your game is starting...', textToWrite="Welcome !")

myModel.setCurrentPlayer("Player 1")
myModel.launch()


sys.exit(monApp.exec_())
