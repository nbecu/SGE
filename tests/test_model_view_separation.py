"""
Test de validation pour la séparation Model-View
Ce test valide le comportement actuel et prépare la nouvelle architecture
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from mainClasses.SGModel import SGModel
from mainClasses.SGGrid import SGGrid
from mainClasses.SGEntityDef import SGCellDef, SGAgentDef
from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell

class TestModelViewSeparation:
    """Test class pour valider la séparation Model-View"""
    
    def __init__(self):
        self.app = QApplication([])
        self.model = SGModel()
        self.setup_test_environment()
    
    def setup_test_environment(self):
        """Configure l'environnement de test avec une grille simple"""
        # Créer une grille 3x3
        self.grid = SGGrid(self.model, "test_grid", 3, 3, "square", 50, 5)
        self.model.addGrid(self.grid)
        
        # Créer une définition de cellule
        self.cell_def = SGCellDef(
            self.grid, 
            "square", 
            50, 
            entDefAttributesAndValues={"value": 0},
            defaultColor="white",
            entityName="test_cell"
        )
        
        # Créer une définition d'agent
        self.agent_def = SGAgentDef(
            self.model,
            "test_agent",
            "circleAgent",
            30,
            entDefAttributesAndValues={"health": 100, "energy": 50},
            defaultColor="blue",
            locationInEntity="cell"
        )
        
        # Créer des cellules
        self.cells = {}
        for x in range(1, 4):
            for y in range(1, 4):
                cell = self.cell_def.newEntityAtCoords(x, y)
                self.cells[(x, y)] = cell
        
        # Créer un agent dans la cellule (1,1)
        self.agent = self.agent_def.newEntityAtCoords(1, 1)
        
    def test_current_agent_movement(self):
        """Test le déplacement actuel d'un agent"""
        print("=== Test du déplacement actuel d'agent ===")
        
        # Vérifier l'état initial
        initial_cell = self.agent.cell
        initial_health = self.agent.value("health")
        initial_energy = self.agent.value("energy")
        agent_id = self.agent.id
        
        print(f"Agent initial: ID={agent_id}, Cellule=({initial_cell.xCoord},{initial_cell.yCoord})")
        print(f"État initial: health={initial_health}, energy={initial_energy}")
        
        # Simuler un déplacement (actuellement: tuer + recréer)
        target_cell = self.cells[(2, 2)]
        
        # Sauvegarder l'état avant déplacement
        saved_attributes = self.agent.dictAttributes.copy()
        saved_id = self.agent.id
        
        # Supprimer l'agent de sa cellule actuelle
        if self.agent in initial_cell.agents:
            initial_cell.agents.remove(self.agent)
        
        # Recréer l'agent dans la nouvelle cellule
        new_agent = SGAgent(
            target_cell,
            self.agent.size,
            saved_attributes,
            self.agent.classDef.povShapeColor,
            self.agent.classDef,
            self.agent.defaultImage,
            self.agent.popupImage
        )
        
        # Vérifier les différences
        print(f"\nAprès déplacement:")
        print(f"Nouvel agent: ID={new_agent.id}, Cellule=({new_agent.cell.xCoord},{new_agent.cell.yCoord})")
        print(f"État: health={new_agent.value('health')}, energy={new_agent.value('energy')}")
        
        # Problèmes identifiés
        print(f"\nPROBLÈMES IDENTIFIÉS:")
        print(f"1. ID différent: {saved_id} -> {new_agent.id}")
        print(f"2. Instance différente: {self.agent is new_agent}")
        print(f"3. Références perdues: Les autres objets qui référencent l'ancien agent")
        
        return {
            "old_agent": self.agent,
            "new_agent": new_agent,
            "problems": {
                "id_changed": saved_id != new_agent.id,
                "instance_changed": self.agent is not new_agent,
                "references_lost": True
            }
        }
    
    def test_agent_state_preservation(self):
        """Test la préservation de l'état d'un agent"""
        print("\n=== Test de préservation d'état ===")
        
        # Modifier l'état de l'agent
        self.agent.setValue("health", 75)
        self.agent.setValue("energy", 25)
        
        # Ajouter des watchers (simulation d'indicateurs)
        watcher_count = len(self.agent.watchers)
        
        print(f"État modifié: health={self.agent.value('health')}, energy={self.agent.value('energy')}")
        print(f"Watchers: {watcher_count}")
        
        # Simuler un déplacement
        target_cell = self.cells[(3, 3)]
        saved_attributes = self.agent.dictAttributes.copy()
        
        # Recréer l'agent
        new_agent = SGAgent(
            target_cell,
            self.agent.size,
            saved_attributes,
            self.agent.classDef.povShapeColor,
            self.agent.classDef,
            self.agent.defaultImage,
            self.agent.popupImage
        )
        
        print(f"\nAprès déplacement:")
        print(f"État: health={new_agent.value('health')}, energy={new_agent.value('energy')}")
        print(f"Watchers: {len(new_agent.watchers)}")
        
        # Vérifier ce qui est préservé
        state_preserved = (
            new_agent.value("health") == 75 and
            new_agent.value("energy") == 25
        )
        watchers_preserved = len(new_agent.watchers) == watcher_count
        
        print(f"\nRÉSULTATS:")
        print(f"État préservé: {state_preserved}")
        print(f"Watchers préservés: {watchers_preserved}")
        
        return {
            "state_preserved": state_preserved,
            "watchers_preserved": watchers_preserved
        }
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("🚀 Démarrage des tests de séparation Model-View")
        print("=" * 50)
        
        # Test 1: Déplacement actuel
        movement_result = self.test_current_agent_movement()
        
        # Test 2: Préservation d'état
        state_result = self.test_agent_state_preservation()
        
        # Résumé
        print("\n" + "=" * 50)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 50)
        
        problems = movement_result["problems"]
        print(f"Problèmes identifiés:")
        print(f"  - ID change lors du déplacement: {problems['id_changed']}")
        print(f"  - Instance différente: {problems['instance_changed']}")
        print(f"  - Références perdues: {problems['references_lost']}")
        
        print(f"\nPréservation d'état:")
        print(f"  - État préservé: {state_result['state_preserved']}")
        print(f"  - Watchers préservés: {state_result['watchers_preserved']}")
        
        print(f"\n🎯 CONCLUSION:")
        print(f"La séparation Model-View est nécessaire pour:")
        print(f"  1. Préserver l'identité des agents")
        print(f"  2. Maintenir les références")
        print(f"  3. Permettre un déplacement fluide")
        
        return {
            "movement_result": movement_result,
            "state_result": state_result
        }

if __name__ == "__main__":
    test = TestModelViewSeparation()
    results = test.run_all_tests()
