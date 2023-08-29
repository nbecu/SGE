import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1000,850, windowTitle="A simulation/game with one agent")

aGrid=myModel.newGrid(10,10,"square",size=60, gap=2)
aGrid.setCells("landUse","grass")
aGrid.setCells_withColumn("landUse","forest",1)
aGrid.setCells_withColumn("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)

myModel.newPov("Cell -> Farmer","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.newPov("Cell -> Global","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})



theFirstLegend=myModel.newLegendAdmin()

GameRounds=myModel.newTimeLabel('Rounds&Phases')

DashBoard=myModel.newDashBoard('Les Scores','withButton',borderColor=Qt.black,)
i1=DashBoard.addIndicator_Nb('cell','landUse',"forest","Taille de la foret",(Qt.blue))
# i1.setUpdateAtEachRound(True)
DashBoard.showIndicators()

aTextBox=myModel.newTextBox(title='La foret regresse petit à petit')


#CREATIONS DE MODEL ACTIONS
aModelAction1=myModel.newModelAction(lambda: aGrid.setRandomCells("landUse","shrub",2), feedBacks=(lambda: i1.setResult(i1.result -1))) 

aModelAction2=myModel.newModelAction(lambda: aGrid.setRandomCells_withValueNot("landUse","shrub",2,"landUse","shrub"))
aFeedbackAction=myModel.newModelAction(lambda: aGrid.setRandomCells_withValueNot("landUse","forest",5,"landUse","forest"))
aFeedbackAction.addModelAction(lambda: aTextBox.addText("Replantation (+ 5 forets)",toTheLine=True)) #Probleme -> ca ne rafraichit pas le texte
aFeedbackAction.addCondition(lambda: i1.result <15)                                     
aModelAction2.addFeedback(aFeedbackAction) 


# AJOUT DES MODEL ACTIONS DANS LES PHASE
myModel.timeManager.newModelPhase([(lambda:i1.updateText()),aModelAction2])

myModel.launch() 

sys.exit(monApp.exec_())