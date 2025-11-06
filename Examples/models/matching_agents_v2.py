import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(450,375,windowTitle="Agents preference matching simulation",nb_columns=2)

# Popup to choose number of preference types
from PyQt5.QtWidgets import QInputDialog
num_types, ok = QInputDialog.getInt(None, "Preference Types", "Number of preference types (2-5):", 3, 2, 5, 1)
if not ok:
    num_types = 3  # Default value

boxes = myModel.newCellsOnGrid(10, 10, name="Box",neighborhood="neumann",boundaries="open")

# Define all possible types and colors
all_types = ["environmental", "social", "economic", "politic", "esthetic"]
all_colors = [Qt.green, Qt.pink, Qt.blue, Qt.red, Qt.magenta]
all_dark_colors = [Qt.darkGreen, Qt.red, Qt.darkBlue, Qt.darkRed, Qt.darkMagenta]

# Select types and colors based on user choice
selected_types = all_types[:num_types]
selected_colors = all_colors[:num_types]
selected_dark_colors = all_dark_colors[:num_types]

boxes.setEntities_randomChoicePerEntity("type", selected_types)

# Create color dictionary for cells
cell_colors = dict(zip(selected_types, selected_colors))
boxes.newPov("type", "type", cell_colors)

agents = myModel.newAgentType("Agent", "squareAgent", locationInEntity="center")

# Create agents for each selected type
for pref_type in selected_types:
    agents.newAgentsAtRandom(10, attributesAndValues={"pref": pref_type}, 
                           condition=lambda c, t=pref_type: c.isEmpty() and c.isNotValue("type", t))

# Create color dictionary for agents
agent_colors = dict(zip(selected_types, selected_dark_colors))
agents.newPov("pref", "pref", agent_colors)

score = myModel.newSimVariable("score", 0)

aAction = myModel.newModelAction_onAgents(agents,lambda aAgent : moveToPref(aAgent))

def moveToPref(aAgent):
    if aAgent.cell.isValue("type", aAgent.value("pref")):
        return
    matches = aAgent.cell.getNeighborCells(condition=lambda c: c.isValue("type", aAgent.value("pref")) and c.isEmpty())
    if matches:
        aAgent.moveTo(random.choice(matches))
        score.incValue(1)
    else:
        aAgent.moveRandomly(condition=lambda c: c.isEmpty())

myModel.newModelPhase(aAction)

dashboard = myModel.newDashBoard()
score_indicator = dashboard.addIndicatorOnSimVariable(score)
dashboard.addSeparator()
myModel.displayTimeInWindowTitle()

endGameRule=myModel.newEndGameRule()
endGameRule.addEndGameCondition_onIndicator(
    score_indicator, "equal", num_types * 10, name="All agents are happy")
endGameRule.showEndGameConditions()
endGameRule.setLayoutOrder(4)

myModel.launch()

sys.exit(monApp.exec_())
