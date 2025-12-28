# Diagnostic : Gestion des Sessions Distribuées - État Actuel et Recommandations

## Date
Diagnostic réalisé pour évaluer l'état actuel du système de gestion de sessions distribuées et proposer un plan d'action fiable.

---

## 0. Approche UX Validée

**Recommandation UX** : Unification avec rôles distincts
- **Source de vérité unique** : `session_state.connected_instances` (Phase 2)
- **Rôles différents** : Navigation (liste "Available Sessions") vs Monitoring (bas de fenêtre)
- **Même information** : Les deux affichages montrent le même nombre pour la même session
- **Cohérence garantie** : Plus de désynchronisation possible

**Implémentation** : Intégrée dans Phase 2 du plan d'implémentation.

Voir `RECOMMANDATION_UX_AFFICHAGE_INSTANCES.md` pour les détails complets.

---

## 1. État Actuel de l'Implémentation

### 1.1 Ce qui existe

#### ✅ Infrastructure de base
- **`SGDistributedSessionManager`** : Classe existante gérant les opérations MQTT de session
- **`SGDistributedConnectionDialog`** : Dialog complet pour connexion et synchronisation
- **Système de découverte de sessions** : Fonctionnel via `session_discovery/{session_id}`
- **Synchronisation de seed** : Implémentée avec gestion du leader
- **Tracking des instances** : Via `session_instance_ready/{client_id}` avec `retain=True`

#### ⚠️ Ce qui manque (selon Plan V1)
- **`SGDistributedSession`** : Classe non implémentée (fichier absent)
- **Méthodes de gestion du session state** : `publishSessionState()`, `readSessionState()`, `updateSessionState()`, `subscribeToSessionState()` non trouvées dans le code
- **Topic `session_state/{session_id}`** : Non utilisé actuellement
- **Système de versioning** : Non implémenté

### 1.2 Architecture Actuelle (Réelle)

```
┌─────────────────────────────────────────────────────────────┐
│              Système Actuel (Sans Session State)               │
└─────────────────────────────────────────────────────────────┘

Sources de vérité multiples (PROBLÉMATIQUE) :
1. session_discovery/{session_id} (retain=True) → Info de base
2. session_instance_ready/{client_id} (retain=True) → Instances prêtes
3. session_player_registration/{player_name} (retain=True) → Joueurs enregistrés
4. session_instances_cache (local) → Cache mis à jour par handlers

Flux actuel :
- Découverte : session_discovery → available_sessions
- Comptage instances : session_instance_ready → session_instances_cache → _updateSessionsList()
- Problème : Messages retenus obsolètes corrompent le cache
```

---

## 2. Problèmes Identifiés

### 2.1 Problème Principal : Messages Retenus Obsolètes

**Symptôme observé** :
- Quand une instance quitte, le nombre d'instances affiché revient temporairement à l'ancienne valeur (ex: 2/4 au lieu de 1/4)

**Cause racine** :
1. **Messages retenus persistants** : `session_instance_ready/{client_id}` avec `retain=True` reste sur le broker même après déconnexion
2. **Handlers multiples** : Plusieurs handlers (`_subscribeToInstanceReady()`, `_subscribeToPlayerRegistrationForTracking()`) mettent à jour `session_instances_cache`
3. **Réception lors de réabonnement** : Quand un handler se réinitialise ou qu'une nouvelle instance s'abonne, les messages retenus sont reçus
4. **Cache corrompu** : Le cache est mis à jour avec des instances déconnectées, même avec vérifications

**Code problématique identifié** :
```python
# Ligne 1822 de SGDistributedConnectionDialog.py
self.session_instances_cache[session_id].add(sender_client_id)
# Aucune vérification que l'instance est toujours connectée
```

### 2.2 Architecture Fragile : Sources de Vérité Multiples

**Problème** :
- `session_instances_cache` (local) peut être désynchronisé avec la réalité
- `_updateSessionsList()` utilise le cache comme source principale (ligne 683)
- Pas de mécanisme de réconciliation automatique

**Code actuel** :
```python
# Ligne 683 de SGDistributedConnectionDialog.py
connected_instances = self.session_instances_cache.get(session_id, set())
num_instances = len(connected_instances)
# Utilise le cache directement, sans vérification
```

### 2.3 Handlers MQTT Complexes et Fragiles

**Problème** :
- Chaînage de handlers (`game_start_handler` → `instance_ready_handler` → `player_registration_tracker` → ...)
- Gestion complexe de l'ordre d'installation
- Risque de perte de messages ou de duplication
- Difficulté à déboguer

