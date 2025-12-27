# Plan de Développement - Gestion Centralisée des Sessions Distribuées

## Date de création
Plan créé pour résoudre les problèmes de synchronisation des instances connectées dans le système de jeu distribué.

## Contexte et Problèmes à Résoudre

### Problèmes identifiés
1. **Problème initial** : Les instances déjà connectées ne voyaient pas les nouvelles instances rejoindre la session
2. **Problème de déconnexion** : Les instances déconnectées n'étaient pas retirées du comptage
3. **Problème de messages retenus** : Les instances déconnectées étaient ré-ajoutées via les messages MQTT retenus

### Fonctionnalité à Maintenir
- **Indicateur visuel (coche ✓)** : La liste "Available Sessions" doit afficher une coche ✓ sur la session à laquelle l'instance est actuellement connectée
- Cette fonctionnalité existe déjà dans le système actuel (lignes 710-712 de `SGDistributedConnectionDialog.py`) et doit être préservée dans le nouveau système

### Solution proposée
Créer un système centralisé de gestion des sessions via une classe `SGDistributedSession` qui circule sur le broker MQTT, servant de source unique de vérité pour l'état de chaque session.

---

## Architecture de la Solution

### Principe Fondamental
- **Une instance `SGDistributedSession` par session** publiée sur le broker MQTT
- **Source unique de vérité** : Toutes les instances consultent et mettent à jour cet objet
- **État explicite** : La session a un état clair (`open`, `closed`, `starting`, etc.)
- **Liste centralisée** : Les instances connectées sont stockées dans l'objet session

### Avantages
- ✅ Simplicité conceptuelle : un objet = une session
- ✅ Cohérence garantie : source unique de vérité
- ✅ Maintenabilité : moins de handlers à coordonner
- ✅ Résout les problèmes de synchronisation identifiés

---

## Structure de la Classe SGDistributedSession

### Fichier
`mainClasses/SGDistributedSession.py`

### Classe
```python
class SGDistributedSession:
    """
    Represents a distributed game session state.
    This object is published on MQTT and serves as the single source of truth
    for session information.
    """
    
    # Core session information
    session_id: str
    creator_client_id: str  # ClientId of the instance that created the session
    model_name: str
    
    # Session state
    state: str  # 'open', 'closed', 'starting', 'in_progress'
    
    # Connected instances
    connected_instances: List[str]  # List of clientIds currently in the session
    
    # Player configuration
    num_players_min: int
    num_players_max: int
    
    # Metadata
    created_at: datetime
    last_updated: datetime
    last_heartbeat: datetime  # Last heartbeat from creator
    
    # Conflict resolution
    version: int  # Incremented on each update to detect conflicts
    
    # Methods
    def to_dict(self) -> dict
    def from_dict(self, data: dict)
    def increment_version(self)
    def add_instance(self, client_id: str)
    def remove_instance(self, client_id: str)
    def is_expired(self, timeout_seconds: float = 15.0) -> bool
    def can_accept_more_instances(self) -> bool
```

### Format JSON publié sur MQTT
```json
{
    "session_id": "abc-123-def",
    "creator_client_id": "client-uuid-1",
    "model_name": "Sea Zones",
    "state": "open",
    "connected_instances": ["client-uuid-1", "client-uuid-2"],
    "num_players_min": 2,
    "num_players_max": 4,
    "created_at": "2024-01-01T12:00:00",
    "last_updated": "2024-01-01T12:05:00",
    "last_heartbeat": "2024-01-01T12:05:00",
    "version": 5
}
```

---

## Protocole MQTT

### Topic Structure
- **Topic de session** : `session_state/{session_id}`
- **Format** : Un topic par session, publié avec `retain=True`
- **QoS** : `qos=1` pour garantir la livraison

### Messages

#### 1. Création de session
**Quand** : Instance crée une nouvelle session  
**Action** :
- Créer instance `SGDistributedSession` avec `state='open'`
- `creator_client_id` = clientId de l'instance créatrice
- `connected_instances` = [creator_client_id]
- `version` = 1
- Publier sur `session_state/{session_id}` avec `retain=True`

#### 2. Join session
**Quand** : Instance rejoint une session existante  
**Action** :
- Lire l'objet session actuel depuis le broker
- Vérifier `state == 'open'` et `can_accept_more_instances()`
- Ajouter son `clientId` à `connected_instances`
- Incrémenter `version`
- Mettre à jour `last_updated`
- Publier la mise à jour (avec `retain=True`)

