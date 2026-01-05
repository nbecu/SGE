# --- Standard library imports ---
import json
import time
from typing import Dict, Set, Optional, Callable
from datetime import datetime

# --- Third-party imports ---
from PyQt5.QtCore import QTimer

# --- Project imports ---
from mainClasses.distributedGame.SGDistributedSession import SGDistributedSession
from mainClasses.distributedGame.SGMQTTHandlerManager import SGMQTTHandlerManager, HandlerPriority


class SGSessionDiscoveryManager:
    """
    Manages session discovery and caching for distributed games.
    
    This class centralizes session discovery logic, separating it from UI concerns.
    It handles:
    - Session discovery via MQTT
    - Caching of discovered sessions, instances, players, and session states
    - Callbacks for session updates
    
    Usage:
        manager = SGSessionDiscoveryManager(mqtt_client, session_manager, mqtt_handler_manager)
        manager.on_sessions_updated(lambda sessions: print(f"Found {len(sessions)} sessions"))
        manager.start_discovery()
    """
    
    def __init__(self, mqtt_client, session_manager, mqtt_handler_manager: Optional[SGMQTTHandlerManager] = None):
        """
        Initialize the session discovery manager.
        
        Args:
            mqtt_client: MQTT client instance
            session_manager: SGDistributedSessionManager instance
            mqtt_handler_manager: Optional SGMQTTHandlerManager instance (will be created if None)
        """
        self.mqtt_client = mqtt_client
        self.session_manager = session_manager
        self.mqtt_handler_manager = mqtt_handler_manager
        
        # Caches
        self.available_sessions: Dict[str, dict] = {}  # {session_id: {'timestamp': float, 'info': dict}}
        self.session_players_cache: Dict[str, Set[str]] = {}  # {session_id: set of player_names}
        self.session_instances_cache: Dict[str, Set[str]] = {}  # {session_id: set of client_ids}
        self.session_states_cache: Dict[str, SGDistributedSession] = {}  # {session_id: SGDistributedSession}
        
        # Callbacks
        self._sessions_updated_callbacks: list = []  # List of callbacks(sessions_dict)
        self._session_state_updated_callbacks: list = []  # List of callbacks(session_id, session)
        
        # Handler IDs
        self._session_discovery_handler_id: Optional[int] = None
        self._session_state_discovery_handler_id: Optional[int] = None
        self._session_player_registration_handler_id: Optional[int] = None
        
        # Cleanup flag
        self._cleaning_up = False
    
    def on_sessions_updated(self, callback: Callable[[Dict[str, dict]], None]):
        """
        Register a callback to be called when sessions are discovered/updated.
        
        Args:
            callback: Function(sessions_dict) called when sessions are updated
        """
        if callback not in self._sessions_updated_callbacks:
            self._sessions_updated_callbacks.append(callback)
    
    def remove_sessions_updated_callback(self, callback: Callable[[Dict[str, dict]], None]):
        """Remove a sessions updated callback"""
        if callback in self._sessions_updated_callbacks:
            self._sessions_updated_callbacks.remove(callback)
    
    def on_session_state_updated(self, callback: Callable[[str, SGDistributedSession], None]):
        """
        Register a callback to be called when a session state is updated.
        
        Args:
            callback: Function(session_id, session) called when session state is updated
        """
        if callback not in self._session_state_updated_callbacks:
            self._session_state_updated_callbacks.append(callback)
    
    def remove_session_state_updated_callback(self, callback: Callable[[str, SGDistributedSession], None]):
        """Remove a session state updated callback"""
        if callback in self._session_state_updated_callbacks:
            self._session_state_updated_callbacks.remove(callback)
    
    def _notify_sessions_updated(self):
        """Notify all callbacks that sessions have been updated"""
        for callback in self._sessions_updated_callbacks:
            try:
                callback(self.available_sessions.copy())
            except Exception as e:
                print(f"[SGSessionDiscoveryManager] Error in sessions_updated callback: {e}")
                import traceback
                traceback.print_exc()
    
    def _notify_session_state_updated(self, session_id: str, session: SGDistributedSession):
        """Notify all callbacks that a session state has been updated"""
        for callback in self._session_state_updated_callbacks:
            try:
                callback(session_id, session)
            except Exception as e:
                print(f"[SGSessionDiscoveryManager] Error in session_state_updated callback: {e}")
                import traceback
                traceback.print_exc()
    
    def start_discovery(self, connected_session_id: Optional[str] = None):
        """
        Start session discovery.
        
        Args:
            connected_session_id: Session ID we're currently connected to (will be skipped)
        """
        if not (self.mqtt_client and self.mqtt_client.is_connected()):
            return
        
        # Initialize MQTT Handler Manager if not provided
        if not self.mqtt_handler_manager:
            self.mqtt_handler_manager = SGMQTTHandlerManager(self.mqtt_client)
            self.mqtt_handler_manager.install()
        
        # Remove existing handlers if any
        if self._session_discovery_handler_id is not None:
            self.mqtt_handler_manager.remove_handler(self._session_discovery_handler_id)
        if self._session_state_discovery_handler_id is not None:
            self.mqtt_handler_manager.remove_handler(self._session_state_discovery_handler_id)
        
        # Create handler for session discovery messages
        def session_discovery_handler(client, userdata, msg):
            if self._cleaning_up:
                return
            
            discovery_topic_prefix = f"{self.session_manager.DISCOVERY_TOPIC}/"
            if not msg.topic.startswith(discovery_topic_prefix):
                return
            
            try:
                payload_str = msg.payload.decode("utf-8")
                if not payload_str or payload_str.strip() == "":
                    return  # Ignore empty messages (used to clear retained messages)
                
                msg_dict = json.loads(payload_str)
                session_id = msg_dict.get('session_id')
                if not session_id:
                    return
                
                # Skip if this is the session we're connected to
                if connected_session_id and session_id == connected_session_id:
                    return
                
                # Check expiration for retained messages
                current_time = time.time()
                is_expired = False
                
                if msg.retain:
                    msg_timestamp_iso = msg_dict.get('timestamp')
                    if msg_timestamp_iso:
                        try:
                            timestamp_str = str(msg_timestamp_iso)
                            if 'Z' in timestamp_str:
                                timestamp_str = timestamp_str.replace('Z', '+00:00')
                            msg_datetime = datetime.fromisoformat(timestamp_str)
                            msg_timestamp_unix = msg_datetime.timestamp()
                            age_seconds = current_time - msg_timestamp_unix
                            if age_seconds > 15.0:
                                is_expired = True
                        except (ValueError, AttributeError, TypeError):
                            pass
                
                # Only add session if it's not expired
                if not is_expired:
                    # Update discovered sessions cache
                    if not hasattr(self.session_manager, 'discovered_sessions'):
                        self.session_manager.discovered_sessions = {}
                    
                    self.session_manager.discovered_sessions[session_id] = {
                        'timestamp': current_time,
                        'info': msg_dict
                    }
                    
                    # Clean expired sessions
                    expired_sessions = [
                        sid for sid, data in self.session_manager.discovered_sessions.items()
                        if current_time - data['timestamp'] > 15.0
                    ]
                    for sid in expired_sessions:
                        del self.session_manager.discovered_sessions[sid]
                    
                    # Update available_sessions
                    self.available_sessions = self.session_manager.discovered_sessions.copy()
                    
                    # Subscribe to session_state topic for newly discovered session
                    if session_id != connected_session_id:
                        topic = f"{session_id}/session_state"
                        self.mqtt_client.subscribe(topic, qos=1)
                    
                    # Notify callbacks
                    self._notify_sessions_updated()
                    
            except Exception as e:
                print(f"[SGSessionDiscoveryManager] Error in session_discovery_handler: {e}")
                import traceback
                traceback.print_exc()
        
        # Create handler for session_state updates for discovered sessions
        def session_state_discovery_handler(client, userdata, msg):
            if self._cleaning_up:
                return
            
            if not msg.topic.endswith('/session_state'):
                return
            
            try:
                payload_str = msg.payload.decode("utf-8")
                if not payload_str or payload_str.strip() == "":
                    return  # Ignore empty messages (used to clear retained messages)
                
                data = json.loads(payload_str)
                session = SGDistributedSession.from_dict(data)
                session_id = session.session_id
                
                # Skip if this is the session we're connected to
                if connected_session_id and session_id == connected_session_id:
                    return
                
                # Only process if this is a discovered session
                if session_id not in self.available_sessions:
                    return
                
                # Update cache
                self.session_states_cache[session_id] = session
                
                # If session is closed, remove it from available_sessions
                if session.state == 'closed':
                    if session_id in self.available_sessions:
                        del self.available_sessions[session_id]
                    # Also remove from session_manager's cache
                    if hasattr(self.session_manager, 'discovered_sessions') and session_id in self.session_manager.discovered_sessions:
                        del self.session_manager.discovered_sessions[session_id]
                
                # Notify callbacks
                self._notify_session_state_updated(session_id, session)
                self._notify_sessions_updated()
                
            except Exception as e:
                print(f"[SGSessionDiscoveryManager] Error in session_state_discovery_handler: {e}")
                import traceback
                traceback.print_exc()
        
        # Add handlers using SGMQTTHandlerManager
        self._session_discovery_handler_id = self.mqtt_handler_manager.add_prefix_handler(
            topic_prefix=f"{self.session_manager.DISCOVERY_TOPIC}/",
            handler_func=session_discovery_handler,
            priority=HandlerPriority.NORMAL,
            stop_propagation=False
        )
        
        self._session_state_discovery_handler_id = self.mqtt_handler_manager.add_filter_handler(
            topic_filter=lambda topic: topic.endswith('/session_state'),
            handler_func=session_state_discovery_handler,
            priority=HandlerPriority.NORMAL,
            stop_propagation=False
        )
        
        # Subscribe to discovery topic
        discovery_topic_wildcard = f"{self.session_manager.DISCOVERY_TOPIC}/+"
        
        # Unsubscribe first to force broker to send retained messages on resubscribe
        try:
            self.mqtt_client.unsubscribe(discovery_topic_wildcard)
            time.sleep(0.1)
        except Exception:
            pass
        
        # Subscribe to discovery topic
        self.mqtt_client.subscribe(discovery_topic_wildcard, qos=1)
        
        # Wait a moment for retained messages, then notify
        def notify_after_discovery():
            if hasattr(self.session_manager, 'discovered_sessions'):
                self.available_sessions = self.session_manager.discovered_sessions.copy()
            self._notify_sessions_updated()
            # Start player registration tracking
            self._start_player_registration_tracking(connected_session_id)
        
        QTimer.singleShot(500, notify_after_discovery)
    
    def _start_player_registration_tracking(self, connected_session_id: Optional[str] = None):
        """
        Subscribe to player registration topics for all discovered sessions.
        
        Args:
            connected_session_id: Session ID we're connected to (will be skipped)
        """
        if not (self.mqtt_client and self.mqtt_client.is_connected()):
            return
        
        # Initialize MQTT Handler Manager if not provided
        if not self.mqtt_handler_manager:
            self.mqtt_handler_manager = SGMQTTHandlerManager(self.mqtt_client)
            self.mqtt_handler_manager.install()
        
        # Remove existing handler if any
        if self._session_player_registration_handler_id is not None:
            self.mqtt_handler_manager.remove_handler(self._session_player_registration_handler_id)
        
        # Create handler for player registrations
        def player_registration_tracker(client, userdata, msg):
            if self._cleaning_up:
                return
            
            # Check if this is a player registration/disconnect message for a discovered session
            for session_id in self.available_sessions.keys():
                if connected_session_id and session_id == connected_session_id:
                    continue
                
                # Check player registration
                registration_topic_base = f"{session_id}/session_player_registration"
                if msg.topic.startswith(registration_topic_base + "/"):
                    try:
                        payload_str = msg.payload.decode("utf-8")
                        if not payload_str or payload_str.strip() == "":
                            return
                        
                        msg_dict = json.loads(payload_str)
                        client_id = msg_dict.get('clientId')
                        player_name = msg_dict.get('assigned_player_name')
                        
                        # Track instances
                        if client_id:
                            if session_id not in self.session_instances_cache:
                                self.session_instances_cache[session_id] = set()
                            self.session_instances_cache[session_id].add(client_id)
                            self._notify_sessions_updated()
                        
                        # Track players
                        if player_name:
                            if session_id not in self.session_players_cache:
                                self.session_players_cache[session_id] = set()
                            self.session_players_cache[session_id].add(player_name)
                            self._notify_sessions_updated()
                    except Exception as e:
                        print(f"[SGSessionDiscoveryManager] Error tracking player registration: {e}")
                        import traceback
                        traceback.print_exc()
                    return
                
                # Check player disconnect
                disconnect_topic_base = f"{session_id}/session_player_disconnect"
                if msg.topic.startswith(disconnect_topic_base + "/"):
                    try:
                        payload_str = msg.payload.decode("utf-8")
                        if not payload_str or payload_str.strip() == "":
                            return  # Ignore empty messages (used to clear retained messages)
                        
                        msg_dict = json.loads(payload_str)
                        client_id = msg_dict.get('clientId')
                        
                        if client_id and session_id in self.session_instances_cache:
                            if client_id in self.session_instances_cache[session_id]:
                                self.session_instances_cache[session_id].remove(client_id)
                                self._notify_sessions_updated()
                    except Exception as e:
                        print(f"[SGSessionDiscoveryManager] Error tracking player disconnect: {e}")
                        import traceback
                        traceback.print_exc()
                    return
                
                # Check instance_ready
                instance_ready_topic_base = f"{session_id}/session_instance_ready"
                if msg.topic.startswith(instance_ready_topic_base + "/"):
                    try:
                        payload_str = msg.payload.decode("utf-8")
                        if not payload_str or payload_str.strip() == "":
                            return  # Ignore empty messages (used to clear retained messages)
                        
                        msg_dict = json.loads(payload_str)
                        client_id = msg_dict.get('clientId')
                        
                        if client_id:
                            if session_id not in self.session_instances_cache:
                                self.session_instances_cache[session_id] = set()
                            if client_id not in self.session_instances_cache[session_id]:
                                self.session_instances_cache[session_id].add(client_id)
                                self._notify_sessions_updated()
                    except Exception as e:
                        print(f"[SGSessionDiscoveryManager] Error tracking instance_ready: {e}")
                        import traceback
                        traceback.print_exc()
                    return
        
        # Add handler using SGMQTTHandlerManager
        # Use a filter that dynamically checks if topic matches any discovered session
        # This allows the filter to work even as sessions are discovered/removed
        def topic_filter(topic: str) -> bool:
            # Check against current available_sessions (dynamic)
            for session_id in self.available_sessions.keys():
                if connected_session_id and session_id == connected_session_id:
                    continue
                if (topic.startswith(f"{session_id}/session_player_registration/") or
                    topic.startswith(f"{session_id}/session_player_disconnect/") or
                    topic.startswith(f"{session_id}/session_instance_ready/")):
                    return True
            return False
        
        self._session_player_registration_handler_id = self.mqtt_handler_manager.add_filter_handler(
            topic_filter=topic_filter,
            handler_func=player_registration_tracker,
            priority=HandlerPriority.NORMAL,
            stop_propagation=False,
            description="session_player_registration_tracking"
        )
        
        # Subscribe to player registration topics for all discovered sessions
        for session_id in self.available_sessions.keys():
            if connected_session_id and session_id == connected_session_id:
                continue
            
            # Subscribe to wildcard topics to get all registrations/disconnects/instance_ready
            registration_topic_wildcard = f"{session_id}/session_player_registration/+"
            disconnect_topic_wildcard = f"{session_id}/session_player_disconnect/+"
            instance_ready_topic_wildcard = f"{session_id}/session_instance_ready/+"
            
            self.mqtt_client.subscribe(registration_topic_wildcard, qos=1)
            self.mqtt_client.subscribe(disconnect_topic_wildcard, qos=1)
            self.mqtt_client.subscribe(instance_ready_topic_wildcard, qos=1)
    
    def stop_discovery(self):
        """Stop session discovery and clean up handlers"""
        self._cleaning_up = True
        
        if self.mqtt_handler_manager:
            if self._session_discovery_handler_id is not None:
                self.mqtt_handler_manager.remove_handler(self._session_discovery_handler_id)
                self._session_discovery_handler_id = None
            if self._session_state_discovery_handler_id is not None:
                self.mqtt_handler_manager.remove_handler(self._session_state_discovery_handler_id)
                self._session_state_discovery_handler_id = None
            if self._session_player_registration_handler_id is not None:
                self.mqtt_handler_manager.remove_handler(self._session_player_registration_handler_id)
                self._session_player_registration_handler_id = None
        
        self._cleaning_up = False

