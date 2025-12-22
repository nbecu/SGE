# --- Standard library imports ---
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class SGDistributedGameDialog(QDialog):
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
        
        self.setWindowTitle("Select Your Player")
        self.setModal(True)
        self.resize(400, 300)
        
        self._buildUI()
        self._setupTimers()
        
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
    
    
    def updateAvailablePlayers(self):
        """
        Update the list of available players by filtering out already connected players.
        Called by timer every second.
        """
        if not self.config.session_id:
            return
        
        # Get connected players from session manager
        connected_players = self.session_manager.getConnectedPlayers(self.config.session_id)
        
        # Update radio buttons: disable already connected players
        for player_name, radio in self.player_radio_buttons.items():
            if player_name in connected_players and player_name != self.selected_player_name:
                radio.setEnabled(False)
                radio.setStyleSheet("color: gray;")
            else:
                radio.setEnabled(True)
                radio.setStyleSheet("")
        
        # Auto-select first available player if current selection becomes unavailable
        if self.selected_player_name and self.selected_player_name in connected_players:
            # Current selection is unavailable, find first available
            for player_name in self.player_names:
                if player_name not in connected_players:
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
        
        # Validate player is not already connected
        connected_players = self.session_manager.getConnectedPlayers(self.config.session_id)
        if selected_player in connected_players:
            QMessageBox.warning(self, "Player Already Connected", 
                              f"Player '{selected_player}' is already connected to this session.")
            return
        
        self.selected_player_name = selected_player
        super().accept()
