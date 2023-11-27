import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1000,700, windowTitle="A simulation/game with one agent")

Cell=myModel.newCellsOnGrid(10,10,"square",size=60, gap=2)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("Cell -> Farmer","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("Cell -> Global","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})


# Moutons=myModel.newAgentSpecies("Moutons","circleAgent",{"health":{"good","bad"},"hunger":{"good","bad"}})
# Moutons=myModel.newAgentSpecies("Moutons","circleAgent",uniqueColor=Qt.yellow)

# Moutons.newPov("Moutons -> Health","health",{'good':Qt.blue,'bad':Qt.red})
# Moutons.newPov("Moutons -> Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})


# m1=myModel.newAgent(aGrid,Moutons,3,7)
# m2=myModel.newAgent(aGrid,Moutons,6,3)
# m2.setValue('health','good')
# m1.setValue('health','bad')
# m2.setValue('hunger','good')
# m1.setValue('hunger','bad')
# #print(myModel.AgentSpecies)

# agent_list = []
# for animal, sub_dict in myModel.agentSpecies.items():
#     for agent_id, agent_dict in sub_dict['AgentList'].items():
#         agent_list.append(agent_dict['AgentObject'])

theFirstLegend=myModel.newLegend()

GameRounds=myModel.newTimeLabel('Rounds&Phases')
# myModel.timeManager.newGamePhase('Phase 1', 'player1')


# myModel.timeManager.newModelPhase(lambda: Cell.setRandomEntities("landUse","shrub",3))

# myModel.timeManager.newModelPhase(
#     # lambda: Cell.setRandomEntities("landUse","shrub",3),
#     # lambda: len(aGrid.getCellOfValue({'landUse':'forest'})) > 15,
#     lambda: Cell.setRandomEntities("landUse","forest"))
# myModel.timeManager.newModelPhase(
#     lambda: Cell.setRandomEntities("landUse","shrub",3),
#     )
myModel.timeManager.newModelPhase(
    
    [
    lambda: Cell.setRandomEntities("landUse","forest"),
    lambda: Cell.setRandomEntities("landUse","shrub",3)]
    )



myModel.launch() 

sys.exit(monApp.exec_())