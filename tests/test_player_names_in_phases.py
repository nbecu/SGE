import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mainClasses.SGSGE import *
from PyQt6 import QtWidgets

@pytest.fixture(scope="module")
def app():
    """Fixture pour créer l'application Qt"""
    return QtWidgets.QApplication([])

@pytest.fixture
def model(app):
    """Fixture pour créer un modèle de test avec des joueurs"""
    model = SGModel(800, 600, windowTitle="Test Player Names in Phases")
    
    # Créer une grille simple
    Cell = model.newCellsOnGrid(5, 5, "square", size=50, gap=2)
    Cell.setEntities("status", "empty")
    
    # Créer des joueurs
    Player1 = model.newPlayer("Player 1")
    Player2 = model.newPlayer("Player 2")
    Player3 = model.newPlayer("Player 3")
    
    # Ajouter des actions aux joueurs
    Player1.addGameAction(model.newModifyAction(Cell, {"status": "player1"}, 3))
    Player2.addGameAction(model.newModifyAction(Cell, {"status": "player2"}, 3))
    Player3.addGameAction(model.newModifyAction(Cell, {"status": "player3"}, 3))
    
    yield model
    
    # Nettoyer
    model.close()

def test_phase_with_player_instances(model):
    """Test: Créer une phase avec des instances de joueurs"""
    # Créer une phase avec des instances de joueurs
    Player1 = model.getPlayer("Player 1")
    Player2 = model.getPlayer("Player 2")
    phase = model.newPlayPhase("Test Phase 1", [Player1, Player2])
    
    # Vérifier que les joueurs autorisés sont corrects
    authorized_players = phase.authorizedPlayers
    assert len(authorized_players) == 2, f"Attendu 2 joueurs, obtenu {len(authorized_players)}"
    assert Player1 in authorized_players, "Player1 devrait être dans les joueurs autorisés"
    assert Player2 in authorized_players, "Player2 devrait être dans les joueurs autorisés"

def test_phase_with_player_names(model):
    """Test: Créer une phase avec des noms de joueurs"""
    # Créer une phase avec des noms de joueurs
    phase = model.newPlayPhase("Test Phase 2", ["Player 1", "Player 2"])
    
    # Vérifier que les joueurs autorisés sont corrects
    authorized_players = phase.authorizedPlayers
    assert len(authorized_players) == 2, f"Attendu 2 joueurs, obtenu {len(authorized_players)}"
    
    Player1 = model.getPlayer("Player 1")
    Player2 = model.getPlayer("Player 2")
    assert Player1 in authorized_players, "Player1 devrait être dans les joueurs autorisés"
    assert Player2 in authorized_players, "Player2 devrait être dans les joueurs autorisés"

def test_phase_with_admin_string(model):
    """Test: Créer une phase avec 'Admin' comme chaîne"""
    # Créer une phase avec 'Admin' comme chaîne
    phase = model.newPlayPhase("Test Phase 3", ["Admin", "Player 1"])
    
    # Vérifier que les joueurs autorisés sont corrects
    authorized_players = phase.authorizedPlayers
    assert len(authorized_players) == 2, f"Attendu 2 joueurs, obtenu {len(authorized_players)}"
    
    # Vérifier que Admin est présent
    admin_player = model.getAdminPlayer()
    Player1 = model.getPlayer("Player 1")
    assert admin_player in authorized_players, "Admin devrait être dans les joueurs autorisés"
    assert Player1 in authorized_players, "Player1 devrait être dans les joueurs autorisés"

def test_phase_with_mixed_types(model):
    """Test: Créer une phase avec un mélange d'instances et de noms"""
    # Créer une phase avec un mélange
    Player1 = model.getPlayer("Player 1")
    phase = model.newPlayPhase("Test Phase 4", [Player1, "Player 2", "Admin"])
    
    # Vérifier que les joueurs autorisés sont corrects
    authorized_players = phase.authorizedPlayers
    assert len(authorized_players) == 3, f"Attendu 3 joueurs, obtenu {len(authorized_players)}"
    
    # Vérifier que tous les joueurs sont présents
    admin_player = model.getAdminPlayer()
    Player2 = model.getPlayer("Player 2")
    assert Player1 in authorized_players, "Player1 devrait être dans les joueurs autorisés"
    assert Player2 in authorized_players, "Player2 devrait être dans les joueurs autorisés"
    assert admin_player in authorized_players, "Admin devrait être dans les joueurs autorisés"

def test_phase_with_invalid_player_name(model):
    """Test: Créer une phase avec un nom de joueur invalide"""
    # Créer une phase avec un nom de joueur invalide
    phase = model.newPlayPhase("Test Phase 5", ["Player 1", "Invalid Player", "Player 2"])
    
    # Vérifier que seuls les joueurs valides sont présents
    authorized_players = phase.authorizedPlayers
    assert len(authorized_players) == 2, f"Attendu 2 joueurs, obtenu {len(authorized_players)}"
    
    Player1 = model.getPlayer("Player 1")
    Player2 = model.getPlayer("Player 2")
    assert Player1 in authorized_players, "Player1 devrait être dans les joueurs autorisés"
    assert Player2 in authorized_players, "Player2 devrait être dans les joueurs autorisés"

def test_phase_with_none_active_players(model):
    """Test: Créer une phase avec activePlayers=None (tous les joueurs)"""
    # Créer une phase avec activePlayers=None
    phase = model.newPlayPhase("Test Phase 6", None)
    
    # Vérifier que tous les joueurs sont présents
    authorized_players = phase.authorizedPlayers
    expected_count = len(model.users)  # Tous les utilisateurs
    assert len(authorized_players) == expected_count, f"Attendu {expected_count} joueurs, obtenu {len(authorized_players)}"

def test_model_phase_delegation(model):
    """Test: Vérifier que la délégation fonctionne aussi pour les phases modèle"""
    # Créer une phase modèle via la délégation
    model_action = model.newModelAction(lambda: print("Test action"))
    phase = model.newModelPhase(actions=model_action, name="Test Model Phase")
    
    # Vérifier que la phase a été créée
    assert phase is not None, "La phase modèle devrait être créée"
    assert phase.name == "Test Model Phase", "Le nom de la phase devrait être correct"

# Test de régression pour vérifier que la fonctionnalité complète fonctionne
def test_all_player_names_functionality(model):
    """Test de régression: Vérifie que toutes les fonctionnalités de conversion fonctionnent"""
    print("🚀 Test de régression: Conversion automatique des noms de joueurs")
    
    # Test avec différents types d'entrées
    test_cases = [
        (["Player 1", "Player 2"], 2, "noms de joueurs"),
        (["Admin", "Player 1"], 2, "Admin + nom"),
        (["Player 1", "Invalid Player", "Player 2"], 2, "nom invalide"),
        (None, len(model.users), "tous les joueurs")
    ]
    
    for active_players, expected_count, description in test_cases:
        phase = model.newPlayPhase(f"Test {description}", active_players)
        authorized_players = phase.authorizedPlayers
        assert len(authorized_players) == expected_count, f"Échec pour {description}: attendu {expected_count}, obtenu {len(authorized_players)}"
    
    print("✅ Test de régression réussi")
