import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(860, 700, windowTitle="Test ModifyActionWithDialog")

# Create a simple grid
Cell = myModel.newCellsOnGrid(5, 5, "square", size=40, gap=2, name='testgrid')
Cell.setEntities("landUse", "grass")
Cell.setRandomEntities("landUse", "shrub", 3)
Cell.setRandomEntities("landUse", "forest", 2)

# Create POVs
Cell.newPov("LandUse", "landUse", {
    "grass": Qt.green,
    "shrub": Qt.yellow, 
    "forest": Qt.darkGreen
})

# Create agents
Sheeps = myModel.newAgentSpecies("Sheeps", "triangleAgent1")
Sheeps.newPov("Health", "health", {'good': Qt.blue, 'bad': Qt.red})
Sheeps.setDefaultValues({"health": "good"})

# Create some agents
m1 = Sheeps.newAgentAtCoords(Cell, 1, 1, {"health": "good"})
m2 = Sheeps.newAgentAtCoords(Cell, 2, 2, {"health": "bad"})

# Create Player1 as a super player
Player1 = myModel.newPlayer("Player1")
Player1.addGameAction(myModel.newModifyAction(Cell, {"landUse":'forest'}, 'infinite'))
Player1.addGameAction(myModel.newModifyActionWithDialog(Cell, "landUse", 'infinite'))
Player1.addGameAction(myModel.newModifyActionWithDialog(Sheeps, "health", 'infinite'))

# Create control panel for Player1
Player1ControlPanel = Player1.newControlPanel("Player1 Actions")

# Set Player1 as current player
myModel.setCurrentPlayer("Player1")

# Create legend
myModel.newLegend("Test Legend", showAgentsWithNoAtt=True)

# Create time label
myModel.newTimeLabel()

# Launch the model
myModel.launch()

sys.exit(monApp.exec_())