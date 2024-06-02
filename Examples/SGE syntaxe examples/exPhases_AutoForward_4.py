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
Sheeps.newPov("Sheeps -> Health","health",{'good':Qt.blue,'bad':Qt.red})
Sheeps.newPov("Sheeps -> Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})
m1=Sheeps.newAgentAtCoords(Cell,1,1,{"health":"good","hunger":"bad"})
m2=Sheeps.newAgentAtCoords(Cell,5,1)

theFirstLegend=myModel.newLegend()


Player1=myModel.newPlayer("Player 1")
Player1.addGameAction(myModel.newUpdateAction('Cell',{"landUse":"grass"},3))
Player1Legend=Player1.newControlPanel("Actions du Joueur 1",showAgentsWithNoAtt=True)


p1=myModel.timeManager.newGamePhase('Game Phase 1', [Player1])
p1.showMessageBoxAtStart="New round. You can play!"

p2= myModel.timeManager.newModelPhase([lambda: Cell.setRandomEntities("landUse","forest"),lambda: Cell.setRandomEntities("landUse","shrub",3)], name = 'Model Phase 1')
# comment or not
p2.autoForwardOn=True 
p2.messageAutoForward=False
p2.showMessageBoxAtStart=True

aModelAction1=myModel.newModelAction(lambda: Cell.setRandomEntities_withValueNot("landUse","forest",2,"landUse","forest"))
aModelAction2=myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2,condition=(lambda x: x.value("landUse") != "shrub" and x.value("landUse") != "forest"  )))
aModelAction3=myModel.newModelAction(lambda: Cell.setRandomEntities_withValueNot("landUse","forest",3,"landUse","forest",condition=(lambda x: x.value("landUse") != "shrub") ))

aModelAction4 =myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2))
aModelAction4.addCondition(lambda: myModel.roundNumber()==3) 

aModelAction4.addFeedback(lambda : Cell.setRandomEntities('landUse','grass'))

#Choose one or the other
# myModel.timeManager.newModelPhase(aModelAction2, name = 'Model Phase 2')
myModel.timeManager.newModelPhase(aModelAction2, name = 'Model Phase 2',
                                  autoForwardOn=True,
                                  messageAutoForward=False,
                                  showMessageBoxAtStart="The forest will now grow"
)


GameRounds = myModel.newTimeLabel("My Game Time", Qt.white, Qt.black, Qt.black)
userSelector=myModel.newUserSelector()


myModel.launch() 

sys.exit(monApp.exec_())