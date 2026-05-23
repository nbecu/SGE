import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# ============================================================
# Example: addEndGameCondition_onSimVar
#
# A forager moves through a forest and collects resources
# each round. The game ends when the total score reaches 15.
#
# Key method: endGameRule.addEndGameCondition_onSimVar(simVar, op, objective)
#   - Takes a SimVariable directly (no Indicator needed)
#   - Same operators as addEndGameCondition_onIndicator:
#       "equal", "greater", "less", "greater or equal", "less or equal"
#   - Also supports: delay_rounds, final_phase
#
# Compare with the older approach that required an Indicator:
#   i = dashboard.addIndicatorOnSimVariable(score)
#   endGameRule.addEndGameCondition_onIndicator(i, "greater or equal", 15)
# ============================================================

monApp = QtWidgets.QApplication([])

myModel = SGModel(700, 600, windowTitle="EndGame on SimVar - example")

# Grid
Forest = myModel.newCellsOnGrid(6, 6, "square", size=70, gap=2)
Forest.setEntities("resources", 0)
Forest.setRandomEntities("resources", 3, 8)
Forest.setRandomEntities("resources", 1, 6)
Forest.newPov("Forest", "resources", {0: Qt.white, 1: Qt.yellow, 3: Qt.darkGreen})

# Agent
Forager = myModel.newAgentType("Forager", "circleAgent", defaultColor=Qt.red, defaultSize=18)
forager = Forager.newAgentAtCoords(Forest, 3, 3)

# SimVariable — tracks the total score
score = myModel.newSimVariable("Score", 0)

# Simulation: forager moves randomly and collects resources each round
def collect():
    forager.moveRandomly()
    cell = forager.cell
    if cell.getValue("resources") > 0:
        score.incValue(cell.getValue("resources"))
        cell.setValue("resources", 0)

myModel.newModelPhase(actions=collect, name="Forage")

# Dashboard — shows the score
dashboard = myModel.newDashBoard("Score", borderColor=Qt.black)
dashboard.addIndicatorOnSimVariable(score)

myModel.newTimeLabel("Rounds")

# End game rule — condition directly on SimVar (no Indicator needed)
endGameRule = myModel.newEndGameRule(title="Victory Condition", numberRequired=1)
endGameRule.addEndGameCondition_onSimVar(
    score, "greater or equal", 15, name="Score >= 15"
)
endGameRule.displayEndGameConditions()

myModel.launch()
sys.exit(monApp.exec_())