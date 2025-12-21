# Distributed Game System - Specification Document V2

## Overview

This document specifies the development of a distributed multiplayer game system for SGE (Simulation Game Engine) that allows multiple instances of a game model to run on different machines and synchronize via MQTT.

**Key Principle**: The distributed game system builds upon the existing `SGMQTTManager` infrastructure, extending it with session management capabilities rather than replacing it.

**Topic Naming Convention**: 
- **Game topics**: Use `game_` prefix (e.g., `game_gameAction_performed`, `game_nextTurn`)
- **Session topics**: Use `session_` prefix (e.g., `session_player_registration`, `session_seed_sync`)
- This clear distinction allows easy routing and extensibility for future message types
- Centralized topic lists in each class enable easy addition of new topics without modifying routing logic

**Topic Naming Convention**: 
- **Game topics**: Use `game_` prefix (e.g., `game_gameAction_performed`, `game_nextTurn`)
- **Session topics**: Use `session_` prefix (e.g., `session_player_registration`, `session_seed_sync`)
- This clear distinction allows easy routing and extensibility for future message types

## Goals

- Enable distributed multiplayer games with minimal code changes in model scripts
- One instance per player (one model execution = one player)
- Synchronized random seed across all instances in a session
- User-friendly interface for connection management
- Automatic filtering of players and phases based on assigned player
- Session isolation via MQTT topics
- **Build upon existing `SGMQTTManager` infrastructure**

## ⚠️ CRITICAL IMPLEMENTATION NOTES

**⚠️ À LIRE EN PREMIER avant toute implémentation ⚠️**

### Principe Architectural Fondamental

**SGMQTTManager est une classe EXISTANTE qui fonctionne bien avec `launch_withMQTT()`.**
**Le système distribué doit S'APPUYER sur cette infrastructure, pas la remplacer.**

- `SGMQTTManager` gère TOUS les messages de jeu (`game_gameAction_performed`, `game_nextTurn`, `game_execute_method`)
- `SGDistributedSessionManager` gère UNIQUEMENT les topics de session (`session_player_registration`, `session_seed_sync`)
- Les deux classes travaillent ENSEMBLE, pas l'une à la place de l'autre

### Ordre d'Initialisation CRITIQUE

**PROBLÈME IDENTIFIÉ**: Si `setMQTTProtocol()` est appelé deux fois, la connexion MQTT est réinitialisée, causant des problèmes.

**SOLUTION**:
1. `setMQTTProtocol()` doit être appelé **UNE SEULE FOIS** dans `SGDistributedGameDialog._connectToBroker()`
2. `launch_withMQTT()` doit **RÉUTILISER** la connexion existante, pas en créer une nouvelle
3. Vérifier si connexion existe déjà avant d'appeler `setMQTTProtocol()`

**Code correct pour `launch_withMQTT()`**:
```python
def launch_withMQTT(self, majType, broker_host="localhost", broker_port=1883, session_id=None):
    # Use session_id from distributedConfig if available
    if session_id is None and self.isDistributed():
        session_id = self.distributedConfig.session_id
    
    # CRITICAL: Check if MQTT is already initialized (from enableDistributedGame dialog)
    if (self.mqttManager.client and 
        self.mqttManager.client.is_connected() and
        self.mqttManager.session_id == session_id):
        # Reuse existing connection - just update majType if needed
        self.model.mqttMajType = majType
    else:
        # Initialize new connection (only if not already connected)
        self.mqttManager.setMQTTProtocol(majType, broker_host, broker_port, session_id=session_id)
    
    # Launch the game (don't call self.launch() to avoid recursion)
    self.initBeforeShowing()
    self.show()
    self.initAfterOpening()
```

### Gestion des Handlers MQTT

**PROBLÈME IDENTIFIÉ**: Si `syncSeed()` forward les messages non-seed au handler original, cela peut causer un double traitement.

**SOLUTION**:
- `syncSeed()` installe un handler temporaire **UNIQUEMENT** pour le topic `session_seed_sync`
- Ce handler **NE DOIT PAS** forwarder les autres messages
- Le handler doit être restauré immédiatement après synchronisation
- Les messages de jeu continuent d'être gérés par `SGMQTTManager.on_message`

**Code correct pour `syncSeed()`**:
```python
def syncSeed(self, session_id, shared_seed=None, timeout=5):
    seed_topic = f"{session_id}/session_seed_sync"
    self.mqtt_manager.client.subscribe(seed_topic)
    
    # Save original handler
    original_on_message = self.mqtt_manager.client.on_message
    
    def seed_message_handler(client, userdata, msg):
        if msg.topic == seed_topic:
            # Process session_seed_sync message ONLY
            try:
                msg_dict = json.loads(msg.payload.decode("utf-8"))
                if msg_dict['clientId'] != self.mqtt_manager.clientId:
                    self.synced_seed = msg_dict['seed']
                    self.seed_received = True
                    self.seedReceived.emit(self.synced_seed)
                    # Restore original handler immediately
                    self.mqtt_manager.client.on_message = original_on_message
            except Exception as e:
                print(f"Error processing seed message: {e}")
        # CRITICAL: Do NOT forward other messages - they are handled by SGMQTTManager
    
    # Install temporary handler
    self.mqtt_manager.client.on_message = seed_message_handler
    
    # Wait for seed or generate if leader
    # ... (rest of implementation)
    
    # Restore original handler before returning
    self.mqtt_manager.client.on_message = original_on_message
    return self.synced_seed
```

### Séparation des Responsabilités

**SGMQTTManager** (existing):
- Gère la connexion MQTT complète
- Traite TOUS les messages de jeu
- **NE TRAITE PAS** les topics de session (`session_player_registration`, `session_seed_sync`)

**SGDistributedSessionManager** (new):
- Gère UNIQUEMENT les topics de session
- **NE TRAITE PAS** les messages de jeu
- Travaille avec `SGMQTTManager`, ne le remplace pas

## Architecture

### Core Components

1. **SGDistributedGameConfig** - Configuration class storing distributed game parameters
2. **SGDistributedGameDialog** - Dialog for user to select assigned player and manage session
3. **SGConnectionStatusWidget** - Persistent widget showing connection status
4. **SGDistributedSessionManager** - Manages session-level operations (player registration, seed sync)
5. **SGMQTTManager** (existing, enhanced) - Handles all MQTT communication and game synchronization
6. **SGModel** (modified) - Added distributed game methods and hooks

### Architecture Principle: Separation of Concerns

**SGMQTTManager** (existing):
- Manages MQTT connection lifecycle
- Handles ALL game-related MQTT messages (`game_gameAction_performed`, `game_nextTurn`, `game_execute_method`)
- Processes and executes actions from broker
- **Does NOT handle session management topics**

**SGDistributedSessionManager** (new):
- Manages session-level operations ONLY
- Handles `session_player_registration` and `session_seed_sync` topics
- Does NOT interfere with game message handling
- Works alongside `SGMQTTManager`, not replacing it

### Data Flow

```
Model Script
    ↓
enableDistributedGame()
    ↓
Dialog: Select assigned_player + Connect to broker
    ↓
setMQTTProtocol() called ONCE (in dialog)
    ↓
Register player on {session_id}/session_player_registration
    ↓
Sync seed via {session_id}/session_seed_sync
    ↓
Open Connection Status Widget
    ↓
Apply synchronized seed
    ↓
Filter players/phases automatically
    ↓
Launch game (launch_withMQTT() uses existing connection)
```

## 📋 IMPLEMENTATION ORDER

**Implémenter dans cet ordre, tester après chaque phase avant de passer à la suivante.**

### Phase 1: Infrastructure de Base

**Objectif**: Créer les classes de base et ajouter les attributs nécessaires.

1. **Créer `SGDistributedGameConfig`**
   - Classe simple avec attributs de configuration
   - Méthodes: `set_num_players()`, `generate_session_id()`, `validate()`
   - Tests: Instanciation, validation avec différents paramètres

2. **Modifications minimales dans `SGModel`**
   - Ajouter attributs: `self.distributedConfig = None`, `self.distributedSessionManager = None`, `self.connectionStatusWidget = None`
   - Ajouter méthode: `isDistributed()` (simple vérification)
   - Tests: `isDistributed()` retourne False si pas de config

**Validation après Phase 1**:
- [ ] Code compile sans erreurs
- [ ] `SGDistributedGameConfig` peut être instancié
- [ ] `set_num_players()` accepte int et tuple
- [ ] `isDistributed()` retourne False si pas de config
- [ ] Attributs ajoutés à `SGModel` sans casser l'existant

### Phase 2: SGMQTTManager Modifications

**Objectif**: Ajouter support de `session_id` sans casser l'existant.

1. **Modifier `setMQTTProtocol()`**
   - Ajouter paramètre `session_id=None`
   - Stocker `session_id` dans `self.session_id`

2. **Modifier `initMQTT()`**
   - Préfixer topics avec `{session_id}/` si `session_id` présent
   - Garder topics globaux si `session_id=None` (compatibilité ascendante)

3. **Modifier méthodes de publication**
   - `buildNextTurnMsgAndPublishToBroker()`: Préfixer topic si `session_id` présent
   - `buildExeMsgAndPublishToBroker()`: Préfixer topic si `session_id` présent

