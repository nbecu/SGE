import sys
from pathlib import Path
import random
import itertools
import string
import numpy as np
from collections import deque
from PyQt5 import QtWidgets, QtGui, QtCore

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
from mainClasses.SGBotPlayer import SGBotGameAdapter, SGBotPlayer
from examples.games.TicTacToe import tic_tac_toe_game


# ============================================================================
# TicTacToe - Adapter
# ============================================================================
class TicTacToeAdapter(SGBotGameAdapter):
    def __init__(self, model):
        super().__init__(model)
        self.cell_def = model.getCellType()
        self.player_mark_map = {"Player 1": "X", "Player 2": "O"}

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
        if hasattr(self.model, "winner"):
            # print(f"ICI 1 {self.model.winner}")
            return self.model.winner
        # print(f"ICI 2")
        # cells = list(self._iter_cells())
        # grid = [cells[i].value("state") for i in range(9)]
        # lines = [
        #     (0, 1, 2), (3, 4, 5), (6, 7, 8),
        #     (0, 3, 6), (1, 4, 7), (2, 5, 8),
        #     (0, 4, 8), (2, 4, 6)
        # ]
        # for a, b, c in lines:
        #     if grid[a] == grid[b] == grid[c] and grid[a] != "empty":
        #         return grid[a]
        # return None

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
                for player_name, mark in self.player_mark_map.items():
                    if mark == grid[a]:
                        if hasattr(self.model, "winner"):
                            self.model.winner = player_name
                        return player_name
        return None

    def is_draw(self):
        return all(cell.value("state") != "empty" for cell in self._iter_cells())

    def reset_board(self):
        if hasattr(self.model, "winner"):
            self.model.winner = None
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


def train_morpion_bot(episodes=500, epsilon=1.0, epsilon_min=0.1, epsilon_decay=0.98, gamma=0.9, seed=42, output_path=None, game_name="morpion", self_play=True, step_penalty=0.02, debug=False, eval_games=0):
    random.seed(seed)
    np.random.seed(seed)

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    model = tic_tac_toe_game(ui_enabled=False, with_control_panels=False)
    Player1 = model.getPlayer("Player 1")
    Player2 = model.getPlayer("Player 2")

    adapter = TicTacToeAdapter(model)
    policy_model = build_policy_model()
    target_model = build_policy_model()
    target_model.set_weights(policy_model.get_weights())
    replay_buffer = deque(maxlen=5000)
    batch_size = 64
    target_update_steps = 200
    train_steps = 0

    def reset_game():
        adapter.reset_board()
        for action in model.getAllGameActions():
            action.reset()
        model.timeManager.currentRoundNumber = 0
        model.timeManager.currentPhaseNumber = 0
        model.setCurrentPlayer(Player1.name)
        model.timeManager.nextPhase()

    def _debug_state(label, player, winner_override=None):
        if not debug:
            return
        action_space = adapter.get_action_space()
        grid_states = [cell.value("state") for cell in action_space]
        pretty = [('_' if s == 'empty' else s) for s in grid_states]
        obs = adapter.get_observation(player)
        obs_marks = []
        for v in obs.tolist():
            if v == 0:
                obs_marks.append('_')
            elif v == 1:
                obs_marks.append('P')
            else:
                obs_marks.append('O')
        print(f"[DEBUG] {label} | player={player.name} mark={adapter.player_mark_map[player.name]}")
        print(f"[DEBUG] grid   [ {' '.join(pretty)} ]")
        print(f"[DEBUG] obs    [ {' '.join(obs_marks)} ]")
        if winner_override is not None:
            print(f"[DEBUG] winner={winner_override}")
        elif hasattr(model, "winner"):
            print(f"[DEBUG] winner={model.winner}")

    def count_two_in_row(mark):
        cells = list(adapter._iter_cells())
        grid = [cells[i].value("state") for i in range(9)]
        lines = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        count = 0
        for a, b, c in lines:
            values = [grid[a], grid[b], grid[c]]
            if values.count(mark) == 2 and values.count("empty") == 1:
                count += 1
        return count

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

    def remember(obs, action_idx, reward, next_obs, done):
        replay_buffer.append((obs, action_idx, reward, next_obs, done))

    def train_from_replay():
        nonlocal train_steps
        if len(replay_buffer) < batch_size:
            return
        batch = random.sample(replay_buffer, batch_size)
        obs_batch = np.array([b[0] for b in batch], dtype=np.float32)
        next_obs_batch = np.array([b[3] for b in batch], dtype=np.float32)
        q_current = policy_model.predict(obs_batch, verbose=0)
        q_next = target_model.predict(next_obs_batch, verbose=0)
        for i, (_, action_idx, reward, _, done) in enumerate(batch):
            if done:
                q_current[i, action_idx] = reward
            else:
                q_current[i, action_idx] = reward + gamma * float(np.max(q_next[i]))
        policy_model.fit(obs_batch, q_current, verbose=0)
        train_steps += 1
        if train_steps % target_update_steps == 0:
            target_model.set_weights(policy_model.get_weights())

    def evaluate_policy(games=50):
        if games <= 0:
            return
        wins = 0
        losses = 0
        draws = 0
        for _ in range(games):
            reset_game()
            done = False
            while not done:
                current_player = model.getCurrentPlayer()
                if current_player is None:
                    break
                if current_player.name == Player1.name:
                    obs = adapter.get_observation(current_player).reshape(1, -1)
                    q_values = policy_model.predict(obs, verbose=0)[0]
                    valid_indices = adapter.get_valid_action_indices()
                    if not valid_indices:
                        break
                    action_idx = max(valid_indices, key=lambda i: q_values[i])
                    action = current_player.gameActions[0]
                    action.perform_with(adapter.get_action_space()[action_idx], serverUpdate=False)
                else:
                    valid_indices = adapter.get_valid_action_indices()
                    if not valid_indices:
                        break
                    action_idx = random.choice(valid_indices)
                    action = current_player.gameActions[0]
                    action.perform_with(adapter.get_action_space()[action_idx], serverUpdate=False)

                winner = adapter.check_victory()
                if winner:
                    if winner == Player1.name:
                        wins += 1
                    else:
                        losses += 1
                    done = True
                elif adapter.is_draw():
                    draws += 1
                    done = True
        print(f"[EVAL] games={games} wins={wins} losses={losses} draws={draws}")

    for _ in range(episodes):
        reset_game()
        done = False
        while not done:
            current_player = model.getCurrentPlayer()
            if current_player is None:
                break

            _debug_state("before_move", current_player)

            current_mark = adapter.player_mark_map[current_player.name]
            opponent_mark = adapter.player_mark_map[Player2.name if current_player.name == Player1.name else Player1.name]
            before_two = count_two_in_row(current_mark)
            before_opp_two = count_two_in_row(opponent_mark)

            obs, action_idx, target_cell = select_action(current_player)
            if target_cell is None:
                break
            action = current_player.gameActions[0]
            action.perform_with(target_cell, serverUpdate=False)

            winner = adapter.check_victory()
            _debug_state("after_move", current_player, winner_override=winner)

            after_two = count_two_in_row(current_mark)
            after_opp_two = count_two_in_row(opponent_mark)
            if winner:
                reward = 1.0 if winner == current_player.name else -1.0
                done = True
            elif adapter.is_draw():
                reward = 0.2
                done = True
            else:
                reward = -float(step_penalty)
                if after_two > before_two:
                    reward += 0.2
                if after_opp_two < before_opp_two:
                    reward += 0.2

            if done:
                next_obs = adapter.get_observation(current_player)
                remember(obs, action_idx, reward, next_obs, True)
                train_from_replay()
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
                winner_after_opponent = adapter.check_victory()
                _debug_state("after_opponent_move", opponent, winner_override=winner_after_opponent)
            else:
                targets = adapter.get_valid_targets(Player2.gameActions[0], Player2)
                if not targets:
                    break
                Player2.gameActions[0].perform_with(random.choice(targets), serverUpdate=False)
                winner_after_opponent = adapter.check_victory()
                _debug_state("after_opponent_move", Player2, winner_override=winner_after_opponent)
                obs_op = None
                action_idx_op = None

            winner = adapter.check_victory()
            if winner:
                reward_op = 1.0 if opponent and winner == opponent.name else -1.0
                reward_cur = 1.0 if winner == current_player.name else -1.0
                if winner == opponent.name:
                    reward_cur -= 0.5
                done = True
            elif adapter.is_draw():
                reward_op = 0.2
                reward_cur = 0.2
                done = True
            else:
                reward_op = -float(step_penalty)
                reward_cur = -float(step_penalty)

            # Store opponent transition (self-play only)
            if self_play and obs_op is not None and action_idx_op is not None:
                next_obs_op = adapter.get_observation(opponent)
                remember(obs_op, action_idx_op, reward_op, next_obs_op, done)

            # Store current player transition (after opponent move)
            next_obs = adapter.get_observation(current_player)
            remember(obs, action_idx, reward_cur, next_obs, done)
            train_from_replay()

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
    evaluate_policy(eval_games)
    return model_path


