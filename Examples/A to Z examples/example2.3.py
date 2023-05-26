import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="About legend (3)")

aGrid=myModel.newGrid(10,10,"square",size=60, gap=2)
aGrid.setCells("landUse","grass")
aGrid.setCells_withColumn("landUse","forest",1)
aGrid.setCells_withColumn("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)

myModel.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

theFirstLegend=myModel.newLegendAdmin()

Player1=myModel.newPlayer("Player 1")
Player1.addGameAction(myModel.createUpdateAction('Cell',3,{"landUse":"grass"}))
Player1Legend=Player1.newLegendPlayer("Actions du Joueur 1",showAgents=True)

# Create a second player
Player2=myModel.newPlayer("Player 2")
Player2.addGameAction(myModel.createUpdateAction("Cell",1,{"landUse":"forest"}))
Player2Legend=Player2.newLegendPlayer("Actions du Joueur 2")

userSelector=myModel.newUserSelector()

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
