# --- Standard library imports ---
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class SGConnectionStatusWidget(QWidget):
    """
    Persistent widget showing connection status and managing connections.
    
    Displays as a separate window showing:
    - Session ID
    - Broker connection status
    - List of connected players with visual indicators
    - Statistics (connected players count)
    """
    
    def __init__(self, parent, model, distributed_config, session_manager):
        """
        Initialize connection status widget.
        
        Args:
            parent: Parent widget (None for separate window)
            model: SGModel instance
            distributed_config: SGDistributedGameConfig instance
            session_manager: SGDistributedSessionManager instance
        """
        super().__init__(parent)
        self.model = model
        self.distributed_config = distributed_config
        self.session_manager = session_manager
        
        # Set as separate window
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("Connection Status")
        self.resize(350, 400)
        
        self._buildUI()
        self._setupTimers()
        self._connectSignals()
        
        # Initial update
        self.updateConnectionStatus()
    
    def _buildUI(self):
        """Build the user interface"""
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("Connection Status")
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Session ID
        session_label = QLabel("Session ID:")
        layout.addWidget(session_label)
        
        self.session_id_label = QLabel(self.distributed_config.session_id or "N/A")
        self.session_id_label.setWordWrap(True)
        self.session_id_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px;")
        layout.addWidget(self.session_id_label)
        
        # Broker Status
        broker_layout = QHBoxLayout()
        broker_label = QLabel("Broker:")
        broker_layout.addWidget(broker_label)
        
        broker_info = QLabel(f"{self.distributed_config.broker_host}:{self.distributed_config.broker_port}")
        broker_layout.addWidget(broker_info)
        
        self.broker_status_label = QLabel("[●] Connected")
        self.broker_status_label.setStyleSheet("color: green; font-weight: bold;")
        broker_layout.addWidget(self.broker_status_label)
        broker_layout.addStretch()
        
        layout.addLayout(broker_layout)
        
        # Players List
        players_label = QLabel("Players:")
        layout.addWidget(players_label)
        
        self.players_list = QListWidget()
        self.players_list.setStyleSheet("QListWidget { border: 1px solid #ccc; border-radius: 3px; }")
        layout.addWidget(self.players_list)
        
        # Statistics
        self.stats_label = QLabel("Connected: 0/0")
        self.stats_label.setStyleSheet("padding: 5px; background-color: #e8f4f8; border-radius: 3px;")
        layout.addWidget(self.stats_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        disconnect_button = QPushButton("Disconnect")
        disconnect_button.clicked.connect(self.disconnect)
        button_layout.addWidget(disconnect_button)
        
        layout.addLayout(button_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _setupTimers(self):
        """Setup timers for periodic updates"""
        # Timer to auto-refresh every 3 seconds
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.updateConnectionStatus)
        self.refresh_timer.start(3000)  # Update every 3 seconds
    
    def _connectSignals(self):
        """Connect to session manager signals"""
        self.session_manager.playerConnected.connect(self._onPlayerConnected)
        self.session_manager.playerDisconnected.connect(self._onPlayerDisconnected)
    
    def updateConnectionStatus(self):
        """Update connection status from MQTT messages and session manager"""
        # Update broker status
        if (self.model.mqttManager.client and 
            self.model.mqttManager.client.is_connected()):
            self.broker_status_label.setText("[●] Connected")
            self.broker_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.broker_status_label.setText("[✗] Disconnected")
            self.broker_status_label.setStyleSheet("color: red; font-weight: bold;")
        
        # Update session ID
        self.session_id_label.setText(self.distributed_config.session_id or "N/A")
        
        # Update players list
        self.players_list.clear()
        
        # Get all player names from model (exclude Admin)
        all_player_names = [name for name in self.model.players.keys() if name != "Admin"]
        connected_players = self.session_manager.getConnectedPlayers(self.distributed_config.session_id)
        assigned_player = self.distributed_config.assigned_player_name
        
        for player_name in all_player_names:
            if player_name == assigned_player:
                # Assigned player (You)
                item_text = f"✓ {player_name} (You)"
                item = QListWidgetItem(item_text)
                item.setForeground(QColor("blue"))
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            elif player_name in connected_players:
                # Other connected players
                item_text = f"● {player_name} (Connected)"
                item = QListWidgetItem(item_text)
                item.setForeground(QColor("green"))
            else:
                # Not yet connected
                item_text = f"⏳ {player_name} (Waiting...)"
                item = QListWidgetItem(item_text)
                item.setForeground(QColor("orange"))
            
            self.players_list.addItem(item)
        
        # Update statistics
        num_connected = len(connected_players)
        if isinstance(self.distributed_config.num_players, int):
            total_players = self.distributed_config.num_players
        else:
            total_players = self.distributed_config.num_players_max
        
        self.stats_label.setText(f"Connected: {num_connected}/{total_players}")
    
    def _onPlayerConnected(self, player_name):
        """Handle player connected signal from session manager"""
        self.updateConnectionStatus()
    
    def _onPlayerDisconnected(self, player_name):
        """Handle player disconnected signal from session manager"""
        self.updateConnectionStatus()
    
    def disconnect(self):
        """Disconnect from session (with confirmation dialog)"""
        reply = QMessageBox.question(
            self,
            "Disconnect",
            "Are you sure you want to disconnect from this session?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Disconnect session manager
            self.session_manager.disconnect()
            
            # Close widget
            self.close()
            
            # Optionally disable distributed mode in model
            # (This would require additional logic in SGModel)
