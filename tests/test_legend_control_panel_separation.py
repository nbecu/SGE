"""
Test script for Legend vs ControlPanel separation refactoring.

This test validates the complete separation between SGLegend (pure legend display) 
and SGControlPanel (game action interface) after the refactoring.

Test cases:
1. Pure Legend - should NOT be selectable (no controller behavior)
2. Player ControlPanel - should be selectable when player is current
3. Admin ControlPanel - should be selectable when admin is current
4. UserSelector - to switch between players

The test also includes automated assertions to validate the expected behavior
and diagnostic information for troubleshooting gameAction issues.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
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
Player1.addGameAction(myModel.newCreateAction(Sheeps,{"health":"bad"}))
Player1.addGameAction(myModel.newCreateAction(Sheeps,{"health":"good","hunger":"good"}))
Player1ControlPanel=Player1.newControlPanel("P1 actions")
myModel.setCurrentPlayer("Player 1")

# Test 3: AdminPlayer with ControlPanel (should have controller behavior)
# AdminPlayer is created automatically by SGModel
adminPlayer = myModel.getAdminPlayer()
adminPlayer.createAllGameActions()  # Create all gameActions for Admin
adminControlPanel = adminPlayer.newControlPanel("Admin actions")

# UserSelector to switch between players
userSelector=myModel.newUserSelector()

# Add a play phase to test Player1 ControlPanel after initialization
playPhase = myModel.newPlayPhase("play phase", ["Player 1", "Admin"])

# Automated test: Check that Legend items are not selectable
print("🔍 Running automated tests...")

# Test 1: Check that Legend items are not selectable
legend_items = Legend.legendItems
legend_selectable_count = sum(1 for item in legend_items if item.isSelectable())
print(f"   Legend items: {len(legend_items)} total, {legend_selectable_count} selectable")
if legend_selectable_count == 0:
    print("   ✅ Legend items are correctly NOT selectable")
else:
    print(f"   ❌ ERROR: {legend_selectable_count} Legend items are selectable (should be 0)")

# Test 2: Check that ControlPanel items are selectable
control_panel_items = Player1ControlPanel.getLegendItemsOfGameActions()
control_panel_selectable_count = sum(1 for item in control_panel_items if item.isSelectable())
print(f"   Player1 ControlPanel items: {len(control_panel_items)} total, {control_panel_selectable_count} selectable")
if control_panel_selectable_count == len(control_panel_items):
    print("   ✅ Player1 ControlPanel items are correctly selectable")
else:
    print(f"   ❌ ERROR: Only {control_panel_selectable_count}/{len(control_panel_items)} ControlPanel items are selectable")

# Test 3: Check that Admin ControlPanel items are selectable
admin_control_panel_items = adminControlPanel.getLegendItemsOfGameActions()
admin_control_panel_selectable_count = sum(1 for item in admin_control_panel_items if item.isSelectable())
print(f"   Admin ControlPanel items: {len(admin_control_panel_items)} total, {admin_control_panel_selectable_count} selectable")
if admin_control_panel_selectable_count == len(admin_control_panel_items):
    print("   ✅ Admin ControlPanel items are correctly selectable")
else:
    print(f"   ❌ ERROR: Only {admin_control_panel_selectable_count}/{len(admin_control_panel_items)} Admin ControlPanel items are selectable")

# Test 4: Diagnose createAction problem
print("\n🔍 Diagnosing createAction problem...")
print(f"   Current round: {myModel.timeManager.currentRoundNumber}")
print(f"   Is initialization: {myModel.timeManager.isInitialization()}")

# Test Player1 gameActions
player1_actions = Player1.gameActions
print(f"   Player1 has {len(player1_actions)} gameActions")
for i, action in enumerate(player1_actions):
    can_use = action.canBeUsed()
    print(f"     Action {i+1} ({action.actionType}): canBeUsed = {can_use}")
    if action.actionType == "Create":
        print(f"       Target entity: {action.targetEntDef.entityName}")
        print(f"       Target entityType: {action.targetEntDef.entityType()}")
        print(f"       Target isAgentDef: {action.targetEntDef.isAgentDef}")
        print(f"       Target isCellDef: {action.targetEntDef.isCellDef}")
        print(f"       Conditions count: {len(action.conditions)}")
        for j, condition in enumerate(action.conditions):
            print(f"         Condition {j+1}: {condition}")

print("")
print("✅ Test setup completed!")
print("📋 Test cases:")
print("  1. Pure Legend (top) - should NOT be selectable")
print("  2. Player1 ControlPanel - should be selectable when Player1 is current (after 1 turn)")
print("  3. Admin ControlPanel - should be selectable when Admin is current")
print("  4. UserSelector - to switch between players")
print("")
print("🎮 To test Player1 ControlPanel:")
print("  1. Click 'Next Turn' button to exit initialization phase")
print("  2. Use UserSelector to select 'Player 1'")
print("  3. Try clicking on Player1 ControlPanel items")
print("")
print("💡 Expected behavior:")
print("  - During initialization (round 0): Only Admin actions should work")
print("  - After 'Next Turn': Player1 actions should work")

myModel.launch() 

sys.exit(monApp.exec_())