# Documentation : Gestion des Sessions Distribuées - État Actuel et Solutions

## Date de création
Date actuelle : Documentation pour reprise du chantier

## Contexte

Ce document décrit l'architecture actuelle du système de gestion de sessions distribuées, les difficultés rencontrées, et les solutions proposées pour résoudre les problèmes de synchronisation liés aux messages MQTT retenus.

---

## 1. Architecture Actuelle

### 1.1 Composants Principaux

#### 1.1.1 `SGDistributedSession` (nouveau fichier)
**Fichier** : `mainClasses/SGDistributedSession.py`

**Rôle** : Classe représentant l'état d'une session distribuée. Cette classe est la **source de vérité unique** pour l'état d'une session.

**Attributs clés** :
- `session_id` : Identifiant unique de la session
- `creator_client_id` : ClientId de l'instance qui a créé la session
- `model_name` : Nom du modèle/jeu
- `state` : État de la session ('open', 'closed', 'starting', 'in_progress')
- `connected_instances` : Liste des clientIds actuellement connectés à la session
- `version` : Numéro de version pour la résolution de conflits
- `last_heartbeat` : Timestamp du dernier heartbeat du créateur
- `created_at`, `last_updated` : Timestamps de création et dernière mise à jour

**Méthodes principales** :
- `to_dict()` / `from_dict()` : Sérialisation JSON
- `add_instance(client_id)` : Ajouter une instance (incrémente version)
- `remove_instance(client_id)` : Retirer une instance (incrémente version)
- `close()` : Fermer la session (incrémente version)
- `update_heartbeat()` : Mettre à jour le heartbeat (sans incrémenter version)
- `is_expired(timeout_seconds)` : Vérifier si la session est expirée
- `can_accept_more_instances()` : Vérifier si la session peut accepter plus d'instances

**Topic MQTT** : `session_state/{session_id}` avec `retain=True`, `qos=1`

#### 1.1.2 `SGDistributedSessionManager`
**Fichier** : `mainClasses/SGDistributedSessionManager.py`

**Rôle** : Gère les opérations de session via MQTT.

**Méthodes de gestion du session state** (ajoutées récemment) :
- `publishSessionState(session)` : Publie l'état de session sur MQTT
  - Si session fermée : publie message vide pour effacer le message retenu
  - Sinon : publie le JSON de la session avec `retain=True`
- `readSessionState(session_id, timeout)` : Lit l'état de session depuis le broker
  - Gère les messages vides (session fermée)
  - Timeout configurable
- `updateSessionState(session_id, updater, max_retries)` : Met à jour l'état avec résolution de conflits
  - Pattern read-modify-write avec vérification de version
  - Retry automatique en cas de conflit (max 3 tentatives)
- `subscribeToSessionState(session_id, callback)` : S'abonne aux mises à jour en temps réel
  - Callback appelé à chaque mise à jour du session state

**Topics MQTT existants** (anciens, toujours utilisés) :
- `{session_id}/session_player_registration/{client_id}` : Enregistrement de joueur (avec `retain=True`)
- `{session_id}/session_instance_ready/{client_id}` : Instance prête (avec `retain=True`)
- `{session_id}/session_player_disconnect/{client_id}` : Déconnexion (sans `retain`)
- `session_discovery/{session_id}` : Découverte de sessions (avec `retain=True`)

#### 1.1.3 `SGDistributedConnectionDialog`
**Fichier** : `mainClasses/SGDistributedConnectionDialog.py`

**Rôle** : Dialog pour la connexion MQTT et la synchronisation des seeds.

**Flux de connexion** :

1. **Mode "Create new session"** :
   - Connexion au broker MQTT
   - Synchronisation du seed (`_syncSeed()`)
   - Initialisation du session state (`_initializeSessionState()`)
     - Crée un nouveau `SGDistributedSession`
     - Publie le session state initial
   - Publication de la découverte de session (`publishSession()`)
   - Abonnement aux mises à jour du session state (`_subscribeToSessionStateUpdates()`)
   - Démarrage du polling périodique (`_startSessionStatePolling()`)
   - Démarrage du heartbeat si créateur (`_startSessionStateHeartbeat()`)
   - Démarrage de la vérification du créateur (`_startCreatorCheckTimer()`)

2. **Mode "Join existing session"** :
   - Connexion au broker MQTT
   - Démarrage de la découverte de sessions (`_startSessionDiscovery()`)
   - L'utilisateur sélectionne une session dans la liste
   - Synchronisation du seed
   - Lecture du session state existant
   - Ajout de l'instance au session state
   - Abonnement aux mises à jour

