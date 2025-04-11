import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="ActivateActions Menu")

Cell=myModel.newCellsOnGrid(10,10,"square",size=40, gap=2)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1")
Sheeps.newPov("Sheeps -> Health","health",{'good':Qt.blue,'bad':Qt.red})
Sheeps.newPov("Sheeps -> Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})
Sheeps.setDefaultValues({"health":"good","hunger":"good"})
m1=Sheeps.newAgentAtCoords(Cell,4,2,{"health":"good","hunger":"bad"})
m2=Sheeps.newAgentAtCoords(Cell,5,2)

theFirstLegend=myModel.newLegend()


Player1=myModel.newPlayer("Player 1")
# For SGActivateAction it is possible to specify setControllerContextualMenu=True to set the controller on the entity on right clic
Player1.addGameAction(myModel.newModifyAction(Cell,{"landUse":"grass"},3))
UpdateTest=myModel.newModifyAction(Sheeps,{"health":"good"},setControllerContextualMenu=True)
Player1.addGameAction(UpdateTest)
UpdateTest2=myModel.newModifyAction(Sheeps,{"health":"bad"},setControllerContextualMenu=True)
Player1.addGameAction(UpdateTest2)
UpdateTest3=myModel.newModifyAction(Sheeps,{"hunger":"good"},setControllerContextualMenu=True)
Player1.addGameAction(UpdateTest3)
UpdateTest4=myModel.newModifyAction(Sheeps,{"hunger":"bad"},setControllerContextualMenu=True)
Player1.addGameAction(UpdateTest4)
Player1Legend=Player1.newControlPanel("Actions du Joueur 1",showAgentsWithNoAtt=True)

userSelector=myModel.newUserSelector()


myModel.timeManager.newGamePhase('Phase 1', [Player1])
aModelAction5=myModel.newModelAction(lambda: Sheeps.getEntity(1).moveAgent(method="cardinal",direction="South"))
myModel.timeManager.newModelPhase(aModelAction5)
myModel.timeManager.newModelPhase([lambda: Cell.setRandomEntities("landUse","forest"),lambda: Cell.setRandomEntities("landUse","shrub",3)])

aModelAction1=myModel.newModelAction(lambda: Cell.setRandomEntities_withValueNot("landUse","forest",2,"landUse","forest"))
aModelAction2=myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2,condition=(lambda x: x.value("landUse") != "shrub" and x.value("landUse") != "forest"  )))
aModelAction3=myModel.newModelAction(lambda: Cell.setRandomEntities_withValueNot("landUse","forest",3,"landUse","forest",condition=(lambda x: x.value("landUse") != "shrub") ))

aModelAction4 =myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2))
aModelAction4.addCondition(lambda: myModel.roundNumber()==3) 

myModel.timeManager.newModelPhase(aModelAction2)

GameRounds = myModel.newTimeLabel("My Game Time", Qt.white, Qt.black, Qt.black)

DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.black)
score1= myModel.newSimVariable("Score",0)
i1 = DashBoard.addIndicatorOnSimVariable(score1) 
i2 = DashBoard.addIndicator(Cell,"nbEqualTo",  attribute='landUse',value='forest',color=Qt.black)
aModelAction4.addFeedback(lambda: score1.incValue(5))
myModel.timeManager.newModelPhase(aModelAction4, name="Score Time!")


endGameRule = myModel.newEndGameRule(numberRequired=1)
endGameRule.addEndGameCondition_onIndicator(i1, "equal", 90, name="Score equal to 90")
endGameRule.showEndGameConditions()

myModel.launch() 

sys.exit(monApp.exec_())