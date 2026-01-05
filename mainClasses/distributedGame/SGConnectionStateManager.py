# --- Standard library imports ---
from typing import Callable, List
from enum import Enum


class ConnectionState(Enum):
    """Connection dialog states"""
    SETUP = "setup"
    CONNECTING = "connecting"
    WAITING = "waiting"
    READY_MIN = "ready_min"  # Minimum reached, manual start available (creator only)
    READY_MAX = "ready_max"  # Maximum reached, auto-countdown triggers
    READY = "ready"  # Legacy state (kept for backward compatibility)


class SGConnectionStateManager:
    """
    Manages connection dialog state transitions.
    
    This class centralizes state management logic, separating it from UI updates.
    It provides a clean API for state transitions with optional validation and callbacks.
    
    Usage:
        manager = SGConnectionStateManager(initial_state=ConnectionState.SETUP)
        
        # Register a callback for state changes
        manager.on_state_changed(lambda old_state, new_state: print(f"{old_state} -> {new_state}"))
        
        # Transition to a new state
        manager.transition_to(ConnectionState.CONNECTING)
    """
    
    def __init__(self, initial_state: ConnectionState = ConnectionState.SETUP):
        """
        Initialize the state manager.
        
        Args:
            initial_state: Initial state (default: SETUP)
        """
        self._current_state = initial_state
        self._state_changed_callbacks: List[Callable[[ConnectionState, ConnectionState], None]] = []
    
    @property
    def current_state(self) -> ConnectionState:
        """Get the current state"""
        return self._current_state
    
    def on_state_changed(self, callback: Callable[[ConnectionState, ConnectionState], None]):
        """
        Register a callback to be called when state changes.
        
        Args:
            callback: Function(old_state, new_state) called on state change
        """
        if callback not in self._state_changed_callbacks:
            self._state_changed_callbacks.append(callback)
    
    def transition_to(self, new_state: ConnectionState, force: bool = False) -> bool:
        """
        Transition to a new state.
        
        Args:
            new_state: Target state
            force: Unused parameter (kept for backward compatibility)
        
        Returns:
            True if transition was successful
        """
        if new_state == self._current_state:
            return True  # Already in this state
        
        # Perform transition
        old_state = self._current_state
        self._current_state = new_state
        
        # Call state changed callbacks
        for callback in self._state_changed_callbacks:
            try:
                callback(old_state, new_state)
            except Exception as e:
                print(f"[SGConnectionStateManager] Error in state changed callback: {e}")
                import traceback
                traceback.print_exc()
        
        return True

