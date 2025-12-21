# --- Standard library imports ---
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class SGDistributedConnectionDialog(QDialog):
    """
    Minimal dialog for MQTT connection and seed synchronization.
    
    This dialog allows users to:
    - View/edit session_id
    - Connect to MQTT broker
    - Synchronize seed (happens automatically after connection)
    - See connection status in real-time
    
    Note: Player selection happens later in completeDistributedGameSetup()
    """
    
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
        
        # Info label
        info_label = QLabel("Connect to the MQTT broker to join a distributed game session.\nPlayer selection will happen after the game window opens.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(info_label)
        
        # MQTT Broker Info
        broker_info_label = QLabel(f"MQTT Broker: {self.config.broker_host}:{self.config.broker_port}")
        broker_info_label.setStyleSheet("color: #333; padding: 3px; font-weight: bold;")
        layout.addWidget(broker_info_label)
        
        # Session ID Section
        session_group = QGroupBox("Session ID")
        session_layout = QVBoxLayout()
        
        session_input_layout = QHBoxLayout()
        self.session_id_edit = QLineEdit()
        self.session_id_edit.setText(self.config.session_id or "")
        self.session_id_edit.setPlaceholderText("Enter or generate session ID")
        session_input_layout.addWidget(QLabel("Session ID:"))
        session_input_layout.addWidget(self.session_id_edit)
        
        copy_session_btn = QPushButton("Copy")
        copy_session_btn.clicked.connect(self._copySessionId)
        session_input_layout.addWidget(copy_session_btn)
        
        new_session_btn = QPushButton("New Session")
        new_session_btn.clicked.connect(self._generateNewSessionId)
        session_input_layout.addWidget(new_session_btn)
        session_layout.addLayout(session_input_layout)
        
        session_group.setLayout(session_layout)
        layout.addWidget(session_group)
        
        # Number of Players Display
        num_players_label = QLabel()
        if isinstance(self.config.num_players, int):
            num_players_text = f"Number of players: {self.config.num_players}"
        else:
            num_players_text = f"Number of players: {self.config.num_players_min}-{self.config.num_players_max}"
        num_players_label.setText(num_players_text)
        layout.addWidget(num_players_label)
        
        # Connection Status
        self.status_label = QLabel(f"Connection Status: {self.connection_status}")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px;")
        layout.addWidget(self.status_label)
        
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
        instances_group.setLayout(instances_layout)
        layout.addWidget(instances_group)
        
        # Spacer
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.connect_button = QPushButton("Connect & Sync Seed")
        self.connect_button.clicked.connect(self._onConnect)
        button_layout.addWidget(self.connect_button)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(False)  # Disabled until seed is synced
        button_layout.addWidget(self.ok_button)
        
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
    
    def _connectSignals(self):
        """Connect to session manager signals for real-time updates"""
        # Note: We don't connect to playerConnected/playerDisconnected here
        # because players are not registered yet at this stage
        # Instead, we track instances via seed sync messages
    
    def _generateNewSessionId(self):
        """Generate a new UUID session ID and update UI"""
        new_id = self.config.generate_session_id()
        self.session_id_edit.setText(new_id)
    
    def _copySessionId(self):
        """Copy session ID to clipboard"""
        session_id = self.session_id_edit.text().strip()
        if session_id:
            clipboard = QApplication.clipboard()
            clipboard.setText(session_id)
        else:
            QMessageBox.warning(self, "No Session ID", "Please enter or generate a session ID first.")
    
    def _updateConnectedInstances(self):
        """Update the connected instances list display"""
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            self.connected_instances_label.setText("No instances connected yet")
            return
        
        try:
            num_instances = len(self.connected_instances)
            if num_instances > 0:
                self.connected_instances_label.setText(f"{num_instances} instance(s) connected to this session")
                self.connected_instances_label.setStyleSheet("padding: 5px; color: #27ae60; font-weight: bold;")
            else:
                self.connected_instances_label.setText("No instances connected yet")
                self.connected_instances_label.setStyleSheet("padding: 5px; color: #666;")
        except Exception as e:
            self.connected_instances_label.setText("No instances connected yet")
            self.connected_instances_label.setStyleSheet("padding: 5px; color: #666;")
    
    def _onConnect(self):
        """Handle Connect button click - update session_id, connect to broker, and sync seed"""
        # Update session_id from edit field
        session_id = self.session_id_edit.text().strip()
        if not session_id:
            QMessageBox.warning(self, "Invalid Session ID", "Please enter a session ID or generate a new one.")
            return
        
        self.config.session_id = session_id
        
        # Connect to broker
        self._connectToBroker()
    
    def _connectToBroker(self):
        """Connect to MQTT broker by calling setMQTTProtocol()"""
        try:
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
            self.connection_status = f"Connection failed: {str(e)}"
            self.status_label.setText(f"Connection Status: {self.connection_status}")
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to MQTT broker:\n{str(e)}")
    
    def _checkConnection(self):
        """Check if MQTT connection is established (polling)"""
        if (self.model.mqttManager.client and 
            self.model.mqttManager.client.is_connected()):
            self.connection_status = "Connected to broker"
            self.status_label.setText(f"Connection Status: {self.connection_status}")
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
                self.connected_instances.add(client_id)
                self._updateConnectedInstances()
            
            synced_seed = self.session_manager.syncSeed(
                self.config.session_id,
                shared_seed=self.config.shared_seed,
                timeout=self.config.seed_sync_timeout + 1.0,
                initial_wait=self.config.seed_sync_timeout,
                client_id_callback=track_client_id
            )
            
            self.config.shared_seed = synced_seed
            self.synced_seed_value = synced_seed
            
            # Apply seed immediately
            import random
            random.seed(synced_seed)
            
            self.seed_synced = True
            self.seed_status_label.setText("Seed Status: Synchronized ✓")
            self.seed_status_label.setStyleSheet("padding: 5px; background-color: #d4edda; border-radius: 3px;")
            
            # After seed sync, subscribe to seed sync topic to track other instances
            self._subscribeToSeedSyncForTracking()
            
            # Enable OK button
            self.ok_button.setEnabled(True)
            
        except Exception as e:
            self.seed_status_label.setText(f"Seed Status: Sync failed - {str(e)}")
            self.seed_status_label.setStyleSheet("padding: 5px; background-color: #f8d7da; border-radius: 3px;")
            QMessageBox.critical(self, "Seed Sync Error", f"Failed to synchronize seed:\n{str(e)}")
    
    def _subscribeToSeedSyncForTracking(self):
        """Subscribe to seed sync topic to track connected instances"""
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            return
        
        # Get seed sync topic
        session_topics = self.session_manager.getSessionTopics(self.config.session_id)
        seed_topic = session_topics[1]  # session_seed_sync
        
        # Save original handler (current handler after syncSeed)
        original_on_message = self.model.mqttManager.client.on_message
        
        def seed_tracking_handler(client, userdata, msg):
            # Track instances via seed sync messages
            if msg.topic == seed_topic:
                try:
                    import json
                    msg_dict = json.loads(msg.payload.decode("utf-8"))
                    client_id = msg_dict.get('clientId')
                    if client_id:
                        self.connected_instances.add(client_id)
                        self._updateConnectedInstances()
                except Exception:
                    pass
            
            # Forward to original handler
            if original_on_message:
                original_on_message(client, userdata, msg)
        
        # Install tracking handler BEFORE subscribing to ensure we receive retained messages
        self.model.mqttManager.client.on_message = seed_tracking_handler
        
        # Subscribe to seed sync topic (to receive retained messages from other instances)
        # Note: This will trigger retained messages to be sent, which will be handled by our handler
        self.model.mqttManager.client.subscribe(seed_topic)
        
        # Wait a moment for retained messages to be processed by MQTT client thread
        QTimer.singleShot(500, self._updateConnectedInstances)
    
    def _checkSeedSync(self):
        """Periodically check if seed sync completed (called by timer)"""
        if self.seed_synced and self.ok_button.isEnabled():
            # Seed already synced, stop checking
            self.seed_check_timer.stop()
    
    def accept(self):
        """Override accept to validate seed sync before closing"""
        if not self.seed_synced:
            QMessageBox.warning(self, "Seed Not Synchronized", 
                              "Please wait for seed synchronization to complete.")
            return
        
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            QMessageBox.warning(self, "Not Connected", "Please connect to the broker first.")
            return
        
        super().accept()
