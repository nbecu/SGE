import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1000,850, windowTitle="How to use modelAction - example 4")

Cell=myModel.newCellsOnGrid(10,10,"square",size=60, gap=2)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("Cell -> Farmer","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("Cell -> Global","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})



theFirstLegend=myModel.newLegend()

GameRounds=myModel.newTimeLabel('Rounds&Phases')

DashBoard=myModel.newDashBoard('Les Scores')

scoreB=myModel.newSimVariable('Score Biodiv',0,Qt.GlobalColor.darkGreen)

DashBoard.addIndicator_Nb(Cell,'landUse',"forest","Taille de la foret",(Qt.blue))
DashBoard.addIndicatorOnSimVariable(scoreB)



#MODEL ACTIONS CREATION
aModelAction4=myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","shrub",2))

#POSSIBILITY TO ADD A GENERAL CONDITION TO THE ACTION
aModelAction4.addFeedback(lambda: scoreB.incValue(5)) 

# ADDING MODEL ACTIONS TO THE PHASES
myModel.newModelPhase(aModelAction4)




myModel.launch() 

sys.exit(monApp.exec_())