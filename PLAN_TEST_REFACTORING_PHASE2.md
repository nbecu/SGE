# Plan de Test - Refactoring Phase 2 : SGMQTTHandlerManager

## Objectif
Valider que le refactoring du handler `game_start` avec `SGMQTTHandlerManager` fonctionne correctement et n'introduit pas de régressions.

## Tests à effectuer

### Test 1 : Création de session et démarrage manuel
**Objectif** : Vérifier que le handler `game_start` fonctionne correctement avec le nouveau système.

**Scénario** :
1. Lancer l'instance 1 (créateur) avec `Sea_Zones_distributed2.py`
2. Créer une nouvelle session
3. Se connecter au broker MQTT
4. Attendre la synchronisation du seed
5. Lancer l'instance 2 (joiner)
6. Joindre la session existante
7. Attendre que les deux instances soient connectées (2/4)
8. Sur l'instance 1, cliquer sur "Start Game"

**Résultats attendus** :
- ✅ Les deux instances reçoivent le message `game_start`
- ✅ Les deux dialogs se ferment automatiquement
- ✅ Le jeu démarre correctement sur les deux instances
- ✅ Aucune erreur dans les logs concernant `SGMQTTHandlerManager`

**Points de vérification** :
- Vérifier les logs pour s'assurer qu'il n'y a pas d'erreurs liées au handler
- Vérifier que le message `game_start` est bien reçu et traité
- Vérifier que le cleanup du handler fonctionne correctement

---

### Test 2 : Démarrage automatique (countdown)
**Objectif** : Vérifier que le handler fonctionne aussi avec le démarrage automatique.

**Scénario** :
1. Lancer l'instance 1 (créateur)
2. Créer une nouvelle session
3. Se connecter au broker MQTT
4. Lancer les instances 2, 3 et 4 (joiners)
5. Toutes rejoignent la session
6. Attendre que le countdown démarre automatiquement (4/4 instances)
7. Laisser le countdown se terminer

**Résultats attendus** :
- ✅ Le countdown démarre automatiquement quand 4/4 instances sont connectées
- ✅ Le message `game_start` est publié automatiquement après le countdown
- ✅ Toutes les instances reçoivent le message et ferment leur dialog
- ✅ Le jeu démarre correctement sur toutes les instances

---

### Test 3 : Déconnexion avant démarrage
**Objectif** : Vérifier que le cleanup du handler fonctionne correctement lors d'une déconnexion.

**Scénario** :
1. Lancer l'instance 1 (créateur)
2. Créer une nouvelle session et se connecter
3. Lancer l'instance 2 (joiner) et rejoindre
4. Sur l'instance 1, cliquer sur "Cancel" avant de démarrer le jeu
5. Vérifier que l'instance 2 détecte la fermeture de session

**Résultats attendus** :
- ✅ Le handler `game_start` est correctement retiré lors du cleanup
- ✅ Aucune erreur dans les logs lors de la déconnexion
- ✅ L'instance 2 détecte correctement la fermeture de session
- ✅ Aucun handler orphelin ne reste actif

---

### Test 4 : Vérification des logs
**Objectif** : S'assurer qu'il n'y a pas d'erreurs ou de warnings dans les logs.

**Points à vérifier** :
- ✅ Aucune erreur `[SGMQTTHandlerManager]` dans les logs
- ✅ Aucune erreur liée au handler `game_start`
- ✅ Les messages MQTT sont correctement reçus et traités
- ✅ Le cleanup s'effectue sans erreur

---

## Critères de validation

Le refactoring est considéré comme **validé** si :
1. ✅ Tous les tests ci-dessus passent sans erreur
2. ✅ Le comportement est identique à avant le refactoring
3. ✅ Aucune régression n'est observée
4. ✅ Les logs ne montrent pas d'erreurs liées au nouveau système

## Prochaines étapes après validation

Si les tests sont validés :
- Continuer le refactoring d'autres handlers (seed sync, player registration, etc.)
- Progressivement migrer tous les handlers vers `SGMQTTHandlerManager`

Si des problèmes sont détectés :
- Analyser les logs pour identifier la cause
- Corriger les bugs dans `SGMQTTHandlerManager` ou dans l'utilisation
- Re-tester jusqu'à validation complète