**Validation après Phase 2**:
- [ ] Code compile sans erreurs
- [ ] `setMQTTProtocol()` accepte `session_id=None` (compatibilité)
- [ ] Topics préfixés avec `{session_id}/` si présent
- [ ] Topics globaux si `session_id=None` (legacy)
- [ ] **CRITICAL**: Exemples existants (`MQTT_GameExample_Player1.py`) fonctionnent toujours
- [ ] Test avec `session_id` et sans `session_id`

### Phase 3: Session Manager

**Objectif**: Créer `SGDistributedSessionManager` pour gérer les topics de session.

1. **Créer `SGDistributedSessionManager`**
   - `registerPlayer()`: Publie sur `{session_id}/session_player_registration`
   - `syncSeed()`: Handler temporaire UNIQUEMENT pour `session_seed_sync`
   - `getConnectedPlayers()`: Cache local des joueurs connectés
   - Signaux PyQt: `playerConnected`, `playerDisconnected`, `seedReceived`

2. **CRITICAL**: `syncSeed()` handler
   - Ne traite QUE le topic `session_seed_sync`
   - Ne forwarde PAS les autres messages
   - Restaure le handler original immédiatement

3. **CRITICAL**: `registerPlayer()` handler
   - Traite les messages `session_player_registration`
   - Forward UNIQUEMENT les topics de jeu (`game_*`) au handler original
   - Utilise `isSessionTopic()` et `mqtt_manager.isGameTopic()` pour le routage
   - Ignore les autres topics de session (ne pas forwarder `session_seed_sync`, etc.)

**Validation après Phase 3**:
- [ ] Code compile sans erreurs
- [ ] `registerPlayer()` publie sur le bon topic
- [ ] `syncSeed()` handler temporaire uniquement pour `session_seed_sync`
- [ ] Handler restauré après synchronisation
- [ ] **CRITICAL**: Pas d'interférence avec les messages de jeu
- [ ] Test isolé: `registerPlayer()` et `syncSeed()` fonctionnent

### Phase 4: Interfaces Utilisateur

**Objectif**: Créer les interfaces pour la gestion de session.

1. **Créer `SGDistributedGameDialog`**
   - UI: Session ID éditable, bouton "New Session", bouton "Connect"
   - `_connectToBroker()`: Appelle `setMQTTProtocol()` **UNE SEULE FOIS**
   - Timer: Met à jour les joueurs disponibles toutes les secondes
   - Validation: Empêche sélection de joueur déjà connecté

2. **Créer `SGConnectionStatusWidget`**
   - Fenêtre séparée (`setWindowFlags(Qt.Window)`)
   - Timer: Auto-refresh toutes les 3 secondes
   - Connexion aux signaux du session manager
   - Affichage du statut du broker et des joueurs

**Validation après Phase 4**:
- [ ] Code compile sans erreurs
- [ ] Dialog s'ouvre et affiche les joueurs
- [ ] Bouton "Connect" établit la connexion MQTT
- [ ] **CRITICAL**: `setMQTTProtocol()` appelé une seule fois
- [ ] Timer met à jour les joueurs disponibles
- [ ] Widget de statut s'affiche comme fenêtre séparée
- [ ] Test avec 2 instances: Dialog fonctionne

### Phase 5: Intégration

**Objectif**: Intégrer tout dans `enableDistributedGame()` et `launch()`.

1. **Créer `enableDistributedGame()` dans `SGModel`**
   - Créer config et session manager
   - Ouvrir dialog
   - Appeler `registerPlayer()` et `syncSeed()` après dialog
   - Ouvrir widget de statut

2. **Modifier `launch()`**
   - Détecter mode distribué avec `isDistributed()`
   - Appeler `launch_withMQTT()` si distribué

3. **Modifier `launch_withMQTT()`**
   - **CRITICAL**: Réutiliser connexion existante si disponible
   - Ne pas appeler `setMQTTProtocol()` si déjà connecté

**Validation après Phase 5**:
- [ ] Code compile sans erreurs
- [ ] `enableDistributedGame()` fonctionne end-to-end
- [ ] **CRITICAL**: `launch_withMQTT()` réutilise la connexion existante
- [ ] Pas de double appel à `setMQTTProtocol()`
- [ ] Seed synchronisé avant `launch()`
- [ ] Test avec 2 instances: Connexion et synchronisation fonctionnent

### Phase 6: Fonctionnalités Automatiques

**Objectif**: Ajouter les fonctionnalités automatiques (visibilité, hooks).

1. **Système de visibilité dans `SGGameSpace`**
   - Ajouter `isVisibleForPlayers` (attribut)
   - Ajouter `setVisibilityForPlayers()` (méthode)
   - Ajouter `_updateVisibility()` (méthode privée)

2. **Hooks dans `SGPlayer.newControlPanel()`**
   - Auto-configurer visibilité en mode distribué
   - Appeler `setVisibilityForPlayers(player.name)`

3. **Hooks dans `SGModel.newPlayer()`**
   - Marquer `player.isRemote` selon joueur assigné
   - `isRemote = True` pour joueurs non-assignés
   - `isRemote = False` pour joueur assigné

**Validation après Phase 6**:
- [ ] Code compile sans erreurs
- [ ] `setVisibilityForPlayers()` fonctionne
- [ ] Control panels visibles uniquement pour leur propriétaire
- [ ] `player.isRemote` correctement défini
- [ ] Test avec 2 instances: Visibilité correcte sur chaque instance

## ✅ VALIDATION CHECKLIST

### Tests de Régression (CRITICAL)

**Avant de considérer l'implémentation terminée, vérifier que l'existant fonctionne toujours:**

- [ ] **`MQTT_GameExample_Player1.py` et `Player2.py` fonctionnent exactement comme avant**
  - Topics globaux fonctionnent toujours
  - Pas de régression dans le comportement MQTT existant

- [ ] **`Sea_Zones.py` (version non-distribuée) fonctionne sans changement**
  - `launch()` fonctionne normalement
  - Pas d'impact sur les jeux locaux

- [ ] **`launch_withMQTT()` en mode legacy fonctionne**
  - Sans `session_id` → topics globaux
  - Avec `session_id` → topics préfixés

### Tests par Phase

**Phase 1**:
- [ ] `SGDistributedGameConfig` instanciation
- [ ] `set_num_players()` avec int et tuple
- [ ] `isDistributed()` retourne False

**Phase 2**:
- [ ] `setMQTTProtocol()` avec et sans `session_id`
- [ ] Topics préfixés correctement
- [ ] Exemples existants fonctionnent

**Phase 3**:
- [ ] `registerPlayer()` publie correctement
- [ ] `syncSeed()` synchronise correctement
- [ ] Pas d'interférence avec messages de jeu

**Phase 4**:
- [ ] Dialog fonctionne
- [ ] Connexion MQTT établie
- [ ] Widget de statut s'affiche

**Phase 5**:
- [ ] `enableDistributedGame()` end-to-end
- [ ] `launch_withMQTT()` réutilise connexion
- [ ] Pas de double initialisation

**Phase 6**:
- [ ] Visibilité fonctionne
- [ ] Hooks automatiques fonctionnent
- [ ] `isRemote` correctement défini

### Tests End-to-End

**Test final avec 2 instances de `Sea_Zones_distributed.py`:**

- [ ] Instance 1: Dialog s'ouvre, connexion établie, joueur sélectionné
- [ ] Instance 2: Dialog s'ouvre, connexion établie, joueur différent sélectionné
- [ ] Seed synchronisé entre les deux instances
- [ ] Phases synchronisées (nextTurn sur instance 1 → instance 2 avance aussi)
- [ ] Actions synchronisées (move sur instance 1 → instance 2 voit le move)
- [ ] Visibilité correcte (chaque instance voit uniquement son propre board)
- [ ] Widget de statut affiche les deux joueurs connectés

## ⚠️ KNOWN PITFALLS & SOLUTIONS

### Piège 1: Double appel à `setMQTTProtocol()`

**Symptôme**: Connexion MQTT réinitialisée, messages perdus, désynchronisation.

**Cause**: `setMQTTProtocol()` appelé dans le dialog ET dans `launch_withMQTT()`.

**Solution**: Vérifier si connexion existe déjà dans `launch_withMQTT()`:
```python
if (self.mqttManager.client and 
    self.mqttManager.client.is_connected() and
    self.mqttManager.session_id == session_id):
    # Réutiliser connexion existante
    self.model.mqttMajType = majType
else:
    # Créer nouvelle connexion
    self.mqttManager.setMQTTProtocol(...)
```

### Piège 2: Handler de messages conflictuel

**Symptôme**: Messages traités deux fois, actions dupliquées, désynchronisation.

**Cause**: `syncSeed()` handler forward les messages non-seed au handler original.

**Solution**: Handler temporaire ne traite QUE `session_seed_sync`, ne forwarde rien d'autre:
```python
def seed_message_handler(client, userdata, msg):
    if msg.topic == seed_topic:
        # Traiter session_seed_sync
        ...
    # CRITICAL: Ne PAS forwarder les autres messages
```

### Piège 3: Topics mal préfixés

**Symptôme**: Messages non reçus, instances non synchronisées.

**Cause**: Topics non préfixés avec `{session_id}/` ou préfixés incorrectement.

