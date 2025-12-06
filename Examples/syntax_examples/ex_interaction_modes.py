import sys
import random
from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor, QPixmap

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# Application initialization
monApp = QtWidgets.QApplication([])

# Model creation
myModel = SGModel(800, 600, windowTitle="Interaction Modes Examples")
myModel.displayTimeInWindowTitle()

# ============================================================================
# Example: Demonstrating action_controler for different game actions
# ============================================================================
print("Creating example demonstrating action_controler...")

# Create a grid
Grid = myModel.newCellsOnGrid(5, 4, "square", size=70, gap=5, name="InteractionGrid")

# Create a text box to display action feedback
textBox = myModel.newTextBox(width=300, height=200, chronologicalOrder=False, title="Action Log")

# ============================================================================
# TILE EXAMPLES
# ============================================================================

# Single Tile Type that can be both flipped and moved
Tile = myModel.newTileType(
    name="Tile",
    shape="rectTile",
    defaultSize=60,
    defaultPositionOnCell="center",
    backColor=QColor("red"),
    # colorForLegend=QColor("blue")
)

# Flip action with default directClick=True
flipAction = myModel.newFlipAction(
    Tile,
    action_controler={
        "controlPanel": True,      # Appears in ControlPanel (default)
        "contextMenu": True,        # Also in context menu
        "directClick": True         # Default for Flip - works automatically on click
    },
    feedbacks=[lambda aTargetEntity: textBox.addText(f"Tile {aTargetEntity.id} flipped!")],
)

# Move action with drag & drop (default, independent of directClick)
moveActionTile = myModel.newMoveAction(
    Tile,
    action_controler={
        "controlPanel": True,      # Appears in ControlPanel (default)
        # "contextMenu": False,        # Also in context menu
        "directClick": True         
        # Move actions use drag & drop by default (independent of directClick)
    },
    feedbacks=[lambda aTargetEntity: textBox.addText(f"Tile {aTargetEntity.id} moved to cell {aTargetEntity.cell.id}")]
)

# Place tiles
for x in range(1, 4):
    Tile.newTileOnCell(Grid.getCell(x, 1))

# ============================================================================
# AGENT EXAMPLES
# ============================================================================

# Agent Type 1: Activate with directClick=True (optional, not default)
AgentActivate = myModel.newAgentType(
    name="Agent_Activate",
    shape="circleAgent",
    defaultSize=40,
    defaultColor=QColor("green")  # Note: defaultColor is correct for AgentType
)

# Activate action with directClick=True (optional)
def activateAgent(agent):
    """Example activation method"""
    textBox.addText(f"Agent {agent.id} activated!")

activateAction = myModel.newActivateAction(
    AgentActivate,
    method=lambda agent: activateAgent(agent),
    action_controler={
        # "controlPanel": True,      # Appears in ControlPanel (default)
        "contextMenu": True,        # Also in context menu
        "directClick": True         # Optional - enables automatic click activation
    }
)
# Move action with drag & drop 
moveActionAgent = myModel.newMoveAction(
    AgentActivate,
    action_controler={
        "controlPanel": True,      # Appears in ControlPanel (default)
        # "contextMenu": False,        # Also in context menu
        "directClick": True         
        # Move actions use drag & drop by default (independent of directClick)
    },
    feedbacks=[lambda aTargetEntity: textBox.addText(f"Agent {aTargetEntity.id} moved to cell {aTargetEntity.cell.id}")]
)

# Agent Type 2: Modify WITHOUT directClick (default)
# This agent requires selecting the action in ControlPanel first
AgentModify = myModel.newAgentType(
    name="Agent_Modify",
    shape="squareAgent",
    defaultSize=40,
    defaultColor=QColor("yellow")  # Note: defaultColor is correct for AgentType
)

# Set default values
AgentModify.setDefaultValues({"status": "normal"})
AgentModify.newPov("default","status",{"normal":QColor("yellow"),"modified":QColor("red")})

# Modify action WITHOUT directClick (default for Modify)
modifyAction_status_modified = myModel.newModifyAction(
    AgentModify,
    dictAttributes={"status": "modified"},
    label="Status -> Modified",
    action_controler={
        "controlPanel": True,      # Appears in ControlPanel (default)
        "contextMenu": True,        # Also in context menu
        "directClick": True        # Default for Modify - requires selection
    },
    feedbacks=[lambda aTargetEntity: textBox.addText(f"Agent {aTargetEntity.id} status changed to modified")]
)
modifyAction_status_normal = myModel.newModifyAction(
    AgentModify,
    dictAttributes={"status": "normal"},
    label="Status -> Normal",
    action_controler={
        "controlPanel": True,      # Appears in ControlPanel (default)
        "contextMenu": True,        # Also in context menu
        "directClick": False        # Default for Modify - requires selection
    },
    feedbacks=[lambda aTargetEntity: textBox.addText(f"Agent {aTargetEntity.id} status changed to normal")]
)

