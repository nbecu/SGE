import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mainClasses.SGSGE import *
from mainClasses.SGAdminPlayer import SGAdminPlayer
from mainClasses.gameAction.SGModify import *

# Créer l'application Qt (nécessaire pour les widgets)
monApp = QtWidgets.QApplication([])

# Test simple de la classe SGAdminPlayer
print("Testing SGAdminPlayer...")

# Créer un modèle simple
myModel = SGModel(800, 600, windowTitle="Test SGAdminPlayer")

# Créer une grille simple
Cell = myModel.newCellsOnGrid(3, 3, "square", size=40)
Cell.setEntities("type", "grass")
Cell.newPov("Type", "type", {"grass": Qt.green})

# Créer un agent simple
Sheeps = myModel.newAgentSpecies("Sheeps", "circleAgent")
Sheeps.setDefaultValues({"health": "good"})
Sheeps.newPov("Health", "health", {"good": Qt.blue, "bad": Qt.red})

# Créer un AdminPlayer
adminPlayer = SGAdminPlayer(myModel)

print(f"AdminPlayer created successfully!")
print(f"Number of game actions: {len(adminPlayer.gameActions)}")
print(f"Move actions: {len(adminPlayer.getMoveActionsOn(None))}")
print(f"Modify actions: {len([a for a in adminPlayer.gameActions if isinstance(a, SGModify)])}")

print("Test completed successfully!")

# Fermer l'application Qt proprement
monApp.quit()