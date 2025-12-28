# Guide : Jeux Distribués dans SGE

Ce guide explique comment mettre en place et utiliser le système de jeux distribués dans SGE, permettant à plusieurs instances de votre modèle de jouer ensemble via MQTT.

---

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Mise en place dans le modèle](#mise-en-place-dans-le-modèle)
3. [Phases de connexion](#phases-de-connexion)
4. [Options MQTT disponibles](#options-mqtt-disponibles)
5. [Paramètres de configuration](#paramètres-de-configuration)
6. [Récupération du nombre d'instances](#récupération-du-nombre-dinstances)
7. [États de connexion](#états-de-connexion)
8. [Gestion des joueurs](#gestion-des-joueurs)
9. [Comportements et cas particuliers](#comportements-et-cas-particuliers)
10. [Exemples pratiques](#exemples-pratiques)
11. [Bonnes pratiques](#bonnes-pratiques)
12. [Dépannage](#dépannage)

---

## Vue d'ensemble

### Qu'est-ce qu'un jeu distribué ?

Un jeu distribué permet à plusieurs instances de votre modèle SGE de se connecter et de jouer ensemble. Chaque instance s'exécute sur une machine différente et communique via un broker MQTT.

### Concepts clés

- **Session** :** Une session représente une partie de jeu. Chaque session a un identifiant unique (`session_id`).
- **Créateur** : L'instance qui crée la session. Elle est responsable de la synchronisation du seed et de la gestion de la session.
- **Joiner** : Une instance qui rejoint une session existante.
- **Seed synchronisé** : Toutes les instances utilisent le même seed aléatoire pour garantir la cohérence du jeu.

### Workflow général

1. **Création de session** : Une instance crée une nouvelle session
2. **Rejoindre une session** : D'autres instances rejoignent la session créée
3. **Synchronisation** : Le seed est synchronisé automatiquement
4. **Attente** : Les instances attendent que le nombre requis de joueurs soit connecté
5. **Démarrage** : Le jeu peut démarrer lorsque toutes les conditions sont remplies

---

## Mise en place dans le modèle

### Où appeler `enableDistributedGame()`

**IMPORTANT** : Vous devez appeler `enableDistributedGame()` **AVANT toute opération aléatoire** dans votre script.

```python
import sys
from pathlib import Path
from PyQt5 import QtWidgets

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# Application initialization
monApp = QtWidgets.QApplication([])

# Model creation
myModel = SGModel(1200, 900, windowTitle="My Game")

# ============================================================================
# Distributed Game Configuration - MUST BE CALLED BEFORE ANY RANDOM OPERATIONS
# ============================================================================
myModel.enableDistributedGame(num_players=4)

# Maintenant vous pouvez utiliser des opérations aléatoires
# Le seed est déjà synchronisé et appliqué
import random
random_value = random.randint(1, 100)  # Utilise le seed synchronisé
```

### Exemple minimal

```python
# Configuration minimale
myModel.enableDistributedGame(num_players=2)

# Le reste de votre code...
```

### Ordre d'exécution dans le script

1. Création de l'application Qt
2. Création du modèle (`SGModel`)
3. **Appel à `enableDistributedGame()`** ← ICI
4. Toutes les autres opérations (création de grilles, agents, etc.)

---

## Phases de connexion

Le processus de connexion se déroule en plusieurs phases, chacune avec des états spécifiques.

### Phase 1 : Connexion au broker MQTT

**Objectif** : Établir la connexion avec le broker MQTT.

**États possibles** :
- **Non connecté** : Aucune connexion établie
- **Connexion en cours** : Tentative de connexion en cours
- **Connecté** : Connexion établie avec succès
- **Erreur de connexion** : Échec de la connexion (broker inaccessible, mauvais port, etc.)

**Interface utilisateur** :
- Le dialog affiche l'état de connexion
- Vous pouvez configurer `broker_host` et `broker_port`
- Bouton "Connect" pour établir la connexion

### Phase 2 : Création ou rejoindre une session

**Objectif** : Créer une nouvelle session ou rejoindre une session existante.

**Options disponibles** :
- **Créer une nouvelle session** :
  - Un `session_id` unique est généré automatiquement
  - Vous pouvez le modifier si nécessaire
  - Cliquez sur "Connect" pour créer la session
  
- **Rejoindre une session existante** :
  - La liste "Available Sessions" affiche les sessions disponibles
  - Sélectionnez une session dans la liste
  - Cliquez sur "Connect" pour rejoindre

**États possibles** :
- **Aucune session** : Aucune session créée ou rejointe
- **Session créée** : Vous avez créé une nouvelle session (vous êtes le créateur)
- **Session rejointe** : Vous avez rejoint une session existante (vous êtes un joiner)
- **Session fermée** : La session a été fermée (créateur déconnecté)

### Phase 3 : Synchronisation du seed

**Objectif** : Synchroniser le seed aléatoire entre toutes les instances.

**Fonctionnement** :
- **Automatique** : La synchronisation se fait automatiquement après la connexion
- **Créateur** : Si vous créez la session, votre seed devient le seed de référence
- **Joiner** : Si vous rejoignez, vous recevez le seed du créateur

**États possibles** :
- **En attente** : Attente de la synchronisation
- **Synchronisation en cours** : Synchronisation en cours
- **Synchronisé ✓** : Seed synchronisé avec succès
- **Erreur de synchronisation** : Échec de la synchronisation

**Interface utilisateur** :
- Le "Session Status" affiche "Seed: Synchronized ✓" (fond vert) lorsque synchronisé
- "Seed: Not synchronized" (fond jaune/rouge) sinon

### Phase 4 : Attente des autres instances

**Objectif** : Attendre que le nombre requis d'instances soit connecté.

**Affichage** :
- **Session Status** : Affiche le nombre d'instances connectées
  - Format : `Instances: X/Y connected` (nombre fixe)
  - Format : `Instances: X/Y-Z connected` (plage)
  - Format : `Instances: X/Y-∞ connected` (minimum sans maximum)
  
- **Available Sessions** : Affiche également le nombre d'instances pour chaque session

**États possibles** :
- **En attente** : Nombre d'instances insuffisant
  - Affiche : `Instances: X/Y connected (waiting for N more...)`
- **Minimum atteint** : Nombre minimum atteint, peut démarrer
  - Affiche : `Instances: X/Y-Z connected ✓ (min)`
- **Maximum atteint** : Nombre maximum atteint
  - Affiche : `Instances: X/Y connected ✓`
- **Prêt** : Conditions remplies, jeu peut démarrer

**Validation** :
- Le jeu peut démarrer lorsque le nombre d'instances est dans la plage autorisée
- Si `num_players=4` : besoin de 4 instances exactement
- Si `num_players=(2, 4)` : besoin de 2 à 4 instances
- Si `num_players=(2,)` : besoin d'au moins 2 instances (pas de maximum)

---

## Options MQTT disponibles

### Paramètres de connexion

#### `broker_host` (str, défaut: `"localhost"`)

Adresse du broker MQTT.

**Exemples** :
```python
# Broker local
myModel.enableDistributedGame(num_players=4, broker_host="localhost")

# Broker distant
myModel.enableDistributedGame(num_players=4, broker_host="192.168.1.100")

# Broker avec nom de domaine
myModel.enableDistributedGame(num_players=4, broker_host="mqtt.example.com")
```

#### `broker_port` (int, défaut: `1883`)

Port du broker MQTT.

**Exemples** :
```python
# Port standard
myModel.enableDistributedGame(num_players=4, broker_port=1883)

# Port personnalisé
myModel.enableDistributedGame(num_players=4, broker_port=8883)
```

### Type de mise à jour MQTT

#### `mqtt_update_type` (str, défaut: `"Instantaneous"`)

Contrôle le mode de synchronisation des mises à jour MQTT.

**Options disponibles** :
- **`"Instantaneous"`** : Les mises à jour sont envoyées immédiatement
- **`"Phase"`** : Les mises à jour sont regroupées par phase de jeu

**Exemple** :
```python
# Mises à jour instantanées (recommandé pour la plupart des cas)
myModel.enableDistributedGame(num_players=4, mqtt_update_type="Instantaneous")

# Mises à jour par phase (pour optimiser le trafic réseau)
myModel.enableDistributedGame(num_players=4, mqtt_update_type="Phase")
```

### Timeout de synchronisation du seed

#### `seed_sync_timeout` (float, défaut: `1.0`)

Délai en secondes avant qu'une instance devienne automatiquement le "leader" (créateur du seed) si aucun seed existant n'est détecté.

**Quand augmenter cette valeur** :
- Si vous avez des latences réseau élevées
- Si plusieurs instances démarrent simultanément
- Si vous voulez plus de temps pour détecter un seed existant

**Exemple** :
```python
# Timeout par défaut (1 seconde)
myModel.enableDistributedGame(num_players=4)

# Timeout augmenté (3 secondes)
myModel.enableDistributedGame(num_players=4, seed_sync_timeout=3.0)
```

---

## Paramètres de configuration

### Nombre de joueurs : `num_players`

Le paramètre `num_players` contrôle le nombre d'instances requises pour démarrer le jeu.

#### Option 1 : Nombre fixe (int)

Le jeu nécessite exactement ce nombre d'instances.

```python
# Jeu à 2 joueurs exactement
myModel.enableDistributedGame(num_players=2)

# Jeu à 4 joueurs exactement
myModel.enableDistributedGame(num_players=4)
```

**Comportement** :
- Le jeu peut démarrer uniquement lorsque exactement `num_players` instances sont connectées
- Si une instance se déconnecte, le jeu ne peut plus continuer (session fermée)

#### Option 2 : Plage de joueurs (tuple avec min et max)

Le jeu peut démarrer avec un nombre d'instances dans la plage spécifiée.

```python
# Jeu avec 2 à 4 joueurs
myModel.enableDistributedGame(num_players=(2, 4))
```

**Comportement** :
- Le jeu peut démarrer lorsque le nombre d'instances est entre 2 et 4 (inclus)
- Affiche : `Instances: X/2-4 connected`
- Si le minimum est atteint : `Instances: 2/2-4 connected ✓ (min)`
- Si le maximum est atteint : `Instances: 4/2-4 connected ✓`

#### Option 3 : Minimum sans maximum (tuple avec un seul élément)

Le jeu nécessite au moins un nombre minimum d'instances, sans limite maximale.

```python
# Jeu avec minimum 2 joueurs (pas de maximum)
myModel.enableDistributedGame(num_players=(2,))
```

**Comportement** :
- Le jeu peut démarrer lorsque au moins 2 instances sont connectées
- Affiche : `Instances: X/2-∞ connected`
- Pas de limite supérieure

### Session ID : `session_id` (optionnel)

Identifiant unique de la session. Si non fourni, un ID est généré automatiquement.

```python
# Génération automatique (recommandé)
myModel.enableDistributedGame(num_players=4)

# Session ID personnalisé
myModel.enableDistributedGame(num_players=4, session_id="my-custom-session-123")
```

**Quand l'utiliser** :
- Pour rejoindre une session spécifique
- Pour créer une session avec un nom reconnaissable
- Pour des tests ou démonstrations

### Seed partagé : `shared_seed` (optionnel)

Seed aléatoire personnalisé. Si non fourni, un seed est généré et synchronisé automatiquement.

```python
# Seed automatique (recommandé)
myModel.enableDistributedGame(num_players=4)

# Seed personnalisé
myModel.enableDistributedGame(num_players=4, shared_seed=12345)
```

**Quand l'utiliser** :
- Pour reproduire une partie spécifique
- Pour des tests déterministes
- Pour synchroniser manuellement le seed

---

## Récupération du nombre d'instances

### Méthode : `getConnectedInstancesCount()`

Cette méthode retourne le nombre d'instances actuellement connectées à la session.

#### Signature

```python
def getConnectedInstancesCount(self, default=0):
    """
    Get the number of connected instances in distributed game mode.
    
    Args:
        default (int, optional): Default value to return if count is not available.
    
    Returns:
        int: Number of connected instances, or default value if not in distributed mode.
    """
```

#### Utilisation de base

```python
# Récupérer le nombre d'instances
nb_players = myModel.getConnectedInstancesCount()
print(f"Nombre d'instances connectées : {nb_players}")
```

#### Avec valeur par défaut

```python
# Si le mode distribué n'est pas activé, retourne 1 (valeur par défaut)
nb_players = myModel.getConnectedInstancesCount(default=1)

# Utilisation dans une condition
if nb_players >= 2:
    print("Minimum de joueurs atteint !")
else:
    print(f"En attente de {2 - nb_players} joueur(s) supplémentaire(s)")
```

#### Quand l'appeler

**Après `enableDistributedGame()`** :
```python
# Configuration
myModel.enableDistributedGame(num_players=4)

# Récupération immédiate (peut être 1 si vous êtes seul)
nb_players = myModel.getConnectedInstancesCount(default=4)
print(f"Instances connectées : {nb_players}")
```

**Dans votre code de jeu** :
```python
# Dans une méthode de jeu
def checkPlayersReady(self):
    nb_players = myModel.getConnectedInstancesCount()
    if nb_players >= 2:
        # Démarrer le jeu
        self.startGame()
    else:
        # Attendre plus de joueurs
        print(f"En attente de {2 - nb_players} joueur(s)")
```

#### Cas d'erreur

Si le mode distribué n'est pas activé ou si le comptage n'est pas disponible, la méthode retourne la valeur `default` :

```python
# Mode distribué non activé
nb_players = myModel.getConnectedInstancesCount(default=1)
# Retourne : 1 (valeur par défaut)

# Mode distribué activé mais comptage indisponible
nb_players = myModel.getConnectedInstancesCount(default=0)
# Retourne : 0 (valeur par défaut)
```

---

## États de connexion

Cette section détaille tous les états possibles de la connexion pendant les différentes phases de mise en place.

### État initial

**Quand** : Avant toute connexion

**Caractéristiques** :
- Aucune connexion au broker
- Aucune session créée ou rejointe
- Seed non synchronisé

**Interface utilisateur** :
- "Connection Status: Not connected"
- "Seed: Not synchronized"
- "Instances: No instances connected yet"

### Connexion en cours

**Quand** : Pendant la tentative de connexion au broker MQTT

**Caractéristiques** :
- Tentative de connexion active
- Attente de réponse du broker

**Interface utilisateur** :
- "Connection Status: Connecting..."
- Bouton "Connect" désactivé

### Connecté (sans session)

**Quand** : Broker connecté, mais aucune session créée ou rejointe

**Caractéristiques** :
- Connexion MQTT établie
- Pas encore de session active
- Seed non synchronisé

**Interface utilisateur** :
- "Connection Status: Connected to broker"
- "Seed: Not synchronized"
- "Instances: No instances connected yet"

### Synchronisation du seed

**Quand** : Pendant la synchronisation du seed

**Caractéristiques** :
- Connexion MQTT établie
- Session créée ou rejointe
- Synchronisation du seed en cours

**États possibles** :
- **En attente** : Attente de réception/émission du seed
- **Synchronisation en cours** : Seed en cours de transmission
- **Synchronisé ✓** : Seed synchronisé avec succès
- **Erreur** : Échec de la synchronisation

**Interface utilisateur** :
- "Seed: Checking for existing seed..." (en attente)
- "Seed: Synchronized ✓" (synchronisé, fond vert)
- "Seed: Sync failed - [erreur]" (erreur, fond rouge)

### Session créée/rejointe

**Quand** : Session active, seed synchronisé

**Caractéristiques** :
- Connexion MQTT établie
- Session active (créée ou rejointe)
- Seed synchronisé
- Instance ajoutée à la session

**Interface utilisateur** :
- "Seed: Synchronized ✓"
- "Instances: X/Y connected" (où X est le nombre actuel, Y le nombre requis)

### En attente d'instances

**Quand** : Session active, mais nombre d'instances insuffisant

**Caractéristiques** :
- Session active
- Seed synchronisé
- Nombre d'instances < minimum requis

**Interface utilisateur** :
- "Instances: X/Y connected (waiting for N more...)" (fond orange)
- Le nombre X augmente au fur et à mesure que d'autres instances rejoignent

### Prêt (conditions remplies)

**Quand** : Nombre d'instances dans la plage autorisée

**Caractéristiques** :
- Session active
- Seed synchronisé
- Nombre d'instances suffisant
- Jeu peut démarrer

**Interface utilisateur** :
- "Instances: X/Y connected ✓" (fond vert)
- Ou "Instances: X/Y-Z connected ✓ (min)" si minimum atteint

### Erreur de connexion

**Quand** : Échec de connexion au broker

**Caractéristiques** :
- Impossible de se connecter au broker
- Causes possibles : broker inaccessible, mauvais port, firewall, etc.

**Interface utilisateur** :
- "Connection Status: Connection failed"
- Message d'erreur détaillé

### Session fermée

**Quand** : La session a été fermée (créateur déconnecté, timeout, etc.)

**Caractéristiques** :
- Session marquée comme "closed"
- Toutes les instances doivent quitter
- Interface réinitialisée

**Interface utilisateur** :
- "Instances: Session closed" (fond rouge)
- "Seed: Not synchronized"
- Session retirée de la liste "Available Sessions"
- Message d'avertissement : "The session creator has disconnected. The session has been closed."

### Déconnexion brutale du créateur

**Quand** : Le créateur de la session se déconnecte sans fermer proprement la session

**Caractéristiques** :
- Détection automatique après 15 secondes sans heartbeat
- Session fermée automatiquement
- Toutes les instances sont notifiées

**Interface utilisateur** :
- Message d'avertissement après ~15-20 secondes
- Session fermée automatiquement
- Interface réinitialisée

---

## Gestion des joueurs

### Méthode : `completeDistributedGameSetup()`

Cette méthode complète la configuration du jeu distribué en permettant à l'utilisateur de sélectionner son joueur assigné.

#### Quand l'appeler

**Dans `initAfterOpening()`** : Cette méthode doit être appelée après l'ouverture de la fenêtre principale.

```python
def initAfterOpening(self):
    # Compléter la configuration du jeu distribué
    # (sélection du joueur assigné)
    if myModel.isDistributed():
        myModel.completeDistributedGameSetup()
    
    # Reste de votre code d'initialisation...
```

#### Fonctionnement

1. **Ouvre un dialog** : Permet à l'utilisateur de sélectionner son joueur assigné
2. **Affiche les joueurs disponibles** : Liste des joueurs créés dans votre modèle
3. **Enregistrement MQTT** : Enregistre le joueur sélectionné sur MQTT
4. **Widget de statut** : Ouvre un widget affichant le statut de connexion

#### Relation avec `enableDistributedGame()`

- **`enableDistributedGame()`** : Configure la connexion et la session (appelé au début du script)
- **`completeDistributedGameSetup()`** : Sélectionne le joueur assigné (appelé dans `initAfterOpening()`)

**Ordre d'exécution** :
```python
# 1. Au début du script
myModel.enableDistributedGame(num_players=4)

# 2. Dans initAfterOpening()
def initAfterOpening(self):
    if myModel.isDistributed():
        myModel.completeDistributedGameSetup()
```

#### Retour

- **`True`** : Configuration complétée avec succès
- **`False`** : Configuration annulée ou mode distribué non activé

---

## Comportements et cas particuliers

### Déconnexion du créateur

**Comportement** :
- Si le créateur de la session se déconnecte (brutalement ou via Cancel), la session est automatiquement fermée
- Toutes les autres instances sont notifiées et doivent quitter la session
- Un message d'avertissement s'affiche : "The session creator has disconnected. The session has been closed."

**Détection** :
- **Déconnexion brutale** : Détectée après ~15 secondes sans heartbeat
- **Déconnexion propre (Cancel)** : Détectée immédiatement

**Impact** :
- La session est marquée comme "closed"
- Toutes les instances voient "Session closed" dans l'interface
- La session est retirée de la liste "Available Sessions"

### Déconnexion d'une instance (non-créateur)

**Comportement** :
- Si une instance non-créateur se déconnecte, le compteur d'instances est mis à jour automatiquement
- Les autres instances voient le nombre d'instances diminuer
- La session reste active tant que le créateur est connecté

**Exemple** :
- 4 instances connectées → Instance 2 se déconnecte → 3 instances connectées
- Affichage mis à jour automatiquement : "Instances: 3/4 connected"

### Timeout et heartbeat

**Système de heartbeat** :
- Le créateur envoie un heartbeat toutes les 5 secondes
- Les autres instances vérifient le heartbeat toutes les 3 secondes
- Timeout : 15 secondes sans heartbeat = créateur déconnecté

**Comportement** :
- Si le créateur ne répond pas pendant 15 secondes, la session est fermée automatiquement
- Les autres instances sont notifiées et doivent quitter

### Messages d'erreur courants

#### "Connection failed"

**Cause** : Impossible de se connecter au broker MQTT

**Solutions** :
- Vérifier que le broker MQTT est en cours d'exécution
- Vérifier `broker_host` et `broker_port`
- Vérifier les règles de firewall
- Vérifier la connectivité réseau

#### "Seed: Sync failed"

**Cause** : Échec de la synchronisation du seed

**Solutions** :
- Vérifier la connexion MQTT
- Augmenter `seed_sync_timeout` si plusieurs instances démarrent simultanément
- Vérifier que le créateur est bien connecté

#### "Session closed"

**Cause** : La session a été fermée (créateur déconnecté)

**Solutions** :
- Rejoindre une nouvelle session
- Créer une nouvelle session

---

## Exemples pratiques

### Exemple 1 : Jeu à 4 joueurs fixes

```python
import sys
from pathlib import Path
from PyQt5 import QtWidgets

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# Application initialization
monApp = QtWidgets.QApplication([])

# Model creation
myModel = SGModel(1200, 900, windowTitle="My Game")

# ============================================================================
# Distributed Game Configuration
# ============================================================================
myModel.enableDistributedGame(num_players=4)
nb_players = myModel.getConnectedInstancesCount(default=4)

# Le seed est synchronisé automatiquement
# Vous pouvez maintenant utiliser des opérations aléatoires
import random
random_value = random.randint(1, 100)

# ============================================================================
# Création des joueurs
# ============================================================================
Players = {}
for i in range(1, nb_players + 1):
    player = myModel.newPlayer(f"Player {i}")
    Players[i] = player

# ============================================================================
# Reste de votre code...
# ============================================================================

# Dans initAfterOpening()
def initAfterOpening(self):
    if myModel.isDistributed():
        myModel.completeDistributedGameSetup()
    
    # Reste de votre initialisation...

myModel.launch()
```

### Exemple 2 : Jeu avec 2-4 joueurs (flexible)

```python
# Configuration avec plage de joueurs
myModel.enableDistributedGame(num_players=(2, 4))

# Le jeu peut démarrer avec 2, 3 ou 4 joueurs
nb_players = myModel.getConnectedInstancesCount(default=2)

# Adapter votre code au nombre réel de joueurs
if nb_players >= 2:
    print(f"Jeu démarré avec {nb_players} joueurs")
    # Démarrer le jeu
```

### Exemple 3 : Jeu avec minimum 2 joueurs (sans maximum)

```python
# Configuration avec minimum seulement
myModel.enableDistributedGame(num_players=(2,))

# Le jeu peut démarrer avec 2 joueurs ou plus
nb_players = myModel.getConnectedInstancesCount(default=2)

# Vérifier le minimum
if nb_players >= 2:
    print(f"Minimum atteint : {nb_players} joueurs connectés")
    # Démarrer le jeu
```

### Exemple 4 : Utilisation du nombre d'instances dans le code

```python
# Configuration
myModel.enableDistributedGame(num_players=4)

# Récupérer le nombre d'instances
nb_players = myModel.getConnectedInstancesCount(default=4)

# Utiliser dans votre logique de jeu
def checkGameStart(self):
    nb_players = myModel.getConnectedInstancesCount()
    
    if nb_players >= 4:
        # Tous les joueurs sont connectés
        self.startGame()
    elif nb_players >= 2:
        # Minimum atteint, peut démarrer (si configuré avec plage)
        self.startGameWithMinPlayers()
    else:
        # Attendre plus de joueurs
        print(f"En attente de {4 - nb_players} joueur(s)")

# Utiliser pour adapter le jeu au nombre de joueurs
def setupGameBoard(self):
    nb_players = myModel.getConnectedInstancesCount(default=4)
    
    # Adapter la taille du plateau selon le nombre de joueurs
    if nb_players == 2:
        board_size = 8
    elif nb_players == 3:
        board_size = 10
    else:  # 4 joueurs
        board_size = 12
    
    Board = myModel.newCellsOnGrid(board_size, board_size, "square")
```

### Exemple 5 : Configuration MQTT personnalisée

```python
# Configuration avec broker distant
myModel.enableDistributedGame(
    num_players=4,
    broker_host="192.168.1.100",
    broker_port=1883,
    mqtt_update_type="Instantaneous",
    seed_sync_timeout=2.0
)
```

### Exemple 6 : Gestion du cas d'annulation

```python
# Configuration
config = myModel.enableDistributedGame(num_players=4)

# Vérifier si l'utilisateur a annulé
if config is None:
    print("Mode distribué annulé, utilisation du mode local")
    nb_players = 1  # Mode local
else:
    nb_players = myModel.getConnectedInstancesCount(default=4)
    print(f"Mode distribué activé avec {nb_players} instances")
```

---

## Bonnes pratiques

### 1. Toujours appeler `enableDistributedGame()` avant les opérations aléatoires

**❌ Incorrect** :
```python
import random
random_value = random.randint(1, 100)  # Utilise un seed non synchronisé

myModel.enableDistributedGame(num_players=4)  # Trop tard !
```

**✅ Correct** :
```python
myModel.enableDistributedGame(num_players=4)  # D'abord

import random
random_value = random.randint(1, 100)  # Utilise le seed synchronisé
```

### 2. Gérer le cas où l'utilisateur annule

**✅ Bonne pratique** :
```python
config = myModel.enableDistributedGame(num_players=4)

if config is None:
    # Mode distribué annulé, utiliser le mode local
    nb_players = 1
else:
    # Mode distribué activé
    nb_players = myModel.getConnectedInstancesCount(default=4)
```

### 3. Vérifier `isDistributed()` si nécessaire

**✅ Bonne pratique** :
```python
def initAfterOpening(self):
    if myModel.isDistributed():
        myModel.completeDistributedGameSetup()
        # Code spécifique au mode distribué
    else:
        # Code pour le mode local
        pass
```

### 4. Utiliser des valeurs par défaut appropriées

**✅ Bonne pratique** :
```python
# Utiliser le nombre de joueurs configuré comme valeur par défaut
nb_players = myModel.getConnectedInstancesCount(default=4)

# Ou utiliser 1 pour le mode local
nb_players = myModel.getConnectedInstancesCount(default=1)
```

### 5. Tester avec plusieurs instances

**✅ Bonne pratique** :
- Tester avec le nombre exact de joueurs configuré
- Tester avec moins de joueurs (si plage configurée)
- Tester avec plus de joueurs (si plage configurée)
- Tester les déconnexions
- Tester la déconnexion du créateur

---

## Dépannage

### Problème : Impossible de se connecter au broker MQTT

**Symptômes** :
- Message "Connection failed"
- Dialog reste sur "Connecting..."

**Solutions** :
1. **Vérifier que le broker MQTT est en cours d'exécution**
   ```bash
   # Sur Linux/Mac
   systemctl status mosquitto
   
   # Vérifier les processus
   ps aux | grep mosquitto
   ```

2. **Vérifier `broker_host` et `broker_port`**
   ```python
   # Vérifier les paramètres
   myModel.enableDistributedGame(
       num_players=4,
       broker_host="localhost",  # Ou l'adresse IP correcte
       broker_port=1883  # Ou le port correct
   )
   ```

3. **Vérifier les règles de firewall**
   - Le port MQTT (par défaut 1883) doit être ouvert
   - Vérifier les règles de firewall sur le serveur et le client

4. **Tester la connectivité réseau**
   ```bash
   # Tester la connexion
   ping <broker_host>
   telnet <broker_host> <broker_port>
   ```

### Problème : Seed non synchronisé

**Symptômes** :
- "Seed: Not synchronized"
- "Seed: Sync failed"

**Solutions** :
1. **Vérifier la connexion MQTT**
   - S'assurer que la connexion au broker est établie

2. **Augmenter `seed_sync_timeout`**
   ```python
   # Si plusieurs instances démarrent simultanément
   myModel.enableDistributedGame(
       num_players=4,
       seed_sync_timeout=3.0  # Augmenter à 3 secondes
   )
   ```

3. **Vérifier que le créateur est connecté**
   - S'assurer que l'instance créatrice est bien connectée
   - Vérifier les logs pour les erreurs MQTT

### Problème : Session introuvable

**Symptômes** :
- La session n'apparaît pas dans "Available Sessions"
- Impossible de rejoindre une session

**Solutions** :
1. **Vérifier que la session est créée**
   - S'assurer que le créateur a bien créé la session
   - Vérifier que le `session_id` est correct

2. **Vérifier la connexion MQTT**
   - Les deux instances doivent être connectées au même broker
   - Vérifier `broker_host` et `broker_port`

3. **Attendre quelques secondes**
   - La découverte de sessions peut prendre quelques secondes
   - Rafraîchir la liste si nécessaire

### Problème : Nombre d'instances incorrect

**Symptômes** :
- Le nombre d'instances affiché ne correspond pas à la réalité
- Des instances déconnectées apparaissent encore

**Solutions** :
1. **Attendre la mise à jour automatique**
   - Les mises à jour peuvent prendre quelques secondes
   - Le système se met à jour automatiquement

2. **Vérifier la connexion MQTT**
   - S'assurer que toutes les instances sont connectées
   - Vérifier les logs pour les erreurs

3. **Redémarrer les instances**
   - Si le problème persiste, redémarrer les instances concernées

### Problème : Session fermée inopinément

**Symptômes** :
- Message "Session closed"
- Session retirée de la liste

**Causes possibles** :
1. **Créateur déconnecté**
   - Le créateur s'est déconnecté (brutalement ou via Cancel)
   - Solution : Rejoindre une nouvelle session ou créer une nouvelle session

2. **Timeout de heartbeat**
   - Le créateur n'a pas envoyé de heartbeat pendant 15 secondes
   - Solution : Vérifier la connexion du créateur, redémarrer si nécessaire

**Solutions** :
- Rejoindre une nouvelle session
- Créer une nouvelle session
- Vérifier la connexion réseau du créateur

### Problème : Le jeu ne démarre pas

**Symptômes** :
- Le nombre d'instances est insuffisant
- Message "waiting for X more instances"

**Solutions** :
1. **Vérifier la configuration `num_players`**
   ```python
   # Vérifier que la configuration correspond au nombre d'instances
   myModel.enableDistributedGame(num_players=4)  # Nécessite 4 instances
   ```

2. **Vérifier que toutes les instances sont connectées**
   - S'assurer que toutes les instances ont rejoint la session
   - Vérifier l'affichage "Instances: X/Y connected"

3. **Utiliser une plage si nécessaire**
   ```python
   # Permettre de démarrer avec moins de joueurs
   myModel.enableDistributedGame(num_players=(2, 4))  # 2 à 4 joueurs
   ```

---

## Conclusion

Ce guide couvre l'essentiel pour utiliser le système de jeux distribués dans SGE. Pour des questions spécifiques ou des problèmes non couverts, consultez la documentation technique ou les exemples dans le dossier `examples/games/`.

**Résumé des points clés** :
- Appelez `enableDistributedGame()` **avant** toute opération aléatoire
- Le seed est synchronisé automatiquement
- Utilisez `getConnectedInstancesCount()` pour récupérer le nombre d'instances
- Appelez `completeDistributedGameSetup()` dans `initAfterOpening()`
- Gérer le cas où l'utilisateur annule (retour `None`)

**Exemples complets** : Voir `examples/games/Sea_Zones_distributed2.py` pour un exemple complet.

