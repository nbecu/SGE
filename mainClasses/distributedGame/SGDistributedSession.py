# --- Standard library imports ---
import json
from datetime import datetime
from typing import List, Set, Optional


class SGDistributedSession:
    """
    Represents the state of a distributed game session.
    
    This class serves as the single source of truth for session state,
    replacing multiple caches and tracking mechanisms.
    
    Attributes:
        session_id (str): Unique identifier for the session
        creator_client_id (str): Client ID of the instance that created the session
        model_name (str): Name of the game model
        state (str): Current state of the session ('open', 'started', or 'closed')
        connected_instances (Set[str]): Set of client IDs currently connected to the session
        version (int): Version number for conflict resolution (incremented on each update)
        last_heartbeat (datetime): Timestamp of the last heartbeat from the creator
        created_at (datetime): Timestamp when the session was created
        last_updated (datetime): Timestamp of the last update
        num_players_min (int): Minimum number of players required
        num_players_max (int): Maximum number of players allowed
    """
    
    def __init__(self, session_id: str, creator_client_id: str, model_name: str = "Unknown",
                 num_players_min: int = 1, num_players_max: int = 4):
        """
        Initialize a new session.
        
        Args:
            session_id: Unique identifier for the session
            creator_client_id: Client ID of the instance creating the session
            model_name: Name of the game model
            num_players_min: Minimum number of players required
            num_players_max: Maximum number of players allowed
        """
        self.session_id = session_id
        self.creator_client_id = creator_client_id
        self.model_name = model_name
        self.state = 'open'
        self.connected_instances: Set[str] = set()
        self.version = 1
        self.last_heartbeat = datetime.now()
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.num_players_min = num_players_min
        self.num_players_max = num_players_max
        
        # Add creator to connected instances
        self.connected_instances.add(creator_client_id)
    
    def to_dict(self) -> dict:
        """
        Convert session to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the session
        """
        return {
            'session_id': self.session_id,
            'creator_client_id': self.creator_client_id,
            'model_name': self.model_name,
            'state': self.state,
            'connected_instances': list(self.connected_instances),
            'version': self.version,
            'last_heartbeat': self.last_heartbeat.isoformat(),
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'num_players_min': self.num_players_min,
            'num_players_max': self.num_players_max
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SGDistributedSession':
        """
        Create session from dictionary (deserialization).
        
        Args:
            data: Dictionary representation of the session
            
        Returns:
            SGDistributedSession instance
        """
        session = cls(
            session_id=data['session_id'],
            creator_client_id=data['creator_client_id'],
            model_name=data.get('model_name', 'Unknown'),
            num_players_min=data.get('num_players_min', 1),
            num_players_max=data.get('num_players_max', 4)
        )
        
        # Note: 'started' is a valid state (session where game has begun)
        session.state = data.get('state', 'open')
        session.connected_instances = set(data.get('connected_instances', []))
        session.version = data.get('version', 1)
        
        # Parse datetime strings
        if 'last_heartbeat' in data:
            session.last_heartbeat = datetime.fromisoformat(data['last_heartbeat'])
        if 'created_at' in data:
            session.created_at = datetime.fromisoformat(data['created_at'])
        if 'last_updated' in data:
            session.last_updated = datetime.fromisoformat(data['last_updated'])
        
        return session
    
    def add_instance(self, client_id: str) -> bool:
        """
        Add an instance to the session.
        
        Args:
            client_id: Client ID of the instance to add
            
        Returns:
            True if instance was added, False if already present or session is closed
        """
        if not self.is_open():
            return False
        
        if client_id not in self.connected_instances:
            self.connected_instances.add(client_id)
            self.version += 1
            self.last_updated = datetime.now()
            return True
        return False
    
    def remove_instance(self, client_id: str) -> bool:
        """
        Remove an instance from the session.
        
        Args:
            client_id: Client ID of the instance to remove
            
        Returns:
            True if instance was removed, False if not present
        """
        if client_id in self.connected_instances:
            self.connected_instances.remove(client_id)
            self.version += 1
            self.last_updated = datetime.now()
            return True
        return False
    
    def close(self):
        """
        Close the session (cancelled/abandoned).
        
        Sets state to 'closed' and updates version and timestamp.
        Note: Use start() to mark a session as started (game in progress), not close().
        """
        if not self.is_closed():
            self.state = 'closed'
            self.version += 1
            self.last_updated = datetime.now()
    
    def start(self):
        """
        Mark the session as started (game has begun).
        
        Sets state to 'started' and updates version and timestamp.
        A started session is no longer joinable, but the game is active.
        This is different from close(), which marks a session as cancelled/abandoned.
        """
        if self.state != 'started':
            self.state = 'started'
            self.version += 1
            self.last_updated = datetime.now()
    
    def update_heartbeat(self):
        """
        Update the heartbeat timestamp.
        
        Called by the creator instance to indicate it's still alive.
        """
        self.last_heartbeat = datetime.now()
        self.last_updated = datetime.now()
        # Note: We don't increment version for heartbeat-only updates to reduce traffic
        # Version is only incremented for state changes
    
    def is_expired(self, timeout_seconds: float = 15.0) -> bool:
        """
        Check if the session has expired (creator hasn't sent heartbeat).
        
        Note: Sessions with state 'started' are never considered expired, as the game
        is in progress and heartbeat may not be as critical.
        
        Args:
            timeout_seconds: Number of seconds without heartbeat before considering expired
            
        Returns:
            True if session is expired, False otherwise
        """
        if self.is_closed():
            return True
        
        time_since_heartbeat = (datetime.now() - self.last_heartbeat).total_seconds()
        return time_since_heartbeat > timeout_seconds
    
    def can_accept_more_instances(self) -> bool:
        """
        Check if the session can accept more instances.
        
        Returns:
            True if session is open and has capacity, False otherwise
        """
        if not self.is_open():
            return False
        
        return len(self.connected_instances) < self.num_players_max
    
    def get_num_connected(self) -> int:
        """
        Get the number of connected instances.
        
        Returns:
            Number of connected instances
        """
        return len(self.connected_instances)
    
    def is_creator(self, client_id: str) -> bool:
        """
        Check if a client ID is the creator of the session.
        
        Args:
            client_id: Client ID to check
            
        Returns:
            True if client_id is the creator, False otherwise
        """
        return client_id == self.creator_client_id
    
    def is_open(self) -> bool:
        """Check if session is open (accepting new instances)."""
        return self.state == 'open'
    
    def is_started(self) -> bool:
        """Check if session has started (game is in progress)."""
        return self.state == 'started'
    
    def is_closed(self) -> bool:
        """Check if session is closed (cancelled/abandoned)."""
        return self.state == 'closed'
    
    def is_joinable(self) -> bool:
        """Check if session can accept new instances (open only)."""
        return self.state == 'open'
    
    def is_active(self) -> bool:
        """Check if session is active (open or started, not closed)."""
        return self.state in ('open', 'started')
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (f"SGDistributedSession(session_id={self.session_id[:8]}..., "
                f"state={self.state}, instances={len(self.connected_instances)}/{self.num_players_max}, "
                f"version={self.version})")

