import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="EndGame Conditions and Scores")

aGrid=myModel.newGrid(10,10,"square",size=60, gap=2)
aGrid.setCells("landUse","grass")
aGrid.setCells_withColumn("landUse","forest",1)
aGrid.setCells_withColumn("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)

myModel.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1",{"health":{"good","bad"},"hunger":{"good","bad"}})
Sheeps.newPov("Sheeps -> Health","health",{'good':Qt.blue,'bad':Qt.red})
Sheeps.newPov("Sheeps -> Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})
m1=myModel.newAgentAtCoords(aGrid,Sheeps,1,1,aDictofAttributs={"health":"good","hunger":"bad"})
m2=myModel.newAgentAtCoords(aGrid,Sheeps,5,1)

theFirstLegend=myModel.newLegendAdmin()


Player1=myModel.newPlayer("Player 1")
Player1.addGameAction(myModel.newUpdateAction('Cell',3,{"landUse":"grass"}))
Player1Legend=Player1.newControlPanel("Actions du Joueur 1",showAgentsWithNoAtt=True)

userSelector=myModel.newUserSelector()


myModel.timeManager.newGamePhase('Phase 1', [Player1])
aModelAction5=myModel.newModelAction(lambda: myModel.getAgent(Sheeps,"1").moveAgent(method="cardinal",direction="South"))
myModel.timeManager.newModelPhase(aModelAction5)
myModel.timeManager.newModelPhase([lambda: aGrid.setRandomCell("landUse","forest"),lambda: aGrid.setRandomCells("landUse","shrub",3)])

aModelAction1=myModel.newModelAction(lambda: aGrid.setRandomCells_withValueNot("landUse","forest",2,"landUse","forest"))
aModelAction2=myModel.newModelAction(lambda: aGrid.setRandomCells("landUse","forest",2,condition=(lambda x: x.value("landUse") != "shrub" and x.value("landUse") != "forest"  )))
aModelAction3=myModel.newModelAction(lambda: aGrid.setRandomCells_withValueNot("landUse","forest",3,"landUse","forest",condition=(lambda x: x.value("landUse") != "shrub") ))

aModelAction4 =myModel.newModelAction(lambda: aGrid.setRandomCells("landUse","forest",2))
aModelAction4.addCondition(lambda: myModel.getCurrentRound()==3) 

myModel.timeManager.newModelPhase(aModelAction2)

GameRounds = myModel.newTimeLabel("My Game Time", Qt.white, Qt.black, Qt.black)

DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.black)
i1 = DashBoard.addIndicator("score",None,indicatorName="Score : ",color=Qt.black)
i2 = DashBoard.addIndicator("nb", 'cell', attribute='landUse',value='forest',color=Qt.black)
DashBoard.showIndicators()
# Here is the way to add feedback on score on ModelAction
aModelAction4.addFeedback(lambda: i1.setResult(i1.result + 5))
myModel.timeManager.newModelPhase(aModelAction4, name="Score Time!")


# Here you can add a Widget to show the EndGame Conditions of your game
# This game will be declared ended when the score declared in the DashBoard is equal to 90. 
endGameRule = myModel.newEndGameRule(numberRequired=1)
endGameRule.addEndGameCondition_onIndicator(
    i1, "equal", 90, name="Score equal to 90")
endGameRule.showEndGameConditions()

myModel.launch() 

sys.exit(monApp.exec_())