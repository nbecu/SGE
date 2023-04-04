import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1000,700, windowTitle="A simulation/game with agents", typeOfLayout ="grid")

aGrid=myModel.createGrid(10,10,"square",size=60, gap=2)
aGrid.setValueForCells("landUse","grass")
aGrid.setForX("landUse","forest",1)
aGrid.setForX("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)

myModel.setUpPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.setUpPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

# Here, a "type" of agent is called a species.
# To create a species, it needs : a name, a shape and a dict of attributs with values.
Moutons=myModel.newAgentSpecies("Moutons","circleAgent",{"health":{"good","bad"},"hunger":{"good","bad"}})

# For each attribute, you can set up points of view with colors :
Moutons.setUpPov("Moutons -> Health","health",{'good':Qt.blue,'bad':Qt.red})
Moutons.setUpPov("Moutons -> Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})

# You can now create agents from its species and place them on a particular cell, or random by giving None values :
m1=myModel.newAgent(aGrid,Moutons,3,7)
m2=myModel.newAgent(aGrid,Moutons,None,None)

# Don't forget to give values to your agent attributes !
m2.updateAgentValue('health','good')
m1.updateAgentValue('health','bad')
m2.updateAgentValue('hunger','good')
m1.updateAgentValue('hunger','bad')

theFirstLegend=myModel.createLegendAdmin()

GameRounds=myModel.addTimeLabel('Rounds&Phases')
myModel.timeManager.addGamePhase('Phase 1')
myModel.timeManager.addGamePhase('Phase 2')
myModel.timeManager.addGamePhase('Phase 3')
myModel.timeManager.addGamePhase('Phase 4')
myModel.timeManager.addGamePhase('Phase 5')


myModel.iAm("Admin")

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