**Mécanismes de synchronisation** :

- **Subscription MQTT temps réel** : `subscribeToSessionState()` avec callback
- **Polling périodique** : Timer toutes les 2 secondes pour lire le session state
- **Heartbeat du créateur** : Timer toutes les 5 secondes pour mettre à jour le heartbeat
- **Vérification du créateur** : Timer toutes les 3 secondes pour détecter la déconnexion (timeout 15s)

**Mise à jour de la liste "Available Sessions"** :

- `_updateSessionsList()` : Lit le session state pour chaque session découverte
- Utilise `session_state.connected_instances` comme source de vérité
- Synchronise le cache `session_instances_cache` avec le session state
- Affiche une coche ✓ pour la session connectée

**Anciens mécanismes de tracking** (encore présents, source de problèmes) :

- `session_instances_cache` : Cache des instances par session
- `_subscribeToPlayerRegistrationForTracking()` : Tracker les messages `player_registration`
- `_subscribeToInstanceReady()` : Tracker les messages `instance_ready`
- Ces handlers mettent à jour le cache, mais avec vérifications pour éviter les messages retenus obsolètes

### 1.2 Flux de Données

```
Instance 1 (Créateur)              Instance 2 (Join)
     |                                    |
     |-- Crée session_state/{id}          |
     |   (retain=True)                     |
     |                                    |
     |                                    |-- S'abonne à session_state/{id}
     |                                    |-- Reçoit message retenu
     |                                    |-- Lit état initial
     |                                    |
     |-- Ajoute instance 2                |
     |   (updateSessionState)             |
     |                                    |
     |-- Publie session_state/{id}        |
     |   (version incrémentée)            |
     |                                    |-- Reçoit mise à jour via callback
     |                                    |-- Met à jour localement
     |                                    |
     |-- Heartbeat toutes les 5s          |
     |                                    |-- Vérifie heartbeat toutes les 3s
     |                                    |
     |-- Instance 2 quitte                |
     |                                    |
     |-- Retire instance 2                |
     |   (updateSessionState)             |
     |                                    |
     |-- Publie session_state/{id}        |
     |   (version incrémentée)            |
     |                                    |-- Reçoit mise à jour
     |                                    |-- Met à jour localement
```

### 1.3 Problème Actuel : Messages Retenus Obsolètes

**Symptôme** : Quand une instance quitte, le nombre d'instances affiché revient temporairement à l'ancienne valeur (ex: 2/4 au lieu de 1/4).

**Cause racine** :

1. Les anciens topics utilisent `retain=True` :
   - `session_player_registration/{client_id}` avec `retain=True`
   - `session_instance_ready/{client_id}` avec `retain=True`

2. Quand une instance quitte :
   - Le session state est correctement mis à jour (1 instance)
   - Mais les messages retenus restent sur le broker

3. Quand une nouvelle instance s'abonne ou qu'un handler se réinitialise :
   - Les messages retenus sont reçus
   - Les anciens handlers (`player_registration_tracker`, `instance_ready_handler`) tentent de mettre à jour le cache
   - Même avec vérifications, il y a des cas où le cache est mis à jour incorrectement

4. Le cache corrompu affecte l'affichage :
   - `_updateSessionsList()` lit le session state (correct)
   - Mais le cache peut être mis à jour par les anciens handlers
   - Si le session state n'est pas disponible temporairement, le cache (incorrect) est utilisé

---

## 2. Difficultés Rencontrées

### 2.1 Messages Retenus MQTT

**Problème** : Les messages retenus (`retain=True`) restent sur le broker même après qu'une instance a quitté la session.

**Impact** :
- Les nouveaux abonnés reçoivent des messages obsolètes
- Les handlers peuvent réintroduire des instances déconnectées dans le cache
- Incohérences temporaires dans l'affichage

**Tentatives de résolution** :
1. Vérification du session state avant de mettre à jour le cache
2. Synchronisation du cache avec le session state dans `_updateSessionsList()`
3. Ignorer les messages si l'instance n'est pas dans le session state

**Résultat** : Amélioration mais problème persistant dans certains cas.

### 2.2 Gestion des Handlers MQTT

**Problème** : Plusieurs handlers MQTT se chaînent et peuvent entrer en conflit.

**Handlers existants** :
- Handler de découverte de sessions
- Handler de tracking des player registrations
- Handler de tracking des instance ready
- Handler du session state
- Handler du game start
- Handler original