**Solution**: Vérifier préfixage dans `SGMQTTManager.initMQTT()`:
```python
if self.session_id:
    self.client.subscribe(f"{self.session_id}/game_gameAction_performed")
    self.client.subscribe(f"{self.session_id}/game_nextTurn")
else:
    # Legacy: topics globaux (sans préfixe session, mais avec préfixe game_)
    self.client.subscribe("game_gameAction_performed")
    self.client.subscribe("game_nextTurn")
```

### Piège 4: Visibilité non mise à jour

**Symptôme**: GameSpaces visibles pour tous les joueurs au lieu d'être filtrés.

**Cause**: `_updateVisibility()` non appelé après configuration.

**Solution**: Appeler `_updateVisibility()` automatiquement dans `setVisibilityForPlayers()`:
```python
def setVisibilityForPlayers(self, players):
    # ... configuration ...
    self._updateVisibility()  # Mise à jour automatique
```

### Piège 5: Seed appliqué trop tard

**Symptôme**: Instances ont des seeds différents malgré synchronisation.

**Cause**: Seed appliqué après des opérations aléatoires dans le modèle.

**Solution**: Appliquer seed immédiatement après synchronisation dans `enableDistributedGame()`:
```python
synced_seed = session_manager.syncSeed(config.session_id, shared_seed)
config.shared_seed = synced_seed
random.seed(synced_seed)  # Appliquer IMMÉDIATEMENT
```

## 💡 CODE EXAMPLES

### Exemple 1: `launch_withMQTT()` réutilisant la connexion

**Code CORRECT**:
```python
def launch_withMQTT(self, majType, broker_host="localhost", broker_port=1883, session_id=None):
    # Use session_id from distributedConfig if available
    if session_id is None and self.isDistributed():
        session_id = self.distributedConfig.session_id
    
    # CRITICAL: Check if MQTT is already initialized
    if (self.mqttManager.client and 
        self.mqttManager.client.is_connected() and
        self.mqttManager.session_id == session_id):
        # Reuse existing connection - just update majType
        self.model.mqttMajType = majType
    else:
        # Initialize new connection (only if not already connected)
        self.mqttManager.setMQTTProtocol(majType, broker_host, broker_port, session_id=session_id)
    
    # Launch the game
    self.initBeforeShowing()
    self.show()
    self.initAfterOpening()
```

**Code INCORRECT** (à éviter):
```python
def launch_withMQTT(self, majType, broker_host="localhost", broker_port=1883, session_id=None):
    # ❌ TOUJOURS appeler setMQTTProtocol() - cause double initialisation
    self.mqttManager.setMQTTProtocol(majType, broker_host, broker_port, session_id=session_id)
    self.launch()  # ❌ Appelle self.launch() qui peut causer récursion
```

### Exemple 2: `syncSeed()` avec handler temporaire correct

**Code CORRECT**:
```python
def syncSeed(self, session_id, shared_seed=None, timeout=5):
    seed_topic = f"{session_id}/session_seed_sync"
    self.mqtt_manager.client.subscribe(seed_topic)
    
    original_on_message = self.mqtt_manager.client.on_message
    
    def seed_message_handler(client, userdata, msg):
        if msg.topic == seed_topic:
            # Traiter uniquement session_seed_sync
            try:
                msg_dict = json.loads(msg.payload.decode("utf-8"))
                if msg_dict['clientId'] != self.mqtt_manager.clientId:
                    self.synced_seed = msg_dict['seed']
                    self.seed_received = True
                    self.seedReceived.emit(self.synced_seed)
                    # Restaurer handler immédiatement
                    self.mqtt_manager.client.on_message = original_on_message
            except Exception as e:
                print(f"Error processing seed message: {e}")
        # ✅ Ne PAS forwarder les autres messages
    
    self.mqtt_manager.client.on_message = seed_message_handler
    
    # Attendre seed ou générer si leader
    # ... (rest of implementation)
    
    # Restaurer handler avant de retourner
    self.mqtt_manager.client.on_message = original_on_message
    return self.synced_seed
```

**Code INCORRECT** (à éviter):
```python
def seed_message_handler(client, userdata, msg):
    if msg.topic == seed_topic:
        # Traiter session_seed_sync
        ...
    else:
        # ❌ Forwarder les autres messages - cause double traitement
        if original_on_message:
            original_on_message(client, userdata, msg)
```

### Exemple 3: Vérification de connexion existante

**Code CORRECT**:
```python
def _checkConnection(self):
    """Check if MQTT connection is established."""
    if (self.model.mqttManager.client and 
        self.model.mqttManager.client.is_connected()):
        self.connection_status = "Connected to broker"
        self.status_label.setText(f"Connection Status: {self.connection_status}")
        self.ok_button.setEnabled(True)
    else:
        # Réessayer
        QTimer.singleShot(500, self._checkConnection)
```

### Exemple 4: Configuration automatique de visibilité

**Code CORRECT dans `SGPlayer.newControlPanel()`**:
```python
def newControlPanel(self, title=None, defaultActionSelected=None):
    control_panel = SGControlPanel(...)
    
    # Auto-configure visibility in distributed mode
    if self.model.isDistributed():
        control_panel.setVisibilityForPlayers(self.name)
    
    return control_panel
```

## API Specification

### Public API for Modeler

#### Method: `enableDistributedGame()`

**Location**: `SGModel.enableDistributedGame()`

**Signature**:
```python
def enableDistributedGame(self,
                         num_players,
                         session_id=None,
                         shared_seed=None,
                         broker_host="localhost",
                         broker_port=1883,
                         mqtt_update_type="Instantaneous"):
    """
    Enable distributed multiplayer game mode.
    Opens dialog for user to select assigned_player and connect to broker.
    All other aspects are handled automatically.
    
    Args:
        num_players (int or tuple): Number of players. Can be:
            - int: Fixed number of players (e.g., 2)
            - tuple: Range of players (min, max) (e.g., (2, 4) for 2-4 players)
            Game can start when number of connected instances is within this range.
        session_id (str, optional): Session ID. Auto-generated if None.
        shared_seed (int, optional): Shared seed. Auto-generated and synced if None.
        broker_host (str): MQTT broker host (default: "localhost")
        broker_port (int): MQTT broker port (default: 1883)
        mqtt_update_type (str): "Instantaneous" or "Phase" (default: "Instantaneous")
    
    Returns:
        SGDistributedGameConfig or None: Configuration object if distributed mode enabled,
                                         None if cancelled or local mode.
    """
```

**Behavior**:
1. Creates `SGDistributedGameConfig` object with provided parameters
2. Creates `SGDistributedSessionManager` instance
3. Opens `SGDistributedGameDialog` for user to:
   - View/edit session_id
   - Connect to MQTT broker (calls `setMQTTProtocol()`)
   - Select assigned_player
4. If user cancels, returns `None` (local mode)
5. If user confirms:
   - Registers player on MQTT topic
   - Synchronizes seed if needed
   - Opens connection status widget
   - Stores config in `self.distributedConfig`
6. Returns config object

**Usage in Model Script**:
```python
myModel.enableDistributedGame(num_players=2)
```

#### Method: `isDistributed()`

**Location**: `SGModel.isDistributed()`

**Signature**:
```python
def isDistributed(self):
    """
    Check if distributed game mode is enabled.
    
    Returns:
        bool: True if distributed mode is enabled, False otherwise
    """
    return hasattr(self, 'distributedConfig') and self.distributedConfig is not None
```

**Usage**:
```python
if myModel.isDistributed():
    # Do distributed-specific logic
```

### Modified Method: `launch()`

**Location**: `SGModel.launch()`

**Modification**:
```python
def launch(self):
    """
    Launch the game.
    Automatically uses MQTT if distributed mode is enabled.
    """
    # Check if distributed mode is enabled
    if self.isDistributed():
        # Automatically launch with MQTT (reuses existing connection)
        self.launch_withMQTT(
            self.distributedConfig.mqtt_update_type,
            broker_host=self.distributedConfig.broker_host,
            broker_port=self.distributedConfig.broker_port,
            session_id=self.distributedConfig.session_id
        )
    else:
        # Normal local launch
        self.initBeforeShowing()
        self.show()
        self.initAfterOpening()
```

### Modified Method: `launch_withMQTT()`

**Location**: `SGModel.launch_withMQTT()`

**Modification**:
```python
def launch_withMQTT(self, majType, broker_host="localhost", broker_port=1883, session_id=None):
    """
    Set the mqtt protocol, then launch the game.
    
    IMPORTANT: In distributed mode, MQTT connection is already established in enableDistributedGame().
    This method should reuse the existing connection if possible, or establish a new one if needed.
    
    Args:
        majType (str): "Phase" or "Instantaneous"
        broker_host (str): MQTT broker host (default: "localhost")
        broker_port (int): MQTT broker port (default: 1883)
        session_id (str, optional): Session ID for topic isolation. 
                                    If None and distributedConfig exists, uses its session_id.
    """
    # Use session_id from distributedConfig if available
    if session_id is None and self.isDistributed():
        session_id = self.distributedConfig.session_id
    
    # Check if MQTT is already initialized (from enableDistributedGame dialog)
    if (self.mqttManager.client and 
        self.mqttManager.client.is_connected() and
        self.mqttManager.session_id == session_id):
        # Reuse existing connection - just update majType if needed
        self.model.mqttMajType = majType
    else:
        # Initialize new connection
        self.mqttManager.setMQTTProtocol(majType, broker_host, broker_port, session_id=session_id)
    
    # Launch the game (don't call self.launch() to avoid recursion)
    self.initBeforeShowing()
    self.show()
    self.initAfterOpening()
```

