import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="add a TimeLabel")

Cell=myModel.newCellsOnGrid(10,10,"square",size=40, gap=2)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

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
Player1ControlPanel=Player1.newControlPanel("Actions du Joueur 1",showAgentsWithNoAtt=True)


myModel.newPlayPhase('Game Phase 1', [Player1])
p2= myModel.newModelPhase([lambda: Cell.setRandomEntities("landUse","forest"),lambda: Cell.setRandomEntities("landUse","shrub",3)], name = 'Model Phase 1')
# comment or not
p2.auto_forward=True 
p2.message_auto_forward=False

aModelAction1=myModel.newModelAction(lambda: Cell.setRandomEntities_withValueNot("landUse","forest",2,"landUse","forest"))
aModelAction2=myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2,condition=(lambda x: x.value("landUse") != "shrub" and x.value("landUse") != "forest"  )))
aModelAction3=myModel.newModelAction(lambda: Cell.setRandomEntities_withValueNot("landUse","forest",3,"landUse","forest",condition=(lambda x: x.value("landUse") != "shrub") ))

aModelAction4 =myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2))
aModelAction4.addCondition(lambda: myModel.roundNumber()==3) 

aModelAction4.addFeedback(lambda : Cell.setRandomEntities('landUse','grass'))

#Choose one or the other
# myModel.newModelPhase(aModelAction2, name = 'Model Phase 2')
myModel.newModelPhase(aModelAction2, name = 'Model Phase 2',auto_forward=True,message_auto_forward="The land use has evolve. Continue to next turn")


GameRounds = myModel.newTimeLabel("My Game Time", Qt.white, Qt.black, Qt.black)
userSelector=myModel.newUserSelector()


myModel.launch() 

sys.exit(monApp.exec_())