**Complexité** : Gérer le chaînage correctement sans perdre de messages.

### 2.3 Race Conditions

**Problème** : Mises à jour concurrentes du session state.

**Solution partielle** : Versioning avec retry automatique dans `updateSessionState()`.

**Limitation** : Le timeout de 0.2-0.5s pour lire le session state peut être insuffisant dans certains cas.

### 2.4 Synchronisation Cache vs Session State

**Problème** : Le cache `session_instances_cache` peut être désynchronisé avec le session state.

**Tentative de résolution** : Synchronisation dans `_updateSessionsList()`, mais le cache peut être corrompu entre-temps par les anciens handlers.

---

## 3. Solutions Proposées

### 3.1 Solution 1 : Ne pas utiliser de messages retenus pour les états dynamiques

**Principe** : Désactiver `retain=True` pour les topics qui représentent des états dynamiques.

**Topics concernés** :
- `{session_id}/session_player_registration/{client_id}` : Passer à `retain=False`
- `{session_id}/session_instance_ready/{client_id}` : Passer à `retain=False`

**Topics à conserver avec `retain=True`** :
- `session_state/{session_id}` : Source de vérité, doit être retenu
- `session_discovery/{session_id}` : Découverte de sessions, doit être retenu

**Avantages** :
- Élimine le problème à la source
- Plus simple à maintenir
- Pas de messages obsolètes

**Inconvénients** :
- Les nouveaux abonnés ne reçoivent plus l'état initial via les messages retenus
- Nécessite de s'appuyer uniquement sur `session_state` pour l'état initial

**Implémentation** :

1. Modifier `registerPlayer()` dans `SGDistributedSessionManager` :
   ```python
   # Avant
   self.mqtt_manager.client.publish(topic, serialized_msg, qos=1, retain=True)
   
   # Après
   self.mqtt_manager.client.publish(topic, serialized_msg, qos=1, retain=False)
   ```

2. Modifier `_publishInstanceReady()` dans `SGDistributedConnectionDialog` :
   ```python
   # Avant
   result = self.model.mqttManager.client.publish(
       instance_ready_topic, 
       serialized_msg, 
       qos=1,
       retain=True
   )
   
   # Après
   result = self.model.mqttManager.client.publish(
       instance_ready_topic, 
       serialized_msg, 
       qos=1,
       retain=False
   )
   ```

3. Nettoyer les anciens messages retenus lors de la migration :
   - Publier des messages vides avec `retain=True` sur tous les topics concernés

**Impact sur le code existant** :
- Les handlers `_subscribeToPlayerRegistrationForTracking()` et `_subscribeToInstanceReady()` ne recevront plus de messages retenus
- Ces handlers peuvent être simplifiés ou supprimés
- `_updateSessionsList()` doit s'appuyer uniquement sur `session_state`

### 3.2 Solution 2 : Nettoyer explicitement les messages retenus obsolètes

**Principe** : Quand une instance quitte, publier des messages vides avec `retain=True` pour effacer les messages retenus.

**Avantages** :
- Solution immédiate sans refonte majeure
- Compatible avec l'architecture actuelle
- Simple à implémenter

**Implémentation** :

Dans `_cancelConnection()` de `SGDistributedConnectionDialog`, après la mise à jour du session state :

```python
# Nettoyer les messages retenus pour cette instance
if self.config.session_id and self.model.mqttManager.clientId:
    client_id = self.model.mqttManager.clientId
    session_topics = self.session_manager.getSessionTopics(self.config.session_id)
    
    # Nettoyer player_registration
    registration_topic = f"{session_topics[0]}/{client_id}"  # session_player_registration/{client_id}
    self.model.mqttManager.client.publish(registration_topic, "", qos=1, retain=True)
    
    # Nettoyer instance_ready
    instance_ready_topic_base = session_topics[4]  # session_instance_ready
    instance_ready_topic = f"{instance_ready_topic_base}/{client_id}"
    self.model.mqttManager.client.publish(instance_ready_topic, "", qos=1, retain=True)
    
    print(f"[Dialog] Cleared retained messages for {client_id[:8]}...")
```

**Points d'attention** :
- Faire cela AVANT de mettre à jour le session state pour éviter les race conditions
- Attendre un court délai après publication pour s'assurer que le message est propagé
- Gérer les erreurs de publication