## Class Specifications

### 1. SGDistributedGameConfig

**File**: `mainClasses/SGDistributedGameConfig.py`

**Purpose**: Stores all distributed game configuration parameters

**Attributes**:
```python
class SGDistributedGameConfig:
    def __init__(self):
        self.distributed_mode = False  # bool: Enable distributed mode
        self.num_players = None  # int or tuple: Number of players (fixed int or (min, max) range)
        self.num_players_min = None  # int: Minimum number of players (extracted from num_players)
        self.num_players_max = None  # int: Maximum number of players (extracted from num_players)
        self.assigned_player_name = None  # str: Name of player assigned to this instance
        self.session_id = None  # str: Unique session identifier
        self.shared_seed = None  # int: Shared random seed
        self.broker_host = "localhost"  # str: MQTT broker host
        self.broker_port = 1883  # int: MQTT broker port
        self.mqtt_update_type = "Instantaneous"  # str: "Instantaneous" or "Phase"
```

**Methods**:
```python
def set_num_players(self, num_players):
    """
    Set number of players (fixed or range).
    
    Args:
        num_players: int (fixed number) or tuple (min, max) range
    """

def generate_session_id(self):
    """Generate a unique session ID (UUID4)"""

def generate_shared_seed(self):
    """Generate a random seed"""

def validate(self):
    """
    Validate configuration parameters.
    
    Returns:
        tuple: (is_valid, error_message)
    """
```

### 2. SGDistributedGameDialog

**File**: `mainClasses/SGDistributedGameDialog.py`

**Purpose**: Dialog for user to select assigned player and manage session connection

**UI Components**:
- **Title**: "Select Your Player"
- **Session ID Section**:
  - Editable text field: Shows current session_id, allows user to enter existing session_id to join
  - "New Session" button: Generates a new UUID session_id
  - Display label: Shows current session_id (small gray text)
- **Number of Players**: Display num_players (fixed or range)
- **Connection Status**: 
  - Label: Shows "Connecting...", "Connected to broker", or error message
  - Updates in real-time
- **Player Selection**:
  - Radio buttons: Shows actual player names from the model (excludes "Admin")
  - Auto-updates: Timer refreshes list every second to show already connected players
  - Visual feedback: Already connected players are disabled/grayed out
  - Auto-selection: If selected player becomes unavailable, automatically selects first available
- **Buttons**:
  - "Cancel": Closes dialog, cancels distributed mode
  - "Connect": Connects to MQTT broker (calls `setMQTTProtocol()`)
  - "OK": Confirms selection and closes dialog (disabled until connection established)

**Behavior**:
1. Dialog opens BEFORE MQTT connection (shows "Connecting...")
2. User can edit session_id or generate new one
3. User clicks "Connect" → `setMQTTProtocol()` is called → MQTT connection established
4. Connection status updates to "Connected to broker"
5. Timer (every 1 second) updates available players list by filtering out already connected players
6. User selects assigned_player from available players
7. User clicks "OK":
   - Validates selection (not already connected)
   - Validates connection is established
   - Closes dialog, returns selected player name

**Key Features**:
- **Session ID Management**: User can join existing session or create new one
- **Real-time Updates**: Timer updates player availability every second
- **Visual Feedback**: Connected players are visually disabled
- **Auto-selection**: Automatically selects first available player if current selection becomes unavailable
- **Connection Validation**: OK button disabled until connection established

**Methods**:
```python
def __init__(self, parent, config, model, session_manager):
    """
    Initialize dialog.
    
    Args:
        parent: Parent widget (SGModel)
        config: SGDistributedGameConfig object
        model: SGModel instance (to retrieve player names)
        session_manager: SGDistributedSessionManager instance
    """

def _generateNewSessionId(self):
    """Generate a new UUID session ID and update UI"""

def _onConnect(self):
    """Handle Connect button click - update session_id and connect to broker"""

def _connectToBroker(self):
    """Connect to MQTT broker by calling setMQTTProtocol()"""

def _checkConnection(self):
    """Check if MQTT connection is established (polling)"""

def updateAvailablePlayers(self):
    """
    Update the list of available players by filtering out already connected players.
    Called by timer every second.
    """

def getSelectedPlayerName(self):
    """
    Returns selected player name (str) or None if cancelled.
    """
```

### 3. SGConnectionStatusWidget

**File**: `mainClasses/SGConnectionStatusWidget.py`

**Purpose**: Persistent widget showing connection status and managing connections

**UI Components**:
- **Header**: "Connection Status" (bold, 12pt)
- **Session ID**: Display current session_id (word-wrapped)
- **Broker Status**:
  - Label: "Broker: {host}:{port}"
  - Status indicator: "[●] Connected" (green) or "[✗] Disconnected" (red)
- **Players List**:
  - QListWidget showing:
    - "✓ {player_name} (You)" - Assigned player (blue, bold)
    - "● {player_name} (Connected)" - Other connected players (green)
    - "⏳ {player_name} (Waiting...)" - Not yet connected (orange)
  - Excludes "Admin" from list
- **Statistics**: "Connected: {n}/{total_players}"
- **Buttons**:
  - "Refresh": Manually refresh connection status
  - "Disconnect": Disconnect from session (with confirmation dialog)

**Behavior**:
1. Opens automatically after MQTT connection is established (in `enableDistributedGame()`)
2. Displays as separate window (`setWindowFlags(Qt.Window)`)
3. Initial size: 350x400 pixels
4. Auto-refresh: Timer updates every 3 seconds
5. Real-time updates: Listens to `playerConnected` and `playerDisconnected` signals
6. Visual indicators: Colors and styles for different player states
7. Can be closed by user but remains available via menu (future enhancement)

**Key Features**:
- **Separate Window**: Independent window, not embedded in main UI
- **Auto-refresh**: Timer updates status every 3 seconds
- **Signal-based Updates**: Listens to session manager signals for real-time updates
- **Visual Feedback**: Color-coded player states
- **Disconnect Functionality**: Allows user to disconnect from session

**Methods**:
```python
def __init__(self, parent, model, distributed_config, session_manager):
    """
    Initialize connection status widget.
    
    Args:
        parent: Parent widget (None for separate window)
        model: SGModel instance
        distributed_config: SGDistributedGameConfig instance
        session_manager: SGDistributedSessionManager instance
    """

def updateConnectionStatus(self):
    """Update connection status from MQTT messages and session manager"""

def _onPlayerConnected(self, player_name):
    """Handle player connected signal from session manager"""

def _onPlayerDisconnected(self, player_name):
    """Handle player disconnected signal from session manager"""

def refreshStatus(self):
    """Manually refresh connection status"""

def disconnect(self):
    """Disconnect from session (with confirmation dialog)"""
```

### 4. SGDistributedSessionManager

**File**: `mainClasses/SGDistributedSessionManager.py`

**Purpose**: Manages session-level operations via MQTT (player registration, seed sync)

**IMPORTANT**: This class handles ONLY session management topics. It does NOT handle game messages (`game_gameAction_performed`, `game_nextTurn`, `game_execute_method`), which are handled by `SGMQTTManager`.

**MQTT Topics Handled**:
- `{session_id}/session_player_registration` - Player registration messages
- `{session_id}/session_seed_sync` - Seed synchronization messages

**MQTT Topics NOT Handled** (handled by SGMQTTManager):
- `{session_id}/game_gameAction_performed` - Game actions
- `{session_id}/game_nextTurn` - Next turn messages
- `{session_id}/game_execute_method` - Method execution

**Centralized Topic Management**:
- `SESSION_TOPICS` - Class-level list: `['player_registration', 'seed_sync']`
- `getSessionTopics(session_id)` - Returns full topic names with session prefix
- `isSessionTopic(topic, session_id)` - Checks if topic is a session topic

**Attributes**:
```python
class SGDistributedSessionManager(QObject):
    def __init__(self, model, mqtt_manager):
        self.model = model
        self.mqtt_manager = mqtt_manager  # Reference to SGMQTTManager
        self.session_id = None
        self.connected_players = {}  # {player_name: client_id}
        self.seed_received = False
        self.synced_seed = None
        self.is_leader = False  # True if this instance generated the seed
```

**Signals**:
```python
playerConnected = pyqtSignal(str)  # Emitted when a player connects
playerDisconnected = pyqtSignal(str)  # Emitted when a player disconnects
seedReceived = pyqtSignal(int)  # Emitted when seed is received
```

