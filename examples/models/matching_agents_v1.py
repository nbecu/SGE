import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(450,375,windowTitle="Agents preference matching simulation",nb_columns=2)

boxes = myModel.newCellsOnGrid(10, 10, name="Box",neighborhood="neumann",boundaries="open")

boxes.setEntities_randomChoicePerEntity("type", ["environmental","social","economic"])

boxes.newPov("type", "type",{"environmental": Qt.green, "social": Qt.pink, "economic": Qt.blue})

agents =myModel.newAgentType("Agent", "squareAgent",locationInEntity="center")
agents.newAgentsAtRandom(10,attributesAndValues={"pref":"environmental"},condition=lambda c: c.isEmpty() and c.isNotValue("type", "environmental"))
agents.newAgentsAtRandom(10,attributesAndValues={"pref":"social"},condition=lambda c: c.isEmpty() and c.isNotValue("type", "social"))
agents.newAgentsAtRandom(10,attributesAndValues={"pref":"economic"},condition=lambda c: c.isEmpty() and c.isNotValue("type", "economic"))

agents.newPov("pref", "pref",{"environmental": Qt.darkGreen, "social": Qt.red, "economic": Qt.darkBlue})

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
    score_indicator, "equal", 30, name="All agents are happy")
endGameRule.displayEndGameConditions()
endGameRule.setLayoutOrder(4)

myModel.launch()

sys.exit(monApp.exec_())
