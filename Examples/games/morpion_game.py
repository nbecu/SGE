import sys
from pathlib import Path
import random
from PyQt5 import QtWidgets, QtGui

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# Initialisation de l'application
monApp = QtWidgets.QApplication([])

# Création du modèle
myModel = SGModel(600, 600, windowTitle="Jeu du Morpion")

# Création de la grille 3x3 pour le morpion
Cell = myModel.newCellsOnGrid(3, 3, "square", size=100, gap=5)
Cell.setEntities("state", "empty")

# Définition des points de vue pour les cellules
Cell.newPov("Morpion", "state", {
    "empty": QtGui.QColor("white"),
    "X": QtGui.QColor("blue"),
    "O": QtGui.QColor("red")
})

# Création des joueurs
Player1 = myModel.newPlayer("Joueur 1")
Player2 = myModel.newPlayer("Joueur 2")

# Actions des joueurs pour placer X ou O
Player1.addGameAction(myModel.newModifyAction(Cell, {"state": "X"}, 1))
Player2.addGameAction(myModel.newModifyAction(Cell, {"state": "O"}, 1))
Player1.newControlPanel("Joueur 1",showAgentsWithNoAtt=True)
Player2.newControlPanel("Joueur 2",showAgentsWithNoAtt=True)
# Gestion des tours
myModel.timeManager.newGamePhase("Tour de Joueur 1", [Player1],autoForwardWhenAllActionsUsed=True,message_auto_forward=False)
myModel.timeManager.newGamePhase("Tour de Joueur 2", [Player2],autoForwardWhenAllActionsUsed=True,message_auto_forward=False)

#
userSelector=myModel.newUserSelector()

# Condition de fin de jeu
endGameRule = myModel.newEndGameRule()

def check_victory():
    # Vérification des lignes, colonnes et diagonales
    for i in range(1, 4):
        if Cell.getCell(i, 1).value("state") == Cell.getCell(i, 2).value("state") == Cell.getCell(i, 3).value("state") != "empty":
            return True
        if Cell.getCell(1, i).value("state") == Cell.getCell(2, i).value("state") == Cell.getCell(3, i).value("state") != "empty":
            return True
    if Cell.getCell(1, 1).value("state") == Cell.getCell(2, 2).value("state") == Cell.getCell(3, 3).value("state") != "empty":
        return True
    if Cell.getCell(1, 3).value("state") == Cell.getCell(2, 2).value("state") == Cell.getCell(3, 1).value("state") != "empty":
        return True
    return False

endGameRule.addEndGameCondition_onLambda(lambda: check_victory(), name="Victoire")

# Lancement du jeu
myModel.setCurrentPlayer("Joueur 1")
myModel.launch()

sys.exit(monApp.exec_())