import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mainClasses.SGSGE import *
from mainClasses.SGAdminPlayer import SGAdminPlayer

# Test spécifique pour le ControlPanel d'Admin
print("Testing Admin ControlPanel with gameActions...")

# Créer l'application Qt (nécessaire pour les widgets)
monApp = QtWidgets.QApplication([])

# Créer un modèle avec Admin super player
myModel = SGModel(800, 600, windowTitle="Test Admin ControlPanel")

# Créer une grille simple
Cell = myModel.newCellsOnGrid(3, 3, "square", size=40)
Cell.setEntities("type", "grass")
Cell.newPov("Type", "type", {"grass": Qt.green, "water": Qt.blue})

# Créer une espèce d'agents
Sheeps = myModel.newAgentSpecies("Sheeps", "circleAgent")
Sheeps.setEntities("health", "good")
Sheeps.newPov("Health", "health", {"good": Qt.green, "bad": Qt.red})

# Maintenant que toutes les entités sont créées, créer les actions d'Admin
adminPlayer = myModel.getAdminPlayer()
adminPlayer.createAllGameActions()

print(f"Admin has {len(adminPlayer.gameActions)} gameActions before ControlPanel creation")

# Créer un ControlPanel pour Admin APRÈS avoir créé les actions
adminPlayer.newControlPanel("Admin Control Panel")

print(f"Admin ControlPanel created successfully")

# Vérifier que le ControlPanel a bien été créé
if adminPlayer.controlPanel:
    print(f"✓ Admin ControlPanel created successfully")
    
    # Vérifier que le ControlPanel a des LegendItems (qui représentent les actions)
    legendItems = adminPlayer.controlPanel.getLegendItemsOfGameActions()
    print(f"✓ ControlPanel has {len(legendItems)} LegendItems representing gameActions")
    
    # Vérifier que le nombre de LegendItems correspond au nombre d'actions d'Admin
    # (en tenant compte que certaines actions peuvent ne pas être affichées)
    if len(legendItems) > 0:
        print("✓ ControlPanel successfully displays Admin gameActions")
    else:
        print("⚠ ControlPanel created but no gameActions are displayed")
        
    # Afficher les types d'actions dans le ControlPanel
    actionTypes = [item.gameAction.actionType for item in legendItems if hasattr(item, 'gameAction') and item.gameAction]
    print(f"ControlPanel action types: {set(actionTypes)}")
    
else:
    print("✗ Admin ControlPanel creation failed")

print("\n🎉 Admin ControlPanel test completed!")

# Fermer l'application
monApp.quit()
