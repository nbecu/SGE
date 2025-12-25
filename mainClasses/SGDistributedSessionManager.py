# --- Standard library imports ---
import json
import time
from datetime import datetime

# --- Third-party imports ---
from PyQt5.QtCore import QObject, pyqtSignal, QTimer


class SGDistributedSessionManager(QObject):
    """
    Manages session-level operations for distributed multiplayer games via MQTT.
    
    IMPORTANT: This class handles ONLY session management topics. It does NOT handle 
    game messages (game_gameAction_performed, game_nextTurn, game_execute_method), 
    which are handled by SGMQTTManager.
    
    MQTT Topics Handled:
    - {session_id}/session_player_registration - Player registration messages
    - {session_id}/session_seed_sync - Seed synchronization messages
    
    MQTT Topics NOT Handled (handled by SGMQTTManager):
    - {session_id}/game_gameAction_performed - Game actions
    - {session_id}/game_nextTurn - Next turn messages
    - {session_id}/game_execute_method - Method execution
    """
    
    # Centralized list of session topics (base names without prefixes)
    SESSION_TOPICS = ['player_registration', 'seed_sync', 'player_disconnect', 'game_start', 'instance_ready', 'player_reservation', 'all_players_selected']
    
    # Global topic for session discovery (no session_id prefix)
    DISCOVERY_TOPIC = 'session_discovery'
    
    # Signals for UI updates
    playerConnected = pyqtSignal(str)  # Emitted when a player connects
    playerDisconnected = pyqtSignal(str)  # Emitted when a player disconnects
    seedReceived = pyqtSignal(int)  # Emitted when seed is received
    
    def __init__(self, model, mqtt_manager):
        """
        Initialize Distributed Session Manager
        
        Args:
            model: Reference to the SGModel instance
            mqtt_manager: Reference to the SGMQTTManager instance
        """
        super().__init__()
        self.model = model
        self.mqtt_manager = mqtt_manager  # Reference to SGMQTTManager
        self.session_id = None
        self.connected_players = {}  # {player_name: client_id}
        self.seed_received = False
        self.synced_seed = None
        self.is_leader = False  # True if this instance generated the seed
        self._seed_adopted_and_published = False  # Track if we've already published after adopting seed (to prevent loops)
        
        # Save original message handler
        self._original_on_message = None
        
        # Session discovery state
        self.discovered_sessions = {}  # {session_id: {'timestamp': float, 'info': dict}}
        self.session_heartbeat_timer = None  # QTimer for heartbeat (initialized in _startSessionHeartbeat)
        self.session_discovery_handler = None  # Handler for discovery messages
        self._discovery_callback = None  # Callback for discovery updates
        self._pre_discovery_handler = None  # Handler before discovery was installed
        
        # Seed sync republishing timer (persists after dialog closes)
        self.seed_sync_republish_timer = None  # QTimer for republishing seed sync messages
        self.synced_seed_value = None  # Store synced seed value for republishing
        self._seed_republish_session_id = None  # Session ID for republishing
    
    @classmethod
    def getSessionTopics(cls, session_id):
        """
        Get full session topic names with session_ prefix and session prefix.
        
        Args:
            session_id (str): Session ID for topic isolation
            
        Returns:
            list: List of full topic names (e.g., ['{session_id}/session_player_registration', ...])
        """
        topics = []
        for base_topic in cls.SESSION_TOPICS:
            full_topic = f"session_{base_topic}"
            if session_id:
                full_topic = f"{session_id}/{full_topic}"
            topics.append(full_topic)
        return topics
    
    @classmethod
    def isSessionTopic(cls, topic, session_id):
        """
        Check if a topic is a session topic.
        
        Args:
            topic (str): Topic name to check
            session_id (str): Session ID for topic isolation
            
        Returns:
            bool: True if topic is a session topic, False otherwise
        """
        session_topics = cls.getSessionTopics(session_id)
        return topic in session_topics
    
    def registerPlayer(self, session_id, assigned_player_name, num_players_min, num_players_max):
        """
        Register this instance as a player in the session.
        
        IMPORTANT: Requires MQTT client to be already connected (via setMQTTProtocol()).
        
        Args:
            session_id (str): Session identifier
            assigned_player_name (str): Name of player assigned to this instance
            num_players_min (int): Minimum number of players required
            num_players_max (int): Maximum number of players allowed
        
        Returns:
            bool: True if registration successful
        
        Raises:
            ValueError: If player name is already registered in this session
        """
        if not self.mqtt_manager.client or not self.mqtt_manager.client.is_connected():
            raise ValueError("MQTT client must be connected before registering player")
        
        self.session_id = session_id
        
        # Subscribe to session_player_registration topic using centralized method
        session_topics = self.getSessionTopics(session_id)
        registration_topic_base = session_topics[0]  # session_player_registration
        disconnect_topic_base = session_topics[2]  # session_player_disconnect
        
        # Use a wildcard subscription to receive all player registrations and disconnections
        # Format: {session_id}/session_player_registration/{player_name}
        # Format: {session_id}/session_player_disconnect/{player_name}
        registration_topic_wildcard = f"{registration_topic_base}/+"
        registration_topic_own = f"{registration_topic_base}/{assigned_player_name}"
        disconnect_topic_wildcard = f"{disconnect_topic_base}/+"
        disconnect_topic_own = f"{disconnect_topic_base}/{assigned_player_name}"
        
        # Save original handler BEFORE installing our handler
        original_on_message = self.mqtt_manager.client.on_message
        
        # Diagnostic: track retained messages received
        retained_messages_received = []
        
        def registration_message_handler(client, userdata, msg):
            # Process session_player_registration messages (with or without player name suffix)
            if msg.topic.startswith(registration_topic_base):
                try:
                    msg_dict = json.loads(msg.payload.decode("utf-8"))
                    player_name = msg_dict.get('assigned_player_name')
                    client_id = msg_dict.get('clientId')
                    is_retained = msg.retain
                    
                    print(f"[SessionManager] registration_message_handler: Processing registration for {player_name} from {client_id[:8] if client_id else 'N/A'}... (retained={is_retained})")
                    
                    if is_retained:
                        retained_messages_received.append((player_name, client_id))
                    
                    if player_name and client_id:
                        # Update connected players cache
                        self.connected_players[player_name] = client_id
                        print(f"[SessionManager] Updated connected_players: {list(self.connected_players.keys())}")
                        # Emit signal if not our own registration
                        if client_id != self.mqtt_manager.clientId:
                            self.playerConnected.emit(player_name)
                except Exception as e:
                    print(f"Error processing player registration message: {e}")
                    import traceback
                    traceback.print_exc()
            # Process session_player_disconnect messages
            elif msg.topic.startswith(disconnect_topic_base):
                try:
                    msg_dict = json.loads(msg.payload.decode("utf-8"))
                    player_name = msg_dict.get('assigned_player_name')
                    client_id = msg_dict.get('clientId')
                    
                    if player_name and client_id:
                        # Remove from connected players cache
                        if player_name in self.connected_players:
                            del self.connected_players[player_name]
                            # Emit signal if not our own disconnection
                            if client_id != self.mqtt_manager.clientId:
                                self.playerDisconnected.emit(player_name)
                except Exception as e:
                    print(f"Error processing player disconnect message: {e}")
            # CRITICAL: Forward ALL other messages to original handler (which may include all_players_selected_handler)
            # This ensures that handlers installed after this one (like all_players_selected_handler) still receive messages
            else:
                if original_on_message:
                    original_on_message(client, userdata, msg)
        
        # Install handler BEFORE subscribing (to receive retained messages)
        # CRITICAL: This wraps the existing handler chain, preserving all handlers installed before this one
        self.mqtt_manager.client.on_message = registration_message_handler
        self._original_on_message = original_on_message
        
        # Subscribe to wildcard topics to receive all player registrations and disconnections
        self.mqtt_manager.client.subscribe(registration_topic_wildcard)
        self.mqtt_manager.client.subscribe(disconnect_topic_wildcard)
        
        # Store disconnect topic for later use in disconnect()
        self.disconnect_topic_own = disconnect_topic_own
        
        # Wait a moment for retained messages to be processed
        time.sleep(0.3)
        
        # Publish registration message with retain=True on player-specific topic
        registration_msg = {
            'clientId': self.mqtt_manager.clientId,
            'assigned_player_name': assigned_player_name,
            'num_players_min': num_players_min,
            'num_players_max': num_players_max,
            'timestamp': datetime.now().isoformat()
        }
        
        serialized_msg = json.dumps(registration_msg)
        # Use retain=True and qos=1 on player-specific topic so each player's registration is retained separately
        result = self.mqtt_manager.client.publish(registration_topic_own, serialized_msg, qos=1, retain=True)
        
        # Add self to connected players cache
        self.connected_players[assigned_player_name] = self.mqtt_manager.clientId
        
        return True
    
    def syncSeed(self, session_id, shared_seed=None, timeout=2, initial_wait=1.0, client_id_callback=None):
        """
        Synchronize random seed across all instances.
        
        IMPORTANT: Requires MQTT client to be already connected.
        Uses temporary message handler ONLY for session_seed_sync topic.
        
        CRITICAL: Resets _seed_adopted_and_published flag to allow new synchronization.
        Does NOT interfere with game message handling.
        
        Args:
            session_id (str): Session identifier
            shared_seed (int, optional): Seed to use. If None, first instance generates it.
            timeout (float): Maximum wait time in seconds for seed sync
            initial_wait (float): Time to wait before becoming leader (default: 1.0)
            client_id_callback (callable, optional): Callback function(client_id) called for each clientId seen in seed messages
        
        Returns:
            int: Synchronized seed value
        """
        if not self.mqtt_manager.client or not self.mqtt_manager.client.is_connected():
            raise ValueError("MQTT client must be connected before syncing seed")
        
        # Get session_seed_sync topic using centralized method
        session_topics = self.getSessionTopics(session_id)
        seed_topic = session_topics[1]  # session_seed_sync
        
        # Save original handler BEFORE installing our handler
        original_on_message = self.mqtt_manager.client.on_message
        
        # CRITICAL: Reset flag to allow new synchronization
        self._seed_adopted_and_published = False
        
        # Track when we received a seed from another instance (to delay handler restoration)
        seed_received_time = None
        
        def seed_message_handler(client, userdata, msg):
            nonlocal seed_received_time
            if msg.topic == seed_topic:
                # Process seed message ONLY
                try:
                    msg_dict = json.loads(msg.payload.decode("utf-8"))
                    seed_value = msg_dict['seed']
                    client_id = msg_dict['clientId']
                    
                    print(f"[SessionManager] Seed message received: client_id={client_id[:8]}..., seed={seed_value}, is_own={client_id == self.mqtt_manager.clientId}")
                    
                    # Call callback if provided (for tracking connected instances)
                    # This captures ALL clientIds seen, not just the first one
                    # CRITICAL: Call callback for ALL messages (retained and new) to ensure all instances are tracked
                    if client_id_callback and client_id:
                        try:
                            client_id_callback(client_id)
                        except Exception as e:
                            import traceback
                            traceback.print_exc()
                    
                    # If this is not our own message, use this seed
                    if client_id != self.mqtt_manager.clientId:
                        # CRITICAL: Only adopt and publish ONCE to prevent infinite loops
                        # If we've already adopted and published, skip to prevent re-publishing on every message
                        if not self._seed_adopted_and_published:
                            print(f"[SessionManager] Adopting seed from other instance: {seed_value}")
                            self.synced_seed = seed_value
                            self.seed_received = True
                            self.seedReceived.emit(self.synced_seed)
                            # Mark when we received the seed (don't restore handler immediately)
                            # This allows us to continue receiving retained messages
                            seed_received_time = time.time()
                            # CRITICAL: Publish our own seed message (with adopted seed) so other instances can detect us
                            # This is important for instance tracking - each instance must publish its presence
                            # BUT: Only publish ONCE to prevent infinite loops when multiple instances connect
                            seed_msg = {
                                'clientId': self.mqtt_manager.clientId,
                                'seed': seed_value,  # Use adopted seed
                                'is_leader': False,  # We're not the leader
                                'timestamp': datetime.now().isoformat()
                            }
                            serialized_msg = json.dumps(seed_msg)
                            self.mqtt_manager.client.publish(seed_topic, serialized_msg, qos=1, retain=True)
                            print(f"[SessionManager] Published own seed message (adopted seed) to {seed_topic}")
                            
                            # CRITICAL: Mark that we've adopted and published to prevent re-publishing
                            self._seed_adopted_and_published = True
                            
                            # CRITICAL: Store seed value (republishing will be started at end of syncSeed)
                            self.synced_seed_value = seed_value
                            # CRITICAL: Return immediately after setting seed_received
                            # This prevents the code from continuing to check if not self.seed_received
                            return
                        else:
                            # Seed already adopted and published - just update synced_seed if different
                            # (shouldn't happen, but just in case)
                            if self.synced_seed != seed_value:
                                print(f"[SessionManager] Seed already adopted, but received different seed. Updating from {self.synced_seed} to {seed_value}")
                                self.synced_seed = seed_value
                                self.synced_seed_value = seed_value
                            # Don't republish - we've already published once
                            return
                except Exception as e:
                    print(f"Error processing seed message: {e}")
            # CRITICAL: Do NOT forward other messages - they are handled by SGMQTTManager
            # The original handler will continue to handle game messages
        
        # Initialize seed_received BEFORE installing handler
        self.seed_received = False
        start_time = time.time()
        
        # Install temporary handler BEFORE subscribing (to receive retained messages)
        print(f"[SessionManager] Installing seed sync handler for topic: {seed_topic}")
        self.mqtt_manager.client.on_message = seed_message_handler
        
        # Subscribe AFTER handler is installed to receive any existing retained seed message
        self.mqtt_manager.client.subscribe(seed_topic)
        print(f"[SessionManager] Subscribed to {seed_topic}")
        
        # CRITICAL: Wait a moment for retained messages to be processed by MQTT client thread
        # This ensures we capture retained messages before checking seed_received
        # The handler will set self.seed_received = True if a retained message is received
        # Increased delay to ensure all retained messages are received (especially important for 3+ instances)
        time.sleep(0.5)
        
        # If shared_seed is provided, use it directly
        if shared_seed is not None:
            print(f"[SessionManager] Using provided shared_seed: {shared_seed}")
            self.synced_seed = shared_seed
            self.is_leader = True
            self.seed_received = True
            # Call callback for our own clientId
            if client_id_callback:
                try:
                    client_id_callback(self.mqtt_manager.clientId)
                except Exception:
                    pass
            # Publish seed as retained message for other instances
            seed_msg = {
                'clientId': self.mqtt_manager.clientId,
                'seed': shared_seed,
                'is_leader': True,
                'timestamp': datetime.now().isoformat()
            }
            serialized_msg = json.dumps(seed_msg)
            self.mqtt_manager.client.publish(seed_topic, serialized_msg, qos=1, retain=True)
            print(f"[SessionManager] Published seed message to {seed_topic}")
            
            # CRITICAL: Store seed value (republishing will be started at end of syncSeed)
            self.synced_seed_value = shared_seed
        else:
            # Wait for retained seed message (if leader already exists)
            # Use configurable initial_wait (default 1.0 second)
            # CRITICAL: Wait for retained messages to be processed by MQTT client thread
            # This ensures we capture retained messages before checking seed_received
            elapsed = time.time() - start_time
            while elapsed < initial_wait:
                if self.seed_received:
                    print(f"[SessionManager] Seed received during wait (elapsed: {elapsed:.2f}s), using: {self.synced_seed}")
                    break
                time.sleep(0.1)
                elapsed = time.time() - start_time
            
            # If no seed received after initial wait, become leader immediately
            if not self.seed_received:
                elapsed = time.time() - start_time
                print(f"[SessionManager] No seed received after {elapsed:.2f}s, becoming leader")
                import random
                self.synced_seed = random.randint(1, 1000000)
                self.is_leader = True
                self.seed_received = True
                print(f"[SessionManager] No seed received, becoming leader with seed: {self.synced_seed}")
                # Call callback for our own clientId
                if client_id_callback:
                    try:
                        client_id_callback(self.mqtt_manager.clientId)
                    except Exception:
                        pass
                # Publish seed as retained message
                seed_msg = {
                    'clientId': self.mqtt_manager.clientId,
                    'seed': self.synced_seed,
                    'is_leader': True,
                    'timestamp': datetime.now().isoformat()
                }
                serialized_msg = json.dumps(seed_msg)
                self.mqtt_manager.client.publish(seed_topic, serialized_msg, qos=1, retain=True)
                print(f"[SessionManager] Published seed message to {seed_topic}")
                
                # CRITICAL: Store seed value and start republishing timer
                self.synced_seed_value = self.synced_seed
                self._startSeedSyncRepublishing(session_id, self.synced_seed)
            else:
                # Continue waiting up to timeout if seed was received but not processed yet
                while time.time() - start_time < timeout:
                    if self.seed_received:
                        break
                    time.sleep(0.1)
            
            # Fallback if still no seed (should not happen)
            if not self.seed_received:
                import random
                self.synced_seed = random.randint(1, 1000000)
        
        # Wait a bit more after seed sync to capture all retained messages
        # This ensures we see all instances that have published their seed
        # CRITICAL: Increased wait time to ensure all retained messages are received
        # This is especially important when multiple instances are already connected
        if seed_received_time:
            # Wait up to 1.0 second after receiving seed to capture other retained messages
            # This gives more time for all retained messages to be delivered
            while time.time() - seed_received_time < 1.0:
                time.sleep(0.1)
        else:
            # If we're the leader, wait longer to capture any retained messages from other instances
            # Increased from 0.3s to 0.8s to ensure all retained messages are received
            time.sleep(0.8)
        
        # CRITICAL: Restore original handler before returning
        self.mqtt_manager.client.on_message = original_on_message
        
        # CRITICAL: Start republishing seed sync messages periodically
        # This ensures instances that connect later can detect us even after dialog closes
        # The timer persists after dialog closes, unlike the dialog's timer
        if self.synced_seed_value is None:
            self.synced_seed_value = self.synced_seed
        if self.synced_seed_value is not None:
            self._startSeedSyncRepublishing(session_id, self.synced_seed_value)
        
        return self.synced_seed
    
    def publishSession(self, session_id, num_players_min, num_players_max, model_name=None):
        """
        Publish session information to the global discovery topic.
        This allows other instances to discover and join this session.
        
        Args:
            session_id (str): Session ID
            num_players_min (int): Minimum number of players
            num_players_max (int): Maximum number of players
            model_name (str, optional): Name of the model/game
        """
        if not (self.mqtt_manager.client and self.mqtt_manager.client.is_connected()):
            return
        
        session_info = {
            'session_id': session_id,
            'clientId': self.mqtt_manager.clientId,
            'num_players_min': num_players_min,
            'num_players_max': num_players_max,
            'model_name': model_name or getattr(self.model, 'name', 'Unknown'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Publish on session-specific topic within discovery namespace
        # Format: session_discovery/{session_id}
        discovery_topic = f"{self.DISCOVERY_TOPIC}/{session_id}"
        serialized_msg = json.dumps(session_info)
        
        # Use retain=True so new subscribers receive the session info
        # Use qos=1 for reliability
        result = self.mqtt_manager.client.publish(discovery_topic, serialized_msg, qos=1, retain=True)
        print(f"[SessionManager] Published session discovery: {session_id} on topic {discovery_topic}, result: {result}")
        
        # Start heartbeat timer to keep session alive
        self._startSessionHeartbeat(session_id, num_players_min, num_players_max, model_name)
    
    def _startSessionHeartbeat(self, session_id, num_players_min, num_players_max, model_name=None):
        """Start periodic heartbeat to keep session discovery message fresh"""
        # Stop existing timer if any
        if hasattr(self, 'session_heartbeat_timer') and self.session_heartbeat_timer:
            self.session_heartbeat_timer.stop()
            self.session_heartbeat_timer = None
        
        def heartbeat():
            if (self.mqtt_manager.client and 
                self.mqtt_manager.client.is_connected() and
                session_id):
                self.publishSession(session_id, num_players_min, num_players_max, model_name)
        
        self.session_heartbeat_timer = QTimer()
        self.session_heartbeat_timer.timeout.connect(heartbeat)
        self.session_heartbeat_timer.start(5000)  # Heartbeat every 5 seconds
    
    def _startSeedSyncRepublishing(self, session_id, seed_value):
        """Start republishing seed sync messages periodically
        
        This ensures instances that connect later can detect us even after dialog closes.
        The timer persists after dialog closes, unlike the dialog's timer.
        
        Args:
            session_id (str): Session ID
            seed_value (int): Synchronized seed value to republish
        """
        # Stop existing timer if any
        if self.seed_sync_republish_timer:
            self.seed_sync_republish_timer.stop()
        
        # Store values for republishing
        self.synced_seed_value = seed_value
        self._seed_republish_session_id = session_id
        
        # Create timer that republishes seed sync message periodically
        def republish_seed_sync():
            if not (self.mqtt_manager.client and self.mqtt_manager.client.is_connected()):
                return
            
            if not self._seed_republish_session_id:
                return
            
            session_topics = self.getSessionTopics(self._seed_republish_session_id)
            seed_topic = session_topics[1]  # session_seed_sync
            
            seed_msg = {
                'clientId': self.mqtt_manager.clientId,
                'seed': self.synced_seed_value,
                'is_leader': self.is_leader,
                'timestamp': datetime.now().isoformat()
            }
            serialized_msg = json.dumps(seed_msg)
            self.mqtt_manager.client.publish(seed_topic, serialized_msg, qos=1, retain=True)
            print(f"[SessionManager] Republished seed sync message for instance {self.mqtt_manager.clientId[:8]}...")
        
        self.seed_sync_republish_timer = QTimer(self.model)
        self.seed_sync_republish_timer.timeout.connect(republish_seed_sync)
        self.seed_sync_republish_timer.start(3000)  # Republish every 3 seconds
        print(f"[SessionManager] Started seed sync republishing timer (persists after dialog closes)")
    
    def stopSeedSyncRepublishing(self):
        """Stop republishing seed sync messages"""
        if self.seed_sync_republish_timer:
            self.seed_sync_republish_timer.stop()
            self.seed_sync_republish_timer = None
            print(f"[SessionManager] Stopped seed sync republishing timer")
    
    def reservePlayer(self, session_id, player_name):
        """
        Reserve a player by publishing a reservation message.
        
        Args:
            session_id (str): Session identifier
            player_name (str): Name of player to reserve
        
        Returns:
            bool: True if reservation published successfully, False otherwise
        """
        if not (self.mqtt_manager.client and self.mqtt_manager.client.is_connected()):
            return False
        
        session_topics = self.getSessionTopics(session_id)
        reservation_topic_base = session_topics[5]  # session_player_reservation (index 5)
        reservation_topic = f"{reservation_topic_base}/{player_name}"
        
        reservation_msg = {
            'clientId': self.mqtt_manager.clientId,
            'player_name': player_name,
            'action': 'reserve',
            'timestamp': datetime.now().isoformat()
        }
        
        serialized_msg = json.dumps(reservation_msg)
        result = self.mqtt_manager.client.publish(reservation_topic, serialized_msg, qos=1, retain=True)
        
        print(f"[SessionManager] Published player reservation: {player_name} on {reservation_topic}")
        return result.rc == 0
    
    def releasePlayer(self, session_id, player_name):
        """
        Release a player reservation by publishing a release message.
        
        Args:
            session_id (str): Session identifier
            player_name (str): Name of player to release
        
        Returns:
            bool: True if release published successfully, False otherwise
        """
        if not (self.mqtt_manager.client and self.mqtt_manager.client.is_connected()):
            return False
        
        session_topics = self.getSessionTopics(session_id)
        reservation_topic_base = session_topics[5]  # session_player_reservation (index 5)
        reservation_topic = f"{reservation_topic_base}/{player_name}"
        
        release_msg = {
            'clientId': self.mqtt_manager.clientId,
            'player_name': player_name,
            'action': 'release',
            'timestamp': datetime.now().isoformat()
        }
        
        serialized_msg = json.dumps(release_msg)
        result = self.mqtt_manager.client.publish(reservation_topic, serialized_msg, qos=1, retain=True)
        
        print(f"[SessionManager] Published player release: {player_name} on {reservation_topic}")
        return result.rc == 0
    
    def subscribeToPlayerReservations(self, session_id, callback):
        """
        Subscribe to player reservation messages and call callback for each message.
        
        Args:
            session_id (str): Session identifier
            callback (callable): Function(client_id, player_name, action) called for each reservation message
        
        Returns:
            bool: True if subscription successful, False otherwise
        """
        if not (self.mqtt_manager.client and self.mqtt_manager.client.is_connected()):
            return False
        
        session_topics = self.getSessionTopics(session_id)
        reservation_topic_base = session_topics[5]  # session_player_reservation (index 5)
        reservation_topic_wildcard = f"{reservation_topic_base}/+"
        
        # Get current handler
        original_handler = self.mqtt_manager.client.on_message
        
        def reservation_message_handler(client, userdata, msg):
            # Debug: log all messages to see what's being received
            # Only log reservation-related topics to avoid spam
            if msg.topic.startswith(reservation_topic_base) or 'reservation' in msg.topic.lower():
                print(f"[SessionManager] reservation_message_handler called: topic={msg.topic}, handler={reservation_message_handler}")
            elif 'session_all_players_selected' in msg.topic:
                print(f"[SessionManager] reservation_message_handler called for all_players_selected: topic={msg.topic}, handler={reservation_message_handler}")
            
            # Process reservation messages
            if msg.topic.startswith(reservation_topic_base):
                try:
                    # Log all reservation messages (including retained)
                    is_retained = msg.retain
                    msg_dict = json.loads(msg.payload.decode("utf-8"))
                    client_id = msg_dict.get('clientId')
                    player_name = msg_dict.get('player_name')
                    action = msg_dict.get('action')
                    
                    print(f"[SessionManager] Reservation message received: topic={msg.topic}, action={action}, player={player_name}, client={client_id[:8] if client_id else 'N/A'}..., retained={is_retained}, our_client_id={self.mqtt_manager.clientId[:8] if self.mqtt_manager.clientId else 'N/A'}..., handler={reservation_message_handler}")
                    
                    if client_id and player_name and action:
                        # Call callback
                        if callback:
                            try:
                                print(f"[SessionManager] Calling reservation callback for {player_name}")
                                callback(client_id, player_name, action)
                                print(f"[SessionManager] Reservation callback completed for {player_name}")
                            except Exception as e:
                                print(f"[SessionManager] Error in reservation callback: {e}")
                                import traceback
                                traceback.print_exc()
                        else:
                            print(f"[SessionManager] WARNING: No callback provided for reservation message")
                    else:
                        print(f"[SessionManager] WARNING: Invalid reservation message - missing fields: client_id={client_id}, player_name={player_name}, action={action}")
                except Exception as e:
                    print(f"[SessionManager] Error processing reservation message: {e}")
                    import traceback
                    traceback.print_exc()
                # Don't forward reservation messages
                return
            
            # Forward other messages to original handler
            # NOTE: original_handler was the handler active BEFORE reservation handler was installed
            # But after all_players_selected_handler is installed, the chain should be:
            # all_players_selected_handler -> reservation_message_handler -> original_handler
            # So we forward to original_handler, which is correct
            if original_handler:
                if 'session_all_players_selected' in msg.topic:
                    print(f"[SessionManager] Forwarding all_players_selected message to original handler: topic={msg.topic}, original_handler={original_handler}")
                print(f"[SessionManager] Forwarding non-reservation message to original handler: topic={msg.topic}")
                original_handler(client, userdata, msg)
            else:
                print(f"[SessionManager] WARNING: No original handler to forward message: topic={msg.topic}")
        
        # Install handler BEFORE subscribing (to receive retained messages)
        # CRITICAL: Save the current handler to preserve the chain
        previous_handler = self.mqtt_manager.client.on_message
        self.mqtt_manager.client.on_message = reservation_message_handler
        self._player_reservation_handler = reservation_message_handler
        self._previous_handler_before_reservations = previous_handler  # Store for debugging
        
        print(f"[SessionManager] Installing reservation handler. Previous handler: {previous_handler}")
        
        # Subscribe to wildcard topic
        result = self.mqtt_manager.client.subscribe(reservation_topic_wildcard, qos=1)
        print(f"[SessionManager] Subscribed to player reservations: {reservation_topic_wildcard}, result: {result}")
        print(f"[SessionManager] Handler after subscription: {self.mqtt_manager.client.on_message}")
        
        # Check subscription result
        if isinstance(result, tuple):
            rc, mid = result
            success = rc == 0  # MQTT_ERR_SUCCESS is 0
            print(f"[SessionManager] Subscription result: rc={rc}, mid={mid}, success={success}")
        else:
            success = False
            print(f"[SessionManager] WARNING: Unexpected subscription result type: {result}")
        
        # Wait a moment for retained messages to be received
        # Increased delay to ensure retained messages are received
        print(f"[SessionManager] Waiting for retained reservation messages...")
        time.sleep(0.5)
        print(f"[SessionManager] Finished waiting for retained messages")
        
        return success
    
    def stopSessionHeartbeat(self):
        """Stop the session heartbeat timer"""
        if hasattr(self, 'session_heartbeat_timer') and self.session_heartbeat_timer:
            self.session_heartbeat_timer.stop()
            self.session_heartbeat_timer = None
    
    def discoverSessions(self, callback=None):
        """
        Subscribe to session discovery topic and discover available sessions.
        
        Args:
            callback (callable, optional): Callback function called when sessions are discovered.
                Signature: callback(sessions_dict) where sessions_dict is {session_id: session_info}
        """
        if not (self.mqtt_manager.client and self.mqtt_manager.client.is_connected()):
            return
        
        # Subscribe to wildcard topic to receive all session discovery messages
        discovery_topic_wildcard = f"{self.DISCOVERY_TOPIC}/+"
        
        # Store callback
        self._discovery_callback = callback
        
        # Get current handler (might be seed tracking wrapper or original handler)
        current_handler = self.mqtt_manager.client.on_message
        print(f"[SessionManager] Current handler before discovery: {current_handler}")
        
        def process_discovery_message(client, userdata, msg):
            """Process a discovery message"""
            print(f"[SessionManager] Received discovery message on topic: {msg.topic}")
            try:
                msg_dict = json.loads(msg.payload.decode("utf-8"))
                session_id = msg_dict.get('session_id')
                print(f"[SessionManager] Processing discovery message for session: {session_id}")
                if session_id:
                    # Check if this is a retained message with old timestamp
                    # Retained messages contain timestamp as ISO string in msg_dict
                    msg_timestamp_iso = msg_dict.get('timestamp')
                    current_time = time.time()
                    
                    # If timestamp is in ISO format, check if it's expired
                    # For retained messages, we need to check the original timestamp
                    is_expired = False
                    if msg_timestamp_iso:
                        try:
                            # Parse ISO timestamp to datetime, then to Unix timestamp
                            # Handle different ISO formats
                            timestamp_str = str(msg_timestamp_iso)
                            if 'Z' in timestamp_str:
                                timestamp_str = timestamp_str.replace('Z', '+00:00')
                            elif '+' not in timestamp_str and '-' in timestamp_str[-6:]:
                                # Already has timezone
                                pass
                            else:
                                # No timezone, assume local time
                                pass
                            
                            msg_datetime = datetime.fromisoformat(timestamp_str)
                            msg_timestamp_unix = msg_datetime.timestamp()
                            # Check if message is older than 15 seconds
                            age_seconds = current_time - msg_timestamp_unix
                            if age_seconds > 15.0:
                                is_expired = True
                                print(f"[SessionManager] Retained message for {session_id} is expired (age: {age_seconds:.1f}s)")
                        except (ValueError, AttributeError, TypeError) as e:
                            # If parsing fails, treat as new message (not expired)
                            print(f"[SessionManager] Could not parse timestamp '{msg_timestamp_iso}': {e}, treating as new message")
                            pass
                    
                    # Only add session if it's not expired
                    if not is_expired:
                        # Update discovered sessions cache with current timestamp
                        self.discovered_sessions[session_id] = {
                            'timestamp': current_time,  # Use current time for active sessions
                            'info': msg_dict
                        }
                        print(f"[SessionManager] Added session {session_id} to discovered sessions. Total: {len(self.discovered_sessions)}")
                    else:
                        print(f"[SessionManager] Skipping expired session {session_id} from retained message")
                    
                    # Clean expired sessions (older than 15 seconds) from cache
                    expired_sessions = [
                        sid for sid, data in self.discovered_sessions.items()
                        if current_time - data['timestamp'] > 15.0
                    ]
                    for sid in expired_sessions:
                        del self.discovered_sessions[sid]
                        print(f"[SessionManager] Removed expired session: {sid}")
                    
                    # Call callback if provided
                    if self._discovery_callback:
                        try:
                            print(f"[SessionManager] Calling discovery callback with {len(self.discovered_sessions)} sessions")
                            self._discovery_callback(self.discovered_sessions.copy())
                        except Exception as e:
                            print(f"[SessionManager] Error in discovery callback: {e}")
                            import traceback
                            traceback.print_exc()
            except Exception as e:
                print(f"[SessionManager] Error processing discovery message: {e}")
                import traceback
                traceback.print_exc()
        
        # Install handler - wrap existing handler instead of replacing it
        # This allows discovery to coexist with other handlers (like seed tracking)
        def wrapped_discovery_handler(client, userdata, msg):
            # First, handle discovery messages
            if msg.topic.startswith(f"{self.DISCOVERY_TOPIC}/"):
                # Process discovery message
                process_discovery_message(client, userdata, msg)
                # Don't forward discovery messages - they're handled here
                return
            
            # Forward other messages to current handler
            if current_handler:
                current_handler(client, userdata, msg)
        
        # Store reference to handler that existed before discovery
        self._pre_discovery_handler = current_handler
        
        # Install wrapped handler
        self.session_discovery_handler = wrapped_discovery_handler
        self.mqtt_manager.client.on_message = wrapped_discovery_handler
        print(f"[SessionManager] Installed discovery handler wrapper")
        
        # Subscribe to discovery topic
        self.mqtt_manager.client.subscribe(discovery_topic_wildcard, qos=1)
        print(f"[SessionManager] Subscribed to session discovery: {discovery_topic_wildcard}")
        
        # Wait a moment for retained messages to be received
        time.sleep(0.3)
        
        # Clean expired sessions immediately after receiving retained messages
        # This ensures only active sessions are shown by default
        current_time = time.time()
        expired_sessions = [
            sid for sid, data in self.discovered_sessions.items()
            if current_time - data['timestamp'] > 15.0
        ]
        for sid in expired_sessions:
            del self.discovered_sessions[sid]
            print(f"[SessionManager] Removed expired session on initial subscription: {sid}")
        
        # Trigger callback with initial discovered sessions (after cleaning)
        if self._discovery_callback:
            try:
                print(f"[SessionManager] Triggering initial callback with {len(self.discovered_sessions)} active sessions")
                self._discovery_callback(self.discovered_sessions.copy())
            except Exception as e:
                print(f"[SessionManager] Error in initial discovery callback: {e}")
                import traceback
                traceback.print_exc()
    
    def stopSessionDiscovery(self):
        """Stop session discovery and restore original message handler"""
        if self.session_discovery_handler:
            # Restore the handler that existed before discovery was installed
            if hasattr(self, '_pre_discovery_handler') and self._pre_discovery_handler:
                self.mqtt_manager.client.on_message = self._pre_discovery_handler
            self.session_discovery_handler = None
            self._discovery_callback = None
            self._pre_discovery_handler = None
    
    def getConnectedPlayers(self, session_id):
        """
        Get list of connected players in the session.
        
        Returns:
            list: List of player names (str) that are currently connected
        
        Note: Maintains local cache updated via MQTT messages.
        """
        return list(self.connected_players.keys())
    
    def isPlayerNameAvailable(self, session_id, player_name):
        """
        Check if a player name is available (not already connected).
        
        Returns:
            bool: True if player name is available, False if already taken
        """
        return player_name not in self.connected_players
    
    def waitForPlayers(self, session_id, num_players_min, num_players_max, timeout=30):
        """
        Wait for sufficient players to connect (within range).
        
        Returns:
            bool: True if number of connected players is within range, False if timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            num_connected = len(self.connected_players)
            if num_players_min <= num_connected <= num_players_max:
                return True
            time.sleep(0.5)
        return False
    
    def disconnect(self):
        """Disconnect from session (stop timer, clear cache, publish disconnect message)"""
        # Stop seed sync republishing
        self.stopSeedSyncRepublishing()
        
        # Publish disconnect message before clearing cache
        if hasattr(self, 'disconnect_topic_own') and self.disconnect_topic_own:
            # Get assigned player name from connected_players (find our own entry)
            assigned_player_name = None
            for player_name, client_id in self.connected_players.items():
                if client_id == self.mqtt_manager.clientId:
                    assigned_player_name = player_name
                    break
            
            if assigned_player_name and self.mqtt_manager.client and self.mqtt_manager.client.is_connected():
                disconnect_msg = {
                    'clientId': self.mqtt_manager.clientId,
                    'assigned_player_name': assigned_player_name,
                    'timestamp': datetime.now().isoformat()
                }
                serialized_msg = json.dumps(disconnect_msg)
                # Publish disconnect message with retain=False (one-time message)
                self.mqtt_manager.client.publish(self.disconnect_topic_own, serialized_msg, qos=1, retain=False)
        
        # Restore original handler if it was changed
        if self._original_on_message and self.mqtt_manager.client:
            self.mqtt_manager.client.on_message = self._original_on_message
        
        self.connected_players.clear()
        self.seed_received = False
        self.synced_seed = None
        self.is_leader = False
