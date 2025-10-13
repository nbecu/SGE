# Système de BotPlayer pour SGE

## Contexte et découverte

Lors du développement de l'export des logs de gameActions, nous avons découvert que l'exécution directe d'actions via `perform_with()` fonctionne parfaitement pour tous les types de game actions dans SGE. Cette découverte ouvre la possibilité de créer des bots automatisés qui peuvent remplacer des joueurs humains.

## Système d'exécution directe

### Fonctionnement technique

Toutes les game actions dans SGE héritent de `SGAbstractAction` et implémentent la méthode `perform_with()` :

```python
# Exécution directe d'une action
action.perform_with(target_entity, serverUpdate=False)
```

### Types d'actions supportées

- **SGModify** : Modification d'attributs d'entités
- **SGCreate** : Création de nouvelles entités
- **SGMove** : Déplacement d'agents (avec destination)
- **SGActivate** : Activation de méthodes
- **SGDelete** : Suppression d'entités

### Avantages de l'exécution directe

1. **Fiabilité** : Fonctionne pour tous les types d'actions
2. **Contrôle** : Permet de choisir précisément l'action et la cible
3. **Reproductibilité** : Même résultat à chaque exécution
4. **Performance** : Plus rapide que la simulation d'événements UI

## Système de Fallback

### Nécessité des fallbacks

Lors de l'exécution d'actions par des bots, des échecs peuvent survenir :
- Conditions d'autorisation non remplies
- Entité cible invalide
- Limites d'usage atteintes
- Erreurs de contexte

### Implémentation du fallback

```python
def execute_action_with_fallback(bot_player, target_entity):
    """Exécute une action avec système de fallback"""
    try:
        # Tentative d'exécution de l'action choisie
        chosen_action.perform_with(target_entity, serverUpdate=False)
        return True
    except Exception as e:
        print(f"Action échouée: {e}")
        # Fallback : choisir une autre action valide
        try:
            fallback_action = select_alternative_action(bot_player.player.gameActions)
            fallback_action.perform_with(target_entity, serverUpdate=False)
            print("Action de fallback exécutée avec succès")
            return True
        except Exception as e2:
            print(f"Fallback échoué: {e2}")
            return False
```

## Architecture BotPlayer

### Concept de base

Un BotPlayer est un système automatisé qui :
1. **Remplace un joueur humain** dans une simulation
2. **Utilise uniquement les actions du joueur** qu'il remplace
3. **Respecte les contraintes** du système de jeu
4. **Applique une stratégie** de décision

### Stratégies proposées

#### 1. Explorateur
```python
strategy = "explorer"
# - Teste toutes les actions disponibles du joueur
# - Varie les cibles (cellules, agents différents)
# - Prend des risques calculés pour découvrir de nouvelles stratégies
# - Équilibre exploration et exploitation
```

#### 2. Conservateur
```python
strategy = "conservative"
# - Se limite à 2-3 actions préférées du joueur
# - Répète les actions qui ont fonctionné
# - Évite les actions risquées ou complexes
# - Privilégie la stabilité
```

#### 3. Adaptatif
```python
strategy = "adaptive"
# - Apprend des résultats précédents
# - Ajuste ses choix selon le contexte
# - Équilibre exploration/exploitation dynamiquement
# - S'adapte aux autres joueurs
```

### Interface proposée

```python
# Activation d'un bot pour un joueur existant
myModel.enableBotPlayer("Player 1", strategy="explorer")
myModel.enableBotPlayer("Player 2", strategy="conservative")

# Simulation entièrement automatisée
results = myModel.runBotSimulation(
    rounds=100,
    players=["Bot_Explorer", "Bot_Conservative"],
    strategies=["explorer", "conservative"]
)
```

## Code de référence

### Exécution directe (test_export_with_actions.py)

