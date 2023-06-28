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
# you can add GameAction to your Player here.
# This is a Update Action : the player can update 3 cells to landUse grass
Player1.addGameAction(myModel.newUpdateAction('Cell',3,{"landUse":"grass"}))
Player1Legend=Player1.newLegendPlayer("Actions du Joueur 1",showAgents=True)

userSelector=myModel.newUserSelector()

myModel.launch() 

sys.exit(monApp.exec_())
