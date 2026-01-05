# --- Standard library imports ---
import uuid
import random


class SGDistributedGameConfig:
    """
    Configuration class for distributed multiplayer game mode.
    
    Stores all distributed game configuration parameters including:
    - Number of players (fixed or range)
    - Assigned player name for this instance
    - Session ID for topic isolation
    - Shared random seed
    - MQTT broker configuration
    """
    
    def __init__(self):
        """Initialize distributed game configuration with default values."""
        self.num_players = None  # int or tuple: Number of players (fixed int or (min, max) range)
        self.num_players_min = None  # int: Minimum number of players (extracted from num_players)
        self.num_players_max = None  # int: Maximum number of players (extracted from num_players)
        self.assigned_player_name = None  # str: Name of player assigned to this instance
        self.session_id = None  # str: Unique session identifier
        self.shared_seed = None  # int: Shared random seed
        self.broker_host = "localhost"  # str: MQTT broker host
        self.broker_port = 1883  # int: MQTT broker port
        self.mqtt_update_type = "Instantaneous"  # str: "Instantaneous" or "Phase"
        self.seed_sync_timeout = 1.0  # float: Timeout in seconds to wait for existing seed before becoming leader
        self.is_session_creator = False  # bool: True if this instance created the session
        self.connected_instances_count = 0  # int: Number of connected instances
    
    def set_num_players(self, num_players):
        """
        Set number of players (fixed or range).
        
        Args:
            num_players: int (fixed number) or tuple (min, max) range
        
        Examples:
            config.set_num_players(2)  # Fixed 2 players
            config.set_num_players((2, 4))  # Range: 2-4 players
        """
        self.num_players = num_players
        
        if isinstance(num_players, int):
            # Fixed number of players
            self.num_players_min = num_players
            self.num_players_max = num_players
        elif isinstance(num_players, tuple) and len(num_players) == 2:
            # Range of players
            self.num_players_min = num_players[0]
            self.num_players_max = num_players[1]
        else:
            raise ValueError(f"num_players must be int or tuple (min, max), got {type(num_players)}")
    
    def generate_session_id(self):
        """Generate a unique session ID (UUID4)."""
        self.session_id = str(uuid.uuid4())
        return self.session_id
    
    def generate_shared_seed(self):
        """Generate a random seed."""
        self.shared_seed = random.randint(1, 1000000)
        return self.shared_seed
    
    def validate(self):
        """
        Validate configuration parameters.
        
        Returns:
            tuple: (is_valid, error_message)
                - is_valid (bool): True if configuration is valid
                - error_message (str): Error message if invalid, None if valid
        """
        if self.num_players is None:
            return False, "num_players must be set"
        
        if self.num_players_min is None or self.num_players_max is None:
            return False, "num_players_min and num_players_max must be set"
        
        if self.num_players_min > self.num_players_max:
            return False, "num_players_min must be <= num_players_max"
        
        if self.num_players_min < 1:
            return False, "num_players_min must be >= 1"
        
        if self.session_id is None or self.session_id == "":
            return False, "session_id must be set"
        
        if self.assigned_player_name is None or self.assigned_player_name == "":
            return False, "assigned_player_name must be set"
        
        if self.broker_host is None or self.broker_host == "":
            return False, "broker_host must be set"
        
        if not isinstance(self.broker_port, int) or self.broker_port < 1 or self.broker_port > 65535:
            return False, "broker_port must be an integer between 1 and 65535"
        
        if self.mqtt_update_type not in ["Instantaneous", "Phase"]:
            return False, "mqtt_update_type must be 'Instantaneous' or 'Phase'"
        
        return True, None