**Methods**:
```python
def registerPlayer(self, session_id, assigned_player_name, num_players_min, num_players_max):
    """
    Register this instance as a player in the session.
    
    IMPORTANT: Requires MQTT client to be already connected (via setMQTTProtocol()).
    
    Args:
        session_id (str): Session identifier
        assigned_player_name (str): Name of player assigned to this instance
        num_players_min (int): Minimum number of players required
        num_players_max (int): Maximum number of players allowed
    
    Returns:
        bool: True if registration successful
    
    Raises:
        ValueError: If player name is already registered in this session
    """
    # Subscribe to session_player_registration topic
    # Publish registration message
    # Add self to connected players cache

def syncSeed(self, session_id, shared_seed=None, timeout=5):
    """
    Synchronize random seed across all instances.
    
    IMPORTANT: Requires MQTT client to be already connected.
    Uses temporary message handler ONLY for seed_sync topic.
    Does NOT interfere with game message handling.
    
    Args:
        session_id (str): Session identifier
        shared_seed (int, optional): Seed to use. If None, first instance generates it.
        timeout (int): Maximum wait time in seconds for seed sync
    
    Returns:
        int: Synchronized seed value
    """
    # Subscribe to session_seed_sync topic
    # Install temporary handler ONLY for session_seed_sync messages
    # Wait for seed or generate if leader
    # Restore original handler

def getConnectedPlayers(self, session_id):
    """
    Get list of connected players in the session.
    
    Returns:
        list: List of player names (str) that are currently connected
    
    Note: Maintains local cache updated via MQTT messages.
    """

def isPlayerNameAvailable(self, session_id, player_name):
    """
    Check if a player name is available (not already connected).
    
    Returns:
        bool: True if player name is available, False if already taken
    """

def waitForPlayers(self, session_id, num_players_min, num_players_max, timeout=30):
    """
    Wait for sufficient players to connect (within range).
    
    Returns:
        bool: True if number of connected players is within range, False if timeout
    """

def disconnect(self):
    """Disconnect from session (stop timer, clear cache)"""
```

**Timer**:
- `status_timer`: QTimer that checks connection status every 3 seconds
- Calls `_checkConnectionStatus()` periodically

**Message Handling Strategy**:
- **Seed Sync**: Uses temporary message handler that ONLY processes `session_seed_sync` topic
- **Player Registration**: Messages are processed via handler that ONLY processes `session_player_registration` topic
- **Game Messages**: NOT handled by this class (handled by SGMQTTManager)
- **Topic Routing**: Uses `isSessionTopic()` and `mqtt_manager.isGameTopic()` to route messages correctly

### 5. SGMQTTManager (Existing, Enhanced)

**File**: `mainClasses/SGMQTTManager.py`

**Purpose**: Manages ALL MQTT communication for game synchronization

**Enhancements for Distributed Mode**:
1. **Session ID Support**: Added `session_id` parameter to `setMQTTProtocol()`
2. **Topic Prefixing**: Topics are prefixed with `{session_id}/` if session_id is provided
3. **Backward Compatibility**: If `session_id` is None, uses global topics (legacy behavior)

**Key Methods**:
```python
def setMQTTProtocol(self, majType, broker_host="localhost", broker_port=1883, session_id=None):
    """
    Set the MQTT protocol configuration.
    
    Args:
        majType (str): "Phase" or "Instantaneous"
        broker_host (str): MQTT broker host
        broker_port (int): MQTT broker port
        session_id (str, optional): Session ID for topic isolation
    """

def initMQTT(self):
    """
    Initialize MQTT client and subscribe to game topics.
    
    Subscribes to:
    - {session_id}/game_gameAction_performed (or game_gameAction_performed if no session_id)
    - {session_id}/game_nextTurn (or game_nextTurn if no session_id)
    - {session_id}/game_execute_method (or game_execute_method if no session_id)
    """

def on_message(self, client, userdata, msg):
    """
    Handle incoming MQTT messages.
    
    Processes ONLY game-related topics:
    - game_gameAction_performed
    - game_nextTurn
    - game_execute_method

    Does NOT process session management topics (handled by SGDistributedSessionManager).

**Centralized Topic Management**:
- `GAME_TOPICS` - Class-level list: `['gameAction_performed', 'nextTurn', 'execute_method']` (base names without prefix)
- `getGameTopics(session_id)` - Returns full topic names with session prefix and `game_` prefix
- `isGameTopic(topic, session_id)` - Checks if topic is a game topic
    """
```

**Important**: `SGMQTTManager` does NOT handle `session_player_registration` or `session_seed_sync` topics. These are handled by `SGDistributedSessionManager`.

### 6. SGModel (Modified)

**File**: `mainClasses/SGModel.py`

**New Attributes**:
```python
self.distributedConfig = None  # SGDistributedGameConfig or None
self.distributedSessionManager = None  # SGDistributedSessionManager or None
self.connectionStatusWidget = None  # SGConnectionStatusWidget or None
```

**New Methods**:
```python
def enableDistributedGame(self, ...):
    """Enable distributed multiplayer game mode (see API Specification)"""

def isDistributed(self):
    """Check if distributed game mode is enabled"""
```

**Modified Methods**:
```python
def launch(self):
    """Automatically uses MQTT if distributed mode is enabled"""

def launch_withMQTT(self, ...):
    """Reuses existing MQTT connection if available"""

def newPlayer(self, name, ...):
    """
    Create a new player.
    
    In distributed mode:
    - Sets player.isRemote = True for non-assigned players
    - Sets player.isRemote = False for assigned player
    """
```

**Player Filtering Hook**:
```python
def newPlayer(self, name, attributesAndValues=None):
    player = SGPlayer(self, name, attributesAndValues=attributesAndValues)
    
    # Auto-filter if distributed mode
    if self.isDistributed():
        assigned_player_name = self.distributedConfig.assigned_player_name
        
        if name != assigned_player_name:
            # This is a remote player (exists but not controlled here)
            player.isRemote = True
        else:
            # This is the assigned player for this instance
            player.isRemote = False
    
    self.players[name] = player
    return player
```

### 7. SGGameSpace (Modified)

**File**: `mainClasses/SGGameSpace.py`

**New Attribute**:
```python
self.isVisibleForPlayers = 'all'  # str or list: 'all', 'none', or list of player names
```

**New Methods**:
```python
def setVisibilityForPlayers(self, players):
    """
    Set which players can see this GameSpace.
    
    Args:
        players: Can be:
            - 'all': Visible to all players (default)
            - 'none': Not visible to any player
            - str: Single player name (e.g., "Player 1", "Viticulteur")
            - list: List of player names (e.g., ["Player 1", "Player 2"])
    
    Examples:
        gameSpace.setVisibilityForPlayers('all')
        gameSpace.setVisibilityForPlayers('none')
        gameSpace.setVisibilityForPlayers('Player 1')
        gameSpace.setVisibilityForPlayers(['Player 1', 'Player 2'])
    """
    # Sets self.isVisibleForPlayers
    # Calls self._updateVisibility()

def _updateVisibility(self):
    """
    Update GameSpace visibility based on isVisibleForPlayers and current distributed mode.
    Called automatically when visibility is set or when distributed mode changes.
    
    Behavior:
    - Local mode: Always visible
    - Distributed mode: Visible only if assigned_player_name is in isVisibleForPlayers list
    """
    if not self.model.isDistributed():
        self.setVisible(True)
        return
    
    assigned_player_name = self.model.distributedConfig.assigned_player_name
    
    if self.isVisibleForPlayers == 'all':
        self.setVisible(True)
    elif self.isVisibleForPlayers == 'none':
        self.setVisible(False)
    elif isinstance(self.isVisibleForPlayers, list):
        self.setVisible(assigned_player_name in self.isVisibleForPlayers)
    else:
        self.setVisible(True)  # Default to visible if invalid state
```

**Rendering Behavior**:
- When `isVisibleForPlayers` indicates that a GameSpace is not visible:
  - The GameSpace exists in the model (for synchronization purposes)
  - The GameSpace is NOT rendered (`setVisible(False)`)
  - The GameSpace is NOT clickable (hidden from user interaction)
  - MQTT synchronization still works (all instances have the same GameSpace structure)

### 8. SGPlayer (Modified)

**File**: `mainClasses/SGPlayer.py`

**New Attribute**:
```python
self.isRemote = False  # bool: True if this is a remote player (not controlled by this instance)
```

**Modified Method**:
```python
def newControlPanel(self, title=None, defaultActionSelected=None):
    """
    Create a Player Control Panel.
    
    In distributed mode:
    - Automatically sets visibility to assigned player only
    - Calls controlPanel.setVisibilityForPlayers(self.name)
    """
    control_panel = SGControlPanel(...)
    
    # Auto-configure visibility in distributed mode
    if self.model.isDistributed():
        control_panel.setVisibilityForPlayers(self.name)
    
    return control_panel
```

## MQTT Topic Structure

### Topic Naming Convention

**Two-level prefixing system**:
1. **Session isolation**: All topics are prefixed with `{session_id}/` to isolate sessions
2. **Message type distinction**: Topics use prefixes to distinguish game messages from session messages

**Convention**:
- **Game Topics** use `game_` prefix: `{session_id}/game_*`
- **Session Topics** use `session_` prefix: `{session_id}/session_*`

**Game Topics** (handled by SGMQTTManager):
- `{session_id}/game_gameAction_performed` - Game actions synchronization
- `{session_id}/game_nextTurn` - Next turn coordination
- `{session_id}/game_execute_method` - Method execution

**Session Management Topics** (handled by SGDistributedSessionManager):
- `{session_id}/session_player_registration` - Player registration messages
- `{session_id}/session_seed_sync` - Seed synchronization messages

**Architecture for Extensibility**:
- Each class maintains a centralized list of topics:
  - `SGMQTTManager.GAME_TOPICS` - List of base game topic names (without prefixes): `['gameAction_performed', 'nextTurn', 'execute_method']`
  - `SGDistributedSessionManager.SESSION_TOPICS` - List of base session topic names (without prefixes): `['player_registration', 'seed_sync']`
