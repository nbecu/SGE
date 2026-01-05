# Plan de développement : Correctif pour empêcher la jonction aux sessions démarrées

## Objectif

Empêcher les nouvelles instances de voir et rejoindre des sessions où le jeu a déjà démarré ("Start Now" ou auto-start). Distinguer sémantiquement une session "démarrée" d'une session "fermée/annulée".

## Problème identifié

Quand "Start Now" est cliqué (ou que le décompte automatique se termine), la `session_state` reste à `state='open'` au lieu de passer à un état indiquant que le jeu a démarré. Les nouvelles instances voient donc la session comme disponible et peuvent la rejoindre.

## Solution proposée

1. Ajouter un nouvel état `'started'` pour les sessions où le jeu a démarré
2. Ajouter des méthodes helper pour encapsuler la logique de vérification d'état
3. Modifier la logique pour marquer la session comme `'started'` lors du démarrage du jeu
4. Mettre à jour tous les filtres pour exclure les sessions `'started'` comme les sessions `'closed'`
---

## Phase 1 : Ajout des méthodes helper dans SGDistributedSession

### Fichier : `mainClasses/distributedGame/SGDistributedSession.py`
1.1 Mise à jour de la docstring de la classe
Modifier la docstring de l'attribut state (ligne 18) pour inclure 'started' :
Avant : state (str): Current state of the session ('open' or 'closed')
Après : state (str): Current state of the session ('open', 'started', or 'closed')
1.2 Ajout des méthodes helper
Ajouter les méthodes suivantes après is_creator() (après la ligne 215) :

```python
def is_open(self) -> bool:
    """Check if session is open (accepting new instances)."""
    return self.state == 'open'

def is_started(self) -> bool:
    """Check if session has started (game is in progress)."""
    return self.state == 'started'

def is_closed(self) -> bool:
    """Check if session is closed (cancelled/abandoned)."""
    return self.state == 'closed'

def is_joinable(self) -> bool:
    """Check if session can accept new instances (open only)."""
    return self.state == 'open'

def is_active(self) -> bool:
    """Check if session is active (open or started, not closed)."""
    return self.state in ('open', 'started')
```
1.3 Modification de add_instance() pour utiliser is_open()
Ligne 119 : Remplacer if self.state != 'open': par if not self.is_open():
1.4 Modification de close() pour utiliser is_closed()
Ligne 152 : Remplacer if self.state != 'closed': par if not self.is_closed():
1.5 Modification de is_expired() pour exclure 'started'
Ligne 178 : Modifier la condition pour retourner False si state == 'started' :
Avant : if self.state == 'closed': return True
Après : if self.is_closed(): return True (les sessions démarrées ne sont pas expirées)
1.6 Modification de can_accept_more_instances() pour utiliser is_open()
Ligne 191 : Remplacer if self.state != 'open': par if not self.is_open():
1.7 Ajout de la méthode start()
Ajouter une nouvelle méthode après close() (après la ligne 155) :

```python
def start(self):
    """
    Mark the session as started (game has begun).
    
    Sets state to 'started' and updates version and timestamp.
    """
    if self.state != 'started':
        self.state = 'started'
        self.version += 1
        self.last_updated = datetime.now()
```
---

## Phase 2 : Mise à jour des filtres de sessions

### Fichier : `mainClasses/distributedGame/SGDistributedConnectionDialog.py`
2.1 Modification de _updateSessionsList()
Ligne 629 : Remplacer if session_state and session_state.state == 'closed': par if session_state and not session_state.is_joinable():
Cela exclut à la fois 'closed' et 'started'
Ligne 740 : Même modification si une autre vérification existe
2.2 Modification de _onConnect()
Ligne 808 : Remplacer if self.session_state.state == 'closed': par if not self.session_state.is_joinable():
2.3 Modification de on_session_state_update()
Ligne 1558 : Remplacer if session.state == 'closed': par if session.is_closed():
Note : Ici, on veut uniquement détecter les sessions fermées (annulées), pas les sessions démarrées
Ligne 1593 : Remplacer if session.state == 'closed': par if not session.is_joinable():
Ici, on veut exclure les sessions non joignables (fermées ou démarrées)
2.4 Modification de check_creator() dans _startCreatorCheckTimer()
Ligne 1685 : Remplacer if self.session_state.state == 'closed': par if not self.session_state.is_active():
On arrête le timer si la session est fermée (pas si elle est démarrée, car le jeu continue)
Ligne 1726 : Remplacer if self.session_state.state == 'closed': par if self.session_state.is_closed():
Double vérification avant de fermer la session
### Fichier : `mainClasses/distributedGame/SGSessionDiscoveryManager.py`
2.5 Modification de session_state_discovery_handler()
Ligne 239 : Remplacer if session.state == 'closed': par if not session.is_joinable():
Exclure les sessions fermées et démarrées de la liste des sessions disponibles
---

## Phase 3 : Implémentation de la logique de démarrage

### Fichier : `mainClasses/distributedGame/SGDistributedConnectionDialog.py`
3.1 Modification de _publishGameStartMessage()
Après la publication du message game_start (après la ligne 1998), ajouter la logique pour marquer la session comme démarrée :

