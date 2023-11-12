import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1000,700, windowTitle="A simulation/game with one agent")

Cell=myModel.newGrid(10,10,"square",size=60, gap=2)
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
m2.setValue('health','good')
m1.setValue('health','bad')
m2.setValue('hunger','good')
m1.setValue('hunger','bad')
#print(myModel.AgentSpecies)

agent_list = []
for animal, sub_dict in myModel.agentSpecies.items():
    for agent_id, agent_dict in sub_dict['AgentList'].items():
        agent_list.append(agent_dict['AgentObject'])

#print(agent_list)
theFirstLegend=myModel.newLegend()

GameRounds=myModel.newTimeLabel('Rounds&Phases')
myModel.timeManager.newGamePhase('Phase 1')
myModel.timeManager.newGamePhase('Phase 2',
                                 None,
#                               trying to specify a condition of application of the setForRandom --> but it doesn't work
                                 [lambda: aGrid.setForRandom({"landUse":"shrub"},3)],[lambda aCell: aCell.checkValue({"landUse":"grass"})])
                                 
myModel.timeManager.newGamePhase('Phase 3',
                                 None,
                                 [lambda: aGrid.setForRandom({"landUse":"forest"},1)])


myModel.iAm("Admin")

myModel.launch() 

sys.exit(monApp.exec_())