- Helper methods for topic identification:
  - `SGMQTTManager.getGameTopics(session_id)` - Returns full topic names with `game_` prefix and optional `{session_id}/` prefix
  - `SGMQTTManager.isGameTopic(topic, session_id)` - Check if topic is a game topic
  - `SGDistributedSessionManager.getSessionTopics(session_id)` - Returns full topic names with `session_` prefix and `{session_id}/` prefix
  - `SGDistributedSessionManager.isSessionTopic(topic, session_id)` - Check if topic is a session topic
- This architecture allows easy addition of new topics without modifying routing logic:
  - Add new topic to `GAME_TOPICS` or `SESSION_TOPICS` list
  - Routing logic automatically handles it via `isGameTopic()` or `isSessionTopic()`

**Topic Format**:
- Full format: `{session_id}/game_{base_topic}` or `{session_id}/session_{base_topic}`
- Without session prefix: `game_{base_topic}` or `session_{base_topic}`
- Examples:
  - Game: `abc123/game_gameAction_performed` or `game_gameAction_performed`
  - Session: `abc123/session_player_registration` or `session_player_registration`

**Message Routing Architecture**:
- MQTT client has only ONE active handler at a time (`client.on_message`)
- When `registerPlayer()` is called, it replaces the handler with `registration_message_handler`
- `registration_message_handler` must:
  1. Process `session_player_registration` messages (session)
  2. Forward ONLY `game_*` topics to original handler (game messages)
  3. Ignore other `session_*` topics (other session messages)
- Use centralized methods: `isGameTopic()` and `isSessionTopic()` for routing decisions
- This allows easy addition of new topics without modifying routing logic

**Backward Compatibility**:
- If `session_id` is None, topics are global (no session prefix)
- Format: `game_*` for game topics, `session_*` for session topics
- All topics use the prefix convention (no legacy topics without prefix)
- Existing MQTT games must be updated to use `game_` prefix for topics

### Message Formats

#### Player Registration Message
```json
{
    "clientId": "uuid-hex",
    "assigned_player_name": "Player 1",
    "num_players_min": 2,
    "num_players_max": 4,
    "timestamp": "2024-01-01T12:00:00"
}
```

#### Seed Sync Message
```json
{
    "clientId": "uuid-hex",
    "seed": 42,
    "is_leader": true,
    "timestamp": "2024-01-01T12:00:00"
}
```

## Initialization Order

### Critical: Order of Operations

1. **Model Script**: Calls `enableDistributedGame()`
2. **enableDistributedGame()**: Creates config and session manager
3. **Dialog Opens**: User can edit session_id
4. **User Clicks "Connect"**: Dialog calls `setMQTTProtocol()` → MQTT connection established
5. **User Selects Player**: User selects assigned_player from available players
6. **User Clicks "OK"**: Dialog closes
7. **enableDistributedGame() continues**:
   - Calls `registerPlayer()` → Registers on MQTT topic `{session_id}/session_player_registration`
   - Calls `syncSeed()` → Synchronizes seed via `{session_id}/session_seed_sync` (uses temporary handler)
   - Opens connection status widget
   - Stores config
8. **Model Script**: Calls `myModel.launch()`
9. **launch()**: Detects distributed mode, calls `launch_withMQTT()`
10. **launch_withMQTT()**: Reuses existing MQTT connection (does NOT call `setMQTTProtocol()` again)

### Key Points

- **`setMQTTProtocol()` is called ONCE**: In the dialog's `_connectToBroker()` method
- **`launch_withMQTT()` reuses connection**: Checks if connection exists and reuses it
- **Session manager works alongside MQTT manager**: Does NOT replace it
- **Seed sync uses temporary handler**: Does NOT interfere with game message handling
- **Topic routing**: Uses `isGameTopic()` and `isSessionTopic()` for clear message routing
- **Topic prefixes**: All topics use `game_` or `session_` prefix for clear distinction

## Seed Synchronization Protocol

### Leader Election

- First instance to connect becomes the "leader"
- Leader generates `shared_seed` if not provided
- Leader publishes seed on `{session_id}/session_seed_sync`

### Seed Sync Flow

1. Instance connects to broker (via dialog)
2. Instance subscribes to `{session_id}/session_seed_sync`
3. **Temporary handler installed**: Only processes `session_seed_sync` topic
4. If `shared_seed` is provided in config:
   - Instance uses it directly
   - Instance publishes it on topic (for other instances)
5. If `shared_seed` is None:
   - Instance waits for seed message (max 5 seconds)
   - If no message received and instance is first (no other players registered):
     - Instance becomes leader
     - Generates random seed
     - Publishes seed on topic
   - If message received:
     - Instance uses received seed
6. **Temporary handler restored**: Original handler (from SGMQTTManager) is restored
7. All instances apply seed: `random.seed(shared_seed)`
8. Seed is applied BEFORE any random operations in model setup

### Important: Handler Management

- `syncSeed()` installs a temporary handler ONLY for `session_seed_sync` topic
- This handler does NOT forward other messages (avoids double processing)
- Handler is restored immediately after seed is received or timeout
- Game messages continue to be handled by SGMQTTManager's handler
- Handler uses `isSessionTopic()` to identify session messages and `mqtt_manager.isGameTopic()` to route game messages

## Automatic Filtering

### Player Filtering

**Important**: All players are created in all instances (for synchronization purposes). The filtering happens at:

1. **Connection level**: Only one instance per player name can connect to a session (validated via MQTT)
2. **Interaction level**: Only the instance of the active player can interact during their phase (control panels, actions)
3. **Visibility level**: Control panels and gameSpaces are hidden for remote players
4. **Attribute level**: `player.isRemote` marks remote players

**Hook Location**: `SGModel.newPlayer()`

**Behavior**:
```python
def newPlayer(self, name):
    player = SGPlayer(...)
    
    if self.isDistributed():
        assigned_player_name = self.distributedConfig.assigned_player_name
        
        if name != assigned_player_name:
            player.isRemote = True  # Remote player
        else:
            player.isRemote = False  # Assigned player
    
    self.players[name] = player
    return player
```

**Note**: 
- All players are created in all instances (needed for MQTT synchronization)
- Connection validation ensures only one instance per player name connects to a session
- If "Player 2" is already connected, another instance cannot connect as "Player 2" in the same session
- The dialog filters out already connected players from the selection list

### Phase Synchronization

**Important**: All phases are created in all instances. There is NO filtering of phases in distributed mode.

**Behavior**:
- All instances create all phases (same phase list in all instances)
- Phase transitions are synchronized via MQTT: when one instance calls `nextPhase()`, all instances advance to the next phase
- During a phase, only the instance of the active player can interact:
  - Control panels are automatically activated/deactivated based on the current player
  - Only authorized actions for the current player are available
  - Other instances wait passively during phases for other players

**Example**:
- Instance 1 (Player 1) and Instance 2 (Player 2) both have:
  - "Player 1 Turn" phase
  - "Player 2 Turn" phase
  - "Refill River" ModelPhase
- When "Player 1 Turn" phase is active:
  - Instance 1: Player 1 can interact (control panel active, actions available)
  - Instance 2: Player 2 waits (control panel inactive, no actions)
- When "Player 2 Turn" phase is active:
  - Instance 1: Player 1 waits (control panel inactive, no actions)
  - Instance 2: Player 2 can interact (control panel active, actions available)

**ModelPhase Handling**:
- ModelPhase (automatic phases like "Refill River") are created in all instances
- When a ModelPhase executes, SGMQTTManager automatically synchronizes it with other instances
- All instances execute ModelPhase actions simultaneously

### GameSpace Visibility System

**Automatic Configuration**:
- **Control Panels**: Automatically configured in `SGPlayer.newControlPanel()`
  - Each control panel is visible only to its owner player
  - Set via `controlPanel.setVisibilityForPlayers(player.name)`

- **Player Boards**: Configured in model script (example: Sea_Zones_distributed.py)
  ```python
  for i in range(1, nb_players + 1):
      player_board = PlayerBoards[i]
      player = Players[i]
      player_board.grid.setVisibilityForPlayers(player.name)
  ```

**Rendering Behavior**:
- When `isVisibleForPlayers` indicates that a GameSpace is not visible:
  - The GameSpace exists in the model (for synchronization purposes)
  - The GameSpace is NOT rendered (`setVisible(False)`)
  - The GameSpace is NOT clickable (hidden from user interaction)
  - MQTT synchronization still works (all instances have the same GameSpace structure)

## Error Handling

### Connection Failures

- **Broker unreachable**: Show error dialog in dialog, allow retry or cancel
- **Timeout waiting for players**: Show warning, allow to continue with fewer players
- **Seed sync timeout**: Use fallback seed or show error

### Session Conflicts

- **Duplicate player assignment**: 
  - Prevented at registration: Check if player name is already connected before allowing registration
  - If duplicate detected: Show error "Player X is already connected to this session"
  - Dialog filters out already connected players from selection list
  - Registration fails if duplicate player name is attempted
- **Session ID collision**: Very unlikely with UUID, but handle gracefully
- **Wrong number of players**: Validate that number of connected instances matches fixed num_players or is within range (min, max) before starting game

### MQTT Errors

