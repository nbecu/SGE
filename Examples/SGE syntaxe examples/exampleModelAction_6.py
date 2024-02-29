import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1000,850, windowTitle="A simulation/game with one agent")

Cell=myModel.newCellsOnGrid(10,10,"square",size=60, gap=2)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("Cell -> Farmer","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("Cell -> Global","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})



theFirstLegend=myModel.newLegend()

GameRounds=myModel.newTimeLabel('Rounds&Phases')

DashBoard=myModel.newDashBoard('Les Scores','withButton',borderColor=Qt.black,)
scoreB=myModel.newSimVariable('Score Biodiv',0,Qt.GlobalColor.darkGreen)
DashBoard.addIndicatorOnSimVariable(scoreB)

aTextBox=myModel.newTextBox(title='La foret regresse petit à petit')


#MODEL ACTIONS CREATION
aModelAction1=myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","shrub",2), feedbacks=(lambda: scoreB.decValue(1)))


aModelAction2=myModel.newModelAction(lambda: Cell.setRandomEntities_withValueNot("landUse","shrub",2,"landUse","shrub"))
aFeedbackAction=myModel.newModelAction(lambda: Cell.setRandomEntities_withValueNot("landUse","forest",5,"landUse","forest"))
aFeedbackAction.addModelAction(lambda: aTextBox.addText("Replantation (+ 5 forets)",toTheLine=True)) # TODO : Probleme -> ca ne rafraichit pas le texte
aFeedbackAction.addCondition(lambda: scoreB.value <15)                                     
aModelAction2.addFeedback(aFeedbackAction) 


# ADDING MODEL ACTIONS TO THE PHASES
myModel.timeManager.newModelPhase(aModelAction1, 'Model action 1')
myModel.timeManager.newModelPhase(aModelAction2, 'Model action 2')

myModel.launch() 

sys.exit(monApp.exec_())