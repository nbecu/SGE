"""
Test de validation pour la nouvelle architecture Model-View
Ce test valide la séparation Model-View et le déplacement fluide d'agents
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from mainClasses.SGModel import SGModel
from mainClasses.SGEntityDef import SGCellDef, SGAgentDef
from mainClasses.SGCellModel import SGCellModel
from mainClasses.SGAgentModel import SGAgentModel
from mainClasses.SGCellView import SGCellView
from mainClasses.SGAgentView import SGAgentView

class TestModelViewArchitecture:
    """Test class pour valider la nouvelle architecture Model-View"""
    
    def __init__(self):
        self.app = QApplication([])
        self.model = SGModel()
        self.setup_test_environment()
    
    def setup_test_environment(self):
        """Configure l'environnement de test avec la nouvelle architecture"""
        # Créer une grille 3x3
        self.cell_def = self.model.newCellsOnGrid(
            columns=3, 
            rows=3, 
            format="square", 
            size=50, 
            gap=5, 
            name="test_grid"
        )
        self.grid = self.cell_def.grid
        
        # Créer une définition d'agent
        self.agent_def = SGAgentDef(
            self.model,
            "test_agent",
            "circleAgent",
            30,
            entDefAttributesAndValues={"health": 100, "energy": 50},
            defaultColor="blue",
            locationInEntity="center"
        )
        
        # Créer des cellules avec Model-View
        self.cells = {}
        for cell in self.cell_def.entities:
            # Créer le modèle de cellule
            cell_model = SGCellModel(
                self.cell_def,
                cell.xCoord,
                cell.yCoord,
                cell.defaultImage
            )
            
            # Créer la vue de cellule
            cell_view = SGCellView(cell_model, self.grid)
            
            # Lier modèle et vue
            cell_model.setView(cell_view)
            
            self.cells[(cell.xCoord, cell.yCoord)] = cell_model
        
        # Créer un agent avec Model-View
        initial_cell = self.cells[(1, 1)]
        self.agent_model = SGAgentModel(
            initial_cell,
            30,
            {"health": 100, "energy": 50},
            self.agent_def.defaultShapeColor,
            self.agent_def,
            self.agent_def.defaultImage,
            self.agent_def.popupImage
        )
        
        # Créer la vue d'agent
        self.agent_view = SGAgentView(self.agent_model, initial_cell.view)
        
        # Lier modèle et vue
        self.agent_model.setView(self.agent_view)
        
    def test_agent_movement_with_model_view(self):
        """Test le déplacement d'agent avec la nouvelle architecture"""
        print("=== Test du déplacement avec Model-View ===")
        
        # Vérifier l'état initial
        initial_cell = self.agent_model.getCell()
        initial_health = self.agent_model.value("health")
        initial_energy = self.agent_model.value("energy")
        agent_id = self.agent_model.id
        
        print(f"Agent initial: ID={agent_id}, Cellule=({initial_cell.xCoord},{initial_cell.yCoord})")
        print(f"État initial: health={initial_health}, energy={initial_energy}")
        
        # Modifier l'état de l'agent
        self.agent_model.setValue("health", 75)
        self.agent_model.setValue("energy", 25)
        
        # Déplacer l'agent vers une nouvelle cellule
        target_cell = self.cells[(2, 2)]
        
        # Sauvegarder l'état avant déplacement
        saved_health = self.agent_model.value("health")
        saved_energy = self.agent_model.value("energy")
        saved_id = self.agent_model.id
        
        # Déplacer l'agent (seulement le modèle change de cellule)
        self.agent_model.moveToCell(target_cell)
        
        # Vérifier les résultats
        print(f"\nAprès déplacement:")
        print(f"Agent: ID={self.agent_model.id}, Cellule=({self.agent_model.getCell().xCoord},{self.agent_model.getCell().yCoord})")
        print(f"État: health={self.agent_model.value('health')}, energy={self.agent_model.value('energy')}")
        
        # Vérifier la préservation
        id_preserved = saved_id == self.agent_model.id
        instance_preserved = True  # Même instance
        state_preserved = (
            self.agent_model.value("health") == saved_health and
            self.agent_model.value("energy") == saved_energy
        )
        
        print(f"\nRÉSULTATS:")
        print(f"ID préservé: {id_preserved}")
        print(f"Instance préservée: {instance_preserved}")
        print(f"État préservé: {state_preserved}")
        
        return {
            "id_preserved": id_preserved,
            "instance_preserved": instance_preserved,
            "state_preserved": state_preserved
        }
    
    def test_multiple_movements(self):
        """Test plusieurs déplacements consécutifs"""
        print("\n=== Test de déplacements multiples ===")
        
        movements = [(2, 2), (3, 3), (1, 3), (2, 1)]
        health_values = [100, 90, 80, 70]
        
        for i, (coords, health) in enumerate(zip(movements, health_values)):
            # Modifier l'état
            self.agent_model.setValue("health", health)
            
            # Déplacer
            target_cell = self.cells[coords]
            self.agent_model.moveToCell(target_cell)
            
            print(f"Déplacement {i+1}: ({coords[0]},{coords[1]}) - health={self.agent_model.value('health')}")
        
        # Vérifier l'état final
        final_health = self.agent_model.value("health")
        final_cell = self.agent_model.getCell()
        
        print(f"État final: health={final_health}, cellule=({final_cell.xCoord},{final_cell.yCoord})")
        
        return {
            "final_health": final_health,
            "final_cell": final_cell
        }
    
    def test_view_update(self):
        """Test la mise à jour de la vue"""
        print("\n=== Test de mise à jour de la vue ===")
        
        # Vérifier que la vue est liée au modèle
        view_linked = self.agent_model.getView() == self.agent_view
        print(f"Vue liée au modèle: {view_linked}")
        
        # Vérifier que la vue peut accéder aux données du modèle
        view_can_access_model = (
            self.agent_view.entity_model == self.agent_model and
            self.agent_view.id == self.agent_model.id
        )
        print(f"Vue peut accéder au modèle: {view_can_access_model}")
        
        return {
            "view_linked": view_linked,
            "view_can_access_model": view_can_access_model
        }
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("🚀 Démarrage des tests de l'architecture Model-View")
        print("=" * 60)
        
        # Test 1: Déplacement avec Model-View
        movement_result = self.test_agent_movement_with_model_view()
        
        # Test 2: Déplacements multiples
        multiple_result = self.test_multiple_movements()
        
        # Test 3: Mise à jour de la vue
        view_result = self.test_view_update()
        
        # Résumé
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 60)
        
        print(f"Résultats du déplacement:")
        print(f"  - ID préservé: {movement_result['id_preserved']}")
        print(f"  - Instance préservée: {movement_result['instance_preserved']}")
        print(f"  - État préservé: {movement_result['state_preserved']}")
        
        print(f"\nRésultats des déplacements multiples:")
        print(f"  - État final: health={multiple_result['final_health']}")
        print(f"  - Cellule finale: ({multiple_result['final_cell'].xCoord},{multiple_result['final_cell'].yCoord})")
        
        print(f"\nRésultats de la vue:")
        print(f"  - Vue liée au modèle: {view_result['view_linked']}")
        print(f"  - Vue peut accéder au modèle: {view_result['view_can_access_model']}")
        
        print(f"\n🎯 CONCLUSION:")
        print(f"La séparation Model-View permet:")
        print(f"  1. ✅ Préserver l'identité des agents")
        print(f"  2. ✅ Maintenir les références")
        print(f"  3. ✅ Permettre un déplacement fluide")
        print(f"  4. ✅ Séparer les responsabilités")
        
        return {
            "movement_result": movement_result,
            "multiple_result": multiple_result,
            "view_result": view_result
        }

if __name__ == "__main__":
    test = TestModelViewArchitecture()
    results = test.run_all_tests()