- **Disconnection during game**: Show warning, attempt reconnection (reconnection mechanism to be implemented in future)
- **Message parsing errors**: Log error, skip message
- **Topic subscription failures**: Show error, disable distributed mode

### Player Disconnection

- **During game**: Currently no reconnection mechanism exists
- **Future enhancement**: Reconnection mechanism should allow players to rejoin a session
- **Current behavior**: If a player disconnects, the game continues but that player's actions cannot be performed
- Connection status widget shows disconnected players

## Backward Compatibility

### Legacy MQTT Usage

- If `session_id` is None in `setMQTTProtocol()`, use global topics (backward compatible)
- Existing MQTT games continue to work without changes
- New distributed games use session-prefixed topics

### Local Mode

- If `enableDistributedGame()` is not called, behavior is unchanged
- All existing model scripts work without modification
- Distributed mode is opt-in only

## Example Model Script

```python
import sys
import random
from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor, QPixmap

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# Application initialization
monApp = QtWidgets.QApplication([])

# Model creation
myModel = SGModel(1200, 700, windowTitle="Sea Zones")
myModel.displayTimeInWindowTitle()

# ============================================================================
# Create players (must be created before enableDistributedGame for dialog)
# ============================================================================
Players = {}
for i in range(1, nb_players + 1):
    player = myModel.newPlayer(f"Player {i}")
    Players[i] = player

# ============================================================================
# Distributed Game Configuration (ONE LINE - OPTIONAL)
# ============================================================================
# Option 1: Fixed number of players
myModel.enableDistributedGame(num_players=2)

# Option 2: Range of players (2-4 players)
# myModel.enableDistributedGame(num_players=(2, 4))

# This will:
# 1. Open dialog to select assigned_player (shows session_id and connection status)
#    - Dialog opens BEFORE MQTT connection (shows "Connecting...")
#    - User can edit session_id or generate new one
#    - User clicks "Connect" → MQTT connection established
#    - Shows actual player names from model (e.g., "Player 1", "Player 2")
# 2. Register player on MQTT
# 3. Synchronize seed automatically
# 4. Open connection status widget automatically
# 5. Filter players/phases automatically
# 6. Configure GameSpace visibility automatically

# NOTE: Do NOT call random.seed() in distributed mode scripts
# The seed is synchronized and applied automatically

# ============================================================================
# Configure player board visibility (for distributed mode)
# ============================================================================
if myModel.isDistributed():
    for i in range(1, nb_players + 1):
        player_board = PlayerBoards[i]
        player = Players[i]
        player_board.grid.setVisibilityForPlayers(player.name)

# ============================================================================
# Rest of model setup (NO CHANGES NEEDED)
# ============================================================================
# Create all phases normally (filtering happens automatically)
# Everything else stays the same

# Launch (automatically uses MQTT if distributed mode enabled)
myModel.launch()

sys.exit(monApp.exec_())
```

## ✅ VALIDATION CHECKLIST

### Tests de Régression (CRITICAL)

**Avant de considérer l'implémentation terminée, vérifier que l'existant fonctionne toujours:**

- [ ] **`MQTT_GameExample_Player1.py` et `Player2.py` fonctionnent exactement comme avant**
  - Topics globaux fonctionnent toujours
  - Pas de régression dans le comportement MQTT existant
  - Test: Lancer les deux exemples, vérifier que les actions sont synchronisées

- [ ] **`Sea_Zones.py` (version non-distribuée) fonctionne sans changement**
  - `launch()` fonctionne normalement
  - Pas d'impact sur les jeux locaux
  - Test: Lancer le jeu local, vérifier qu'il fonctionne normalement

- [ ] **`launch_withMQTT()` en mode legacy fonctionne**
  - Sans `session_id` → topics globaux
  - Avec `session_id` → topics préfixés
  - Test: Appeler `launch_withMQTT()` avec et sans `session_id`

### Tests par Phase

**Phase 1 - Infrastructure de Base**:
- [ ] `SGDistributedGameConfig` peut être instancié
- [ ] `set_num_players()` accepte int et tuple
- [ ] `isDistributed()` retourne False si pas de config
- [ ] Attributs ajoutés à `SGModel` sans casser l'existant

**Phase 2 - SGMQTTManager Modifications**:
- [ ] `setMQTTProtocol()` accepte `session_id=None` (compatibilité)
- [ ] Topics préfixés avec `{session_id}/game_*` si présent
- [ ] Topics globaux `game_*` si `session_id=None` (legacy)
- [ ] `GAME_TOPICS` liste centralisée créée
- [ ] `isGameTopic()` méthode helper créée
- [ ] **CRITICAL**: Exemples existants (`MQTT_GameExample_Player1.py`) fonctionnent toujours (avec préfixe `game_`)
- [ ] Test avec `session_id` et sans `session_id`

**Phase 3 - Session Manager**:
- [ ] `registerPlayer()` publie sur le bon topic (`session_player_registration`)
- [ ] `registerPlayer()` handler forward uniquement les topics de jeu (`game_*`) au handler original
- [ ] `registerPlayer()` handler ignore les autres topics de session (ne forwarde pas `session_seed_sync`)
- [ ] `syncSeed()` handler temporaire uniquement pour `session_seed_sync`
- [ ] Handler restauré après synchronisation
- [ ] **CRITICAL**: Pas d'interférence avec les messages de jeu
- [ ] `SESSION_TOPICS` liste centralisée créée
- [ ] `isSessionTopic()` méthode helper créée
- [ ] `isGameTopic()` utilisé pour identifier les topics de jeu à forwarder
- [ ] Test isolé: `registerPlayer()` et `syncSeed()` fonctionnent

**Phase 4 - Interfaces Utilisateur**:
- [ ] Dialog s'ouvre et affiche les joueurs
- [ ] Bouton "Connect" établit la connexion MQTT
- [ ] **CRITICAL**: `setMQTTProtocol()` appelé une seule fois
- [ ] Timer met à jour les joueurs disponibles
- [ ] Widget de statut s'affiche comme fenêtre séparée
- [ ] Test avec 2 instances: Dialog fonctionne

**Phase 5 - Intégration**:
- [ ] `enableDistributedGame()` fonctionne end-to-end
- [ ] **CRITICAL**: `launch_withMQTT()` réutilise la connexion existante
- [ ] Pas de double appel à `setMQTTProtocol()`
- [ ] Seed synchronisé avant `launch()`
- [ ] Test avec 2 instances: Connexion et synchronisation fonctionnent

**Phase 6 - Fonctionnalités Automatiques**:
- [ ] `setVisibilityForPlayers()` fonctionne
- [ ] Control panels visibles uniquement pour leur propriétaire
- [ ] `player.isRemote` correctement défini
- [ ] Test avec 2 instances: Visibilité correcte sur chaque instance

### Tests End-to-End

**Test final avec 2 instances de `Sea_Zones_distributed.py`:**

- [ ] Instance 1: Dialog s'ouvre, connexion établie, joueur sélectionné
- [ ] Instance 2: Dialog s'ouvre, connexion établie, joueur différent sélectionné
- [ ] Seed synchronisé entre les deux instances
- [ ] Phases synchronisées (nextTurn sur instance 1 → instance 2 avance aussi)
- [ ] Actions synchronisées (move sur instance 1 → instance 2 voit le move)
- [ ] Visibilité correcte (chaque instance voit uniquement son propre board)
- [ ] Widget de statut affiche les deux joueurs connectés

## ⚠️ KNOWN PITFALLS & SOLUTIONS

### Piège 1: Double appel à `setMQTTProtocol()`

**Symptôme**: Connexion MQTT réinitialisée, messages perdus, désynchronisation.

**Cause**: `setMQTTProtocol()` appelé dans le dialog ET dans `launch_withMQTT()`.

**Solution**: Vérifier si connexion existe déjà dans `launch_withMQTT()`:
```python
if (self.mqttManager.client and 
    self.mqttManager.client.is_connected() and
    self.mqttManager.session_id == session_id):
    # Réutiliser connexion existante
    self.model.mqttMajType = majType
else:
    # Créer nouvelle connexion
    self.mqttManager.setMQTTProtocol(...)
```

**Comment détecter**: Logs montrent deux connexions MQTT, ou messages non reçus.

### Piège 2: Handler de messages conflictuel

**Symptôme**: Messages traités deux fois, actions dupliquées, désynchronisation.

**Cause**: `syncSeed()` handler forward les messages non-seed au handler original.

**Solution**: Handler temporaire ne traite QUE `session_seed_sync`, ne forwarde rien d'autre:
```python
def seed_message_handler(client, userdata, msg):
    if msg.topic == seed_topic:
        # Traiter session_seed_sync
        ...
    # CRITICAL: Ne PAS forwarder les autres messages
```

**Comment détecter**: Logs montrent messages traités deux fois, ou queue contient doublons.

### Piège 3: Topics mal préfixés

**Symptôme**: Messages non reçus, instances non synchronisées.

**Cause**: Topics non préfixés avec `{session_id}/` ou préfixés incorrectement.

**Solution**: Vérifier préfixage dans `SGMQTTManager.initMQTT()`:
```python
if self.session_id:
    self.client.subscribe(f"{self.session_id}/game_gameAction_performed")
    self.client.subscribe(f"{self.session_id}/game_nextTurn")
else:
    # Legacy: topics globaux (sans préfixe session, mais avec préfixe game_)
    self.client.subscribe("game_gameAction_performed")
    self.client.subscribe("game_nextTurn")
```

