# --- Standard library imports ---
from typing import Callable, Optional, List, Tuple
from enum import Enum


class HandlerPriority(Enum):
    """Priority levels for MQTT handlers"""
    HIGH = 1
    NORMAL = 2
    LOW = 3


class SGMQTTHandlerManager:
    """
    Centralizes MQTT message handler management with chaining support.
    
    This class eliminates the duplication of the wrapper pattern used throughout
    the distributed game module. It provides a clean API for adding/removing
    handlers and automatically chains them in priority order.
    
    Usage:
        manager = SGMQTTHandlerManager(mqtt_client)
        
        # Add a handler for a specific topic
        handler_id = manager.add_topic_handler(
            topic="session_state",
            handler_func=my_handler,
            priority=HandlerPriority.HIGH
        )
        
        # Add a handler with custom filter
        handler_id = manager.add_filter_handler(
            topic_filter=lambda topic: topic.startswith("session_"),
            handler_func=my_handler,
            priority=HandlerPriority.NORMAL
        )
        
        # Remove a handler
        manager.remove_handler(handler_id)
    """
    
    def __init__(self, mqtt_client):
        """
        Initialize the handler manager.
        
        Args:
            mqtt_client: The MQTT client instance (paho.mqtt.client.Client)
        """
        self.mqtt_client = mqtt_client
        self._handlers: List[Tuple[int, Callable, Callable[[str], bool], HandlerPriority, bool, str]] = []
        self._next_handler_id = 1
        self._original_handler = None
        self._chain_handler = None
        self._is_installed = False
    
    def add_topic_handler(self, 
                          topic: str, 
                          handler_func: Callable,
                          priority: HandlerPriority = HandlerPriority.NORMAL,
                          stop_propagation: bool = False) -> int:
        """
        Add a handler for a specific MQTT topic.
        
        Args:
            topic: Exact topic to handle (e.g., "session_state")
            handler_func: Function(client, userdata, msg) to call for matching messages
            priority: Handler priority (HIGH handlers are called first)
            stop_propagation: If True, don't forward message to next handlers after processing
        
        Returns:
            Handler ID that can be used to remove the handler later
        """
        def topic_filter(msg_topic: str) -> bool:
            return msg_topic == topic
        
        return self.add_filter_handler(
            topic_filter=topic_filter,
            handler_func=handler_func,
            priority=priority,
            stop_propagation=stop_propagation,
            description=f"topic:{topic}"
        )
    
    def add_prefix_handler(self,
                           topic_prefix: str,
                           handler_func: Callable,
                           priority: HandlerPriority = HandlerPriority.NORMAL,
                           stop_propagation: bool = False) -> int:
        """
        Add a handler for topics starting with a prefix.
        
        Args:
            topic_prefix: Topic prefix to match (e.g., "session_")
            handler_func: Function(client, userdata, msg) to call for matching messages
            priority: Handler priority (HIGH handlers are called first)
            stop_propagation: If True, don't forward message to next handlers after processing
        
        Returns:
            Handler ID that can be used to remove the handler later
        """
        def prefix_filter(msg_topic: str) -> bool:
            return msg_topic.startswith(topic_prefix)
        
        return self.add_filter_handler(
            topic_filter=prefix_filter,
            handler_func=handler_func,
            priority=priority,
            stop_propagation=stop_propagation,
            description=f"prefix:{topic_prefix}"
        )
    
    def add_filter_handler(self,
                           topic_filter: Callable[[str], bool],
                           handler_func: Callable,
                           priority: HandlerPriority = HandlerPriority.NORMAL,
                           stop_propagation: bool = False,
                           description: str = "") -> int:
        """
        Add a handler with a custom topic filter function.
        
        Args:
            topic_filter: Function(topic: str) -> bool that returns True if topic matches
            handler_func: Function(client, userdata, msg) to call for matching messages
            priority: Handler priority (HIGH handlers are called first)
            stop_propagation: If True, don't forward message to next handlers after processing
            description: Optional description for debugging
        
        Returns:
            Handler ID that can be used to remove the handler later
        """
        handler_id = self._next_handler_id
        self._next_handler_id += 1
        
        # Wrap handler_func to add error handling
        # Note: Cleanup checks should be done in handler_func itself if needed
        def wrapped_handler(client, userdata, msg):
            # CRITICAL: Protect against RuntimeError if object is destroyed
            try:
                handler_func(client, userdata, msg)
            except RuntimeError:
                # Object has been deleted, ignore
                return
            except Exception as e:
                print(f"[SGMQTTHandlerManager] Error in handler {handler_id} ({description}): {e}")
                import traceback
                traceback.print_exc()
        
        # Add handler to list (sorted by priority)
        # Format: (handler_id, wrapped_handler, topic_filter, priority, stop_propagation, description)
        handler_entry = (handler_id, wrapped_handler, topic_filter, priority, stop_propagation, description)
        self._handlers.append(handler_entry)
        self._handlers.sort(key=lambda x: x[3].value)  # Sort by priority
        
        # Reinstall chain handler if already installed
        if self._is_installed:
            self._install_chain_handler()
        
        return handler_id
    
    def remove_handler(self, handler_id: int) -> bool:
        """
        Remove a handler by ID.
        
        Args:
            handler_id: Handler ID returned by add_*_handler()
        
        Returns:
            True if handler was found and removed, False otherwise
        """
        original_count = len(self._handlers)
        self._handlers = [h for h in self._handlers if h[0] != handler_id]
        
        if len(self._handlers) < original_count:
            # Reinstall chain handler if already installed
            if self._is_installed:
                self._install_chain_handler()
            return True
        return False
    
    def install(self):
        """
        Install the chain handler on the MQTT client.
        This must be called before handlers will receive messages.
        """
        if self._is_installed:
            return
        
        # Save original handler
        self._original_handler = self.mqtt_client.on_message
        
        # Install chain handler
        self._install_chain_handler()
        self._is_installed = True
    
    def _install_chain_handler(self):
        """Install or reinstall the chain handler."""
        def chain_handler(client, userdata, msg):
            """Chain handler that calls registered handlers in priority order."""
            handled = False
            stop_propagation = False
            
            # Call handlers in priority order
            for handler_id, handler_func, topic_filter, priority, stop_prop, description in self._handlers:
                try:
                    # Check if topic matches
                    if topic_filter(msg.topic):
                        # Call handler
                        handler_func(client, userdata, msg)
                        handled = True
                        if stop_prop:
                            stop_propagation = True
                            break  # Stop propagation, don't call other handlers
                except Exception as e:
                    # Log error but continue with other handlers
                    print(f"[SGMQTTHandlerManager] Error in handler {handler_id} ({description}): {e}")
                    import traceback
                    traceback.print_exc()
            
            # Forward to original handler if message wasn't handled or propagation not stopped
            if not stop_propagation and self._original_handler:
                try:
                    self._original_handler(client, userdata, msg)
                except Exception as e:
                    print(f"[SGMQTTHandlerManager] Error in original handler: {e}")
                    import traceback
                    traceback.print_exc()
        
        # Store reference to avoid garbage collection
        self._chain_handler = chain_handler
        
        # Install on client
        self.mqtt_client.on_message = chain_handler
    
    def _uninstall_chain_handler(self):
        """Uninstall chain handler and restore original."""
        if self._original_handler:
            self.mqtt_client.on_message = self._original_handler
        else:
            self.mqtt_client.on_message = None
        self._chain_handler = None
        self._original_handler = None

