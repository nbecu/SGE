import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1000,700, windowTitle="A simulation/game with agents", typeOfLayout ="grid")

Cell=myModel.newGrid(10,10,"square",size=60, gap=2)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

# Here, a "type" of agent is called a species.
# To create a species, it needs : a name, a shape and a dict of attributs with values.
Moutons=myModel.newAgentSpecies("Moutons","circleAgent",{"health":{"good","bad"},"hunger":{"good","bad"}})

# For each attribute, you can set up points of view with colors :
Moutons.newPov("Moutons -> Health","health",{'good':Qt.blue,'bad':Qt.red})
Moutons.newPov("Moutons -> Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})

# You can now create agents from its species and place them on a particular cell, or random by giving None values :
m1=myModel.newAgent(aGrid,Moutons,3,7)
m2=myModel.newAgent(aGrid,Moutons,None,None)

# Don't forget to give values to your agent attributes !
m2.setValue('health','good')
m1.setValue('health','bad')
m2.setValue('hunger','good')
m1.setValue('hunger','bad')

theFirstLegend=myModel.newLegend()

GameRounds=myModel.newTimeLabel('Rounds&Phases')
myModel.timeManager.newGamePhase('Phase 1')
myModel.timeManager.newGamePhase('Phase 2')
myModel.timeManager.newGamePhase('Phase 3')
myModel.timeManager.newGamePhase('Phase 4')
myModel.timeManager.newGamePhase('Phase 5')


myModel.iAm("Admin")

myModel.launch() 

sys.exit(monApp.exec_())
