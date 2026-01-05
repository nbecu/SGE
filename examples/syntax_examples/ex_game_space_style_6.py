import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
from mainClasses.SGTestGetData import SGTestGetData
monApp=QtWidgets.QApplication([])

myModel=SGModel(800, 660, windowTitle="Test gs_aspect System - use image as background of game spaces")

#background image
background_image_1 = QPixmap("images/background_sea.jpg")
background_image_2 = QPixmap("icon/solutre/fond_solutre.jpg")

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
# TEST 4: Mixed Approach - Theme + Individual Methods + Style Dictionary
# ============================================================================

print("Testing mixed approach...")

# Create GameSpaces
textBox = myModel.newTextBox("Hello World!", "Test TextBox", titleAlignment='center')

endGameRule = myModel.newEndGameRule("Test Rules", 1, borderColor=Qt.green, backgroundColor=Qt.white)

dashboard = myModel.newDashBoard("Test Dashboard", Qt.black, 1, Qt.white, Qt.black, "vertical")
dashboard.setLayoutOrder(3)
dashboard.setTitleText("Custom Dashboard")

timeLabel = myModel.newTimeLabel("Game Time", backgroundColor=Qt.cyan, textColor=Qt.cyan)
timeLabel.setTitleText("Time")

void = myModel.newVoid("Test Void", 150, 100)

Player1ControlPanel=Player1.newControlPanel("Actions du Joueur 1")
Player1ControlPanel.setLayoutOrder(1)

Player2ControlPanel=Player2.newControlPanel("Actions du Joueur 2")
Player1ControlPanel.setLayoutOrder(2)

userSelector = myModel.newUserSelector()
userSelector.setLayoutOrder(1)
userSelector.setTitleText("User Selection")

score1= myModel.newSimVariable("Global Score",0)
progressGauge = myModel.newProgressGauge(score1, minimum=0, maximum=100, title="Progress")
progressGauge.setLayoutOrder(3)

theFirstLegend=myModel.newLegend()

aLabel=myModel.newLabel("Test Label")
aLabel.setLayoutOrder(3)

aButton=myModel.newButton(lambda: print('hello'),"Test Button")
aButton.setLayoutOrder(3)

# Mixed approach: Start with theme, then customize
print("Applying mixed approach...")

# 1. Start with theme
textBox.applyTheme('modern')
print("  - TextBox: started with modern theme")

# 2. Then customize with individual methods
textBox.setBorderColor(Qt.red)
textBox.setFontSize(16)
textBox.setBorderRadius(8)
textBox.setBackgroundImage(background_image_1)
print("  - TextBox: customized with individual methods")

# 3. Start with theme
endGameRule.applyTheme('colorful')
print("  - EndGameRule: started with colorful theme")

# 4. Then customize with style dictionary
endGameRule.setStyle({
    'border_size': 3,
    'padding': 15,
    'min_width': 250
})
endGameRule.setBackgroundImage(background_image_2)
print("  - EndGameRule: customized with style dictionary")

# 5. Start with theme
userSelector.applyTheme('blue')
print("  - UserSelector: started with blue theme")

# 6. Then customize with individual methods
userSelector.setTitleText("Custom User Selection")
userSelector.setCheckboxStyle({'color': 'darkblue', 'font_weight': 'bold'})
print("  - UserSelector: customized with individual methods")
userSelector.setBackgroundImage(background_image_1)


# 7. Start with theme
dashboard.applyTheme('green')
print("  - Dashboard: started with green theme")

# 8. Then customize with style dictionary
dashboard.setStyle({
    'border_radius': 10,
    'padding': 20,
    'min_height': 200
})
dashboard.setBackgroundImage(background_image_2)
print("  - Dashboard: customized with style dictionary")

# 9. Start with theme
timeLabel.applyTheme('minimal')
print("  - TimeLabel: started with minimal theme")

# 10. Then customize with individual methods
timeLabel.setDisplayRoundNumber(True)
timeLabel.setDisplayPhaseName(True)
timeLabel.setLabelStyle({'font_size': 14, 'font_weight': 'bold'})
timeLabel.setBackgroundImage(background_image_1)
print("  - TimeLabel: customized with individual methods")

# 11. Start with theme
void.applyTheme('gray')
print("  - Void: started with gray theme")

# 12. Then customize with individual methods
void.setSize(250, 180)
void.setBorderColor(Qt.darkgray)
void.setBackgroundImage(background_image_1)
print("  - Void: customized with individual methods")

# 13. Start with theme
Player1ControlPanel.applyTheme('modern')
Player1ControlPanel.setLayoutOrder(1)
print("  - Player1ControlPanel: started with modern theme")

# 14. Then customize with style dictionary
Player1ControlPanel.setStyle({
    'border_radius': 6,
    'padding': 12
})
Player1ControlPanel.setBackgroundImage(background_image_2)
print("  - Player1ControlPanel: customized with style dictionary")

# 15. Start with theme
Player2ControlPanel.applyTheme('colorful')
Player2ControlPanel.setLayoutOrder(1)
print("  - Player2ControlPanel: started with colorful theme")

# 16. Then customize with individual methods
Player2ControlPanel.setBorderColor(Qt.darkblue)
Player2ControlPanel.setBackgroundColor(Qt.lightblue)
Player2ControlPanel.setBackgroundImage(background_image_1)
print("  - Player2ControlPanel: customized with individual methods")

# 17. Start with theme
progressGauge.applyTheme('blue')
print("  - ProgressGauge: started with blue theme")

# 18. Then customize with style dictionary
progressGauge.setStyle({
    'border_radius': 8,
    'padding': 2
})
progressGauge.setBackgroundImage(background_image_2)
print("  - ProgressGauge: customized with style dictionary")

# 19. Start with theme
theFirstLegend.applyTheme('green')
print("  - Legend: started with green theme")

# 20. Then customize with individual methods
theFirstLegend.setBorderColor(Qt.darkgreen)
# theFirstLegend.setBackgroundColor(Qt.lightgreen)
theFirstLegend.setBackgroundImage(background_image_2)

print("  - Legend: customized with individual methods")

# 21. Add background images to remaining GameSpaces
aLabel.setBackgroundImage(background_image_1)
aButton.setBackgroundImage(background_image_2)
print("  - Added background images to Label and Button")

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

print("Mixed approach test completed!")

sys.exit(monApp.exec_())
