# Recommandation UX : Affichage du Nombre d'Instances Connectées

## Date
Recommandation pour l'approche UX d'affichage des instances dans l'interface "Connect to Distributed Game".

---

## 1. Principe Fondamental

### Source de Vérité Unique
**Règle absolue** : Les deux affichages doivent utiliser la **même source de vérité** (`session_state.connected_instances`) pour garantir la cohérence.

### Rôles Distincts des Affichages
Les deux affichages ont des **rôles différents** dans le workflow utilisateur, mais doivent afficher la **même information** pour la même session.

---

## 2. Approche Recommandée : Unification avec Différenciation Contextuelle

### 2.1 Architecture Technique

**Source de vérité unique** : `session_state.connected_instances`
- Les deux affichages lisent depuis `session_state` (Phase 2)
- Plus de désynchronisation possible
- Cohérence garantie

### 2.2 Rôles UX des Affichages

#### Affichage 1 : Liste "Available Sessions" (Haut)
**Rôle** : **Navigation et sélection**
- **Objectif** : Permettre à l'utilisateur de **choisir** une session à rejoindre
- **Public** : Utilisateur qui cherche une session
- **Contexte** : Mode "Join existing session", avant connexion
- **Information affichée** : État de **toutes** les sessions disponibles
- **Format** : `{model_name} ({num_instances}/{num_max} instances)`

**Comportement** :
- Affiche toutes les sessions découvertes
- Montre le nombre d'instances connectées pour chaque session
- Permet la sélection d'une session
- Affiche une coche ✓ pour la session à laquelle l'instance est connectée

#### Affichage 2 : En Bas de la Fenêtre (Section "Connected Instances")
**Rôle** : **Monitoring et attente**
- **Objectif** : Informer l'utilisateur sur l'état de la session à laquelle il est **connecté**
- **Public** : Utilisateur qui attend que la session soit prête
- **Contexte** : Après connexion à une session, pendant l'attente
- **Information affichée** : État de la session **connectée uniquement**
- **Format** : `{num_instances}/{min}-{max} instance(s) connected [✓]`

**Comportement** :
- Affiche seulement pour la session connectée
- Montre le nombre d'instances connectées
- Indique si le minimum/maximum est atteint
- Change de couleur selon l'état (attente/minimum/maximum)

### 2.3 Différence Sémantique (Clarifiée)

