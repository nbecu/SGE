import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *


monApp=QtWidgets.QApplication([])

myModel=SGModel(1000,700, windowTitle="A simulation/game with one agent", typeOfLayout ="grid")

aGrid=myModel.newGrid(10,10,"square",size=60, gap=2,name='grid1')
aGrid.setCells("landUse","grass")
aGrid.setCells_withColumn("landUse","forest",1)
aGrid.setCells_withColumn("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)


myModel.newPov("Cell -> Farmer","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.newPov("Cell -> Global","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})


Sheeps=myModel.newAgentSpecies("Sheeps","circleAgent",{"health":{"good","bad"},"hunger":{"good","bad"}})
Sheeps.newPov("Sheeps -> Health","health",{'good':Qt.blue,'bad':Qt.red})
Sheeps.newPov("Sheeps -> Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})



a1=myModel.newAgent(aGrid,Sheeps,3,7)
# a2=myModel.newAgent(aGrid,Sheeps,6,3)

a1.setValueAgent('health','bad')
a1.setValueAgent('hunger','bad')

# a2.setValueAgent('hunger','good')
# a2.setValueAgent('health','good')



# m1.moveAgent(aGrid,numberOfMovement=3)

Cows=myModel.newAgentSpecies("Cows","squareAgent",{"health":{"good","bad"}},18)
Cows.newPov("Cows -> Health","health",{'good':Qt.blue,'bad':Qt.red})
v1=myModel.newAgent(aGrid,Cows,2,2)
v1.setValueAgent('health','good')
# print(myModel.agentSpecies)

theFirstLegend=myModel.newLegendAdmin()


GameRounds=myModel.newTimeLabel()
myModel.timeManager.newGamePhase('Phase 1',None, [lambda: a1.moveAgent(aGrid,numberOfMovement=3)])
myModel.timeManager.newGamePhase('Phase 2',None,[lambda: myModel.deleteAgent('1')])

MessageBox=myModel.newTextBox()

#myModel.iAm("Admin")

myModel.launch() 

sys.exit(monApp.exec_())
