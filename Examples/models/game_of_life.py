import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
from mainClasses.SGTestGetData import SGTestGetData
monApp=QtWidgets.QApplication([])

myModel=SGModel(520,545, windowTitle="Game of Life from Conway")
myModel.displayTimeInWindowTitle()



## Define Production Units
Cells = myModel.newCellsOnGrid(20,20,size=25)
Cells.setEntities("state", lambda: random.choice(['dead', 'alive']))

# Define point of view for status
Cells.newPov("base", "state", {'dead': Qt.black, 'alive': Qt.white})

# dynamic of cells' state
def calculateNextState(aCell):
    # Count living neighbors
    neighbors = aCell.getNeighborCells()
    living_neighbors = sum(1 for n in neighbors if n.value('state') == 'alive')
    
    # Apply Conway's Game of Life rules
    if aCell.value('state') == 'alive':
        # Any live cell with fewer than two live neighbors dies (underpopulation)
        # Any live cell with more than three live neighbors dies (overpopulation)
        # Any live cell with two or three live neighbors lives on to the next generation
        nextState = 'alive' if 2 <= living_neighbors <= 3 else 'dead'
    else:
        # Any dead cell with exactly three live neighbors becomes a live cell (reproduction)
        nextState = 'alive' if living_neighbors == 3 else 'dead'
    
    #stores the result in a buffer in order to execute the new state action, asynchronously
    aCell.setValue("bufferState", nextState)

## Model actions 
modelAction1 = myModel.newModelAction_onCells(lambda aCell: calculateNextState(aCell))
modelAction2 = myModel.newModelAction_onCells(lambda aCell:  aCell.setValue("state", aCell.value("bufferState")))

## adds the model actions into a model phase
myModel.timeManager.newModelPhase([modelAction1, modelAction2])

## open the simulation
myModel.launch()
sys.exit(monApp.exec_())