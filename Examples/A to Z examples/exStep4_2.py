import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="Create a empty ControlPanel")

aGrid=myModel.newGrid(10,10,"square",size=60, gap=2,name='mygrid')
aGrid.setCells("landUse","grass")
aGrid.setCells_withColumn("landUse","forest",1)
aGrid.setCells_withColumn("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)

myModel.newPov("ICanSeeSchrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1",{"health":{"good","bad"},"hunger":{"good","bad"}})
Sheeps.newPov("Sheeps -> Health","health",{'good':Qt.blue,'bad':Qt.red})
Sheeps.newPov("Sheeps -> Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})
m1=myModel.newAgentAtCoords(aGrid,Sheeps,1,1,adictAttributes={"health":"good","hunger":"bad"})
m2=myModel.newAgentAtCoords(aGrid,Sheeps,5,1)

theFirstLegend=myModel.newLegendAdmin()
# You can also create Players. They are users who need GameActions to interact with the Model
# create a player
Player1=myModel.newPlayer("Player 1")
# create a ControlPanel for this player, according to their actions
Player1Legend=Player1.newControlPanel("Actions du Joueur 1",showAgentsWithNoAtt=True)


# if you want to start the application as Player 1 :
myModel.currentPlayer='Player 1'


myModel.launch() 

sys.exit(monApp.exec_())