#### 3. Quit session
**Quand** : Instance quitte une session  
**Action** :
- Lire l'objet session actuel
- Retirer son `clientId` de `connected_instances`
- Incrémenter `version`
- Mettre à jour `last_updated`
- Publier la mise à jour

#### 4. Heartbeat (créateur)
**Quand** : Toutes les 5 secondes (timer)  
**Action** :
- Lire l'objet session actuel
- Mettre à jour `last_heartbeat` = maintenant
- Publier la mise à jour (sans modifier `version` si rien d'autre n'a changé)

#### 5. Fermeture de session
**Quand** : Créateur quitte OU timeout heartbeat  
**Action** :
- Lire l'objet session actuel
- Changer `state` = `'closed'`
- Incrémenter `version`
- Publier la mise à jour
- **Optionnel** : Publier un message `retain=False` pour notification immédiate

---

## Gestion des Conflits

### Problème
Plusieurs instances peuvent tenter de modifier la session simultanément.

### Solution : Versioning
1. **Lire-Modifier-Écrire avec vérification de version** :
   ```python
   # Pseudo-code
   current_session = read_session_from_broker(session_id)
   current_version = current_session.version
   
   # Modifier
   current_session.add_instance(my_client_id)
   current_session.increment_version()
   
   # Publier
   publish_session(current_session)
   
   # Vérifier après un court délai
   updated_session = read_session_from_broker(session_id)
   if updated_session.version != current_version + 1:
       # Conflit détecté, réessayer
       retry_with_updated_session(updated_session)
   ```

2. **Stratégie de retry** :
   - En cas de conflit, relire la session et réappliquer la modification
   - Maximum 3 tentatives
   - Si échec après 3 tentatives, afficher erreur à l'utilisateur

### Alternative : Last-Write-Wins
Si le versioning est trop complexe, utiliser `last_updated` timestamp :
- Accepter la mise à jour avec le timestamp le plus récent
- Simpler mais moins robuste

---

## Gestion de la Déconnexion du Créateur

### Problème
Si le créateur se déconnecte sans fermer la session, les autres instances restent bloquées.

### Solution : Timeout Heartbeat

#### 1. Détection automatique
- Chaque instance (non-créateur) vérifie périodiquement (toutes les 3 secondes) :
  - Si `last_heartbeat` est > 15 secondes → créateur déconnecté
  - Si créateur déconnecté ET `state == 'open'` → transition automatique à `'closed'`

#### 2. Transfert de créateur (optionnel, future amélioration)
- Si créateur déconnecté, la première instance qui détecte devient le nouveau créateur
- Mettre à jour `creator_client_id` et `last_heartbeat`
- Publier la mise à jour

#### 3. Nettoyage des messages retenus
- Quand `state == 'closed'`, publier un message vide (`payload=""`) avec `retain=True`
- Cela efface le message retenu du broker
- **Alternative** : Publier avec `retain=False` et laisser le timeout naturel (15s) nettoyer

---

## Consultation Périodique vs Événementielle

### Approche Hybride (Recommandée)

