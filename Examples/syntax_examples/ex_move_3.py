import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

# Create model with larger window for better visualization
myModel = SGModel(600, 500, windowTitle="Robots - Multiple Movements")
myModel.displayTimeInWindowTitle()

# Create grid with different terrain types
Cell = myModel.newCellsOnGrid(12, 10, "square",neighborhood="neumann")
Cell.setEntities("terrain", "concrete")
Cell.setRandomEntities("terrain", "metal", 15)
Cell.setRandomEntities("terrain", "energy", 8)

# Create POV for terrain visualization
Cell.newPov("terrain", "terrain", {
    "concrete": Qt.gray, 
    "metal": Qt.darkGray, 
    "energy": Qt.yellow
})

# Create agent species with move_type attribute
Robots = myModel.newAgentSpecies("Robots", "triangleAgent1", defaultSize=20)
Robots.setDefaultValues({"move_type": "random"})

# Create POV for movement types with different colors
Robots.newPov("MovementType", "move_type", {
    "single": Qt.red,           # Red for single movement
    "double": Qt.darkRed,      # Dark red for double movement
    "double_north": Qt.blue, # Blue for double direction movement
    "quadruple_randomly": Qt.cyan # Cyan for quadruple randomly movement
})

# Create fewer robots with different movement strategies
# Robot 1: Single random movement
robot_single = Robots.newAgentAtCoords(Cell, 2, 2, {"move_type": "single"})

# Robot 2: double random movement
robot_double = Robots.newAgentAtCoords(Cell, 6, 2, {"move_type": "double"})

# Robot 3: Double direction movement (North)
robot_double_direction = Robots.newAgentAtCoords(Cell, 2, 6, {"move_type": "double_direction"})

# Robot 4: Quadruple randomly movement
robot_quadruple_randomly = Robots.newAgentAtCoords(Cell, 6, 6, {"move_type": "quadruple_randomly"})

# Create legend to show movement types
movementLegend = myModel.newLegend()

# Create a single model phase with all movement actions
aModelPhase = myModel.newModelPhase()

# Add all movement actions to the single phase
# Single random movement for robot_single
aModelPhase.addAction(myModel.newModelAction(
    lambda: robot_single.moveAgent(method="random", numberOfMovement=1)
))

# double random movement for robot_double
aModelPhase.addAction(myModel.newModelAction(
    lambda: robot_double.moveAgent(method="random", numberOfMovement=2)
))

# Double direction movement for robot_double_direction (North)
aModelPhase.addAction(myModel.newModelAction(
    lambda: robot_double_direction.moveAgent(method="direction", target="up", numberOfMovement=2)
))

# Quadruple randomly movement for robot_quadruple_randomly
aModelPhase.addAction(myModel.newModelAction(
    lambda: robot_quadruple_randomly.moveRandomly(numberOfMovement=4)
))

# Launch the model
myModel.launch()
sys.exit(monApp.exec_())
