import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="About legend (3)")

aGrid=myModel.createGrid(10,10,"square",size=60, gap=2)
aGrid.setValueForCells("landUse","grass")
aGrid.setForX("landUse","forest",1)
aGrid.setForX("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)

myModel.setUpPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.setUpPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

theFirstLegend=myModel.createLegendAdmin()

"""myModel.createPlayer("Player 1")
myModel.createLegendForPlayer(name='Player 1 Legend',aListOfElement='landUse',playerName='Player 1')
# to have the Player 1 view 
myModel.iAm("Name of the player")
# To come back to Admin user status, type the instruction -> myModel.iAm("Admin")
#myModel.iAm("Admin")
"""
myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
