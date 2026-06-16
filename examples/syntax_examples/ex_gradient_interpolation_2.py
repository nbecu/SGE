"""
Gradient Interpolation - Multiple Methods (Phase 3, Feature 3)

Demonstrates different interpolation methods:
- linear: Straight line interpolation (uniform transition)
- log: Logarithmic (soft/smooth transition)
- exp: Exponential (fast transition at start)

Switch between methods using: Menu > Symbology > By Type > Cells
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Gradient Interpolation Methods Comparison")

# Create cells with score attribute (0-100)
# Horizontal line to show gradient transitions clearly
Cells = myModel.newCellsOnGrid(12, 1, "square", size=60)
Cells.setEntities("score", 50)

# Set score values from 0 to 100 across the grid using gradient method
Cells.setEntities_withGradient("score", 0, 100)

# Define gradient with 2 key points (0=blue, 100=red)
score_gradient = {
    0: SGAspect(
        background_color=QColor("blue"),
        text_content="{score}",
        text_color="white",
        text_size=11,
        text_weight="bold",
        text_alignment="center"
    ),
    100: SGAspect(
        background_color=QColor("red"),
        text_content="{score}",
        text_color="white",
        text_size=11,
        text_weight="bold",
        text_alignment="center"
    ),
}

# Create three gradient symbologies with different interpolation methods

# Method 1: Linear interpolation (uniform color transition - default)
Cells.newSymbologyGradient(
    "score",
    score_gradient.copy(),
    name="ScoreLinear"
)

# Method 2: Logarithmic interpolation (smooth soft transition)
Cells.newSymbologyGradient(
    "score",
    score_gradient.copy(),
    interpolation="log",
    name="ScoreLog"
)

# Method 3: Exponential interpolation (fast start, slow end)
Cells.newSymbologyGradient(
    "score",
    score_gradient.copy(),
    interpolation="exp",
    name="ScoreExp"
)

# Add agents with nominal symbology to test legend display with both gradients + nominal
AgentType = myModel.newAgentType("Worker", "squareAgent", defaultSize=25)
AgentType.setEntities("status", "idle")

# Define nominal symbology for agent status
agent_status_aspects = {
    "idle": SGAspect(
        background_color=QColor("green"),
        text_content="Idle"
    ),
    "working": SGAspect(
        background_color=QColor("yellow"),
        text_content="Working"
    ),
    "paused": SGAspect(
        background_color=QColor("red"),
        text_content="Paused"
    ),
}

AgentType.newSymbology("status", agent_status_aspects, name="AgentStatus")

# Create agents with different statuses
statuses = ["idle", "working", "paused", "idle", "working", "paused"]
for i, status in enumerate(statuses):
    cell = Cells.entities[i % len(Cells.entities)]
    agent = AgentType.newAgentAtCoords(Cells, cell.xCoord, cell.yCoord)
    agent.setValue("status", status)

myModel.newLegend()

# Launch
myModel.launch()
sys.exit(monApp.exec())
