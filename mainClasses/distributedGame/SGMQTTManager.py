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
    GAME_TOPICS = ['gameAction_performed', 'nextTurn', 'execute_method']
    
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
                unserializedMsg= json.loads(msg_decoded)
                if unserializedMsg['clientId']== self.clientId:
                    # Own update, no action required
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
                return
            # Not a game topic - ignore silently (could be session topic or other message type)
            # Session topics are handled by SGDistributedSessionManager
            # Other unknown topics are ignored   

        self.connect_mqtt()

        # Subscribe to game topics using centralized method
        game_topics = self.getGameTopics(self.session_id)
        for topic in game_topics:
            self.client.subscribe(topic)
        
        self.client.on_message = on_message

    def connect_mqtt(self):
        """MQTT Basic function to connect to the broker"""
        def on_log(client, userdata, level, buf):
            # Logs MQTT de bas niveau désactivés pour réduire la verbosité
            pass

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
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
            else: raise ValueError('No other possible choices')

        self.actionsFromBrokerToBeExecuted=[]

    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.haveToBeClose = True
        if self.client:
            # Stop the background loop thread before disconnecting
            self.client.loop_stop()
            self.client.disconnect()
