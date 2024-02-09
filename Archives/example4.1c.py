import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *


monApp=QtWidgets.QApplication([])

myModel=SGModel(1000,700, windowTitle="Adding agents", typeOfLayout ="grid")

Cell=myModel.newCellsOnGrid(10,10,"square",size=60, gap=2)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)


Cell.newPov("Cell -> Farmer","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("Cell -> Global","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})


Moutons=myModel.newAgentSpecies("Moutons","circleAgent",{"health":{"good","bad"},"hunger":{"good","bad"}})
Moutons.newPov("Moutons -> Health","health",{'good':Qt.blue,'bad':Qt.red})
Moutons.newPov("Moutons -> Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})

m1=myModel.newAgent(aGrid,Moutons,3,7)
m1.setValue('health','bad')
m1.setValue('hunger','bad')

Vaches=myModel.newAgentSpecies("Vaches","squareAgent",{"health":{"good","bad"}},18)
Vaches.newPov("Vaches -> Health","health",{'good':Qt.blue,'bad':Qt.red})

theFirstLegend=myModel.newLegend()

GameRounds=myModel.newTimeLabel()
myModel.timeManager.newGamePhase(
    'Adding 1 agent',
    None,
    lambda: myModel.addAgent(aGrid,Vaches,{'health':'good'},numberOfAgent=1)    )

myModel.launch() 

sys.exit(monApp.exec_())
