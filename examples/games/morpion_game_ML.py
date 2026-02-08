import sys
from pathlib import Path
import random
import itertools
import string
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
from mainClasses.SGBotPlayer import SGBotGameAdapter, SGBotPlayer


# ============================================================================
# Model factory
# ============================================================================
def build_morpion_model(ui_enabled=True, with_control_panels=True):
    myModel = SGModel(600, 600, windowTitle="Jeu du Morpion (ML)")

    # Grid
    Cell = myModel.newCellsOnGrid(3, 3, "square", size=100, gap=5)
    Cell.setEntities("state", "empty")

    # POV
    Cell.newPov("Morpion", "state", {
        "empty": QtGui.QColor("white"),
        "X": QtGui.QColor("blue"),
        "O": QtGui.QColor("red")
    })

    # Players
    Player1 = myModel.newPlayer("Joueur 1")
    Player2 = myModel.newPlayer("Joueur 2")

    # Actions (only on empty cells)
    empty_condition = [lambda cell: cell.value("state") == "empty"]
    Player1.addGameAction(myModel.newModifyAction(Cell, {"state": "X"}, 1, conditions=empty_condition))
    Player2.addGameAction(myModel.newModifyAction(Cell, {"state": "O"}, 1, conditions=empty_condition))

    if with_control_panels and ui_enabled:
        Player1.newControlPanel("Joueur 1")
        Player2.newControlPanel("Joueur 2")

    # Phases
    myModel.newPlayPhase("Tour de Joueur 1", [Player1], autoForwardWhenAllActionsUsed=True, message_auto_forward=False)
    myModel.newPlayPhase("Tour de Joueur 2", [Player2], autoForwardWhenAllActionsUsed=True, message_auto_forward=False)

    if ui_enabled:
        myModel.newUserSelector()
    myModel.setCurrentPlayer('Admin')

    # End game rule
    endGameRule = myModel.newEndGameRule()

    def check_victory():
        for i in range(1, 4):
            if Cell.getCell(i, 1).value("state") == Cell.getCell(i, 2).value("state") == Cell.getCell(i, 3).value("state") != "empty":
                return True
            if Cell.getCell(1, i).value("state") == Cell.getCell(2, i).value("state") == Cell.getCell(3, i).value("state") != "empty":
                return True
        if Cell.getCell(1, 1).value("state") == Cell.getCell(2, 2).value("state") == Cell.getCell(3, 3).value("state") != "empty":
            return True
        if Cell.getCell(1, 3).value("state") == Cell.getCell(2, 2).value("state") == Cell.getCell(3, 1).value("state") != "empty":
            return True
        return False

    def check_draw():
        if check_victory():
            return False
        for i in range(1, 4):
            for j in range(1, 4):
                if Cell.getCell(i, j).value("state") == "empty":
                    return False
        return True

    endGameRule.addEndGameCondition_onLambda(lambda: check_victory(), name="Victoire")
    endGameRule.addEndGameCondition_onLambda(lambda: check_draw(), name="Match nul")

    if ui_enabled:
        time_label = myModel.newTimeLabel()
        time_label.moveToCoords(390, 300)

    return myModel, Cell, Player1, Player2, check_victory


