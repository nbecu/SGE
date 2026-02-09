# Système BotPlayer (version à jour)

## Objectif

Fournir un système générique permettant :
- d’exécuter des parties automatisées (bots),
- d’entraîner des bots (ML) sans interface,
- de jouer “bot vs humain” avec interface.

## Principe clé

Les actions SGE peuvent être exécutées directement via `perform_with()`, ce qui
permet d’automatiser un joueur sans UI.

```python
action.perform_with(target_entity, serverUpdate=False)
```

## Architecture actuelle

### 1) Adaptateur (spécifique au jeu)

Responsable de :
- représenter l’état du jeu (observation),
- fournir l’espace d’actions (cases/cibles),
- valider les actions possibles,
- déterminer victoire / match nul,
- réinitialiser le plateau.

Exemple :
- `examples/games/TicTacToe_bot_adapter.py`

### 2) Runner (wiring, spécifique au jeu)

Responsable de :
- lancer l’entraînement (headless),
- lancer “bot vs humain” (UI),
- évaluer un modèle sauvegardé.

Exemple :
- `examples/games/TicTacToe_bot_runner.py`

### 3) Cœur ML générique

Responsable de :
- la boucle DQN (replay buffer, target network),
- le builder du modèle Q.

Exemple :
- `mainClasses/bot_ml/bot_trainer.py`

## Flux d’entraînement (headless)

1. Le runner instancie le modèle de jeu (UI désactivée).
2. L’adaptateur fournit observations et actions possibles.
3. Le trainer DQN apprend à partir des transitions.
4. Un modèle `.keras` est sauvegardé.

## Flux “bot vs humain” (UI)

1. Le runner charge un modèle `.keras` (ou fallback aléatoire).
2. Le bot joue via l’adaptateur et `execute_action_with_fallback`.
3. Le joueur humain interagit via l’UI.

## Fallback d’exécution

Le bot tente l’action prévue, puis applique un fallback si nécessaire :

```python
bot.execute_action_with_fallback(action, target)
```

## Évaluation

Deux modes :
- pendant l’entraînement (`eval_games`),
- à partir d’un modèle sauvegardé.

## État actuel (exemple TicTacToe)

- Jeu : `examples/games/TicTacToe.py`
- Adaptateur : `examples/games/TicTacToe_bot_adapter.py`
- Runner : `examples/games/TicTacToe_bot_runner.py`
- DQN générique : `mainClasses/bot_ml/bot_trainer.py`

## Notes

- Cette architecture est réutilisable pour d’autres jeux SGE.
- Un futur chantier pourra intégrer “bot vs humain” directement dans le core SGE.