**Impact** :
- Les nouveaux abonnés ne recevront plus les messages retenus obsolètes
- Le problème de réintroduction des instances déconnectées est résolu

### 3.3 Solution 3 : S'appuyer uniquement sur session_state comme source de vérité

**Principe** : Utiliser `session_state` comme seule source pour compter les instances. Les autres topics ne servent que pour les notifications en temps réel.

**Avantages** :
- Source de vérité unique et centralisée
- Plus de conflits entre cache et session state
- Architecture plus simple et maintenable

**Implémentation** :

1. **Simplifier `_updateSessionsList()`** :
   - Ne lire que `session_state` pour chaque session
   - Ne plus utiliser `session_instances_cache` comme fallback
   - Si `session_state` n'est pas disponible, afficher "?" ou utiliser les infos de découverte

2. **Simplifier les handlers de tracking** :
   - `_subscribeToPlayerRegistrationForTracking()` : Ne plus mettre à jour le cache, juste notifier
   - `_subscribeToInstanceReady()` : Ne plus mettre à jour le cache, juste notifier
   - Ces handlers peuvent être supprimés ou simplifiés

3. **Utiliser `session_state` pour toutes les décisions** :
   - Compter les instances : `len(session_state.connected_instances)`
   - Vérifier si une instance est connectée : `client_id in session_state.connected_instances`
   - Détecter les déconnexions : Comparer les versions du session state

**Code modifié** :

```python
def _updateSessionsList(self):
    # ...
    for session_id, session_data in sorted_sessions:
        # TOUJOURS lire le session state (source de vérité)
        session_state = self.session_manager.readSessionState(session_id, timeout=0.5)
        
        if session_state is None:
            # Session state non disponible - utiliser découverte comme fallback
            num_min = info.get('num_players_min', '?')
            num_max = info.get('num_players_max', '?')
            num_instances = 0  # Ne pas utiliser le cache
        else:
            # Utiliser session state comme source de vérité
            num_min = session_state.num_players_min
            num_max = session_state.num_players_max
            num_instances = len(session_state.connected_instances)
            
            # Synchroniser le cache (pour compatibilité, mais ne plus l'utiliser)
            self.session_instances_cache[session_id] = set(session_state.connected_instances)
            
            if session_state.state == 'closed' or session_state.is_expired():
                continue
```

**Impact** :
- Suppression de la dépendance au cache pour l'affichage
- Code plus simple et plus fiable
- Moins de race conditions

---

## 4. Plan d'Implémentation Recommandé

### Phase 1 : Solution 2 (Nettoyage explicite) - PRIORITÉ 1
**Objectif** : Résoudre le problème immédiatement

**Tâches** :
1. Ajouter le nettoyage des messages retenus dans `_cancelConnection()`
2. Tester avec plusieurs instances qui quittent
3. Vérifier que les messages retenus sont bien effacés

**Durée estimée** : 1-2 heures

### Phase 2 : Solution 1 (Désactiver retain) - PRIORITÉ 2
**Objectif** : Prévenir le problème à la source

**Tâches** :
1. Modifier `registerPlayer()` pour `retain=False`
2. Modifier `_publishInstanceReady()` pour `retain=False`
3. Nettoyer les anciens messages retenus (migration)
4. Tester que les nouveaux abonnés reçoivent bien l'état via `session_state`

**Durée estimée** : 2-3 heures

### Phase 3 : Solution 3 (Source de vérité unique) - PRIORITÉ 3
**Objectif** : Simplifier l'architecture

**Tâches** :
1. Simplifier `_updateSessionsList()` pour ne s'appuyer que sur `session_state`
2. Supprimer ou simplifier les handlers de tracking
3. Supprimer la dépendance au cache `session_instances_cache`
4. Tests complets de toutes les fonctionnalités

**Durée estimée** : 3-4 heures

---

## 5. Points d'Attention pour la Reprise

### 5.1 Fichiers Clés à Modifier

1. **`mainClasses/SGDistributedConnectionDialog.py`** :
   - `_cancelConnection()` : Ajouter nettoyage des messages retenus
   - `_publishInstanceReady()` : Changer `retain=True` à `retain=False`
   - `_updateSessionsList()` : Simplifier pour ne s'appuyer que sur `session_state`
   - `_subscribeToPlayerRegistrationForTracking()` : Simplifier ou supprimer
   - `_subscribeToInstanceReady()` : Simplifier ou supprimer

2. **`mainClasses/SGDistributedSessionManager.py`** :
   - `registerPlayer()` : Changer `retain=True` à `retain=False`

