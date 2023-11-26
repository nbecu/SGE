import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1000,850, windowTitle="A simulation/game with one agent")

Cell=myModel.newGrid(10,10,"square",size=60, gap=2)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("Cell -> Farmer","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("Cell -> Global","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})



theFirstLegend=myModel.newLegend()

GameRounds=myModel.newTimeLabel('Rounds&Phases')

DashBoard=myModel.newDashBoard('Les Scores','withButton',borderColor=Qt.black,)
i1=DashBoard.addIndicator_Nb('cell','landUse',"forest","Taille de la foret",(Qt.blue))
# i1.setUpdateAtEachRound(True)
DashBoard.showIndicators()


#CREATIONS DE MODEL ACTIONS
aModelAction4=myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","shrub",2))
    #POSSIBILITE d'AJOUTER UN FEEDBACK  A l'ACTION
aModelAction4.addFeedback(lambda: i1.setResult(i1.result + 5)) 
# TODO Trouver un autre exemple car le modeleler n'a pas le droit d'intervenir sur le setResult d'un indicateur (c'est une méthdoe prviée)


# AJOUT DES MODEL ACTIONS DANS LES PHASE
myModel.timeManager.newModelPhase(aModelAction4)




myModel.launch() 

sys.exit(monApp.exec_())