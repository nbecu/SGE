import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# Initialisation de l'application
monApp = QtWidgets.QApplication([])

myModel = SGModel(600, 600, windowTitle="Jeu du Morpion")

# Grid
Cell = myModel.newCellsOnGrid(3, 3, "square", size=100, gap=5)
Cell.setEntities("state", "empty")

# POV
Cell.newPov("Morpion", "state", {
    "empty": Qt.white,
    "X": Qt.blue,
    "O": Qt.red
})

# Players
Player1 = myModel.newPlayer("Joueur 1")
Player2 = myModel.newPlayer("Joueur 2")

# Actions (only on empty cells)
empty_condition = [lambda cell: cell.value("state") == "empty"]
Player1.addGameAction(myModel.newModifyAction(Cell, {"state": "X"}, 1,conditions=empty_condition))
Player2.addGameAction(myModel.newModifyAction(Cell, {"state": "O"}, 1,conditions=empty_condition))
Player1.newControlPanel("Joueur 1")
Player2.newControlPanel("Joueur 2")

# Phases
myModel.newPlayPhase("Tour de Joueur 1", [Player1],autoForwardWhenAllActionsUsed=True,message_auto_forward=False)
myModel.newPlayPhase("Tour de Joueur 2", [Player2],autoForwardWhenAllActionsUsed=True,message_auto_forward=False)

# User selector
userSelector=myModel.newUserSelector()
myModel.setCurrentPlayer('Admin')

# End game rule
endGameRule = myModel.newEndGameRule()
winner = None

def check_victory():
    # Check victory lines, columns and diagonals
    for i in range(1, 4):
        if Cell.getCell(i, 1).value("state") == Cell.getCell(i, 2).value("state") == Cell.getCell(i, 3).value("state") != "empty":
            winner = Cell.getCell(i, 1).value("state")
            print(f"Victoire de {winner}")
            return True
        if Cell.getCell(1, i).value("state") == Cell.getCell(2, i).value("state") == Cell.getCell(3, i).value("state") != "empty":
            winner = Cell.getCell(1, i).value("state")
            print(f"Victoire de {winner}")
            return True
    if Cell.getCell(1, 1).value("state") == Cell.getCell(2, 2).value("state") == Cell.getCell(3, 3).value("state") != "empty":
        winner = Cell.getCell(1, 1).value("state")
        print(f"Victoire de {winner}")
        return True
    if Cell.getCell(1, 3).value("state") == Cell.getCell(2, 2).value("state") == Cell.getCell(3, 1).value("state") != "empty":
        winner = Cell.getCell(1, 3).value("state")
        print(f"Victoire de {winner}")
        return True
    return False

def check_draw():
    # Draw if no empty cells and no victory
    if len(Cell.getEntities_withValue("state", "empty")) == 0 and winner is None:
        print(f"Match nul")
        return True
    return False

endGameRule.addEndGameCondition_onLambda(lambda: check_victory(), name="Victoire")
endGameRule.addEndGameCondition_onLambda(lambda: check_draw(), name="Match nul")

#affichage des phases de jeu
time_label = myModel.newTimeLabel()
time_label.moveToCoords(390,300)

# Lancement du jeu
myModel.launch()

sys.exit(monApp.exec())