#### 1. Mise à jour événementielle (prioritaire)
- Quand une instance join/quit → mise à jour immédiate de l'objet session
- Publication immédiate (pas d'attente de polling)
- **Avantage** : Latence minimale

#### 2. Consultation périodique (backup)
- Toutes les 2-3 secondes, chaque instance :
  - Lit l'objet session depuis le broker
  - Compare avec sa copie locale
  - Si différences détectées → mettre à jour l'UI
- **Avantage** : Détecte les incohérences et les messages manqués

#### 3. Subscription MQTT (optimisation)
- S'abonner au topic `session_state/{session_id}` pour recevoir les mises à jour en temps réel
- Combiner avec polling pour robustesse
- **Avantage** : Meilleur des deux mondes

---

## Phases d'Implémentation

### Phase 1 : Infrastructure de Base

#### 1.1 Créer la classe `SGDistributedSession`
**Fichier** : `mainClasses/SGDistributedSession.py`

**Tâches** :
- [ ] Définir la structure de la classe avec tous les attributs
- [ ] Implémenter `to_dict()` et `from_dict()`
- [ ] Implémenter `add_instance()` et `remove_instance()`
- [ ] Implémenter `increment_version()`
- [ ] Implémenter `is_expired()` et `can_accept_more_instances()`
- [ ] Ajouter validation des données

**Tests** :
- [ ] Instanciation avec différents paramètres
- [ ] Sérialisation/désérialisation JSON
- [ ] Ajout/retrait d'instances
- [ ] Vérification des limites (min/max)

#### 1.2 Ajouter méthodes dans `SGDistributedSessionManager`
**Fichier** : `mainClasses/SGDistributedSessionManager.py`

**Nouvelles méthodes** :
- [ ] `publishSessionState(session: SGDistributedSession)` : Publie l'état de session sur MQTT
- [ ] `readSessionState(session_id: str) -> SGDistributedSession` : Lit l'état depuis le broker
- [ ] `updateSessionState(session_id: str, updater: callable) -> bool` : Met à jour avec gestion de conflits
- [ ] `subscribeToSessionState(session_id: str, callback: callable)` : S'abonne aux mises à jour

**Tests** :
- [ ] Publication et lecture depuis le broker
- [ ] Gestion des conflits (versioning)
- [ ] Subscription et réception de mises à jour

---

### Phase 2 : Intégration dans le Flux de Connexion

#### 2.1 Modifier `SGDistributedConnectionDialog._syncSeed()`
**Fichier** : `mainClasses/SGDistributedConnectionDialog.py`

**Modifications** :
- [ ] Après synchronisation du seed, créer ou lire l'objet session
- [ ] Si créateur : créer `SGDistributedSession` avec `state='open'`
- [ ] Si joiner : lire l'objet session existant
- [ ] Ajouter l'instance à `connected_instances`
- [ ] Publier la mise à jour

**Tests** :
- [ ] Création de session par le créateur
- [ ] Join d'une session existante
- [ ] Mise à jour de la liste des instances

#### 2.2 Ajouter consultation périodique
**Fichier** : `mainClasses/SGDistributedConnectionDialog.py`

**Modifications** :
- [ ] Ajouter timer (2-3 secondes) pour consulter l'état de session
- [ ] Comparer avec copie locale
- [ ] Mettre à jour UI si différences détectées
- [ ] Gérer les états `closed` (fermer le dialog)

**Tests** :
- [ ] Détection de nouvelles instances via polling
- [ ] Détection de déconnexions via polling
- [ ] Réaction à l'état `closed`

#### 2.3 Ajouter subscription MQTT
**Fichier** : `mainClasses/SGDistributedConnectionDialog.py`

**Modifications** :
- [ ] S'abonner à `session_state/{session_id}` après connexion
- [ ] Handler pour recevoir les mises à jour en temps réel
- [ ] Mettre à jour UI immédiatement à la réception

**Tests** :
- [ ] Réception immédiate des mises à jour
- [ ] Pas de duplication avec le polling
- [ ] Gestion des messages retenus

---

### Phase 3 : Gestion des Déconnexions

#### 3.1 Heartbeat du créateur
**Fichier** : `mainClasses/SGDistributedConnectionDialog.py`

**Modifications** :
- [ ] Timer heartbeat (5 secondes) si créateur
- [ ] Mettre à jour `last_heartbeat` dans l'objet session
- [ ] Publier la mise à jour

**Tests** :
- [ ] Heartbeat publié régulièrement
- [ ] `last_heartbeat` mis à jour correctement

#### 3.2 Détection de déconnexion du créateur
**Fichier** : `mainClasses/SGDistributedConnectionDialog.py`

**Modifications** :
- [ ] Timer de vérification (3 secondes) pour toutes les instances
- [ ] Vérifier si `last_heartbeat` > 15 secondes
- [ ] Si oui ET `state == 'open'` → transition à `'closed'`
- [ ] Publier la mise à jour

**Tests** :
- [ ] Détection de déconnexion du créateur
- [ ] Transition automatique à `closed`
- [ ] Notification des autres instances

#### 3.3 Gestion du quit
**Fichier** : `mainClasses/SGDistributedConnectionDialog.py`

**Modifications** :
- [ ] Dans `_cleanupBeforeClose()` : retirer l'instance de `connected_instances`
- [ ] Si créateur : changer `state` à `'closed'`
- [ ] Publier la mise à jour
- [ ] Nettoyer les messages retenus si session fermée

**Tests** :
- [ ] Retrait correct lors du quit
- [ ] Fermeture de session si créateur quitte
- [ ] Nettoyage des messages retenus

---

### Phase 4 : Intégration dans la Liste "Available Sessions"

#### 4.1 Modifier `_updateSessionsList()`
**Fichier** : `mainClasses/SGDistributedConnectionDialog.py`

**Modifications** :
- [ ] Lire les objets session depuis le broker (via `session_state/{session_id}`)
- [ ] Utiliser `connected_instances` pour afficher le nombre d'instances
- [ ] Utiliser `state` pour afficher l'état de la session
- [ ] Filtrer les sessions `closed` ou expirées
- [ ] **CRITICAL** : Maintenir l'indicateur visuel (coche ✓) pour la session connectée
  - Vérifier si `self.config.session_id == session_id` ET instance connectée
  - Afficher `{model_name} ✓ ({instances_text})` pour la session connectée
  - Afficher `{model_name} ({instances_text})` pour les autres sessions
  - Appliquer un style visuel distinct (ex: fond bleu) pour la session connectée

**Tests** :
- [ ] Affichage correct du nombre d'instances
- [ ] Mise à jour en temps réel
- [ ] Filtrage des sessions fermées
- [ ] **CRITICAL** : Coche ✓ affichée uniquement pour la session à laquelle l'instance est connectée
- [ ] Coche ✓ mise à jour correctement lors des changements de session
- [ ] Style visuel distinct pour la session connectée

#### 4.2 Synchronisation avec l'objet session
**Fichier** : `mainClasses/SGDistributedConnectionDialog.py`

**Modifications** :
- [ ] Supprimer les anciens mécanismes de tracking (`session_instances_cache`, etc.)
- [ ] Utiliser uniquement l'objet session comme source de vérité
- [ ] Simplifier le code en supprimant les handlers redondants

**Tests** :
- [ ] Cohérence entre l'objet session et l'affichage
- [ ] Pas de régression dans les fonctionnalités

---

### Phase 5 : Robustesse et Optimisations

#### 5.1 Gestion des erreurs
**Tâches** :
- [ ] Gestion des erreurs de lecture/écriture MQTT
- [ ] Retry automatique en cas d'échec
- [ ] Messages d'erreur utilisateur clairs
- [ ] Fallback si broker inaccessible

#### 5.2 Performance
**Tâches** :
- [ ] Optimiser la fréquence de polling (2-3s semble optimal)
- [ ] Réduire la taille des messages (compression si nécessaire)
- [ ] Cache local pour éviter les lectures inutiles

#### 5.3 Tests de charge
**Tâches** :
- [ ] Tester avec 10+ instances simultanées
- [ ] Tester les déconnexions multiples
- [ ] Tester la création/fermeture rapide de sessions

---

## Migration depuis l'Ancien Système

### Étapes de Migration

1. **Phase de transition** :
   - Implémenter le nouveau système en parallèle de l'ancien
   - Les deux systèmes coexistent temporairement
   - Le nouveau système prend le relais progressivement

2. **Dépréciation** :
   - Marquer les anciennes méthodes comme `@deprecated`
   - Ajouter des warnings dans les logs
   - Documenter la migration

3. **Nettoyage** :
   - Supprimer les anciens handlers (`seed_tracking_wrapper`, etc.)
   - Supprimer les anciens caches (`session_instances_cache`, etc.)
   - Simplifier le code

### Compatibilité
- **Backward compatibility** : Non requise (nouveau système)
- **Migration des sessions existantes** : Les sessions en cours utilisent l'ancien système jusqu'à fermeture

---

## Tests à Effectuer

### Tests Unitaires

1. **SGDistributedSession** :
   - [ ] Création avec différents paramètres
   - [ ] Sérialisation/désérialisation
   - [ ] Ajout/retrait d'instances
   - [ ] Vérification des limites
   - [ ] Détection d'expiration

2. **SGDistributedSessionManager** :
   - [ ] Publication et lecture depuis MQTT
   - [ ] Gestion des conflits (versioning)
   - [ ] Subscription et callbacks

### Tests d'Intégration

1. **Scénario 1 : Création et Join**
   - [ ] Instance 1 crée une session
   - [ ] Instance 1 doit voir la coche ✓ sur sa session dans la liste
   - [ ] Instance 2 rejoint → doit voir 2 instances
   - [ ] Instance 2 doit voir la coche ✓ sur la session jointe
   - [ ] Instance 3 rejoint → Instance 2 doit voir 3 instances
   - [ ] Instance 3 doit voir la coche ✓ sur la session jointe

2. **Scénario 2 : Déconnexion**
   - [ ] Instance 3 se déconnecte
   - [ ] Instance 2 doit voir 2 instances (pas 3)
   - [ ] Instance 3 ne doit pas être ré-ajoutée via messages retenus

3. **Scénario 3 : Déconnexion du créateur**
   - [ ] Instance 1 (créateur) se déconnecte
   - [ ] Instance 2 doit détecter la déconnexion (> 15s)
   - [ ] Session doit passer à `closed`
   - [ ] Instance 2 doit quitter la session

4. **Scénario 4 : Messages retenus**
   - [ ] Instance 3 se connecte après déconnexion d'Instance 2
   - [ ] Instance 3 ne doit pas voir Instance 2 dans la liste
   - [ ] Messages retenus d'Instance 2 doivent être ignorés

5. **Scénario 5 : Conflits simultanés**
   - [ ] Instance 2 et Instance 3 rejoignent simultanément
   - [ ] Les deux doivent être ajoutées correctement
   - [ ] Pas de perte de données

### Tests de Régression

- [ ] Vérifier que les fonctionnalités existantes fonctionnent toujours
- [ ] Vérifier que `enableDistributedGame()` fonctionne
- [ ] Vérifier que `completeDistributedGameSetup()` fonctionne
- [ ] Vérifier que la sélection de joueur fonctionne

---

## Points d'Attention

### 1. Messages MQTT Retenus
- **Problème** : Les messages retenus peuvent contenir des données obsolètes
- **Solution** : Toujours vérifier `last_updated` et `state` avant d'utiliser les données
- **Nettoyage** : Publier message vide avec `retain=True` quand session fermée

### 2. Conflits de Version
- **Problème** : Plusieurs instances modifient simultanément
- **Solution** : Versioning avec retry automatique
- **Limite** : Maximum 3 tentatives avant erreur utilisateur

### 3. Latence
- **Problème** : Polling peut introduire de la latence
- **Solution** : Combiner avec subscription MQTT pour temps réel
- **Compromis** : Polling comme backup si subscription échoue

### 4. Performance
- **Problème** : Trop de polling = charge réseau
- **Solution** : Fréquence optimale (2-3 secondes)
- **Optimisation** : Cache local avec validation périodique

### 5. Fiabilité
- **Problème** : Broker MQTT peut être inaccessible
- **Solution** : Gestion d'erreurs avec retry et fallback
- **UX** : Messages d'erreur clairs pour l'utilisateur

---

## Métriques de Succès

### Objectifs
- ✅ **Synchronisation en temps réel** : Toutes les instances voient les changements dans < 3 secondes
- ✅ **Pas de ré-ajout d'instances déconnectées** : 0% de faux positifs
- ✅ **Détection de déconnexion** : < 20 secondes pour détecter créateur déconnecté
- ✅ **Robustesse** : Gestion correcte des conflits (0% de perte de données)

### Critères d'Acceptation
1. Instance 2 voit Instance 3 rejoindre dans < 3 secondes
2. Instance 2 voit Instance 3 quitter dans < 3 secondes
3. Instance 3 déconnectée n'est jamais ré-ajoutée
4. Créateur déconnecté est détecté et session fermée automatiquement
5. Pas de perte de données lors de conflits simultanés

---

## Documentation à Mettre à Jour

### Fichiers à Modifier
1. **README_developer.md** :
   - [ ] Documenter la nouvelle architecture `SGDistributedSession`
   - [ ] Expliquer le protocole MQTT
   - [ ] Documenter la gestion des conflits

2. **CONTEXT_SGE_FOR_CHATBOT.md** :
   - [ ] Ajouter section sur `SGDistributedSession`
   - [ ] Documenter les nouveaux topics MQTT
   - [ ] Expliquer la migration depuis l'ancien système

3. **DISTRIBUTED_GAME_SPECIFICATION_V2.md** :
   - [ ] Mettre à jour avec la nouvelle architecture
   - [ ] Documenter les changements de protocole
   - [ ] Ajouter exemples d'utilisation

---

## Ordre d'Implémentation Recommandé

1. **Phase 1** : Infrastructure de base (classe + méthodes de base)
2. **Phase 2** : Intégration dans le flux de connexion (création/join)
3. **Phase 3** : Gestion des déconnexions (heartbeat + détection)
4. **Phase 4** : Intégration dans la liste "Available Sessions"
5. **Phase 5** : Robustesse et optimisations

**Durée estimée** : 3-5 jours de développement + 2 jours de tests

---

## Conclusion

Ce plan détaille l'implémentation d'un système centralisé de gestion des sessions distribuées via `SGDistributedSession`. Cette approche résout les problèmes de synchronisation identifiés en fournissant une source unique de vérité pour l'état de chaque session.

**Avantages principaux** :
- Simplicité conceptuelle
- Cohérence garantie
- Maintenabilité améliorée
- Résolution des problèmes de synchronisation

**Risques identifiés** :
- Gestion des conflits (résolu via versioning)
- Messages retenus (résolu via vérification d'état)
- Latence (résolu via approche hybride)

Le système proposé est robuste et fournit une base solide pour le système distribué.

