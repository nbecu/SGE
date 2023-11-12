import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1000,700, windowTitle="A simulation/game with one agent", typeOfLayout ="grid")

Cell=myModel.newGrid(10,10,"square",size=60, gap=2,name='grid1')
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
m2=myModel.newAgent(aGrid,Moutons,6,3)
m1.setValue('health','bad')
m1.setValue('hunger','bad')
m2.setValue('hunger','good')
m2.setValue('health','good')



# addding a second specie
Vaches=myModel.newAgentSpecies("Vaches","squareAgent",{"health":{"good","bad"}},18)
Vaches.newPov("Vaches -> Health","health",{'good':Qt.blue,'bad':Qt.red})
v1=myModel.newAgent(aGrid,Vaches,2,2)
v1.setValue('health','good')

theFirstLegend=myModel.newLegend()

GameRounds=myModel.newTimeLabel('Rounds&Phases')
myModel.timeManager.newGamePhase('début',
                                 None,
                                 [lambda: m1.setValue('health','good'),
                                 lambda: v1.setValue('health','bad')])
myModel.timeManager.newGamePhase('fin',
                                  None,
                                 [lambda: m1.setValue('health','bad'),
                                lambda: v1.setValue('health','good')])


myModel.iAm("Admin")

myModel.launch() 

sys.exit(monApp.exec_())
