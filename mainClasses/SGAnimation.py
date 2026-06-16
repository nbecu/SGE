"""
SGAnimation - Simple animation system for entities.

Supports basic animation types:
- pulse: Fade in/out color
- flash: Quick on/off toggle
- rotate: Rotate entity (for agents)
"""

import time
from PyQt6.QtGui import QColor


class SGAnimationManager:
    """Manages animations for entities in real-time."""

    def __init__(self):
        self.animations = {}  # {entity_id: animation_data}

    def add_animation(self, entity_id, animation_type, duration=1.0, intensity=0.5):
        """Add an animation to an entity.

        Args:
            entity_id (str): Unique entity identifier
            animation_type (str): 'pulse', 'flash', 'rotate'
            duration (float): Animation cycle duration in seconds
            intensity (float): Animation intensity (0-1)
        """
        self.animations[entity_id] = {
            'type': animation_type,
            'duration': duration,
            'intensity': intensity,
            'start_time': time.time(),
        }

    def remove_animation(self, entity_id):
        """Remove animation from an entity.

        Args:
            entity_id (str): Unique entity identifier
        """
        if entity_id in self.animations:
            del self.animations[entity_id]

    def get_animation_factor(self, entity_id):
        """Get the current animation factor (0-1) for an entity.

        Returns factor for current animation cycle position.
        """
        if entity_id not in self.animations:
            return 1.0

        anim = self.animations[entity_id]
        elapsed = time.time() - anim['start_time']
        cycle_position = (elapsed % anim['duration']) / anim['duration']

        anim_type = anim['type']

        if anim_type == 'pulse':
            # Sinusoidal pulse: 1 → 0.5 → 1
            import math
            factor = 0.5 + 0.5 * math.cos(2 * math.pi * cycle_position)
            return factor

        elif anim_type == 'flash':
            # Quick on/off toggle
            return 1.0 if cycle_position < 0.5 else 0.3

        elif anim_type == 'rotate':
            # Rotation angle (0-360)
            return (cycle_position * 360) % 360

        return 1.0

    def apply_pulse_animation(self, base_color, factor):
        """Apply pulse animation to a color.

        Args:
            base_color (QColor): Original color
            factor (float): Animation factor (0-1)

        Returns:
            QColor: Animated color with modified opacity/brightness
        """
        if not isinstance(base_color, QColor):
            base_color = QColor(base_color)

        # Modify opacity based on factor
        color = QColor(base_color)
        new_alpha = int(base_color.alpha() * factor)
        color.setAlpha(max(50, new_alpha))  # Minimum opacity to stay visible
        return color

    @staticmethod
    def global_manager():
        """Get or create the global animation manager."""
        if not hasattr(SGAnimationManager, '_global_manager'):
            SGAnimationManager._global_manager = SGAnimationManager()
        return SGAnimationManager._global_manager
