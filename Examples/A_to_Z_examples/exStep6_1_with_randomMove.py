import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="Add a DashBoard")

Cell=myModel.newCellsOnGrid(10,10,"square",size=60, gap=2)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",30)

Cell.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1")
Sheeps.newPov("Health","health",{'good':Qt.blue,'bad':Qt.red})
Sheeps.newPov("Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})
m1=Sheeps.newAgentAtCoords(Cell,1,1,{"health":"good","hunger":"bad"})
m2=Sheeps.newAgentAtCoords(Cell,5,1)

theFirstLegend=myModel.newLegend()


Player1=myModel.newPlayer("Player 1")
Player1.addGameAction(myModel.newModifyAction(Cell,{"landUse":"grass"},3))
Player1Legend=Player1.newControlPanel("Actions du Joueur 1",showAgentsWithNoAtt=True)

userSelector=myModel.newUserSelector()


myModel.timeManager.newGamePhase('Phase 1', [Player1])
p2 = myModel.timeManager.newModelPhase([lambda: Cell.setRandomEntities("landUse","forest"),lambda: Cell.setRandomEntities("landUse","shrub",3)])
p2.addAction(lambda : Sheeps.moveRandomly())

aModelAction1=myModel.newModelAction(lambda: Cell.setRandomEntities_withValueNot("landUse","forest",2,"landUse","forest"))
aModelAction2=myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2,condition=(lambda x: x.value("landUse") != "shrub" and x.value("landUse") != "forest"  )))
aModelAction3=myModel.newModelAction(lambda: Cell.setRandomEntities_withValueNot("landUse","forest",3,"landUse","forest",condition=(lambda x: x.value("landUse") != "shrub") ))

aModelAction4 =myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2))
aModelAction4.addCondition(lambda: myModel.roundNumber()==3) 
aModelAction4.addFeedback(lambda : Cell.setRandomEntities('landUse','grass'))

myModel.timeManager.newModelPhase(aModelAction2)
GameRounds = myModel.newTimeLabel("My Game Time", Qt.white, Qt.black, Qt.black)

# The DashBoard is a widget which permits to create scores.
# Each score is defined by the word indicator.
# You have several methods to calculate indicators like : sum, average, max, min... you can find the complete list by searching the function or by reading the documentation
DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.black)
i1 = DashBoard.addIndicator(Cell,"nbEqualTo",  attribute='landUse',value='forest',color=Qt.black)
# Be careful ! Your value needs to be integrers or float to be logical tested. Only number functions for string values.

myModel.launch() 

sys.exit(monApp.exec_())