**Handlers identifiés** :
1. `registration_message_handler` (SGDistributedSessionManager)
2. `instance_ready_handler` (SGDistributedConnectionDialog)
3. `player_registration_tracking_wrapper` (SGDistributedConnectionDialog)
4. `game_start_handler` (SGDistributedConnectionDialog)
5. `wrapped_discovery_handler` (SGDistributedSessionManager)

### 2.4 Absence de Session State Centralisé

**Impact** :
- Pas de source de vérité unique
- Pas de versioning pour résoudre les conflits
- Pas de mécanisme de heartbeat centralisé
- Détection de déconnexion du créateur non fiable

### 2.5 Déconnexion du Créateur Non Gérée (CRITIQUE)

**Problème** : Si le créateur de la session quitte, les autres instances restent bloquées dans la session.

**Scénario problématique** :
1. Instance 1 (créateur) crée la session
2. Instance 2 et 3 rejoignent → 3 instances connectées
3. Instance 1 quitte brutalement (fermeture de l'application)
4. Instance 2 et 3 restent dans la session, mais :
   - Le créateur n'est plus là pour démarrer le jeu
   - La session n'est pas fermée automatiquement
   - Les instances ne savent pas qu'elles doivent quitter

**Code actuel** :
- `_cancelConnection()` (ligne 1933) : Publie un message de déconnexion mais ne ferme pas la session
- Pas de mécanisme de heartbeat pour détecter la déconnexion du créateur
- Pas de vérification périodique de l'état du créateur
- Pas de fermeture automatique de la session si créateur déconnecté

**Impact** :
- ❌ Les instances restent bloquées dans une session orpheline
- ❌ Pas de moyen de détecter que le créateur a quitté
- ❌ La session reste "ouverte" indéfiniment
- ❌ Les autres instances ne peuvent pas quitter proprement

---

## 3. Analyse des Plans V1 et V2

### 3.1 Plan V1 : Approche Centralisée (Non Implémentée)

**Concept** :
- Créer `SGDistributedSession` comme source de vérité unique
- Topic `session_state/{session_id}` avec versioning
- Pattern read-modify-write avec retry

**Pourquoi pas de résultats** :
- **Complexité** : Système de versioning et retry difficile à implémenter correctement
- **Migration** : Nécessite refonte complète de l'architecture existante
- **Risque** : Introduction de nouveaux bugs lors de la migration
- **Temps** : Estimation 3-5 jours + tests, mais complexité sous-estimée

**Points positifs** :
- ✅ Architecture conceptuellement solide
- ✅ Source de vérité unique
- ✅ Résout les problèmes à long terme

**Points négatifs** :
- ❌ Complexité élevée
- ❌ Migration risquée
- ❌ Temps de développement long

### 3.2 Plan V2 : Approche Progressive (Plus Pragmatique)

**Concept** :
- 3 solutions complémentaires, par ordre de priorité
- Solution 1 : Désactiver `retain=True` pour états dynamiques
- Solution 2 : Nettoyer explicitement les messages retenus
- Solution 3 : Utiliser session_state comme source unique (si implémenté)

**Avantages** :
- ✅ Solutions progressives et testables
- ✅ Moins de risque (changements ciblés)
- ✅ Résout le problème immédiat rapidement
- ✅ Compatible avec architecture existante

**Inconvénients** :
- ⚠️ Solution 3 nécessite toujours l'implémentation de `SGDistributedSession`
- ⚠️ Solution 1 et 2 sont des correctifs, pas une refonte architecturale

---

## 4. Recommandations pour un Système Fiable

### 4.1 Approche Recommandée : Hybride (V2 Amélioré)

**Stratégie** :
1. **Court terme** : Implémenter Solutions 1 et 2 du Plan V2 (correction immédiate)
2. **Moyen terme** : Implémenter Solution 3 avec `SGDistributedSession` simplifié
3. **Long terme** : Migration progressive vers architecture centralisée complète

### 4.2 Plan d'Action Priorisé

#### Phase 1 : Correction Immédiate (1-2 jours) - PRIORITÉ CRITIQUE

**Objectif** : Éliminer le problème des messages retenus obsolètes

**Actions** :
1. **Solution 2 (Nettoyage explicite)** :
   - Modifier `_cancelConnection()` pour publier messages vides avec `retain=True`
   - Nettoyer `session_instance_ready/{client_id}` et `session_player_registration/{player_name}`
   - Tester avec plusieurs instances qui quittent

2. **Solution 1 (Désactiver retain pour états dynamiques)** :
   - Modifier `registerPlayer()` : `retain=False` pour `session_player_registration`
   - Modifier `_publishInstanceReady()` : `retain=False` pour `session_instance_ready`
   - **IMPORTANT** : S'assurer que les nouveaux abonnés peuvent obtenir l'état via une autre source

**Risques** :
- ⚠️ Les nouveaux abonnés ne recevront plus l'état initial via messages retenus
- ✅ **Mitigation** : Utiliser `session_discovery` pour l'état initial (déjà avec `retain=True`)

#### Phase 2 : Session State Simplifié (2-3 jours) - PRIORITÉ HAUTE

**Objectif** : Implémenter `SGDistributedSession` comme source de vérité, mais version simplifiée

**Actions** :
1. **Créer `SGDistributedSession` simplifié** :
   - Attributs essentiels : `session_id`, `creator_client_id`, `connected_instances`, `state`, `version`, `last_heartbeat`
   - Méthodes : `to_dict()`, `from_dict()`, `add_instance()`, `remove_instance()`, `close()`, `is_expired()`
   - **SANS** versioning complexe initialement (last-write-wins)

2. **Méthodes de base dans `SGDistributedSessionManager`** :
   - `publishSessionState(session)` : Publie avec `retain=True`
   - `readSessionState(session_id, timeout)` : Lit depuis broker
   - `subscribeToSessionState(session_id, callback)` : Abonnement temps réel
   - **SANS** `updateSessionState()` avec retry (pour simplifier)

3. **Intégration dans `SGDistributedConnectionDialog`** :
   - `_initializeSessionState()` : Crée session state lors de création
   - **Unification UX** : Les deux affichages utilisent `session_state.connected_instances` comme source unique
   - `_updateSessionsList()` : Lit `session_state` comme source de vérité (remplace `session_instances_cache`)
   - `_updateConnectedInstances()` : Lit `session_state` comme source de vérité (remplace `ready_instances`)
   - **Heartbeat du créateur** : Timer toutes les 5 secondes pour mettre à jour `last_heartbeat`
   - **Détection de déconnexion du créateur** : Timer toutes les 3 secondes pour vérifier `last_heartbeat`
   - **Fermeture automatique** : Si créateur déconnecté (timeout 15s), fermer la session et faire quitter toutes les instances
   - **Suppression des anciennes sources** : Supprimer `session_instances_cache`, `ready_instances`, `connected_instances_snapshot`

**Avantages** :
- ✅ Source de vérité unique
- ✅ Plus simple que Plan V1 (pas de versioning complexe)
- ✅ Résout le problème à long terme

**Limitations acceptées** :
- ⚠️ Pas de résolution de conflits automatique (last-write-wins)
- ⚠️ Risque de perte de données en cas de mises à jour simultanées
- ✅ Acceptable pour usage typique (peu de conflits simultanés)

#### Phase 3 : Robustesse (1-2 jours) - PRIORITÉ MOYENNE

**Objectif** : Ajouter versioning et gestion d'erreurs

**Actions** :
1. **Ajouter versioning** :
   - Implémenter `updateSessionState()` avec pattern read-modify-write
   - Retry automatique (max 3 tentatives)
   - Gestion des conflits

2. **Améliorer gestion d'erreurs** :
   - Retry sur échec de lecture/écriture MQTT
   - Messages d'erreur utilisateur clairs
   - Fallback si broker inaccessible

3. **Tests de charge** :
   - Tester avec 10+ instances simultanées
   - Tester déconnexions multiples
   - Tester création/fermeture rapide de sessions

---

## 5. Architecture Cible Recommandée

### 5.1 Architecture Hybride (Court Terme)

```
┌─────────────────────────────────────────────────────────────┐
│              Source de Vérité Unique                         │
│         session_state/{session_id} (retain=True)             │
│                                                              │
│  - connected_instances: [client_id1, client_id2]            │
│  - state: 'open' | 'closed'                                  │
│  - version: 1 (simple, sans retry initialement)              │
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
- session_player_registration/{player_name} : Notification uniquement
- session_instance_ready/{client_id} : Notification uniquement
- session_player_disconnect/{client_id} : Notification uniquement

Topics avec retain=True (état statique) :
- session_state/{session_id} : Source de vérité
- session_discovery/{session_id} : Découverte de sessions
```

### 5.2 Migration Progressive

**Étape 1** : Solutions 1 et 2 (correction immédiate)
- ✅ Pas de changement d'architecture
- ✅ Correction du problème actuel
- ✅ Tests rapides

**Étape 2** : Session State simplifié
- ✅ Ajout de `SGDistributedSession` simple
- ✅ Migration progressive de `_updateSessionsList()`
- ✅ Conservation des anciens handlers comme fallback

**Étape 3** : Versioning et robustesse
- ✅ Ajout de versioning si nécessaire
- ✅ Amélioration de la gestion d'erreurs
- ✅ Tests de charge

---

## 6. Points d'Attention Critiques

### 6.1 Compatibilité Ascendante

**Risque** : Les sessions existantes utilisent l'ancien système

**Solution** :
- Phase de transition : Les deux systèmes coexistent
- Détection automatique : Si `session_state/{session_id}` existe, l'utiliser, sinon fallback sur ancien système
- Migration automatique : Créer `session_state` lors de la prochaine connexion

### 6.2 Gestion des Messages Retenus Existants

**Problème** : Les messages retenus obsolètes restent sur le broker

**Solution** :
- Script de nettoyage : Publier messages vides avec `retain=True` sur tous les topics concernés
- Nettoyage automatique : Lors de la connexion, vérifier et nettoyer les messages obsolètes
- Documentation : Expliquer aux utilisateurs comment nettoyer manuellement si nécessaire

### 6.3 Performance et Scalabilité

**Considérations** :
- Polling toutes les 2 secondes : Acceptable pour < 20 sessions
- Subscription temps réel : Meilleure performance que polling
- Cache local : Réduit les lectures MQTT inutiles

**Optimisations futures** :
- Réduire fréquence de polling si subscription fonctionne bien
- Cache avec validation périodique au lieu de polling constant
- Compression des messages si taille devient problématique

---

## 7. Plan d'Implémentation Détaillé

### Phase 1 : Correction Immédiate (1-2 jours)

#### Tâche 1.1 : Nettoyage des messages retenus
**Fichier** : `mainClasses/SGDistributedConnectionDialog.py`
**Méthode** : `_cancelConnection()`
**Action** : Ajouter nettoyage après mise à jour du session state (si existant) ou avant déconnexion

```python
# Nettoyer les messages retenus pour cette instance
if self.config.session_id and self.model.mqttManager.clientId:
    client_id = self.model.mqttManager.clientId
    session_topics = self.session_manager.getSessionTopics(self.config.session_id)
    
    # Nettoyer player_registration
    registration_topic = f"{session_topics[0]}/{assigned_player_name}"
    self.model.mqttManager.client.publish(registration_topic, "", qos=1, retain=True)
    
    # Nettoyer instance_ready
    instance_ready_topic = f"{session_topics[4]}/{client_id}"
    self.model.mqttManager.client.publish(instance_ready_topic, "", qos=1, retain=True)
```

#### Tâche 1.2 : Désactiver retain pour états dynamiques (partiel)
**Fichier 1** : `mainClasses/SGDistributedSessionManager.py`
**Méthode** : `registerPlayer()`
**Ligne** : ~227
**Action** : Changer `retain=True` à `retain=False`
**Note** : `player_registration` n'est plus retenu (nettoyage explicite suffit)

**Fichier 2** : `mainClasses/SGDistributedConnectionDialog.py`
**Méthode** : `_publishInstanceReady()`
**Ligne** : ~1757
**Action** : **GARDER `retain=True`** (nécessaire pour que les nouveaux joiners voient les instances existantes)
**Note** : Le nettoyage explicite dans `_cancelConnection()` empêche les messages obsolètes. Phase 2 remplacera par `session_state`.

#### Tests Phase 1
- [ ] Instance 1 crée session
- [ ] Instance 2 rejoint → doit voir 2 instances
- [ ] Instance 2 quitte → Instance 1 doit voir 1 instance (stable)
- [ ] Instance 3 rejoint → ne doit pas voir Instance 2 dans la liste

### Phase 2 : Session State Simplifié (2-3 jours)

#### Tâche 2.1 : Créer `SGDistributedSession`
**Fichier** : `mainClasses/SGDistributedSession.py` (nouveau)
**Structure** :
```python
class SGDistributedSession:
    session_id: str
    creator_client_id: str
    model_name: str
    state: str  # 'open', 'closed'
    connected_instances: List[str]
    version: int
    last_heartbeat: datetime
    created_at: datetime
    last_updated: datetime
    num_players_min: int
    num_players_max: int
    
    def to_dict() -> dict
    def from_dict(data: dict)
    def add_instance(client_id: str)
    def remove_instance(client_id: str)
    def close()
    def update_heartbeat()
    def is_expired(timeout_seconds: float) -> bool
    def can_accept_more_instances() -> bool
```

#### Tâche 2.2 : Méthodes dans `SGDistributedSessionManager`
**Fichier** : `mainClasses/SGDistributedSessionManager.py`
**Nouvelles méthodes** :
- `publishSessionState(session: SGDistributedSession)`
- `readSessionState(session_id: str, timeout: float) -> SGDistributedSession`
- `subscribeToSessionState(session_id: str, callback: callable)`

#### Tâche 2.3 : Intégration dans `SGDistributedConnectionDialog`
**Fichier** : `mainClasses/SGDistributedConnectionDialog.py`
**Nouvelles méthodes** :
- `_initializeSessionState()` : Crée session state lors de création
- `_subscribeToSessionStateUpdates()` : S'abonne aux mises à jour
- `_startSessionStatePolling()` : Polling périodique (2s)
- `_startSessionStateHeartbeat()` : Heartbeat si créateur (5s) - **CRITIQUE**
- `_startCreatorCheckTimer()` : Vérification créateur (3s, timeout 15s) - **CRITIQUE**

**Modifications UX - Unification des affichages** :
- `_updateSessionsList()` : 
  - Lire `session_state.connected_instances` comme source de vérité unique
  - Remplacer `session_instances_cache` par `session_state`
  - Format : `"{model_name} ({num_instances}/{num_max} instances)"`
- `_updateConnectedInstances()` :
  - Lire `session_state.connected_instances` comme source de vérité unique
  - Remplacer `ready_instances` et `connected_instances_snapshot` par `session_state`
  - Format : `"{num_instances}/{min}-{max} instance(s) connected [✓]"`
- **Suppression des anciennes sources** :
  - Supprimer `session_instances_cache` (remplacé par `session_state`)
  - Supprimer `ready_instances` (remplacé par `session_state.connected_instances`)
  - Supprimer `connected_instances_snapshot` (remplacé par `session_state.connected_instances`)
- **Simplification des handlers** :
  - `_subscribeToInstanceReady()` : Ne plus mettre à jour le cache, juste notifier
  - `_subscribeToPlayerRegistrationForTracking()` : Ne plus mettre à jour le cache, juste notifier

**Modifications gestion déconnexion** :
- `_cancelConnection()` : 
  - Si créateur : Fermer la session (`state='closed'`) avant déconnexion
  - Sinon : Retirer l'instance de `connected_instances`
  - Mettre à jour session state avant déconnexion
- **Gestion déconnexion créateur** :
  - Dans `_checkCreatorDisconnection()` : Si `last_heartbeat` > 15s ET `state == 'open'` :
    - Fermer la session (`state='closed'`)
    - Publier la mise à jour
    - Fermer le dialog pour toutes les instances (via callback ou signal)

#### Tests Phase 2
- [ ] Création de session → session_state créé avec `creator_client_id`
- [ ] Join session → session_state mis à jour
- [ ] Quit session → session_state mis à jour
- [ ] **CRITIQUE** : Déconnexion créateur (fermeture brutale) → session_state fermé automatiquement
- [ ] **CRITIQUE** : Déconnexion créateur → toutes les autres instances quittent la session
- [ ] **CRITIQUE** : Déconnexion créateur → session marquée comme `closed` et retirée de la liste
- [ ] Heartbeat du créateur → `last_heartbeat` mis à jour toutes les 5s
- [ ] Détection déconnexion → timeout 15s détecté correctement
- [ ] **UX** : Liste "Available Sessions" utilise session_state comme source unique
- [ ] **UX** : En bas de la fenêtre utilise session_state comme source unique
- [ ] **UX** : Les deux affichages montrent le même nombre pour la même session (cohérence garantie)
- [ ] **UX** : Pas de désynchronisation entre les deux affichages
- [ ] **UX** : Mise à jour en temps réel (< 3 secondes) pour les deux affichages
- [ ] **UX** : Suppression des anciennes sources (`session_instances_cache`, `ready_instances`, `connected_instances_snapshot`)

### Phase 3 : Robustesse (1-2 jours) - Optionnel

#### Tâche 3.1 : Versioning avec retry
**Fichier** : `mainClasses/SGDistributedSessionManager.py`
**Méthode** : `updateSessionState(session_id: str, updater: callable, max_retries: int = 3)`
**Pattern** : read-modify-write avec vérification de version

#### Tâche 3.2 : Gestion d'erreurs améliorée
- Retry sur échec MQTT
- Messages d'erreur utilisateur
- Fallback si broker inaccessible

#### Tests Phase 3
- [ ] Conflits simultanés → résolution correcte
- [ ] Échecs MQTT → retry automatique
- [ ] 10+ instances simultanées → performance acceptable

---

## 8. Critères de Succès

### Objectifs Mesurables

1. **Synchronisation** :
   - ✅ Toutes les instances voient les changements dans < 3 secondes
   - ✅ Pas de ré-ajout d'instances déconnectées (0% de faux positifs)

2. **Robustesse** :
   - ✅ Détection de déconnexion du créateur < 20 secondes
   - ✅ Gestion correcte des conflits (0% de perte de données)

3. **Performance** :
   - ✅ Support de 10+ instances simultanées
   - ✅ Latence < 3 secondes pour mises à jour

4. **Cohérence UX** :
   - ✅ Les deux affichages montrent le même nombre pour la même session (100% de cohérence)
   - ✅ Pas de désynchronisation visible entre liste et bas de fenêtre
   - ✅ Mise à jour en temps réel (< 3 secondes) pour les deux affichages

### Tests de Validation

**Scénario 1 : Création et Join**
- [ ] Instance 1 crée session → coche ✓ affichée
- [ ] Instance 2 rejoint → Instance 1 voit 2 instances
- [ ] Instance 2 voit coche ✓ sur session jointe

**Scénario 2 : Déconnexion**
- [ ] Instance 2 quitte → Instance 1 voit 1 instance (stable)
- [ ] Instance 2 ne réapparaît pas via messages retenus

**Scénario 3 : Déconnexion créateur (CRITIQUE)**
- [ ] Instance 1 (créateur) quitte brutalement (fermeture application)
- [ ] Instance 2 détecte déconnexion < 20s (via heartbeat timeout)
- [ ] Session fermée automatiquement (`state='closed'`)
- [ ] Instance 2 quitte automatiquement la session (dialog fermé)
- [ ] Instance 3 quitte automatiquement la session (dialog fermé)
- [ ] Session retirée de la liste "Available Sessions"

**Scénario 4 : Cohérence UX des affichages**
- [ ] Instance 2 rejoint session → Liste affiche "2/4 instances", Bas affiche "2/2-4 instances" (même nombre)
- [ ] Instance 3 rejoint → Liste affiche "3/4 instances", Bas affiche "3/2-4 instances" (même nombre)
- [ ] Instance 3 quitte → Liste affiche "2/4 instances", Bas affiche "2/2-4 instances" (même nombre, pas de réminiscence)
- [ ] Les deux affichages se mettent à jour simultanément (< 3 secondes)

**Scénario 5 : Messages retenus**
- [ ] Instance 3 rejoint après déconnexion Instance 2
- [ ] Instance 3 ne voit pas Instance 2 dans la liste

---

## 9. Conclusion et Recommandation Finale

### Recommandation : Approche Hybride (V2 Amélioré)

**Pourquoi** :
1. ✅ **Rapidité** : Phase 1 résout le problème immédiatement (1-2 jours)
2. ✅ **Fiabilité** : Phase 2 ajoute source de vérité unique sans complexité excessive
3. ✅ **Pragmatisme** : Migration progressive, moins de risque
4. ✅ **Maintenabilité** : Architecture plus simple que Plan V1 complet

**Ordre d'implémentation** :
1. **Phase 1** (1-2 jours) : Correction immédiate → Résout problème actuel
2. **Phase 2** (2-3 jours) : Session State simplifié → Architecture fiable
3. **Phase 3** (1-2 jours, optionnel) : Robustesse → Production-ready

**Total estimé** : 4-7 jours de développement + 2 jours de tests

### Points Clés à Retenir

1. **Ne pas réinventer la roue** : Utiliser l'architecture existante comme base
2. **Correction progressive** : Résoudre le problème immédiat, puis améliorer
3. **Tests continus** : Valider chaque phase avant de passer à la suivante
4. **Documentation** : Documenter les changements pour maintenance future

---

## 10. Questions Ouvertes

1. **Compatibilité** : Faut-il maintenir compatibilité avec anciennes sessions ?
2. **Migration** : Script automatique de migration ou manuel ?
3. **Performance** : Nombre maximum d'instances/sessions à supporter ?
4. **Monitoring** : Logs et métriques à ajouter pour diagnostic ?

---

**Fin du Diagnostic**

