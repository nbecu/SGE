# Plan de Test - Phase 2 : Session State comme Source de Vérité Unique

## Objectif
Valider que `session_state` fonctionne correctement comme source de vérité unique pour remplacer les multiples caches (`session_instances_cache`, `ready_instances`, `connected_instances_snapshot`).

## Prérequis
- MQTT broker en cours d'exécution (localhost:1883)
- Fichier de test : `examples/games/Sea_Zones_distributed2.py`

---

## Test 1 : Création de Session → session_state créé

### Étapes
1. Lancer l'instance 1 (créateur)
2. Mode "Create new session"
3. Cliquer sur "Connect"
4. Attendre la synchronisation du seed

### Résultats attendus
- ✅ `session_state` créé avec `creator_client_id = client_id de l'instance 1`
- ✅ `session_state.state = 'open'`
- ✅ `session_state.connected_instances` contient uniquement l'instance 1
- ✅ `session_state.version = 1`
- ✅ Message dans les logs : `"[Dialog] Initialized session state for ..."`
- ✅ Heartbeat timer démarré (logs toutes les 5s)
- ✅ Affichage en bas : "1/4 instance(s) connected"

### Vérifications dans les logs
```
[Dialog] Initialized session state for ... (creator: ...)
[SessionManager] Published session state for ... (version 1, 1 instances)
[Dialog] Started session state heartbeat timer (5s interval)
```

---

## Test 2 : Join Session → session_state mis à jour

### Étapes
1. Lancer l'instance 1 (créateur) - créer session
2. Lancer l'instance 2 (joiner)
3. Mode "Join existing session"
4. Sélectionner la session dans la liste
5. Cliquer sur "Connect"
6. Attendre la synchronisation du seed

### Résultats attendus
- ✅ Instance 2 lit `session_state` existant depuis le broker
- ✅ Instance 2 s'ajoute à `session_state.connected_instances`
- ✅ `session_state.version` incrémenté (1 → 2)
- ✅ Instance 1 reçoit la mise à jour via subscription
- ✅ Instance 2 démarre le timer de vérification du créateur
- ✅ Affichage instance 1 : "2/4 instance(s) connected"
- ✅ Affichage instance 2 : "2/4 instance(s) connected"
- ✅ Liste "Available Sessions" : "2/4 instances" (cohérent)

### Vérifications dans les logs
```
[Dialog] Joined existing session state for ... (2 instances)
[SessionManager] Read session state for ... (version 1, 1 instances)
[SessionManager] Published session state for ... (version 2, 2 instances)
[Dialog] Received session state update for ... (version 2, 2 instances)
[Dialog] Started creator check timer (3s interval, 15s timeout)
```

---

## Test 3 : Quit Session → session_state mis à jour

### Étapes
1. Lancer l'instance 1 (créateur) - créer session
2. Lancer l'instance 2 (joiner) - rejoindre session
3. Attendre que les deux affichent "2/4 instance(s) connected"
4. Instance 2 : Cliquer sur "Cancel" pour quitter

### Résultats attendus
- ✅ Instance 2 retire son `client_id` de `session_state.connected_instances`
- ✅ `session_state.version` incrémenté
- ✅ Instance 1 reçoit la mise à jour
- ✅ Affichage instance 1 : "1/4 instance(s) connected"
- ✅ Liste "Available Sessions" instance 1 : "1/4 instances" (cohérent)
- ✅ Timer de vérification créateur arrêté pour instance 2

### Vérifications dans les logs
```
[Dialog] Removing instance from session state...
[SessionManager] Published session state for ... (version 3, 1 instances)
[Dialog] Received session state update for ... (version 3, 1 instances)
```

---

## Test 4 : Déconnexion Créateur → Session fermée automatiquement

### Étapes
1. Lancer l'instance 1 (créateur) - créer session
2. Lancer l'instance 2 (joiner) - rejoindre session
3. Attendre que les deux affichent "2/4 instance(s) connected"
4. Instance 1 : Fermer brutalement (fermer la fenêtre ou tuer le processus)
5. Attendre 15-20 secondes

