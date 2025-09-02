import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
from mainClasses.SGTestGetData import SGTestGetData
monApp=QtWidgets.QApplication([])

print("DEBUG: Starting ex_move.py")

myModel=SGModel(410,380, windowTitle="Test move methods")
myModel.displayTimeInWindowTitle()

Cell=myModel.newCellsOnGrid(10,10,"square")
Cell.setEntities("landUse","grass")
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("pov","landUse",{"grass":Qt.green,"shrub":Qt.yellow})

Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1")

print("DEBUG: Creating agents...")
m1=Sheeps.newAgentAtCoords(Cell,1,1)
print(f"DEBUG: Agent m1 created with ID {m1.id}, position: ({m1.xCoord}, {m1.yCoord})")
m2=Sheeps.newAgentAtCoords(Cell,5,1)
print(f"DEBUG: Agent m2 created with ID {m2.id}, position: ({m2.xCoord}, {m2.yCoord})")

aDestinationCell=Cell.getRandomEntity()
print(f"DEBUG: Destination cell selected: {aDestinationCell.id} at ({aDestinationCell.xCoord}, {aDestinationCell.yCoord})")

print("DEBUG: Creating model phase with move action...")
# Use a lambda that gets a new random destination each time
myModel.newModelPhase(Sheeps.newModelAction(lambda aSheep: aSheep.moveTo(Cell.getRandomEntity())))
# Note: moveRandomly requires getNeighborCells which is not yet implemented
# myModel.newModelPhase(myModel.newModelAction(lambda: Sheeps.moveRandomly()))

print("DEBUG: Launching model...")
myModel.launch()

print("DEBUG: Model launched, starting event loop...")
sys.exit(monApp.exec_())