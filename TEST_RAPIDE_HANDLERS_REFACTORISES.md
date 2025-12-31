# Test Rapide - Handlers MQTT Refactorisés

## Objectif
Valider rapidement que tous les handlers refactorisés fonctionnent correctement avec `SGMQTTHandlerManager`.

## Test Simple (5-10 minutes)

### Scénario Principal
1. **Lancer l'instance 1 (créateur)** avec `Sea_Zones_distributed2.py`
2. Créer une nouvelle session
3. Se connecter au broker MQTT
4. Attendre la synchronisation du seed
5. **Lancer l'instance 2 (joiner)** et rejoindre la session
6. Attendre que les deux instances affichent "2/4 instances connected"
7. Sur l'instance 1, cliquer sur "Start Game"

### Vérifications
- ✅ Les deux dialogs se ferment automatiquement (handler `game_start`)
- ✅ Le jeu démarre correctement sur les deux instances
- ✅ Aucune erreur dans la console Python
- ✅ Les compteurs d'instances sont corrects (handlers `seed_sync`, `player_registration`, `instance_ready`)

### Test Additionnel (optionnel)
- Lancer une 3ème instance en mode "join"
- Vérifier que la liste "Available Sessions" se met à jour correctement (handler `session_player_registrations`)

## Si le test passe
→ Tous les handlers refactorisés fonctionnent correctement ✅

## Si le test échoue
→ Copier les erreurs et on corrige avant de continuer.