### Résultats attendus
- ✅ Après 15s sans heartbeat, instance 2 détecte la déconnexion du créateur
- ✅ `session_state.state` passe à `'closed'`
- ✅ `session_state.version` incrémenté
- ✅ Instance 2 reçoit un message d'avertissement
- ✅ Dialog instance 2 se ferme automatiquement
- ✅ Session retirée de la liste "Available Sessions"

### Vérifications dans les logs
```
[Dialog] Creator disconnected (timeout 15s), closing session...
[SessionManager] Published session state for ... (version X, 2 instances)
[Dialog] Received session state update for ... (version X, state=closed)
```

---

## Test 5 : UX - Cohérence entre les deux affichages

### Étapes
1. Lancer l'instance 1 (créateur) - créer session
2. Lancer l'instance 2 (joiner) - rejoindre session
3. Lancer l'instance 3 (joiner) - rejoindre session
4. Observer les deux affichages :
   - Liste "Available Sessions"
   - Section "Connected Instances" en bas

### Résultats attendus
- ✅ Les deux affichages montrent le même nombre d'instances
- ✅ Pas de désynchronisation entre les deux
- ✅ Mise à jour en temps réel (< 3 secondes) pour les deux
- ✅ Instance 1 : "3/4 instance(s) connected" partout
- ✅ Instance 2 : "3/4 instance(s) connected" partout
- ✅ Instance 3 : "3/4 instance(s) connected" partout

### Vérifications
- Comparer le nombre affiché dans "Available Sessions" avec celui en bas
- Vérifier que les deux se mettent à jour simultanément

---

## Test 6 : Heartbeat du Créateur

### Étapes
1. Lancer l'instance 1 (créateur) - créer session
2. Observer les logs pendant 20-30 secondes

### Résultats attendus
- ✅ Heartbeat publié toutes les 5 secondes
- ✅ `session_state.last_heartbeat` mis à jour
- ✅ `session_state.version` reste stable (heartbeat n'incrémente pas version)

### Vérifications dans les logs
```
[SessionManager] Published session state for ... (version 1, 1 instances)
[SessionManager] Published session state for ... (version 1, 1 instances)
[SessionManager] Published session state for ... (version 1, 1 instances)
```

---

## Test 7 : Détection Déconnexion → Timeout 15s

### Étapes
1. Lancer l'instance 1 (créateur) - créer session
2. Lancer l'instance 2 (joiner) - rejoindre session
3. Instance 1 : Fermer brutalement
4. Observer les logs de l'instance 2

### Résultats attendus
- ✅ Timer de vérification créateur actif (toutes les 3s)
- ✅ Après 15s sans heartbeat, détection de déconnexion
- ✅ Session fermée automatiquement
- ✅ Dialog instance 2 fermé avec message d'avertissement

### Vérifications dans les logs
```
[Dialog] Started creator check timer (3s interval, 15s timeout)
[Dialog] Creator disconnected (timeout 15s), closing session...
```

---

## Points de Vérification Généraux

### Logs à surveiller
- `[Dialog] Initialized session state` : Création de session
- `[SessionManager] Published session state` : Publication d'état
- `[SessionManager] Read session state` : Lecture d'état
- `[Dialog] Received session state update` : Réception de mise à jour
- `[Dialog] Started session state heartbeat timer` : Démarrage heartbeat
- `[Dialog] Started creator check timer` : Démarrage vérification créateur

### Erreurs à éviter
- ❌ `session_state` non créé lors de la création
- ❌ `session_state` non lu lors de la jointure
- ❌ Désynchronisation entre les deux affichages
- ❌ Heartbeat non publié
- ❌ Déconnexion créateur non détectée
- ❌ Session non fermée après déconnexion créateur

---

## Notes de Test

### Ordre recommandé
1. Test 1 (Création)
2. Test 2 (Join)
3. Test 3 (Quit)
4. Test 5 (UX Cohérence)
5. Test 6 (Heartbeat)
6. Test 7 (Détection déconnexion)
7. Test 4 (Déconnexion créateur - test critique)

### Durée estimée
- Tests 1-3 : ~5 minutes
- Test 4 : ~2 minutes (attente 15s)
- Test 5 : ~3 minutes
- Test 6 : ~30 secondes
- Test 7 : ~2 minutes (attente 15s)

**Total : ~15-20 minutes**

