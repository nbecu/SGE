# --- Standard library imports ---
import json
import time
from datetime import datetime

# --- Third-party imports ---
from PyQt5.QtCore import QObject, pyqtSignal


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
    SESSION_TOPICS = ['player_registration', 'seed_sync', 'player_disconnect']
    
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
        
        # Save original message handler
        self._original_on_message = None
    
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
        
        def registration_message_handler(client, userdata, msg):
            # Process session_player_registration messages (with or without player name suffix)
            if msg.topic.startswith(registration_topic_base):
                try:
                    msg_dict = json.loads(msg.payload.decode("utf-8"))
                    player_name = msg_dict.get('assigned_player_name')
                    client_id = msg_dict.get('clientId')
                    
                    if player_name and client_id:
                        # Update connected players cache
                        self.connected_players[player_name] = client_id
                        # Emit signal if not our own registration
                        if client_id != self.mqtt_manager.clientId:
                            self.playerConnected.emit(player_name)
                except Exception as e:
                    print(f"Error processing player registration message: {e}")
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
            # CRITICAL: Forward ONLY game topics to original handler
            elif self.mqtt_manager.isGameTopic(msg.topic, session_id):
                if original_on_message:
                    original_on_message(client, userdata, msg)
            # Ignore other session topics (like session_seed_sync) - they have their own handlers
        
        # Install handler BEFORE subscribing (to receive retained messages)
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
        self.mqtt_manager.client.publish(registration_topic_own, serialized_msg, qos=1, retain=True)
        
        # Add self to connected players cache
        self.connected_players[assigned_player_name] = self.mqtt_manager.clientId
        
        return True
    
    def syncSeed(self, session_id, shared_seed=None, timeout=2, initial_wait=1.0, client_id_callback=None):
        """
        Synchronize random seed across all instances.
        
        IMPORTANT: Requires MQTT client to be already connected.
        Uses temporary message handler ONLY for session_seed_sync topic.
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
                    
                    # Call callback if provided (for tracking connected instances)
                    # This captures ALL clientIds seen, not just the first one
                    if client_id_callback and client_id:
                        try:
                            client_id_callback(client_id)
                        except Exception:
                            pass  # Ignore callback errors
                    
                    # If this is not our own message, use this seed
                    if client_id != self.mqtt_manager.clientId:
                        self.synced_seed = seed_value
                        self.seed_received = True
                        self.seedReceived.emit(self.synced_seed)
                        # Mark when we received the seed (don't restore handler immediately)
                        # This allows us to continue receiving retained messages
                        seed_received_time = time.time()
                except Exception as e:
                    print(f"Error processing seed message: {e}")
            # CRITICAL: Do NOT forward other messages - they are handled by SGMQTTManager
            # The original handler will continue to handle game messages
        
        # Install temporary handler BEFORE subscribing (to receive retained messages)
        self.mqtt_manager.client.on_message = seed_message_handler
        
        # Subscribe AFTER handler is installed to receive any existing retained seed message
        self.mqtt_manager.client.subscribe(seed_topic)
        
        # Wait a moment for retained messages to be processed by MQTT client thread
        # This ensures we capture all retained messages before proceeding
        time.sleep(0.2)
        
        # Wait for retained messages to be processed by MQTT client thread
        self.seed_received = False
        start_time = time.time()
        
        # If shared_seed is provided, use it directly
        if shared_seed is not None:
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
        else:
            # Wait for retained seed message (if leader already exists)
            # Use configurable initial_wait (default 1.0 second)
            while time.time() - start_time < initial_wait:
                if self.seed_received:
                    break
                time.sleep(0.1)
            
            # If no seed received after initial wait, become leader immediately
            if not self.seed_received:
                import random
                self.synced_seed = random.randint(1, 1000000)
                self.is_leader = True
                self.seed_received = True
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
        if seed_received_time:
            # Wait up to 0.5 seconds after receiving seed to capture other retained messages
            while time.time() - seed_received_time < 0.5:
                time.sleep(0.1)
        else:
            # If we're the leader, wait a bit to capture any retained messages from other instances
            time.sleep(0.3)
        
        # CRITICAL: Restore original handler before returning
        self.mqtt_manager.client.on_message = original_on_message
        
        return self.synced_seed
    
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
