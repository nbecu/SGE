import sys
from pathlib import Path
# sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(800,600, windowTitle="Test SGLegend vs SGControlPanel refactoring")

Cell=myModel.newCellsOnGrid(6,4,"square",gap=2,size=40)

Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

# In SGE a "type" of agent is called a species.
# To create a species, it needs : a name and a shape 
Sheeps=myModel.newAgentSpecies("Sheeps","ellipseAgent1")
# available shapes are "circleAgent","squareAgent", "ellipseAgent1","ellipseAgent2", "rectAgent1","rectAgent2", "triangleAgent1","triangleAgent2", "arrowAgent1","arrowAgent2"

# You can also set default values to the species so that new agents will be initialized 
Sheeps.setDefaultValues_randomChoice({
                "health": ["good", "bad"],
                "hunger": ("good", "bad")            })
Sheeps.newAgentsAtRandom(10)

# For each attribute, you need to set up at least one point of view with its colors :
Sheeps.newPov("Health","health",{'good':Qt.blue,'bad':Qt.red})
Sheeps.newPov("Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})

# Test 1: Pure Legend (should not have controller behavior)
Legend=myModel.newLegend()

# Test 2: Player with ControlPanel (should have controller behavior)
Player1=myModel.newPlayer("Player 1")
Player1.addGameAction(myModel.newModifyAction(Cell,{"landUse":"grass"},4))
Player1.addGameAction(myModel.newCreateAction(Sheeps,{"health":"good","hunger":"good"}))
Player1ControlPanel=Player1.newControlPanel("P1 actions")

# Test 3: AdminPlayer with ControlPanel (should have controller behavior)
# AdminPlayer is created automatically by SGModel
adminPlayer = myModel.getAdminPlayer()
adminPlayer.createAllGameActions()  # Create all gameActions for Admin
adminControlPanel = adminPlayer.newControlPanel("Admin actions")

# UserSelector to switch between players
userSelector=myModel.newUserSelector()

print("✅ Test setup completed!")
print("📋 Test cases:")
print("  1. Pure Legend (top) - should NOT be selectable")
print("  2. Player1 ControlPanel - should be selectable when Player1 is current")
print("  3. Admin ControlPanel - should be selectable when Admin is current")
print("  4. UserSelector - to switch between players")

myModel.launch() 

sys.exit(monApp.exec_())