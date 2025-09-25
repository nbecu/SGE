import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

# Create model with larger window for better visualization
myModel = SGModel(600, 500, windowTitle="Multiple Agents - Different Move Types")
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

# Create agent species with move_type attribute
Robots = myModel.newAgentType("Robots", "triangleAgent1", defaultSize=20)
Robots.setDefaultValues({"move_type": "random"})

# Create POV for movement types with different colors
Robots.newPov("MovementType", "move_type", {
    "random": Qt.red,           # Red for random movement
    "direction N": Qt.blue,       # Blue for direction North movement
    "direction S": Qt.darkBlue,   # Dark blue for direction South movement
    "cell": Qt.magenta,         # Magenta for cell-specific movement
    "towards": Qt.darkYellow,   # Dark yellow for towards movement
    "randomly": Qt.cyan,        # Cyan for randomly movement
    "avoid_metal": Qt.darkMagenta # Dark magenta for avoiding metal movement
})

# Create multiple agents with different movement strategies
# Agent 1: Random movement
agent_random = Robots.newAgentAtCoords(Cell, 1, 1, {"move_type": "random"})

# Agent 2: direction movement (North/South)
agent_direction_N = Robots.newAgentAtCoords(Cell, 6, 10, {"move_type": "direction N"})
agent_direction_S = Robots.newAgentAtCoords(Cell, 6, 1, {"move_type": "direction S"})

# Agent 3: Cell-specific movement
agent_cell = Robots.newAgentAtCoords(Cell, 1, 5, {"move_type": "cell"})

# Agent 4: Towards target movement
agent_towards = Robots.newAgentAtCoords(Cell, 6, 5, {"move_type": "towards"})

# Agent 5: Randomly movement (using moveRandomly method)
agent_randomly = Robots.newAgentAtCoords(Cell, 1, 8, {"move_type": "randomly"})

# Agent 6: Avoid metal movement (with condition)
agent_avoid_metal = Robots.newAgentAtCoords(Cell, 6, 8, {"move_type": "avoid_metal"})

# Create legend to show movement types
movementLegend = myModel.newLegend()

# Create a single model phase with all movement actions
aModelPhase = myModel.newModelPhase()

# Add all movement actions to the single phase
# Random movement for agent_random
aModelPhase.addAction(myModel.newModelAction(
    lambda : agent_random.moveAgent(method="random") ))


# direction movement for agent_direction_N (North)
aModelPhase.addAction(myModel.newModelAction(
    lambda: agent_direction_N.moveAgent(target="up")
))

# direction movement for agent_direction_S (South)
aModelPhase.addAction(myModel.newModelAction(
    lambda: agent_direction_S.moveAgent(target="down")
))

# Cell-specific movement for agent_cell (to cell 6-6) - Syntax 1: explicit method
aModelPhase.addAction(myModel.newModelAction(
    lambda: agent_cell.moveAgent(method="cell", target=(6,6))
))

# Cell-specific movement for agent_cell (to cell 3-3) - Syntax 2: automatic method detection
aModelPhase.addAction(myModel.newModelAction(
    lambda: agent_cell.moveAgent(target=(3,3))
))

# Towards movement for agent_towards (moves towards agent_random)
aModelPhase.addAction(myModel.newModelAction(
    lambda: agent_towards.moveTowards(agent_random)
))

# Randomly movement for agent_randomly
aModelPhase.addAction(myModel.newModelAction(
    lambda: agent_randomly.moveRandomly()
))

# Avoid metal movement for agent_avoid_metal
aModelPhase.addAction(myModel.newModelAction(
    lambda: agent_avoid_metal.moveAgent(method="random", condition=lambda cell: cell.isNotValue("terrain", "metal"))
))

# Launch the model
myModel.launch()
sys.exit(monApp.exec_())
