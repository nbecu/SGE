import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(700,430, windowTitle="Trigger actions with contextual Menu")

Cell=myModel.newCellsOnGrid(5,5,"square",size=60, gap=2,neighborhood="neumann")
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","short grass",10)
Cell.newPov("base","landUse",{"grass":Qt.green,"short grass":Qt.yellow,"forest":Qt.darkGreen})

Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1",defaultSize=30)
Sheeps.newPov("Health","health",{'good':Qt.blue,'bad':Qt.red})
Sheeps.newPov("Hunger","hunger",{'low':Qt.green,'high':Qt.yellow})
Sheeps.setAttributeValueToDisplayInContextualMenu('health')
Sheeps.setAttributeValueToDisplayInContextualMenu('hunger')

Sheeps.setDefaultValues({"health":"bad","hunger":"low"})
m1=Sheeps.newAgentAtCoords(Cell,4,2,{"health":"good","hunger":"high"})
m2=Sheeps.newAgentAtCoords(Cell,5,2)

theFirstLegend=myModel.newLegend()

aTextBox = myModel.newTextBox('',title='Shout box')


Player1=myModel.newPlayer("Player 1")

# By default the game actions are controlled (trigger) through the controlPanel
Player1.addGameAction(myModel.newModifyAction(Cell,{"landUse":"grass"},3))

# For SGModifyAction it is possible to specify setControllerContextualMenu=True to control (trigger) the action through a right clic (contextual menu)
# when setControllerContextualMenu is True, the action is not controlled anymore though the controlPanel
Player1.addGameActions([
    myModel.newModifyAction(Sheeps,{"health":"good"},setControllerContextualMenu=True),
    myModel.newModifyAction(Sheeps,{"health":"bad"},setControllerContextualMenu=True),
    myModel.newModifyAction(Sheeps,{"hunger":"low"},setControllerContextualMenu=True),
    myModel.newModifyAction(Sheeps,{"hunger":"high"},setControllerContextualMenu=True)])

# Same applies for ActivateAction
Player1.addGameActions([
        myModel.newActivateAction(Sheeps,lambda aSheep: aSheep.moveAgent(),setControllerContextualMenu=True,aNameToDisplay='moveAgent (call move of SGAgent)')
        ,
        myModel.newActivateAction(Sheeps,lambda aSheep: eat(aSheep),setControllerContextualMenu=True,aNameToDisplay='eat (call custom method on agent)')
        ,
        myModel.newActivateAction(Sheeps,lambda : shout(),setControllerContextualMenu=True,aNameToDisplay='shout (call custom method in script)')
        ])

def eat(aSheep):
    if aSheep.cell.value('landUse') == 'grass':
        aSheep.setValue('health','good')
        aSheep.setValue('hunger','low')
        aSheep.cell.setValue('landUse','short grass')
    else: 
        aTextBox.addText('cannot eat here')
def shout():
    aTextBox.addText('meh!!!')

Player1ControlPanel=Player1.newControlPanel("Actions du Joueur 1")
userSelector=myModel.newUserSelector()

myModel.newPlayPhase('Phase 1', [Player1])
myModel.newModelPhase(lambda: Cell.setRandomEntities_withValue("landUse","grass",2,"landUse","short grass"),auto_forward=True,message_auto_forward=False)

myModel.launch() 
sys.exit(monApp.exec_())