```python
# Exécution d'actions de modification
target_cell = Cell.getCell(x=2, y=2)
if target_cell:
    modifyAction.perform_with(target_cell, serverUpdate=False)
    print(f"Action de modification exécutée sur cellule {target_cell.id}")

# Exécution d'actions de création
target_cell2 = Cell.getCell(x=4, y=4)
if target_cell2:
    createAction.perform_with(target_cell2, serverUpdate=False)
    print(f"Action de création exécutée sur cellule {target_cell2.id}")

# Exécution d'actions sur plusieurs rounds
myModel.timeManager.nextPhase()
target_cell3 = Cell.getCell(x=1, y=3)
if target_cell3:
    modifyAction.perform_with(target_cell3, serverUpdate=False)
    print(f"Action de modification exécutée sur cellule {target_cell3.id}")
```

### Système de fallback (test_export_realistic_user_interaction.py)

```python
# Simulation d'événement avec fallback
try:
    # Créer un événement de clic simulé
    click_pos = QPoint(10, 10)
    mouse_event = QMouseEvent(
        QMouseEvent.MouseButtonPress,
        click_pos,
        Qt.LeftButton,
        Qt.LeftButton,
        Qt.NoModifier
    )
    
    # Déclencher l'événement sur la vue de la cellule
    target_cell.view.mousePressEvent(mouse_event)
    actions_executed += 1
    print("Action exécutée avec succès!")
    
except Exception as e:
    print(f"Erreur lors de la simulation du clic: {e}")
    # Fallback: exécuter l'action directement
    try:
        selectable_item.gameAction.perform_with(target_cell, serverUpdate=False)
        actions_executed += 1
        print("Action exécutée directement (fallback)")
    except Exception as e2:
        print(f"Erreur fallback: {e2}")
```

## Applications possibles

### 1. Tests automatisés
- Validation de fonctionnalités
- Tests de régression
- Tests de performance
- Tests de stress

### 2. Analyses de sensibilité
- Équilibrage de jeux
- Analyse de stratégies
- Simulation de milliers de parties
- Optimisation de paramètres

### 3. Débogage et développement
- Tests sans intervention humaine
- Validation de nouvelles fonctionnalités
- Tests de compatibilité
- Validation de corrections

### 4. Recherche et analyse
- Études comportementales
- Analyse de stratégies optimales
- Simulation de scénarios complexes
- Génération de données de test

## Implémentation technique

### Structure de base

```python
class BotPlayer:
    def __init__(self, player, strategy="random"):
        self.player = player
        self.strategy = strategy
        self.available_actions = player.gameActions
        self.action_history = []
        self.success_rate = {}
        self.target_preferences = {}
    
    def choose_action(self):
        """Choisit une action selon la stratégie"""
        valid_actions = [action for action in self.available_actions 
                        if action.numberUsed < action.number]
        return self.select_based_on_strategy(valid_actions)
    
    def choose_target(self, action):
        """Choisit une cible pour l'action"""
        # Implémentation selon la stratégie
        pass
    
    def execute_turn(self):
        """Exécute un tour complet du bot"""
        action = self.choose_action()
        target = self.choose_target(action)
        return self.execute_action_with_fallback(action, target)
```

### Intégration avec SGE

```python
# Extension de SGModel
def enableBotPlayer(self, player_name, strategy="random"):
    """Active un bot pour remplacer un joueur humain"""
    if player_name in self.players:
        player = self.players[player_name]
        bot = BotPlayer(player, strategy)
        self.bot_players[player_name] = bot
        print(f"Bot activé pour {player_name} avec stratégie {strategy}")

def runBotSimulation(self, rounds=10, **kwargs):
    """Lance une simulation entièrement automatisée"""
    # Implémentation de la simulation avec bots
    pass
```

## Bénéfices attendus

1. **Automatisation** : Tests et simulations sans intervention humaine
2. **Reproductibilité** : Résultats identiques à chaque exécution
3. **Scalabilité** : Simulation de milliers de parties
4. **Analyse** : Données statistiques riches
5. **Développement** : Validation rapide des fonctionnalités
6. **Recherche** : Outil puissant pour l'analyse de stratégies

## Priorité

**Haute** - Cette fonctionnalité transformerait SGE en une plateforme de simulation automatisée puissante, ouvrant de nouvelles possibilités pour la recherche, le développement et l'analyse de jeux de simulation.