# Agent Type 3: Delete with directClick=True (optional)
AgentDelete = myModel.newAgentType(
    name="Agent_Delete",
    shape="triangleAgent1",
    defaultSize=40,
    defaultColor=QColor("orange")  # Note: defaultColor is correct for AgentType
)

# Delete action with directClick=True (optional)
deleteAction = myModel.newDeleteAction(
    AgentDelete,
    action_controler={
        "controlPanel": True,      # Appears in ControlPanel (default)
        "contextMenu": True,        # Also in context menu
        "directClick": True        # Optional - enables automatic click deletion
    },
    feedbacks=[lambda aTargetEntity: textBox.addText(f"Agent {aTargetEntity.id} deleted")]
)

# Place agents
AgentActivate.newAgentAtCoords(Grid, 1, 3)
AgentModify.newAgentAtCoords(Grid, 2, 3)
AgentDelete.newAgentAtCoords(Grid, 3, 3)

# ============================================================================
# CELL EXAMPLES
# ============================================================================

# Cell Type: Create with directClick=True (optional)
# This allows creating entities by clicking directly on cells
createAction = myModel.newCreateAction(
    AgentActivate,
    action_controler={
        "controlPanel": True,      # Appears in ControlPanel (default)
        "contextMenu": True,        # Also in context menu
        "directClick": True        # Optional - enables automatic click creation
    },
    feedbacks=[lambda cellOnWhichAgentIsCreated: textBox.addText(f"Agent {cellOnWhichAgentIsCreated.getYoungestAgent(AgentActivate).id} created on cell {cellOnWhichAgentIsCreated.id}")]
)

# ============================================================================
# ACTIVATE WITH BUTTON EXAMPLE
# ============================================================================

# Activate action with button (for model-level actions)
def globalAction():
    """Global action triggered by button - adds 2 agents to empty cells"""
    empty_cells = []
    # Find all empty cells in the grid
    for cell in Grid.entities:
        if cell.isEmpty():
            empty_cells.append(cell)
    
    # Add up to 2 agents to empty cells
    if len(empty_cells) >= 2:
        # Randomly select 2 empty cells
        selected_cells = random.sample(empty_cells, 2)
        for cell in selected_cells:
            AgentActivate.newAgentOnCell(cell)
        textBox.addText(f"Added 2 agents to cells {[c.id for c in selected_cells]}")
    elif len(empty_cells) == 1:
        # Only one empty cell available
        AgentActivate.newAgentOnCell(empty_cells[0])
        textBox.addText(f"Added 1 agent to cell {empty_cells[0].id} (only one empty cell available)")
    else:
        textBox.addText("No empty cells available!")

activateButtonAction = myModel.newActivateAction(
    None,  # Model-level action
    method=lambda: globalAction(),
    label="🌐 Add 2 Agents",
    action_controler={
        "controlPanel": True,      # Appears in ControlPanel
        "button": True,            # Create a button
        "buttonPosition": (665, 200)  # Position of the button (moved to avoid overlap with grid)
    }
)

# ============================================================================
# PLAYER SETUP
# ============================================================================

# Create a player
Player1 = myModel.newPlayer("Player 1")

# Add all actions to the player
Player1.addGameAction(flipAction)
Player1.addGameAction(moveActionTile)
Player1.addGameAction(activateAction)
Player1.addGameAction(moveActionAgent)
Player1.addGameAction(modifyAction_status_modified)
Player1.addGameAction(modifyAction_status_normal)
Player1.addGameAction(deleteAction)
Player1.addGameAction(createAction)
Player1.addGameAction(activateButtonAction)

# Create control panel
Player1.newControlPanel("Player 1 Actions")

# Create a play phase
myModel.newPlayPhase("Player 1 Turn", [Player1])

# Set current player
myModel.setCurrentPlayer("Player 1")

# Create legend
# myModel.newLegend("Game Legend")

myModel.applyLayoutConfig("interaction_modes_ex")


# Launch the game
myModel.launch()

sys.exit(monApp.exec_())

