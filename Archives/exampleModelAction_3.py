import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1000,700, windowTitle="A simulation/game with one agent")

aGrid=myModel.newGrid(10,10,"square",size=60, gap=2)
aGrid.setCells("landUse","grass")
aGrid.setCells_withColumn("landUse","forest",1)
aGrid.setCells_withColumn("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)

myModel.newPov("Cell -> Farmer","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.newPov("Cell -> Global","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})



theFirstLegend=myModel.newLegendAdmin()

GameRounds=myModel.newTimeLabel('Rounds&Phases')

#CREATIONS DE MODEL ACTIONS
    #TROIS ECRITURES POSSIBLES
aModelAction1=myModel.newModelAction(lambda: aGrid.setRandomCells_withValueNot("landUse","forest",2,"landUse","forest"))
aModelAction2=myModel.newModelAction(lambda: aGrid.setRandomCells("landUse","forest",2,condition=(lambda x: x.value("landUse") != "shrub" and x.value("landUse") != "forest"  )))
aModelAction3=myModel.newModelAction(lambda: aGrid.setRandomCells_withValueNot("landUse","forest",3,"landUse","forest",condition=(lambda x: x.value("landUse") != "shrub") ))

    #POSSIBILITE d'AJOUTER UNE CONDITION GENERALE A l'ACTION
aModelAction4 =myModel.newModelAction(lambda: aGrid.setRandomCells("landUse","forest",2))
aModelAction4.addCondition(lambda: myModel.getCurrentRound()==3) 

aModelAction5 =myModel.newModelAction((lambda: aGrid.setRandomCells("landUse","forest",2)), conditions= (lambda: myModel.getCurrentRound()==3) )
 #cette instruction ne marche pas car y'a ne embrouille dans conditions qui est appliqué sur toutes les modelActions  

# AJOUT DES MODEL ACTIONS DANS LES PHASE
myModel.timeManager.newModelPhase(aModelAction2)





myModel.launch() 

sys.exit(monApp.exec_())