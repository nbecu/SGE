import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# ============================================================
# Example: getLastArrivedAgent
#
# Three scouts race through a grid. A designated "goal cell"
# is highlighted in yellow. Each round the simulation reads
# which scout arrived there last and displays their name.
#
# Key method: cell.getLastArrivedAgent()
#   - Returns the agent that most recently arrived on this cell
#     (via moveTo() or agent creation)
#   - Returns None if no agent has ever arrived on this cell
#
# Hover over a scout to see its name (setTooltip).
# Each scout has a distinct color (POV on scout_name attribute).
# ============================================================

monApp = QtWidgets.QApplication([])

myModel = SGModel(800, 600, windowTitle="getLastArrivedAgent - example")

# Grid
Arena = myModel.newCellsOnGrid(5, 5, "square", size=80, gap=2, boundaries='closed')
Arena.setEntities("type", "open")
Arena.newPov("Arena", "type", {"open": Qt.lightGray, "goal": Qt.yellow})

# Mark the goal cell (center)
goal_cell = Arena.getCell(3, 3)
goal_cell.setValue("type", "goal")

# Three scouts — each with a name attribute used for color and tooltip
Scout = myModel.newAgentType("Scout", "triangleAgent1", defaultSize=18)
Scout.setDefaultValues({"scout_name": "none"})

# POV: each scout gets a distinct color based on their name
Scout.newPov("Identity", "scout_name", {
    "Alpha": Qt.blue,
    "Beta":  Qt.red,
    "Gamma": Qt.darkGreen
})

# Tooltip: hover over a scout to see its name
Scout.setTooltip("Scout", "scout_name")

s1 = Scout.newAgentAtCoords(Arena, 1, 1)
s1.setValue("scout_name", "Alpha")

s2 = Scout.newAgentAtCoords(Arena, 5, 1)
s2.setValue("scout_name", "Beta")

s3 = Scout.newAgentAtCoords(Arena, 3, 5)
s3.setValue("scout_name", "Gamma")

# Legend — shows the color/name mapping for each scout
myModel.newLegend()

# TextBox to display the last scout at the goal
status_box = myModel.newTextBox(
    "No scout has reached the goal yet.",
    title="Goal cell status"
)

# Simulation: scouts move randomly, goal cell tracks last arrival
def move_and_check():
    s1.moveRandomly()
    s2.moveRandomly()
    s3.moveRandomly()

    last = goal_cell.getLastArrivedAgent()
    if last is not None:
        name = last.getValue("scout_name")
        status_box.setText(f"Last scout at goal: {name}")
    else:
        status_box.setText("No scout has reached the goal yet.")

myModel.newModelPhase(actions=move_and_check, name="Move")

myModel.newTimeLabel("Rounds")

myModel.launch()
sys.exit(monApp.exec())