**Comment détecter**: Logs MQTT montrent subscriptions sur mauvais topics, ou messages non reçus.

### Piège 4: Visibilité non mise à jour

**Symptôme**: GameSpaces visibles pour tous les joueurs au lieu d'être filtrés.

**Cause**: `_updateVisibility()` non appelé après configuration.

**Solution**: Appeler `_updateVisibility()` automatiquement dans `setVisibilityForPlayers()`:
```python
def setVisibilityForPlayers(self, players):
    # ... configuration ...
    self._updateVisibility()  # Mise à jour automatique
```

**Comment détecter**: GameSpaces visibles sur toutes les instances au lieu d'une seule.

### Piège 5: Seed appliqué trop tard

**Symptôme**: Instances ont des seeds différents malgré synchronisation.

**Cause**: Seed appliqué après des opérations aléatoires dans le modèle.

**Solution**: Appliquer seed immédiatement après synchronisation dans `enableDistributedGame()`:
```python
synced_seed = session_manager.syncSeed(config.session_id, shared_seed)
config.shared_seed = synced_seed
random.seed(synced_seed)  # Appliquer IMMÉDIATEMENT
```

**Comment détecter**: Instances génèrent des résultats différents malgré seed synchronisé.

### Piège 6: Handler non restauré après syncSeed()

**Symptôme**: Messages de jeu ne sont plus traités après synchronisation seed.

**Cause**: Handler temporaire de `syncSeed()` n'est pas restauré.

**Solution**: Toujours restaurer le handler avant de retourner de `syncSeed()`:
```python
def syncSeed(self, ...):
    # ... installation handler temporaire ...
    # ... attente seed ...
    # CRITICAL: Restaurer handler avant de retourner
    self.mqtt_manager.client.on_message = original_on_message
    return self.synced_seed
```

**Comment détecter**: Messages de jeu ne sont plus reçus après synchronisation seed.

## 💡 CODE EXAMPLES

### Exemple 1: `launch_withMQTT()` réutilisant la connexion

**Code CORRECT**:
```python
def launch_withMQTT(self, majType, broker_host="localhost", broker_port=1883, session_id=None):
    """
    Set the mqtt protocol, then launch the game.
    
    IMPORTANT: In distributed mode, MQTT connection is already established in enableDistributedGame().
    This method should reuse the existing connection if possible.
    """
    # Use session_id from distributedConfig if available
    if session_id is None and self.isDistributed():
        session_id = self.distributedConfig.session_id
    
    # CRITICAL: Check if MQTT is already initialized
    if (self.mqttManager.client and 
        self.mqttManager.client.is_connected() and
        self.mqttManager.session_id == session_id):
        # Reuse existing connection - just update majType if needed
        self.model.mqttMajType = majType
    else:
        # Initialize new connection (only if not already connected)
        self.mqttManager.setMQTTProtocol(majType, broker_host, broker_port, session_id=session_id)
    
    # Launch the game (don't call self.launch() to avoid recursion)
    self.initBeforeShowing()
    self.show()
    self.initAfterOpening()
```

**Code INCORRECT** (à éviter):
```python
def launch_withMQTT(self, majType, broker_host="localhost", broker_port=1883, session_id=None):
    # ❌ TOUJOURS appeler setMQTTProtocol() - cause double initialisation
    self.mqttManager.setMQTTProtocol(majType, broker_host, broker_port, session_id=session_id)
    self.launch()  # ❌ Appelle self.launch() qui peut causer récursion
```

### Exemple 2: `syncSeed()` avec handler temporaire correct

**Code CORRECT**:
```python
def syncSeed(self, session_id, shared_seed=None, timeout=5):
    """
    Synchronize random seed across all instances.
    
    Uses temporary message handler ONLY for session_seed_sync topic.
    Does NOT interfere with game message handling.
    """
    seed_topic = f"{session_id}/session_seed_sync"
    self.mqtt_manager.client.subscribe(seed_topic)
    
    # Save original handler
    original_on_message = self.mqtt_manager.client.on_message
    
    def seed_message_handler(client, userdata, msg):
        if msg.topic == seed_topic:
            # Process seed message ONLY
            try:
                msg_dict = json.loads(msg.payload.decode("utf-8"))
                if msg_dict['clientId'] != self.mqtt_manager.clientId:
                    self.synced_seed = msg_dict['seed']
                    self.seed_received = True
                    self.seedReceived.emit(self.synced_seed)
                    # Restore original handler immediately
                    self.mqtt_manager.client.on_message = original_on_message
            except Exception as e:
                print(f"Error processing seed message: {e}")
        # ✅ CRITICAL: Do NOT forward other messages - they are handled by SGMQTTManager
    
    # Install temporary handler
    self.mqtt_manager.client.on_message = seed_message_handler
    
    # Wait for seed or generate if leader
    start_time = time.time()
    while time.time() - start_time < timeout:
        if self.seed_received:
            return self.synced_seed
        time.sleep(0.1)
    
    # ... (rest of implementation: generate seed if leader, etc.)
    
    # CRITICAL: Restore original handler before returning
    self.mqtt_manager.client.on_message = original_on_message
    return self.synced_seed
```

**Code INCORRECT** (à éviter):
```python
def seed_message_handler(client, userdata, msg):
    if msg.topic == seed_topic:
        # Traiter session_seed_sync
        ...
    else:
        # ❌ Forwarder les autres messages - cause double traitement
        if original_on_message:
            original_on_message(client, userdata, msg)
```

### Exemple 3: Vérification de connexion existante

**Code CORRECT dans `SGDistributedGameDialog._checkConnection()`**:
```python
def _checkConnection(self):
    """Check if MQTT connection is established."""
    if (self.model.mqttManager.client and 
        self.model.mqttManager.client.is_connected()):
        self.connection_status = "Connected to broker"
        self.status_label.setText(f"Connection Status: {self.connection_status}")
        self.ok_button.setEnabled(True)
    else:
        # Réessayer après 500ms
        QTimer.singleShot(500, self._checkConnection)
```

### Exemple 4: Configuration automatique de visibilité

**Code CORRECT dans `SGPlayer.newControlPanel()`**:
```python
def newControlPanel(self, title=None, defaultActionSelected=None):
    """
    Create a Player Control Panel.
    
    In distributed mode, automatically sets visibility to assigned player only.
    """
    if title is None:
        title = (self.name + ' actions')
    
    control_panel = SGControlPanel(self, title, defaultActionSelected=defaultActionSelected)
    
    # Auto-configure visibility in distributed mode
    if self.model.isDistributed():
        control_panel.setVisibilityForPlayers(self.name)
    
    # ... (rest of method: positioning, etc.)
    
    return control_panel
```

### Exemple 5: Préfixage des topics dans `SGMQTTManager.initMQTT()`

**Code CORRECT**:
```python
def initMQTT(self):
    """Init the MQTT client"""
    def on_message(aClient, userdata, msg):
        # ... (message handling logic)
    
    self.connect_mqtt()
    
    # Wait for connection
    import time
    while not (self.client and self.client.is_connected()):
        time.sleep(0.1)
    
    # Subscribe to game topics (with or without session prefix)
    if self.session_id:
        # Distributed mode: prefix topics with session_id and game_ prefix
        self.client.subscribe(f"{self.session_id}/game_gameAction_performed")
        self.client.subscribe(f"{self.session_id}/game_nextTurn")
        self.client.subscribe(f"{self.session_id}/game_execute_method")
    else:
        # Legacy mode: global topics (without session prefix, but with game_ prefix)
        self.client.subscribe("game_gameAction_performed")
        self.client.subscribe("game_nextTurn")
        self.client.subscribe("game_execute_method")
    
    self.client.on_message = on_message
```

### Exemple 6: Publication avec préfixe de session

**Code CORRECT dans `SGMQTTManager.buildNextTurnMsgAndPublishToBroker()`**:
```python
def buildNextTurnMsgAndPublishToBroker(self):
    """Build and publish next turn message to MQTT broker"""
    # Determine topic (with or without session prefix)
    if self.session_id:
        msgTopic = f"{self.session_id}/game_nextTurn"
    else:
        msgTopic = 'game_nextTurn'
    
    msg_dict = {}
    msg_dict['clientId'] = self.clientId
    serializedMsg = json.dumps(msg_dict)
    
    if self.client:
        self.client.publish(msgTopic, serializedMsg)
    else:
        raise ValueError('MQTT client not initialized')
```

## Notes

- All code and docstrings must be in English
- Maintain backward compatibility with existing MQTT games
- Ensure thread safety for MQTT operations
- Handle edge cases gracefully (disconnections, timeouts, etc.)
- Provide clear error messages to users
- Log important events for debugging
- Player names are used directly (not converted to numbers) - supports any naming convention
- ModelPhase synchronization is already handled by SGMQTTManager
- GameSpace visibility system ensures players only see their own UI elements
- Validation ensures correct number of players before game starts (fixed number or within range)
- **Critical**: `setMQTTProtocol()` is called ONCE in the dialog, not in `launch_withMQTT()`
- **Critical**: Session manager handles ONLY session topics, game topics handled by SGMQTTManager
- **Critical**: Test regression after each phase to ensure existing functionality still works
