import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1000,700, windowTitle="A simulation/game with one agent")

aGrid=myModel.newGrid(10,10,"square",size=60, gap=2)
aGrid.setCells("landUse","grass")
aGrid.setCells_withColumn("landUse","forest",1)
aGrid.setCells_withColumn("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)

myModel.newPov("Cell -> Farmer","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.newPov("Cell -> Global","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})


Moutons=myModel.newAgentSpecies("Moutons","circleAgent",{"health":{"good","bad"},"hunger":{"good","bad"}})
Moutons.newPov("Moutons -> Health","health",{'good':Qt.blue,'bad':Qt.red})
Moutons.newPov("Moutons -> Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})


m1=myModel.newAgent(aGrid,Moutons,3,7)
m2=myModel.newAgent(aGrid,Moutons,6,3)
m2.setValueAgent('health','good')
m1.setValueAgent('health','bad')
m2.setValueAgent('hunger','good')
m1.setValueAgent('hunger','bad')
#print(myModel.AgentSpecies)

agent_list = []
for animal, sub_dict in myModel.agentSpecies.items():
    for agent_id, agent_dict in sub_dict['AgentList'].items():
        agent_list.append(agent_dict['AgentObject'])

#print(agent_list)
theFirstLegend=myModel.newLegendAdmin()

GameRounds=myModel.newTimeLabel('Rounds&Phases')

# myModel.timeManager.newModelPhase(lambda: aGrid.setRandomCells("landUse","shrub",3))

myModel.timeManager.newModelPhase(
    lambda: aGrid.setRandomCells("landUse","shrub",3),
    lambda: len(aGrid.getCellOfValue({'landUse':'forest'})) > 15)


# myModel.timeManager.newGamePhase('Phase 2',
#                                  None,
#                                  [lambda: aGrid.setRandomCell("landUse","forest")])



myModel.iAm("Admin")

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
