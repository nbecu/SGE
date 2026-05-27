import sys
from pathlib import Path
import random
import itertools
import string
import numpy as np
from PyQt6 import QtWidgets, QtGui, QtCore

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
from mainClasses.bot_ml import DQNTrainer, build_dense_q_model
from examples.games.TicTacToe import tic_tac_toe_game
from examples.games.TicTacToe_bot_adapter import TicTacToeAdapter


# ============================================================================
# Notes
# - This bot runner is intentionally separated from the game definition.
# - Recommended training config (stable):
#     self_play=False, opponent_strategy="heuristic"
#     eval_games=200
# - Future: integrate "run bot vs human" into SGE core architecture.
# ============================================================================


# ============================================================================
# Training (TensorFlow/Keras)
# ============================================================================
def build_policy_model():
    return build_dense_q_model(input_size=9, output_size=9, learning_rate=0.0005, hidden_sizes=(64, 64))


def _iter_suffixes():
    letters = string.ascii_lowercase
    for size in range(1, 3):
        for comb in itertools.product(letters, repeat=size):
            yield "".join(comb)


def _get_auto_model_path(models_dir, game_name, episodes, bot_role):
    for suffix in _iter_suffixes():
        candidate = models_dir / f"{game_name}_bot_role{bot_role}_ep{episodes}_{suffix}.keras"
        if not candidate.exists():
            return candidate
    raise RuntimeError("No available suffix for model file name.")


def train_tictactoe_bot(
    episodes=500,
    epsilon=1.0,
    epsilon_min=0.05,
    epsilon_decay=0.99,
    gamma=0.95,
    seed=42,
    output_path=None,
    game_name="tictactoe",
    self_play=True,
    step_penalty=0.02,
    debug=False,
    eval_games=0,
    opponent_strategy="heuristic",
    train_player="X",
):
    random.seed(seed)
    np.random.seed(seed)

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    model = tic_tac_toe_game(ui_enabled=False, with_control_panels=False)
    Player1 = model.getPlayer("Player 1")
    Player2 = model.getPlayer("Player 2")
    learner = Player1 if str(train_player).upper() == "X" else Player2
    opponent = Player2 if learner == Player1 else Player1

    adapter = TicTacToeAdapter(model)
    policy_model = build_policy_model()
    target_model = build_policy_model()
    target_model.set_weights(policy_model.get_weights())
    trainer = DQNTrainer(
        policy_model,
        target_model,
        gamma=gamma,
        batch_size=128,
        target_update_steps=200,
        replay_maxlen=20000,
    )

    def reset_game():
        adapter.reset_board()
        for action in model.getAllGameActions():
            action.reset()
        model.timeManager.currentRoundNumber = 0
        model.timeManager.currentPhaseNumber = 0
        model.setCurrentPlayer(learner.name)
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


    def _find_winning_indices(mark, valid_indices):
        cells = list(adapter._iter_cells())
        grid = [cells[i].value("state") for i in range(9)]
        lines = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        winning = []
        for i in valid_indices:
            trial = list(grid)
            trial[i] = mark
            for a, b, c in lines:
                if trial[a] == trial[b] == trial[c] == mark:
                    winning.append(i)
                    break
        return winning

    def select_opponent_action(player):
        valid_indices = adapter.get_valid_action_indices()
        if not valid_indices:
            return None, None
        if opponent_strategy != "heuristic":
            action_idx = random.choice(valid_indices)
            return action_idx, adapter.get_action_space()[action_idx]
        mark = adapter.player_mark_map[player.name]
        opponent_mark = adapter.player_mark_map[Player1.name if player.name == Player2.name else Player2.name]
        winning = _find_winning_indices(mark, valid_indices)
        if winning:
            action_idx = random.choice(winning)
            return action_idx, adapter.get_action_space()[action_idx]
        blocking = _find_winning_indices(opponent_mark, valid_indices)
        if blocking:
            action_idx = random.choice(blocking)
            return action_idx, adapter.get_action_space()[action_idx]
        action_idx = random.choice(valid_indices)
        return action_idx, adapter.get_action_space()[action_idx]

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
            if current_player.name != learner.name:
                model.setCurrentPlayer(learner.name)
                model.timeManager.nextPhase()
                current_player = model.getCurrentPlayer()
                if current_player is None:
                    break

            _debug_state("before_move", current_player)

            current_mark = adapter.player_mark_map[learner.name]
            opponent_mark = adapter.player_mark_map[opponent.name]
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
                trainer.remember(obs, action_idx, reward, next_obs, True)
                trainer.train_from_replay()
                continue

            opponent_turn = model.getCurrentPlayer()
            if opponent_turn is None:
                break

            if self_play:
                obs_op, action_idx_op, target_cell_op = select_action(opponent_turn)
                if target_cell_op is None:
                    break
                opponent_action = opponent_turn.gameActions[0]
                opponent_action.perform_with(target_cell_op, serverUpdate=False)
                winner_after_opponent = adapter.check_victory()
                _debug_state("after_opponent_move", opponent_turn, winner_override=winner_after_opponent)
            else:
                action_idx_op, target_cell_op = select_opponent_action(opponent)
                if target_cell_op is None:
                    break
                opponent.gameActions[0].perform_with(target_cell_op, serverUpdate=False)
                winner_after_opponent = adapter.check_victory()
                _debug_state("after_opponent_move", opponent, winner_override=winner_after_opponent)
                obs_op = None
                action_idx_op = None

            winner = winner_after_opponent
            if winner:
                reward_op = 1.0 if opponent_turn and winner == opponent_turn.name else -1.0
                reward_cur = 1.0 if winner == learner.name else -1.0
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

            if self_play and obs_op is not None and action_idx_op is not None:
                next_obs_op = adapter.get_observation(opponent_turn)
                trainer.remember(obs_op, action_idx_op, reward_op, next_obs_op, done)

            next_obs = adapter.get_observation(current_player)
            trainer.remember(obs, action_idx, reward_cur, next_obs, done)
            trainer.train_from_replay()

        epsilon = max(epsilon_min, epsilon * epsilon_decay)

    models_dir = Path(__file__).parent / "trained_bots"
    models_dir.mkdir(parents=True, exist_ok=True)
    if output_path:
        model_path = Path(output_path)
        if not model_path.is_absolute():
            model_path = models_dir / model_path
    else:
        model_path = _get_auto_model_path(models_dir, game_name, episodes, str(train_player).upper())
    policy_model.save(model_path)
    evaluate_policy(eval_games)
    return model_path


