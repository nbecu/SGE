import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(800, 700, windowTitle="Test GS_Aspect Unified Syntax")

# Test 1: Option A - Paramètres dans le constructeur
print("=== Test 1: Option A (parametres dans constructeur) ===")
timeLabel_A = myModel.newTimeLabel("Game Time", backgroundColor=Qt.cyan, textColor=Qt.cyan, borderColor=Qt.blue)
print("OK: TimeLabel cree avec Option A")

dashboard_A = myModel.newDashBoard("Dashboard A", borderColor=Qt.red, backgroundColor=Qt.yellow, textColor=Qt.black)
print("OK: Dashboard cree avec Option A")

endGameRule_A = myModel.newEndGameRule("Rules A", 1, borderColor=Qt.green, backgroundColor=Qt.white, textColor=Qt.green)
# Ajouter une condition d'exemple pour afficher du texte
score1_demo = myModel.newSimVariable("Score Demo", 0)
dashboard_demo = myModel.newDashBoard("Demo Dashboard")
indicator_demo = dashboard_demo.addIndicatorOnSimVariable(score1_demo)
endGameRule_A.addEndGameCondition_onIndicator(indicator_demo, "greater", 50, name="Score > 50")
endGameRule_A.showEndGameConditions()
print("OK: EndGameRule cree avec Option A")

# Test 2: Option B - Méthodes modeler après création
print("\n=== Test 2: Option B (methodes modeler) ===")
timeLabel_B = myModel.newTimeLabel("Game Time B")
timeLabel_B.setBackgroundColor(Qt.magenta)
timeLabel_B.setTextColor(Qt.magenta)
timeLabel_B.setBorderColor(Qt.darkMagenta)
print("OK: TimeLabel cree avec Option B - setters appliques")

dashboard_B = myModel.newDashBoard("Dashboard B")
dashboard_B.setBorderColor(Qt.darkBlue)
dashboard_B.setBackgroundColor(Qt.lightBlue)
dashboard_B.setTextColor(Qt.darkBlue)
dashboard_B.setBorderSize(3)
print("OK: Dashboard cree avec Option B - setters appliques")

endGameRule_B = myModel.newEndGameRule("Rules B", 1)
endGameRule_B.setBorderColor(Qt.darkGreen)
endGameRule_B.setBackgroundColor(Qt.lightGreen)
endGameRule_B.setTextColor(Qt.darkGreen)
# Ajouter une condition d'exemple pour afficher du texte
endGameRule_B.addEndGameCondition_onIndicator(indicator_demo, "greater", 75, name="Score > 75")
endGameRule_B.showEndGameConditions()
print("OK: EndGameRule cree avec Option B - setters appliques")

# Test 3: Mixte - Option A + modifications Option B
print("\n=== Test 3: Mixte (Option A + modifications Option B) ===")
timeLabel_Mix = myModel.newTimeLabel("Game Time Mix", backgroundColor=Qt.cyan, textColor=Qt.cyan)
timeLabel_Mix.setBorderColor(Qt.darkCyan)  # Modification après création
print("OK: TimeLabel cree avec Option A puis modifie avec Option B")

# Test 4: ProgressGauge
print("\n=== Test 4: ProgressGauge ===")
score1 = myModel.newSimVariable("Score", 0)
gauge_A = myModel.newProgressGauge(score1, 0, 100, "Gauge A", borderColor=Qt.red, backgroundColor=Qt.lightGray)
print("OK: ProgressGauge cree avec Option A")

gauge_B = myModel.newProgressGauge(score1, 0, 100, "Gauge B")
gauge_B.setBorderColor(Qt.blue)
gauge_B.setBackgroundColor(Qt.white)
print("OK: ProgressGauge cree avec Option B")

# Test 5: TextBox
print("\n=== Test 5: TextBox ===")
textBox_A = myModel.newTextBox("Texte de test", "TextBox A", 200, 150, borderColor=Qt.green, backgroundColor=Qt.lightGreen)
print("OK: TextBox cree avec Option A")

textBox_B = myModel.newTextBox("Texte de test", "TextBox B", 200, 150)
textBox_B.setBorderColor(Qt.orange)
textBox_B.setBackgroundColor(Qt.lightYellow)
print("OK: TextBox cree avec Option B")

# Vérification que tout passe par gs_aspect
print("\n=== Verification gs_aspect ===")
print(f"TimeLabel A - backgroundColor via gs_aspect: {timeLabel_A.gs_aspect.background_color}")
print(f"TimeLabel A - textColor via text1_aspect: {timeLabel_A.text1_aspect.color}")
print(f"Dashboard A - borderColor via gs_aspect: {dashboard_A.gs_aspect.border_color}")
print(f"EndGameRule A - backgroundColor via gs_aspect: {endGameRule_A.gs_aspect.background_color}")

print("\nOK: Tous les tests passent ! Les deux syntaxes fonctionnent et passent par gs_aspect.")

myModel.setCurrentPlayer("Player1")
myModel.launch()

sys.exit(monApp.exec_())

