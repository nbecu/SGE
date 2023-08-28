import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="Create your ModelActions")

aGrid=myModel.newGrid(10,10,"square",size=60, gap=2)
aGrid.setCells("landUse","grass")
aGrid.setCells_withColumn("landUse","forest",1)
aGrid.setCells_withColumn("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)

myModel.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

theFirstLegend=myModel.newLegendAdmin()


Player1=myModel.newPlayer("Player 1")
Player1.addGameAction(myModel.newUpdateAction('Cell',3,{"landUse":"grass"}))
Player1Legend=Player1.newControlPanel("Actions du Joueur 1",showAgentsWithNoAtt=True)

userSelector=myModel.newUserSelector()


myModel.timeManager.newGamePhase('Phase 1', [Player1])
myModel.timeManager.newModelPhase([lambda: aGrid.setRandomCell("landUse","forest"),lambda: aGrid.setRandomCells("landUse","shrub",3)])

# You also can, with the same scheme as GamePhase, first create ModelActions and place them after on a ModelPhase
# MODEL ACTIONS CREATION
    # 3 POSSIBLE WAYS
aModelAction1=myModel.newModelAction(lambda: aGrid.setRandomCells_withValueNot("landUse","forest",2,"landUse","forest"))
aModelAction2=myModel.newModelAction(lambda: aGrid.setRandomCells("landUse","forest",2,condition=(lambda x: x.value("landUse") != "shrub" and x.value("landUse") != "forest"  )))
aModelAction3=myModel.newModelAction(lambda: aGrid.setRandomCells_withValueNot("landUse","forest",3,"landUse","forest",condition=(lambda x: x.value("landUse") != "shrub") ))

    # You also can add a general condition to your action
aModelAction4 =myModel.newModelAction(lambda: aGrid.setRandomCells("landUse","forest",2))
aModelAction4.addCondition(lambda: myModel.getCurrentRound()==3) 

    # You can add a general feedback :
aModelAction4.addFeedback(lambda : aGrid.setRandomCell('landUse','grass'))

# Don't forget to add your Actions to a ModelPhase!
myModel.timeManager.newModelPhase(aModelAction2)


myModel.launch() 

sys.exit(monApp.exec_())