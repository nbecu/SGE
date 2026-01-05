import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
from mainClasses.SGTestGetData import SGTestGetData
monApp=QtWidgets.QApplication([])

myModel=SGModel(760, 620, windowTitle="Test gs_aspect System - Style Dictionary Method")

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

# ============================================================================
# TEST 2: Style Dictionary Method
# ============================================================================

print("Testing setStyle dictionary method...")

# Test SGTextBox with style dictionary
print("  - Testing SGTextBox...")
textBox = myModel.newTextBox("Hello World!", "Test TextBox", titleAlignment='center')
textBox.setStyle({
    'border_color': Qt.red,
    'background_color': Qt.white,
    'text_color': Qt.black,
    'font_size': 16,
    'font_weight': 'bold',
    'border_radius': 5,
    'padding': 10
})
print("  - SGTextBox OK")

# Test SGEndGameRule with style dictionary
print("  - Testing SGEndGameRule...")
endGameRule = myModel.newEndGameRule("Test Rules", 1, borderColor=Qt.green, backgroundColor=Qt.white)
endGameRule.setStyle({
    'border_color': Qt.darkgreen,
    'background_color': Qt.lightgreen,
    'text_color': Qt.darkgreen,
    'border_size': 3,
    'border_radius': 10,
    'padding': 15
})
print("  - SGEndGameRule OK")


# Test SGDashBoard with style dictionary
print("  - Testing SGDashBoard...")
dashboard = myModel.newDashBoard("Test Dashboard", Qt.black, 1, Qt.white, Qt.black, "vertical")
dashboard.setLayoutOrder(3)
dashboard.setStyle({
    'border_color': Qt.purple,
    'background_color': Qt.lightgray,
    'text_color': Qt.purple,
    'border_radius': 4,
    'padding': 12
})
dashboard.setTitleText("Custom Dashboard")
print("  - SGDashBoard OK")

# Test SGTimeLabel with style dictionary
print("  - Testing SGTimeLabel...")
timeLabel = myModel.newTimeLabel("Game Time", backgroundColor=Qt.cyan, textColor=Qt.cyan)
timeLabel.setStyle({
    'border_color': Qt.cyan,
    'background_color': Qt.cyan,
    'text_color': Qt.darkblue,
    'border_radius': 7,
    'padding': 6
})
timeLabel.setTitleText("Custom Time")
print("  - SGTimeLabel OK")

# Test SGVoid with style dictionary
print("  - Testing SGVoid...")
void = myModel.newVoid("Test Void", 150, 100)
void.setStyle({
    'border_color': Qt.gray,
    'background_color': Qt.lightgray,
    'border_radius': 3,
    'padding': 5
})
void.setSize(200, 150)
print("  - SGVoid OK")

# Test Control Panels with style dictionary
print("  - Testing Player1ControlPanel...")
Player1ControlPanel=Player1.newControlPanel("Actions du Joueur 1")
Player1ControlPanel.setLayoutOrder(1)
Player1ControlPanel.setStyle({
    'border_color': Qt.darkgreen,
    'background_color': Qt.lightgreen,
    'border_radius': 5,
    'padding': 10
})
print("  - Player1ControlPanel OK")

print("  - Testing Player2ControlPanel...")
Player2ControlPanel=Player2.newControlPanel("Actions du Joueur 2")
Player2ControlPanel.setLayoutOrder(1)
Player2ControlPanel.setStyle({
    'border_color': Qt.darkblue,
    'background_color': Qt.lightblue,
    'border_radius': 5,
    'padding': 10
})
print("  - Player2ControlPanel OK")


# Test SGUserSelector with style dictionary
print("  - Testing SGUserSelector...")
userSelector = myModel.newUserSelector()
userSelector.setLayoutOrder(1)
userSelector.setStyle({
    'border_color': Qt.blue,
    'background_color': Qt.lightblue,
    'text_color': Qt.darkblue,
    'border_radius': 6,
    'padding': 8
})
userSelector.setTitleText("User Selection")
print("  - SGUserSelector OK")


# Test Progress Gauge with style dictionary
print("  - Testing ProgressGauge...")
score1= myModel.newSimVariable("Global Score:",0)
progressGauge = myModel.newProgressGauge(score1, minimum=0, maximum=100, title="Progress")
progressGauge.setLayoutOrder(3)
progressGauge.setStyle({
    'border_color': Qt.orange,
    'background_color': Qt.lightyellow,
    'border_radius': 6,
    'padding': 8
})
print("  - ProgressGauge OK")

# Test Legend with style dictionary
print("  - Testing Legend...")
theFirstLegend=myModel.newLegend()
theFirstLegend.setLayoutOrder(2)
theFirstLegend.setStyle({
    'border_color': Qt.darkred,
    'background_color': Qt.pink,
    'border_radius': 4,
    'padding': 7
})
print("  - Legend OK")

# Add some indicators to dashboard
i1 = dashboard.addIndicatorOnSimVariable(score1)

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
endGameRule.displayEndGameConditions()

myModel.setCurrentPlayer("Player1")

myModel.launch()

print("Style dictionary method test completed!")

sys.exit(monApp.exec_())
