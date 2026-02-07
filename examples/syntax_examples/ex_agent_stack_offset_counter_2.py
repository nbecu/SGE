import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp = QtWidgets.QApplication([])

myModel = SGModel(700, 450, windowTitle="Stack offset and counter demo (dynamic)")

# Create a small grid
Cells = myModel.newCellsOnGrid(2, 2, "square", size=120, gap=6)

# Agent type with stack offset and stack counter
Agent = myModel.newAgentType(
    "Agent",
    "squareAgent",
    defaultSize=40,
    defaultColor=Qt.lightBlue,
    locationInEntity="topRight",
    stackOffset=(-28, 20),
    stackCounter={"format": "{n}", "min_count": 2, "position": "center"}
)

# Seed some markers to show static stacking
Agent.newAgentsAtCoords(3, x=1, y=1)

# ---------------------------------------------------------------------------
# Add a admin control panel to add and control agents dynamically
# ---------------------------------------------------------------------------

myModel.displayAdminControlPanel()


myModel.launch()

sys.exit(monApp.exec_())