# ============================================================================
# Adapter
# ============================================================================
class MorpionAdapter(SGBotGameAdapter):
    def __init__(self, model, cell_def, player_mark_map):
        super().__init__(model)
        self.cell_def = cell_def
        self.player_mark_map = player_mark_map

    def _iter_cells(self):
        for y in range(1, 4):
            for x in range(1, 4):
                yield self.cell_def.getCell(x, y)

    def get_observation(self, player):
        mark = self.player_mark_map[player.name]
        values = []
        for cell in self._iter_cells():
            state = cell.value("state")
            if state == "empty":
                values.append(0)
            elif state == mark:
                values.append(1)
            else:
                values.append(-1)
        return np.array(values, dtype=np.float32)

    def get_valid_targets(self, action, player):
        return [cell for cell in self._iter_cells() if cell.value("state") == "empty"]

    def get_action_space(self):
        return list(self._iter_cells())

    def get_valid_action_indices(self):
        indices = []
        for idx, cell in enumerate(self.get_action_space()):
            if cell.value("state") == "empty":
                indices.append(idx)
        return indices

    def choose_action_with_policy(self, player, policy_model, epsilon=0.1, rng=None):
        rng = rng or random.Random()
        action = player.gameActions[0]
        valid_indices = self.get_valid_action_indices()
        if not valid_indices:
            return None, None

        if rng.random() < epsilon:
            idx = rng.choice(valid_indices)
        else:
            obs = self.get_observation(player).reshape(1, -1)
            q_values = policy_model.predict(obs, verbose=0)[0]
            # Mask invalid moves
            masked = [(i, q_values[i]) for i in valid_indices]
            idx = max(masked, key=lambda t: t[1])[0]

        target = self.get_action_space()[idx]
        return action, target

    def check_victory(self):
        cells = list(self._iter_cells())
        grid = [cells[i].value("state") for i in range(9)]
        lines = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        for a, b, c in lines:
            if grid[a] == grid[b] == grid[c] and grid[a] != "empty":
                return grid[a]
        return None

    def is_draw(self):
        return all(cell.value("state") != "empty" for cell in self._iter_cells())

    def reset_board(self):
        for cell in self._iter_cells():
            cell.setValue("state", "empty")


# ============================================================================
# Training (TensorFlow/Keras)
# ============================================================================
def build_policy_model():
    try:
        import tensorflow as tf
        from tensorflow import keras
    except Exception as exc:
        raise ImportError("TensorFlow/Keras is required for training.") from exc

    model = keras.Sequential([
        keras.layers.Input(shape=(9,)),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(9, activation="linear"),
    ])
    model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001), loss="mse")
    return model


def _iter_suffixes():
    letters = string.ascii_lowercase
    for size in range(1, 3):
        for comb in itertools.product(letters, repeat=size):
            yield "".join(comb)


def _get_auto_model_path(models_dir, game_name, episodes):
    for suffix in _iter_suffixes():
        candidate = models_dir / f"{game_name}_ep{episodes}_{suffix}.keras"
        if not candidate.exists():
            return candidate
    raise RuntimeError("No available suffix for model file name.")


