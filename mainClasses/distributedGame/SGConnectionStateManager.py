# --- Standard library imports ---
from typing import Callable, Optional, Dict, List
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
        self._state_handlers: Dict[ConnectionState, List[Callable[[], None]]] = {}
        self._transition_validators: Dict[tuple, Callable[[ConnectionState, ConnectionState], bool]] = {}
    
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
    
    def remove_state_changed_callback(self, callback: Callable[[ConnectionState, ConnectionState], None]):
        """Remove a state changed callback"""
        if callback in self._state_changed_callbacks:
            self._state_changed_callbacks.remove(callback)
    
    def register_state_handler(self, state: ConnectionState, handler: Callable[[], None]):
        """
        Register a handler to be called when entering a specific state.
        
        Args:
            state: State to handle
            handler: Function() called when entering this state
        """
        if state not in self._state_handlers:
            self._state_handlers[state] = []
        if handler not in self._state_handlers[state]:
            self._state_handlers[state].append(handler)
    
    def remove_state_handler(self, state: ConnectionState, handler: Callable[[], None]):
        """Remove a state handler"""
        if state in self._state_handlers and handler in self._state_handlers[state]:
            self._state_handlers[state].remove(handler)
    
    def register_transition_validator(self, 
                                     from_state: ConnectionState, 
                                     to_state: ConnectionState,
                                     validator: Callable[[ConnectionState, ConnectionState], bool]):
        """
        Register a validator for a specific transition.
        
        Args:
            from_state: Source state
            to_state: Target state
            validator: Function(old_state, new_state) -> bool that returns True if transition is allowed
        """
        key = (from_state, to_state)
        self._transition_validators[key] = validator
    
    def transition_to(self, new_state: ConnectionState, force: bool = False) -> bool:
        """
        Transition to a new state.
        
        Args:
            new_state: Target state
            force: If True, skip validation (default: False)
        
        Returns:
            True if transition was successful, False if validation failed
        """
        if new_state == self._current_state:
            return True  # Already in this state
        
        # Validate transition if not forced
        if not force:
            key = (self._current_state, new_state)
            if key in self._transition_validators:
                validator = self._transition_validators[key]
                if not validator(self._current_state, new_state):
                    return False  # Validation failed
        
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
        
        # Call state-specific handlers
        if new_state in self._state_handlers:
            for handler in self._state_handlers[new_state]:
                try:
                    handler()
                except Exception as e:
                    print(f"[SGConnectionStateManager] Error in state handler: {e}")
                    import traceback
                    traceback.print_exc()
        
        return True
    
    def can_transition_to(self, new_state: ConnectionState) -> bool:
        """
        Check if transition to a new state is allowed.
        
        Args:
            new_state: Target state
        
        Returns:
            True if transition is allowed, False otherwise
        """
        if new_state == self._current_state:
            return True
        
        key = (self._current_state, new_state)
        if key in self._transition_validators:
            validator = self._transition_validators[key]
            return validator(self._current_state, new_state)
        
        return True  # No validator means transition is allowed

