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

myModel.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

theFirstLegend=myModel.newLegendAdmin()
"""# create a player
myModel.createPlayer("Player 1")
# create a legend for this player, according to the POVs
#Player1Leg=myModel.createLegendForPlayer("Player1Legend",{"mygrid":{'povLandUse':{"grass":Qt.green}}},"Player 1")
#Player1Leg.addDeleteButton('Delete')
"""

# to have the Player 1 view 
#myModel.iAm("Player 1")
#myModel.iAm("Admin")

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