def train_morpion_bot(episodes=500, epsilon=1.0, epsilon_min=0.1, epsilon_decay=0.995, gamma=0.9, seed=42, output_path=None, game_name="morpion", self_play=True, step_penalty=0.02):
    random.seed(seed)
    np.random.seed(seed)

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    model, Cell, Player1, Player2, _ = build_morpion_model(ui_enabled=False, with_control_panels=False)

    adapter = MorpionAdapter(model, Cell, {Player1.name: "X", Player2.name: "O"})
    policy_model = build_policy_model()

    def reset_game():
        adapter.reset_board()
        for action in model.getAllGameActions():
            action.reset()
        model.timeManager.currentRoundNumber = 0
        model.timeManager.currentPhaseNumber = 0
        model.setCurrentPlayer(Player1.name)
        model.timeManager.nextPhase()

    def select_action(player):
        obs = adapter.get_observation(player)
        valid_indices = adapter.get_valid_action_indices()
        if not valid_indices:
            return None, None, None
        if random.random() < epsilon:
            action_idx = random.choice(valid_indices)
        else:
            q_values = policy_model.predict(obs.reshape(1, -1), verbose=0)[0]
            masked = [(i, q_values[i]) for i in valid_indices]
            action_idx = max(masked, key=lambda t: t[1])[0]
        target_cell = adapter.get_action_space()[action_idx]
        return obs, action_idx, target_cell

    for _ in range(episodes):
        reset_game()
        done = False
        while not done:
            current_player = model.getCurrentPlayer()
            if current_player is None:
                break

            obs, action_idx, target_cell = select_action(current_player)
            if target_cell is None:
                break
            action = current_player.gameActions[0]
            action.perform_with(target_cell, serverUpdate=False)

            winner = adapter.check_victory()
            if winner:
                reward = 1.0 if winner == adapter.player_mark_map[current_player.name] else -1.0
                done = True
            elif adapter.is_draw():
                reward = 0.2
                done = True
            else:
                reward = -float(step_penalty)

            if done:
                target_q = policy_model.predict(obs.reshape(1, -1), verbose=0)[0]
                target_q[action_idx] = reward
                policy_model.fit(obs.reshape(1, -1), target_q.reshape(1, -1), verbose=0)
                continue

            # Opponent move (self-play or random)
            opponent = model.getCurrentPlayer()
            if opponent is None:
                break

            if self_play:
                obs_op, action_idx_op, target_cell_op = select_action(opponent)
                if target_cell_op is None:
                    break
                opponent_action = opponent.gameActions[0]
                opponent_action.perform_with(target_cell_op, serverUpdate=False)
            else:
                targets = adapter.get_valid_targets(Player2.gameActions[0], Player2)
                if not targets:
                    break
                Player2.gameActions[0].perform_with(random.choice(targets), serverUpdate=False)
                obs_op = None
                action_idx_op = None

            winner = adapter.check_victory()
            if winner:
                reward_op = 1.0 if opponent and winner == adapter.player_mark_map[opponent.name] else -1.0
                reward_cur = 1.0 if winner == adapter.player_mark_map[current_player.name] else -1.0
                done = True
            elif adapter.is_draw():
                reward_op = 0.2
                reward_cur = 0.2
                done = True
            else:
                reward_op = -float(step_penalty)
                reward_cur = -float(step_penalty)

            # Update opponent (self-play only)
            if self_play and obs_op is not None and action_idx_op is not None:
                target_q_op = policy_model.predict(obs_op.reshape(1, -1), verbose=0)[0]
                if done:
                    target_q_op[action_idx_op] = reward_op
                else:
                    next_obs_op = adapter.get_observation(opponent)
                    next_q_op = policy_model.predict(next_obs_op.reshape(1, -1), verbose=0)[0]
                    target_q_op[action_idx_op] = reward_op + gamma * float(np.max(next_q_op))
                policy_model.fit(obs_op.reshape(1, -1), target_q_op.reshape(1, -1), verbose=0)

            # Update current player using state after opponent move
            next_obs = adapter.get_observation(current_player)
            target_q = policy_model.predict(obs.reshape(1, -1), verbose=0)[0]
            if done:
                target_q[action_idx] = reward_cur
            else:
                next_q = policy_model.predict(next_obs.reshape(1, -1), verbose=0)[0]
                target_q[action_idx] = reward_cur + gamma * float(np.max(next_q))
            policy_model.fit(obs.reshape(1, -1), target_q.reshape(1, -1), verbose=0)

        epsilon = max(epsilon_min, epsilon * epsilon_decay)

    models_dir = Path(__file__).parent / "trained_bots"
    models_dir.mkdir(parents=True, exist_ok=True)
    if output_path:
        model_path = Path(output_path)
        if not model_path.is_absolute():
            model_path = models_dir / model_path
    else:
        model_path = _get_auto_model_path(models_dir, game_name, episodes)
    policy_model.save(model_path)
    return model_path


# ============================================================================
# UI: Bot vs Human
# ============================================================================
def run_bot_vs_human(model_path=None, bot_player="O"):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    model, Cell, Player1, Player2, _ = build_morpion_model(ui_enabled=True, with_control_panels=True)
    adapter = MorpionAdapter(model, Cell, {Player1.name: "X", Player2.name: "O"})

    policy_model = None
    if model_path:
        try:
            model_path = Path(model_path)
            if not model_path.is_absolute():
                model_path = Path(__file__).parent / model_path
            from tensorflow import keras
            policy_model = keras.models.load_model(str(model_path))
        except Exception:
            policy_model = None

    bot_name = Player2.name if bot_player.upper() == "O" else Player1.name
    strategy = "policy" if policy_model is not None else "random"
    bot = model.enableBotPlayer(bot_name, adapter, strategy=strategy, policy_model=policy_model, epsilon=0.0)

    def bot_tick():
        current_player = model.getCurrentPlayer()
        if current_player and current_player.name == bot_name:
            bot.execute_turn()
        QtCore.QTimer.singleShot(200, bot_tick)

    # Start with X by default
    # model.setCurrentPlayer(Player1.name)
    model.launch()
    QtCore.QTimer.singleShot(200, bot_tick)
    sys.exit(app.exec_())


if __name__ == "__main__":
    # Example:
    # 1) Train headless: train_morpion_bot(episodes=500)
    # 2) Run UI: run_bot_vs_human("trained_bots/morpion_ep500_a.keras", bot_player="O")
    run_bot_vs_human('trained_bots/morpion_ep2000_c.keras', bot_player="X")
