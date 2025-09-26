"""
Example of using the defaultActionSelected parameter for a controlPanel

This file demonstrates how to define a default action that will be automatically
selected when creating a controlPanel.

"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

# Create the model
myModel = SGModel(700,400,name="defaultActionSelected Example", windowTitle="ControlPanel with default action")

# Create a grid
grid = myModel.newCellsOnGrid(5, 5, size=50, name="myGrid")

# Create an agent type
agents = myModel.newAgentType("CircleAgent", "circleAgent", defaultSize=20, defaultColor=Qt.blue)

# Create another agent type (triangular)
triangularAgents = myModel.newAgentType("TriangularAgent", "triangleAgent1", defaultSize=25, defaultColor=Qt.yellow)

# Create a third agent type (square)
squareAgents = myModel.newAgentType("SquareAgent", "squareAgent", defaultSize=30, defaultColor=Qt.darkYellow)

# Create an agent creation action
createAction = myModel.newCreateAction("CircleAgent", aNameToDisplay="Create an agent")

# Create a move action
moveAction = myModel.newMoveAction("CircleAgent", aNameToDisplay="Move the agent",setOnController=False)

# Create an action to create triangular agents
createTriangularAction = myModel.newCreateAction("TriangularAgent", aNameToDisplay="Create triangular agent")

# Create an action to create square agents
createSquareAction = myModel.newCreateAction("SquareAgent", aNameToDisplay="Create square agent")

# Create a player
player1 = myModel.newPlayer("Player1")

# Add game actions to the player
player1.addGameActions([createAction, moveAction, createTriangularAction, createSquareAction])

# Create the controlPanel with a default action
# The createSquareAction will be automatically selected
controlPanel = player1.newControlPanel(
    "Player 1 Actions", 
    defaultActionSelected=createSquareAction
)

# Create a game phase
myModel.newPlayPhase('Main Phase', [player1])

# Add explanatory label
myModel.newLabel_stylised(
    "This example demonstrates the defaultActionSelected parameter for controlPanels.\n\n"
    "The SquareAgent creation action is set as default and will be automatically selected.\n\n"
    "Modelers can change the defaultActionSelected by modifying this line in the code:\n"
    "defaultActionSelected=createSquareAction\n\n"
    "Try changing it to createAction or createTriangularAction to see the difference!",
    position=(280, 200),
    font="Arial",
    size=12,
    color="navy",
    background_color="lightblue",
    border_style="solid",
    border_size=2,
    border_color="darkblue",
    alignement="Left",
    fixedWidth=400
)

# Launch the model
myModel.launch()
sys.exit(monApp.exec_())

