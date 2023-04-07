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
m2=myModel.newAgent(aGrid,Moutons,6,3)
m1.updateAgentValue('health','bad')
m1.updateAgentValue('hunger','bad')
m2.updateAgentValue('hunger','good')
m2.updateAgentValue('health','good')



Vaches=myModel.newAgentSpecies("Vaches","squareAgent",{"health":{"good","bad"}},18)
Vaches.newPov("Vaches -> Health","health",{'good':Qt.blue,'bad':Qt.red})
v1=myModel.newAgent(aGrid,Vaches,2,2)
v1.updateAgentValue('health','good')

theFirstLegend=myModel.newLegendAdmin()

# Testing other programatic changes on the cell and agents
GameRounds=myModel.newTimeLabel('Rounds&Phases')
myModel.timeManager.newGamePhase('début')
myModel.timeManager.newGamePhase('milieu',None,
                                 [lambda: m1.updateAgentValue('health','good'),
                                 lambda: v1.updateAgentValue('health','bad')])
myModel.timeManager.newGamePhase('fin',None,
                                 [lambda: m1.updateAgentValue('health','bad'),
                                lambda: v1.updateAgentValue('health','good')])
myModel.timeManager.newGamePhase('fin2',None,
                                    [lambda: aGrid.setForRandom({"landUse":"shrub"},20)],[lambda: myModel.getTimeManager().currentRound == 3 ])
myModel.timeManager.newGamePhase('fin2',None,
                                    [lambda: aGrid.setForRandom({"landUse":"forest"},6)],[lambda: myModel.getTimeManager().verifNumberOfRound(5) ])
# myModel.timeManager.newGamePhase('fin des fins',None,
#                                     [lambda: aGrid.addAgentOnValue("Moutons",{"health":"bad"})])      --->  Does not work
# myModel.timeManager.newGamePhase('fin des fins',None,
#                                     [lambda: aGrid.moveRandomlyAgent("Moutons")])   --->  Does not work
# myModel.timeManager.newGamePhase('fin des fins',None,
#                                     [lambda: aGrid.deleteAgent("Moutons")])  --->  Does not work


# To test later
# [lambda: myModel.getGameSpace("basicGrid").makeEvolve(["Forest"])
# [lambda: myModel.getGameSpace("basicGrid").makeDecrease(["sea"])])


myModel.iAm("Admin")

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
