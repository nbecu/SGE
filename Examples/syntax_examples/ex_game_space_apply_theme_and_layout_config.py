import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(730, 520, windowTitle="Apply Theme and Layout Config")

myModel.applyThemeConfig('Theme_config_ex7')
myModel.applyLayoutConfig('layout_config_ex7')

# Create a grid
Cell=myModel.newCellsOnGrid(8,8,"square",size=40, gap=2)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",8)

Cell.newPov("pov","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkgreen})

# Create agents
Sheeps=myModel.newAgentType("Sheeps","triangleAgent1")
Sheeps.setDefaultValues({"health": (lambda: random.randint(0, 10)*10)})
Sheeps.setTooltip("Health", "health")

aDict = generate_color_gradient(
    Qt.red, Qt.blue,
    mapping={"values": list(range(0, 110, 10)), "value_min": 0, "value_max": 100},
    as_dict=True
)
Sheeps.newPov("Health","health",aDict)

m1_model = Sheeps.newAgentAtCoords(Cell,1,1)
m2_model = Sheeps.newAgentAtCoords(Cell,5,1)

# Create players
Player1=myModel.newPlayer("Player 1",{"Percentage of grass":0})
Player1.addGameAction(myModel.newModifyAction(Cell,{"landUse":"grass"},3))
Player2=myModel.newPlayer("Player 2",{"Sheeps in good health":0})
Player2.addGameAction(myModel.newCreateAction(Sheeps,{"health":100},4))

# add game spaces
textBox = myModel.newTextBox("Hello World!", "Test TextBox", titleAlignment='center')

endGameRule = myModel.newEndGameRule("Test Rules", 1, borderColor=Qt.green, backgroundColor=Qt.white)

dashboard = myModel.newDashBoard("Test Dashboard", Qt.black, 1, Qt.white, Qt.black, "vertical")
dashboard.setTitleText("Custom Dashboard")

timeLabel = myModel.newTimeLabel("Game Time", backgroundColor=Qt.cyan, textColor=Qt.cyan)
timeLabel.setTitleText("Custom Time")

void = myModel.newVoid("Test Void", 150, 100)
void.setSize(200, 150)

Player1ControlPanel=Player1.newControlPanel("Actions du Joueur 1")
Player1ControlPanel.setLayoutOrder(1)

Player2ControlPanel=Player2.newControlPanel("Actions du Joueur 2")
Player2ControlPanel.setLayoutOrder(1)


userSelector = myModel.newUserSelector()
userSelector.setLayoutOrder(1)
userSelector.setTitleText("User Selection")

score1= myModel.newSimVariable("Global Score:",0)
progressGauge = myModel.newProgressGauge(score1, minimum=0, maximum=100, title="Progress")
progressGauge.setLayoutOrder(3)
i1 = dashboard.addIndicatorOnSimVariable(score1)

theFirstLegend=myModel.newLegend()
theFirstLegend.setLayoutOrder(2)

# Create game phases
myModel.newPlayPhase('Phase 1', [Player1,Player2])
myModel.newModelPhase([lambda: Cell.setRandomEntities("landUse","forest"),lambda: Cell.setRandomEntities("landUse","shrub",3)])

aModelAction2=myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2,condition=(lambda x: x.value("landUse") != "shrub" and x.value("landUse") != "forest"  )))
myModel.newModelPhase(aModelAction2)

myModel.newModelPhase(myModel.newModelAction(lambda: Sheeps.moveRandomly()))
myModel.newModelPhase(myModel.newModelAction_onAgents('Sheeps',lambda aSheep: eat(aSheep)))

def eat(aSheep):
    if aSheep.cell.value('landUse') == "forest":
        aSheep.incValue('health',10)
        aSheep.cell.setValue('landUse',"grass")
    elif aSheep.cell.value('landUse') == "grass":
        aSheep.cell.setValue('landUse', "shrub")
        return
    elif aSheep.cell.value('landUse') == "shrub":
        aSheep.decValue('health',10)
    else:
        raise ValueError

# Add end game condition
endGameRule.addEndGameCondition_onIndicator(
    i1, "greater", 90, name="Score greater than 90")
endGameRule.showEndGameConditions()

myModel.setCurrentPlayer("Player1")

myModel.launch()

sys.exit(monApp.exec_())
