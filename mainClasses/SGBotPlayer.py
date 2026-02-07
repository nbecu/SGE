from typing import Any, List, Optional
import random


class SGBotGameAdapter:
    """
    Base adapter for bots.

    An adapter exposes game state and valid actions/targets using the same
    information a human player would have access to.
    """

    def __init__(self, model):
        self.model = model

    def get_observation(self, player) -> Any:
        """Return a game-state observation for the given player."""
        raise NotImplementedError()

    def get_valid_actions(self, player) -> List[Any]:
        """Return the list of valid actions for the given player."""
        return [a for a in getattr(player, "gameActions", []) if a.canBeUsed()]

    def get_valid_targets(self, action, player) -> List[Any]:
        """Return the list of valid targets for a given action."""
        return []

    def choose_action_with_policy(self, player, policy_model, epsilon=0.1, rng=None):
        """Optional policy-based action selection (adapter-specific)."""
        raise NotImplementedError()


class SGBotPlayer:
    """
    Bot wrapper for an existing SGPlayer.
    Uses only the player's actions and game state available to a human player.
    """

    def __init__(self, player, adapter: SGBotGameAdapter, strategy="random", policy_model=None, epsilon=0.1, rng=None):
        self.player = player
        self.adapter = adapter
        self.strategy = strategy
        self.policy_model = policy_model
        self.epsilon = float(epsilon)
        self.rng = rng or random.Random()

    def get_valid_actions(self):
        return self.adapter.get_valid_actions(self.player)

    def choose_action_and_target(self):
        valid_actions = self.get_valid_actions()
        if not valid_actions:
            return None, None

        if self.strategy == "policy" and self.policy_model is not None:
            try:
                return self.adapter.choose_action_with_policy(
                    self.player, self.policy_model, epsilon=self.epsilon, rng=self.rng
                )
            except Exception:
                pass

        action = self.rng.choice(valid_actions)
        targets = self.adapter.get_valid_targets(action, self.player)
        target = self.rng.choice(targets) if targets else None
        return action, target

    def _execute_action(self, action, target):
        if target is None:
            raise ValueError("No target provided for action execution")

        if isinstance(target, tuple) and len(target) == 2:
            action.perform_with(target[0], target[1], serverUpdate=False)
        else:
            action.perform_with(target, serverUpdate=False)

    def execute_action_with_fallback(self, action, target):
        try:
            self._execute_action(action, target)
            return True
        except Exception:
            # Fallback: try other actions/targets
            for alt_action in self.get_valid_actions():
                alt_targets = self.adapter.get_valid_targets(alt_action, self.player)
                for alt_target in alt_targets:
                    try:
                        self._execute_action(alt_action, alt_target)
                        return True
                    except Exception:
                        continue
        return False

    def execute_turn(self):
        action, target = self.choose_action_and_target()
        if action is None:
            return False
        return self.execute_action_with_fallback(action, target)