### 5.2 Tests à Effectuer

1. **Test de déconnexion** :
   - Instance 1 crée une session
   - Instance 2 rejoint
   - Instance 2 quitte
   - Vérifier que la liste affiche "1/4 instances" et reste stable

2. **Test de messages retenus** :
   - Instance 1 crée une session
   - Instance 2 rejoint
   - Instance 2 quitte
   - Instance 3 rejoint (nouvelle instance)
   - Vérifier que l'instance 3 ne voit pas l'instance 2 dans la liste

3. **Test de découverte** :
   - Instance 1 crée une session
   - Instance 2 démarre en mode "join"
   - Vérifier que la session apparaît dans la liste

4. **Test de heartbeat** :
   - Instance 1 crée une session
   - Instance 2 rejoint
   - Instance 1 quitte brutalement (fermeture de l'application)
   - Vérifier que l'instance 2 détecte la déconnexion et ferme la session

### 5.3 Logs à Surveiller

- `[Dialog] Published session state` : Vérifier que le session state est bien publié
- `[Dialog] Received session state update` : Vérifier que les mises à jour sont reçues
- `[Dialog] Ignoring ... for disconnected instance` : Vérifier que les messages obsolètes sont ignorés
- `[Dialog] Cleared retained messages` : Vérifier que le nettoyage fonctionne

---

## 6. Architecture Cible (Après Implémentation)

```
┌─────────────────────────────────────────────────────────────┐
│                    Source de Vérité Unique                   │
│              session_state/{session_id}                      │
│              (retain=True, qos=1)                            │
│                                                              │
│  - connected_instances: [client_id1, client_id2]            │
│  - version: 3                                                │
│  - state: 'open'                                             │
│  - last_heartbeat: timestamp                                 │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ (lecture/écriture)
                          │
        ┌─────────────────┴─────────────────┐
        │                                     │
┌───────▼────────┐                  ┌────────▼──────┐
│ Instance 1     │                  │ Instance 2     │
│ (Créateur)     │                  │ (Join)         │
│                │                  │                │
│ - Heartbeat    │                  │ - Polling      │
│   (5s)         │                  │   (2s)         │
│ - Subscription │                  │ - Subscription │
│   (temps réel) │                  │   (temps réel) │
└────────────────┘                  └────────────────┘

Topics de notification (retain=False, qos=1) :
- session_player_registration/{client_id} : Notification uniquement
- session_instance_ready/{client_id} : Notification uniquement
- session_player_disconnect/{client_id} : Notification uniquement
```

---

## 7. Notes Techniques

### 7.1 Versioning et Conflits

Le système utilise un mécanisme de versioning pour gérer les conflits :
- Chaque mise à jour incrémente `version`
- `updateSessionState()` utilise un pattern read-modify-write avec retry
- En cas de conflit (version différente), retry automatique (max 3 tentatives)

### 7.2 Heartbeat et Détection de Déconnexion

- **Heartbeat du créateur** : Toutes les 5 secondes
- **Vérification par les autres instances** : Toutes les 3 secondes
- **Timeout** : 15 secondes (3 vérifications × 5 secondes)
- Si le heartbeat est expiré, la session est fermée automatiquement

### 7.3 Messages Retenus vs Messages Normaux

**Messages retenus** (`retain=True`) :
- Stockés par le broker
- Envoyés automatiquement aux nouveaux abonnés
- Utiles pour l'état initial
- Problématique pour les états dynamiques

**Messages normaux** (`retain=False`) :
- Non stockés par le broker
- Envoyés uniquement aux abonnés actifs
- Utiles pour les notifications en temps réel
- Pas de problème d'obsolescence

---

## 8. Références

- **Plan initial** : `PLAN_DISTRIBUTED_SESSION_MANAGEMENT.md`
- **Bilan des modifications** : `BILAN_MODIFICATIONS_SESSION_CONNECT.md`
- **Spécification** : `DISTRIBUTED_GAME_SPECIFICATION_V2.md`

---

## 9. Conclusion

Le système actuel avec `SGDistributedSession` est bien conçu et fournit une base solide. Le problème principal vient de l'utilisation de messages retenus pour des états dynamiques. Les solutions proposées (1, 2, 3) sont complémentaires et doivent être implémentées dans l'ordre de priorité indiqué pour résoudre définitivement le problème de synchronisation.

**Recommandation finale** : Implémenter les trois solutions dans l'ordre de priorité pour une solution robuste et maintenable.

