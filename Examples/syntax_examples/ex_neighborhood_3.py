import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(400,260, windowTitle="Set neighborhood - neumann (4 neighbors) and closed boundaries")

# To change neighborhood and boundaries settings, you can pass new values in arguments of the grid or of newCellsOnGrid()"
Cell=myModel.newCellsOnGrid(7,4,"square",gap=0,size=50,neighborhood='neumann',boundaries='closed')

Cell.setEntities("landForm","plain")
Cell.setEntities_withColumn("landForm","mountain",1)
Cell.setEntities_withColumn("landForm","mountain",2)
Cell.setRandomEntities("landForm","lac",3,condition=lambda cell : cell.isValue('landForm','plain'))
Cell.newPov("base","landForm",{"plain":Qt.green,"lac":Qt.blue,"mountain":Qt.darkGray})
Cell.newBorderPov("transparent","landForm",{"plain":Qt.transparent,"lac":Qt.transparent,"mountain":Qt.transparent})
Cell.displayBorderPov("transparent")


Sheeps=myModel.newAgentSpecies("Sheeps","ellipseAgent1",defaultSize=20,locationInEntity='center')

Sheeps.newAgentsAtRandom(1, condition=lambda cell : cell.isValue('landForm','plain'))

p1 = myModel.newModelPhase()
p1.addAction(lambda : Sheeps.moveRandomly(condition=(lambda aCell : aCell.isValue('landForm','plain'))))


myModel.launch() 
sys.exit(monApp.exec_())
