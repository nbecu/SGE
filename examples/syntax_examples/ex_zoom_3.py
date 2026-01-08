import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(800, 600, windowTitle="Test zoom with agents in different locations")

# Create a larger square grid
squareCell = myModel.newCellsOnGrid(4, 4, "square", name="SquareGrid", size=50, gap=3,borderColor=Qt.pink)
squareCell.grid.setBorderSize(4)
squareCell.setEntities("terrain", "grass")
squareCell.setRandomEntities("terrain", "rock", 3)
squareCell.newPov("base", "terrain", {
    "grass": Qt.green,
    "rock": Qt.darkGray
})

# Create agents with different locations
# Top-left agents
TopLeftAgents = myModel.newAgentType("TopLeft", "triangleAgent1", defaultSize=8, defaultColor=Qt.red, locationInEntity="topLeft")
TopLeftAgents.setDefaultValues_randomChoice({
    "health": ["good", "fair", "poor"]
})
TopLeftAgents.newAgentsAtRandom(3, squareCell, condition=lambda c: c.isValue("terrain", "grass"))

# Top-right agents
TopRightAgents = myModel.newAgentType("TopRight", "triangleAgent1", defaultSize=8, defaultColor=Qt.blue, locationInEntity="topRight")
TopRightAgents.setDefaultValues_randomChoice({
    "health": ["good", "fair", "poor"]
})
TopRightAgents.newAgentsAtRandom(3, squareCell, condition=lambda c: c.isValue("terrain", "grass"))

# Bottom-left agents
BottomLeftAgents = myModel.newAgentType("BottomLeft", "triangleAgent1", defaultSize=8, defaultColor=Qt.yellow, locationInEntity="bottomLeft")
BottomLeftAgents.setDefaultValues_randomChoice({
    "health": ["good", "fair", "poor"]
})
BottomLeftAgents.newAgentsAtRandom(3, squareCell, condition=lambda c: c.isValue("terrain", "grass"))

# Bottom-right agents
BottomRightAgents = myModel.newAgentType("BottomRight", "triangleAgent1", defaultSize=8, defaultColor=Qt.magenta, locationInEntity="bottomRight")
BottomRightAgents.setDefaultValues_randomChoice({
    "health": ["good", "fair", "poor"]
})
BottomRightAgents.newAgentsAtRandom(3, squareCell, condition=lambda c: c.isValue("terrain", "grass"))

# Center agents
CenterAgents = myModel.newAgentType("Center", "triangleAgent1", defaultSize=8, defaultColor=Qt.white, locationInEntity="center")
CenterAgents.setDefaultValues_randomChoice({
    "health": ["good", "fair", "poor"]
})
CenterAgents.newAgentsAtRandom(3, squareCell, condition=lambda c: c.isValue("terrain", "grass"))

# Create a legend
aLegend = myModel.newLegend()

# Create instructions
aTextBox = myModel.newTextBox(
    "Test zoom with agents in different locations:\n"
    "Red = topLeft, Blue = topRight, Yellow = bottomLeft,\n"
    "Magenta = bottomRight, White = center\n"
    "Move mouse over the grid and use mouse wheel to zoom in/out.\n"
    "Check that all agents maintain their relative positions.",
    title="Multi-Location Agent Zoom Test"
)
aTextBox.setTextFormat(fontName="Arial", size=10)
myModel.launch()
sys.exit(monApp.exec_())
