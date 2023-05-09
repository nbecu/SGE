import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *


monApp=QtWidgets.QApplication([])

myModel=SGModel(1000,700, windowTitle="A simulation/game with one agent", typeOfLayout ="grid")

aGrid=myModel.newGrid(10,10,"square",size=60, gap=2,name='grid1')
aGrid.setValueCell("landUse","grass")
aGrid.setForX("landUse","forest",1)
aGrid.setForX("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)


myModel.newPov("Cell -> Farmer","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.newPov("Cell -> Global","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})


Moutons=myModel.newAgentSpecies("Moutons","circleAgent",{"health":{"good","bad"},"hunger":{"good","bad"}})
Moutons.newPov("Moutons -> Health","health",{'good':Qt.blue,'bad':Qt.red})
Moutons.newPov("Moutons -> Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})



m1=myModel.newAgent(aGrid,Moutons,3,7)
# m2=myModel.newAgent(aGrid,Moutons,6,3)

m1.setValueAgent('health','bad')
m1.setValueAgent('hunger','bad')

# m2.setValueAgent('hunger','good')
# m2.setValueAgent('health','good')



# m1.moveAgent(aGrid,numberOfMovement=3)

Vaches=myModel.newAgentSpecies("Vaches","squareAgent",{"health":{"good","bad"}},18)
Vaches.newPov("Vaches -> Health","health",{'good':Qt.blue,'bad':Qt.red})
v1=myModel.newAgent(aGrid,Vaches,2,2)
v1.setValueAgent('health','good')
# print(myModel.agentSpecies)

theFirstLegend=myModel.newLegendAdmin()


GameRounds=myModel.newTimeLabel()
myModel.timeManager.newGamePhase('Phase 1',None, [lambda: m1.moveAgent(aGrid,numberOfMovement=3)])
myModel.timeManager.newGamePhase('Phase 2',None,[lambda: myModel.deleteAgent(1)])

MessageBox=myModel.newMessageBox()

myModel.iAm("Admin")

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
