# --- Standard library imports ---
import json
from typing import Optional, Callable, Set
from PyQt5.QtCore import QTimer, QObject, pyqtSignal

# --- Project imports ---
from mainClasses.distributedGame.SGMQTTHandlerManager import SGMQTTHandlerManager, HandlerPriority


class SGSeedSyncManager(QObject):
    """
    Manages seed synchronization for distributed games.
    
    This class centralizes seed synchronization logic, separating it from UI concerns.
    It handles:
    - Seed synchronization via MQTT
    - Tracking of connected instances via seed sync messages
    - Periodic republishing of seed sync messages
    - Callbacks for seed sync events
    
    Usage:
        manager = SGSeedSyncManager(mqtt_client, session_manager, mqtt_handler_manager)
        manager.on_seed_synced(lambda seed: print(f"Seed synced: {seed}"))
        manager.on_instance_connected(lambda client_id: print(f"Instance connected: {client_id}"))
        synced_seed = manager.sync_seed(session_id, shared_seed=12345)
    """
    
    # Signals
    seed_synced_signal = pyqtSignal(int)  # Emitted when seed is successfully synchronized
    instance_connected_signal = pyqtSignal(str)  # Emitted when a new instance is detected via seed sync
    sync_failed_signal = pyqtSignal(str)  # Emitted when seed sync fails (error message)
    
    def __init__(self, mqtt_client, session_manager, mqtt_handler_manager: Optional[SGMQTTHandlerManager] = None, model=None):
        """
        Initialize the seed sync manager.
        
        Args:
            mqtt_client: MQTT client instance
            session_manager: SGDistributedSessionManager instance
            mqtt_handler_manager: Optional SGMQTTHandlerManager instance (will be created if None)
            model: Optional SGModel instance (for accessing clientId)
        """
        super().__init__()
        self.mqtt_client = mqtt_client
        self.session_manager = session_manager
        self.mqtt_handler_manager = mqtt_handler_manager
        self.model = model
        
        # State
        self._seed_synced = False
        self._synced_seed_value: Optional[int] = None
        self._connected_instances: Set[str] = set()
        self._last_republish_time = 0  # Timestamp of last seed sync republish (to prevent loops)
        self._republish_cooldown = 2.0  # Minimum seconds between republishes (to prevent loops)
        self._current_session_id: Optional[str] = None
        
        # Handler ID
        self._seed_sync_tracking_handler_id: Optional[int] = None
        
        # Timer for periodic republishing
        self._republish_timer: Optional[QTimer] = None
        
        # Callbacks
        self._seed_synced_callbacks: list = []  # List of callbacks(seed: int)
        self._instance_connected_callbacks: list = []  # List of callbacks(client_id: str)
        self._sync_failed_callbacks: list = []  # List of callbacks(error: str)
    
    @property
    def seed_synced(self) -> bool:
        """Check if seed is synchronized"""
        return self._seed_synced
    
    @property
    def synced_seed_value(self) -> Optional[int]:
        """Get the synchronized seed value"""
        return self._synced_seed_value
    
    @property
    def connected_instances(self) -> Set[str]:
        """Get the set of connected instance client IDs"""
        return self._connected_instances.copy()
    
    def on_seed_synced(self, callback: Callable[[int], None]):
        """
        Register a callback to be called when seed is synchronized.
        
        Args:
            callback: Function(seed: int) called when seed is synchronized
        """
        if callback not in self._seed_synced_callbacks:
            self._seed_synced_callbacks.append(callback)
    
    def remove_seed_synced_callback(self, callback: Callable[[int], None]):
        """Remove a seed synced callback"""
        if callback in self._seed_synced_callbacks:
            self._seed_synced_callbacks.remove(callback)
    
    def on_instance_connected(self, callback: Callable[[str], None]):
        """
        Register a callback to be called when a new instance is detected.
        
        Args:
            callback: Function(client_id: str) called when instance is detected
        """
        if callback not in self._instance_connected_callbacks:
            self._instance_connected_callbacks.append(callback)
    
    def remove_instance_connected_callback(self, callback: Callable[[str], None]):
        """Remove an instance connected callback"""
        if callback in self._instance_connected_callbacks:
            self._instance_connected_callbacks.remove(callback)
    
    def on_sync_failed(self, callback: Callable[[str], None]):
        """
        Register a callback to be called when seed sync fails.
        
        Args:
            callback: Function(error: str) called when sync fails
        """
        if callback not in self._sync_failed_callbacks:
            self._sync_failed_callbacks.append(callback)
    
    def remove_sync_failed_callback(self, callback: Callable[[str], None]):
        """Remove a sync failed callback"""
        if callback in self._sync_failed_callbacks:
            self._sync_failed_callbacks.remove(callback)
    
    def _notify_seed_synced(self, seed: int):
        """Notify all callbacks that seed has been synchronized"""
        self.seed_synced_signal.emit(seed)
        for callback in self._seed_synced_callbacks:
            try:
                callback(seed)
            except Exception as e:
                print(f"[SGSeedSyncManager] Error in seed_synced callback: {e}")
                import traceback
                traceback.print_exc()
    
    def _notify_instance_connected(self, client_id: str):
        """Notify all callbacks that a new instance has been detected"""
        self.instance_connected_signal.emit(client_id)
        for callback in self._instance_connected_callbacks:
            try:
                callback(client_id)
            except Exception as e:
                print(f"[SGSeedSyncManager] Error in instance_connected callback: {e}")
                import traceback
                traceback.print_exc()
    
    def _notify_sync_failed(self, error: str):
        """Notify all callbacks that seed sync has failed"""
        self.sync_failed_signal.emit(error)
        for callback in self._sync_failed_callbacks:
            try:
                callback(error)
            except Exception as e:
                print(f"[SGSeedSyncManager] Error in sync_failed callback: {e}")
                import traceback
                traceback.print_exc()
    
    def sync_seed(self, session_id: str, shared_seed: Optional[int] = None, 
                  timeout: float = 2.0, initial_wait: float = 1.0,
                  client_id_callback: Optional[Callable[[str], None]] = None) -> Optional[int]:
        """
        Synchronize random seed across all instances.
        
        Args:
            session_id: Session identifier
            shared_seed: Optional seed to use. If None, first instance generates it.
            timeout: Maximum wait time in seconds for seed sync
            initial_wait: Time to wait before becoming leader (default: 1.0)
            client_id_callback: Optional callback function(client_id) called for each clientId seen
        
        Returns:
            Synchronized seed value, or None if sync failed
        """
        if not (self.mqtt_client and self.mqtt_client.is_connected()):
            error_msg = "MQTT client must be connected before syncing seed"
            self._notify_sync_failed(error_msg)
            return None
        
        if self._seed_synced:
            # Already synced, return existing value
            return self._synced_seed_value
        
        try:
            # Callback to track connected instances during seed sync
            def track_client_id(client_id):
                if not client_id:
                    return
                old_count = len(self._connected_instances)
                self._connected_instances.add(client_id)
                new_count = len(self._connected_instances)
                
                # Call external callback if provided
                if client_id_callback:
                    try:
                        client_id_callback(client_id)
                    except Exception as e:
                        print(f"[SGSeedSyncManager] Error in client_id_callback: {e}")
                
                # Notify if new instance detected
                if new_count != old_count:
                    self._notify_instance_connected(client_id)
            
            # Get seed sync topic
            session_topics = self.session_manager.getSessionTopics(session_id)
            seed_topic = session_topics[1]  # session_seed_sync
            
            # Synchronize seed using session_manager
            synced_seed = self.session_manager.syncSeed(
                session_id,
                shared_seed=shared_seed,
                timeout=timeout,
                initial_wait=initial_wait,
                client_id_callback=track_client_id
            )
            
            # Verify that seed sync actually succeeded
            if synced_seed is None:
                error_msg = "Seed synchronization returned None"
                self._notify_sync_failed(error_msg)
                return None
            
            # Store synchronized seed
            self._synced_seed_value = synced_seed
            self._seed_synced = True
            self._current_session_id = session_id
            
            # Apply seed immediately
            import random
            random.seed(synced_seed)
            
            # Notify callbacks
            self._notify_seed_synced(synced_seed)
            
            # Start tracking seed sync messages
            self._start_tracking(session_id)
            
            # Start periodic republishing
            self._start_republishing(session_id)
            
            return synced_seed
            
        except Exception as e:
            error_msg = f"Seed synchronization failed: {str(e)}"
            print(f"[SGSeedSyncManager] {error_msg}")
            import traceback
            traceback.print_exc()
            self._notify_sync_failed(error_msg)
            return None
    
    def _start_tracking(self, session_id: str):
        """
        Start tracking seed sync messages to detect new instances.
        
        Args:
            session_id: Session identifier
        """
        if not (self.mqtt_client and self.mqtt_client.is_connected()):
            return
        
        # Initialize MQTT Handler Manager if not provided
        if not self.mqtt_handler_manager:
            self.mqtt_handler_manager = SGMQTTHandlerManager(self.mqtt_client)
            self.mqtt_handler_manager.install()
        
        # Remove existing handler if any
        if self._seed_sync_tracking_handler_id is not None:
            self.mqtt_handler_manager.remove_handler(self._seed_sync_tracking_handler_id)
        
        # Get seed sync topic
        session_topics = self.session_manager.getSessionTopics(session_id)
        seed_topic = session_topics[1]  # session_seed_sync
        
        # Create handler function for seed sync tracking
        def seed_sync_tracking_handler(client, userdata, msg):
            try:
                msg_dict = json.loads(msg.payload.decode("utf-8"))
                client_id = msg_dict.get('clientId')
                
                if client_id:
                    old_count = len(self._connected_instances)
                    is_new_instance = client_id not in self._connected_instances
                    
                    # Only add if not already in set
                    if is_new_instance:
                        self._connected_instances.add(client_id)
                        # Notify if count changed
                        if len(self._connected_instances) != old_count:
                            self._notify_instance_connected(client_id)
                            
            except Exception as e:
                print(f"[SGSeedSyncManager] Error tracking instance: {e}")
                import traceback
                traceback.print_exc()
            # CRITICAL: Do NOT forward seed sync messages to other handlers
            # They are not game topics and will be ignored anyway
        
        # Add handler using SGMQTTHandlerManager
        # stop_propagation=True because we don't want to forward seed_sync messages
        self._seed_sync_tracking_handler_id = self.mqtt_handler_manager.add_topic_handler(
            topic=seed_topic,
            handler_func=seed_sync_tracking_handler,
            priority=HandlerPriority.HIGH,
            stop_propagation=True  # Don't forward seed_sync messages to other handlers
        )
    
    def _start_republishing(self, session_id: str, interval_ms: int = 3000):
        """
        Start periodic republishing of seed sync messages.
        
        Args:
            session_id: Session identifier
            interval_ms: Republish interval in milliseconds (default: 3000)
        """
        if not self._seed_synced or not self._synced_seed_value:
            return  # Don't start if seed not synced yet
        
        # Stop existing timer if any
        if self._republish_timer:
            self._republish_timer.stop()
            self._republish_timer = None
        
        # Store session_id for republishing
        self._current_session_id = session_id
        
        # Create timer for periodic republishing
        self._republish_timer = QTimer(self)
        self._republish_timer.timeout.connect(self._republish_seed_sync)
        self._republish_timer.start(interval_ms)
    
    def _republish_seed_sync(self, session_id: Optional[str] = None):
        """
        Republish seed sync message periodically to ensure new instances can detect us.
        
        Args:
            session_id: Optional session identifier (uses current if not provided)
        """
        if not self._seed_synced or not self._synced_seed_value:
            return  # Don't republish if seed not synced yet
        
        if not (self.mqtt_client and self.mqtt_client.is_connected()):
            return
        
        # Use provided session_id or current one
        if session_id is None:
            session_id = self._current_session_id
        
        if not session_id:
            return
        
        try:
            # Get seed sync topic
            session_topics = self.session_manager.getSessionTopics(session_id)
            seed_topic = session_topics[1]  # session_seed_sync
            
            # CRITICAL: Cooldown check to prevent infinite loops
            import time
            current_time = time.time()
            if (current_time - self._last_republish_time) < self._republish_cooldown:
                return  # Too soon since last republish, skip to prevent loops
            
            # Get client_id from model or session_manager
            client_id = None
            if self.model and hasattr(self.model, 'mqttManager') and hasattr(self.model.mqttManager, 'clientId'):
                client_id = self.model.mqttManager.clientId
            elif hasattr(self.session_manager, 'mqtt_manager') and hasattr(self.session_manager.mqtt_manager, 'clientId'):
                client_id = self.session_manager.mqtt_manager.clientId
            else:
                client_id = 'unknown'
            
            # Prepare seed sync message (include timestamp for debugging)
            from datetime import datetime
            seed_message = {
                'seed': self._synced_seed_value,
                'clientId': client_id,
                'is_leader': False,
                'timestamp': datetime.now().isoformat()
            }
            
            # Update last republish time
            self._last_republish_time = current_time
            
            # Publish seed sync message with retain flag
            self.mqtt_client.publish(seed_topic, json.dumps(seed_message), qos=1, retain=True)
            
        except Exception as e:
            print(f"[SGSeedSyncManager] Error republishing seed sync: {e}")
            import traceback
            traceback.print_exc()
    
    def stop_republishing(self):
        """Stop periodic republishing of seed sync messages"""
        if self._republish_timer:
            self._republish_timer.stop()
            self._republish_timer = None
    
    def stop_tracking(self):
        """Stop tracking seed sync messages"""
        if self.mqtt_handler_manager and self._seed_sync_tracking_handler_id is not None:
            self.mqtt_handler_manager.remove_handler(self._seed_sync_tracking_handler_id)
            self._seed_sync_tracking_handler_id = None
    
    def reset(self):
        """Reset seed sync state"""
        self._seed_synced = False
        self._synced_seed_value = None
        self._connected_instances.clear()
        self._last_republish_time = 0
        self._current_session_id = None
        self.stop_republishing()
        self.stop_tracking()

