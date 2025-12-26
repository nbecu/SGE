# --- Standard library imports ---
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class SGDistributedGameDialog(QDialog):
    # Signal for thread-safe UI updates from MQTT callbacks
    reservationUpdateRequested = pyqtSignal()
    waitingStatusUpdateRequested = pyqtSignal()
    """
    Dialog for user to select assigned player.
    
    This dialog allows users to:
    - View session_id (read-only, discrete display)
    - Select assigned_player from available players
    - See connection status in real-time
    
    Note: MQTT connection and session selection are handled by SGDistributedConnectionDialog
    before this dialog is shown.
    """
    
    def __init__(self, parent, config, model, session_manager):
        """
        Initialize dialog.
        
        Args:
            parent: Parent widget (SGModel)
            config: SGDistributedGameConfig object
            model: SGModel instance (to retrieve player names)
            session_manager: SGDistributedSessionManager instance
        """
        super().__init__(parent)
        self.config = config
        self.model = model
        self.session_manager = session_manager
        self.selected_player_name = None
        self.connection_status = "Not connected"
        
        # Player reservation system
        self.player_reservations = {}  # {player_name: client_id} - tracks who reserved what
        self.reservation_confirmed = False  # Whether current reservation is confirmed
        self.pending_reservation = None  # Player name being reserved (during conflict check)
        self.conflict_detected = False  # Flag for conflict detection
        self._reservation_handler = None  # Handler reference to prevent garbage collection
        self.waiting_for_others = False  # Whether we're waiting for other instances to select their players
        self._all_players_selected_processed = False  # Flag to prevent double processing of all_players_selected message
        self._all_players_selected_published = False  # Flag to prevent multiple publications
        self._all_players_selected_subscribed = False  # Flag to prevent multiple subscriptions
        self._cleaning_up = False  # Flag to prevent MQTT callbacks during cleanup
        self._handler_before_all_players_selected = None  # Store handler before installing all_players_selected_handler
        
        self.setWindowTitle("Select Your Player")
        self.setModal(True)
        self.resize(400, 300)
        
        self._buildUI()
        self._setupTimers()
        
        # Connect signals for thread-safe UI updates from MQTT callbacks
        self.reservationUpdateRequested.connect(self.updateAvailablePlayers)
        self.waitingStatusUpdateRequested.connect(self._updateWaitingStatus)
        
        self._subscribeToPlayerReservations()
        self._subscribeToPlayerRegistrations()
        # NOTE: _subscribeToAllPlayersSelected() is now called from _subscribeToPlayerReservations()
        # after the reservation handler is installed, to ensure correct handler chain order
        
        # Update session ID display
        if self.config.session_id:
            self.session_id_display.setText(f"Session: {self.config.session_id}")
        else:
            self.session_id_display.setText("Session: Not set")
        
        # Check if MQTT connection already exists (from enableDistributedGame())
        # In normal flow, connection should always be established by SGDistributedConnectionDialog
        if (self.model.mqttManager.client and 
            self.model.mqttManager.client.is_connected() and
            self.model.mqttManager.session_id == self.config.session_id):
            # Connection already established, enable OK button
            self.connection_status = "Connected to broker"
            self.status_label.setText(f"Connection Status: {self.connection_status}")
            self.ok_button.setEnabled(True)
        else:
            # Connection not established - this should not happen in normal flow
            # But handle gracefully by enabling OK button anyway (connection will be checked in accept())
            self.connection_status = "Warning: Connection not detected"
            self.status_label.setText(f"Connection Status: {self.connection_status}")
            # Keep discrete style even for warning
            self.ok_button.setEnabled(True)  # Allow user to proceed, validation happens in accept()
    
    def _buildUI(self):
        """Build the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title_label = QLabel("Select Your Player")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Info section (compact, in correct order)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        # 1. Connection Status (discrete)
        self.status_label = QLabel(f"Connection Status: {self.connection_status}")
        self.status_label.setStyleSheet("color: #888; font-size: 9px; padding: 2px;")
        info_layout.addWidget(self.status_label)
        
        # 2. Session ID Display (read-only, discrete)
        self.session_id_display = QLabel(f"Session: {self.config.session_id or 'Not set'}")
        self.session_id_display.setStyleSheet("color: #888; font-size: 9px; padding: 2px;")
        self.session_id_display.setWordWrap(True)
        info_layout.addWidget(self.session_id_display)
        
        # 3. Number of Players Display (not discrete)
        num_players_label = QLabel()
        if isinstance(self.config.num_players, int):
            num_players_text = f"Number of players: {self.config.num_players}"
        else:
            num_players_text = f"Number of players: {self.config.num_players_min}-{self.config.num_players_max}"
        num_players_label.setText(num_players_text)
        num_players_label.setStyleSheet("font-size: 11px; color: #333; padding: 3px;")
        info_layout.addWidget(num_players_label)
        
        # 4. Waiting status label (for when player is selected but waiting for others)
        self.waiting_status_label = QLabel("")
        self.waiting_status_label.setStyleSheet("font-size: 11px; color: #f39c12; padding: 5px; font-weight: bold;")
        self.waiting_status_label.setWordWrap(True)
        self.waiting_status_label.hide()  # Hidden by default
        info_layout.addWidget(self.waiting_status_label)
        
        layout.addLayout(info_layout)
        
        # Player Selection Section
        player_group = QGroupBox("Select Your Player")
        player_layout = QVBoxLayout()
        player_layout.setSpacing(5)
        
        # Get player names from model (exclude "Admin")
        self.player_names = [name for name in self.model.players.keys() if name != "Admin"]
        
        self.player_radio_buttons = {}
        self.player_button_group = QButtonGroup(self)
        
        for i, player_name in enumerate(self.player_names):
            radio = QRadioButton(player_name)
            self.player_radio_buttons[player_name] = radio
            self.player_button_group.addButton(radio, i)
            player_layout.addWidget(radio)
        
        # Auto-select first player if available
        if self.player_names:
            self.player_radio_buttons[self.player_names[0]].setChecked(True)
            self.selected_player_name = self.player_names[0]
        
        player_group.setLayout(player_layout)
        layout.addWidget(player_group)
        
        # Add stretch to push buttons to bottom
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _setupTimers(self):
        """Setup timers for periodic updates"""
        # Timer to update available players every second
        self.player_update_timer = QTimer(self)
        self.player_update_timer.timeout.connect(self.updateAvailablePlayers)
        self.player_update_timer.start(1000)  # Update every second
        
        # Timer to check if all players are selected (when waiting)
        self.waiting_check_timer = QTimer(self)
        self.waiting_check_timer.timeout.connect(self._checkAllPlayersSelected)
        self.waiting_check_timer.setSingleShot(False)
    
    def _subscribeToPlayerReservations(self):
        """Subscribe to player reservation messages for real-time updates"""
        print(f"[Dialog] _subscribeToPlayerReservations called for session: {self.config.session_id}")
        if not self.config.session_id:
            print(f"[Dialog] WARNING: No session_id, skipping subscription")
            return
        
        if not (self.model.mqttManager.client and self.model.mqttManager.client.is_connected()):
            print(f"[Dialog] WARNING: MQTT client not connected, will retry subscription in 500ms")
            # Retry subscription after a short delay to allow MQTT connection to be established
            QTimer.singleShot(500, self._subscribeToPlayerReservations)
            return
        
        def on_reservation_received(client_id, player_name, action):
            """Handle reservation messages"""
            # CRITICAL: Ignore callbacks during cleanup
            if hasattr(self, '_cleaning_up') and self._cleaning_up:
                return
            
            print(f"[Dialog] Reservation received: {action} for {player_name} by {client_id[:8] if client_id else 'N/A'}...")
            
            # CRITICAL: Update reservations dict first (this is thread-safe for dict operations)
            # because this callback runs in the MQTT thread, not the main Qt thread
            
            if action == 'reserve':
                self.player_reservations[player_name] = client_id
                print(f"[Dialog] Updated reservations dict: {self.player_reservations}")
            elif action == 'release':
                if player_name in self.player_reservations:
                    del self.player_reservations[player_name]
                print(f"[Dialog] Updated reservations dict: {self.player_reservations}")
            
            # Emit signal for thread-safe UI update
            # Signals are thread-safe and will be processed in the main Qt thread
            self.reservationUpdateRequested.emit()
            
            # Also trigger waiting status update if needed
            if self.waiting_for_others:
                self.waitingStatusUpdateRequested.emit()
            
            # Check for conflicts during pending reservation
            # CRITICAL: Only check for conflicts if:
            # 1. We have a pending reservation for this player
            # 2. The action is 'reserve' (not 'release')
            # 3. It's from another client (not ourselves)
            # 4. We haven't already confirmed this reservation
            # 5. We're not waiting for others (all players already selected)
            if (self.pending_reservation == player_name and 
                action == 'reserve' and 
                client_id != self.model.mqttManager.clientId and
                not (self.reservation_confirmed and self.selected_player_name == player_name) and
                not getattr(self, 'waiting_for_others', False)):
                print(f"[Dialog] CONFLICT DETECTED for {player_name}!")
                self.conflict_detected = True
        
        print(f"[Dialog] Subscribing to player reservations for session: {self.config.session_id}")
        print(f"[Dialog] Current handler before subscription: {self.model.mqttManager.client.on_message}")
        print(f"[Dialog] Client ID: {self.model.mqttManager.clientId[:8] if self.model.mqttManager.clientId else 'N/A'}...")
        result = self.session_manager.subscribeToPlayerReservations(
            self.config.session_id,
            on_reservation_received
        )
        print(f"[Dialog] subscribeToPlayerReservations result: {result}")
        print(f"[Dialog] Current handler after subscription: {self.model.mqttManager.client.on_message}")
        print(f"[Dialog] Initial reservations dict after subscription: {self.player_reservations}")
        
        # CRITICAL: Subscribe to all_players_selected AFTER player reservations subscription
        # This ensures the handler chain is correct: all_players_selected_handler -> reservation_message_handler -> original_handler
        # Use a small delay to ensure the reservation handler is fully installed
        QTimer.singleShot(100, self._subscribeToAllPlayersSelected)
        
        # Force UI update after a short delay to ensure retained messages are processed
        # This ensures that if retained messages were received, the UI is updated
        QTimer.singleShot(600, self.updateAvailablePlayers)
        QTimer.singleShot(700, lambda: print(f"[Dialog] Reservations dict after delay: {self.player_reservations}"))
        QTimer.singleShot(800, lambda: print(f"[Dialog] Final reservations dict: {self.player_reservations}"))
    
    def _subscribeToPlayerRegistrations(self):
        """Subscribe to player registration signals to update waiting status"""
        if not self.config.session_id:
            return
        
        # Connect to playerConnected signal to update waiting status
        self.session_manager.playerConnected.connect(self._onPlayerRegistered)
    
    def _onPlayerRegistered(self, player_name):
        """Handle when a player is registered (connected)"""
        # Ignore during cleanup
        if hasattr(self, '_cleaning_up') and self._cleaning_up:
            return
        
        print(f"[Dialog] Player registered signal received: {player_name}")
        # Update waiting status if we're waiting
        if self.waiting_for_others:
            # Use longer delay to ensure the connected_players dict is updated
            QTimer.singleShot(200, self._updateWaitingStatus)
            QTimer.singleShot(300, self._checkAllPlayersSelected)
    
    def _subscribeToAllPlayersSelected(self):
        """Subscribe to all_players_selected topic to synchronize dialog closure"""
        # Prevent multiple subscriptions
        if self._all_players_selected_subscribed:
            print(f"[Dialog] Already subscribed to all_players_selected, skipping")
            return
        
        if not self.config.session_id:
            return
        
        if not (self.model.mqttManager.client and self.model.mqttManager.client.is_connected()):
            # Retry subscription after a short delay to allow MQTT connection to be established
            QTimer.singleShot(500, self._subscribeToAllPlayersSelected)
            return
        
        # Get all_players_selected topic
        session_topics = self.session_manager.getSessionTopics(self.config.session_id)
        all_players_selected_topic = session_topics[6]  # session_all_players_selected (index 6)
        
        # CRITICAL: Get current handler (which should be the reservation handler from subscribeToPlayerReservations)
        # We need to wrap it, not replace it
        current_handler = self.model.mqttManager.client.on_message
        # Save handler for restoration during cleanup
        self._handler_before_all_players_selected = current_handler
        print(f"[Dialog] Current handler before all_players_selected subscription: {current_handler}")
        
        def all_players_selected_handler(client, userdata, msg):
            # CRITICAL: Ignore callbacks during cleanup
            if hasattr(self, '_cleaning_up') and self._cleaning_up:
                return
            # CRITICAL: This handler should be called for ALL messages
            # Log ALL messages to verify handler is being called
            if 'session_all_players_selected' in msg.topic:
                print(f"[Dialog] *** all_players_selected_handler CALLED for session_all_players_selected: topic={msg.topic} ***")
            else:
                # Log other messages occasionally to verify handler is active
                # Only log every 10th message to avoid spam
                import random
                if random.random() < 0.1:  # 10% chance
                    print(f"[Dialog] all_players_selected_handler called for other message: topic={msg.topic[:50]}...")
            
            # CRITICAL: Protect against RuntimeError if dialog is destroyed
            try:
                # Log ALL messages that match the topic to diagnose routing issues
                # This should be called for EVERY message on session_all_players_selected topic
                if 'session_all_players_selected' in msg.topic:
                    print(f"[Dialog] all_players_selected_handler CALLED for session_all_players_selected: topic={msg.topic}, expected={all_players_selected_topic}, match={msg.topic == all_players_selected_topic}")
                
                # Log ALL messages that match the topic to diagnose routing issues
                if msg.topic == all_players_selected_topic or 'session_all_players_selected' in msg.topic:
                    print(f"[Dialog] all_players_selected_handler CALLED: topic={msg.topic}, expected={all_players_selected_topic}, match={msg.topic == all_players_selected_topic}")
                
                # Log ALL messages to diagnose routing issues
                if 'session_all_players_selected' in msg.topic:
                    print(f"[Dialog] all_players_selected_handler: Received message on topic {msg.topic}, expected: {all_players_selected_topic}, match: {msg.topic == all_players_selected_topic}")
                elif msg.topic == all_players_selected_topic:
                    print(f"[Dialog] all_players_selected_handler: Received message on exact topic {msg.topic}")
                
                if msg.topic == all_players_selected_topic:
                    # All players selected message received
                    try:
                        import json
                        msg_dict = json.loads(msg.payload.decode("utf-8"))
                        sender_client_id = msg_dict.get('clientId')
                        is_retained = msg.retain
                        
                        print(f"[Dialog] All players selected message received from {sender_client_id[:8] if sender_client_id else 'N/A'}... (retained={is_retained}, waiting_for_others={getattr(self, 'waiting_for_others', False)})")
                        
                        # Check if already processed (avoid double processing)
                        if hasattr(self, '_all_players_selected_processed') and self._all_players_selected_processed:
                            print(f"[Dialog] All players selected message already processed, ignoring duplicate")
                            return
                        
                        # CRITICAL: If we're waiting for others, trust the message
                        # The message is only published when all players are registered, so we can trust it
                        # The local connected_players may not be up-to-date due to MQTT latency
                        if not getattr(self, 'waiting_for_others', False):
                            print(f"[Dialog] Not waiting for others, ignoring all_players_selected message")
                            return
                        
                        # Optional: Verify that all players are actually selected before closing
                        # This is a safety check, but we trust the message if we're waiting
                        connected_players = self.session_manager.getConnectedPlayers(self.config.session_id)
                        num_registered = len(connected_players)
                        
                        # Get required number of players (based on actual connected instances for variable player count)
                        required = self._getRequiredPlayersCount()
                        
                        print(f"[Dialog] Verifying: {num_registered}/{required} players registered (message trusted because waiting_for_others=True)")
                        
                        # Only warn if significantly off, but still trust the message
                        if num_registered < required - 1:  # Allow 1 player difference due to latency
                            print(f"[Dialog] WARNING: Local count ({num_registered}/{required}) is low, but trusting message (MQTT latency)")
                        
                        # Mark as processed
                        self._all_players_selected_processed = True
                        
                        # Stop waiting check timer if it's running
                        if hasattr(self, 'waiting_check_timer') and self.waiting_check_timer.isActive():
                            self.waiting_check_timer.stop()
                        
                        self.waiting_for_others = False
                        
                        print(f"[Dialog] All players selected signal received, closing dialog...")
                        
                        # Close dialog - use QMetaObject.invokeMethod to ensure we're in the main Qt thread
                        from PyQt5.QtCore import QMetaObject, Qt
                        QMetaObject.invokeMethod(
                            self,
                            "accept",
                            Qt.QueuedConnection
                        )
                        return
                    except Exception as e:
                        print(f"[Dialog] Error processing all players selected message: {e}")
                        import traceback
                        traceback.print_exc()
                        return
            except RuntimeError:
                # Dialog has been deleted, ignore
                return
            
            # CRITICAL: Forward other messages to current handler (which includes reservation handler)
            if current_handler:
                try:
                    print(f"[Dialog] Forwarding non-all_players_selected message to current handler: topic={msg.topic}")
                    current_handler(client, userdata, msg)
                except Exception as e:
                    print(f"[Dialog] Error forwarding message to handler: {e}, topic={msg.topic}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"[Dialog] WARNING: No current_handler to forward message: topic={msg.topic}")
        
        # Install handler BEFORE subscribing (to receive retained messages)
        # This wraps the reservation handler, so both work together
        self._all_players_selected_handler = all_players_selected_handler
        self.model.mqttManager.client.on_message = all_players_selected_handler
        print(f"[Dialog] Handler after all_players_selected installation: {self.model.mqttManager.client.on_message}")
        print(f"[Dialog] Handler chain: all_players_selected_handler -> {current_handler}")
        
        # Verify handler is actually installed
        if self.model.mqttManager.client.on_message != all_players_selected_handler:
            print(f"[Dialog] ERROR: Handler was not installed correctly! Expected: {all_players_selected_handler}, Got: {self.model.mqttManager.client.on_message}")
        
        # Store a reference to verify handler is still active when messages arrive
        self._verify_all_players_selected_handler = lambda: (
            print(f"[Dialog] VERIFY: Current handler is {self.model.mqttManager.client.on_message}, expected {all_players_selected_handler}, match: {self.model.mqttManager.client.on_message == all_players_selected_handler}")
        )
        
        # Subscribe to all_players_selected topic
        result = self.model.mqttManager.client.subscribe(all_players_selected_topic, qos=1)
        print(f"[Dialog] Subscribed to all players selected topic: {all_players_selected_topic}")
        print(f"[Dialog] Subscribe result: mid={result[0]}, rc={result[1]}")
        
        # Mark as subscribed to prevent multiple subscriptions
        self._all_players_selected_subscribed = True
        
        # Initialize processed flag
        self._all_players_selected_processed = False
        
        # Wait a moment for retained messages to be received, then check if all players are already selected
        # This handles the case where the message was published before this instance subscribed
        QTimer.singleShot(500, self._checkRetainedAllPlayersSelected)
    
    def _checkRetainedAllPlayersSelected(self):
        """Check if a retained all_players_selected message was received, indicating all players are already selected"""
        print(f"[Dialog] Checking retained message: waiting_for_others={self.waiting_for_others}, processed={getattr(self, '_all_players_selected_processed', False)}")
        
        # Check if all players are already selected
        connected_players = self.session_manager.getConnectedPlayers(self.config.session_id)
        num_registered = len(connected_players)
        
        # Get required number of players (based on actual connected instances for variable player count)
        required = self._getRequiredPlayersCount()
        
        print(f"[Dialog] Retained check: {num_registered}/{required} players registered (connected_players: {connected_players}, connected_instances: {getattr(self.config, 'connected_instances_count', 0) if not isinstance(self.config.num_players, int) else 'N/A'})")
        
        if num_registered >= required:
            # All players are already selected!
            if self.waiting_for_others:
                # We're in waiting mode, close via _checkAllPlayersSelected to ensure proper cleanup
                print(f"[Dialog] All players selected while in waiting mode, closing dialog...")
                self._checkAllPlayersSelected()
            else:
                # We haven't clicked OK yet, but all players are selected - close immediately
                print(f"[Dialog] All {required} players already selected when subscribing (retained message), closing dialog...")
                self._all_players_selected_processed = True
                QTimer.singleShot(100, lambda: super(SGDistributedGameDialog, self).accept())
    
    def _publishAllPlayersSelected(self):
        """Publish all players selected message to synchronize dialog closure"""
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            return
        
        # Get all_players_selected topic
        session_topics = self.session_manager.getSessionTopics(self.config.session_id)
        all_players_selected_topic = session_topics[6]  # session_all_players_selected (index 6)
        
        # Create message
        from datetime import datetime
        msg = {
            'clientId': self.model.mqttManager.clientId,
            'timestamp': datetime.now().isoformat(),
            'all_players_selected': True
        }
        
        import json
        serialized_msg = json.dumps(msg)
        
        # Publish with retain=True so instances that subscribe later will receive it
        result = self.model.mqttManager.client.publish(
            all_players_selected_topic,
            serialized_msg,
            qos=1,
            retain=True
        )
        
        print(f"[Dialog] Published all players selected message to {all_players_selected_topic}")
        print(f"[Dialog] Publish result: mid={result.mid}, rc={result.rc}")
    
    def _updatePlayerButtonState(self, player_name, state):
        """Update the visual state of a player button"""
        if player_name not in self.player_radio_buttons:
            return
        
        radio = self.player_radio_buttons[player_name]
        
        # Check if this is our confirmed selection
        is_our_confirmed_selection = (self.reservation_confirmed and 
                                     self.selected_player_name == player_name)
        
        if state == 'available':
            radio.setEnabled(True)
            radio.setStyleSheet("")
            # Remove any special text
            radio.setText(player_name)
            print(f"[Dialog] Updated {player_name} to available state")
        elif state == 'reserved':
            reserved_by_self = (player_name in self.player_reservations and 
                               self.player_reservations[player_name] == self.model.mqttManager.clientId)
            if reserved_by_self:
                # Reserved by this instance
                radio.setEnabled(True)
                radio.setStyleSheet("color: #27ae60; font-weight: bold;")
                radio.setText(f"{player_name} - You have selected")
                # CRITICAL: If this is our confirmed selection, ensure radio button stays checked
                if is_our_confirmed_selection:
                    radio.setChecked(True)
                print(f"[Dialog] Updated {player_name} to reserved by self")
            else:
                # Reserved by another instance
                radio.setEnabled(False)
                radio.setStyleSheet("color: gray;")
                radio.setText(f"{player_name} - Already taken")
                # Don't uncheck if it's our confirmed selection (shouldn't happen, but safety check)
                if not is_our_confirmed_selection:
                    radio.setChecked(False)
                print(f"[Dialog] Updated {player_name} to reserved by other")
        elif state == 'conflict':
            radio.setEnabled(False)
            radio.setStyleSheet("color: #e74c3c; font-weight: bold;")
            radio.setText(f"{player_name} - Conflict detected")
            # Don't uncheck if it's our confirmed selection (shouldn't happen, but safety check)
            if not is_our_confirmed_selection:
                radio.setChecked(False)
            print(f"[Dialog] Updated {player_name} to conflict state")
    
    def _checkForConflict(self, player_name, wait_time_ms=250):
        """
        Check for conflicts after reserving a player.
        
        Args:
            player_name (str): Name of player being reserved
            wait_time_ms (int): Milliseconds to wait for conflict detection
        
        Returns:
            bool: True if conflict detected, False otherwise
        """
        self.pending_reservation = player_name
        self.conflict_detected = False
        
        # Publish reservation
        self.session_manager.reservePlayer(self.config.session_id, player_name)
        
        # Wait for potential conflicts using QTimer for better event processing
        import time
        start_time = time.time()
        while (time.time() - start_time) * 1000 < wait_time_ms:
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()  # Process events to receive MQTT messages
            if self.conflict_detected:
                break
            time.sleep(0.01)  # Small sleep to avoid busy-waiting
        
        self.pending_reservation = None
        return self.conflict_detected
    
    def _showConflictMessage(self):
        """Show conflict error message that auto-closes after 3 seconds"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Player already selected")
        msg_box.setText("This player has just been selected by another instance. Please choose another player.")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setDefaultButton(QMessageBox.Ok)
        
        # Show the message box
        msg_box.show()
        
        # Auto-close after 3 seconds
        QTimer.singleShot(3000, msg_box.close)
    
    def _getRequiredPlayersCount(self):
        """
        Get the required number of players based on configuration.
        
        Returns:
            int: Required number of players
                - If num_players is int: returns that value
                - If num_players is tuple (min, max): returns min(connected_instances_count, max)
                  with validation that connected_instances_count >= min
        """
        if isinstance(self.config.num_players, int):
            return self.config.num_players
        else:
            # Variable number of players: use the actual number of connected instances
            # but capped at num_players_max
            connected_count = getattr(self.config, 'connected_instances_count', 0)
            min_required = self.config.num_players_min
            max_allowed = self.config.num_players_max
            
            # If connected_instances_count is not available or 0, fallback to minimum
            if connected_count <= 0:
                return min_required
            
            # Validate that we have at least the minimum required
            if connected_count < min_required:
                # Not enough instances connected yet, use minimum as requirement
                return min_required
            
            # Use the actual number of connected instances, capped at maximum
            return min(connected_count, max_allowed)
    
    def _updateWaitingStatus(self):
        """Update the waiting status label"""
        if not self.waiting_for_others:
            self.waiting_status_label.hide()
            return
        
        # Count how many players are registered (not just reserved)
        connected_players = self.session_manager.getConnectedPlayers(self.config.session_id)
        num_registered = len(connected_players)
        
        # Get required number of players (based on actual connected instances for variable player count)
        required = self._getRequiredPlayersCount()
        
        remaining = max(0, required - num_registered)
        
        if remaining > 0:
            self.waiting_status_label.setText(f"✓ You selected: {self.selected_player_name}\n⏳ Waiting for {remaining} more player(s) to select their role...")
            self.waiting_status_label.show()
        else:
            self.waiting_status_label.setText(f"✓ You selected: {self.selected_player_name}\n✓ All players have selected their roles!")
            self.waiting_status_label.setStyleSheet("font-size: 11px; color: #27ae60; padding: 5px; font-weight: bold;")
            self.waiting_status_label.show()
    
    def _checkAllPlayersSelected(self):
        """Check if all required players have selected their roles"""
        if not self.waiting_for_others:
            return
        
        # Verify handler is still installed
        if hasattr(self, '_all_players_selected_handler'):
            current_handler = self.model.mqttManager.client.on_message
            if current_handler != self._all_players_selected_handler:
                print(f"[Dialog] WARNING: Handler was replaced! Expected: {self._all_players_selected_handler}, Got: {current_handler}")
        
        # Count how many players are registered (not just reserved)
        connected_players = self.session_manager.getConnectedPlayers(self.config.session_id)
        num_registered = len(connected_players)
        
        # Get required number of players (based on actual connected instances for variable player count)
        required = self._getRequiredPlayersCount()
        
        print(f"[Dialog] Checking: {num_registered}/{required} players registered (connected_players: {connected_players}, connected_instances: {getattr(self.config, 'connected_instances_count', 0) if not isinstance(self.config.num_players, int) else 'N/A'})")
        
        if num_registered >= required:
            # All players selected! 
            print(f"[Dialog] All {required} players have selected their roles. Closing dialog...")
            self.waiting_check_timer.stop()
            self.waiting_for_others = False  # Prevent multiple closes
            self.waiting_status_label.setText(f"✓ All players ready! Starting game...")
            
            # Mark as processed to prevent double processing
            self._all_players_selected_processed = True
            
            # Publish all players selected message to synchronize all instances
            # This ensures all instances close their dialogs at the same time
            # Only publish once to avoid multiple messages
            if not self._all_players_selected_published:
                self._all_players_selected_published = True
                self._publishAllPlayersSelected()
                print(f"[Dialog] Published all players selected message")
            
            # Close this instance's dialog after a short delay
            # (Other instances will close when they receive the MQTT message or when their timer detects all players)
            print(f"[Dialog] Closing dialog in 300ms...")
            QTimer.singleShot(300, lambda: super(SGDistributedGameDialog, self).accept())
    
    def updateAvailablePlayers(self):
        """
        Update the list of available players by filtering out already connected players and reservations.
        Called by timer every second.
        """
        if not self.config.session_id:
            return
        
        # Get connected players from session manager (players already registered)
        connected_players = self.session_manager.getConnectedPlayers(self.config.session_id)
        
        # Update radio buttons based on reservations (primary) and connections (secondary)
        for player_name, radio in self.player_radio_buttons.items():
            # Priority 1: Check if reserved by another instance (most important - shows real-time reservations)
            reserved_by_other = (player_name in self.player_reservations and 
                                self.player_reservations[player_name] != self.model.mqttManager.clientId)
            # Priority 2: Check if connected (registered) - this is a fallback for already registered players
            is_connected = player_name in connected_players
            # Check if this is our confirmed selection
            is_our_confirmed_selection = (self.reservation_confirmed and 
                                        self.selected_player_name == player_name)
            
            if reserved_by_other:
                # Player is reserved by another instance - show as "Already taken"
                self._updatePlayerButtonState(player_name, 'reserved')
            elif is_connected and player_name != self.selected_player_name:
                # Player is already registered by another instance
                radio.setEnabled(False)
                radio.setStyleSheet("color: gray;")
                radio.setText(f"{player_name} - Already connected")
            elif (player_name in self.player_reservations and 
                  self.player_reservations[player_name] == self.model.mqttManager.clientId):
                # Our own reservation - show as selected
                self._updatePlayerButtonState(player_name, 'reserved')
                # CRITICAL: If this is our confirmed selection, ensure radio button stays checked
                if is_our_confirmed_selection:
                    radio.setChecked(True)
            else:
                # Player is available
                self._updatePlayerButtonState(player_name, 'available')
        
        # Auto-select first available player if current selection becomes unavailable
        # BUT: Don't change selection if player is already confirmed or we're waiting for others
        if (self.selected_player_name and 
            not self.reservation_confirmed and 
            not self.waiting_for_others):
            reserved_by_other = (self.selected_player_name in self.player_reservations and 
                               self.player_reservations[self.selected_player_name] != self.model.mqttManager.clientId)
            # Also check if our own reservation is still active
            reserved_by_self = (self.selected_player_name in self.player_reservations and 
                               self.player_reservations[self.selected_player_name] == self.model.mqttManager.clientId)
            
            # Only auto-change if player is unavailable AND not reserved by us
            if (reserved_by_other or (self.selected_player_name in connected_players)) and not reserved_by_self:
                # Current selection is unavailable, find first available
                for player_name in self.player_names:
                    reserved_by_other_check = (player_name in self.player_reservations and 
                                             self.player_reservations[player_name] != self.model.mqttManager.clientId)
                    if (player_name not in connected_players and not reserved_by_other_check):
                        self.player_radio_buttons[player_name].setChecked(True)
                        self.selected_player_name = player_name
                        break
    
    def getSelectedPlayerName(self):
        """
        Returns selected player name (str) or None if cancelled.
        """
        if self.result() == QDialog.Accepted:
            # Get selected player from radio buttons
            checked_button = self.player_button_group.checkedButton()
            if checked_button:
                for player_name, radio in self.player_radio_buttons.items():
                    if radio == checked_button:
                        return player_name
            return self.selected_player_name
        return None
    
    def accept(self):
        """Override accept to validate selection before closing"""
        # CRITICAL: If we're already waiting for others, don't process any new selections
        # This prevents false conflict detection from late-arriving MQTT messages
        if getattr(self, 'waiting_for_others', False):
            print(f"[Dialog] Already waiting for others, ignoring accept() call")
            return
        
        # Get selected player
        checked_button = self.player_button_group.checkedButton()
        if not checked_button:
            QMessageBox.warning(self, "No Player Selected", "Please select a player.")
            return
        
        selected_player = None
        for player_name, radio in self.player_radio_buttons.items():
            if radio == checked_button:
                selected_player = player_name
                break
        
        if not selected_player:
            QMessageBox.warning(self, "Invalid Selection", "Please select a valid player.")
            return
        
        # Validate connection is established
        if not (self.model.mqttManager.client and 
                self.model.mqttManager.client.is_connected()):
            QMessageBox.warning(self, "Not Connected", "Please connect to the broker first.")
            return
        
        # Check if player is reserved by another instance (before attempting our own reservation)
        reserved_by_other = (selected_player in self.player_reservations and 
                            self.player_reservations[selected_player] != self.model.mqttManager.clientId)
        if reserved_by_other:
            self._showConflictMessage()
            self._updatePlayerButtonState(selected_player, 'conflict')
            # After a moment, update to 'reserved' state
            QTimer.singleShot(100, lambda: self._updatePlayerButtonState(selected_player, 'reserved'))
            return
        
        # Release previous reservation if changing player
        if (self.selected_player_name and 
            self.selected_player_name != selected_player and 
            self.selected_player_name in self.player_reservations and
            self.player_reservations[self.selected_player_name] == self.model.mqttManager.clientId):
            self.session_manager.releasePlayer(self.config.session_id, self.selected_player_name)
            if self.selected_player_name in self.player_reservations:
                del self.player_reservations[self.selected_player_name]
        
        # Check for conflicts by attempting reservation
        # Always check for conflicts unless this exact player is already confirmed
        if not (self.reservation_confirmed and self.selected_player_name == selected_player):
            # Need to check for conflicts
            conflict = self._checkForConflict(selected_player, wait_time_ms=250)
            if conflict:
                self._showConflictMessage()
                self._updatePlayerButtonState(selected_player, 'conflict')
                # After a moment, update to 'reserved' state
                QTimer.singleShot(100, lambda: self._updatePlayerButtonState(selected_player, 'reserved'))
                return
        
        # Validate player is not already connected (registered) by another instance
        # CRITICAL: Skip this check if we've already confirmed this player
        # (This prevents false alarms when accept() is called multiple times or when MQTT messages arrive late)
        if not (self.reservation_confirmed and self.selected_player_name == selected_player):
            connected_players = self.session_manager.getConnectedPlayers(self.config.session_id)
            if selected_player in connected_players:
                # Player is already connected - this could be:
                # 1. Another instance registered this player (real conflict)
                # 2. We registered this player in a previous call (shouldn't happen due to early return)
                # 3. Late-arriving MQTT message from another instance (false alarm if we're about to register)
                
                # If we're waiting for others, we've already registered, so this is a duplicate call
                # (This should have been caught by the early return, but check again to be safe)
                if getattr(self, 'waiting_for_others', False):
                    print(f"[Dialog] WARNING: accept() called while waiting_for_others=True, ignoring duplicate call")
                    return
                
                # If we have a pending reservation for this player, it means we're in the process of registering
                # In this case, the player might appear as "connected" due to late MQTT messages from other instances
                # or due to our own registration. Don't show error in this case.
                if self.pending_reservation == selected_player:
                    print(f"[Dialog] Player {selected_player} is in connected_players but we have pending reservation, continuing (likely late MQTT message)")
                    # Continue with registration - the pending reservation will be cleared after registration
                else:
                    # Player is already connected by another instance - this is a real conflict
                    QMessageBox.warning(self, "Player Already Connected", 
                                  f"Player '{selected_player}' is already connected to this session.")
                    return
        
        # Reservation confirmed - register the player
        self.selected_player_name = selected_player
        self.reservation_confirmed = True
        
        # CRITICAL: Clear pending_reservation to prevent false conflict detection
        # from late-arriving MQTT messages
        self.pending_reservation = None
        self.conflict_detected = False
        
        # Register the player on MQTT (this makes it "connected")
        self.session_manager.registerPlayer(
            self.config.session_id,
            selected_player,
            self.config.num_players_min,
            self.config.num_players_max
        )
        
        # Update UI to show we're waiting for others
        self.waiting_for_others = True
        
        # Disable player selection (player is confirmed)
        for player_name, radio in self.player_radio_buttons.items():
            radio.setEnabled(False)
        
        # Disable OK button (selection is confirmed)
        self.ok_button.setEnabled(False)
        self.ok_button.setText("Waiting...")
        
        # Wait a moment for the registration message to be published and propagated
        # Then update status and start checking
        QTimer.singleShot(300, self._updateWaitingStatus)  # Update status after 300ms
        # Start checking if all players are selected
        # Use a longer initial delay to ensure all registration messages are propagated to all instances
        QTimer.singleShot(800, lambda: self.waiting_check_timer.start(500))  # Start checking after 800ms, then every 500ms
        
        # Don't close dialog yet - wait for all players
        # super().accept() will be called automatically when all players are selected
    
    def reject(self):
        """Override reject to cleanup properly before closing"""
        self._cleanupBeforeClose()
        super().reject()
    
    def closeEvent(self, event):
        """Handle close event to cleanup properly"""
        self._cleanupBeforeClose()
        event.accept()
    
    def _cleanupBeforeClose(self):
        """Cleanup method called before dialog closes (reject or closeEvent)"""
        # Set cleaning flag to prevent MQTT callbacks during cleanup
        self._cleaning_up = True
        
        try:
            # 1. Stop all timers
            if hasattr(self, 'waiting_check_timer') and self.waiting_check_timer:
                if self.waiting_check_timer.isActive():
                    self.waiting_check_timer.stop()
            
            if hasattr(self, 'player_update_timer') and self.player_update_timer:
                if self.player_update_timer.isActive():
                    self.player_update_timer.stop()
            
            # 2. Release reservation (even if reservation_confirmed = True)
            if self.selected_player_name:
                try:
                    self.session_manager.releasePlayer(self.config.session_id, self.selected_player_name)
                except Exception as e:
                    print(f"[Dialog] Error releasing player reservation: {e}")
            
            # 3. Disconnect player if waiting_for_others (player is registered)
            if self.waiting_for_others:
                try:
                    # Disconnect from session (publishes player_disconnect message)
                    self.session_manager.disconnect()
                except Exception as e:
                    print(f"[Dialog] Error disconnecting player: {e}")
            
            # 4. Restore MQTT handler if saved
            if (self._handler_before_all_players_selected and 
                self.model.mqttManager.client and 
                hasattr(self, '_all_players_selected_handler') and
                self.model.mqttManager.client.on_message == self._all_players_selected_handler):
                self.model.mqttManager.client.on_message = self._handler_before_all_players_selected
                self._handler_before_all_players_selected = None
            
        except Exception as e:
            print(f"[Dialog] Error during cleanup: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Clear cleaning flag
            self._cleaning_up = False