# ============================================================================
# UI: Bot vs Human
# ============================================================================
def run_bot_vs_human(model_path=None, bot_player="O"):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    model = tic_tac_toe_game(ui_enabled=True, with_control_panels=True)
    Player1 = model.getPlayer("Player 1")
    Player2 = model.getPlayer("Player 2")
    adapter = TicTacToeAdapter(model)

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
            if policy_model is not None:
                action, target = adapter.choose_action_with_policy(current_player, policy_model, epsilon=0.0)
                if action is None or target is None:
                    return
                obs = adapter.get_observation(current_player).reshape(1, -1)
                q_values = policy_model.predict(obs, verbose=0)[0]
                action_space = adapter.get_action_space()
                try:
                    idx = action_space.index(target)
                    valid_indices = adapter.get_valid_action_indices()
                    grid_states = [cell.value("state") for cell in action_space]
                    pretty = [('_' if s == 'empty' else s) for s in grid_states]
                    coords = [(cell.xCoord, cell.yCoord) for cell in action_space]
                    mark = adapter.player_mark_map[current_player.name]
                    lines = [
                        (0, 1, 2), (3, 4, 5), (6, 7, 8),
                        (0, 3, 6), (1, 4, 7), (2, 5, 8),
                        (0, 4, 8), (2, 4, 6)
                    ]
                    winning_indices = []
                    for i in valid_indices:
                        trial = list(grid_states)
                        trial[i] = mark
                        for a, b, c in lines:
                            if trial[a] == trial[b] == trial[c] == mark:
                                winning_indices.append(i)
                                break
                    print(f"index_values [ {' '.join(pretty)} ]")
                    print(f"Indices valides: {valid_indices}")
                    print(f"Index->coords: {coords}")
                    print(f"Joueur courant: {current_player.name} (mark={mark})")
                    if winning_indices:
                        print(f"Coups gagnants immediats: {sorted(set(winning_indices))}")
                    else:
                        print("Coups gagnants immediats: []")
                    print(f"Q-values (0-8): {q_values}")
                    print(f"Q-value du coup choisi (index {idx}): {q_values[idx]}")
                except ValueError:
                    pass
                bot.execute_action_with_fallback(action, target)
            else:
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
    run_bot_vs_human('trained_bots/morpion_ep500_b.keras', bot_player="X")