# ============================================================================
# UI: Bot vs Human
# ============================================================================
def run_bot_vs_human(model_path=None, bot_player="O", bot_epsilon=0, randomize_first_bot_move=True, logs_ui=False):
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
            if logs_ui:
                print(f"[INFO] Modele charge: {model_path}")
        except Exception:
            policy_model = None
            if logs_ui:
                print("[WARN] Modele non charge, bot aleatoire.")

    bot_name = Player2.name if bot_player.upper() == "O" else Player1.name
    strategy = "policy" if policy_model is not None else "random"
    bot = model.enableBotPlayer(bot_name, adapter, strategy=strategy, policy_model=policy_model, epsilon=0.0)

    bot_moves = {"count": 0}

    def bot_tick():
        current_player = model.getCurrentPlayer()
        if adapter.check_victory() is not None or adapter.is_draw():
            return
        if current_player and current_player.name == bot_name:
            if policy_model is not None:
                action_space = adapter.get_action_space()
                grid_states = [cell.value("state") for cell in action_space]
                if randomize_first_bot_move and all(s == "empty" for s in grid_states):
                    valid_indices = adapter.get_valid_action_indices()
                    action_idx = random.choice(valid_indices)
                    action = current_player.gameActions[0]
                    target = action_space[action_idx]
                else:
                    if randomize_first_bot_move:
                        epsilon = float(bot_epsilon) if bot_moves["count"] == 0 else 0.0
                    else:
                        epsilon = 0.0
                    action, target = adapter.choose_action_with_policy(current_player, policy_model, epsilon=epsilon)
                if action is None or target is None:
                    return
                obs = adapter.get_observation(current_player).reshape(1, -1)
                q_values = policy_model.predict(obs, verbose=0)[0]
                try:
                    idx = action_space.index(target)
                    valid_indices = adapter.get_valid_action_indices()
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
                    if logs_ui:
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
                bot_moves["count"] += 1
            else:
                bot.execute_turn()
        QtCore.QTimer.singleShot(200, bot_tick)

    model.launch()
    QtCore.QTimer.singleShot(200, bot_tick)
    sys.exit(app.exec())


def evaluate_saved_model(model_path, games=200, bot_player="X"):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    model = tic_tac_toe_game(ui_enabled=False, with_control_panels=False)
    Player1 = model.getPlayer("Player 1")
    Player2 = model.getPlayer("Player 2")
    adapter = TicTacToeAdapter(model)

    try:
        model_path = Path(model_path)
        if not model_path.is_absolute():
            model_path = Path(__file__).parent / model_path
        from tensorflow import keras
        policy_model = keras.models.load_model(str(model_path))
    except Exception as exc:
        raise RuntimeError(f"Impossible de charger le modele: {model_path}") from exc

    bot_name = Player2.name if bot_player.upper() == "O" else Player1.name
    wins = 0
    losses = 0
    draws = 0

    for _ in range(games):
        adapter.reset_board()
        for action in model.getAllGameActions():
            action.reset()
        model.timeManager.currentRoundNumber = 0
        model.timeManager.currentPhaseNumber = 0
        model.setCurrentPlayer(Player1.name)
        model.timeManager.nextPhase()

        done = False
        while not done:
            current_player = model.getCurrentPlayer()
            if current_player is None:
                break
            if current_player.name == bot_name:
                obs = adapter.get_observation(current_player).reshape(1, -1)
                q_values = policy_model.predict(obs, verbose=0)[0]
                valid_indices = adapter.get_valid_action_indices()
                if not valid_indices:
                    break
                action_idx = max(valid_indices, key=lambda i: q_values[i])
                current_player.gameActions[0].perform_with(adapter.get_action_space()[action_idx], serverUpdate=False)
            else:
                valid_indices = adapter.get_valid_action_indices()
                if not valid_indices:
                    break
                action_idx = random.choice(valid_indices)
                current_player.gameActions[0].perform_with(adapter.get_action_space()[action_idx], serverUpdate=False)

            winner = adapter.check_victory()
            if winner:
                if winner == bot_name:
                    wins += 1
                else:
                    losses += 1
                done = True
            elif adapter.is_draw():
                draws += 1
                done = True

    print(f"[EVAL_MODEL] games={games} wins={wins} losses={losses} draws={draws} bot={bot_name}")


if __name__ == "__main__":
    # 1) Train headless: train_tictactoe_bot(episodes=500)
    # 2) Run UI: run_bot_vs_human("trained_bots/tictactoe_bot_roleX_ep2000_a.keras", bot_player="O")
    run_bot_vs_human('trained_bots/tictactoe_bot_roleX_ep2000_a.keras', bot_player="X")
