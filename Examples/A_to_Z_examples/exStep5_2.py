import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="Create your ModelPhase")

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

userSelector=myModel.newUserSelector()


myModel.newPlayPhase('Phase 1', [Player1])
# SGE is also able to have ModelPhase : this phase includes model activities/events
myModel.newModelPhase(
    [lambda: Cell.setRandomEntities("landUse","shrub",3),
    lambda: Cell.setRandomEntities("landUse","forest")] #If no number of entities is defined, it will pick 1 entity by default
    )
# this Model Phase has an Action. THis Action will randomly update 1 cell to landUse forest and 3 cells to shrub
# and will be performed after every Phase 1
myModel.launch() 

sys.exit(monApp.exec_())