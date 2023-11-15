import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="Add a TextBox")

Cell=myModel.newGrid(10,10,"square",size=60, gap=2)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1",{"health":{"good","bad"},"hunger":{"good","bad"}})
Sheeps.newPov("Sheeps -> Health","health",{'good':Qt.blue,'bad':Qt.red})
Sheeps.newPov("Sheeps -> Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})
m1=Sheeps.newAgentAtCoords(Cell,1,1,{"health":"good","hunger":"bad"})
m2=Sheeps.newAgentAtCoords(Cell,5,1)

theFirstLegend=myModel.newLegend()


Player1=myModel.newPlayer("Player 1")
Player1.addGameAction(myModel.newUpdateAction('Cell',3,{"landUse":"grass"}))
# Player2.addGameAction(myModel.newCreateAction(Sheeps,4,{"health":"good"}))

Player1Legend=Player1.newControlPanel("Actions du Joueur 1",showAgentsWithNoAtt=True)

userSelector=myModel.newUserSelector()


myModel.timeManager.newGamePhase('Phase 1', [Player1])
myModel.timeManager.newModelPhase([lambda: Cell.setRandomEntities("landUse","forest"),lambda: Cell.setRandomEntities("landUse","shrub",3)])

# aModelAction1=myModel.newModelAction(lambda: Cell.setRandomEntities_withValueNot("landUse","forest",2,"landUse","forest"))
aModelAction2=myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2,condition=(lambda x: x.value("landUse") != "shrub" and x.value("landUse") != "forest"  )))
# aModelAction3=myModel.newModelAction(lambda: Cell.setRandomEntities_withValueNot("landUse","forest",3,"landUse","forest",condition=(lambda x: x.value("landUse") != "shrub") ))

aModelAction4 =myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2))
aModelAction4.addCondition(lambda: myModel.round()==2) 

myModel.timeManager.newModelPhase(aModelAction2)

GameRounds = myModel.newTimeLabel("My Game Time", Qt.white, Qt.black, Qt.black)

DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.black)
i1 = DashBoard.addIndicator("score",None,indicatorName="Score")
DashBoard.showIndicators()
aModelAction4.addFeedback(lambda: i1.setResult(i1.result + 5))
myModel.timeManager.newModelPhase(aModelAction4)

endGameRule = myModel.newEndGameRule(numberRequired=1)
endGameRule.addEndGameCondition_onIndicator(
    i1, "equal", 90, name="Score equal to 90")
endGameRule.showEndGameConditions()

# You can add TextBoxes to your game
# You can cuztomize the text, the title color and font by using the proper functions.
TextBox = myModel.newTextBox(
    title='Your game is starting...', textToWrite="Welcome !")

myModel.setCurrentPlayer("Player1")
myModel.launch()


sys.exit(monApp.exec_())