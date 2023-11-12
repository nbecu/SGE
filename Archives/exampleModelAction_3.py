import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1000,700, windowTitle="A simulation/game with one agent")

Cell=myModel.newGrid(10,10,"square",size=60, gap=2)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("Cell -> Farmer","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("Cell -> Global","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})



theFirstLegend=myModel.newLegend()

GameRounds=myModel.newTimeLabel('Rounds&Phases')

#CREATIONS DE MODEL ACTIONS
    #TROIS ECRITURES POSSIBLES
aModelAction1=myModel.newModelAction(lambda: Cell.setRandomEntities_withValueNot("landUse","forest",2,"landUse","forest"))
aModelAction2=myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2,condition=(lambda x: x.value("landUse") != "shrub" and x.value("landUse") != "forest"  )))
aModelAction3=myModel.newModelAction(lambda: Cell.setRandomEntities_withValueNot("landUse","forest",3,"landUse","forest",condition=(lambda x: x.value("landUse") != "shrub") ))

    #POSSIBILITE d'AJOUTER UNE CONDITION GENERALE A l'ACTION
aModelAction4 =myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2))
aModelAction4.addCondition(lambda: myModel.round()==3) 

aModelAction5 =myModel.newModelAction((lambda: Cell.setRandomEntities("landUse","forest",2)), conditions= (lambda: myModel.round()==3) )
 #cette instruction ne marche pas car y'a ne embrouille dans conditions qui est appliqué sur toutes les modelActions  

# AJOUT DES MODEL ACTIONS DANS LES PHASE
myModel.timeManager.newModelPhase(aModelAction2)





myModel.launch() 

sys.exit(monApp.exec_())