```python
# CRITICAL: Mark session as started (no longer joinable)
if self.session_state and self.config.is_session_creator:
    self.session_state.start()
    self.session_manager.publishSessionState(self.session_state)
```
3.2 Modification de _onStartNowClicked()
Après l'appel à _publishGameStartMessage() (ligne 2271), la session sera automatiquement marquée comme 'started' grâce à la modification de _publishGameStartMessage()
Aucune modification supplémentaire nécessaire
3.3 Modification de _updateCountdown() (auto-start)
Après l'appel à _publishGameStartMessage() dans le cas du décompte automatique (ligne 2661), la session sera automatiquement marquée comme 'started' grâce à la modification de _publishGameStartMessage()
Aucune modification supplémentaire nécessaire
---

## Phase 4 : Mise à jour de la désérialisation

### Fichier : `mainClasses/distributedGame/SGDistributedSession.py`
4.1 Vérification de from_dict()
Ligne 95 : La ligne session.state = data.get('state', 'open') accepte déjà n'importe quelle valeur de state, donc 'started' sera correctement désérialisé
Aucune modification nécessaire, mais ajouter un commentaire pour documenter que 'started' est un état valide
---

## Phase 5 : Tests et validation
5.1 Tests unitaires pour SGDistributedSession
Créer ou mettre à jour les tests pour vérifier :
is_open() retourne True uniquement pour state='open'
is_started() retourne True uniquement pour state='started'
is_closed() retourne True uniquement pour state='closed'
is_joinable() retourne True uniquement pour state='open'
is_active() retourne True pour 'open' et 'started', False pour 'closed'
start() change l'état de 'open' à 'started' et incrémente la version
is_expired() retourne False pour une session 'started' (même sans heartbeat récent)
can_accept_more_instances() retourne False pour une session 'started'
5.2 Tests d'intégration
Scénarios à tester :
Créateur démarre le jeu manuellement ("Start Now")
Vérifier que session_state.state == 'started' après le démarrage
Vérifier que la session n'apparaît plus dans la liste des sessions disponibles pour une nouvelle instance
Créateur démarre le jeu automatiquement (décompte)
Même vérifications que le scénario 1
Nouvelle instance tente de rejoindre une session démarrée
Vérifier que la session n'apparaît pas dans la liste
Vérifier qu'il est impossible de la rejoindre
Session fermée vs session démarrée
Vérifier que les deux sont exclues de la liste des sessions disponibles
Vérifier que is_closed() et is_started() retournent les bonnes valeurs
5.3 Tests de régression
Vérifier que les fonctionnalités existantes continuent de fonctionner :
Création de session
Connexion à une session ouverte
Déconnexion du créateur (session fermée)
Annulation de connexion par le créateur (session fermée)
Heartbeat des sessions ouvertes et démarrées
Phase 6 : Documentation
6.1 Mise à jour des docstrings
Mettre à jour toutes les docstrings qui mentionnent les états de session
Documenter la différence entre 'closed' (annulée) et 'started' (démarrée)
6.2 Commentaires dans le code
Ajouter des commentaires expliquant pourquoi on utilise is_joinable() vs is_closed() dans chaque contexte
Documenter le comportement de is_expired() pour les sessions 'started'
---

## Résumé des modifications

### Fichiers modifiés

1. `mainClasses/distributedGame/SGDistributedSession.py`
Ajout de 5 méthodes helper (is_open(), is_started(), is_closed(), is_joinable(), is_active())
Ajout de la méthode start()
Modification de 4 méthodes existantes pour utiliser les helpers
Mise à jour de la docstring
mainClasses/distributedGame/SGDistributedConnectionDialog.py
Modification de _publishGameStartMessage() pour marquer la session comme 'started'
Modification de 7 vérifications d'état pour utiliser les méthodes helper
mainClasses/distributedGame/SGSessionDiscoveryManager.py
Modification de 1 vérification d'état pour utiliser is_joinable()
### Nombre total de modifications

- **Ajout** : 6 nouvelles méthodes
- **Modification** : 12 endroits où `state` est vérifié
- **Total** : ~18 points de modification

### Risques et précautions
Compatibilité ascendante : les anciennes sessions avec state='open' ou state='closed' continueront de fonctionner
Désérialisation : from_dict() accepte déjà n'importe quelle valeur de state
Filtres : s'assurer que tous les filtres utilisent is_joinable() pour exclure les sessions non joignables
Heartbeat : les sessions 'started' ne doivent pas être considérées comme expirées même sans heartbeat récent
### Ordre d'implémentation recommandé

1. **Phase 1** : Ajouter les méthodes helper (base)
2. **Phase 2** : Mettre à jour les filtres (utiliser les helpers)
3. **Phase 3** : Implémenter la logique de démarrage (marquer comme `'started'`)
4. **Phase 4** : Vérifier la désérialisation (validation)
5. **Phase 5** : Tests (validation complète)
6. **Phase 6** : Documentation (finalisation)

Cet ordre permet de tester chaque phase avant de passer à la suivante.