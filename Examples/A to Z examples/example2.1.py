import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="About legend (2)")

aGrid=myModel.newGrid(10,10,"square",size=60, gap=2,name='mygrid')
aGrid.setCells("landUse","grass")
aGrid.setCells_withColumn("landUse","forest",1)
aGrid.setCells_withColumn("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)

myModel.newPov("ICanSeeSchrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

theFirstLegend=myModel.newLegendAdmin()
# create a player
Player1=myModel.newPlayer("Player 1")
# create a ControlPanel for this player, according to their actions
Player1.addGameAction(myModel.createUpdateAction('Cell',3,{"landUse":"grass"}))
Player1Legend=Player1.newLegendPlayer("Actions du Joueur 1",showAgents=True)


# to have the Player 1 view 
myModel.currentPlayer='Player 1'


myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
