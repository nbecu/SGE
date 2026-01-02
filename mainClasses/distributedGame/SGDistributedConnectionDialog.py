# --- Standard library imports ---
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# --- Project imports ---
from mainClasses.distributedGame.SGDistributedSession import SGDistributedSession
from mainClasses.distributedGame.SGMQTTHandlerManager import SGMQTTHandlerManager, HandlerPriority
from mainClasses.distributedGame.SGConnectionStateManager import SGConnectionStateManager, ConnectionState


class SGDistributedConnectionDialog(QDialog):
    """
    Dialog for MQTT connection and seed synchronization with improved UX.
    
    States:
    - CONFIGURATION: Initial state, user can configure session
    - CONNECTING: Connecting to broker and syncing seed
    - WAITING: Waiting for required number of instances
    - READY: All instances connected, ready to start
    
    Note: Player selection happens later in completeDistributedGameSetup()
    """
    
    # Dialog states (kept for backward compatibility, use ConnectionState enum instead)
    STATE_SETUP = "setup"
    STATE_CONNECTING = "connecting"
    STATE_WAITING = "waiting"
    STATE_READY_MIN = "ready_min"  # Minimum reached, manual start available (creator only)
    STATE_READY_MAX = "ready_max"  # Maximum reached, auto-countdown triggers
    STATE_READY = "ready"  # Legacy state (kept for backward compatibility)
    
    # Map string states to ConnectionState enum for compatibility
    _STATE_MAP = {
        "setup": ConnectionState.SETUP,
        "connecting": ConnectionState.CONNECTING,
        "waiting": ConnectionState.WAITING,
        "ready_min": ConnectionState.READY_MIN,
        "ready_max": ConnectionState.READY_MAX,
        "ready": ConnectionState.READY,
    }
    
    def __init__(self, parent, config, model, session_manager):
        """
        Initialize dialog.
        
        Args:
            parent: Parent widget (SGModel)
            config: SGDistributedGameConfig object
            model: SGModel instance
            session_manager: SGDistributedSessionManager instance
        """
        super().__init__(parent)
        self.config = config
        self.model = model
        self.session_manager = session_manager
        self.connection_status = "Not connected"
        self.seed_synced = False
        self.synced_seed_value = None
        self.connected_instances = set()  # Set of clientIds connected to this session (via seed sync)
        self.ready_instances = set()  # Set of clientIds that have completed seed sync and subscribed to game_start
        self.connected_instances_snapshot = None  # Snapshot of connected instances when dialog becomes ready
        self._last_republish_time = 0  # Timestamp of last seed sync republish (to prevent loops)
        self._republish_cooldown = 2.0  # Minimum seconds between republishes (to prevent loops)
        
        # Phase 2: State management via SGConnectionStateManager
        self.state_manager = SGConnectionStateManager(initial_state=ConnectionState.SETUP)
        self.state_manager.on_state_changed(self._onStateChanged)
        # current_state is now a property that maps to state_manager.current_state.value
        
        self.auto_start_countdown = None  # Countdown timer for auto-start (3, 2, 1...)
        self.auto_start_timer = None  # QTimer for countdown
        self.available_sessions = {}  # Dict of available sessions: {session_id: session_info}
        self.session_players_cache = {}  # Cache of registered players per session: {session_id: set of player_names}
        self.session_instances_cache = {}  # Cache of connected instances per session: {session_id: set of client_ids}
        self.session_discovery_handler = None  # Handler for session discovery
        self._should_start_discovery_on_connect = False  # Flag to start discovery automatically after connection
        self._connection_in_progress = False  # Flag to prevent multiple simultaneous connection attempts
        self._selected_session_id = None
        
        # Phase 2: Session state as single source of truth
        self.session_state = None  # SGDistributedSession instance for current session
        self.session_state_heartbeat_timer = None  # QTimer for creator heartbeat
        self.session_state_creator_check_timer = None  # QTimer for checking creator disconnection
        self._session_joined_at = None  # Timestamp when we joined the session (to track if we've received heartbeat since joining)
        self.session_states_cache = {}  # Cache of session states for discovered sessions: {session_id: SGDistributedSession}  # Session ID selected by user in join mode
        self._temporary_session_id = None  # Temporary session_id used for connection (not a selected session)
        self._cleaning_up = False  # Flag to prevent MQTT callbacks during cleanup
        self._handler_before_game_start = None  # Store handler before installing game_start_handler
        
        # MQTT Handler Manager for centralized handler management (refactoring)
        self._mqtt_handler_manager = None  # Will be initialized when MQTT client is available (SGMQTTHandlerManager instance)
        self._game_start_handler_id = None  # Handler ID for game start handler
        self._seed_sync_tracking_handler_id = None  # Handler ID for seed sync tracking
        self._player_registration_tracking_handler_id = None  # Handler ID for player registration tracking
        self._player_disconnect_tracking_handler_id = None  # Handler ID for player disconnect tracking
        self._instance_ready_handler_id = None  # Handler ID for instance ready tracking
        self._instance_ready_disconnect_handler_id = None  # Handler ID for disconnect tracking in instance ready handler
        self._session_player_registration_tracker_handler_id = None  # Handler ID for session player registration tracker (discovered sessions)
        self._session_state_discovery_handler_id = None  # Handler ID for session_state updates for discovered sessions
        self._session_discovery_handler_id = None  # Handler ID for session discovery messages
        self._session_state_connected_handler_id = None  # Handler ID for session_state updates for connected session
        
        self.setWindowTitle("Connect to Distributed Game")
        self.setModal(True)
        self.resize(500, 400)  # Increased height to accommodate connected players section
        
        self._buildUI()
        self._setupTimers()
        self._connectSignals()
        
        # Initialize session_id if not set
        if not self.config.session_id:
            self.config.generate_session_id()
            self.session_id_edit.setText(self.config.session_id)
        
        # Set is_session_creator flag based on initial mode selection
        if self.create_new_radio.isChecked():
            self.config.is_session_creator = True
        else:
            self.config.is_session_creator = False
    
    def _buildUI(self):
        """Build the user interface"""
        layout = QVBoxLayout()
        
        # Title
        model_name = self.model.name or self.model.windowTitle_prefix or "Game"
        title_label = QLabel(f"Connect to Distributed Game: {model_name}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Mode selection (Create new session vs Join existing)
        mode_group = QGroupBox("Connection Mode")
        mode_layout = QVBoxLayout()
        
        self.create_new_radio = QRadioButton("Create new session")
        self.create_new_radio.setChecked(True)
        self.create_new_radio.toggled.connect(self._onModeChanged)
        mode_layout.addWidget(self.create_new_radio)
        
        self.join_existing_radio = QRadioButton("Join existing session")
        self.join_existing_radio.toggled.connect(self._onModeChanged)
        mode_layout.addWidget(self.join_existing_radio)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # Info label (contextual message)
        self.info_label = QLabel("Create a new distributed game session.")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.info_label)
        
        # Available Sessions List (for join mode)
        self.sessions_group = QGroupBox()  # No title, we'll create custom title
        sessions_layout = QVBoxLayout()
        
        # Custom title row with label and refresh button
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 5)  # Small margin at bottom
        
        # Title label (styled like QGroupBox title)
        title_label = QLabel("Available Sessions")
        title_font = QFont()
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_row.addWidget(title_label)
        title_row.addStretch()
        
        # Refresh button (discrete, icon only, placed on the right of title)
        self.refresh_sessions_btn = QPushButton()
        self.refresh_sessions_btn.setText("🔄")  # Refresh icon
        self.refresh_sessions_btn.setToolTip("Refresh sessions list")
        self.refresh_sessions_btn.setMaximumWidth(30)  # Same size as Copy button
        self.refresh_sessions_btn.setMaximumHeight(24)
        self.refresh_sessions_btn.setStyleSheet("color: #888; font-size: 12px; border: none; background: transparent; padding: 2px;")
        self.refresh_sessions_btn.clicked.connect(lambda: self._refreshAvailableSessions(force=True))
        title_row.addWidget(self.refresh_sessions_btn)
        
        sessions_layout.addLayout(title_row)
        
        self.sessions_list = QListWidget()
        self.sessions_list.setStyleSheet("QListWidget { border: 1px solid #ccc; border-radius: 3px; max-height: 150px; }")
        # Single click selects session, double-click is optional shortcut
        self.sessions_list.itemClicked.connect(self._onSessionClicked)
        self.sessions_list.itemDoubleClicked.connect(self._onSessionDoubleClicked)
        sessions_layout.addWidget(self.sessions_list)
        
        self.sessions_group.setLayout(sessions_layout)
        self.sessions_group.hide()  # Hidden by default (shown in join mode)
        layout.addWidget(self.sessions_group)
        
        # Session ID Section
        self.session_group = QGroupBox("Session ID")
        session_layout = QVBoxLayout()
        
        session_input_layout = QHBoxLayout()
        self.session_id_edit = QLineEdit()
        self.session_id_edit.setText(self.config.session_id or "")
        self.session_id_edit.setPlaceholderText("Enter or generate session ID")
        session_input_layout.addWidget(self.session_id_edit)
        
        self.copy_session_btn = QPushButton()
        # Use Unicode clipboard symbol as icon
        self.copy_session_btn.setText("📋")  # Clipboard emoji
        self.copy_session_btn.setToolTip("Copy Session ID to clipboard")
        # Reduce button size by 60% (keep 40% of default size)
        # Default button width is typically ~75px, so 40% = ~30px
        self.copy_session_btn.setMaximumWidth(30)
        self.copy_session_btn.setMaximumHeight(24)  # Keep reasonable height
        self.copy_session_btn.clicked.connect(self._copySessionId)
        session_input_layout.addWidget(self.copy_session_btn)
        
        session_layout.addLayout(session_input_layout)
        
        self.session_group.setLayout(session_layout)
        layout.addWidget(self.session_group)
        
        # Number of Players Display
        num_players_label = QLabel()
        if isinstance(self.config.num_players, int):
            num_players_text = f"Number of players: {self.config.num_players}"
        else:
            num_players_text = f"Number of players: {self.config.num_players_min}-{self.config.num_players_max}"
        num_players_label.setText(num_players_text)
        layout.addWidget(num_players_label)
        
        # Connection Status
        connection_status_group = QVBoxLayout()
        connection_status_group.setSpacing(2)
        
        self.status_label = QLabel(f"Connection Status: {self.connection_status}")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px;")
        connection_status_group.addWidget(self.status_label)
        
        # MQTT Broker Info (discrete, integrated in Connection Status section)
        self.broker_info_label = QLabel(f"MQTT Broker: {self.config.broker_host}:{self.config.broker_port}")
        self.broker_info_label.setStyleSheet("color: #888; font-size: 9px; padding: 2px 5px;")
        connection_status_group.addWidget(self.broker_info_label)
        
        layout.addLayout(connection_status_group)
        
        # Session Status Section (combines Seed Status and Connected Instances)
        instances_group = QGroupBox("Session Status")
        instances_layout = QVBoxLayout()
        
        # Seed Status line
        self.seed_status_label = QLabel("Seed: Not synchronized")
        self.seed_status_label.setStyleSheet("padding: 5px; background-color: #fff8dc; border-radius: 3px;")
        instances_layout.addWidget(self.seed_status_label)
        
        # Connected Instances line
        self.connected_instances_label = QLabel("Instances: No instances connected yet")
        self.connected_instances_label.setStyleSheet("padding: 5px; color: #666;")
        instances_layout.addWidget(self.connected_instances_label)
        
        # Countdown label for auto-start
        self.countdown_label = QLabel("")
        self.countdown_label.setStyleSheet("padding: 5px; color: #27ae60; font-weight: bold; font-size: 14px;")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        instances_layout.addWidget(self.countdown_label)
        self.countdown_label.hide()  # Hidden by default
        
        instances_group.setLayout(instances_layout)
        layout.addWidget(instances_group)
        
        # Spacer
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.hide()  # Hide by default, only show when connected
        button_layout.addWidget(self.cancel_button)
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self._onConnect)
        button_layout.addWidget(self.connect_button)
        
        self.start_button = QPushButton("Start Now")
        self.start_button.clicked.connect(self._onStartNowClicked)
        self.start_button.setEnabled(False)  # Disabled until ready
        self.start_button.hide()  # Hidden by default, shown when ready
        button_layout.addWidget(self.start_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _setupTimers(self):
        """Setup timers for periodic updates"""
        # Timer to check seed sync status
        self.seed_check_timer = QTimer(self)
        self.seed_check_timer.timeout.connect(self._checkSeedSync)
        self.seed_check_timer.start(500)  # Check every 500ms
        
        # Timer to update connected instances list
        self.instances_update_timer = QTimer(self)
        self.instances_update_timer.timeout.connect(self._updateConnectedInstances)
        self.instances_update_timer.start(1000)  # Update every 1 second
        
        # Timer to periodically update sessions list (to catch missed instance_ready messages)
        # This ensures the display stays accurate even if some MQTT messages are missed
        # CRITICAL: Also force re-subscription periodically to ensure we receive retained messages
        # Use non-blocking approach with QTimer.singleShot instead of time.sleep
        def periodic_sessions_update():
            """Periodically update sessions list and force re-subscription to get retained messages"""
            # Force re-subscription to ensure we receive any missed retained messages
            if self.available_sessions and self.model.mqttManager.client and self.model.mqttManager.client.is_connected():
                # Force unsubscribe/resubscribe to get retained messages
                for session_id in self.available_sessions.keys():
                    instance_ready_topic_wildcard = f"{session_id}/session_instance_ready/+"
                    try:
                        self.model.mqttManager.client.unsubscribe(instance_ready_topic_wildcard)
                    except Exception:
                        pass
                
                # Use QTimer.singleShot for non-blocking delays
                def resubscribe_after_delay():
                    for session_id in self.available_sessions.keys():
                        instance_ready_topic_wildcard = f"{session_id}/session_instance_ready/+"
                        self.model.mqttManager.client.subscribe(instance_ready_topic_wildcard, qos=1)
                    
                    # Wait for retained messages to be received by the handler
                    # The handler will update the cache, then we update the list
                    def update_list_after_retained_messages():
                        self._updateSessionsList()
                    
                    QTimer.singleShot(800, update_list_after_retained_messages)
                
                QTimer.singleShot(100, resubscribe_after_delay)
            else:
                # Update the list even if not connected (will show empty/current state)
                self._updateSessionsList()
        
        self.sessions_list_update_timer = QTimer(self)
        self.sessions_list_update_timer.timeout.connect(periodic_sessions_update)
        self.sessions_list_update_timer.start(3000)  # Update every 3 seconds (with re-subscription)
        
        # Timer to republish seed sync message periodically (to ensure new instances can detect us)
        # This is important because MQTT only keeps the last retained message per topic
        self.seed_republish_timer = QTimer(self)
        self.seed_republish_timer.timeout.connect(self._republishSeedSync)
        # OPTIMIZATION: Increased interval to reduce network traffic (was 2s, now 3s)
        # The timer will be stopped when dialog becomes READY anyway
        self.seed_republish_timer.start(3000)  # Republish every 3 seconds
        
        # Timer to refresh available sessions list (when in join mode)
        # Only refresh if no session is currently selected to avoid disrupting user selection
        self.sessions_refresh_timer = QTimer(self)
        self.sessions_refresh_timer.timeout.connect(self._refreshAvailableSessions)
        self.sessions_refresh_timer.start(3000)  # Refresh every 3 seconds
    
    def _connectSignals(self):
        """Connect to session manager signals for real-time updates"""
        # Note: We don't connect to playerConnected/playerDisconnected here
        # because players are not registered yet at this stage
        # Instead, we track instances via seed sync messages
    
    def _onModeChanged(self):
        """Handle mode selection change (create new vs join existing)"""
        # Prevent multiple calls during radio button toggle
        if not (self.create_new_radio.isChecked() or self.join_existing_radio.isChecked()):
            return  # Neither is checked, ignore (during toggle)
        
        if self.create_new_radio.isChecked():
            # Create new session mode
            self.config.is_session_creator = True
            self.sessions_group.hide()
            self.session_group.show()  # Show Session ID group in create mode
            self.session_id_edit.setEnabled(True)
            if not self.config.session_id:
                self.config.generate_session_id()
                self.session_id_edit.setText(self.config.session_id)
            self.info_label.setText("Create a new distributed game session.")
            
            # Reset selected session
            self._selected_session_id = None
            
            # Stop session discovery if it was running (but keep seed tracking)
            if self.session_manager.session_discovery_handler:
                # Unsubscribe from discovery topic
                discovery_topic_wildcard = f"{self.session_manager.DISCOVERY_TOPIC}/+"
                if self.model.mqttManager.client:
                    self.model.mqttManager.client.unsubscribe(discovery_topic_wildcard)
                self.session_manager.stopSessionDiscovery()
                # Seed tracking is now handled by SGMQTTHandlerManager
                # No need to restore manually - the manager handles it
            
            # Enable Connect button in create mode
            self.connect_button.setEnabled(True)
            self.connect_button.show()
            
            # Adjust window height only (preserve width)
            current_width = self.width()
            self.adjustSize()
            self.resize(current_width, self.height())
        else:
            # Join existing session mode
            self.config.is_session_creator = False
            self.sessions_group.show()
            self.session_id_edit.setEnabled(False)
            
            # Hide Session ID group until a session is selected (no need to show temporary ID)
            self.session_group.hide()
            
            # Reset selected session
            self._selected_session_id = None
            
            # Disable Connect button until a session is selected
            self.connect_button.setEnabled(False)
            self.connect_button.show()
            
            # Start session discovery if already connected
            if (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
                self._startSessionDiscovery()
            else:
                # Not connected yet - automatically start connection to enable session discovery
                # Generate a temporary session_id for connection (will be replaced when user selects a session)
                if not self.config.session_id:
                    temp_id = self.config.generate_session_id()
                    self._temporary_session_id = temp_id  # Store temporary ID
                    self.session_id_edit.setText(temp_id)
                    self.config.session_id = temp_id  # Set it for connection
                else:
                    # If session_id already exists, it might be from a previous selection
                    # Check if it's in discovered sessions to determine if it's temporary
                    self._temporary_session_id = self.config.session_id
                
                # Show connecting message
                self.sessions_list.clear()
                placeholder_item = QListWidgetItem("Connecting to broker to discover sessions...")
                placeholder_item.setForeground(QColor("gray"))
                self.sessions_list.addItem(placeholder_item)
                
                # Set flag to start discovery once connected
                self._should_start_discovery_on_connect = True
                
                # Automatically start connection (only if not already in progress)
                if not self._connection_in_progress:
                    self._updateState(self.STATE_CONNECTING)
                    self._connectToBroker()
            
            self.info_label.setText("Select a session from the list below, then click 'Connect' to join it.")
            
            # Adjust window height only (preserve width)
            current_width = self.width()
            self.adjustSize()
            self.resize(current_width, self.height())
    
    def _startSessionDiscovery(self):
        """Start session discovery"""
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            return
        
        # Initialize MQTT Handler Manager if not already done
        if not self._mqtt_handler_manager:
            self._mqtt_handler_manager = SGMQTTHandlerManager(self.model.mqttManager.client)
            self._mqtt_handler_manager.install()
        
        # Remove existing session_state discovery handler if any
        if self._session_state_discovery_handler_id is not None:
            self._mqtt_handler_manager.remove_handler(self._session_state_discovery_handler_id)
        
        # Create handler for session_state updates for all discovered sessions
        def session_state_discovery_handler(client, userdata, msg):
            # CRITICAL: Ignore callbacks during cleanup
            if hasattr(self, '_cleaning_up') and self._cleaning_up:
                return
            
            # Check if this is a session_state message for a discovered session
            if msg.topic.endswith('/session_state'):
                try:
                    import json
                    payload_str = msg.payload.decode("utf-8")
                    if not payload_str or not payload_str.strip():
                        return
                    
                    data = json.loads(payload_str)
                    session = SGDistributedSession.from_dict(data)
                    session_id = session.session_id
                    
                    # Skip if this is the session we're already connected to (handled elsewhere)
                    if self.config.session_id == session_id:
                        return
                    
                    # Only process if this is a discovered session
                    if session_id not in self.available_sessions:
                        return
                    
                    # Update cache for discovered sessions
                    self.session_states_cache[session_id] = session
                    
                    # CRITICAL: If session is closed, remove it from available_sessions
                    if session.state == 'closed':
                        if session_id in self.available_sessions:
                            del self.available_sessions[session_id]
                    
                    # Update sessions list to reflect the new instance count
                    QTimer.singleShot(0, self._updateSessionsList)
                except Exception as e:
                    print(f"[Dialog] Error in session_state_discovery_handler: {e}")
                    import traceback
                    traceback.print_exc()
        
        # Add handler using SGMQTTHandlerManager (matches all session_state topics)
        self._session_state_discovery_handler_id = self._mqtt_handler_manager.add_filter_handler(
            topic_filter=lambda topic: topic.endswith('/session_state'),
            handler_func=session_state_discovery_handler,
            priority=HandlerPriority.NORMAL,
            stop_propagation=False,
            description="session_state_discovery"
        )
        
        # Remove existing session discovery handler if any
        if self._session_discovery_handler_id is not None:
            self._mqtt_handler_manager.remove_handler(self._session_discovery_handler_id)
        
        # Create handler for session discovery messages using SGMQTTHandlerManager
        def session_discovery_handler(client, userdata, msg):
            # CRITICAL: Ignore callbacks during cleanup
            if hasattr(self, '_cleaning_up') and self._cleaning_up:
                return
            
            # Check if this is a session discovery message
            discovery_topic_prefix = f"{self.session_manager.DISCOVERY_TOPIC}/"
            if not msg.topic.startswith(discovery_topic_prefix):
                return
            
            try:
                import json
                import time
                from datetime import datetime
                
                msg_dict = json.loads(msg.payload.decode("utf-8"))
                session_id = msg_dict.get('session_id')
                if not session_id:
                    return
                
                # CRITICAL: Only check expiration for RETAINED messages
                # Non-retained messages (heartbeats) should always be accepted as they indicate active sessions
                current_time = time.time()
                is_expired = False
                
                # Only check expiration for retained messages
                if msg.retain:
                    # Retained messages contain timestamp as ISO string in msg_dict
                    msg_timestamp_iso = msg_dict.get('timestamp')
                    if msg_timestamp_iso:
                        try:
                            # Parse ISO timestamp to datetime, then to Unix timestamp
                            timestamp_str = str(msg_timestamp_iso)
                            if 'Z' in timestamp_str:
                                timestamp_str = timestamp_str.replace('Z', '+00:00')
                            
                            msg_datetime = datetime.fromisoformat(timestamp_str)
                            msg_timestamp_unix = msg_datetime.timestamp()
                            # Check if message is older than 15 seconds
                            age_seconds = current_time - msg_timestamp_unix
                            if age_seconds > 15.0:
                                is_expired = True
                        except (ValueError, AttributeError, TypeError):
                            # If parsing fails, treat as new message (not expired)
                            pass
                
                # Only add session if it's not expired
                if not is_expired:
                    # Update discovered sessions cache with current timestamp
                    if not hasattr(self.session_manager, 'discovered_sessions'):
                        self.session_manager.discovered_sessions = {}
                    
                    self.session_manager.discovered_sessions[session_id] = {
                        'timestamp': current_time,  # Use current time for active sessions
                        'info': msg_dict
                    }
                    
                    # Clean expired sessions (older than 15 seconds) from cache
                    expired_sessions = [
                        sid for sid, data in self.session_manager.discovered_sessions.items()
                        if current_time - data['timestamp'] > 15.0
                    ]
                    for sid in expired_sessions:
                        del self.session_manager.discovered_sessions[sid]
                    
                    # Update available_sessions and trigger callback
                    self.available_sessions = self.session_manager.discovered_sessions.copy()
                    
                    # Subscribe to session_state topics for newly discovered sessions
                    if session_id != self.config.session_id:
                        topic = f"{session_id}/session_state"
                        self.model.mqttManager.client.subscribe(topic, qos=1)
                    
                    # Update sessions list
                    QTimer.singleShot(0, self._updateSessionsList)
                    
            except Exception as e:
                print(f"[Dialog] Error in session_discovery_handler: {e}")
                import traceback
                traceback.print_exc()
        
        # Add handler using SGMQTTHandlerManager (matches all session_discovery topics)
        self._session_discovery_handler_id = self._mqtt_handler_manager.add_prefix_handler(
            topic_prefix=f"{self.session_manager.DISCOVERY_TOPIC}/",
            handler_func=session_discovery_handler,
            priority=HandlerPriority.NORMAL,
            stop_propagation=False
        )
        
        # Subscribe to discovery topic (handler is already installed above)
        discovery_topic_wildcard = f"{self.session_manager.DISCOVERY_TOPIC}/+"
        
        # CRITICAL: Unsubscribe first to force broker to send retained messages on resubscribe
        # This ensures we receive retained messages even if we were previously subscribed
        try:
            self.model.mqttManager.client.unsubscribe(discovery_topic_wildcard)
            import time
            time.sleep(0.1)  # Brief delay to ensure unsubscribe is processed
        except Exception:
            pass  # Ignore unsubscribe errors
        
        # Subscribe to discovery topic
        self.model.mqttManager.client.subscribe(discovery_topic_wildcard, qos=1)
        
        # Wait a moment for retained messages to be received, then update list
        def update_after_discovery():
            # Update available_sessions from session_manager's cache
            if hasattr(self.session_manager, 'discovered_sessions'):
                self.available_sessions = self.session_manager.discovered_sessions.copy()
            self._updateSessionsList()
            # Subscribe to player registration topics for all discovered sessions
            self._subscribeToSessionPlayerRegistrations()
        
        QTimer.singleShot(500, update_after_discovery)
    
    def _subscribeToSessionPlayerRegistrations(self):
        """Subscribe to player registration topics for all discovered sessions to track player counts"""
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            return
        
        # Initialize MQTT Handler Manager if not already done
        if not self._mqtt_handler_manager:
            self._mqtt_handler_manager = SGMQTTHandlerManager(self.model.mqttManager.client)
            self._mqtt_handler_manager.install()
        
        # Remove existing session player registration tracker handler if any
        # (SGMQTTHandlerManager handles the chain, so we can safely remove and re-add)
        if self._session_player_registration_tracker_handler_id is not None:
            self._mqtt_handler_manager.remove_handler(self._session_player_registration_tracker_handler_id)
        
        # Create wrapper to track player registrations for discovered sessions
        def player_registration_tracker(client, userdata, msg):
            # CRITICAL: Ignore callbacks during cleanup
            if hasattr(self, '_cleaning_up') and self._cleaning_up:
                return
            
            # Check if this is a player registration message for a discovered session
            for session_id in self.available_sessions.keys():
                registration_topic_base = f"{session_id}/session_player_registration"
                if msg.topic.startswith(registration_topic_base + "/"):
                    try:
                        import json
                        # Ignore empty messages (used to clear retained messages)
                        payload_str = msg.payload.decode("utf-8")
                        if not payload_str or payload_str.strip() == "":
                            return
                        
                        msg_dict = json.loads(payload_str)
                        client_id = msg_dict.get('clientId')
                        player_name = msg_dict.get('assigned_player_name')
                        
                        # Track instances (by client_id) - this is what we need for the sessions list
                        if client_id:
                            # Initialize instances cache for this session if needed
                            if session_id not in self.session_instances_cache:
                                self.session_instances_cache[session_id] = set()
                            old_instances_count = len(self.session_instances_cache[session_id])
                            self.session_instances_cache[session_id].add(client_id)
                            new_instances_count = len(self.session_instances_cache[session_id])
                            
                            # Update list if instances count changed
                            # Note: _updateSessionsList() preserves the visual selection, so we can update even if a session is selected
                            if new_instances_count != old_instances_count:
                                QTimer.singleShot(100, self._updateSessionsList)
                        
                        # Also track players (by player_name) for backward compatibility
                        if player_name:
                            # Initialize cache for this session if needed
                            if session_id not in self.session_players_cache:
                                self.session_players_cache[session_id] = set()
                            old_count = len(self.session_players_cache[session_id])
                            self.session_players_cache[session_id].add(player_name)
                            new_count = len(self.session_players_cache[session_id])
                            # Update list if count changed and no session is selected
                            if new_count != old_count and not self._selected_session_id:
                                QTimer.singleShot(100, self._updateSessionsList)
                    except Exception as e:
                        print(f"[Dialog] Error tracking player registration: {e}")
                        import traceback
                        traceback.print_exc()
                    # Don't forward - this is just for tracking
                    return
                
                # Check if this is a player disconnect message for a discovered session
                disconnect_topic_base = f"{session_id}/session_player_disconnect"
                if msg.topic.startswith(disconnect_topic_base + "/"):
                    try:
                        import json
                        msg_dict = json.loads(msg.payload.decode("utf-8"))
                        client_id = msg_dict.get('clientId')
                        
                        # Remove instance from cache
                        if client_id and session_id in self.session_instances_cache:
                            old_instances_count = len(self.session_instances_cache[session_id])
                            if client_id in self.session_instances_cache[session_id]:
                                self.session_instances_cache[session_id].remove(client_id)
                            new_instances_count = len(self.session_instances_cache[session_id])
                            
                            # Update list if instances count changed
                            # Note: _updateSessionsList() preserves the visual selection, so we can update even if a session is selected
                            if new_instances_count != old_instances_count:
                                QTimer.singleShot(100, self._updateSessionsList)
                    except Exception as e:
                        print(f"[Dialog] Error tracking player disconnect: {e}")
                        import traceback
                        traceback.print_exc()
                    # Don't forward - this is just for tracking
                    return
                
                # Check if this is an instance_ready message for a discovered session
                # This is more reliable than player_registration because it's published earlier
                instance_ready_topic_base = f"{session_id}/session_instance_ready"
                if msg.topic.startswith(instance_ready_topic_base + "/"):
                    try:
                        import json
                        # Ignore empty messages (used to clear retained messages)
                        payload_str = msg.payload.decode("utf-8")
                        if not payload_str or payload_str.strip() == "":
                            return
                        
                        msg_dict = json.loads(payload_str)
                        client_id = msg_dict.get('clientId')
                        
                        # Track instances via instance_ready messages
                        if client_id:
                            # Initialize instances cache for this session if needed
                            if session_id not in self.session_instances_cache:
                                self.session_instances_cache[session_id] = set()
                            old_instances_count = len(self.session_instances_cache[session_id])
                            self.session_instances_cache[session_id].add(client_id)
                            new_instances_count = len(self.session_instances_cache[session_id])
                            
                            
                            # Update list if instances count changed
                            # Note: _updateSessionsList() preserves the visual selection, so we can update even if a session is selected
                            # CRITICAL: Always update the list when cache changes, even if session is selected
                            # This ensures the display stays accurate for all sessions
                            if new_instances_count != old_instances_count:
                                QTimer.singleShot(100, self._updateSessionsList)
                    except Exception as e:
                        print(f"[Dialog] Error tracking instance ready: {e}")
                        import traceback
                        traceback.print_exc()
                    # Don't forward - this is just for tracking
                    return
        
        # Create a filter function that checks if the topic matches any discovered session
        def discovered_session_topic_filter(topic: str) -> bool:
            """Check if topic belongs to any discovered session"""
            for session_id in self.available_sessions.keys():
                registration_topic_base = f"{session_id}/session_player_registration"
                disconnect_topic_base = f"{session_id}/session_player_disconnect"
                instance_ready_topic_base = f"{session_id}/session_instance_ready"
                
                if (topic.startswith(registration_topic_base + "/") or
                    topic.startswith(disconnect_topic_base + "/") or
                    topic.startswith(instance_ready_topic_base + "/")):
                    return True
            return False
        
        # Add handler using SGMQTTHandlerManager with filter
        self._session_player_registration_tracker_handler_id = self._mqtt_handler_manager.add_filter_handler(
            topic_filter=discovered_session_topic_filter,
            handler_func=player_registration_tracker,
            priority=HandlerPriority.NORMAL,
            stop_propagation=False,  # Allow other handlers to process these messages too
            description="session_player_registration_tracker"
        )
        
        # Store reference for backward compatibility (used in checks above)
        self._player_registration_tracker = player_registration_tracker
        
        # Subscribe to player registration, disconnect, and instance_ready topics for all discovered sessions
        # CRITICAL: Unsubscribe first to force broker to send retained messages on resubscribe
        import time
        for session_id in self.available_sessions.keys():
            instance_ready_topic_wildcard = f"{session_id}/session_instance_ready/+"
            # Unsubscribe first to force retained messages on resubscribe
            try:
                self.model.mqttManager.client.unsubscribe(instance_ready_topic_wildcard)
            except Exception:
                pass  # Ignore unsubscribe errors
        
        # Brief delay to ensure unsubscribes are processed
        time.sleep(0.1)
        
        # Now subscribe to all topics
        for session_id in self.available_sessions.keys():
            registration_topic_wildcard = f"{session_id}/session_player_registration/+"
            disconnect_topic_wildcard = f"{session_id}/session_player_disconnect/+"
            instance_ready_topic_wildcard = f"{session_id}/session_instance_ready/+"
            result1 = self.model.mqttManager.client.subscribe(registration_topic_wildcard, qos=1)
            result2 = self.model.mqttManager.client.subscribe(disconnect_topic_wildcard, qos=1)
            result3 = self.model.mqttManager.client.subscribe(instance_ready_topic_wildcard, qos=1)
        
        # Wait for retained messages to be received, then update list
        # Increased delay to ensure all retained messages are received
        time.sleep(1.5)  # Increased from 0.8 to 1.5 to allow more time for retained messages
        
        if not self._selected_session_id:
            QTimer.singleShot(300, self._updateSessionsList)
    
    def _refreshAvailableSessions(self, force=False):
        """
        Refresh the list of available sessions
        
        Args:
            force (bool): If True, force refresh even if a session is selected.
                         If False (default), only refresh if no session is selected.
        """
        # Only refresh if in join mode and connected
        if not self.join_existing_radio.isChecked():
            return
        
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            return
        
        # If discovery is not started yet, start it
        if not self.session_manager.session_discovery_handler:
            self._startSessionDiscovery()
        else:
            # Update the list if no session is selected OR if force is True
            # When force=True, we still preserve the selection after updating
            if not self._selected_session_id or force:
                # Refresh player registrations subscriptions for updated sessions
                self._subscribeToSessionPlayerRegistrations()
                # Just update the list with current discovered sessions
                self._updateSessionsList()
            # If a session is selected and force=False, skip update to preserve selection
    
    def _updateSessionsList(self):
        """Update the sessions list widget with discovered sessions"""
        # Preserve currently selected session_id before clearing
        selected_session_id = self._selected_session_id
        
        # DEBUG: Log cache state before update
        
        self.sessions_list.clear()
        
        if not self.available_sessions:
            placeholder_item = QListWidgetItem("No sessions available")
            placeholder_item.setForeground(QColor("gray"))
            self.sessions_list.addItem(placeholder_item)
            return
        
        # Sort sessions by timestamp (most recent first)
        sorted_sessions = sorted(
            self.available_sessions.items(),
            key=lambda x: x[1]['timestamp'],
            reverse=True
        )
        
        selected_item = None
        for session_id, session_data in sorted_sessions:
            info = session_data['info']
            model_name = info.get('model_name', 'Unknown')
            num_min = info.get('num_players_min', '?')
            num_max = info.get('num_players_max', '?')
            
            # Phase 2: Get number of connected instances from session_state (single source of truth)
            # CRITICAL: If this is the session we're connected to, use self.session_state first
            session_state = None
            if self.config.session_id == session_id and self.session_state:
                session_state = self.session_state
            else:
                # Try to get from session_states_cache for discovered sessions
                session_state = self.session_states_cache.get(session_id)
            
            # CRITICAL: Skip closed sessions (don't display them in Available Sessions)
            if session_state and session_state.state == 'closed':
                continue
            
            if not session_state:
                # Try to read from broker (non-blocking, will update cache when received)
                if self.model.mqttManager.client and self.model.mqttManager.client.is_connected():
                    # Read session state asynchronously (will update cache via subscription)
                    def read_state():
                        state = self.session_manager.readSessionState(session_id, timeout=1.0)
                        if state:
                            self.session_states_cache[session_id] = state
                            # Update list after reading
                            QTimer.singleShot(100, self._updateSessionsList)
                    QTimer.singleShot(0, read_state)
                    # Fallback to old cache for now
                    connected_instances = self.session_instances_cache.get(session_id, set())
                    num_instances = len(connected_instances)
                else:
                    # Fallback to old cache
                    connected_instances = self.session_instances_cache.get(session_id, set())
                    num_instances = len(connected_instances)
            else:
                # Use session_state as source of truth
                num_instances = session_state.get_num_connected()
                # Update num_min and num_max from session_state if available
                if session_state.num_players_min and session_state.num_players_max:
                    num_min = session_state.num_players_min
                    num_max = session_state.num_players_max
                model_name = session_state.model_name
            
            
            # Check if this is the session we're connected to
            is_connected_session = (self.config.session_id == session_id and 
                                   self._isConnected())
            
            # Build instances text with availability info
            if num_min == num_max:
                if num_instances >= num_max:
                    instances_text = f"{num_instances}/{num_max} instances (Full)"
                    is_full = True
                else:
                    instances_text = f"{num_instances}/{num_max} instances (Available)"
                    is_full = False
            else:
                if num_instances >= num_max:
                    instances_text = f"{num_instances}/{num_max} instances (Full)"
                    is_full = True
                elif num_instances >= num_min:
                    instances_text = f"{num_instances}/{num_min}-{num_max} instances (Ready)"
                    is_full = False
                else:
                    instances_text = f"{num_instances}/{num_min}-{num_max} instances (Available)"
                    is_full = False
            
            # Add checkmark if this is the connected session
            if is_connected_session:
                display_text = f"{model_name} ✓ ({instances_text})"
            else:
                display_text = f"{model_name} ({instances_text})"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, session_id)
            
            # Style connected session with blue background
            if is_connected_session:
                item.setBackground(QColor("#e3f2fd"))  # Light blue background
                # Make checkmark blue if possible (using rich text or styling)
                # For now, the checkmark will be in default text color
            # Style full sessions differently (only if not connected)
            elif is_full:
                item.setForeground(QColor("#888"))  # Gray color for full sessions
                font = item.font()
                font.setItalic(True)
                item.setFont(font)
            
            tooltip_text = f"Session ID: {session_id}\nModel: {model_name}\nInstances: {instances_text}"
            # Also show registered players in tooltip if available
            registered_players = self.session_players_cache.get(session_id, set())
            if registered_players:
                tooltip_text += f"\nRegistered players: {', '.join(sorted(registered_players))}"
            item.setToolTip(tooltip_text)
            self.sessions_list.addItem(item)
            
            # Restore selection if this was the previously selected session
            if selected_session_id and session_id == selected_session_id:
                selected_item = item
        
        # Restore selection if it still exists
        if selected_item:
            self.sessions_list.setCurrentItem(selected_item)
            # Ensure _selected_session_id is still set
            self._selected_session_id = selected_session_id
        else:
            # No session selected - clear selection and disable Connect button
            self._selected_session_id = None
            if not (self.model.mqttManager.client and 
                    self.model.mqttManager.client.is_connected()):
                self.connect_button.setEnabled(False)
        
        # Force visual update of the list widget
        # This ensures the display is refreshed even when updated programmatically
        # Use QTimer to defer repaint and avoid recursive repaint errors
        QTimer.singleShot(0, lambda: (self.sessions_list.update(), self.sessions_list.repaint()))
        
    
    def _onSessionClicked(self, item):
        """Handle single click on a session in the list - selects the session"""
        session_id = item.data(Qt.UserRole)
        if session_id:
            # CRITICAL: Check if session is closed
            session_state = self.session_states_cache.get(session_id)
            if session_state and session_state.state == 'closed':
                # Session is closed - don't allow selection
                self._selected_session_id = None
                self.connect_button.setEnabled(False)
                self.info_label.setText(f"Session {session_id[:8]}... is closed and cannot be joined.")
                return
            
            self._selected_session_id = session_id
            self.session_id_edit.setText(session_id)
            # Highlight selected item
            self.sessions_list.setCurrentItem(item)
            
            # In join mode, Session ID group remains hidden (not needed for joining)
            # The session ID is stored internally but not displayed to the user
            
            # Enable Connect button if not already connected
            if not (self.model.mqttManager.client and 
                    self.model.mqttManager.client.is_connected()):
                self.connect_button.setEnabled(True)
                self.info_label.setText(f"Session selected: {session_id}\nClick 'Connect' to join this session.")
            else:
                # Already connected - enable Connect button so user can control when to sync seed
                self.config.session_id = session_id
                self._temporary_session_id = None
                self.connect_button.setEnabled(True)
                self.info_label.setText(f"Session selected: {session_id}\nClick 'Connect' to synchronize seed and join this session.")
    
    def _onSessionDoubleClicked(self, item):
        """Handle double-click on a session in the list - shortcut to select and connect"""
        # Single click already selected the session, so just trigger connect if not already connected
        self._onSessionClicked(item)
        
        # If not connected, trigger connect automatically
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            if self._selected_session_id:
                self._onConnect()
    
    
    def _copySessionId(self):
        """Copy session ID to clipboard"""
        session_id = self.session_id_edit.text().strip()
        if session_id:
            clipboard = QApplication.clipboard()
            clipboard.setText(session_id)
        else:
            QMessageBox.warning(self, "No Session ID", "Please enter or generate a session ID first.")
    
    def _updateConnectedInstances(self):
        """Update the connected instances list display and check if ready"""
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            self.connected_instances_label.setText("Instances: No instances connected yet")
            self._updateState(self.STATE_SETUP)
            return
        
        try:
            # CRITICAL: If we're not connected to any session, reset display
            if not self.config.session_id:
                self.connected_instances_label.setText("Instances: No instances connected yet")
                self.connected_instances_label.setStyleSheet("padding: 5px; color: #666;")
                return
            
            # Phase 2: Use session_state as single source of truth
            if self.session_state:
                # CRITICAL: Check if session is closed
                # Note: This should normally be handled in on_session_state_update(),
                # but keep as fallback in case session_state is set to closed elsewhere
                if self.session_state.state == 'closed':
                    # This should not happen if on_session_state_update() is working correctly,
                    # but if it does, reset state here as fallback
                    self.connected_instances_label.setText("Instances: Session closed")
                    self.connected_instances_label.setStyleSheet("padding: 5px; color: #e74c3c; font-weight: bold;")
                    # CRITICAL: Reset dialog state - we're no longer connected to a session
                    self.config.session_id = None
                    self.session_state = None
                    self._selected_session_id = None
                    self.seed_synced = False
                    self.ready_instances.clear()
                    self.connected_instances_snapshot = None
                    # CRITICAL: Reset seed status label (seed is no longer synchronized after session closure)
                    self.seed_status_label.setText("Seed: Not synchronized")
                    self.seed_status_label.setStyleSheet("padding: 5px; background-color: #f8d7da; border-radius: 3px;")
                    self._updateState(self.STATE_SETUP)
                    # Stop creator check timer if running
                    if self.session_state_creator_check_timer:
                        self.session_state_creator_check_timer.stop()
                        self.session_state_creator_check_timer = None
                    return
                
                # Use session_state.connected_instances as source of truth
                num_instances = self.session_state.get_num_connected()
                instances_to_count = self.session_state.connected_instances
            else:
                # Fallback to old method if session_state not available yet
                # CRITICAL: Use ready_instances instead of connected_instances
                # Only count instances that have completed seed sync AND subscribed to game_start
                # CRITICAL: Use snapshot if dialog is READY to avoid counting instances that connect after READY state
                if self.connected_instances_snapshot is not None:
                    instances_to_count = self.connected_instances_snapshot
                else:
                    instances_to_count = self.ready_instances
                num_instances = len(instances_to_count)
            
            # Determine minimum and maximum required instances
            if isinstance(self.config.num_players, int):
                min_required = self.config.num_players
                max_required = self.config.num_players
            else:
                min_required = self.config.num_players_min
                max_required = self.config.num_players_max
            
            # Update connected_instances_count in config
            self.config.connected_instances_count = num_instances
            
            # Check if minimum is reached (for "Start Now" button)
            min_reached = num_instances >= min_required
            
            # Check if maximum is reached (for auto-countdown)
            max_reached = num_instances >= max_required
            
            # Update display
            if num_instances > 0:
                if isinstance(self.config.num_players, int):
                    status_text = f"Instances: {num_instances}/{max_required} connected"
                else:
                    status_text = f"Instances: {num_instances}/{min_required}-{max_required} connected"
                
                if max_reached:
                    status_text += " ✓"
                    self.connected_instances_label.setStyleSheet("padding: 5px; color: #27ae60; font-weight: bold;")
                elif min_reached:
                    status_text += " ✓ (min)"
                    self.connected_instances_label.setStyleSheet("padding: 5px; color: #27ae60; font-weight: bold;")
                else:
                    status_text += f" (waiting for {min_required - num_instances} more...)"
                    self.connected_instances_label.setStyleSheet("padding: 5px; color: #f39c12; font-weight: bold;")
                self.connected_instances_label.setText(status_text)
            else:
                self.connected_instances_label.setText("Instances: No instances connected yet")
                self.connected_instances_label.setStyleSheet("padding: 5px; color: #666;")
            
            # Check if ready to start
            # Check if ready for manual start (minimum reached)
            if self.seed_synced and min_reached:
                # Minimum reached - can start manually (if creator)
                # Check if maximum reached (for auto-countdown)
                if max_reached:
                    # CRITICAL: Take snapshot IMMEDIATELY when we first detect EXACTLY the maximum number of instances
                    # This prevents counting instances that connect after we have enough
                    # Use ready_instances for snapshot (only instances that are truly ready)
                    if self.connected_instances_snapshot is None and num_instances == max_required:
                        self.connected_instances_snapshot = self.ready_instances.copy()
                    elif self.connected_instances_snapshot is None and num_instances > max_required:
                        # We have more than maximum - this means an instance connected after we reached the maximum count
                        # Take snapshot with only the first N instances (where N = max_required)
                        # Take first N instances from the set (order is not guaranteed, but this is better than taking all)
                        instances_list = list(self.ready_instances)
                        self.connected_instances_snapshot = set(instances_list[:max_required])
                    
                    if self.state_manager.current_state != ConnectionState.READY_MAX:
                        self.state_manager.transition_to(ConnectionState.READY_MAX, force=True)
                else:
                    # Minimum reached but not maximum
                    if self.state_manager.current_state != ConnectionState.READY_MIN:
                        self.state_manager.transition_to(ConnectionState.READY_MIN, force=True)
            elif self.seed_synced:
                # Waiting for minimum
                if self.state_manager.current_state != ConnectionState.WAITING:
                    self.state_manager.transition_to(ConnectionState.WAITING, force=True)
                    
        except Exception as e:
            self.connected_instances_label.setText("Instances: No instances connected yet")
            self.connected_instances_label.setStyleSheet("padding: 5px; color: #666;")
    
    @property
    def current_state(self):
        """Get current state (backward compatibility property)"""
        return self.state_manager.current_state.value
    
    @current_state.setter
    def current_state(self, value):
        """Set current state (backward compatibility - triggers transition)"""
        if isinstance(value, str):
            state_enum = self._STATE_MAP.get(value)
            if state_enum is None:
                print(f"[Dialog] Warning: Unknown state '{value}', ignoring")
                return
        else:
            state_enum = value
        self.state_manager.transition_to(state_enum, force=True)
    
    def _onStateChanged(self, old_state: ConnectionState, new_state: ConnectionState):
        """
        Callback called when state changes.
        Updates UI based on new state.
        """
        # Update UI (current_state property will return the correct value)
        self._updateStateUI(new_state)
    
    def _updateState(self, new_state):
        """
        Transition to a new state (backward compatibility wrapper).
        Use state_manager.transition_to() directly for new code.
        """
        # Convert string state to ConnectionState enum
        if isinstance(new_state, str):
            state_enum = self._STATE_MAP.get(new_state)
            if state_enum is None:
                print(f"[Dialog] Warning: Unknown state '{new_state}', using SETUP")
                state_enum = ConnectionState.SETUP
        else:
            state_enum = new_state
        
        # Use state manager for transition
        self.state_manager.transition_to(state_enum, force=True)
    
    def _updateStateUI(self, new_state: ConnectionState):
        """Update dialog UI based on state (UI logic only)"""
        # Convert ConnectionState to string for comparison with old code
        state_str = new_state.value
        
        if new_state == ConnectionState.SETUP:
            # Enable configuration controls
            self.session_id_edit.setEnabled(True)
            self.copy_session_btn.setEnabled(True)
            # CRITICAL: Enable Connect button only if:
            # - In create mode, OR
            # - In join mode AND a session is selected
            if self.create_new_radio.isChecked():
                self.connect_button.setEnabled(True)
            else:
                # Join mode - enable only if session is selected
                self.connect_button.setEnabled(self._selected_session_id is not None)
            self.connect_button.show()
            self.start_button.hide()
            self.countdown_label.hide()
            # Hide Cancel button - not connected yet
            self.cancel_button.hide()
            # Enable radio buttons - user can still change mode before seed sync
            self.create_new_radio.setEnabled(True)
            self.join_existing_radio.setEnabled(True)
            # Show Session ID group only in create mode (needed to share ID)
            # In join mode, Session ID group is always hidden (not needed)
            if self.create_new_radio.isChecked():
                self.session_group.show()
                self.info_label.setText("Create a new distributed game session.")
            else:
                # Join mode - Session ID group always hidden
                self.session_group.hide()
                if self._selected_session_id:
                    self.info_label.setText(f"Session selected: {self._selected_session_id}\nClick 'Connect' to join this session.")
                else:
                    self.info_label.setText("Select a session from the list below, then click 'Connect' to join it.")
            
        elif new_state == ConnectionState.CONNECTING:
            # Disable configuration, show connecting status (but keep Copy enabled)
            self.session_id_edit.setEnabled(False)
            self.copy_session_btn.setEnabled(True)  # Keep Copy enabled
            self.connect_button.setEnabled(False)
            self.connect_button.show()
            self.start_button.hide()
            self.countdown_label.hide()
            # Show Cancel button only if actually connected (seed synced)
            # This prevents showing Cancel while just selecting a session in Join mode
            if self._isConnected():
                self.cancel_button.show()
            else:
                self.cancel_button.hide()
            # Enable radio buttons - user can still change mode before seed sync
            self.create_new_radio.setEnabled(True)
            self.join_existing_radio.setEnabled(True)
            # Show Session ID group only in create mode (needed to share ID)
            # In join mode, Session ID group is always hidden
            if self.create_new_radio.isChecked():
                self.session_group.show()
            else:
                self.session_group.hide()
            self.info_label.setText("Connecting to broker and synchronizing seed...")
            
        elif new_state == ConnectionState.WAITING:
            # Keep session ID read-only, waiting for instances (but keep Copy enabled)
            self.session_id_edit.setEnabled(False)
            self.copy_session_btn.setEnabled(True)  # Keep Copy enabled
            # In join mode, hide Connect button if already connected (seed synced)
            if self.join_existing_radio.isChecked():
                if self._isConnected():
                    # Already connected, hide Connect button
                    self.connect_button.hide()
                else:
                    # Not yet connected, show but disable Connect button
                    self.connect_button.setEnabled(False)
                    self.connect_button.show()
            else:
                # Create mode, hide Connect button
                self.connect_button.hide()
            self.start_button.hide()
            self.countdown_label.hide()
            # Show Cancel button only if actually connected (seed synced)
            if self._isConnected():
                self.cancel_button.show()
            else:
                self.cancel_button.hide()
            # Disable radio buttons - seed is already synced, cannot change mode
            self.create_new_radio.setEnabled(False)
            self.join_existing_radio.setEnabled(False)
            # Show Session ID group only in create mode (needed to share ID)
            # In join mode, Session ID group is always hidden
            if self.create_new_radio.isChecked():
                self.session_group.show()
            else:
                self.session_group.hide()
            num_instances = len(self.connected_instances)
            if isinstance(self.config.num_players, int):
                min_required = self.config.num_players
            else:
                min_required = self.config.num_players_min
            waiting = min_required - num_instances
            self.info_label.setText(f"⏳ Waiting for {waiting} more instance(s) to connect...")
            
            # Update sessions list to show "Connected to" indicator if in join mode
            if self.join_existing_radio.isChecked() and self._isConnected():
                QTimer.singleShot(100, self._updateSessionsList)
            
        elif new_state == ConnectionState.READY_MIN:
            # Minimum reached - show "Start Now" button ONLY on creator instance
            self.session_id_edit.setEnabled(False)
            self.copy_session_btn.setEnabled(True)
            self.connect_button.hide()
            
            # CRITICAL: Show "Start Now" button ONLY if this is the session creator
            if self.config.is_session_creator:
                self.start_button.show()
                self.start_button.setEnabled(True)
                num_instances = len(self.connected_instances)
                if isinstance(self.config.num_players, int):
                    min_required = max_required = self.config.num_players
                else:
                    min_required = self.config.num_players_min
                    max_required = self.config.num_players_max
                self.info_label.setText(
                    f"✓ Minimum instances connected ({num_instances}/{min_required}-{max_required}). "
                    f"Click 'Start Now' to begin, or wait for more players."
                )
            else:
                # Joiner instance - hide button, show waiting message
                self.start_button.hide()
                num_instances = len(self.connected_instances)
                if isinstance(self.config.num_players, int):
                    min_required = max_required = self.config.num_players
                else:
                    min_required = self.config.num_players_min
                    max_required = self.config.num_players_max
                self.info_label.setText(
                    f"✓ Minimum instances connected ({num_instances}/{min_required}-{max_required}). "
                    f"Waiting for session creator to start the game..."
                )
            
            self.countdown_label.hide()
            # Show Cancel button - user can cancel connection
            self.cancel_button.show()
            # Disable radio buttons - seed is already synced, cannot change mode
            self.create_new_radio.setEnabled(False)
            self.join_existing_radio.setEnabled(False)
            # Show Session ID group only in create mode (needed to share ID)
            # In join mode, Session ID group is always hidden
            if self.create_new_radio.isChecked():
                self.session_group.show()
            else:
                self.session_group.hide()
            
            # Update sessions list to show "Connected to" indicator if in join mode
            if self.join_existing_radio.isChecked() and self._isConnected():
                QTimer.singleShot(100, self._updateSessionsList)
        
        elif new_state == ConnectionState.READY_MAX:
            # Maximum reached - auto-countdown will trigger
            self.session_id_edit.setEnabled(False)
            self.copy_session_btn.setEnabled(True)
            self.connect_button.hide()
            
            # CRITICAL: Show "Start Now" button ONLY on creator instance
            if self.config.is_session_creator:
                self.start_button.show()
                self.start_button.setEnabled(True)
            else:
                self.start_button.hide()
            
            self.info_label.setText("✓ All instances connected! The game will start automatically in a few seconds.")
            self._startAutoStartCountdown()  # Only triggers at maximum
            
            # Show Cancel button only if actually connected (seed synced)
            if self._isConnected():
                self.cancel_button.show()
            else:
                self.cancel_button.hide()
            # Disable radio buttons - seed is already synced, cannot change mode
            self.create_new_radio.setEnabled(False)
            self.join_existing_radio.setEnabled(False)
            # Show Session ID group only in create mode (needed to share ID)
            # In join mode, Session ID group is always hidden
            if self.create_new_radio.isChecked():
                self.session_group.show()
            else:
                self.session_group.hide()
            
            # Update sessions list to show "Connected to" indicator if in join mode
            if self.join_existing_radio.isChecked() and self._isConnected():
                QTimer.singleShot(100, self._updateSessionsList)
            
            # NOTE: Snapshot is now taken in _updateConnectedInstances() when enough instances are first detected
            # This ensures we capture exactly the required number of instances, not more
            # The snapshot should already exist when we reach READY_MAX state
            if self.connected_instances_snapshot is None:
                # Fallback: if snapshot wasn't taken yet (shouldn't happen), take it now
                self.connected_instances_snapshot = self.connected_instances.copy()
            
            # OPTIMIZATION: Stop periodic republishing once READY (no need to keep broadcasting)
            if hasattr(self, 'seed_republish_timer') and self.seed_republish_timer:
                self.seed_republish_timer.stop()
        
        elif new_state == ConnectionState.READY:
            # Legacy state (kept for backward compatibility)
            # All ready, show start button (but keep Copy enabled)
            self.session_id_edit.setEnabled(False)
            self.copy_session_btn.setEnabled(True)  # Keep Copy enabled
            self.connect_button.hide()
            self.start_button.show()
            self.start_button.setEnabled(True)
            # Show Cancel button only if actually connected (seed synced)
            if self._isConnected():
                self.cancel_button.show()
            else:
                self.cancel_button.hide()
            # Disable radio buttons - seed is already synced, cannot change mode
            self.create_new_radio.setEnabled(False)
            self.join_existing_radio.setEnabled(False)
            # Show Session ID group only in create mode (needed to share ID)
            # In join mode, Session ID group is always hidden
            if self.create_new_radio.isChecked():
                self.session_group.show()
            else:
                self.session_group.hide()
            
            # NOTE: Snapshot is now taken in _updateConnectedInstances() when enough instances are first detected
            # This ensures we capture exactly the required number of instances, not more
            # The snapshot should already exist when we reach READY state
            if self.connected_instances_snapshot is None:
                # Fallback: if snapshot wasn't taken yet (shouldn't happen), take it now
                self.connected_instances_snapshot = self.connected_instances.copy()
            
            # OPTIMIZATION: Stop periodic republishing once READY (no need to keep broadcasting)
            if hasattr(self, 'seed_republish_timer') and self.seed_republish_timer:
                self.seed_republish_timer.stop()
            
            # Start countdown automatically for both create and join modes
            self.info_label.setText("✓ All instances connected! The game will start automatically in a few seconds.")
            self._startAutoStartCountdown()
    
    def _onConnect(self):
        """Handle Connect button click - update session_id, connect to broker, and sync seed"""
        # In join mode, check if a session has been selected
        if self.join_existing_radio.isChecked():
            # Use selected session_id if available, otherwise get from edit field
            if self._selected_session_id:
                session_id = self._selected_session_id
                self.config.session_id = session_id
                self._temporary_session_id = None  # Clear temporary flag
                self.session_id_edit.setText(session_id)
            else:
                # Fallback: get from edit field
                session_id = self.session_id_edit.text().strip()
                if not session_id or session_id == self._temporary_session_id:
                    QMessageBox.warning(self, "No Session Selected", "Please select a session from the list by clicking on it.")
                    return
                self.config.session_id = session_id
            
            # If already connected, just sync seed for the selected session
            # But don't auto-transition to READY - let user control the flow
            if (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
                # Update connection status to reflect that we're connected
                self.connection_status = "Connected to broker"
                self.status_label.setText(f"Connection Status: [●] {self.connection_status}")
                self.status_label.setStyleSheet("padding: 5px; background-color: #d4edda; border-radius: 3px; color: #155724;")
                # Update state to CONNECTING to show we're processing
                self._updateState(self.STATE_CONNECTING)
                self._syncSeed()
                # After seed sync, check if we should go to WAITING or READY
                # But don't auto-start countdown in join mode
                # Note: _updateConnectedInstances() is called after a delay in _syncSeed()
                # to allow retained messages to be received
                return
        else:
            # In create mode, get session_id from edit field
            session_id = self.session_id_edit.text().strip()
            if not session_id:
                QMessageBox.warning(self, "Invalid Session ID", "Please enter a session ID or generate a new one.")
                return
            self.config.session_id = session_id
        
        # Update state to connecting
        self._updateState(self.STATE_CONNECTING)
        
        # Connect to broker
        self._connectToBroker()
    
    def _connectToBroker(self):
        """Connect to MQTT broker by calling setMQTTProtocol()"""
        # Prevent multiple simultaneous connection attempts
        if self._connection_in_progress:
            return
        
        # Check if already connected
        if (self.model.mqttManager.client and 
            self.model.mqttManager.client.is_connected()):
            self._checkConnection()  # Update UI and start discovery if needed
            return
        
        try:
            self._connection_in_progress = True
            self.model.mqttManager.setMQTTProtocol(
                self.config.mqtt_update_type,
                broker_host=self.config.broker_host,
                broker_port=self.config.broker_port,
                session_id=self.config.session_id
            )
            
            # Start checking connection status
            self.connection_status = "Connecting..."
            self.status_label.setText(f"Connection Status: {self.connection_status}")
            self._checkConnection()
        except Exception as e:
            self._connection_in_progress = False  # Clear flag on error
            self.connection_status = f"Connection failed: {str(e)}"
            self.status_label.setText(f"Connection Status: [✗] {self.connection_status}")
            self.status_label.setStyleSheet("padding: 5px; background-color: #f8d7da; border-radius: 3px; color: #721c24;")
            self._updateState(self.STATE_SETUP)  # Reset to setup state
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to MQTT broker:\n{str(e)}")
    
    def _checkConnection(self):
        """Check if MQTT connection is established (polling)"""
        if (self.model.mqttManager.client and 
            self.model.mqttManager.client.is_connected()):
            # Connection established
            self._connection_in_progress = False  # Clear flag
            
            # Initialize MQTT Handler Manager when client is available
            if not self._mqtt_handler_manager:
                self._mqtt_handler_manager = SGMQTTHandlerManager(self.model.mqttManager.client)
                self._mqtt_handler_manager.install()
            
            self.connection_status = "Connected to broker"
            self.status_label.setText(f"Connection Status: [●] {self.connection_status}")
            self.status_label.setStyleSheet("padding: 5px; background-color: #d4edda; border-radius: 3px; color: #155724;")
            
            # If in join mode, start session discovery FIRST (before seed sync)
            # This allows user to see available sessions immediately after connection
            if self.join_existing_radio.isChecked():
                # Always start discovery if not already started (regardless of when mode was changed)
                if not self.session_manager.session_discovery_handler:
                    self._startSessionDiscovery()
                self._should_start_discovery_on_connect = False  # Clear flag
                # In join mode, sync seed ONLY if user has selected a session from the list
                # Don't sync with temporary session_id - wait for user to select a real session
                if self.config.session_id and self.config.session_id != self._temporary_session_id:
                    # User has selected a session (not the temporary one), sync seed now
                    self._syncSeed()
                else:
                    # Temporary session_id or no session selected yet - don't sync seed
                    pass
                return
            
            # In create mode, sync seed immediately
            # Once connected, sync seed (which will track all instances including our own)
            self._syncSeed()
        else:
            # Retry after 500ms
            QTimer.singleShot(500, self._checkConnection)
    
    def _syncSeed(self):
        """Synchronize seed after connection is established"""
        if self.seed_synced:
            return
        
        try:
            self.seed_status_label.setText("Seed: Checking for existing seed...")
            self.seed_status_label.setStyleSheet("padding: 5px; background-color: #fff8dc; border-radius: 3px;")
            QApplication.processEvents()  # Update UI immediately
            
            # Synchronize seed with configurable timeout
            # Use seed_sync_timeout from config (default 1.0s) for initial wait
            # Total timeout is seed_sync_timeout + 1 second for safety
            # Pass callback to track connected instances during seed sync
            def track_client_id(client_id):
                if not client_id:
                    return
                old_count = len(self.connected_instances)
                self.connected_instances.add(client_id)
                new_count = len(self.connected_instances)
                # Don't update UI here - wait until after seed sync completes
                # This avoids race conditions
            
            # Prepare tracking handler BEFORE syncSeed() so it can be installed immediately after
            # This ensures we don't miss any messages published between syncSeed() completion and handler installation
            session_topics = self.session_manager.getSessionTopics(self.config.session_id)
            seed_topic = session_topics[1]  # session_seed_sync
            
            synced_seed = self.session_manager.syncSeed(
                self.config.session_id,
                shared_seed=self.config.shared_seed,
                timeout=self.config.seed_sync_timeout + 1.0,
                initial_wait=self.config.seed_sync_timeout,
                client_id_callback=track_client_id
            )
            
            
            # Verify that seed sync actually succeeded
            if synced_seed is None:
                raise ValueError("Seed synchronization returned None")
            
            self.config.shared_seed = synced_seed
            self.synced_seed_value = synced_seed
            
            # Apply seed immediately
            import random
            random.seed(synced_seed)
            
            self.seed_synced = True
            self.seed_status_label.setText("Seed: Synchronized ✓")
            self.seed_status_label.setStyleSheet("padding: 5px; background-color: #d4edda; border-radius: 3px;")
            
            # CRITICAL: Install tracking handler IMMEDIATELY after syncSeed() completes
            # This minimizes the window where messages might be missed
            # syncSeed() has restored the original handler, so we wrap that
            self._subscribeToSeedSyncForTracking()
            
            # CRITICAL: Also subscribe to player registration messages to track instances
            # Player registration messages use separate topics per player, so all retained messages are preserved
            # This provides a more reliable way to track connected instances
            self._subscribeToPlayerRegistrationForTracking()
            
            # CRITICAL: Subscribe to game start topic for synchronization
            self._subscribeToGameStart()
            
            # CRITICAL: Subscribe to instance ready topic to track which instances are ready
            self._subscribeToInstanceReady()
            
            # CRITICAL: Publish instance ready signal after seed sync and game start subscription
            self._publishInstanceReady()
            
            # Phase 2: Subscribe to session state updates BEFORE reading (to ensure handler is in chain)
            # This ensures we receive updates even if other handlers are installed later
            if self.join_existing_radio.isChecked() and self.config.session_id:
                # Subscribe first to ensure handler is in chain
                self._subscribeToSessionStateUpdates()
            
            # Phase 2: Read session state if joining existing session
            if self.join_existing_radio.isChecked() and self.config.session_id:
                # Try to read existing session state
                existing_state = self.session_manager.readSessionState(self.config.session_id, timeout=2.0)
                if existing_state:
                    self.session_state = existing_state
                    # CRITICAL: Don't consider session expired immediately after joining
                    # The last_heartbeat might be old, but we just joined so the creator is likely still alive
                    # We'll wait for the next heartbeat (within 5 seconds) before checking expiration
                    # Add ourselves to the session state
                    if self.model.mqttManager.clientId not in self.session_state.connected_instances:
                        self.session_state.add_instance(self.model.mqttManager.clientId)
                        self.session_manager.publishSessionState(self.session_state)
                    # Also update cache for consistency
                    self.session_states_cache[self.config.session_id] = self.session_state
                    # CRITICAL: Record when we joined to track if we've received heartbeat since joining
                    from datetime import datetime
                    self._session_joined_at = datetime.now()
                    self._last_heartbeat_when_joined = self.session_state.last_heartbeat  # Store heartbeat value when we joined
                    # Subscribe to updates (already done above, but ensure it's still active)
                    # Note: _subscribeToSessionStateUpdates() was already called before reading
                    # Start creator check timer (to detect if creator disconnects)
                    # Use a delay to avoid false positives (wait for first heartbeat after join)
                    QTimer.singleShot(10000, self._startCreatorCheckTimer)  # Start checking after 10s (allows time for heartbeat)
                else:
                    # No existing session state found - will be initialized when session_state is received via subscription
                    pass
            
            # NOTE: We do NOT take snapshot here - we continue counting instances until READY state
            # The snapshot will be taken when dialog transitions to READY state
            # This ensures all instances that connect during the waiting period are counted
            
            # If creating a new session (not joining), publish session discovery
            if self.create_new_radio.isChecked():
                model_name = getattr(self.model, 'name', None) or getattr(self.model, 'windowTitle_prefix', 'Unknown')
                if isinstance(self.config.num_players, int):
                    num_min = num_max = self.config.num_players
                else:
                    num_min = self.config.num_players_min
                    num_max = self.config.num_players_max
                self.session_manager.publishSession(
                    self.config.session_id,
                    num_min,
                    num_max,
                    model_name
                )
                
                # Phase 2: Initialize session state for new session
                self._initializeSessionState(model_name, num_min, num_max)
            
            # CRITICAL: Wait for retained messages to be received before updating UI
            # This ensures connected_instances and ready_instances are populated from retained messages
            # Use QTimer to avoid blocking the UI thread
            # Increased delay to ensure all retained messages (instance_ready, player_registration) are received
            def update_with_log():
                self._updateConnectedInstances()
            QTimer.singleShot(1500, update_with_log)
            
        except Exception as e:
            self.seed_status_label.setText(f"Seed: Sync failed - {str(e)}")
            self.seed_status_label.setStyleSheet("padding: 5px; background-color: #f8d7da; border-radius: 3px;")
            self._updateState(self.STATE_SETUP)  # Reset to setup state
            QMessageBox.critical(self, "Seed Sync Error", f"Failed to synchronize seed:\n{str(e)}")
    
    def _initializeSessionState(self, model_name: str, num_players_min: int, num_players_max: int):
        """
        Initialize session state for a new session (Phase 2).
        
        Args:
            model_name: Name of the game model
            num_players_min: Minimum number of players
            num_players_max: Maximum number of players
        """
        if not self.config.session_id or not self.model.mqttManager.clientId:
            return
        
        # Create session state
        self.session_state = SGDistributedSession(
            session_id=self.config.session_id,
            creator_client_id=self.model.mqttManager.clientId,
            model_name=model_name,
            num_players_min=num_players_min,
            num_players_max=num_players_max
        )
        
        # Publish initial session state
        self.session_manager.publishSessionState(self.session_state)
        
        # Start heartbeat timer (creator only)
        self._startSessionStateHeartbeat()
        
        # Subscribe to session state updates
        self._subscribeToSessionStateUpdates()
        
    
    def _subscribeToSessionStateUpdates(self):
        """
        Subscribe to session state updates for the current session (Phase 2).
        """
        if not self.config.session_id:
            return
        
        def on_session_state_update(session: SGDistributedSession):
            """Handle session state update"""
            try:
                
                # CRITICAL: Check if this is the session we're connected to
                # If self.session_state is None but we're connected to this session, initialize it
                is_connected_session = (self.config.session_id and 
                                        session.session_id == self.config.session_id)
                
                if is_connected_session:
                    # This is our connected session
                    was_none = (self.session_state is None)
                    
                    if self.session_state:
                        # CRITICAL: Check if heartbeat was updated (creator is still alive)
                        if session.last_heartbeat > self.session_state.last_heartbeat:
                            # Update our tracking to know we've received a heartbeat since joining
                            if hasattr(self, '_last_heartbeat_when_joined'):
                                self._last_heartbeat_when_joined = session.last_heartbeat
                    else:
                        # First time receiving session_state - will be initialized below
                        pass
                    
                    self.session_state = session
                    
                    # CRITICAL: If this is the first time we receive session_state (was None),
                    # and we're not already in connected_instances, add ourselves
                    if was_none and self.model.mqttManager.clientId not in self.session_state.connected_instances:
                        self.session_state.add_instance(self.model.mqttManager.clientId)
                        self.session_manager.publishSessionState(self.session_state)
                        # CRITICAL: Record when we joined and start creator check timer
                        # (This handles the case where readSessionState() returned None)
                        from datetime import datetime
                        self._session_joined_at = datetime.now()
                        self._last_heartbeat_when_joined = self.session_state.last_heartbeat
                        # Start creator check timer (to detect if creator disconnects)
                        # Use a delay to avoid false positives (wait for first heartbeat after join)
                        QTimer.singleShot(10000, self._startCreatorCheckTimer)  # Start checking after 10s
                    
                    # Also update cache for consistency
                    self.session_states_cache[session.session_id] = session
                    
                    # CRITICAL: If session is closed, completely reset dialog state
                    if session.state == 'closed':
                        print(f"[Dialog] Session closed detected, resetting dialog state...")
                        # Remove from available_sessions if present
                        if session.session_id in self.available_sessions:
                            del self.available_sessions[session.session_id]
                        # CRITICAL: Stop creator check timer since session is closed
                        if self.session_state_creator_check_timer:
                            self.session_state_creator_check_timer.stop()
                            self.session_state_creator_check_timer = None
                        # CRITICAL: Completely reset dialog state - we're no longer connected to a session
                        self.config.session_id = None
                        self.session_state = None
                        self._selected_session_id = None
                        self.seed_synced = False  # Reset seed sync status
                        # Reset connected instances tracking
                        self.ready_instances.clear()
                        self.connected_instances_snapshot = None
                        # CRITICAL: Reset seed status label (seed is no longer synchronized after session closure)
                        self.seed_status_label.setText("Seed: Not synchronized")
                        self.seed_status_label.setStyleSheet("padding: 5px; background-color: #f8d7da; border-radius: 3px;")
                        # Update state to SETUP to reset UI
                        self._updateState(self.STATE_SETUP)
                        # Update UI (defer to avoid recursive repaint)
                        QTimer.singleShot(0, self._updateConnectedInstances)
                        QTimer.singleShot(0, self._updateSessionsList)
                    else:
                        # Session is still open, just update normally
                        # Update UI (defer to avoid recursive repaint)
                        QTimer.singleShot(0, self._updateConnectedInstances)
                        QTimer.singleShot(0, self._updateSessionsList)
                else:
                    # Update cache for discovered sessions
                    self.session_states_cache[session.session_id] = session
                    
                    # CRITICAL: If session is closed, remove it from available_sessions
                    if session.state == 'closed':
                        if session.session_id in self.available_sessions:
                            del self.available_sessions[session.session_id]
                    
                    # Update sessions list (defer to avoid recursive repaint)
                    QTimer.singleShot(0, self._updateSessionsList)
            except Exception as e:
                print(f"[Dialog] Error in on_session_state_update: {e}")
                import traceback
                traceback.print_exc()
                # Don't crash, just log the error
        
        # Use SGMQTTHandlerManager instead of subscribeToSessionState to avoid conflicts
        # Initialize MQTT Handler Manager if not already done
        if not self._mqtt_handler_manager:
            self._mqtt_handler_manager = SGMQTTHandlerManager(self.model.mqttManager.client)
            self._mqtt_handler_manager.install()
        
        # Create handler for session_state updates for the connected session
        topic = f"{self.config.session_id}/session_state"
        
        def session_state_handler(client, userdata, msg):
            if msg.topic == topic:
                try:
                    import json
                    payload_str = msg.payload.decode("utf-8")
                    if not payload_str or not payload_str.strip():
                        return
                    data = json.loads(payload_str)
                    session = SGDistributedSession.from_dict(data)
                    on_session_state_update(session)
                except Exception as e:
                    print(f"[Dialog] Error processing session_state update: {e}")
                    import traceback
                    traceback.print_exc()
        
        # Add handler using SGMQTTHandlerManager
        self._session_state_connected_handler_id = self._mqtt_handler_manager.add_topic_handler(
            topic=topic,
            handler_func=session_state_handler,
            priority=HandlerPriority.HIGH,
            stop_propagation=False
        )
        
        # Subscribe to topic
        self.model.mqttManager.client.subscribe(topic, qos=1)
    
    def _startSessionStateHeartbeat(self):
        """
        Start heartbeat timer for session creator (Phase 2).
        Updates last_heartbeat every 5 seconds.
        """
        if not self.session_state or not self.session_state.is_creator(self.model.mqttManager.clientId):
            return
        
        # Stop existing timer if any
        if self.session_state_heartbeat_timer:
            self.session_state_heartbeat_timer.stop()
        
        def send_heartbeat():
            try:
                if self.session_state and self.session_state.is_creator(self.model.mqttManager.clientId):
                    self.session_state.update_heartbeat()
                    self.session_manager.publishSessionState(self.session_state)
            except Exception as e:
                print(f"[Dialog] Error in send_heartbeat: {e}")
                import traceback
                traceback.print_exc()
                # Don't crash, just log the error
        
        self.session_state_heartbeat_timer = QTimer(self)
        self.session_state_heartbeat_timer.timeout.connect(send_heartbeat)
        self.session_state_heartbeat_timer.start(5000)  # Every 5 seconds
    
    def _startCreatorCheckTimer(self):
        """
        Start timer to check if creator is still alive (Phase 2).
        Checks every 3 seconds, timeout is 15 seconds.
        """
        if not self.session_state:
            return
        
        # Stop existing timer if any
        if self.session_state_creator_check_timer:
            self.session_state_creator_check_timer.stop()
        
        def check_creator():
            try:
                if not self.session_state:
                    return
                
                # CRITICAL: If session is already closed, stop the timer and return
                if self.session_state.state == 'closed':
                    if self.session_state_creator_check_timer:
                        self.session_state_creator_check_timer.stop()
                        self.session_state_creator_check_timer = None
                    return
                
                # Only check if we're not the creator
                if self.session_state.is_creator(self.model.mqttManager.clientId):
                    return
                
                # Check if session is expired
                time_since_last_update = (datetime.now() - self.session_state.last_updated).total_seconds()
                time_since_heartbeat = (datetime.now() - self.session_state.last_heartbeat).total_seconds()
                
                # CRITICAL: Check if we've received a heartbeat since joining
                # If heartbeat hasn't changed since we joined, creator may have quit before we joined
                heartbeat_received_since_join = False
                if hasattr(self, '_last_heartbeat_when_joined') and self._last_heartbeat_when_joined:
                    heartbeat_received_since_join = (self.session_state.last_heartbeat > self._last_heartbeat_when_joined)
                
                
                if self.session_state.is_expired(timeout_seconds=15.0):
                    # CRITICAL: If we've received a heartbeat since joining, we know creator was alive after we joined
                    # If we haven't received a heartbeat since joining, check if enough time has passed
                    if not heartbeat_received_since_join:
                        # We never received a heartbeat since joining - creator may have quit before we joined
                        # Wait at least 15 seconds after joining before closing (to allow for heartbeat delay)
                        if self._session_joined_at:
                            time_since_join = (datetime.now() - self._session_joined_at).total_seconds()
                            if time_since_join < 15.0:
                                return
                        else:
                            # Fallback: if we don't have join time, use last_update check
                            if time_since_last_update < 20.0:
                                return
                    else:
                        # We received a heartbeat since joining, so creator was alive after we joined
                        # If heartbeat is now expired, creator has quit
                        pass
                    
                    # CRITICAL: Double-check that session is not already closed (may have been closed by another instance)
                    if self.session_state.state == 'closed':
                        if self.session_state_creator_check_timer:
                            self.session_state_creator_check_timer.stop()
                            self.session_state_creator_check_timer = None
                        return
                    
                    print(f"[Dialog] Creator disconnected (timeout 15s, heartbeat {time_since_heartbeat:.1f}s ago, last update {time_since_last_update:.1f}s ago), closing session...")
                    # Close the session
                    self.session_state.close()
                    self.session_manager.publishSessionState(self.session_state)
                    # Stop the timer since session is now closed
                    if self.session_state_creator_check_timer:
                        self.session_state_creator_check_timer.stop()
                        self.session_state_creator_check_timer = None
                    # Show warning message
                    QMessageBox.warning(self, "Session Closed", "The session creator has disconnected. The session has been closed.")
                    # CRITICAL: Reset dialog state instead of closing it (same behavior as Cancel)
                    # Save session_id before resetting session_state
                    closed_session_id = self.session_state.session_id if self.session_state else None
                    # Remove from available_sessions if present
                    if closed_session_id and closed_session_id in self.available_sessions:
                        del self.available_sessions[closed_session_id]
                    # Completely reset dialog state - we're no longer connected to a session
                    self.config.session_id = None
                    self.session_state = None
                    self._selected_session_id = None
                    self.seed_synced = False  # Reset seed sync status
                    # Reset connected instances tracking
                    self.ready_instances.clear()
                    self.connected_instances_snapshot = None
                    # CRITICAL: Reset seed status label (seed is no longer synchronized after session closure)
                    self.seed_status_label.setText("Seed: Not synchronized")
                    self.seed_status_label.setStyleSheet("padding: 5px; background-color: #f8d7da; border-radius: 3px;")
                    # Update state to SETUP to reset UI
                    self._updateState(self.STATE_SETUP)
                    # Update UI (defer to avoid recursive repaint)
                    QTimer.singleShot(0, self._updateConnectedInstances)
                    QTimer.singleShot(0, self._updateSessionsList)
            except Exception as e:
                print(f"[Dialog] Error in check_creator: {e}")
                import traceback
                traceback.print_exc()
                # Don't crash, just log the error
        
        self.session_state_creator_check_timer = QTimer(self)
        self.session_state_creator_check_timer.timeout.connect(check_creator)
        self.session_state_creator_check_timer.start(3000)  # Every 3 seconds
    
    def _subscribeToSeedSyncForTracking(self, base_handler=None):
        """Subscribe to seed sync topic to track connected instances
        
        Args:
            base_handler: Handler to wrap (if None, uses current handler) - DEPRECATED, kept for compatibility
        """
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            return
        
        # Initialize MQTT Handler Manager if not already done
        if not self._mqtt_handler_manager:
            self._mqtt_handler_manager = SGMQTTHandlerManager(self.model.mqttManager.client)
            self._mqtt_handler_manager.install()
        
        # Get seed sync topic
        session_topics = self.session_manager.getSessionTopics(self.config.session_id)
        seed_topic = session_topics[1]  # session_seed_sync
        
        # Remove existing seed sync tracking handler if any
        if self._seed_sync_tracking_handler_id is not None:
            self._mqtt_handler_manager.remove_handler(self._seed_sync_tracking_handler_id)
        
        # Create handler function for seed sync tracking
        def seed_sync_tracking_handler(client, userdata, msg):
            # Track instances via seed sync messages
            try:
                import json
                msg_dict = json.loads(msg.payload.decode("utf-8"))
                client_id = msg_dict.get('clientId')
                is_retained = msg.retain
                if client_id:
                    old_count = len(self.connected_instances)
                    is_new_instance = client_id not in self.connected_instances
                    
                    # CRITICAL: Only add instances if dialog is not READY yet
                    # After dialog becomes READY, we don't count new instances (they may be temporary or not yet configured)
                    # The snapshot is taken when dialog transitions to READY state
                    if self.connected_instances_snapshot is None:
                        self.connected_instances.add(client_id)
                        # Update UI if count changed (use QTimer to ensure thread safety)
                        if len(self.connected_instances) != old_count:
                            QTimer.singleShot(0, self._updateConnectedInstances)
                            
                            # NOTE: We do NOT republish seed sync when a new instance is detected
                            # This was causing infinite loops when multiple instances connect simultaneously.
                            # The periodic timer (every 3 seconds) is sufficient to ensure new instances
                            # receive our presence via retained messages.
            except Exception as e:
                print(f"[Dialog] Error tracking instance: {e}")
                import traceback
                traceback.print_exc()
            # CRITICAL: Do NOT forward seed sync messages to other handlers
            # They are not game topics and will be ignored anyway
        
        # Add handler using SGMQTTHandlerManager
        # stop_propagation=True because we don't want to forward seed_sync messages
        self._seed_sync_tracking_handler_id = self._mqtt_handler_manager.add_topic_handler(
            topic=seed_topic,
            handler_func=seed_sync_tracking_handler,
            priority=HandlerPriority.HIGH,
            stop_propagation=True  # Don't forward seed_sync messages to other handlers
        )
        
        # Subscribe to seed sync topic (to receive retained messages from other instances)
        # Note: We're already subscribed from syncSeed(), but this ensures we stay subscribed
        # Use qos=1 to ensure we receive all messages
        
        # CRITICAL: Check if we already have exactly the required number of instances BEFORE waiting
        # If so, take snapshot NOW to prevent instances that connect during wait from being counted
        if self.seed_synced and self.connected_instances_snapshot is None:
            if isinstance(self.config.num_players, int):
                required_instances = self.config.num_players
            else:
                required_instances = self.config.num_players_max
            
            if len(self.connected_instances) == required_instances:
                self.connected_instances_snapshot = self.connected_instances.copy()
        
        # CRITICAL: Do NOT unsubscribe/re-subscribe as this may prevent retained messages from being received
        # Instead, ensure we're subscribed and wait for retained messages to be processed
        # The handler is already installed, so any retained messages will be processed
        import time
        
        # CRITICAL: Wait for retained messages to be processed
        # Need sufficient delay to ensure all retained messages from other instances are received
        # This is especially important when multiple instances are already connected
        # IMPORTANT: Instances that have already left the dialog won't republish, so we must rely on retained messages
        time.sleep(1.5)  # Increased delay to ensure all retained messages are received
        
        # CRITICAL: Force a re-subscription WITHOUT unsubscribe to trigger retained messages
        # Some MQTT brokers only send retained messages on initial subscription
        # By re-subscribing (without unsubscribe), we ensure retained messages are sent again
        self.model.mqttManager.client.subscribe(seed_topic, qos=1)
        
        # Wait again after re-subscription for retained messages
        # CRITICAL: This delay is important because instances that left the dialog won't republish
        time.sleep(1.0)  # Increased delay to receive all retained messages after re-subscription
        
        # CRITICAL: Check if we have exactly the required number of instances and take snapshot NOW
        # This prevents instances that connect during the UI update delay from being counted
        if self.seed_synced and self.connected_instances_snapshot is None:
            if isinstance(self.config.num_players, int):
                required_instances = self.config.num_players
            else:
                required_instances = self.config.num_players_max
            
            if len(self.connected_instances) == required_instances:
                self.connected_instances_snapshot = self.connected_instances.copy()
            elif len(self.connected_instances) > required_instances:
                # We have more than required - take snapshot with only the first N instances
                instances_list = list(self.connected_instances)
                self.connected_instances_snapshot = set(instances_list[:required_instances])
        
        # Schedule UI update after a delay to catch any late messages
        # CRITICAL: Use sufficient delay to ensure all retained messages are processed
        # This is especially important when instances have already left the dialog
        QTimer.singleShot(1200, self._updateConnectedInstances)  # Increased delay to catch all messages
        
    
    def _subscribeToPlayerRegistrationForTracking(self):
        """Subscribe to player registration messages to track connected instances
        
        This is more reliable than seed sync messages because each player has a separate topic,
        so all retained messages are preserved (unlike seed sync where only the last retained message is kept).
        """
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            return
        
        # Initialize MQTT Handler Manager if not already done
        if not self._mqtt_handler_manager:
            self._mqtt_handler_manager = SGMQTTHandlerManager(self.model.mqttManager.client)
            self._mqtt_handler_manager.install()
        
        # Get player registration and disconnect topic bases
        session_topics = self.session_manager.getSessionTopics(self.config.session_id)
        registration_topic_base = session_topics[0]  # session_player_registration
        disconnect_topic_base = session_topics[2]  # session_player_disconnect
        
        # Subscribe to wildcard topics to receive all player registrations and disconnections
        registration_topic_wildcard = f"{registration_topic_base}/+"
        disconnect_topic_wildcard = f"{disconnect_topic_base}/+"
        
        # Remove existing player registration tracking handler if any
        if self._player_registration_tracking_handler_id is not None:
            self._mqtt_handler_manager.remove_handler(self._player_registration_tracking_handler_id)
        
        # Create handler function for player registration tracking
        def player_registration_tracking_handler(client, userdata, msg):
            # CRITICAL: Ignore callbacks during cleanup
            if hasattr(self, '_cleaning_up') and self._cleaning_up:
                return
            
            # Track instances via player registration messages
            if msg.topic.startswith(registration_topic_base):
                try:
                    import json
                    msg_dict = json.loads(msg.payload.decode("utf-8"))
                    client_id = msg_dict.get('clientId')
                    is_retained = msg.retain
                    
                    if client_id:
                        old_count = len(self.connected_instances)
                        is_new_instance = client_id not in self.connected_instances
                        
                        # CRITICAL: Only add instances if dialog is not READY yet
                        # After dialog becomes READY, we don't count new instances (they may be temporary or not yet configured)
                        # The snapshot is taken when dialog transitions to READY state
                        if self.connected_instances_snapshot is None:
                            self.connected_instances.add(client_id)
                            if len(self.connected_instances) != old_count:
                                retained_str = " (RETAINED)" if is_retained else " (NEW)"
                                QTimer.singleShot(0, self._updateConnectedInstances)
                except Exception as e:
                    print(f"[Dialog] Error tracking instance from player registration: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Track disconnections via player_disconnect messages
            elif msg.topic.startswith(disconnect_topic_base):
                try:
                    import json
                    msg_dict = json.loads(msg.payload.decode("utf-8"))
                    client_id = msg_dict.get('clientId')
                    
                    if client_id:
                        old_count = len(self.connected_instances)
                        old_ready_count = len(self.ready_instances)
                        old_snapshot_count = len(self.connected_instances_snapshot) if self.connected_instances_snapshot else 0
                        
                        # Remove from connected instances (always, even if snapshot exists)
                        if client_id in self.connected_instances:
                            self.connected_instances.remove(client_id)
                        
                        # Remove from ready instances
                        if client_id in self.ready_instances:
                            self.ready_instances.remove(client_id)
                        
                        # CRITICAL: Also remove from snapshot if it exists
                        # This ensures the UI updates correctly when an instance disconnects
                        if self.connected_instances_snapshot and client_id in self.connected_instances_snapshot:
                            self.connected_instances_snapshot.remove(client_id)
                        
                        # Update UI if counts changed
                        if (len(self.connected_instances) != old_count or 
                            len(self.ready_instances) != old_ready_count or
                            (self.connected_instances_snapshot and len(self.connected_instances_snapshot) != old_snapshot_count)):
                            QTimer.singleShot(0, self._updateConnectedInstances)
                except Exception as e:
                    print(f"[Dialog] Error tracking instance disconnect: {e}")
                    import traceback
                    traceback.print_exc()
        
        # Add handlers using SGMQTTHandlerManager for both registration and disconnect topics
        # Use prefix handlers since we're subscribing to wildcard topics
        self._player_registration_tracking_handler_id = self._mqtt_handler_manager.add_prefix_handler(
            topic_prefix=registration_topic_base,
            handler_func=player_registration_tracking_handler,
            priority=HandlerPriority.HIGH,
            stop_propagation=False  # Allow other handlers to process these messages too
        )
        
        # Also add handler for disconnect topic (using a filter function since we need two prefixes)
        def disconnect_topic_filter(topic: str) -> bool:
            return topic.startswith(disconnect_topic_base)
        
        self._player_disconnect_tracking_handler_id = self._mqtt_handler_manager.add_filter_handler(
            topic_filter=disconnect_topic_filter,
            handler_func=player_registration_tracking_handler,
            priority=HandlerPriority.HIGH,
            stop_propagation=False,
            description=f"disconnect:{disconnect_topic_base}"
        )
        
        # Subscribe to player registration and disconnect wildcard topics
        self.model.mqttManager.client.subscribe(registration_topic_wildcard, qos=1)
        self.model.mqttManager.client.subscribe(disconnect_topic_wildcard, qos=1)
        
        # Wait for retained messages to be received
        # CRITICAL: Player registration messages are published AFTER dialog closes, so they may not be available yet
        # But we still wait for any existing retained messages from previous sessions
        import time
        time.sleep(1.0)  # Sufficient delay to receive retained messages
        
        # Schedule UI update
        QTimer.singleShot(500, self._updateConnectedInstances)
    
    def _subscribeToGameStart(self):
        """Subscribe to game start topic for synchronization"""
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            return
        
        # Initialize MQTT Handler Manager if not already done
        if not self._mqtt_handler_manager:
            self._mqtt_handler_manager = SGMQTTHandlerManager(self.model.mqttManager.client)
            self._mqtt_handler_manager.install()
        
        # Get game start topic
        session_topics = self.session_manager.getSessionTopics(self.config.session_id)
        game_start_topic = session_topics[3]  # session_game_start (index 3: player_registration=0, seed_sync=1, player_disconnect=2, game_start=3)
        
        # Remove existing game start handler if any
        if self._game_start_handler_id is not None:
            self._mqtt_handler_manager.remove_handler(self._game_start_handler_id)
        
        # Create handler function for game start messages
        def game_start_handler(client, userdata, msg):
            # CRITICAL: Ignore callbacks during cleanup
            if hasattr(self, '_cleaning_up') and self._cleaning_up:
                return
            
            # Game start message received
            try:
                import json
                msg_dict = json.loads(msg.payload.decode("utf-8"))
                sender_client_id = msg_dict.get('clientId')
                start_type = msg_dict.get('start_type', 'unknown')
                
                # Check if already processed (avoid double processing)
                if hasattr(self, '_game_start_processed') and self._game_start_processed:
                    return
                
                # Mark as processed
                self._game_start_processed = True
                
                # Close dialog - use QMetaObject.invokeMethod to ensure we're in the main Qt thread
                # CRITICAL: QTimer.singleShot cannot be called from MQTT thread
                # Use QueuedConnection to execute accept() in the main thread
                from PyQt5.QtCore import QMetaObject, Qt
                QMetaObject.invokeMethod(
                    self, 
                    "accept", 
                    Qt.QueuedConnection
                )
            except Exception as e:
                print(f"[Dialog] Error processing game start message: {e}")
                import traceback
                traceback.print_exc()
        
        # Add handler using SGMQTTHandlerManager
        self._game_start_handler_id = self._mqtt_handler_manager.add_topic_handler(
            topic=game_start_topic,
            handler_func=game_start_handler,
            priority=HandlerPriority.HIGH,
            stop_propagation=True  # Don't forward game_start messages to other handlers
        )
        
        # Subscribe to game start topic
        result = self.model.mqttManager.client.subscribe(game_start_topic, qos=1)
        
        # Initialize processed flag
        self._game_start_processed = False
    
    def _publishGameStartMessage(self, start_type="manual"):
        """
        Publish game start message to synchronize all instances.
        
        Args:
            start_type (str): "manual" (button clicked) or "auto" (countdown finished)
        """
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            return
        
        # Get game start topic
        session_topics = self.session_manager.getSessionTopics(self.config.session_id)
        game_start_topic = session_topics[3]  # session_game_start (index 3: player_registration=0, seed_sync=1, player_disconnect=2, game_start=3)
        
        # Create start message
        from datetime import datetime
        start_msg = {
            'clientId': self.model.mqttManager.clientId,
            'timestamp': datetime.now().isoformat(),
            'start_type': start_type,  # "manual" or "auto"
            'countdown_finished': (start_type == "auto")
        }
        
        import json
        serialized_msg = json.dumps(start_msg)
        
        # CRITICAL: Publish with retain=False (we don't want old start messages)
        # Use QoS=1 to ensure delivery
        result = self.model.mqttManager.client.publish(
            game_start_topic, 
            serialized_msg, 
            qos=1,
            retain=False  # Don't retain - start message is one-time only
        )
        
        
        # Wait a moment to ensure message is sent before continuing
        import time
        time.sleep(0.1)  # Small delay to ensure message is queued
    
    def _publishInstanceReady(self):
        """Publish instance ready message and update session_state (Phase 2)"""
        """
        Publish instance ready signal to indicate this instance has completed seed sync
        and subscribed to game_start topic.
        
        Uses instance-specific topic to ensure all retained messages are preserved.
        """
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            return
        
        # Get instance ready topic base
        session_topics = self.session_manager.getSessionTopics(self.config.session_id)
        instance_ready_topic_base = session_topics[4]  # session_instance_ready (index 4)
        
        # Use instance-specific topic: {session_id}/session_instance_ready/{client_id}
        # This ensures all retained messages are preserved (one per instance)
        instance_ready_topic = f"{instance_ready_topic_base}/{self.model.mqttManager.clientId}"
        
        # Create ready message
        from datetime import datetime
        ready_msg = {
            'clientId': self.model.mqttManager.clientId,
            'timestamp': datetime.now().isoformat(),
            'seed_synced': True,
            'game_start_subscribed': True
        }
        
        import json
        serialized_msg = json.dumps(ready_msg)
        
        # Phase 1: Keep retain=True for instance_ready (needed for new joiners to see existing instances)
        # The explicit cleanup in _cancelConnection() prevents obsolete messages
        # Phase 2 will replace this with session_state
        # Use QoS=1 to ensure delivery
        result = self.model.mqttManager.client.publish(
            instance_ready_topic, 
            serialized_msg, 
            qos=1,
            retain=True  # Keep retain for discovery, but cleanup explicitly on disconnect
        )
        
        
        # Phase 2: Update session_state when instance becomes ready
        if self.session_state and self.model.mqttManager.clientId:
            if self.model.mqttManager.clientId not in self.session_state.connected_instances:
                self.session_state.add_instance(self.model.mqttManager.clientId)
                self.session_manager.publishSessionState(self.session_state)
        
        # Add ourselves to ready_instances immediately
        if self.model.mqttManager.clientId not in self.ready_instances:
            self.ready_instances.add(self.model.mqttManager.clientId)
            # Update UI to reflect that we are ready
            QTimer.singleShot(0, self._updateConnectedInstances)
        
        # CRITICAL: Add ourselves to session_instances_cache for the session we're connected to
        # This ensures the "Available Sessions" list shows the correct count including ourselves
        if self.config.session_id and self.model.mqttManager.clientId:
            if self.config.session_id not in self.session_instances_cache:
                self.session_instances_cache[self.config.session_id] = set()
            if self.model.mqttManager.clientId not in self.session_instances_cache[self.config.session_id]:
                self.session_instances_cache[self.config.session_id].add(self.model.mqttManager.clientId)
                # Update sessions list to show correct count
                if self.join_existing_radio.isChecked():
                    QTimer.singleShot(100, self._updateSessionsList)
    
    def _subscribeToInstanceReady(self):
        """
        Subscribe to instance ready topic to track which instances are ready.
        
        Uses wildcard subscription to receive ready signals from all instances.
        """
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            return
        
        # Get instance ready topic base and disconnect topic base
        session_topics = self.session_manager.getSessionTopics(self.config.session_id)
        instance_ready_topic_base = session_topics[4]  # session_instance_ready (index 4)
        disconnect_topic_base = session_topics[2]  # session_player_disconnect (index 2)
        
        # Subscribe to wildcard topic to receive ready signals from all instances
        # Format: {session_id}/session_instance_ready/+
        instance_ready_topic_wildcard = f"{instance_ready_topic_base}/+"
        
        # Also subscribe to player_disconnect to track disconnections
        # Format: {session_id}/session_player_disconnect/+
        disconnect_topic_wildcard = f"{disconnect_topic_base}/+"
        
        # Initialize MQTT Handler Manager if not already done
        if not self._mqtt_handler_manager:
            self._mqtt_handler_manager = SGMQTTHandlerManager(self.model.mqttManager.client)
            self._mqtt_handler_manager.install()
        
        # Remove existing instance ready handlers if any
        if self._instance_ready_handler_id is not None:
            self._mqtt_handler_manager.remove_handler(self._instance_ready_handler_id)
        if self._instance_ready_disconnect_handler_id is not None:
            self._mqtt_handler_manager.remove_handler(self._instance_ready_disconnect_handler_id)
        
        # Create handler function for instance ready messages
        def instance_ready_handler(client, userdata, msg):
            # Handle instance ready messages
            try:
                import json
                # Ignore empty messages (used to clear retained messages)
                payload_str = msg.payload.decode("utf-8")
                if not payload_str or payload_str.strip() == "":
                    return
                
                msg_dict = json.loads(payload_str)
                sender_client_id = msg_dict.get('clientId')
                
                if sender_client_id:
                    # CRITICAL: Also update session_instances_cache for the sessions list display
                    # Extract session_id from topic (format: {session_id}/session_instance_ready/{client_id})
                    if self.config.session_id:
                        session_id = self.config.session_id
                        # Initialize instances cache for this session if needed
                        if session_id not in self.session_instances_cache:
                            self.session_instances_cache[session_id] = set()
                        old_instances_count = len(self.session_instances_cache[session_id])
                        self.session_instances_cache[session_id].add(sender_client_id)
                        new_instances_count = len(self.session_instances_cache[session_id])
                        
                        # Update sessions list if instances count changed
                        # Note: _updateSessionsList() preserves the visual selection, so we can update even if a session is selected
                        if new_instances_count != old_instances_count:
                            QTimer.singleShot(100, self._updateSessionsList)
                    
                    # Add to ready_instances (whether it's us or another instance)
                    if sender_client_id not in self.ready_instances:
                        self.ready_instances.add(sender_client_id)
                        if sender_client_id != self.model.mqttManager.clientId:
                            # Update UI to reflect new ready instance
                            QTimer.singleShot(0, self._updateConnectedInstances)
            except Exception as e:
                print(f"[Dialog] Error processing instance ready message: {e}")
                import traceback
                traceback.print_exc()
        
        # Create handler function for player disconnect messages (in instance ready context)
        def instance_ready_disconnect_handler(client, userdata, msg):
            # Handle player disconnect messages (to remove instances from cache)
            try:
                import json
                # Ignore empty messages (used to clear retained messages)
                payload_str = msg.payload.decode("utf-8")
                if not payload_str or payload_str.strip() == "":
                    return
                
                msg_dict = json.loads(payload_str)
                client_id = msg_dict.get('clientId')
                
                # Remove instance from cache
                if client_id and self.config.session_id:
                    session_id = self.config.session_id
                    if session_id in self.session_instances_cache:
                        old_instances_count = len(self.session_instances_cache[session_id])
                        if client_id in self.session_instances_cache[session_id]:
                            self.session_instances_cache[session_id].remove(client_id)
                        new_instances_count = len(self.session_instances_cache[session_id])
                        
                        # Update sessions list if instances count changed
                        if new_instances_count != old_instances_count:
                            QTimer.singleShot(100, self._updateSessionsList)
                    
                    # Remove from ready_instances
                    if client_id in self.ready_instances:
                        self.ready_instances.remove(client_id)
                        # Update UI to reflect disconnected instance
                        QTimer.singleShot(0, self._updateConnectedInstances)
            except Exception as e:
                print(f"[Dialog] Error processing player disconnect message: {e}")
                import traceback
                traceback.print_exc()
        
        # Add handlers using SGMQTTHandlerManager
        self._instance_ready_handler_id = self._mqtt_handler_manager.add_prefix_handler(
            topic_prefix=instance_ready_topic_base,
            handler_func=instance_ready_handler,
            priority=HandlerPriority.HIGH,
            stop_propagation=True  # Don't forward instance_ready messages
        )
        
        # Add handler for disconnect topic (using a filter function)
        def disconnect_topic_filter(topic: str) -> bool:
            return topic.startswith(disconnect_topic_base)
        
        self._instance_ready_disconnect_handler_id = self._mqtt_handler_manager.add_filter_handler(
            topic_filter=disconnect_topic_filter,
            handler_func=instance_ready_disconnect_handler,
            priority=HandlerPriority.HIGH,
            stop_propagation=False,  # Allow other handlers to process disconnect messages too
            description=f"instance_ready_disconnect:{disconnect_topic_base}"
        )
        
        # CRITICAL: Unsubscribe first to force broker to send retained messages on resubscribe
        # This ensures we receive retained messages even if we were previously subscribed
        import time
        try:
            self.model.mqttManager.client.unsubscribe(instance_ready_topic_wildcard)
            time.sleep(0.1)  # Brief delay to ensure unsubscribe is processed
        except Exception:
            pass  # Ignore unsubscribe errors
        
        # Subscribe to wildcard topic to receive ready signals from all instances
        result = self.model.mqttManager.client.subscribe(instance_ready_topic_wildcard, qos=1)
        
        # Subscribe to player_disconnect to track disconnections
        result = self.model.mqttManager.client.subscribe(disconnect_topic_wildcard, qos=1)
        
        # Wait a moment for retained messages to be received
        # Increased delay to ensure all retained messages are received
        time.sleep(1.5)  # Increased delay to receive retained ready messages from all instances
        
        # CRITICAL: Ensure session_instances_cache is synchronized with ready_instances
        # This handles cases where retained messages were received but cache wasn't updated
        if self.config.session_id:
            session_id = self.config.session_id
            if session_id not in self.session_instances_cache:
                self.session_instances_cache[session_id] = set()
            # Add all ready instances to cache (in case some were missed)
            for client_id in self.ready_instances:
                self.session_instances_cache[session_id].add(client_id)
            # Update sessions list to reflect correct count
            QTimer.singleShot(100, self._updateSessionsList)
        
        # Update connected instances after receiving retained messages
        # This ensures the UI shows the correct count of connected instances
        QTimer.singleShot(100, self._updateConnectedInstances)
    
    def _onStartNowClicked(self):
        """Handle Start Now button click - only available on creator instance"""
        # Only creator can click this button (UI enforces this)
        if not self.config.is_session_creator:
            return
        
        # Validate minimum is reached
        if isinstance(self.config.num_players, int):
            min_required = self.config.num_players
        else:
            min_required = self.config.num_players_min
        
        # Use snapshot if available, otherwise use current count of ready instances
        # Only count instances that have completed seed sync AND subscribed to game_start
        if self.connected_instances_snapshot is not None:
            num_instances = len(self.connected_instances_snapshot)
        else:
            num_instances = len(self.ready_instances)
        
        if num_instances < min_required:
            QMessageBox.warning(
                self,
                "Insufficient Instances",
                f"Only {num_instances} instance(s) connected, but {min_required} required."
            )
            return
        
        # Publish start message
        self._publishGameStartMessage(start_type="manual")
        
        # Wait for message propagation, then close
        QTimer.singleShot(300, self.accept)
    
    def _isConnected(self):
        """Check if MQTT connection is established and seed is synced"""
        return (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected() and
                self.seed_synced)
    
    def _cancelConnection(self):
        """Cancel connection and reset interface to initial state"""
        # Set cleaning flag to prevent MQTT callbacks during cleanup
        self._cleaning_up = True
        
        try:
            # Phase 2: Update session_state before disconnection
            if self.session_state and self.model.mqttManager.clientId:
                if self.session_state.is_creator(self.model.mqttManager.clientId):
                    # Creator: Close the session
                    self.session_state.close()
                    self.session_manager.publishSessionState(self.session_state)
                else:
                    # Non-creator: Remove instance from session
                    self.session_state.remove_instance(self.model.mqttManager.clientId)
                    self.session_manager.publishSessionState(self.session_state)
                
                # Stop heartbeat and creator check timers
                if self.session_state_heartbeat_timer:
                    self.session_state_heartbeat_timer.stop()
                    self.session_state_heartbeat_timer = None
                if self.session_state_creator_check_timer:
                    self.session_state_creator_check_timer.stop()
                    self.session_state_creator_check_timer = None
            
            # 1. Stop all timers (prevents callbacks on invalid state)
            if hasattr(self, 'seed_republish_timer') and self.seed_republish_timer:
                if self.seed_republish_timer.isActive():
                    self.seed_republish_timer.stop()
            
            if hasattr(self, 'auto_start_timer') and self.auto_start_timer:
                if self.auto_start_timer.isActive():
                    self.auto_start_timer.stop()
            
            if hasattr(self, 'seed_check_timer') and self.seed_check_timer:
                if self.seed_check_timer.isActive():
                    self.seed_check_timer.stop()
            
            # 2. Clean retained messages BEFORE publishing disconnect message
            # This prevents obsolete retained messages from being received by new subscribers
            if (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected() and
                self.config.session_id):
                try:
                    import json
                    session_topics = self.session_manager.getSessionTopics(self.config.session_id)
                    client_id = self.model.mqttManager.clientId
                    
                    if client_id:
                        # Get assigned_player_name from config or session_manager
                        assigned_player_name = self.config.assigned_player_name
                        if not assigned_player_name and self.session_manager:
                            # Try to get from session_manager.connected_players
                            for player_name, cid in self.session_manager.connected_players.items():
                                if cid == client_id:
                                    assigned_player_name = player_name
                                    break
                        
                        # Clean player_registration retained message
                        if assigned_player_name:
                            registration_topic_base = session_topics[0]  # session_player_registration
                            registration_topic = f"{registration_topic_base}/{assigned_player_name}"
                            # Publish empty message with retain=True to clear retained message
                            result = self.model.mqttManager.client.publish(registration_topic, "", qos=1, retain=True)
                        
                        # Clean instance_ready retained message
                        instance_ready_topic_base = session_topics[4]  # session_instance_ready
                        instance_ready_topic = f"{instance_ready_topic_base}/{client_id}"
                        # Publish empty message with retain=True to clear retained message
                        result = self.model.mqttManager.client.publish(instance_ready_topic, "", qos=1, retain=True)
                        
                        # Wait a moment for messages to be published and propagated
                        import time
                        time.sleep(0.2)  # Brief delay to ensure messages are published
                except Exception as e:
                    print(f"[Dialog] Error clearing retained messages: {e}")
                    import traceback
                    traceback.print_exc()
            
            # 3. Publish disconnect message AFTER cleaning retained messages
            # This ensures other instances are notified of the disconnection
            if (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected() and
                self.config.session_id):
                try:
                    from datetime import datetime
                    import json
                    session_topics = self.session_manager.getSessionTopics(self.config.session_id)
                    disconnect_topic_base = session_topics[2]  # session_player_disconnect
                    # Use client_id as identifier (even if no player selected)
                    client_id = self.model.mqttManager.clientId
                    if client_id:
                        # Publish disconnect message using client_id as identifier
                        disconnect_topic = f"{disconnect_topic_base}/{client_id}"
                        disconnect_msg = {
                            'clientId': client_id,
                            'assigned_player_name': None,  # May be None if no player selected
                            'timestamp': datetime.now().isoformat()
                        }
                        serialized_msg = json.dumps(disconnect_msg)
                        # Publish with retain=False (one-time message)
                        result = self.model.mqttManager.client.publish(disconnect_topic, serialized_msg, qos=1, retain=False)
                        # Wait for message to be published and propagated
                        if result.rc == 0:  # MQTT_ERR_SUCCESS
                            # Give MQTT time to publish and propagate the message
                            # Note: client.loop_start() is already running in background,
                            # so we don't need to call loop() manually
                            import time
                            time.sleep(0.3)  # Wait for message to be published and propagated
                except Exception as e:
                    print(f"[Dialog] Error publishing disconnect message: {e}")
                    import traceback
                    traceback.print_exc()
            
            # 4. Disconnect session manager (cleans handlers, but messages already published)
            if self.session_manager:
                self.session_manager.disconnect()
            
            # 5. Unsubscribe from session topics (but stay connected to broker)
            # This allows the user to reconnect to a different session without reconnecting to broker
            # NOTE: We only unsubscribe from the session we were connected to, not from discovered sessions
            # Discovered sessions remain subscribed via _subscribeToSessionPlayerRegistrations()
            if (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected() and
                self.config.session_id):
                try:
                    disconnected_session_id = self.config.session_id
                    session_topics = self.session_manager.getSessionTopics(disconnected_session_id)
                    # Unsubscribe from all session topics for the disconnected session
                    for topic_base in session_topics:
                        if topic_base:
                            # Unsubscribe from wildcard topics
                            if topic_base in ['player_registration', 'player_disconnect', 'instance_ready']:
                                wildcard_topic = f"{disconnected_session_id}/session_{topic_base}/+"
                                self.model.mqttManager.client.unsubscribe(wildcard_topic)
                            else:
                                topic = f"{disconnected_session_id}/session_{topic_base}"
                                self.model.mqttManager.client.unsubscribe(topic)
                    
                    # CRITICAL: Re-subscribe to discovered sessions to ensure we receive instance_ready messages
                    # This is needed because we may have unsubscribed from a session that is also in discovered sessions
                    # We need to re-subscribe via _subscribeToSessionPlayerRegistrations() to get retained messages
                    # Use a longer delay to ensure unsubscribe is fully processed before resubscribe
                    if self.available_sessions:
                        # Use longer delay and force unsubscribe/resubscribe to ensure we get retained messages
                        # Use non-blocking approach with QTimer.singleShot instead of time.sleep
                        def force_unsubscribe():
                            # Force unsubscribe first to ensure we get retained messages on resubscribe
                            for session_id in self.available_sessions.keys():
                                instance_ready_topic_wildcard = f"{session_id}/session_instance_ready/+"
                                try:
                                    self.model.mqttManager.client.unsubscribe(instance_ready_topic_wildcard)
                                except Exception:
                                    pass
                            # Use QTimer.singleShot for non-blocking delay
                            QTimer.singleShot(200, lambda: self._subscribeToSessionPlayerRegistrations())
                        QTimer.singleShot(1000, force_unsubscribe)
                except Exception as e:
                    print(f"[Dialog] Error unsubscribing from session topics: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Note: We do NOT disconnect from MQTT broker here
            # This allows the user to reconnect to a different session without reconnecting to broker
            # If the user wants to disconnect completely, they can close the dialog
            
            # 6. Reset internal states
            self.seed_synced = False
            self.synced_seed_value = None
            self.connected_instances.clear()
            self.ready_instances.clear()
            self.connected_instances_snapshot = None
            self._connection_in_progress = False
            self._game_start_processed = False
            
            # NOTE: We do NOT remove the session from session_instances_cache here
            # Even though we disconnect, we remain subscribed to instance_ready for discovered sessions
            # via _subscribeToSessionPlayerRegistrations(), so the cache will be updated automatically
            # when we receive instance_ready messages (retained or new) for that session.
            # This ensures the cache stays accurate for sessions we're not connected to.
            
            # 7. Reset interface (return to STATE_SETUP)
            self._updateState(self.STATE_SETUP)
            
            # 8. Reset session_id if in Join mode, or generate new one if in Create mode (creator)
            if self.join_existing_radio.isChecked():
                self._selected_session_id = None
                self.config.session_id = None
                # Clear session list selection if exists
                if hasattr(self, 'session_list') and self.session_list:
                    self.session_list.clearSelection()
            elif self.create_new_radio.isChecked():
                # CRITICAL: Generate new session_id for creator (old one is obsolete)
                self.config.generate_session_id()
                self.session_id_edit.setText(self.config.session_id)
            
            # 9. Remove all handlers using SGMQTTHandlerManager
            if self._mqtt_handler_manager:
                if self._game_start_handler_id is not None:
                    self._mqtt_handler_manager.remove_handler(self._game_start_handler_id)
                    self._game_start_handler_id = None
                if self._seed_sync_tracking_handler_id is not None:
                    self._mqtt_handler_manager.remove_handler(self._seed_sync_tracking_handler_id)
                    self._seed_sync_tracking_handler_id = None
                if self._player_registration_tracking_handler_id is not None:
                    self._mqtt_handler_manager.remove_handler(self._player_registration_tracking_handler_id)
                    self._player_registration_tracking_handler_id = None
                if self._player_disconnect_tracking_handler_id is not None:
                    self._mqtt_handler_manager.remove_handler(self._player_disconnect_tracking_handler_id)
                    self._player_disconnect_tracking_handler_id = None
                if self._instance_ready_handler_id is not None:
                    self._mqtt_handler_manager.remove_handler(self._instance_ready_handler_id)
                    self._instance_ready_handler_id = None
                if self._instance_ready_disconnect_handler_id is not None:
                    self._mqtt_handler_manager.remove_handler(self._instance_ready_disconnect_handler_id)
                    self._instance_ready_disconnect_handler_id = None
                if self._session_player_registration_tracker_handler_id is not None:
                    self._mqtt_handler_manager.remove_handler(self._session_player_registration_tracker_handler_id)
                    self._session_player_registration_tracker_handler_id = None
                if self._session_state_discovery_handler_id is not None:
                    self._mqtt_handler_manager.remove_handler(self._session_state_discovery_handler_id)
                    self._session_state_discovery_handler_id = None
                if self._session_discovery_handler_id is not None:
                    self._mqtt_handler_manager.remove_handler(self._session_discovery_handler_id)
                    self._session_discovery_handler_id = None
                if self._session_state_connected_handler_id is not None:
                    self._mqtt_handler_manager.remove_handler(self._session_state_connected_handler_id)
                    self._session_state_connected_handler_id = None
            
            # 10. Update connection status based on actual MQTT client state
            # Don't force "Not connected" if client is still connected to broker
            if (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
                # Client still connected to broker (we only unsubscribed from session topics)
                self.connection_status = "Connected to broker"
                self.status_label.setText(f"Connection Status: [●] {self.connection_status}")
                self.status_label.setStyleSheet("padding: 5px; background-color: #d4edda; border-radius: 3px; color: #155724;")
            else:
                # Client disconnected from broker
                self.connection_status = "Not connected"
                self.status_label.setText(f"Connection Status: {self.connection_status}")
                self.status_label.setStyleSheet("padding: 5px; background-color: #f8d7da; border-radius: 3px; color: #721c24;")
            
            # Reset seed status (seed is no longer synchronized after cancel)
            self.seed_status_label.setText("Seed: Not synchronized")
            self.seed_status_label.setStyleSheet("padding: 5px; background-color: #f8d7da; border-radius: 3px;")
            
        except Exception as e:
            print(f"[Dialog] Error during connection cancellation: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Clear cleaning flag
            self._cleaning_up = False
    
    def reject(self):
        """Override reject to handle Cancel button based on connection state"""
        # Case 1: Not connected yet -> normal behavior (close dialog)
        if not self._isConnected():
            super().reject()
            return
        
        # Case 2 & 3: Connected -> cancel connection and reset interface
        self._cancelConnection()
        # Don't call super().reject() - stay in dialog
    
    def closeEvent(self, event):
        """Handle dialog close event - cleanup session discovery and connection"""
        # If connected, cancel connection first
        if self._isConnected():
            self._cancelConnection()
        
        # Stop session discovery if running
        if self.session_manager.session_discovery_handler:
            self.session_manager.stopSessionDiscovery()
        
        # Stop session heartbeat if running
        self.session_manager.stopSessionHeartbeat()
        
        # Stop seed republish timer
        if hasattr(self, 'seed_republish_timer') and self.seed_republish_timer:
            if self.seed_republish_timer.isActive():
                self.seed_republish_timer.stop()
        
        event.accept()
    
    def _checkSeedSync(self):
        """Periodically check if seed sync completed (called by timer)"""
        if self.seed_synced:
            # Seed synced, stop checking
            self.seed_check_timer.stop()
    
    def _republishSeedSync(self):
        """Republish seed sync message periodically to ensure new instances can detect us"""
        # OPTIMIZATION: Don't republish if dialog is READY (no need to keep broadcasting)
        if self.connected_instances_snapshot is not None:
            return  # Dialog is READY, stop republishing
        
        if not self.seed_synced:
            return  # Don't republish if seed not synced yet
        
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            return
        
        if not self.config.session_id:
            return
        
        # CRITICAL: Cooldown check to prevent infinite loops
        import time
        current_time = time.time()
        if (current_time - self._last_republish_time) < self._republish_cooldown:
            return  # Too soon since last republish, skip to prevent loops
        
        # Get seed sync topic
        session_topics = self.session_manager.getSessionTopics(self.config.session_id)
        seed_topic = session_topics[1]  # session_seed_sync
        
        # Republish our seed sync message
        seed_msg = {
            'clientId': self.model.mqttManager.clientId,
            'seed': self.synced_seed_value,
            'is_leader': False,
            'timestamp': datetime.now().isoformat()
        }
        import json
        serialized_msg = json.dumps(seed_msg)
        self.model.mqttManager.client.publish(seed_topic, serialized_msg, qos=1, retain=True)
        
        # Update last republish time
        self._last_republish_time = current_time
    
    def _startAutoStartCountdown(self):
        """Start 3-second countdown before auto-starting"""
        if self.auto_start_timer:
            self.auto_start_timer.stop()
        
        self.auto_start_countdown = 3
        self.countdown_label.show()
        self.countdown_label.setText(f"⏱️ Starting automatically in: {self.auto_start_countdown}...")
        
        self.auto_start_timer = QTimer(self)
        self.auto_start_timer.timeout.connect(self._updateCountdown)
        self.auto_start_timer.start(1000)  # Update every second
    
    def _updateCountdown(self):
        """Update countdown timer"""
        if self.state_manager.current_state != ConnectionState.READY_MAX:
            # State changed, stop countdown
            if self.auto_start_timer:
                self.auto_start_timer.stop()
            self.countdown_label.hide()
            return
        
        # Check if still at maximum (countdown only runs at maximum)
        # Use snapshot if dialog is READY to avoid counting instances that connect after READY state
        # Only count instances that have completed seed sync AND subscribed to game_start
        if self.connected_instances_snapshot is not None:
            num_instances = len(self.connected_instances_snapshot)
        else:
            num_instances = len(self.ready_instances)
        
        # Check if still at maximum (countdown only runs at maximum)
        if isinstance(self.config.num_players, int):
            required_instances = self.config.num_players
        else:
            required_instances = self.config.num_players_max  # Check maximum, not minimum
        
        if num_instances < required_instances:
            # Not ready anymore, stop countdown
            if self.auto_start_timer:
                self.auto_start_timer.stop()
            self.countdown_label.hide()
            # Transition back to STATE_READY_MIN or STATE_WAITING
            if isinstance(self.config.num_players, int):
                min_required = self.config.num_players
            else:
                min_required = self.config.num_players_min
            if num_instances >= min_required:
                self._updateState(self.STATE_READY_MIN)
            else:
                self._updateState(self.STATE_WAITING)
            return
        
        self.auto_start_countdown -= 1
        
        if self.auto_start_countdown > 0:
            self.countdown_label.setText(f"⏱️ Starting automatically in: {self.auto_start_countdown}...")
        else:
            # Countdown finished - publish start message (creator only)
            if self.auto_start_timer:
                self.auto_start_timer.stop()
            self.countdown_label.setText("Starting now...")
            
            # Publish start message if creator, then wait for propagation
            if self.config.is_session_creator:
                self._publishGameStartMessage(start_type="auto")
                # Creator also needs to close dialog after publishing
                # Wait for message propagation, then close
                QTimer.singleShot(300, self.accept)
            else:
                # Non-creator instance: wait for start message from creator
                pass
                # Don't close yet - wait for game start message
    
    def accept(self):
        """Override accept to validate before closing"""
        if not self.seed_synced:
            QMessageBox.warning(self, "Seed Not Synchronized", 
                              "Please wait for seed synchronization to complete.")
            return
        
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            QMessageBox.warning(self, "Not Connected", "Please connect to the broker first.")
            return
        
        # Validate number of instances
        # Phase 2: Use session_state as single source of truth (same logic as _updateConnectedInstances)
        if self.session_state:
            # Use session_state.connected_instances as source of truth
            num_instances = self.session_state.get_num_connected()
        else:
            # Fallback to old method if session_state not available yet
            # Use snapshot if dialog is READY to ensure consistent counting
            if self.connected_instances_snapshot is not None:
                num_instances = len(self.connected_instances_snapshot)
            else:
                # Fallback to ready_instances (instances that have completed seed sync and subscribed to game_start)
                num_instances = len(self.ready_instances)
        
        # Check minimum requirement (for manual start)
        if isinstance(self.config.num_players, int):
            min_required = self.config.num_players
        else:
            min_required = self.config.num_players_min
        
        if num_instances < min_required:
            reply = QMessageBox.question(
                self,
                "Insufficient Instances",
                f"Only {num_instances} instance(s) connected, but {min_required} required.\n"
                "Do you want to continue anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Stop countdown if running
        if self.auto_start_timer:
            self.auto_start_timer.stop()
        
        super().accept()
