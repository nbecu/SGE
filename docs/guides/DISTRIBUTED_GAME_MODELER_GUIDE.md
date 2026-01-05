# Guide : Jeux Distribués dans SGE

Ce guide explique comment mettre en place et utiliser le système de jeux distribués dans SGE, permettant à plusieurs instances de votre modèle de jouer ensemble via MQTT.

---

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Mise en place dans le modèle](#mise-en-place-dans-le-modèle)
3. [Workflow complet](#workflow-complet)
4. [Phase 1 : Connexion et synchronisation](#phase-1--connexion-et-synchronisation)
5. [Phase 2 : Sélection du rôle de joueur](#phase-2--sélection-du-rôle-de-joueur)
6. [Paramètres de configuration](#paramètres-de-configuration)
7. [Récupération du nombre d'instances](#récupération-du-nombre-dinstances)
8. [États et comportements](#états-et-comportements)
9. [Exemples pratiques](#exemples-pratiques)
10. [Bonnes pratiques](#bonnes-pratiques)
11. [Dépannage](#dépannage)

---

## Vue d'ensemble

### Qu'est-ce qu'un jeu distribué ?

Un jeu distribué permet à plusieurs instances de votre modèle SGE de se connecter et de jouer ensemble. Chaque instance s'exécute sur une machine différente et communique via un broker MQTT.

### Concepts clés

- **Session** : Une session représente une partie de jeu. Chaque session a un identifiant unique (`session_id`).
- **Créateur** : L'instance qui crée la session. Elle est responsable de la synchronisation du seed et de la gestion de la session.
- **Joiner** : Une instance qui rejoint une session existante.
- **Seed synchronisé** : Toutes les instances utilisent le même seed aléatoire pour garantir la cohérence du jeu.
- **Rôle de joueur** : Chaque instance doit sélectionner un rôle de joueur (parmi les joueurs définis dans le modèle) après avoir rejoint une session.

### Workflow général

1. **Configuration** : Appel à `enableDistributedGame()` dans le script du modèle
2. **Phase 1 - Connexion** : Dialog de connexion (créer ou rejoindre une session)
3. **Synchronisation** : Le seed est synchronisé automatiquement
4. **Attente** : Les instances attendent que le nombre requis de joueurs soit connecté
5. **Phase 2 - Sélection du rôle** : Dialog de sélection du rôle de joueur (appelé automatiquement via `launch()`)
6. **Démarrage** : Le jeu peut démarrer lorsque toutes les conditions sont remplies

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
random_value = random.randint(1, 100)  # Utilise le seed synchronisé
```

### Exemple minimal

```python
# Configuration minimale
myModel.enableDistributedGame(num_players=2)

# Le reste de votre code...

# À la fin du script
myModel.launch()  # Appelle automatiquement completeDistributedGameSetup() si mode distribué
```

### Ordre d'exécution dans le script

1. Création de l'application Qt
2. Création du modèle (`SGModel`)
3. **Appel à `enableDistributedGame()`** ← ICI (avant toute opération aléatoire)
4. Toutes les autres opérations (création de grilles, agents, etc.)
5. **Appel à `myModel.launch()`** ← ICI
   - Si mode distribué activé : appelle automatiquement `completeDistributedGameSetup()` pour la sélection du rôle
   - Le dialog de sélection du rôle s'ouvre automatiquement avant l'affichage de la fenêtre

---

## Workflow complet

Le processus de mise en place d'un jeu distribué se déroule en deux phases principales :

### Phase 1 : Connexion et synchronisation (via `enableDistributedGame()`)

Cette phase est gérée par le dialog `SGDistributedConnectionDialog` qui s'ouvre automatiquement lors de l'appel à `enableDistributedGame()`.

**Étapes** :
1. Sélection du mode : "Create new session" ou "Join existing session"
2. Connexion au broker MQTT (automatique, basée sur `broker_host` et `broker_port` dans la configuration)
3. Synchronisation du seed
4. Attente que le nombre requis d'instances soit connecté
5. Le dialog se ferme automatiquement quand toutes les conditions sont remplies

### Phase 2 : Sélection du rôle de joueur (automatique via `launch()`)

Cette phase est gérée par le dialog `SGDistributedGameDialog` qui s'ouvre automatiquement lors de l'appel à `launch()` si le mode distribué est activé. Le dialog s'ouvre avant l'affichage de la fenêtre principale.

**Étapes** :
1. Affichage des rôles de joueur disponibles (basés sur les joueurs créés dans le modèle)
2. Sélection d'un rôle par chaque instance
3. Système de réservation pour éviter les conflits (si deux instances sélectionnent le même rôle)
4. Attente que toutes les instances aient sélectionné leur rôle
5. Le dialog se ferme automatiquement quand tous les rôles sont assignés

---

## Phase 1 : Connexion et synchronisation

### Dialog de connexion

Le dialog `SGDistributedConnectionDialog` s'ouvre automatiquement lors de l'appel à `enableDistributedGame()`.

### Mode "Create new session"

**Quand l'utiliser** : Pour créer une nouvelle session de jeu.

**Interface** :
- Radio button "Create new session" (sélectionné par défaut)
- Champ "Session ID" : Un ID unique est généré automatiquement, mais vous pouvez le modifier
- Bouton "📋" : Copier le Session ID dans le presse-papiers
- Bouton "Connect" : Se connecter au broker et créer la session

**Comportement** :
1. Un `session_id` unique est généré automatiquement (UUID4)
2. Vous pouvez modifier le Session ID si nécessaire
3. Cliquez sur "Connect" pour :
   - Se connecter au broker MQTT (utilise `broker_host` et `broker_port` de la configuration)
   - Créer la session
   - Synchroniser le seed (vous devenez le "leader" et générez le seed)
   - Attendre que d'autres instances rejoignent

**États affichés** :
- "Connection Status" : État de la connexion MQTT
- "Seed" : État de la synchronisation du seed
- "Instances" : Nombre d'instances connectées (format : `X/Y connected` ou `X/Y-Z connected`)

### Mode "Join existing session"

**Quand l'utiliser** : Pour rejoindre une session existante créée par une autre instance.

**Interface** :
- Radio button "Join existing session"
- Liste "Available Sessions" : Affiche les sessions disponibles avec :
  - Session ID (tronqué)
  - Nombre d'instances connectées
  - Nombre de joueurs enregistrés
  - Statut de la session (ouverte, fermée, etc.)
- Bouton "🔄" : Rafraîchir la liste des sessions
- Bouton "Connect" : Rejoindre la session sélectionnée (activé uniquement après sélection d'une session)

**Comportement** :
1. La liste des sessions disponibles se met à jour automatiquement toutes les 3 secondes
2. Cliquez sur une session dans la liste pour la sélectionner
3. Double-cliquez sur une session pour la sélectionner et vous connecter automatiquement
4. Cliquez sur "Connect" pour :
   - Se connecter au broker MQTT (si pas déjà connecté)
   - Rejoindre la session sélectionnée
   - Synchroniser le seed (vous recevez le seed du créateur)
   - Attendre que le nombre requis d'instances soit connecté

**Filtrage des sessions** :
- Seules les sessions "joinable" (ouvertes et non démarrées) sont affichées
- Les sessions fermées ou déjà démarrées ne peuvent pas être rejointes

### Synchronisation du seed

**Fonctionnement automatique** :
- **Créateur** : Si vous créez la session, votre seed devient le seed de référence (généré automatiquement si non fourni)
- **Joiner** : Si vous rejoignez, vous recevez le seed du créateur automatiquement

**Affichage** :
- "Seed: Synchronized ✓" (fond vert) : Seed synchronisé avec succès
- "Seed: Not synchronized" (fond jaune/rouge) : Seed non synchronisé

### Attente des instances

**Affichage** :
- Format pour nombre fixe : `Instances: X/Y connected`
- Format pour plage : `Instances: X/Y-Z connected`
- Format pour minimum seulement : `Instances: X/Y-∞ connected`

**États** :
- **En attente** : `Instances: X/Y connected (waiting for N more...)` (fond orange)
- **Minimum atteint** : `Instances: X/Y-Z connected ✓ (min)` (fond vert)
- **Maximum atteint** : `Instances: X/Y connected ✓` (fond vert)

**Comportement** :
- Le dialog se ferme automatiquement quand le nombre requis d'instances est connecté
- Le créateur peut démarrer manuellement si le minimum est atteint (bouton "Start Game")
- Si le maximum est atteint, un compte à rebours automatique démarre (3, 2, 1...)

### Gestion des erreurs de connexion

**Comportement** :
- Si la connexion au broker MQTT échoue, un message d'avertissement s'affiche (en anglais)
- L'application ne plante pas, vous pouvez réessayer après avoir corrigé le problème
- Les messages d'erreur incluent des suggestions de dépannage

**Types d'erreurs** :
- "Connection timed out" : Le broker ne répond pas
- "The broker may be closed or not running" : Le broker n'est pas accessible
- "The broker hostname could not be resolved" : Nom d'hôte invalide

---

## Phase 2 : Sélection du rôle de joueur

### Dialog de sélection du rôle

Le dialog `SGDistributedGameDialog` s'ouvre automatiquement lors de l'appel à `launch()` si le mode distribué est activé.

**Quand il s'ouvre** :
- Automatiquement lors de l'appel à `myModel.launch()` à la fin de votre script
- Après que la Phase 1 soit terminée (toutes les instances sont connectées et le seed est synchronisé)
- Avant l'affichage de la fenêtre principale du jeu

### Interface

**Éléments affichés** :
- **Titre** : "Select Your Player Role"
- **Connection Status** : Statut de la connexion MQTT (discret)
- **Session ID** : ID de la session (affichage discret, en lecture seule)
- **Number of players** : Nombre de joueurs requis (fixe ou plage)
- **Waiting status** : Message d'attente si vous avez sélectionné votre rôle mais que d'autres instances n'ont pas encore sélectionné le leur
- **Liste des rôles** : Radio buttons pour chaque joueur créé dans le modèle (exclut "Admin")

### Sélection d'un rôle

**Processus** :
1. Les rôles disponibles sont affichés sous forme de radio buttons
2. Cliquez sur un rôle pour le sélectionner
3. Le système de réservation vérifie automatiquement si le rôle est déjà pris
4. Si le rôle est disponible :
   - Le bouton radio devient vert et affiche "You have selected"
   - Votre réservation est confirmée
5. Si le rôle est déjà pris :
   - Le bouton radio devient gris et affiche "Already taken"
   - Vous devez sélectionner un autre rôle

### Système de réservation

**Fonctionnement** :
- Chaque instance "réserve" temporairement un rôle avant de le confirmer
- Si deux instances sélectionnent le même rôle simultanément, un conflit est détecté
- Le système résout automatiquement les conflits (premier arrivé, premier servi)
- Les réservations sont synchronisées via MQTT en temps réel

**États visuels** :
- **Disponible** : Bouton radio normal, texte : nom du joueur
- **Réservé par vous** : Bouton radio vert, texte : "Player Name - You have selected"
- **Réservé par autre** : Bouton radio gris, texte : "Player Name - Already taken"

### Attente de tous les joueurs

**Comportement** :
- Après avoir sélectionné votre rôle et cliqué sur "OK", vous entrez en mode "waiting"
- Un message s'affiche : "Waiting for other players to select their roles..."
- Le dialog se ferme automatiquement quand tous les joueurs ont sélectionné leur rôle
- Toutes les instances voient le dialog se fermer simultanément

**Synchronisation** :
- Le système utilise un message MQTT `all_players_selected` pour synchroniser la fermeture du dialog
- Ce message est publié quand tous les joueurs requis ont sélectionné leur rôle
- Toutes les instances reçoivent ce message et ferment leur dialog automatiquement

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
- Affiche : `Instances: X/Y connected`

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

### Configuration MQTT

#### `broker_host` (str, défaut: `"localhost"`)

Adresse du broker MQTT. **Note** : Ce paramètre est configuré dans `enableDistributedGame()`, pas dans l'interface utilisateur.

```python
# Broker local
myModel.enableDistributedGame(num_players=4, broker_host="localhost")

# Broker distant
myModel.enableDistributedGame(num_players=4, broker_host="192.168.1.100")

# Broker avec nom de domaine
myModel.enableDistributedGame(num_players=4, broker_host="mqtt.example.com")
```

#### `broker_port` (int, défaut: `1883`)

Port du broker MQTT. **Note** : Ce paramètre est configuré dans `enableDistributedGame()`, pas dans l'interface utilisateur.

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

```python
# Timeout par défaut (1 seconde)
myModel.enableDistributedGame(num_players=4)

# Timeout augmenté (3 secondes)
myModel.enableDistributedGame(num_players=4, seed_sync_timeout=3.0)
```

### Session ID : `session_id` (optionnel)

Identifiant unique de la session. Si non fourni, un ID est généré automatiquement.

```python
# Génération automatique (recommandé)
myModel.enableDistributedGame(num_players=4)

# Session ID personnalisé
myModel.enableDistributedGame(num_players=4, session_id="my-custom-session-123")
```

**Quand l'utiliser** :
- Pour créer une session avec un nom reconnaissable
- Pour des tests ou démonstrations
- **Note** : En mode "Join", vous sélectionnez la session depuis la liste, pas besoin de spécifier l'ID

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

---

## États et comportements

### États de la Phase 1 (Connection Dialog)

#### SETUP
**Quand** : État initial, avant toute connexion

**Caractéristiques** :
- Aucune connexion au broker
- Aucune session créée ou rejointe
- Seed non synchronisé

**Interface utilisateur** :
- Mode "Create new session" ou "Join existing session" sélectionnable
- Bouton "Connect" disponible (désactivé en mode "Join" jusqu'à sélection d'une session)

#### CONNECTING
**Quand** : Pendant la tentative de connexion au broker MQTT et la synchronisation du seed

**Caractéristiques** :
- Tentative de connexion active
- Synchronisation du seed en cours

**Interface utilisateur** :
- "Connection Status: Connecting..."
- Bouton "Connect" désactivé

#### WAITING
**Quand** : Session active, seed synchronisé, mais nombre d'instances insuffisant

**Caractéristiques** :
- Connexion MQTT établie
- Session active (créée ou rejointe)
- Seed synchronisé
- Nombre d'instances < minimum requis

**Interface utilisateur** :
- "Instances: X/Y connected (waiting for N more...)" (fond orange)
- Le nombre X augmente au fur et à mesure que d'autres instances rejoignent

#### READY_MIN
**Quand** : Nombre minimum d'instances atteint (pour plages de joueurs)

**Caractéristiques** :
- Session active
- Seed synchronisé
- Nombre d'instances = minimum requis
- Jeu peut démarrer (démarrage manuel disponible pour le créateur)

**Interface utilisateur** :
- "Instances: X/Y-Z connected ✓ (min)" (fond vert)
- Bouton "Start Game" disponible (créateur uniquement)

#### READY_MAX
**Quand** : Nombre maximum d'instances atteint (pour plages de joueurs)

**Caractéristiques** :
- Session active
- Seed synchronisé
- Nombre d'instances = maximum requis
- Compte à rebours automatique démarre (3, 2, 1...)

**Interface utilisateur** :
- "Instances: X/Y connected ✓" (fond vert)
- Compte à rebours affiché : "Starting game in 3... 2... 1..."
- Le dialog se ferme automatiquement à la fin du compte à rebours

### États de la Phase 2 (Player Role Selection Dialog)

#### Sélection en cours
**Quand** : L'utilisateur n'a pas encore sélectionné son rôle

**Caractéristiques** :
- Tous les rôles sont disponibles (sauf ceux déjà pris)
- L'utilisateur peut sélectionner un rôle

**Interface utilisateur** :
- Radio buttons activés pour les rôles disponibles
- Bouton "OK" activé

#### Réservation confirmée
**Quand** : L'utilisateur a sélectionné un rôle et cliqué sur "OK"

**Caractéristiques** :
- Le rôle est réservé pour cette instance
- L'instance attend que les autres instances sélectionnent leur rôle

**Interface utilisateur** :
- Radio button du rôle sélectionné : vert, texte "Player Name - You have selected"
- Autres radio buttons : désactivés
- Message d'attente : "Waiting for other players to select their roles..."
- Bouton "OK" désactivé

#### Tous les joueurs sélectionnés
**Quand** : Tous les joueurs requis ont sélectionné leur rôle

**Caractéristiques** :
- Toutes les instances ont sélectionné leur rôle
- Le dialog se ferme automatiquement sur toutes les instances

**Interface utilisateur** :
- Le dialog se ferme automatiquement
- Le jeu peut démarrer

### Comportements particuliers

#### Déconnexion du créateur

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

#### Déconnexion d'une instance (non-créateur)

**Comportement** :
- Si une instance non-créateur se déconnecte, le compteur d'instances est mis à jour automatiquement
- Les autres instances voient le nombre d'instances diminuer
- La session reste active tant que le créateur est connecté

**Exemple** :
- 4 instances connectées → Instance 2 se déconnecte → 3 instances connectées
- Affichage mis à jour automatiquement : "Instances: 3/4 connected"

#### Timeout et heartbeat

**Système de heartbeat** :
- Le créateur envoie un heartbeat toutes les 5 secondes
- Les autres instances vérifient le heartbeat toutes les 3 secondes
- Timeout : 15 secondes sans heartbeat = créateur déconnecté

**Comportement** :
- Si le créateur ne répond pas pendant 15 secondes, la session est fermée automatiquement
- Les autres instances sont notifiées et doivent quitter

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

# Launch the game (la sélection du rôle se fait automatiquement si mode distribué)
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

### Exemple 3 : Configuration MQTT personnalisée

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

### Exemple 4 : Gestion du cas d'annulation

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
# Dans votre code de jeu, vérifier si mode distribué
if myModel.isDistributed():
    # Code spécifique au mode distribué
    nb_players = myModel.getConnectedInstancesCount(default=4)
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
- Tester la sélection de rôles avec conflits

---

## Dépannage

### Problème : Impossible de se connecter au broker MQTT

**Symptômes** :
- Message d'avertissement "Unable to connect to MQTT broker"
- Dialog affiche un message d'erreur avec des suggestions

**Solutions** :
1. **Vérifier que le broker MQTT est en cours d'exécution**
   ```bash
   # Sur Linux/Mac
   systemctl status mosquitto
   
   # Vérifier les processus
   ps aux | grep mosquitto
   ```

2. **Vérifier `broker_host` et `broker_port` dans `enableDistributedGame()`**
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
   
   # Sur Windows PowerShell
   Test-NetConnection -ComputerName <broker_host> -Port <broker_port>
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

### Problème : Session introuvable dans la liste

**Symptômes** :
- La session n'apparaît pas dans "Available Sessions"
- Impossible de rejoindre une session

**Solutions** :
1. **Vérifier que la session est créée**
   - S'assurer que le créateur a bien créé la session
   - Vérifier que le créateur est toujours connecté

2. **Vérifier la connexion MQTT**
   - Les deux instances doivent être connectées au même broker
   - Vérifier `broker_host` et `broker_port`

3. **Attendre quelques secondes**
   - La découverte de sessions peut prendre quelques secondes
   - Cliquer sur le bouton "🔄" pour rafraîchir la liste

4. **Vérifier que la session est joinable**
   - Les sessions fermées ou déjà démarrées ne peuvent pas être rejointes
   - Seules les sessions ouvertes apparaissent dans la liste

### Problème : Rôle de joueur déjà pris

**Symptômes** :
- Le rôle que vous voulez sélectionner affiche "Already taken"
- Impossible de sélectionner le rôle souhaité

**Solutions** :
1. **Sélectionner un autre rôle**
   - Choisir un rôle disponible dans la liste
   - Le système de réservation empêche les conflits automatiquement

2. **Attendre que le rôle soit libéré**
   - Si une instance se déconnecte, son rôle devient disponible
   - La liste se met à jour automatiquement

### Problème : Le dialog de sélection de rôle ne se ferme pas

**Symptômes** :
- Vous avez sélectionné votre rôle
- Le message "Waiting for other players..." s'affiche
- Le dialog ne se ferme pas

**Solutions** :
1. **Vérifier que toutes les instances ont sélectionné leur rôle**
   - Chaque instance doit sélectionner un rôle unique
   - Le nombre de rôles sélectionnés doit correspondre au nombre d'instances connectées

2. **Vérifier la connexion MQTT**
   - S'assurer que toutes les instances sont connectées
   - Vérifier les logs pour les erreurs MQTT

3. **Redémarrer les instances si nécessaire**
   - Si le problème persiste, redémarrer toutes les instances

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

---

## Conclusion

Ce guide couvre l'essentiel pour utiliser le système de jeux distribués dans SGE. Pour des questions spécifiques ou des problèmes non couverts, consultez la documentation technique ou les exemples dans le dossier `examples/games/`.

**Résumé des points clés** :
- Appelez `enableDistributedGame()` **avant** toute opération aléatoire
- Le seed est synchronisé automatiquement
- Utilisez `getConnectedInstancesCount()` pour récupérer le nombre d'instances
- Appelez `launch()` à la fin de votre script (la sélection du rôle se fait automatiquement)
- Gérer le cas où l'utilisateur annule (retour `None`)
- Les erreurs de connexion MQTT affichent des messages d'avertissement clairs (en anglais) au lieu de faire planter l'application

**Exemples complets** : Voir `examples/games/Sea_Zones_distributed2.py` et `Sea_Zones_distributed2_freebox.py` pour des exemples complets.
