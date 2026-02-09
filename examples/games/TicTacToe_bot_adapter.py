import sys
from pathlib import Path
import random
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGBotPlayer import SGBotGameAdapter


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
