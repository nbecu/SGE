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
m1_model, m1_view = Sheeps.newAgentAtCoordsWithModelView(Cell,1,1)
print(f"DEBUG: Agent m1 created with ID {m1_model.id}, position: ({m1_model.xCoord}, {m1_model.yCoord})")
m2_model, m2_view = Sheeps.newAgentAtCoordsWithModelView(Cell,5,1)
print(f"DEBUG: Agent m2 created with ID {m2_model.id}, position: ({m2_model.xCoord}, {m2_model.yCoord})")

aDestinationCell=Cell.getRandomEntity()
print(f"DEBUG: Destination cell selected: {aDestinationCell.id} at ({aDestinationCell.xCoord}, {aDestinationCell.yCoord})")

print("DEBUG: Creating model phase with move action...")
# Use a lambda that gets a new random destination each time
myModel.newModelPhase(Sheeps.newModelAction(lambda aSheep: aSheep.moveTo(Cell.getRandomEntity())))
# Test moveRandomly now that getNeighborCells is implemented
myModel.newModelPhase(Sheeps.newModelAction(lambda aSheep: aSheep.moveRandomly()))
# Test moveTowards - agent 1 moves towards agent 2
myModel.newModelPhase(Sheeps.newModelAction(lambda aSheep: aSheep.moveTowards(m2_model) if aSheep.id == m1_model.id else aSheep.moveRandomly()))
# Test cardinal movements - agent 1 moves North, agent 2 moves East
myModel.newModelPhase(Sheeps.newModelAction(lambda aSheep: aSheep.moveAgent(direction="North") if aSheep.id == m1_model.id else aSheep.moveAgent(direction="East")))
# Test cell movement - agent 1 moves to cell (3,3), agent 2 moves randomly
myModel.newModelPhase(Sheeps.newModelAction(lambda aSheep: aSheep.moveAgent(method="cell", cellID="cell3-3") if aSheep.id == m1_model.id else aSheep.moveRandomly()))

print("DEBUG: Launching model...")
myModel.launch()

print("DEBUG: Model launched, starting event loop...")
sys.exit(monApp.exec_())