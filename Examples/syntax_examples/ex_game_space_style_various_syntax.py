"""
Example demonstrating different syntaxes for styling GameSpaces in SGE.

This example shows that you can use multiple syntaxes to style GameSpaces, and even mix them:
- Syntax 1: Style parameters directly in the factory method (e.g., newTimeLabel(..., backgroundColor=Qt.cyan))
- Syntax 2: Style methods after creation (e.g., timeLabel.setBackgroundColor(Qt.cyan))
- Syntax 3: Mix both syntaxes (create with some styles, then modify with methods)

All syntaxes pass through the gs_aspect system, ensuring consistent styling behavior.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(700, 300, windowTitle="Test GS_Aspect Unified Syntax")

# ============================================================================
# Syntax 1: Style parameters directly in the factory method
# ============================================================================
# You can define styles directly when creating the GameSpace by passing
# style parameters as keyword arguments to the factory method.
# This is the most concise syntax for initial styling.
timeLabel_A = myModel.newTimeLabel("Game Time", backgroundColor=Qt.cyan, textColor=Qt.darkBlue, borderColor=Qt.blue)

dashboard_A = myModel.newDashBoard("Dashboard A", borderColor=Qt.red, backgroundColor=Qt.yellow, textColor=Qt.black)

endGameRule_A = myModel.newEndGameRule("Rules A", 1, borderColor=Qt.green, backgroundColor=Qt.white, textColor=Qt.green)
# Add an example condition to display text
score1_demo = myModel.newSimVariable("Score Demo", 0)
dashboard_demo = myModel.newDashBoard("Demo Dashboard")
indicator_demo = dashboard_demo.addIndicatorOnSimVariable(score1_demo)
endGameRule_A.addEndGameCondition_onIndicator(indicator_demo, "greater", 50, name="Score > 50")
endGameRule_A.showEndGameConditions()

# ============================================================================
# Syntax 2: Style methods after creation
# ============================================================================
# You can create a GameSpace first, then apply styles using setter methods.
# This syntax is useful when you need to determine styles dynamically or
# apply styles conditionally based on your model logic.
timeLabel_B = myModel.newTimeLabel("Game Time B")
timeLabel_B.setBackgroundColor(Qt.magenta)
timeLabel_B.setTextColor(Qt.red)
timeLabel_B.setBorderColor(Qt.darkMagenta)

dashboard_B = myModel.newDashBoard("Dashboard B")
dashboard_B.setBorderColor(Qt.darkBlue)
dashboard_B.setBackgroundColor(Qt.lightBlue)
dashboard_B.setTextColor(Qt.darkBlue)
dashboard_B.setBorderSize(3)

endGameRule_B = myModel.newEndGameRule("Rules B", 1)
endGameRule_B.setBorderColor(Qt.darkGreen)
endGameRule_B.setBackgroundColor(Qt.lightGreen)
endGameRule_B.setTextColor(Qt.darkGreen)
# Add an example condition to display text
endGameRule_B.addEndGameCondition_onIndicator(indicator_demo, "greater", 75, name="Score > 75")
endGameRule_B.showEndGameConditions()

# ============================================================================
# Syntax 3: Mix both syntaxes
# ============================================================================
# You can combine both syntaxes! Create a GameSpace with some initial styles
# using Syntax 1, then modify or add more styles using Syntax 2.
# This is very flexible and allows you to use the best approach for each case.
timeLabel_Mix = myModel.newTimeLabel("Game Time Mix", backgroundColor=Qt.cyan, textColor=Qt.blue)
timeLabel_Mix.setBorderColor(Qt.darkCyan)  # Modify after creation using Syntax 2

# ============================================================================
# Examples with different GameSpace types
# ============================================================================
# All GameSpaces support both syntaxes. Here are examples with ProgressGauge and TextBox.

# ProgressGauge examples
score1 = myModel.newSimVariable("Score", 0)
gauge_A = myModel.newProgressGauge(score1, 0, 100, "Gauge A", borderColor=Qt.red, backgroundColor=Qt.lightGray)

gauge_B = myModel.newProgressGauge(score1, 0, 100, "Gauge B")
gauge_B.setBorderColor(Qt.blue)
gauge_B.setBackgroundColor(Qt.white)

# TextBox examples
textBox_A = myModel.newTextBox("Texte de test", "TextBox A", 200, 150, borderColor=Qt.green, backgroundColor=Qt.lightGreen)

textBox_B = myModel.newTextBox("Texte de test", "TextBox B", 200, 150)
textBox_B.setBorderColor(Qt.orange)
textBox_B.setBackgroundColor(Qt.lightYellow)

# ============================================================================
# Verification: All styles pass through gs_aspect system
# ============================================================================
# Regardless of which syntax you use, all styles are applied through the
# unified gs_aspect system, ensuring consistent behavior and making it easy
# to apply themes and manage styles across your entire model.
# You can verify this by accessing the gs_aspect attributes:
# - timeLabel_A.gs_aspect.background_color
# - timeLabel_A.text1_aspect.color
# - dashboard_A.gs_aspect.border_color
# - etc.

myModel.setCurrentPlayer("Player1")
myModel.launch()

sys.exit(monApp.exec_())