**Les deux affichages montrent la même information** (nombre d'instances connectées), mais dans des **contextes différents** :

| Aspect | Liste "Available Sessions" | En Bas de la Fenêtre |
|--------|---------------------------|----------------------|
| **Portée** | Toutes les sessions | Session connectée uniquement |
| **Rôle** | Navigation/Sélection | Monitoring/Attente |
| **Contexte** | Avant connexion | Après connexion |
| **Information** | Même source : `session_state.connected_instances` | Même source : `session_state.connected_instances` |

**Pas de différence sémantique** : Les deux affichages montrent le même nombre pour la même session.

---

## 3. Implémentation Technique

### 3.1 Phase 2 : Unification avec session_state

**Modifications dans `_updateSessionsList()`** :
```python
def _updateSessionsList(self):
    # ...
    for session_id, session_data in sorted_sessions:
        # TOUJOURS lire le session state (source de vérité)
        session_state = self.session_manager.readSessionState(session_id, timeout=0.5)
        
        if session_state is None:
            # Session state non disponible - utiliser découverte comme fallback
            num_instances = 0
        else:
            # Utiliser session state comme source de vérité
            num_instances = len(session_state.connected_instances)
            
            if session_state.state == 'closed' or session_state.is_expired():
                continue
```

**Modifications dans `_updateConnectedInstances()`** :
```python
def _updateConnectedInstances(self):
    # ...
    if not self.config.session_id:
        return
    
    # TOUJOURS lire le session state (source de vérité)
    session_state = self.session_manager.readSessionState(self.config.session_id, timeout=0.5)
    
    if session_state is None:
        num_instances = 0
    else:
        # Utiliser session state comme source de vérité
        num_instances = len(session_state.connected_instances)
```

**Résultat** : Les deux affichages utilisent `session_state.connected_instances` → cohérence garantie.

### 3.2 Suppression des Anciennes Sources

**À supprimer** :
- `session_instances_cache` : Remplacé par `session_state`
- `ready_instances` : Remplacé par `session_state.connected_instances`
- `connected_instances_snapshot` : Remplacé par `session_state.connected_instances`

**Handlers à simplifier** :
- `_subscribeToInstanceReady()` : Ne plus mettre à jour le cache, juste notifier
- `_subscribeToPlayerRegistrationForTracking()` : Ne plus mettre à jour le cache, juste notifier

---

## 4. Avantages de cette Approche

### 4.1 Cohérence Technique
- ✅ Source de vérité unique (`session_state`)
- ✅ Plus de désynchronisation possible
- ✅ Architecture simplifiée

### 4.2 Clarté UX
- ✅ Les deux affichages montrent la même information pour la même session
- ✅ Pas de confusion possible
- ✅ Rôles clairs (navigation vs monitoring)

### 4.3 Maintenabilité
- ✅ Code plus simple (une seule source)
- ✅ Moins de handlers à maintenir
- ✅ Moins de bugs possibles

---

## 5. Workflow Utilisateur

### Scénario : Rejoindre une Session

1. **Mode "Join existing session"** sélectionné
2. **Liste "Available Sessions"** affiche :
   - `"Sea Zones (2/4 instances)"`
   - `"Other Game (1/2 instances)"`
3. Utilisateur clique sur "Sea Zones" → session sélectionnée
4. Utilisateur clique sur "Connect" → connexion à la session
5. **En bas de la fenêtre** affiche :
   - `"2/2-4 instance(s) connected ✓ (min)"`
6. Instance 3 rejoint → Les deux affichages se mettent à jour :
   - Liste : `"Sea Zones (3/4 instances)"`
   - Bas : `"3/2-4 instance(s) connected"`
7. Instance 4 rejoint → Les deux affichages se mettent à jour :
   - Liste : `"Sea Zones (4/4 instances) (Full)"`
   - Bas : `"4/2-4 instance(s) connected ✓"`

**Cohérence** : Les deux affichages montrent toujours le même nombre pour la même session.

---

## 6. Cas Particuliers

### 6.1 Session Non Connectée (dans la Liste)
- Affiche le nombre d'instances depuis `session_state`
- Permet de voir l'état avant de rejoindre

### 6.2 Session Connectée (dans la Liste ET en bas)
- Les deux affichages montrent le même nombre
- La liste affiche une coche ✓ pour indiquer la connexion
- Le bas affiche des détails supplémentaires (état min/max)

### 6.3 Session Fermée
- Filtrée de la liste (ne s'affiche pas)
- Si connectée, le dialog se ferme automatiquement

---

## 7. Labels et Messages

### 7.1 Liste "Available Sessions"
**Format** : `{model_name} ({num_instances}/{num_max} instances)`
- Simple et clair
- Pas besoin de préciser "connected" (implicite)

### 7.2 En Bas de la Fenêtre
**Format** : `{num_instances}/{min}-{max} instance(s) connected [✓]`
- Plus détaillé (montre min/max)
- Indique l'état (attente/minimum/maximum)
- Couleur change selon l'état

**Tooltip** (optionnel) :
- "Number of instances currently connected to this session"
- "Session will start automatically when maximum is reached"

---

## 8. Validation

### Critères de Succès
1. ✅ Les deux affichages montrent le même nombre pour la même session
2. ✅ Pas de désynchronisation visible
3. ✅ Mise à jour en temps réel (< 3 secondes)
4. ✅ Rôles clairs (navigation vs monitoring)

### Tests à Effectuer
- [ ] Instance rejoint → Les deux affichages se mettent à jour avec le même nombre
- [ ] Instance quitte → Les deux affichages se mettent à jour avec le même nombre
- [ ] Pas de réminiscence (les nombres restent cohérents)
- [ ] Mise à jour en temps réel (< 3 secondes)

---

## 9. Conclusion

### Recommandation Finale

**Approche** : **Unification avec session_state + Rôles UX distincts**

**Principe** :
- Source de vérité unique : `session_state.connected_instances`
- Rôles différents : Navigation (liste) vs Monitoring (bas)
- Même information : Les deux affichages montrent le même nombre pour la même session

**Avantages** :
- ✅ Cohérence technique garantie
- ✅ Clarté UX (pas de confusion)
- ✅ Architecture simplifiée
- ✅ Aligné avec Phase 2 du diagnostic

**Implémentation** :
- Phase 2 du diagnostic : Implémenter `session_state` comme source de vérité unique
- Modifier `_updateSessionsList()` et `_updateConnectedInstances()` pour utiliser `session_state`
- Supprimer les anciennes sources (`session_instances_cache`, `ready_instances`)

---

**Fin de la Recommandation UX**

