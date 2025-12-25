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
        self._subscribeToAllPlayersSelected()
        
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
            if (self.pending_reservation == player_name and 
                action == 'reserve' and 
                client_id != self.model.mqttManager.clientId):
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
        print(f"[Dialog] Player registered signal received: {player_name}")
        # Update waiting status if we're waiting
        if self.waiting_for_others:
            # Use longer delay to ensure the connected_players dict is updated
            QTimer.singleShot(200, self._updateWaitingStatus)
            QTimer.singleShot(300, self._checkAllPlayersSelected)
    
    def _subscribeToAllPlayersSelected(self):
        """Subscribe to all_players_selected topic to synchronize dialog closure"""
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
        print(f"[Dialog] Current handler before all_players_selected subscription: {current_handler}")
        
        def all_players_selected_handler(client, userdata, msg):
            # CRITICAL: Protect against RuntimeError if dialog is destroyed
            try:
                if msg.topic == all_players_selected_topic:
                    # All players selected message received
                    try:
                        import json
                        msg_dict = json.loads(msg.payload.decode("utf-8"))
                        sender_client_id = msg_dict.get('clientId')
                        
                        print(f"[Dialog] All players selected message received from {sender_client_id[:8] if sender_client_id else 'N/A'}...")
                        
                        # Check if already processed (avoid double processing)
                        if hasattr(self, '_all_players_selected_processed') and self._all_players_selected_processed:
                            print(f"[Dialog] All players selected message already processed, ignoring duplicate")
                            return
                        
                        # Mark as processed
                        self._all_players_selected_processed = True
                        
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
        
        # Subscribe to all_players_selected topic
        result = self.model.mqttManager.client.subscribe(all_players_selected_topic, qos=1)
        print(f"[Dialog] Subscribed to all players selected topic: {all_players_selected_topic}")
        print(f"[Dialog] Subscribe result: mid={result[0]}, rc={result[1]}")
        
        # Initialize processed flag
        self._all_players_selected_processed = False
    
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
        
        # Publish with retain=False (one-time message)
        result = self.model.mqttManager.client.publish(
            all_players_selected_topic,
            serialized_msg,
            qos=1,
            retain=False
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
    
    
    def _updateWaitingStatus(self):
        """Update the waiting status label"""
        if not self.waiting_for_others:
            self.waiting_status_label.hide()
            return
        
        # Count how many players are registered (not just reserved)
        connected_players = self.session_manager.getConnectedPlayers(self.config.session_id)
        num_registered = len(connected_players)
        
        # Get required number of players
        if isinstance(self.config.num_players, int):
            required = self.config.num_players
        else:
            required = self.config.num_players_max  # Use max for waiting
        
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
        
        # Count how many players are registered (not just reserved)
        connected_players = self.session_manager.getConnectedPlayers(self.config.session_id)
        num_registered = len(connected_players)
        
        # Get required number of players
        if isinstance(self.config.num_players, int):
            required = self.config.num_players
        else:
            required = self.config.num_players_max  # Use max for waiting
        
        print(f"[Dialog] Checking: {num_registered}/{required} players registered (connected_players: {connected_players})")
        
        if num_registered >= required:
            # All players selected! Publish message to synchronize all instances
            print(f"[Dialog] All {required} players have selected their roles. Publishing synchronization message...")
            self.waiting_check_timer.stop()
            self.waiting_for_others = False  # Prevent multiple closes
            self.waiting_status_label.setText(f"✓ All players ready! Starting game...")
            
            # Publish all players selected message to synchronize all instances
            # This ensures all instances close their dialogs at the same time
            # Only publish once to avoid multiple messages
            if not self._all_players_selected_published:
                self._all_players_selected_published = True
                self._publishAllPlayersSelected()
            
            # Also close this instance's dialog after a short delay
            # (Other instances will close when they receive the MQTT message)
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
        
        # Validate player is not already connected (registered)
        connected_players = self.session_manager.getConnectedPlayers(self.config.session_id)
        if selected_player in connected_players:
            QMessageBox.warning(self, "Player Already Connected", 
                              f"Player '{selected_player}' is already connected to this session.")
            return
        
        # Reservation confirmed - register the player
        self.selected_player_name = selected_player
        self.reservation_confirmed = True
        
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
        """Override reject to release reservation if any"""
        # Release any reservation before closing
        if self.selected_player_name and not self.reservation_confirmed:
            self.session_manager.releasePlayer(self.config.session_id, self.selected_player_name)
        super().reject()
    
    def closeEvent(self, event):
        """Handle close event to release reservation"""
        # Release any reservation before closing
        if self.selected_player_name and not self.reservation_confirmed:
            self.session_manager.releasePlayer(self.config.session_id, self.selected_player_name)
        event.accept()
