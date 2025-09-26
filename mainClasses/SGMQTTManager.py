# --- Standard library imports ---
import json
import queue
import threading
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
    
    def __init__(self, model):
        """
        Initialize MQTT Manager
        
        Args:
            model: Reference to the SGModel instance
        """
        self.model = model
        self.client = None
        self.clientId = None
        self.q = None
        self.t1 = None
        self.majTimer = None
        self.haveToBeClose = False
        self.actionsFromBrokerToBeExecuted = []
        
    def setMQTTProtocol(self, majType):
        """
        Set the MQTT protocol configuration

        Args:
            majType (str): "Phase" or "Instantaneous"
        """
        self.clientId = uuid.uuid4().hex
        self.majTimer = QTimer(self.model)
        self.majTimer.timeout.connect(self.onMAJTimer)
        self.majTimer.start(100)
        self.initMQTT()
        self.model.mqttMajType = majType


    def connect_mqtt(self):
        """MQTT Basic function to connect to the broker"""
        def on_log(client, userdata, level, buf):
            print("log: "+buf)

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        def on_disconnect(client, userdata, flags, rc=0):
            print("disconnect result code "+str(rc))

        print("connectMQTT")
        # self.client = mqtt_client.Client(self.model.currentPlayerName)  # Old version
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, self.model.currentPlayerName) # for the new version of paho possible correction
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_log = on_log
        self.q = queue.Queue()
        self.t1 = threading.Thread(target=self.handleClientThread, args=())
        self.t1.start()
        self.model.timer.start(5)
        self.client.connect("localhost", 1883)
        self.client.user_data_set(self)

    def handleClientThread(self):
        """Thread that handle the listen of the client"""
        while True:
            self.client.loop(.1)
            if self.haveToBeClose == True:
                break

    def initMQTT(self):
        """Init the MQTT client"""
        def on_message(aClient, userdata, msg):
            self.q.put(msg.payload)
            print("message received " + msg.topic)
            message = self.q.get()
            msg_decoded = message.decode("utf-8")
            if msg.topic in ['gameAction_performed','nextTurn','execute_method']:
                unserializedMsg= json.loads(msg_decoded)
                if unserializedMsg['clientId']== self.clientId:
                    print("Own update, no action required.") 
                else:
                    if msg.topic == 'gameAction_performed':
                        self.processBrokerMsg_gameAction_performed(unserializedMsg)
                    elif msg.topic == 'execute_method':
                        self.processBrokerMsg_executeMethod(unserializedMsg)
                    elif msg.topic == 'nextTurn':
                        self.processBrokerMsg_nextTrun(unserializedMsg)
                return
            msg_list = eval(msg_decoded)   

        self.connect_mqtt()

        self.client.subscribe("gameAction_performed")
        self.client.subscribe("nextTurn")
        self.client.subscribe("execute_method")
        self.client.on_message = on_message
        
    def buildNextTurnMsgAndPublishToBroker(self):
        """Build and publish next turn message to MQTT broker"""
        msgTopic = 'nextTurn'
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
        
        msgTopic = args[0] # The first arg is the topic of the msg
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
            self.client.disconnect()
