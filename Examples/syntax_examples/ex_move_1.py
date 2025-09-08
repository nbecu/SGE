import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

# Create model with larger window for better visualization
myModel = SGModel(600, 500, windowTitle="Robots - MoveTo Examples")
myModel.displayTimeInWindowTitle()

# Create grid with different terrain types
Cell = myModel.newCellsOnGrid(12, 10, "square")
Cell.setEntities("terrain", "concrete")
Cell.setRandomEntities("terrain", "metal", 15)
Cell.setRandomEntities("terrain", "energy", 8)

# Create POV for terrain visualization
Cell.newPov("terrain", "terrain", {
    "concrete": Qt.gray, 
    "metal": Qt.darkGray, 
    "energy": Qt.yellow
})

# Create agent species
Robots = myModel.newAgentSpecies("Robots", "triangleAgent1", defaultSize=20)

# Create multiple robots
robot1 = Robots.newAgentAtCoords(Cell, 1, 1)
robot2 = Robots.newAgentAtCoords(Cell, 6, 1)
robot3 = Robots.newAgentAtCoords(Cell, 1, 5)
robot4 = Robots.newAgentAtCoords(Cell, 6, 5)

# Create legend to show terrain types
terrainLegend = myModel.newLegend()

# Create model phases demonstrating different moveTo() usage patterns

# Phase 1: Robot1 moves to a random cell each time
myModel.newModelPhase(myModel.newModelAction(
    lambda: robot1.moveTo(Cell.getRandomEntity())
))

# Phase 2: Robot2 moves to a specific cell (cell 8-8)
target_cell = Cell.getCell(8, 8)
myModel.newModelPhase(myModel.newModelAction(
    lambda: robot2.moveTo(target_cell)
))

# Phase 3: Robot3 moves to different cells based on terrain type
# Moves to first energy cell found
energy_cells = Cell.getEntities_withValue("terrain", "energy")
if energy_cells:
    myModel.newModelPhase(myModel.newModelAction(
        lambda: robot3.moveTo(energy_cells[0])
    ))

# Phase 4: Robot4 moves to robot1's current position (following behavior)
myModel.newModelPhase(myModel.newModelAction(
    lambda: robot4.moveTo(robot1.cell)
))

# Phase 5: All robots move to random cells simultaneously
myModel.newModelPhase(myModel.newModelAction(
    lambda: robot1.moveTo(Cell.getRandomEntity())
))
myModel.newModelPhase(myModel.newModelAction(
    lambda: robot2.moveTo(Cell.getRandomEntity())
))
myModel.newModelPhase(myModel.newModelAction(
    lambda: robot3.moveTo(Cell.getRandomEntity())
))
myModel.newModelPhase(myModel.newModelAction(
    lambda: robot4.moveTo(Cell.getRandomEntity())
))

# Launch the model
myModel.launch()
sys.exit(monApp.exec_())
