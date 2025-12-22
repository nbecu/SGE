# --- Standard library imports ---
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


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
    
    # Dialog states
    STATE_SETUP = "setup"
    STATE_CONNECTING = "connecting"
    STATE_WAITING = "waiting"
    STATE_READY = "ready"
    
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
        self.connected_instances = set()  # Set of clientIds connected to this session
        self.connected_instances_snapshot = None  # Snapshot of connected instances when dialog becomes ready
        self.current_state = self.STATE_SETUP
        self.auto_start_countdown = None  # Countdown timer for auto-start (3, 2, 1...)
        self.auto_start_timer = None  # QTimer for countdown
        self.available_sessions = {}  # Dict of available sessions: {session_id: session_info}
        self.session_players_cache = {}  # Cache of registered players per session: {session_id: set of player_names}
        self.session_discovery_handler = None  # Handler for session discovery
        self._should_start_discovery_on_connect = False  # Flag to start discovery automatically after connection
        self._connection_in_progress = False  # Flag to prevent multiple simultaneous connection attempts
        self._selected_session_id = None  # Session ID selected by user in join mode
        self._temporary_session_id = None  # Temporary session_id used for connection (not a selected session)
        
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
        
        # Seed Sync Status (simplified - no seed value shown)
        self.seed_status_label = QLabel("Seed Status: Not synchronized")
        self.seed_status_label.setStyleSheet("padding: 5px; background-color: #fff8dc; border-radius: 3px;")
        layout.addWidget(self.seed_status_label)
        
        # Connected Instances Section
        instances_group = QGroupBox("Connected Instances")
        instances_layout = QVBoxLayout()
        self.connected_instances_label = QLabel("No instances connected yet")
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
        button_layout.addWidget(self.cancel_button)
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self._onConnect)
        button_layout.addWidget(self.connect_button)
        
        self.start_button = QPushButton("Start Now")
        self.start_button.clicked.connect(self.accept)
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
                # Restore seed tracking wrapper if it exists
                if hasattr(self, '_seed_tracking_wrapper') and self._seed_tracking_wrapper:
                    self.model.mqttManager.client.on_message = self._seed_tracking_wrapper
            
            # Enable Connect button in create mode
            self.connect_button.setEnabled(True)
            self.connect_button.show()
            
            # Adjust window size after hiding/showing elements
            self.adjustSize()
        else:
            # Join existing session mode
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
                print(f"[Dialog] Already connected, starting session discovery immediately...")
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
                    print(f"[Dialog] Join existing mode selected, starting connection automatically...")
                    self._updateState(self.STATE_CONNECTING)
                    self._connectToBroker()
            
            self.info_label.setText("Select a session from the list below, then click 'Connect' to join it.")
            
            # Adjust window size after showing sessions list
            self.adjustSize()
    
    def _startSessionDiscovery(self):
        """Start session discovery"""
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            return
        
        def onSessionsDiscovered(sessions_dict):
            """Callback when sessions are discovered"""
            # sessions_dict already contains only active sessions (expired ones filtered in SessionManager)
            self.available_sessions = sessions_dict
            
            # Subscribe to player registration topics for all discovered sessions to get player counts
            # This will receive retained messages for already-registered players
            self._subscribeToSessionPlayerRegistrations()
            
            # List will be updated by _subscribeToSessionPlayerRegistrations after receiving retained messages
        
        # Start discovery
        print(f"[Dialog] Starting session discovery...")
        self.session_manager.discoverSessions(callback=onSessionsDiscovered)
    
    def _subscribeToSessionPlayerRegistrations(self):
        """Subscribe to player registration topics for all discovered sessions to track player counts"""
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            return
        
        # Get current handler (might be seed tracking wrapper or discovery handler)
        current_handler = self.model.mqttManager.client.on_message
        
        # Create wrapper to track player registrations for discovered sessions
        def player_registration_tracker(client, userdata, msg):
            # Check if this is a player registration message for a discovered session
            for session_id in self.available_sessions.keys():
                registration_topic_base = f"{session_id}/session_player_registration"
                if msg.topic.startswith(registration_topic_base + "/"):
                    try:
                        import json
                        msg_dict = json.loads(msg.payload.decode("utf-8"))
                        player_name = msg_dict.get('assigned_player_name')
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
                    # Don't forward - this is just for tracking
                    return
            
            # Forward other messages to current handler (seed tracking, discovery, game messages)
            if current_handler:
                current_handler(client, userdata, msg)
        
        # Install wrapper BEFORE subscribing (critical for receiving retained messages)
        # Store reference to avoid garbage collection
        self._player_registration_tracker = player_registration_tracker
        self.model.mqttManager.client.on_message = player_registration_tracker
        
        # Subscribe to player registration topics for all discovered sessions
        for session_id in self.available_sessions.keys():
            registration_topic_wildcard = f"{session_id}/session_player_registration/+"
            self.model.mqttManager.client.subscribe(registration_topic_wildcard, qos=1)
        
        # Wait for retained messages to be received, then update list
        import time
        time.sleep(0.3)
        
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
            
            # Get number of registered players for this session from cache
            registered_players = self.session_players_cache.get(session_id, set())
            num_registered = len(registered_players)
            
            # Build players text with availability info
            if num_min == num_max:
                if num_registered >= num_max:
                    players_text = f"{num_registered}/{num_max} players (Full)"
                    is_full = True
                else:
                    players_text = f"{num_registered}/{num_max} players (Available)"
                    is_full = False
            else:
                if num_registered >= num_max:
                    players_text = f"{num_registered}/{num_max} players (Full)"
                    is_full = True
                elif num_registered >= num_min:
                    players_text = f"{num_registered}/{num_min}-{num_max} players (Ready)"
                    is_full = False
                else:
                    players_text = f"{num_registered}/{num_min}-{num_max} players (Available)"
                    is_full = False
            
            display_text = f"{model_name} ({players_text})"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, session_id)
            
            # Style full sessions differently
            if is_full:
                item.setForeground(QColor("#888"))  # Gray color for full sessions
                font = item.font()
                font.setItalic(True)
                item.setFont(font)
            
            tooltip_text = f"Session ID: {session_id}\nModel: {model_name}\nPlayers: {players_text}"
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
        
        print(f"[Dialog] Updated sessions list: {len(sorted_sessions)} active session(s) found")
    
    def _onSessionClicked(self, item):
        """Handle single click on a session in the list - selects the session"""
        session_id = item.data(Qt.UserRole)
        if session_id:
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
            self.connected_instances_label.setText("No instances connected yet")
            self._updateState(self.STATE_SETUP)
            return
        
        try:
            # CRITICAL: Use snapshot if dialog is READY to avoid counting instances that connect after READY state
            # This prevents counting temporary connections or instances that connect after we have enough instances
            # The snapshot is taken when dialog transitions to READY state
            if self.connected_instances_snapshot is not None:
                # Snapshot available (dialog is READY) - use it to avoid counting new instances
                instances_to_count = self.connected_instances_snapshot
                print(f"[DIAGNOSTIC] Using snapshot for counting: {len(instances_to_count)} instances (snapshot taken when dialog became READY)")
                print(f"[DIAGNOSTIC] Current connected_instances has {len(self.connected_instances)} instances (may include new connections)")
            else:
                # Snapshot not available yet (dialog not READY) - count all instances
                # This allows instances to be counted as they connect during the waiting period
                instances_to_count = self.connected_instances
                print(f"[DIAGNOSTIC] No snapshot yet (dialog not READY), using current count: {len(instances_to_count)} instances")
            
            num_instances = len(instances_to_count)
            
            # Determine required number of instances
            if isinstance(self.config.num_players, int):
                required_instances = self.config.num_players
            else:
                required_instances = self.config.num_players_max
            
            # Update display
            if num_instances > 0:
                status_text = f"{num_instances}/{required_instances} instance(s) connected"
                if num_instances >= required_instances:
                    status_text += " ✓"
                    self.connected_instances_label.setStyleSheet("padding: 5px; color: #27ae60; font-weight: bold;")
                else:
                    status_text += f" (waiting for {required_instances - num_instances} more...)"
                    self.connected_instances_label.setStyleSheet("padding: 5px; color: #f39c12; font-weight: bold;")
                self.connected_instances_label.setText(status_text)
            else:
                self.connected_instances_label.setText("No instances connected yet")
                self.connected_instances_label.setStyleSheet("padding: 5px; color: #666;")
            
            # Check if ready to start
            # Both modes should transition to READY when conditions are met
            # The difference is only in auto-start countdown (handled in _updateState)
            if self.seed_synced and num_instances >= required_instances:
                # CRITICAL: Take snapshot IMMEDIATELY when we first detect EXACTLY the required number of instances
                # This prevents counting instances that connect after we have enough
                # We use == instead of >= to take snapshot only once, at the exact moment we reach the required count
                if self.connected_instances_snapshot is None and num_instances == required_instances:
                    self.connected_instances_snapshot = self.connected_instances.copy()
                    print(f"[DIAGNOSTIC] Snapshot taken IMMEDIATELY when EXACTLY {required_instances} instances detected: {len(self.connected_instances_snapshot)} instances frozen")
                    print(f"[DIAGNOSTIC] Snapshot contains: {list(self.connected_instances_snapshot)}")
                    print(f"[DIAGNOSTIC] NOTE: Instances connecting after this point will NOT be counted")
                elif self.connected_instances_snapshot is None and num_instances > required_instances:
                    # We have more than required - this means an instance connected after we reached the required count
                    # Take snapshot with only the first N instances (where N = required_instances)
                    # We need to identify which instances were present when we first reached the required count
                    # Since we can't track history, we'll take the snapshot now but log a warning
                    print(f"[DIAGNOSTIC] WARNING: {num_instances} instances detected but only {required_instances} required")
                    print(f"[DIAGNOSTIC] Taking snapshot with first {required_instances} instances to avoid overcounting")
                    # Take first N instances from the set (order is not guaranteed, but this is better than taking all)
                    instances_list = list(self.connected_instances)
                    self.connected_instances_snapshot = set(instances_list[:required_instances])
                    print(f"[DIAGNOSTIC] Snapshot taken with {len(self.connected_instances_snapshot)} instances: {list(self.connected_instances_snapshot)}")
                
                if self.current_state != self.STATE_READY:
                    self._updateState(self.STATE_READY)
            elif self.seed_synced:
                if self.current_state != self.STATE_WAITING:
                    self._updateState(self.STATE_WAITING)
                    
        except Exception as e:
            self.connected_instances_label.setText("No instances connected yet")
            self.connected_instances_label.setStyleSheet("padding: 5px; color: #666;")
    
    def _updateState(self, new_state):
        """Update dialog state and UI accordingly"""
        self.current_state = new_state
        
        if new_state == self.STATE_SETUP:
            # Enable configuration controls
            self.session_id_edit.setEnabled(True)
            self.copy_session_btn.setEnabled(True)
            self.connect_button.setEnabled(True)
            self.connect_button.show()
            self.start_button.hide()
            self.countdown_label.hide()
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
            
        elif new_state == self.STATE_CONNECTING:
            # Disable configuration, show connecting status (but keep Copy enabled)
            self.session_id_edit.setEnabled(False)
            self.copy_session_btn.setEnabled(True)  # Keep Copy enabled
            self.connect_button.setEnabled(False)
            self.connect_button.show()
            self.start_button.hide()
            self.countdown_label.hide()
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
            
        elif new_state == self.STATE_WAITING:
            # Keep session ID read-only, waiting for instances (but keep Copy enabled)
            self.session_id_edit.setEnabled(False)
            self.copy_session_btn.setEnabled(True)  # Keep Copy enabled
            # In join mode, keep Connect button visible but disabled
            if self.join_existing_radio.isChecked():
                self.connect_button.setEnabled(False)
                self.connect_button.show()
            else:
                self.connect_button.hide()
            self.start_button.hide()
            self.countdown_label.hide()
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
                required = self.config.num_players
            else:
                required = self.config.num_players_max
            waiting = required - num_instances
            self.info_label.setText(f"⏳ Waiting for {waiting} more instance(s) to connect...")
            
        elif new_state == self.STATE_READY:
            # All ready, show start button (but keep Copy enabled)
            self.session_id_edit.setEnabled(False)
            self.copy_session_btn.setEnabled(True)  # Keep Copy enabled
            self.connect_button.hide()
            self.start_button.show()
            self.start_button.setEnabled(True)
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
                print(f"[DIAGNOSTIC] WARNING: Snapshot taken in READY state (fallback): {len(self.connected_instances_snapshot)} instances")
                print(f"[DIAGNOSTIC] Snapshot contains: {list(self.connected_instances_snapshot)}")
            else:
                print(f"[DIAGNOSTIC] Dialog became READY with snapshot already taken: {len(self.connected_instances_snapshot)} instances")
            
            # OPTIMIZATION: Stop periodic republishing once READY (no need to keep broadcasting)
            if hasattr(self, 'seed_republish_timer') and self.seed_republish_timer:
                self.seed_republish_timer.stop()
                print(f"[DIAGNOSTIC] Stopped periodic seed sync republishing (dialog is READY)")
            
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
                print(f"[Dialog] Session {session_id} selected, syncing seed...")
                # Update state to CONNECTING to show we're processing
                self._updateState(self.STATE_CONNECTING)
                self._syncSeed()
                # After seed sync, check if we should go to WAITING or READY
                # But don't auto-start countdown in join mode
                self._updateConnectedInstances()
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
            print(f"[Dialog] Connection already in progress, skipping...")
            return
        
        # Check if already connected
        if (self.model.mqttManager.client and 
            self.model.mqttManager.client.is_connected()):
            print(f"[Dialog] Already connected to broker")
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
            self.connection_status = "Connected to broker"
            self.status_label.setText(f"Connection Status: [●] {self.connection_status}")
            self.status_label.setStyleSheet("padding: 5px; background-color: #d4edda; border-radius: 3px; color: #155724;")
            
            # If in join mode, start session discovery FIRST (before seed sync)
            # This allows user to see available sessions immediately after connection
            if self.join_existing_radio.isChecked():
                # Always start discovery if not already started (regardless of when mode was changed)
                if not self.session_manager.session_discovery_handler:
                    print(f"[Dialog] Connection established, starting session discovery...")
                    self._startSessionDiscovery()
                self._should_start_discovery_on_connect = False  # Clear flag
                # In join mode, sync seed ONLY if user has selected a session from the list
                # Don't sync with temporary session_id - wait for user to select a real session
                if self.config.session_id and self.config.session_id != self._temporary_session_id:
                    # User has selected a session (not the temporary one), sync seed now
                    print(f"[Dialog] Session selected ({self.config.session_id}), syncing seed...")
                    self._syncSeed()
                else:
                    # Temporary session_id or no session selected yet - don't sync seed
                    print(f"[Dialog] Waiting for user to select a session from the list (temporary session_id: {self._temporary_session_id})")
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
            self.seed_status_label.setText("Seed Status: Checking for existing seed...")
            self.seed_status_label.setStyleSheet("padding: 5px; background-color: #fff8dc; border-radius: 3px;")
            QApplication.processEvents()  # Update UI immediately
            
            # Synchronize seed with configurable timeout
            # Use seed_sync_timeout from config (default 1.0s) for initial wait
            # Total timeout is seed_sync_timeout + 1 second for safety
            # Pass callback to track connected instances during seed sync
            def track_client_id(client_id):
                if not client_id:
                    print(f"[DIAGNOSTIC] track_client_id callback: WARNING - client_id is None or empty")
                    return
                old_count = len(self.connected_instances)
                self.connected_instances.add(client_id)
                new_count = len(self.connected_instances)
                if new_count != old_count:
                    print(f"[DIAGNOSTIC] track_client_id callback: {client_id[:8]}... added. Total: {old_count} -> {new_count}")
                else:
                    print(f"[DIAGNOSTIC] track_client_id callback: {client_id[:8]}... already tracked (duplicate). Total: {new_count}")
                # Don't update UI here - wait until after seed sync completes
                # This avoids race conditions
            
            # Prepare tracking handler BEFORE syncSeed() so it can be installed immediately after
            # This ensures we don't miss any messages published between syncSeed() completion and handler installation
            session_topics = self.session_manager.getSessionTopics(self.config.session_id)
            seed_topic = session_topics[1]  # session_seed_sync
            
            print(f"[Dialog] Starting seed sync...")
            synced_seed = self.session_manager.syncSeed(
                self.config.session_id,
                shared_seed=self.config.shared_seed,
                timeout=self.config.seed_sync_timeout + 1.0,
                initial_wait=self.config.seed_sync_timeout,
                client_id_callback=track_client_id
            )
            
            print(f"[Dialog] Seed sync completed, seed: {synced_seed}")
            
            # Verify that seed sync actually succeeded
            if synced_seed is None:
                raise ValueError("Seed synchronization returned None")
            
            self.config.shared_seed = synced_seed
            self.synced_seed_value = synced_seed
            
            # Apply seed immediately
            import random
            random.seed(synced_seed)
            
            self.seed_synced = True
            self.seed_status_label.setText("Seed Status: Synchronized ✓")
            self.seed_status_label.setStyleSheet("padding: 5px; background-color: #d4edda; border-radius: 3px;")
            
            # CRITICAL: Install tracking handler IMMEDIATELY after syncSeed() completes
            # This minimizes the window where messages might be missed
            # syncSeed() has restored the original handler, so we wrap that
            self._subscribeToSeedSyncForTracking()
            
            # CRITICAL: Also subscribe to player registration messages to track instances
            # Player registration messages use separate topics per player, so all retained messages are preserved
            # This provides a more reliable way to track connected instances
            self._subscribeToPlayerRegistrationForTracking()
            
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
                print(f"[Dialog] Publishing session discovery: {self.config.session_id}")
                self.session_manager.publishSession(
                    self.config.session_id,
                    num_min,
                    num_max,
                    model_name
                )
            
            # Update state - will check if ready or waiting
            self._updateConnectedInstances()
            
        except Exception as e:
            self.seed_status_label.setText(f"Seed Status: Sync failed - {str(e)}")
            self.seed_status_label.setStyleSheet("padding: 5px; background-color: #f8d7da; border-radius: 3px;")
            self._updateState(self.STATE_SETUP)  # Reset to setup state
            QMessageBox.critical(self, "Seed Sync Error", f"Failed to synchronize seed:\n{str(e)}")
    
    def _subscribeToSeedSyncForTracking(self, base_handler=None):
        """Subscribe to seed sync topic to track connected instances
        
        Args:
            base_handler: Handler to wrap (if None, uses current handler)
        """
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            return
        
        # Get seed sync topic
        session_topics = self.session_manager.getSessionTopics(self.config.session_id)
        seed_topic = session_topics[1]  # session_seed_sync
        
        # Use provided handler or current handler (which is the original handler restored by syncSeed)
        # We'll wrap it to add tracking functionality
        if base_handler is None:
            current_handler = self.model.mqttManager.client.on_message
        else:
            current_handler = base_handler
        
        def seed_tracking_wrapper(client, userdata, msg):
            # Track instances via seed sync messages FIRST
            if msg.topic == seed_topic:
                try:
                    import json
                    msg_dict = json.loads(msg.payload.decode("utf-8"))
                    client_id = msg_dict.get('clientId')
                    is_retained = msg.retain
                    # Diagnostic: log ALL seed sync messages received
                    print(f"[DIAGNOSTIC] Seed tracking handler received message: client_id={client_id[:8] if client_id else 'N/A'}..., retained={is_retained}, topic={msg.topic}")
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
                                retained_str = " (RETAINED)" if is_retained else " (NEW)"
                                print(f"[DIAGNOSTIC] Instance tracking: {client_id[:8]}... added{retained_str}. Total: {old_count} -> {len(self.connected_instances)}")
                                QTimer.singleShot(0, self._updateConnectedInstances)
                                print(f"[Dialog] New instance detected: {client_id[:8]}... Total: {len(self.connected_instances)}")
                                
                                # CRITICAL: If this is a NEW instance (not retained), republish our own seed sync message
                                # This ensures that the new instance receives our presence even if our retained message was overwritten
                                # This is especially important when multiple instances are already connected
                                # OPTIMIZATION: Only republish if dialog is not READY yet (to avoid unnecessary messages)
                                if (not is_retained and is_new_instance and 
                                    client_id != self.model.mqttManager.clientId and
                                    self.connected_instances_snapshot is None):  # Only if not READY yet
                                    print(f"[DIAGNOSTIC] New instance {client_id[:8]}... detected, republishing our own seed sync message for visibility...")
                                    # Use QTimer to avoid blocking the MQTT handler thread
                                    QTimer.singleShot(100, lambda: self._republishSeedSync())
                        else:
                            # Dialog is READY - don't count new instances
                            if is_new_instance:
                                print(f"[DIAGNOSTIC] Instance tracking: {client_id[:8]}... detected but NOT counted (dialog is READY, may be temporary connection)")
                            else:
                                # Instance already in set (duplicate message)
                                if is_retained:
                                    print(f"[DIAGNOSTIC] Instance tracking: {client_id[:8]}... already in set (RETAINED message)")
                                else:
                                    print(f"[DIAGNOSTIC] Instance tracking: {client_id[:8]}... already in set (NEW message - duplicate)")
                except Exception as e:
                    print(f"[Dialog] Error tracking instance: {e}")
                    import traceback
                    traceback.print_exc()
                # CRITICAL: Do NOT forward seed sync messages to original handler
                # They are not game topics and will be ignored anyway
                return
            
            # Forward NON-seed-sync messages to the original handler
            # The original handler processes game topics
            if current_handler:
                current_handler(client, userdata, msg)
        
        # Install tracking wrapper - this will remain active permanently
        # Store reference to wrapper so it can access self
        self._seed_tracking_wrapper = seed_tracking_wrapper
        self.model.mqttManager.client.on_message = seed_tracking_wrapper
        
        # Subscribe to seed sync topic (to receive retained messages from other instances)
        # Note: We're already subscribed from syncSeed(), but this ensures we stay subscribed
        # Use qos=1 to ensure we receive all messages
        print(f"[DIAGNOSTIC] Subscribing to seed sync topic for tracking: {seed_topic}")
        print(f"[DIAGNOSTIC] Current connected_instances BEFORE subscription: {list(self.connected_instances)}")
        print(f"[DIAGNOSTIC] Current handler BEFORE subscription: {self.model.mqttManager.client.on_message}")
        
        # CRITICAL: Check if we already have exactly the required number of instances BEFORE waiting
        # If so, take snapshot NOW to prevent instances that connect during wait from being counted
        if self.seed_synced and self.connected_instances_snapshot is None:
            if isinstance(self.config.num_players, int):
                required_instances = self.config.num_players
            else:
                required_instances = self.config.num_players_max
            
            if len(self.connected_instances) == required_instances:
                self.connected_instances_snapshot = self.connected_instances.copy()
                print(f"[DIAGNOSTIC] Snapshot taken BEFORE wait period: {len(self.connected_instances_snapshot)} instances frozen")
                print(f"[DIAGNOSTIC] Snapshot contains: {list(self.connected_instances_snapshot)}")
                print(f"[DIAGNOSTIC] NOTE: Instances connecting during wait period will NOT be counted")
        
        # CRITICAL: Do NOT unsubscribe/re-subscribe as this may prevent retained messages from being received
        # Instead, ensure we're subscribed and wait for retained messages to be processed
        # The handler is already installed, so any retained messages will be processed
        import time
        
        # CRITICAL: Wait for retained messages to be processed
        # Need sufficient delay to ensure all retained messages from other instances are received
        # This is especially important when multiple instances are already connected
        # IMPORTANT: Instances that have already left the dialog won't republish, so we must rely on retained messages
        print(f"[DIAGNOSTIC] Waiting 1.5s for retained seed sync messages to be processed...")
        time.sleep(1.5)  # Increased delay to ensure all retained messages are received
        
        # CRITICAL: Force a re-subscription WITHOUT unsubscribe to trigger retained messages
        # Some MQTT brokers only send retained messages on initial subscription
        # By re-subscribing (without unsubscribe), we ensure retained messages are sent again
        print(f"[DIAGNOSTIC] Re-subscribing (without unsubscribe) to trigger retained messages...")
        self.model.mqttManager.client.subscribe(seed_topic, qos=1)
        
        # Wait again after re-subscription for retained messages
        # CRITICAL: This delay is important because instances that left the dialog won't republish
        print(f"[DIAGNOSTIC] Waiting additional 1.0s after re-subscription...")
        time.sleep(1.0)  # Increased delay to receive all retained messages after re-subscription
        
        print(f"[DIAGNOSTIC] Current connected_instances AFTER wait: {list(self.connected_instances)}")
        print(f"[DIAGNOSTIC] Total instances detected: {len(self.connected_instances)}")
        
        # CRITICAL: Check if we have exactly the required number of instances and take snapshot NOW
        # This prevents instances that connect during the UI update delay from being counted
        if self.seed_synced and self.connected_instances_snapshot is None:
            if isinstance(self.config.num_players, int):
                required_instances = self.config.num_players
            else:
                required_instances = self.config.num_players_max
            
            if len(self.connected_instances) == required_instances:
                self.connected_instances_snapshot = self.connected_instances.copy()
                print(f"[DIAGNOSTIC] Snapshot taken AFTER wait period: {len(self.connected_instances_snapshot)} instances frozen")
                print(f"[DIAGNOSTIC] Snapshot contains: {list(self.connected_instances_snapshot)}")
                print(f"[DIAGNOSTIC] NOTE: Instances connecting after this point will NOT be counted")
            elif len(self.connected_instances) > required_instances:
                # We have more than required - take snapshot with only the first N instances
                print(f"[DIAGNOSTIC] WARNING: {len(self.connected_instances)} instances detected but only {required_instances} required")
                print(f"[DIAGNOSTIC] Taking snapshot with first {required_instances} instances to avoid overcounting")
                instances_list = list(self.connected_instances)
                self.connected_instances_snapshot = set(instances_list[:required_instances])
                print(f"[DIAGNOSTIC] Snapshot taken with {len(self.connected_instances_snapshot)} instances: {list(self.connected_instances_snapshot)}")
        
        # Schedule UI update after a delay to catch any late messages
        # CRITICAL: Use sufficient delay to ensure all retained messages are processed
        # This is especially important when instances have already left the dialog
        QTimer.singleShot(1200, self._updateConnectedInstances)  # Increased delay to catch all messages
        
        print(f"[Dialog] Installed seed tracking handler for topic: {seed_topic}")
    
    def _subscribeToPlayerRegistrationForTracking(self):
        """Subscribe to player registration messages to track connected instances
        
        This is more reliable than seed sync messages because each player has a separate topic,
        so all retained messages are preserved (unlike seed sync where only the last retained message is kept).
        """
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            return
        
        # Get player registration topic base
        session_topics = self.session_manager.getSessionTopics(self.config.session_id)
        registration_topic_base = session_topics[0]  # session_player_registration
        
        # Subscribe to wildcard topic to receive all player registrations
        registration_topic_wildcard = f"{registration_topic_base}/+"
        
        # Get current handler (which is the seed tracking wrapper)
        current_handler = self.model.mqttManager.client.on_message
        
        def player_registration_tracking_wrapper(client, userdata, msg):
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
                                print(f"[DIAGNOSTIC] Player registration tracking: {client_id[:8]}... added{retained_str}. Total: {old_count} -> {len(self.connected_instances)}")
                                QTimer.singleShot(0, self._updateConnectedInstances)
                        else:
                            # Dialog is READY - don't count new instances
                            if is_new_instance:
                                print(f"[DIAGNOSTIC] Player registration tracking: {client_id[:8]}... detected but NOT counted (dialog is READY, may be temporary connection)")
                            else:
                                print(f"[DIAGNOSTIC] Player registration tracking: {client_id[:8]}... already in set (duplicate message)")
                except Exception as e:
                    print(f"[Dialog] Error tracking instance from player registration: {e}")
                    import traceback
                    traceback.print_exc()
                # Don't forward - this is just for tracking
                return
            
            # Forward other messages to current handler (seed tracking wrapper)
            if current_handler:
                current_handler(client, userdata, msg)
        
        # Install wrapper
        self._player_registration_tracking_wrapper = player_registration_tracking_wrapper
        self.model.mqttManager.client.on_message = player_registration_tracking_wrapper
        
        # Subscribe to player registration wildcard topic
        print(f"[DIAGNOSTIC] Subscribing to player registration topic for tracking: {registration_topic_wildcard}")
        self.model.mqttManager.client.subscribe(registration_topic_wildcard, qos=1)
        
        # Wait for retained messages to be received
        # CRITICAL: Player registration messages are published AFTER dialog closes, so they may not be available yet
        # But we still wait for any existing retained messages from previous sessions
        import time
        print(f"[DIAGNOSTIC] Waiting 1.0s for retained player registration messages...")
        time.sleep(1.0)  # Sufficient delay to receive retained messages
        
        print(f"[DIAGNOSTIC] Current connected_instances AFTER player registration tracking: {list(self.connected_instances)}")
        print(f"[DIAGNOSTIC] Total instances detected: {len(self.connected_instances)}")
        
        # Schedule UI update
        QTimer.singleShot(500, self._updateConnectedInstances)
    
    def closeEvent(self, event):
        """Handle dialog close event - cleanup session discovery"""
        # Stop session discovery if running
        if self.session_manager.session_discovery_handler:
            self.session_manager.stopSessionDiscovery()
        
        # Stop session heartbeat if running
        self.session_manager.stopSessionHeartbeat()
        
        # Stop seed republish timer
        if hasattr(self, 'seed_republish_timer') and self.seed_republish_timer:
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
        print(f"[DIAGNOSTIC] Periodically republished seed sync message for instance {self.model.mqttManager.clientId[:8]}...")
    
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
        if self.current_state != self.STATE_READY:
            # State changed, stop countdown
            if self.auto_start_timer:
                self.auto_start_timer.stop()
            self.countdown_label.hide()
            return
        
        # Check if still ready (number of instances might have changed)
        # Use snapshot if dialog is READY to avoid counting instances that connect after READY state
        if self.connected_instances_snapshot is not None:
            num_instances = len(self.connected_instances_snapshot)
        else:
            num_instances = len(self.connected_instances)
        if isinstance(self.config.num_players, int):
            required_instances = self.config.num_players
        else:
            required_instances = self.config.num_players_max
        
        if num_instances < required_instances:
            # Not ready anymore, stop countdown
            if self.auto_start_timer:
                self.auto_start_timer.stop()
            self.countdown_label.hide()
            self._updateState(self.STATE_WAITING)
            return
        
        self.auto_start_countdown -= 1
        
        if self.auto_start_countdown > 0:
            self.countdown_label.setText(f"⏱️ Starting automatically in: {self.auto_start_countdown}...")
        else:
            # Countdown finished, auto-start
            if self.auto_start_timer:
                self.auto_start_timer.stop()
            self.countdown_label.setText("Starting now...")
            QTimer.singleShot(300, self.accept)  # Small delay for visual feedback
    
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
        # Use snapshot if dialog is READY to ensure consistent counting
        if self.connected_instances_snapshot is not None:
            num_instances = len(self.connected_instances_snapshot)
            print(f"[DIAGNOSTIC] Accept validation: Using snapshot (dialog READY) with {num_instances} instances")
        else:
            num_instances = len(self.connected_instances)
            print(f"[DIAGNOSTIC] Accept validation: Using current count (dialog not READY) with {num_instances} instances")
        if isinstance(self.config.num_players, int):
            required_instances = self.config.num_players
        else:
            required_instances = self.config.num_players_max
        
        if num_instances < required_instances:
            reply = QMessageBox.question(
                self,
                "Insufficient Instances",
                f"Only {num_instances} instance(s) connected, but {required_instances} required.\n"
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
