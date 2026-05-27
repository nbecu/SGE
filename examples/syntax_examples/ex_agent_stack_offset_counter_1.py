import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(600, 400, windowTitle="Stack offset and counter demo")

# Create a small grid
Cells = myModel.newCellsOnGrid(2, 2, "square", size=120, gap=6)

# Agent types with stack offset and stack counter
Marker = myModel.newAgentType(
    "Marker",
    "squareAgent",
    defaultSize=40,
    defaultColor=Qt.lightBlue,
    locationInEntity="topRight",
    stackOffset=(-8, 10),
    stackCounter={"format": "{n}", "min_count": 2, "position": "center"}
)

MarkerSmall = myModel.newAgentType(
    "MarkerSmall",
    "circleAgent",
    defaultSize=34,
    defaultColor=Qt.darkGreen,
    locationInEntity="bottomLeft",
    stackOffset=(6, -6),
    stackCounter={"format": "x{n}", "min_count": 3}
)

MarkerNoOffset = myModel.newAgentType(
    "MarkerNoOffset",
    "circleAgent",
    defaultSize=38,
    defaultColor=Qt.darkMagenta,
    locationInEntity="center",
    stackCounter={"format": "x{n}", "min_count": 2, "position": "center"}
)

cell_1 = Cells.getCell(1, 1)
cell_2 = Cells.getCell(2, 1)
cell_3 = Cells.getCell(1, 2)

# Create multiple agents on different cells
for _ in range(4):
    agent = cell_1.newAgentHere(Marker)
    agent.view.show()

for _ in range(5):
    agent = cell_2.newAgentHere(MarkerSmall)
    agent.view.show()

for _ in range(3):
    agent = cell_3.newAgentHere(MarkerNoOffset)
    agent.view.show()

myModel.launch()

sys.exit(monApp.exec())
