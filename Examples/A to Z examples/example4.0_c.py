import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1000,700, windowTitle="A simulation/game with one agent", typeOfLayout ="grid")

aGrid=myModel.createGrid(10,10,"square",size=60, gap=2,name='grid1')
aGrid.setValueForCells({"landUse":"grass"})
aGrid.setForX({"landUse":"forest"},1)
aGrid.setForX({"landUse":"forest"},2)
aGrid.setForRandom({"landUse":"shrub"},10)

myModel.setUpPov("Cell -> Farmer","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.setUpPov("Cell -> Global","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})


Moutons=myModel.newAgentSpecies("Moutons","circleAgent",{"health":{"good","bad"},"hunger":{"good","bad"}})
Moutons.setUpPov("Moutons -> Health","health",{'good':Qt.blue,'bad':Qt.red})
Moutons.setUpPov("Moutons -> Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})


m1=myModel.newAgent(aGrid,Moutons,3,7)
m2=myModel.newAgent(aGrid,Moutons,6,3)
m2.updateAgentValue('health','good')
m1.updateAgentValue('health','bad')
m2.updateAgentValue('hunger','good')
m1.updateAgentValue('hunger','bad')


theFirstLegend=myModel.createLegendAdmin()

GameRounds=myModel.addTimeLabel('Rounds&Phases')
myModel.timeManager.addGamePhase('début')
myModel.timeManager.addGamePhase('milieu',
                                 None,
                                 [lambda: m1.updateAgentValue('health','good')])
myModel.timeManager.addGamePhase('fin',
                                  None,
                                 [lambda: m1.updateAgentValue('health','bad')])


myModel.iAm("Admin")

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
