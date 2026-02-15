# --- Standard library imports ---
import json
import queue
import struct
import uuid
from PyQt5.QtCore import QTimer

# --- Third-party imports ---
from paho.mqtt import client as mqtt_client


class SGMQTTManager:
    """
    Manages MQTT communication for SGE multiplayer functionality.
    
    This class handles all MQTT-related operations including:
    - Connection to MQTT broker
    - Message publishing and subscription
    - Game action synchronization
    - Next turn coordination
    """
    
    # Centralized list of game topics (base names without prefixes)
    # step_navigation: one topic for both backward and forward; payload has 'direction': 'backward'|'forward'
    # recovery: single topic for request/response; payload has 'type': 'request'|'response', request_id, etc.
    GAME_TOPICS = ['gameAction_performed', 'nextTurn', 'execute_method', 'step_navigation', 'recovery']
    
    def __init__(self, model):
        """
        Initialize MQTT Manager
        
        Args:
            model: Reference to the SGModel instance
        """
        self.model = model
        self.client = None
        self.clientId = None
        self.session_id = None  # Session ID for topic isolation (None = global topics for backward compatibility)
        self.q = None
        self.majTimer = None
        self.haveToBeClose = False
        self.actionsFromBrokerToBeExecuted = []
        self._recovery_response_callback = None  # One-shot callback (state, assigned_player_name, seed, rng_state) for reconnecting instance
    
    def setRecoveryResponseCallback(self, callback):
        """Register callback for recovery response (used by connection dialog when reconnecting)."""
        self._recovery_response_callback = callback
    
    @classmethod
    def getGameTopics(cls, session_id=None):
        """
        Get full game topic names with game_ prefix and optional session prefix.
        
        Args:
            session_id (str, optional): Session ID for topic isolation
            
        Returns:
            list: List of full topic names (e.g., ['game_gameAction_performed', 'game_nextTurn', ...])
        """
        topics = []
        for base_topic in cls.GAME_TOPICS:
            full_topic = f"game_{base_topic}"
            if session_id:
                full_topic = f"{session_id}/{full_topic}"
            topics.append(full_topic)
        return topics
    
    @classmethod
    def isGameTopic(cls, topic, session_id=None):
        """
        Check if a topic is a game topic.

        Args:
            topic (str): Topic name to check
            session_id (str, optional): Session ID for topic isolation

        Returns:
            bool: True if topic is a game topic, False otherwise
        """
        game_topics = cls.getGameTopics(session_id)
        return topic in game_topics
        
    def setMQTTProtocol(self, majType, broker_host="localhost", broker_port=1883, session_id=None):
        """
        Set the MQTT protocol configuration

        Args:
            majType (str): "Phase" or "Instantaneous"
            broker_host (str): MQTT broker host (default: "localhost")
            broker_port (int): MQTT broker port (default: 1883)
            session_id (str, optional): Session ID for topic isolation. 
                                       If None, uses global topics (backward compatibility)
        """
        self.clientId = uuid.uuid4().hex
        self.session_id = session_id  # Store session_id for topic prefixing
        self.majTimer = QTimer(self.model)
        self.majTimer.timeout.connect(self.onMAJTimer)
        self.majTimer.start(100)
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.initMQTT()
        self.model.mqttMajType = majType

    def initMQTT(self):
        """Init the MQTT client"""
        def on_message(aClient, userdata, msg):
            self.q.put(msg.payload)
            # Log désactivé pour réduire la verbosité
            # print("message received " + msg.topic)
            message = self.q.get()
            msg_decoded = message.decode("utf-8")
            
            # Check if this is a game topic using centralized method
            if self.isGameTopic(msg.topic, self.session_id):
                unserializedMsg = json.loads(msg_decoded)
                # Skip processing only for our own messages (some payloads e.g. recovery response have no 'clientId')
                if unserializedMsg.get('clientId') == self.clientId:
                    pass
                else:
                    # Determine which game topic this is
                    game_topics = self.getGameTopics(self.session_id)
                    if msg.topic == game_topics[0]:  # game_gameAction_performed
                        self.processBrokerMsg_gameAction_performed(unserializedMsg)
                    elif msg.topic == game_topics[2]:  # game_execute_method
                        self.processBrokerMsg_executeMethod(unserializedMsg)
                    elif msg.topic == game_topics[1]:  # game_nextTurn
                        self.processBrokerMsg_nextTrun(unserializedMsg)
                    elif msg.topic == game_topics[3] or msg.topic.endswith('game_step_navigation'):
                        self.processBrokerMsg_step_navigation(unserializedMsg)
                    elif msg.topic == game_topics[4] or msg.topic.endswith('game_recovery'):
                        self.processBrokerMsg_recovery(unserializedMsg)
                return
            # Session registration/disconnect: forward so Connection Status updates after reconnect
            if self.session_id and ('session_player_registration' in msg.topic or 'session_player_disconnect' in msg.topic):
                if msg.topic.startswith(self.session_id + "/"):
                    session_manager = getattr(self.model, 'distributedSessionManager', None)
                    if session_manager:
                        session_manager.processRegistrationOrDisconnectMessage(msg)
            # Other unknown topics are ignored

        self.connect_mqtt()

        # Subscribe to game topics using centralized method
        game_topics = self.getGameTopics(self.session_id)
        for topic in game_topics:
            self.client.subscribe(topic)
        
        self.client.on_message = on_message

    def ensureSubscribedToGameTopics(self, session_id=None):
        """Subscribe to all game topics (including step_navigation). Call when reusing an existing connection
        so that subscriptions use the current session_id (e.g. after joining a session)."""
        if not self.client or not self.client.is_connected():
            return
        sid = session_id if session_id is not None else self.session_id
        for topic in self.getGameTopics(sid):
            self.client.subscribe(topic)

    def connect_mqtt(self):
        """MQTT Basic function to connect to the broker"""
        def on_log(client, userdata, level, buf):
            # Logs MQTT de bas niveau désactivés pour réduire la verbosité
            pass

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print(f"Connected to MQTT Broker at {self.broker_host}:{self.broker_port}")
            else:
                # Connection failed - error codes from paho-mqtt
                error_messages = {
                    1: "Connection refused - incorrect protocol version",
                    2: "Connection refused - invalid client identifier",
                    3: "Connection refused - server unavailable",
                    4: "Connection refused - bad username or password",
                    5: "Connection refused - not authorised"
                }
                error_msg = error_messages.get(rc, f"Connection refused - return code {rc}")
                print(f"Failed to connect to MQTT broker: {error_msg}")

        def on_disconnect(client, userdata, flags, rc=0):
            # Disconnected from MQTT broker
            pass

        print("connectMQTT")
        # self.client = mqtt_client.Client(self.model.currentPlayerName)  # Old version
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, self.model.currentPlayerName) # for the new version of paho possible correction
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_log = on_log
        self.q = queue.Queue()
        self.model.timer.start(5)
        
        # Wrap connect() in try/except to catch synchronous connection errors
        # Note: ConnectionRefusedError and TimeoutError are subclasses of OSError in Python 3
        # IMPORTANT: We catch all exceptions and check the type to ensure we catch everything
        try:
            self.client.connect(self.broker_host, self.broker_port)
        except BaseException as e:
            # Catch ALL exceptions (including SystemExit, KeyboardInterrupt, etc.)
            # This ensures we catch ConnectionRefusedError, TimeoutError, and any other exceptions
            error_msg = f"Unable to connect to MQTT broker at {self.broker_host}:{self.broker_port}. "
            
            # Check exception type and error code
            error_type = type(e).__name__
            error_str = str(e).lower()
            error_code = getattr(e, 'errno', None)
            
            # Handle specific exception types
            if isinstance(e, TimeoutError) or error_type == 'TimeoutError' or "timeout" in error_str:
                error_msg += "Connection timed out. The broker may be unreachable or not responding."
            elif isinstance(e, ConnectionRefusedError) or error_type == 'ConnectionRefusedError':
                error_msg += "The broker may be closed or not running."
            elif isinstance(e, OSError):
                # Handle OSError and its subclasses
                if (error_code in (10061, 111) or 
                    "connection refused" in error_str or 
                    "refused" in error_str or
                    "no connection could be made" in error_str or
                    "aucune connexion" in error_str):
                    error_msg += "The broker may be closed or not running."
                elif "name or service not known" in error_str or "getaddrinfo failed" in error_str:
                    error_msg += "The broker hostname could not be resolved."
                elif "timeout" in error_str:
                    error_msg += "Connection timed out. The broker may be unreachable."
                else:
                    error_msg += f"Error: {str(e)}"
            else:
                # Any other exception type
                error_msg += f"Error: {str(e)}"
            
            # Always raise ConnectionError with user-friendly message
            raise ConnectionError(error_msg) from e
        
        self.client.user_data_set(self)
        # Use loop_start() instead of manual loop() in thread to avoid struct format errors
        # loop_start() runs in its own background thread automatically
        self.client.loop_start()

    def buildNextTurnMsgAndPublishToBroker(self):
        """Build and publish next turn message to MQTT broker"""
        # Get game topics and use the nextTurn topic (index 1)
        game_topics = self.getGameTopics(self.session_id)
        msgTopic = game_topics[1]  # game_nextTurn (with or without session prefix)
        
        msg_dict={}
        msg_dict['clientId']=self.clientId
        #eventually, one can add some more info about this nextTurn action
        # msg_dict['foo']= foo
        serializedMsg = json.dumps(msg_dict)
        if self.client:
            self.client.publish(msgTopic,serializedMsg)
        else: raise ValueError('Why does this case happens?')

    def buildStepNavigationMsgAndPublishToBroker(self, direction):
        """Build and publish step navigation (backward or forward) message to MQTT broker.
        direction: 'backward' or 'forward'. All instances execute the same step locally."""
        game_topics = self.getGameTopics(self.session_id)
        msgTopic = game_topics[3]  # game_step_navigation
        msg_dict = {'clientId': self.clientId, 'direction': direction}
        serializedMsg = json.dumps(msg_dict)
        if self.client:
            self.client.publish(msgTopic, serializedMsg)
        else:
            raise ValueError('MQTT client not initialized')

    def processBrokerMsg_step_navigation(self, unserializedMsg):
        """Process incoming step_navigation message from broker: queue one local backward or forward step."""
        direction = unserializedMsg.get('direction', 'backward')
        if direction not in ('backward', 'forward'):
            direction = 'backward'
        self.actionsFromBrokerToBeExecuted.append({'action_type': direction})

    def processBrokerMsg_recovery(self, msg):
        """
        Handle recovery topic: request (we're in game, respond with state + assigned_player_name)
        or response (we're reconnecting, apply state and call callback).
        """
        msg_type = msg.get('type')
        if msg_type == 'request':
            req_client_id = msg.get('clientId')
            request_id = msg.get('request_id')
            if req_client_id == self.clientId or not request_id:
                return
            session_manager = getattr(self.model, 'distributedSessionManager', None)
            if not session_manager:
                return
            # Same client_id reconnecting (e.g. network blip): use existing slot
            assigned_name = session_manager.getDisconnectedPlayerName(req_client_id)
            if not assigned_name:
                # New process (new client_id) reconnecting after crash/kill: assign one disconnected slot
                assigned_name, _ = session_manager.popOneDisconnectedPlayerForRecovery()
            if not assigned_name:
                # Fallback: liveness may not have run yet (15s); assign any player slot not in connected_players
                all_player_names = [n for n in getattr(self.model, 'players', {}).keys() if n != 'Admin']
                available = [n for n in all_player_names if n not in session_manager.connected_players]
                if available:
                    assigned_name = available[0]
            if not assigned_name:
                # Fallback: reconnect before 15s prune; assign a "stale" slot (no heartbeat for 10s)
                assigned_name, _ = session_manager.popOneStalePlayerForRecovery(threshold_seconds=10)
            if not assigned_name:
                return
            try:
                from mainClasses.SGStateSnapshot import build_snapshot_from_model
                state = build_snapshot_from_model(self.model, include_history_value=True)
            except Exception as e:
                import traceback
                traceback.print_exc()
                return
            game_topics = self.getGameTopics(self.session_id)
            recovery_topic = game_topics[4]
            # Include synced seed so reconnecting instance can display it; include full RNG state so B is in sync with A (same number of draws)
            seed = getattr(session_manager, 'synced_seed_value', None) or getattr(session_manager, 'synced_seed', None)
            import random
            rng_state = random.getstate()
            def _rng_state_to_json(s):
                if isinstance(s, tuple):
                    return [_rng_state_to_json(x) for x in s]
                return s
            # So reconnecting instance can show other players as Connected in its Connection Status
            connected_players = dict(getattr(session_manager, 'connected_players', None) or {})
            response = {
                'type': 'response',
                'request_id': request_id,
                'target_client_id': req_client_id,
                'assigned_player_name': assigned_name,
                'state': state,
                'seed': seed,
                'rng_state': _rng_state_to_json(rng_state),
                'connected_players': connected_players
            }
            if self.client:
                self.client.publish(recovery_topic, json.dumps(response), qos=1)
        elif msg_type == 'response':
            target = msg.get('target_client_id')
            state = msg.get('state')
            assigned_player_name = msg.get('assigned_player_name')
            cb = self._recovery_response_callback
            if target != self.clientId:
                return
            if not cb or state is None:
                return
            self._recovery_response_callback = None
            seed = msg.get('seed')
            rng_state = msg.get('rng_state')  # Full RNG state so B matches A's random draw count
            connected_players = msg.get('connected_players') or {}  # So B can show others as Connected in Connection Status
            # Emit via model signal so the slot runs in the main thread (QTimer.singleShot from MQTT thread was not always processed)
            if hasattr(self.model, 'recoveryResponseReceived'):
                self.model.recoveryResponseReceived.emit(state, assigned_player_name, seed, rng_state, connected_players)
            else:
                QTimer.singleShot(0, lambda: cb(state, assigned_player_name, seed, rng_state, connected_players))

    def publishRecoveryRequest(self):
        """Publish a recovery request on game_recovery topic (reconnecting instance)."""
        game_topics = self.getGameTopics(self.session_id)
        recovery_topic = game_topics[4]
        request_id = uuid.uuid4().hex
        msg = {'type': 'request', 'clientId': self.clientId, 'request_id': request_id}
        if self.client:
            self.client.publish(recovery_topic, json.dumps(msg), qos=1)
        return request_id

    def buildExeMsgAndPublishToBroker(self,*args):
        """
        Method to build a json_string 'Execution message' and publish it on the mqtt broker
        A 'Execution message' is a message that will triger a specified method, of a specified object, to be executed with some specified arguments
        """
        #Check that a client is declared
        if not self.client: 
            raise ValueError('Why does this case happens?')
        
        baseTopic = args[0] # The first arg is the base topic of the msg (should be without game_ prefix)
        # Add game_ prefix and session prefix if needed
        full_topic = f"game_{baseTopic}"
        if self.session_id:
            msgTopic = f"{self.session_id}/{full_topic}"
        else:
            msgTopic = full_topic
        
        objectAndMethodToExe = args[1] #Second arg is a dict that identifies the object and method to be executed. The dict has three keys: 'class_name', 'id', 'method' (method name called by the object )
        argsToSerialize= args[2:] # The third to the last arg, correspond to all the arguments for the method

        #build the message to publish
        msg_dict={}
        msg_dict['clientId']=self.clientId
        msg_dict['objectAndMethod']= objectAndMethodToExe
        listOfArgs=[]
        for arg in argsToSerialize:
            if isinstance(arg,self.model.JsonManagedDataTypes):
                listOfArgs.append(arg)
            else:
                listOfArgs.append(['SGObjectIdentifer',arg.getObjectIdentiferForJsonDumps()])
        msg_dict['listOfArgs']= listOfArgs

        #serialize (encode) and publish the message
        serializedMsg = json.dumps(msg_dict)
        self.client.publish(msgTopic,serializedMsg)

    def processBrokerMsg_nextTrun(self, unserializedMsg):
        """Process incoming nextTurn message from broker"""
        #eventually, one can add and process some more info about this nextTurn action
        self.actionsFromBrokerToBeExecuted.append({
            'action_type':'nextTurn'
             })
        
    def processBrokerMsg_gameAction_performed(self, unserializedMsg):
        """Method to process the incoming of a "gameAction_performed" msg"""
        msg = unserializedMsg
        objectAndMethod = msg['objectAndMethod']
        classOfObjectToExe = objectAndMethod['class_name']
        idOfObjectToExe = objectAndMethod['id']
        methodOfObjectToExe = objectAndMethod['method']
        if methodOfObjectToExe != 'perform_with': 
            raise ValueError('This method only works for msg that should execute gameAction.perform_with(*args)')
        aGameAction = self.model.getGameAction_withClassAndId(classOfObjectToExe,idOfObjectToExe)
        listOfArgs=[]
        for aArgSpec in msg['listOfArgs']:
            if isinstance(aArgSpec, list) and len(aArgSpec)>0 and aArgSpec[0]== 'SGObjectIdentifer':
                aArg=self.model.getSGEntity_withIdentfier(aArgSpec[1])
            else:
                aArg= aArgSpec
            listOfArgs.append(aArg)
        self.actionsFromBrokerToBeExecuted.append({
            'action_type':'gameAction',
            'gameAction':aGameAction,
             'listOfArgs':listOfArgs
             })

    def processBrokerMsg_executeMethod(self, unserializedMsg):
        """Process incoming execute_method message from broker"""
        msg = unserializedMsg
        objectAndMethod = msg['objectAndMethod']
        classOfObjectToExe = objectAndMethod['class_name']
        idOfObjectToExe = objectAndMethod['id']
        methodNameToExe = objectAndMethod['method']

        aIdentificationDict={}
        aIdentificationDict['name']=classOfObjectToExe
        aIdentificationDict['id']=idOfObjectToExe 
        aSGObject = self.model.getSGObject_withIdentifier(aIdentificationDict)
        
        methodToExe = getattr(aSGObject,methodNameToExe) # this code retrieves the method to be executed and places it in the 'methodToExe' variable. This 'methodToExe' variable can now be used as if it were the method to be executed.
        #retrieve the arguments of the method to be executed
        listOfArgs=[]
        for aArgSpec in msg['listOfArgs']:
            if isinstance(aArgSpec, list) and len(aArgSpec)>0 and aArgSpec[0]== 'SGObjectIdentifer':
                aArg=self.model.getSGObject_withIdentifier(aArgSpec[1])
            else:
                aArg= aArgSpec
            listOfArgs.append(aArg)

        #method execution with these arguments
        methodToExe(*listOfArgs)

        # the code below can be used to defer execution of the method to a thread outside the mqtt read thread.
        # self.actionsFromBrokerToBeExecuted.append({
        #     'action_type':'execute_method',
        #     'boundMethod':methodToExe,     # a bound method is a method already associated with the object that will execute it
        #      'listOfArgs':listOfArgs
        #      })
    
    def onMAJTimer(self):
        """Handle MQTT timer events"""
        self.executeGameActionsAfterBrokerMsg()
    
    def executeGameActionsAfterBrokerMsg(self):
        """Execute game actions received from broker"""
        for item in self.actionsFromBrokerToBeExecuted:
            actionType = item['action_type']
            if actionType == 'gameAction':
                aGameAction = item['gameAction']
                listOfArgs = item['listOfArgs']
                aGameAction.perform_with(*listOfArgs,serverUpdate=False)
            elif actionType == 'nextTurn':
                self.model.timeManager.nextPhase()
            elif actionType == 'backward':
                self.model.backwardAction(serverUpdate=False)
            elif actionType == 'forward':
                self.model.forwardAction(serverUpdate=False)
            else:
                raise ValueError('No other possible choices')

        self.actionsFromBrokerToBeExecuted=[]

    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.haveToBeClose = True
        if self.client:
            # Stop the background loop thread before disconnecting
            self.client.loop_stop()
            self.client.disconnect()
