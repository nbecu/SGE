# Distributed Game Module
"""
Module containing all classes related to distributed multiplayer games in SGE.

Classes:
    - SGDistributedConnectionDialog: Dialog for MQTT connection and seed synchronization
    - SGDistributedGameConfig: Configuration class for distributed games
    - SGDistributedGameDialog: Dialog for player selection
    - SGDistributedSession: Session state representation (single source of truth)
    - SGDistributedSessionManager: Manages session-level MQTT operations
    - SGMQTTManager: Manages MQTT communication for multiplayer functionality
    - SGConnectionStatusWidget: Widget showing connection status
    - SGMQTTHandlerManager: Centralizes MQTT message handler management with chaining support
    - SGConnectionStateManager: Manages connection dialog state transitions
    - SGSessionDiscoveryManager: Manages session discovery and caching
"""

from mainClasses.distributedGame.SGDistributedConnectionDialog import SGDistributedConnectionDialog
from mainClasses.distributedGame.SGDistributedGameConfig import SGDistributedGameConfig
from mainClasses.distributedGame.SGDistributedGameDialog import SGDistributedGameDialog
from mainClasses.distributedGame.SGDistributedSession import SGDistributedSession
from mainClasses.distributedGame.SGDistributedSessionManager import SGDistributedSessionManager
from mainClasses.distributedGame.SGMQTTManager import SGMQTTManager
from mainClasses.distributedGame.SGConnectionStatusWidget import SGConnectionStatusWidget
from mainClasses.distributedGame.SGMQTTHandlerManager import SGMQTTHandlerManager, HandlerPriority
from mainClasses.distributedGame.SGConnectionStateManager import SGConnectionStateManager, ConnectionState
from mainClasses.distributedGame.SGSessionDiscoveryManager import SGSessionDiscoveryManager

__all__ = [
    'SGDistributedConnectionDialog',
    'SGDistributedGameConfig',
    'SGDistributedGameDialog',
    'SGDistributedSession',
    'SGDistributedSessionManager',
    'SGMQTTManager',
    'SGConnectionStatusWidget',
    'SGMQTTHandlerManager',
    'HandlerPriority',
    'SGConnectionStateManager',
    'ConnectionState',
    'SGSessionDiscoveryManager',
]

