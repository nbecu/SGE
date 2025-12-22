# --- Standard library imports ---
import json
import queue
import re
import sys
import threading
import uuid
from email.policy import default
from logging.config import listen
from pathlib import Path

# Ensure the current file's directory is in sys.path for local imports
sys.path.insert(0, str(Path(__file__).parent))

# --- Third-party imports ---
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import *
from PyQt5.QtWidgets import QAction, QMenu, QMainWindow, QMessageBox, QApplication, QActionGroup, QFileDialog, QInputDialog
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets
from paho.mqtt import client as mqtt_client
from pyrsistent import s
from screeninfo import get_monitors

# --- Project imports ---
from mainClasses.SGAgent import *
from mainClasses.SGCell import *
from mainClasses.SGTile import *
from mainClasses.SGControlPanel import *
from mainClasses.SGDashBoard import *
from mainClasses.SGDataRecorder import *
from mainClasses.SGEndGameRule import *
from mainClasses.SGEntity import *
from mainClasses.SGEntityView import *
from mainClasses.SGEntityType import *
from mainClasses.SGGrid import SGGrid
from mainClasses.SGGraphController import SGGraphController
from mainClasses.SGGraphLinear import SGGraphLinear
from mainClasses.SGGraphCircular import SGGraphCircular
from mainClasses.SGGraphWindow import SGGraphWindow
from mainClasses.SGLegend import *
from mainClasses.SGModelAction import *
from mainClasses.SGPlayer import *
from mainClasses.SGAdminPlayer import *
from mainClasses.SGProgressGauge import *
from mainClasses.SGSimulationVariable import *
from mainClasses.SGTestGetData import SGTestGetData
from mainClasses.SGTextBox import *
from mainClasses.SGLabel import *
from mainClasses.SGButton import *
from mainClasses.SGTimeLabel import *
from mainClasses.SGTimeManager import *
from mainClasses.SGTimePhase import *
from mainClasses.SGUserSelector import *
from mainClasses.SGVoid import *
from mainClasses.layout.SGGridLayout import *
from mainClasses.layout.SGHorizontalLayout import *
from mainClasses.layout.SGVerticalLayout import *
from mainClasses.layout.SGLayoutConfigManager import SGLayoutConfigManager
from mainClasses.theme.SGThemeConfigManagerDialog import SGThemeConfigManagerDialog
from mainClasses.theme.SGThemeConfigManager import SGThemeConfigManager
from mainClasses.theme.SGThemeEditTableDialog import SGThemeEditTableDialog
from mainClasses.gameAction.SGActivate import *
from mainClasses.gameAction.SGCreate import *
from mainClasses.gameAction.SGDelete import *
from mainClasses.gameAction.SGModify import *
from mainClasses.gameAction.SGMove import *
from mainClasses.SGEventHandlerGuide import *
from mainClasses.SGMQTTManager import SGMQTTManager
from mainClasses.SGDistributedGameConfig import SGDistributedGameConfig
from mainClasses.SGDistributedSessionManager import SGDistributedSessionManager
from mainClasses.SGDistributedGameDialog import SGDistributedGameDialog
from mainClasses.SGConnectionStatusWidget import SGConnectionStatusWidget



# By default, use a relative path based on the project structure
path_icon = str(Path(__file__).parent.parent / 'icon')
# Alternative method: uncomment the following line, and use an absolute path
# Example of absolute path: 
# path_icon = '/Users/.../Documents/.../SGE/icon/'

# Mother class of all the SGE System
class SGModel(QMainWindow, SGEventHandlerGuide):

    JsonManagedDataTypes=(dict,list,tuple,str,int,float,bool)

    def __init__(self, width=1800, height=900, typeOfLayout="enhanced_grid", nb_columns=3, y=3, name=None, windowTitle=None, createAdminPlayer=True,windowBackgroundColor=None):
        """
        Declaration of a new model

        Args:
            width (int): width of the main window in pixels (default:1800)
            height (int): height of the main window in pixels (default:900)
            typeOfLayout ("vertical", "horizontal", "grid" or "enhanced_grid"): the type of layout used to position the different graphic elements of the simulation (default:"grid")
            nb_columns (int, optional): used for grid and enhanced_grid layouts. defines the number of columns (default:3)
            y (int, optional): used only for grid layout. defines the number layout grid height (default:3)
            name (str, optional): the name of the model. (default:"Simulation")
            windowTitle (str, optional): the title of the main window of the simulation (default:"myGame")
            createAdminPlayer (boolean, optional): Automatically create a Admin player (default:True), that can perform all possible gameActions
            windowBackgroundColor (QColor or Qt.GlobalColor, optional): The background color of the main window (default:None)
        """
        super().__init__()
        # Definition the size of the window ( temporary here)
        primary_monitor = next((m for m in get_monitors() if m.is_primary), None)

        if primary_monitor:
           width_screen = primary_monitor.width
           height_screen = primary_monitor.height
        
        else: raise ValueError("Screen problem")

        screensize = width_screen, height_screen
        self.setGeometry(
            int((screensize[0]/2)-width/2), int((screensize[1]/2)-height/2), width, height)
        # Init of variable of the Model
        self.name = name
        # Unique identifier for this application instance
        self.session_id = str(uuid.uuid4())
        # Definition of the title of the window
        self.windowTitle_prefix = (windowTitle or self.name or ' ') # if windowTitle  is None, the name of the model is used as prefix for window title
        self.setWindowTitle(self.windowTitle_prefix)
        self.windowBackgroundColor = windowBackgroundColor
        # Option to display time (round and phase) in window title
        self.isTimeDisplayedInWindowTitle = False
        # Option to show icons in context menu (default: True)
        self.showIconsInContextMenu = True
        
        # We allow the drag in this widget
        self.setAcceptDrops(True)
        # Definition of variable
        # Definition for all gameSpaces
        self.gameSpaces = {}
        self.TextBoxes = []   # Why textBoxes are not in gameSpaces ?
        # list of graphs
        self.openedGraphs = []
        # Definition of the AgentDef and CellDef
        self.agentTypes = {}
        self.cellTypes = {}
        self.tileTypes = {}
        # Definition of simulation variables
        self.simulationVariables = []
        # definition of layouts and associated parameters
        self.typeOfLayout = typeOfLayout
        if (typeOfLayout == "vertical"):
            self.layoutOfModel = SGVerticalLayout()
        elif (typeOfLayout == "horizontal"):
            self.layoutOfModel = SGHorizontalLayout()
        elif (typeOfLayout == "enhanced_grid"):
            from mainClasses.layout.SGEnhancedGridLayout import SGEnhancedGridLayout
            self.layoutOfModel = SGEnhancedGridLayout(num_columns=nb_columns)
            self.layoutOfModel.model = self  # Set model reference
        else:
            self.layoutOfModel = SGGridLayout(nb_columns, y)
        self.isMoveToCoordsUsed = False
        # To limit the number of zoom out of players
        self.numberOfZoom = 2
        # To keep in memory all the povs already displayed in the menu
        self.listOfPovsForMenu = []
        # List of players (must be initialized before Admin creation)
        self.players = {}
        # Automatically create Admin as a super player (optional)
        if createAdminPlayer:
            self.players["Admin"] = SGAdminPlayer(self)
            self.users = ["Admin"]
            self.shouldDisplayAdminControlPanel = False
        else:
            self.users = []
        # self.users = ["Admin"]
        
        # Auto-save gameAction logs on application close (None = disabled, string = format)
        self.autoSaveGameActionLogs = None

        # To handle the flow of time in the game
        self.timeManager = SGTimeManager(self)
        # List of players
        # self.players = {}  # Moved above
        self.currentPlayerName = None

        self.userSelector = None
        self.myTimeLabel = None

        self.listOfSubChannel = []
        self.listOfMajs = []
        self.processedMAJ = set()
        self.timer = QTimer()
        self.haveToBeClose = False
        self.mqttMajType=None

        self.dataRecorder=SGDataRecorder(self)

        # Initialize MQTT Manager
        self.mqttManager = SGMQTTManager(self)

        # Distributed game mode attributes
        self.distributedConfig = None  # SGDistributedGameConfig or None
        self.distributedSessionManager = None  # SGDistributedSessionManager or None
        self.connectionStatusWidget = None  # SGConnectionStatusWidget or None

        # Initialize runtime themes dictionary for custom themes
        self._runtime_themes = {}
        # Load custom themes from persistent storage
        self._loadCustomThemes()

        # Store pending theme configuration to load after initBeforeShowing
        self._pending_theme_config = None
        # Store pending layout configuration to apply after initBeforeShowing
        self._pending_layout_config = None

        self.initUI()

        self.initModelActions()
        # self.listData = []

    # ============================================================================
    # DEVELOPER METHODS
    # ============================================================================
    def __DEVELOPER_METHODS__(self):
        pass
    
    # ============================================================================
    # INITIALIZATION METHODS
    # ============================================================================
    def __INITIALIZATION_METHODS__(self):
        pass

    def initModelActions(self):
        self.id_modelActions = 0

    def initUI(self):
        # Definition of the view through the a widget
        self.window = QtWidgets.QWidget()
        self.layout = QtWidgets.QGridLayout()
        self.setCentralWidget(self.window)
        self.window.setLayout(self.layout)
        # Set background color for main window
        # Use QPalette instead of stylesheet to avoid cascading to child widgets
        if self.windowBackgroundColor:
            # Normalize color to QColor
            from PyQt5.QtGui import QColor, QPalette
            if isinstance(self.windowBackgroundColor, QColor):
                bg_color = self.windowBackgroundColor
            elif isinstance(self.windowBackgroundColor, str):
                bg_color = QColor(self.windowBackgroundColor)
                if not bg_color.isValid():
                    bg_color = QColor("#ffffff")
            else:
                # Qt.GlobalColor or other - convert to QColor
                try:
                    bg_color = QColor(self.windowBackgroundColor)
                    if not bg_color.isValid():
                        bg_color = QColor("#ffffff")
                except Exception:
                    bg_color = QColor("#ffffff")  # Fallback to white
            
            # Use QPalette to set background without affecting child widgets
            palette = self.window.palette()
            palette.setColor(QPalette.Window, bg_color)
            self.window.setPalette(palette)
            self.window.setAutoFillBackground(True)
        # Definition of the toolbar via a menu and the ac
        self.symbologyMenu = None  # init in case no menu is created
        self.createMenu()
        self.nameOfPov = "default"
        cursorPositionAction = QAction(" &" + "Cursor Position", self, checkable=True)
        self.settingsMenu.addAction(cursorPositionAction)
        cursorPositionAction.triggered.connect(lambda: self.showCursorCoords())
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(10, 10, 350, 30)
        self.label.move(300, 0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.maj_coordonnees)
        self.isLabelVisible = False
        # Add GameAction Logs Export submenu
        self.createGameActionLogsExportMenu()

    def initBeforeShowing(self):
        """Initialize components that need to be ready before the window is shown"""
        # Initialize tooltip menu with all entity definitions
        self.updateTooltipMenu()

        # Reorganize Enhanced Grid Layout orders to eliminate gaps, then apply the layout
        # self.reorganizeEnhancedGridLayoutOrders()
        self.applyAutomaticLayout()


        # Show admin control panel if needed
        if self.shouldDisplayAdminControlPanel:
            self.show_adminControlPanel()

        # Complete distributed game setup if in distributed mode
        # Called here (before showing window) so player selection happens before window appears
        if self.isDistributed():
            self.completeDistributedGameSetup()

        # Set up dashboards
        self.setDashboards()
        
        # Load pending theme configuration if one was memorized by applyThemeConfig()
        if self._pending_theme_config:
            config_name = self._pending_theme_config
            self._pending_theme_config = None  # Clear to avoid reloading
            manager = SGThemeConfigManager(self)
            manager.loadConfig(config_name, suppress_dialogs=True)
        
        # Apply pending layout configuration if one was memorized by applyLayoutConfig()
        if self._pending_layout_config:
            config_name = self._pending_layout_config
            self._pending_layout_config = None  # Clear to avoid reapplying
            config_manager = SGLayoutConfigManager(self)
            config_manager.loadConfig(config_name)

    def initAfterOpening(self):
        if self.currentPlayerName is None:
            possibleUsers = self.getUsers_withControlPanel()
            if possibleUsers != []:
                self.setCurrentPlayer(possibleUsers[0])
            elif possibleUsers == []:
                self.setCurrentPlayer('Admin')
        # todo Obsolete - to delete
        #  if not self.hasDefinedPositionGameSpace() : QTimer.singleShot(100, self.adjustGamespacesPosition)

        # Position all agents after grid layout is applied and window is shown
        # Use QApplication.processEvents() to ensure layouts are processed before positioning
        QApplication.processEvents()
        self.positionAllAgents()
        self.positionAllTiles()

    def launch(self):
        """
        Launch the game.
        Automatically uses MQTT if distributed mode is enabled.
        """
        # Check if distributed mode is enabled
        if self.isDistributed():
            # Automatically launch with MQTT (reuses existing connection)
            self.launch_withMQTT(
                self.distributedConfig.mqtt_update_type,
                broker_host=self.distributedConfig.broker_host,
                broker_port=self.distributedConfig.broker_port,
                session_id=self.distributedConfig.session_id
            )
        else:
            # Normal local launch
            self.initBeforeShowing()
            self.show()
            self.initAfterOpening()

    def launch_withMQTT(self, majType, broker_host="localhost", broker_port=1883, session_id=None):
        """
        Set the mqtt protocol, then launch the game.
        
        IMPORTANT: In distributed mode, MQTT connection is already established in enableDistributedGame().
        This method should reuse the existing connection if possible, or establish a new one if needed.
        
        Args:
            majType (str): "Phase" or "Instantaneous"
            broker_host (str): MQTT broker host (default: "localhost")
            broker_port (int): MQTT broker port (default: 1883)
            session_id (str, optional): Session ID for topic isolation. 
                                       If None and distributedConfig exists, uses its session_id.
        """
        # Use session_id from distributedConfig if available
        if session_id is None and self.isDistributed():
            session_id = self.distributedConfig.session_id
        
        # CRITICAL: Check if MQTT is already initialized (from enableDistributedGame dialog)
        if (self.mqttManager.client and 
            self.mqttManager.client.is_connected() and
            self.mqttManager.session_id == session_id):
            # Reuse existing connection - just update majType if needed
            self.mqttMajType = majType
        else:
            # Initialize new connection (only if not already connected)
            self.mqttManager.setMQTTProtocol(majType, broker_host, broker_port, session_id=session_id)
        
        # Launch the game (don't call self.launch() to avoid recursion)
        self.initBeforeShowing()
        self.show()
        self.initAfterOpening()

    def show_adminControlPanel(self): 
        """
        Private method to show the Admin Control Panel
        """
        adminPlayer = self.getAdminPlayer()
        adminPlayer.createAllGameActions()
        if adminPlayer.controlPanel is None:
            adminPlayer.newControlPanel("Admin")
        else:
            adminPlayer.controlPanel.show()

    def setDashboards(self):
        dashboards = self.getGameSpaceByClass(SGDashBoard)
        for aDashBoard in dashboards:
            aDashBoard.showIndicators()

    def positionAllAgents(self):
        """Position all agents after grid layout is applied"""
        for agent_type in self.getAgentTypes():
            for agent in agent_type.entities:
                if hasattr(agent, 'view') and agent.view:
                    # Show the agent view first
                    agent.view.show()
                    agent.view.raise_()  # Bring to front
                    # Then position it
                    agent.view.getPositionInEntity()
                    # Force update to ensure positioning is applied
                    agent.view.update()
    
    def positionAllTiles(self):
        """Position all tiles after grid layout is applied, respecting layer order"""
        # Collect all tiles with their views
        all_tiles = []
        for tile_type in self.getTileTypes():
            for tile in tile_type.entities:
                if hasattr(tile, 'view') and tile.view:
                    all_tiles.append(tile)
        
        # Sort tiles by layer (lower layers first, higher layers last)
        # This ensures tiles with higher layers are rendered on top
        all_tiles.sort(key=lambda t: t.layer if hasattr(t, 'layer') else 0)
        
        # Position and show tiles in layer order
        for tile in all_tiles:
            if hasattr(tile, 'view') and tile.view:
                # Show the tile view first
                tile.view.show()
                # Position it (tiles should be below agents)
                tile.view.getPositionInCell()
                # Ensure tiles are rendered in correct z-order
                # Lower tiles (lower layer) should be rendered first
                # Higher tiles (higher layer) should be on top
                tile.view.lower()  # Start by lowering all tiles
        
        # Now raise tiles in order of their layer (higher layers on top)
        for tile in all_tiles:
            if hasattr(tile, 'view') and tile.view:
                tile.view.raise_()  # Raise tiles in layer order
                # Force update to ensure positioning is applied
                tile.view.update()
    
    def getTileTypes(self):
        """Get all tile types"""
        return list(self.tileTypes.values())

    # ============================================================================
    # UI MANAGEMENT METHODS
    # ============================================================================
    def __UI_MANAGEMENT_METHODS__(self):
        pass

    def showCursorCoords(self):
        self.isLabelVisible = not self.isLabelVisible
        if self.isLabelVisible:
            self.label.show()
            self.timer.start(100)
        else:
            self.label.hide()
            self.timer.stop()

    def closeEvent(self, event):
        self.haveToBeClose = True
        self.getTextBoxHistory(self.TextBoxes)
        
        # Check for auto-save of gameAction logs
        if self.autoSaveGameActionLogs and self.getAllGameActions():
            # Handle both old format (string) and new format (dict)
            if isinstance(self.autoSaveGameActionLogs, dict):
                format_type = self.autoSaveGameActionLogs["format"]
                save_path = self.autoSaveGameActionLogs["save_path"]
            else:
                # Backward compatibility with old string format
                format_type = self.autoSaveGameActionLogs
                save_path = None
            
            reply = QMessageBox.question(
                self, 
                'Save GameAction Logs',
                'GameActions have been performed. Do you want to save the logs before closing?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                try:
                    if save_path:
                        # Use specified path
                        import os
                        timestamp = self._getCurrentTimestamp()
                        filename = os.path.join(save_path, f"gameAction_logs_{timestamp}.{format_type}")
                        filename = self.exportGameActionLogs(filename=filename, format=format_type)
                    else:
                        # Let user choose path via file dialog
                        timestamp = self._getCurrentTimestamp()
                        default_filename = f"gameAction_logs_{timestamp}.{format_type}"
                        filename, _ = QFileDialog.getSaveFileName(
                            self,
                            'Save GameAction Logs',
                            default_filename,
                            f"{format_type.upper()} files (*.{format_type})"
                        )
                        if filename:
                            filename = self.exportGameActionLogs(filename=filename, format=format_type)
                        else:
                            return  # User cancelled
                    
                    QMessageBox.information(self, 'Success', f'GameAction logs saved to: {filename}')
                except Exception as e:
                    QMessageBox.warning(self, 'Error', f'Failed to save logs: {str(e)}')
        
        # Disconnect from distributed session if in distributed mode
        if hasattr(self, 'distributedSessionManager') and self.distributedSessionManager:
            self.distributedSessionManager.disconnect()
        
        if hasattr(self, 'mqttManager') and self.mqttManager:
            self.mqttManager.disconnect()
        self.close()

    # Function to handle the drag of widget
    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        if isinstance(e.source(), (SGEntity, SGEntityView)):
            # msg_box = QMessageBox(self)
            # msg_box.setIcon(QMessageBox.Information)
            # msg_box.setWindowTitle("Warning Message")
            # # Get the agent model from the view
            # agent_model = e.source().agent_model if hasattr(e.source(), 'agent_model') else e.source()
            # msg_box.setText("A " + agent_model.type.name +" cannot be moved here")
            # msg_box.setStandardButtons(QMessageBox.Ok)
            # msg_box.setDefaultButton(QMessageBox.Ok)
            # msg_box.exec_()
            return
        position = e.pos()
        # Get the agent model from the view
        agent_model = e.source().agent_model if hasattr(e.source(), 'agent_model') else e.source()

        # Get the agent size - handle both model and view cases
        if hasattr(agent_model, 'size') and not callable(agent_model.size):
            # agent_model is a model with size attribute
            agent_size = agent_model.size
        elif hasattr(agent_model, 'size') and callable(agent_model.size):
            # agent_model is a view with size() method
            agent_size = agent_model.size().width()  # Use width as size
        else:
            # Fallback to default size
            agent_size = 30

        position.setX(position.x() - int(agent_size / 2))
        position.setY(position.y() - int(agent_size / 2))
        agent_model.move(position)
        e.setDropAction(Qt.MoveAction)
        e.accept()


    # Handle window title
    def updateWindowTitle(self):
        # Update window title with the number of the round and number of the phase
        if self.isTimeDisplayedInWindowTitle:
            if self.timeManager.numberOfPhases() == 1:
                title = f"{self.windowTitle_prefix} {' - ' if self.windowTitle_prefix != ' ' else ''} Round {self.roundNumber()}"
            else:
                title = f"{self.windowTitle_prefix} {' - ' if self.windowTitle_prefix != ' ' else ''} Round {self.roundNumber()}, Phase {self.phaseNumber()}"
            self.setWindowTitle(title)

    # Create the menu of the menu
    def createMenu(self):
        # Add the 'play' button
        if sys.platform == "darwin":
            # For Mac compatibility: add the play button in a submenu
            self.startGame = self.menuBar().addMenu(QIcon(f"{path_icon}/play.png"), " &Step")
            startGame = QAction(" &Next step", self)
            self.startGame.addAction(startGame)
            startGame.triggered.connect(self.nextTurn)
        else:
            # for all other platforms than Mac, direct action on play icon
            aAction = QAction(QIcon(f"{path_icon}/play.png"), " &play", self)
            aAction.triggered.connect(self.nextTurn)
            self.menuBar().addAction(aAction)

        self.menuBar().addSeparator()
        aAction = QAction(QIcon(f"{path_icon}/zoomPlus.png"), " &zoomPlus", self)
        aAction.triggered.connect(self.zoomPlusModel)
        self.menuBar().addAction(aAction)
        aAction = QAction(QIcon(f"{path_icon}/zoomLess.png"), " &zoomLess", self)
        aAction.triggered.connect(self.zoomLessModel)
        self.menuBar().addAction(aAction)
        aAction = QAction(QIcon(f"{path_icon}/zoomToFit.png"), " &zoomToFit", self)
        aAction.triggered.connect(self.zoomFitModel)
        self.menuBar().addAction(aAction)
        self.menuBar().addSeparator()
        self.symbologyMenu = self.menuBar().addMenu(QIcon(f"{path_icon}/symbology.png"), "&Symbology")
        self.symbologiesInSubmenus = {}
        self.keyword_borderSubmenu = ' border'
        self.createGraphMenu()

        self.settingsMenu = self.menuBar().addMenu(QIcon(f"{path_icon}/settings.png"), " &Settings")
        # Create Enhanced Grid Layout submenu and Theme Manager entries
        self.createEnhancedGridLayoutMenu()
        self.createThemeManagerMenu()
        
    # ============================================================================
    # GAME ACTION LOGS EXPORT METHODS
    # ============================================================================
    
    def _getGameActionLogsData(self):
        """
        Collect all gameAction logs data from all players with detailed action information
        
        Returns:
            dict: Complete gameAction logs data with metadata
        """
        # Use existing method to get players with gameActions (excludes inactive Admin)
        player_names = self.getUsers_withGameActions()
        
        logs_data = {
            "metadata": {
                "model_name": getattr(self, 'name', 'Unnamed Model'),
                "export_timestamp": self._getCurrentTimestamp(),
                "current_round": self.timeManager.currentRoundNumber,
                "current_phase": self.timeManager.currentPhaseNumber,
                "total_players": len(player_names),
                "player_names": player_names
            },
            "players": {}
        }
        
        # Collect data from each player
        for player_name, player in self.players.items():
            # Skip Admin player if no admin control panel is displayed (no gameActions)
            if player_name == "Admin" and not self.shouldDisplayAdminControlPanel:
                continue
                
            player_stats = player.getStatsOfGameActions()
            logs_data["players"][player_name] = {
                "player_name": player_name,
                "total_gameActions": len(player.gameActions),
                "gameActions": [
                    self._getDetailedActionInfo(action)
                    for action in player.gameActions
                ],
                "stats_by_round_phase": player_stats
            }
        
        return logs_data
    
    def _getDetailedActionInfo(self, action):
        """
        Get detailed information about a gameAction using the action's own methods
        
        Args:
            action: GameAction instance
            
        Returns:
            dict: Detailed action information
        """
        # The action knows itself - encapsulation respect
        return action.getExportInfo()
    
    
    def _exportGameActionLogsToJSON(self, logs_data, filename):
        """
        Export gameAction logs to JSON file
        
        Args:
            logs_data (dict): GameAction logs data
            filename (str): Output filename
            
        Returns:
            str: Path to exported file
        """
        try:
            from mainClasses.SGExtensions import serialize_any_object
            
            # Serialize data safely
            safe_logs_data = serialize_any_object(logs_data)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(safe_logs_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"GameAction logs exported to {filename}")
            return filename
            
        except Exception as e:
            raise ValueError(f"Failed to export JSON file: {e}")
    
    def _exportGameActionLogsToCSV(self, logs_data, filename):
        """
        Export gameAction logs to CSV file with detailed information
        
        Args:
            logs_data (dict): GameAction logs data
            filename (str): Output filename
            
        Returns:
            str: Path to exported file
        """
        try:
            import csv
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header with Session_ID first as requested
                writer.writerow([
                    'Session_ID', 'ID_Action', 'Timestamp', 'Round', 'Phase', 'Player', 'Action_ID', 'Action_Name', 'Max_Uses', 'Usage_Count', 'Action_Type', 
                    'Target_Entity_Category', 'Target_Entity_Name', 'Attribute', 'Value', 'Activated_Method',
                    'Action_Details', 'Target_Entity_ID', 'Target_Entity_Coordinates', 'Destination_Entity_ID', 'Destination_Entity_Coordinates',
                    'Result_Action', 'Result_Feedback'
                ])
                
                # Collect all history entries with their metadata for chronological sorting
                all_history_entries = []
                
                for player_name, player_data in logs_data["players"].items():
                    for action_data in player_data["gameActions"]:
                        action_id = action_data["action_id"]
                        action_type = action_data["action_type"]
                        action_name = action_data["action_name"]
                        
                        # Extract flattened fields directly from action_data
                        target_entity_type = action_data.get("target_entity_type", "N/A")
                        target_entity_category = action_data.get("target_entity_category", "N/A")
                        target_entity_name = action_data.get("target_entity_name", "N/A")
                        
                        # Extract action details fields
                        conditions_count = action_data.get("conditions_count", "N/A")
                        feedbacks_count = action_data.get("feedbacks_count", "N/A")
                        contextual_menu = action_data.get("contextual_menu", "N/A")
                        on_controller = action_data.get("on_controller", "N/A")
                        
                        # Extract usage info fields
                        total_uses = action_data.get("total_uses", "N/A")
                        max_uses = action_data.get("max_uses", "N/A")
                        
                        # Collect each history entry with its metadata
                        for history_entry in action_data["history"]:
                            all_history_entries.append({
                                'history_entry': history_entry,
                                'player_name': player_name,
                                'action_id': action_id,
                                'action_type': action_type,
                                'action_name': action_name,
                                'target_entity_type': target_entity_type,
                                'target_entity_category': target_entity_category,
                                'target_entity_name': target_entity_name,
                                'conditions_count': conditions_count,
                                'feedbacks_count': feedbacks_count,
                                'contextual_menu': contextual_menu,
                                'on_controller': on_controller,
                                'total_uses': total_uses,
                                'max_uses': max_uses
                            })
                
                # Sort all entries by ID_Action (chronological order)
                all_history_entries.sort(key=lambda x: x['history_entry'].get('id_action', 0) if isinstance(x['history_entry'], dict) else (x['history_entry'][7] if len(x['history_entry']) > 7 and x['history_entry'][7] != "N/A" else 0))
                
                # Write data rows in chronological order
                for entry_data in all_history_entries:
                    history_entry = entry_data['history_entry']
                    player_name = entry_data['player_name']
                    action_id = entry_data['action_id']
                    action_type = entry_data['action_type']
                    action_name = entry_data['action_name']
                    
                    # Extract flattened fields
                    target_entity_type = entry_data['target_entity_type']
                    target_entity_category = entry_data['target_entity_category']
                    target_entity_name = entry_data['target_entity_name']
                    conditions_count = entry_data['conditions_count']
                    feedbacks_count = entry_data['feedbacks_count']
                    contextual_menu = entry_data['contextual_menu']
                    on_controller = entry_data['on_controller']
                    total_uses = entry_data['total_uses']
                    max_uses = entry_data['max_uses']
                    
                    # Handle both dictionary format (new) and list format (old)
                    if isinstance(history_entry, dict):
                        # New dictionary format from getFormattedHistory()
                        round_num = history_entry.get('round', 0)
                        phase_num = history_entry.get('phase', 0)
                        usage_count = history_entry.get('usage_count', 0)
                        target_entity = history_entry.get('target_entity')
                        res_action = history_entry.get('result_action')
                        res_feedback = history_entry.get('result_feedback')
                        timestamp = history_entry.get('timestamp', 'N/A')
                        id_action = history_entry.get('id_action', 'N/A')
                        session_id = history_entry.get('session_id', 'N/A')
                        destination_entity = history_entry.get('destination_entity')
                    else:
                        # Old list format (backward compatibility)
                        if len(history_entry) == 10:  # Action Move avec destination + nouvelles colonnes
                            round_num, phase_num, usage_count, target_entity, res_action, res_feedback, timestamp, id_action, session_id, destination_entity = history_entry
                        elif len(history_entry) == 9:  # Autres actions avec nouvelles colonnes
                            round_num, phase_num, usage_count, target_entity, res_action, res_feedback, timestamp, id_action, session_id = history_entry
                            destination_entity = None
                        else:  # Old format (backward compatibility)
                            round_num, phase_num, usage_count, target_entity, res_action, res_feedback = history_entry
                            timestamp = "N/A"
                            id_action = "N/A"
                            session_id = "N/A"
                            destination_entity = None
                    
                    # Safe serialization of entities
                    from mainClasses.SGExtensions import serialize_any_object
                    safe_target_entity = target_entity.getObjectIdentiferForExport()
                    safe_res_action = serialize_any_object(res_action) if res_action is not None else "None"
                    safe_res_feedback = serialize_any_object(res_feedback) if res_feedback is not None else "None"
                    
                    # Get coordinates of target entity
                    target_coordinates = "N/A"
                    if hasattr(target_entity, 'getCoords'):
                        try:
                            coords = target_entity.getCoords()
                            target_coordinates = f"({coords[0]}, {coords[1]})" if coords else "N/A"
                        except:
                            target_coordinates = "N/A"
                    elif hasattr(target_entity, 'xCoord') and hasattr(target_entity, 'yCoord'):
                        target_coordinates = f"({target_entity.xCoord}, {target_entity.yCoord})"
                    
                    # Get destination entity information (for Move actions)
                    safe_destination_entity = "N/A"
                    destination_coordinates = "N/A"
                    if destination_entity is not None:
                        safe_destination_entity = destination_entity.getObjectIdentiferForExport()
                        if hasattr(destination_entity, 'getCoords'):
                            try:
                                coords = destination_entity.getCoords()
                                destination_coordinates = f"({coords[0]}, {coords[1]})" if coords else "N/A"
                            except:
                                destination_coordinates = "N/A"
                        elif hasattr(destination_entity, 'xCoord') and hasattr(destination_entity, 'yCoord'):
                            destination_coordinates = f"({destination_entity.xCoord}, {destination_entity.yCoord})"
                    
                    # Find original action to use its methods
                    action = None
                    for player in self.players.values():
                        for act in player.gameActions:
                            if act.id == action_id:
                                action = act
                                break
                        if action:
                            break
                    
                    # Use action methods for formatting
                    if action:
                        action_details_str = action.formatActionDetailsForCSV()
                        # Extract attributes directly from action
                        if hasattr(action, 'att') and hasattr(action, 'value'):
                            attribute_info = {
                                "attribute": str(action.att),
                                "value": str(action.value)
                            }
                        elif hasattr(action, 'dictAttributs') and action.dictAttributs:
                            # For Create actions
                            first_attr = list(action.dictAttributs.keys())[0]
                            attribute_info = {
                                "attribute": str(first_attr),
                                "value": str(action.dictAttributs[first_attr])
                            }
                        else:
                            attribute_info = {"attribute": "N/A", "value": "N/A"}
                    else:
                        action_details_str = "No details"
                        attribute_info = {"attribute": "N/A", "value": "N/A"}
                    
                    # Extract activated method for Activate actions
                    activated_method = "N/A"
                    if action_type == "Activate" and action:
                        activated_method = getattr(action.method, '__name__', str(action.method)) if callable(action.method) else str(action.method)
                    
                    writer.writerow([
                        session_id,
                        id_action,
                        timestamp,
                        round_num,
                        phase_num,
                        player_name,
                        action_id,
                        action_name,
                        max_uses,
                        usage_count,
                        action_type,
                        target_entity_category,
                        target_entity_name,
                        attribute_info["attribute"],
                        attribute_info["value"],
                        activated_method,
                        action_details_str,
                        safe_target_entity,
                        target_coordinates,
                        safe_destination_entity,
                        destination_coordinates,
                        safe_res_action,
                        safe_res_feedback
                    ])
            
            print(f"GameAction logs exported to {filename}")
            return filename
            
        except Exception as e:
            raise ValueError(f"Failed to export CSV file: {e}")
    
    
    def _getCurrentTimestamp(self):
        """
        Get current timestamp for filename generation
        
        Returns:
            str: Formatted timestamp string
        """
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
        

    def createGameActionLogsExportMenu(self):
        """Create GameAction Logs Export submenu in Settings menu"""
        self.gameActionLogsMenu = self.settingsMenu.addMenu("&Export GameAction Logs")
        
        # Export to CSV action
        exportCsvAction = QAction("&Export to CSV...", self)
        exportCsvAction.triggered.connect(self.openExportGameActionLogsDialog)
        exportCsvAction.setData("csv")  # Store format in action data
        self.gameActionLogsMenu.addAction(exportCsvAction)
        # Export to JSON action
        exportJsonAction = QAction("&Export to JSON...", self)
        exportJsonAction.triggered.connect(self.openExportGameActionLogsDialog)
        exportJsonAction.setData("json")  # Store format in action data
        self.gameActionLogsMenu.addAction(exportJsonAction)
        
    def openExportGameActionLogsDialog(self):
        """Open dialog to export GameAction logs"""
        # Get the triggered action to determine format
        action = self.sender()
        format_type = action.data()
        
        # Generate default filename
        timestamp = self._getCurrentTimestamp()
        default_filename = f"gameAction_logs_{timestamp}.{format_type}"
        
        # Open file dialog
        from PyQt5.QtWidgets import QFileDialog
        
        if format_type == "json":
            file_filter = "JSON Files (*.json);;All Files (*)"
        else:  # csv
            file_filter = "CSV Files (*.csv);;All Files (*)"
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            f"Export GameAction Logs to {format_type.upper()}",
            default_filename,
            file_filter
        )
        
        if filename:
            try:
                exported_file = self.exportGameActionLogs(filename, format_type)
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"GameAction logs exported successfully to:\n{exported_file}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to export GameAction logs:\n{str(e)}"
                )

    def createTooltipMenu(self):
        """Create tooltip selection submenu in Settings menu"""
        self.tooltipMenu = self.settingsMenu.addMenu("&Entity Tooltips")

        # Create tooltip options
        tooltipOptions = [
            ("None", "none", "No tooltips displayed"),
            ("Coordinates", "coords", "Show entity coordinates (x, y)"),
            ("Entity ID", "id", "Show entity ID")
        ]

        # Get all entity definitions
        entityTypes = self.getEntityTypes()

        # Create submenus for each entity definition
        for aType in entityTypes:
            # Create submenu for this entity type
            entityMenu = self.tooltipMenu.addMenu(f"&{aType.name}")

            # Create action group for exclusive selection within this entity type
            actionGroup = QActionGroup(self)
            actionGroup.setExclusive(True)

            # Store reference to action group for this entity
            if not hasattr(self, 'tooltipActionGroups'):
                self.tooltipActionGroups = {}
            self.tooltipActionGroups[aType.name] = actionGroup

            # Create actions for each tooltip option
            for label, tooltipType, description in tooltipOptions:
                action = QAction(f"&{label}", self)
                action.setCheckable(True)
                action.setStatusTip(f"{description} for {aType.name}")
                action.setData(tooltipType)

                # Set default selection (none)
                if tooltipType == "none":
                    action.setChecked(True)

                action.triggered.connect(lambda checked, e=aType, t=tooltipType: self.setTooltipTypeForEntity(e, t))
                actionGroup.addAction(action)
                entityMenu.addAction(action)

            # Add custom tooltips defined by modeler
            for tooltipName in aType.customTooltips.keys():
                action = QAction(f"&{tooltipName}", self)
                action.setCheckable(True)
                action.setStatusTip(f"Custom tooltip: {tooltipName} for {aType.name}")
                action.setData(tooltipName)

                action.triggered.connect(lambda checked, e=aType, t=tooltipName: self.setTooltipTypeForEntity(e, t))
                actionGroup.addAction(action)
                entityMenu.addAction(action)

    def updateTooltipMenu(self):
        """Update tooltip menu when custom tooltips are added"""
        # Clear existing tooltip menu
        if hasattr(self, 'tooltipMenu'):
            self.tooltipMenu.clear()
            if hasattr(self, 'tooltipActionGroups'):
                del self.tooltipActionGroups
        # Recreate the menu
        self.createTooltipMenu()

    def createGraphMenu(self):
        self.chooseGraph = self.menuBar().addMenu(QIcon(f"{path_icon}/icon_dashboards.png"), "&openChooseGraph")
        # Submenu linear
        actionLinearDiagram = QAction(QIcon(f'{path_icon}/icon_linear.png'), 'Diagramme Linéaire', self)
        actionLinearDiagram.triggered.connect(self.openLinearGraph)
        self.chooseGraph.addAction(actionLinearDiagram)
        actionHistogramDiagram = QAction(QIcon(f'{path_icon}/icon_histogram.png'), 'Histogramme', self)
        actionHistogramDiagram.triggered.connect(self.openHistoGraph)
        self.chooseGraph.addAction(actionHistogramDiagram)
        actionCircularDiagram = QAction(QIcon(f'{path_icon}/icon_circular.jpg'), 'Diagramme Circulaire', self)
        actionCircularDiagram.triggered.connect(self.openCircularGraph)
        self.chooseGraph.addAction(actionCircularDiagram)
        actionStackPlotDiagram = QAction(QIcon(f'{path_icon}/icon_stackplot.jpg'), 'Diagramme Stack Plot', self)
        actionStackPlotDiagram.triggered.connect(self.openStackPlotGraph)
        self.chooseGraph.addAction(actionStackPlotDiagram)
        actionOtherDiagram = QAction(QIcon(f'{path_icon}/graph.png'), 'Autres Représentations', self)
        actionOtherDiagram.triggered.connect(self.openOtherGraph)
        self.chooseGraph.addAction(actionOtherDiagram)

    # Create all the action related to the menu
    def createAction(self):
        self.save = QAction(QIcon(f"{path_icon}/save.png"), " &save", self)
        self.save.setShortcut("Ctrl+s")
        self.save.triggered.connect(self.saveTheGame)
        self.backward = QAction(
            QIcon(f"{path_icon}/backwardArrow.png"), " &backward", self)
        self.backward.triggered.connect(self.backwardAction)
        self.forward = QAction(
            QIcon(f"{path_icon}/forwardArrow.png"), " &forward", self)
        self.forward.triggered.connect(self.forwardAction)
        self.inspect = QAction(
            QIcon(f"{path_icon}/inspect.png"), " &inspectAll", self)
        self.inspect.triggered.connect(self.inspectAll)

    # Zoom
    def zoomPlusModel(self):
        """
        Zoom in all grids in the model
        """
        for grid in self.getGrids():
            grid.newZoomIn()

    def zoomLessModel(self):
        """
        Zoom out all grids in the model
        """
        for grid in self.getGrids():
            grid.newZoomOut()

    def zoomFitModel(self):
        """
        Reset zoom for all grids in the model
        """
        for grid in self.getGrids():
            grid.resetZoom()

    # open graph windows
    def openLinearGraph(self):
        aGraph = SGGraphWindow(self).open_graph_type("linear")
        self.openedGraphs.append(aGraph)

    def openHistoGraph(self):
        aGraph = SGGraphWindow(self).open_graph_type("histogram")
        self.openedGraphs.append(aGraph)

    def openStackPlotGraph(self):
        aGraph = SGGraphWindow(self).open_graph_type("stackplot")
        self.openedGraphs.append(aGraph)

    def openCircularGraph(self):
        aGraph = SGGraphWindow(self).open_graph_type("circular")
        self.openedGraphs.append(aGraph)

    def openOtherGraph(self):
        print("WITH CSV OPTION")

    def createEnhancedGridLayoutMenu(self):
        """Create Enhanced Grid Layout submenu in Settings menu"""
        if self.typeOfLayout == "enhanced_grid":
            self.enhancedGridMenu = self.settingsMenu.addMenu("&Enhanced Grid Layout")

            # Edit layoutOrders action
            editLayoutOrderAction = QAction("&Edit Layout...", self)
            editLayoutOrderAction.triggered.connect(self.openLayoutOrderTableDialog)
            self.enhancedGridMenu.addAction(editLayoutOrderAction)

            # Save layout configuration action
            saveConfigAction = QAction("&Save Current Layout...", self)
            saveConfigAction.triggered.connect(self.openSaveLayoutConfigDialog)
            self.enhancedGridMenu.addAction(saveConfigAction)

            # Manage layout configurations action
            manageConfigAction = QAction("&Manage Layout Configurations...", self)
            manageConfigAction.triggered.connect(self.openLayoutConfigManagerDialog)
            self.enhancedGridMenu.addAction(manageConfigAction)
            # Separator
            self.enhancedGridMenu.addSeparator()

            # Toggle layoutOrder tooltips action
            self.layoutOrderTooltipAction = QAction("&Show GameSpace order tooltip", self)
            self.layoutOrderTooltipAction.setCheckable(True)
            self.layoutOrderTooltipAction.setChecked(False)
            self.layoutOrderTooltipAction.triggered.connect(self.toggleLayoutOrderTooltips)
            self.enhancedGridMenu.addAction(self.layoutOrderTooltipAction)

    def setTooltipTypeForEntity(self, entityDef, tooltipType):
        """Set tooltip type for a specific entity definition"""
        if hasattr(entityDef, 'displayTooltip'):
            entityDef.displayTooltip(tooltipType)

    def toggleLayoutOrderTooltips(self, checked):
        """
        Toggle layoutOrder tooltips for all gameSpaces

        Args:
            checked (bool): Whether to show layoutOrder tooltips
        """
        if self.typeOfLayout == "enhanced_grid":
            for gameSpace in self.gameSpaces.values():
                gameSpace._enhanced_grid_tooltip_enabled = checked

    def createThemeManagerMenu(self):
        """Create Theme Manager entries in Settings menu"""
        self.themeMenu = self.settingsMenu.addMenu("&Themes")

        # Edit per-GameSpace themes (table)
        editThemesAction = QAction("&Edit Themes...", self)
        editThemesAction.triggered.connect(self.openThemeEditTableDialog)
        self.themeMenu.addAction(editThemesAction)

        # Manage Theme Configurations (dialog)
        manageThemeAction = QAction("&Manage Theme Configurations...", self)
        manageThemeAction.triggered.connect(self.openThemeConfigManagerDialog)
        self.themeMenu.addAction(manageThemeAction)

        # Change window background color
        changeBgColorAction = QAction("&Change window background color...", self)
        changeBgColorAction.triggered.connect(self.openWindowBackgroundColorDialog)
        self.themeMenu.addAction(changeBgColorAction)

    def openThemeConfigManagerDialog(self):
        """Open the Theme Configuration Manager dialog."""
        dialog = SGThemeConfigManagerDialog(self)
        dialog.exec_()

    def openThemeEditTableDialog(self):
        """Open the per-GameSpace theme assignment dialog (table)."""
        dialog = SGThemeEditTableDialog(self)
        dialog.exec_()

    def openWindowBackgroundColorDialog(self):
        """Open a color dialog to change the window background color."""
        from PyQt5.QtWidgets import QColorDialog, QWidget
        from PyQt5.QtGui import QColor
        from PyQt5.QtCore import Qt
        
        # Get current color if set, otherwise default to white
        if self.windowBackgroundColor:
            if isinstance(self.windowBackgroundColor, QColor):
                current_color = self.windowBackgroundColor
            elif isinstance(self.windowBackgroundColor, str):
                # Parse CSS color string (hex format like "#ffffff" or named colors)
                current_color = QColor(self.windowBackgroundColor)
                if not current_color.isValid():
                    current_color = QColor("#ffffff")
            else:
                # Qt.GlobalColor (like Qt.white, Qt.black, etc.) or other types
                try:
                    current_color = QColor(self.windowBackgroundColor)
                    if not current_color.isValid():
                        current_color = QColor("#ffffff")
                except Exception:
                    current_color = QColor("#ffffff")
        else:
            # No color set, check if styleSheet has a background color
            # Otherwise default to white
            current_color = QColor("#ffffff")
        
        # Create a QColorDialog and position it to the right of main window
        dialog = QColorDialog(current_color, self)
        dialog.setWindowTitle("Select Window Background Color")
        
        # Position dialog to the right of main window
        from mainClasses.SGExtensions import position_dialog_to_right
        position_dialog_to_right(dialog, self)
        
        # Open dialog
        if dialog.exec_() == QColorDialog.Accepted:
            color = dialog.currentColor()
            if color.isValid():
                # Store as QColor object for consistency
                self.windowBackgroundColor = color.name()  # Store as hex string for serialization
                # Use QPalette to set background without affecting child widgets
                from PyQt5.QtGui import QPalette
                palette = self.window.palette()
                palette.setColor(QPalette.Window, color)
                self.window.setPalette(palette)
                self.window.setAutoFillBackground(True)
                self.update()

    def applyThemeToAllGameSpaces(self, theme_name: str, include_types=None, exclude_types=None, priority: str = "global_then_individual") -> None:
        """Apply a theme to all GameSpaces; individual overrides remain in effect.

        Args:
            theme_name (str): Theme to apply ('modern','minimal','colorful','blue','green','gray')
            include_types (list|None): Optional list of classes to include
            exclude_types (list|None): Optional list of classes to exclude
            priority (str): Reserved for future conflict resolution
        """
        for gs in self.gameSpaces.values():
            if include_types and not any(isinstance(gs, t) for t in include_types):
                continue
            if exclude_types and any(isinstance(gs, t) for t in exclude_types):
                continue
            if hasattr(gs, 'applyTheme'):
                try:
                    gs.applyTheme(theme_name)
                except Exception:
                    pass

    def _loadCustomThemes(self):
        """Load custom themes from persistent storage into _runtime_themes."""
        try:
            manager = SGThemeConfigManager(self)
            custom_themes = manager.loadCustomThemes()
            self._runtime_themes = custom_themes.copy()
        except Exception:
            # If loading fails, just keep empty dict
            self._runtime_themes = {}


    def getSubmenuSymbology(self, submenuName):
        # return the submenu
        return next((item for item in self.symbologiesInSubmenus.keys() if item.title() == submenuName), None)

    def getOrCreateSubmenuSymbology(self, submenu_name):
        # return the submenu (or create it if it doesn't exist yet)
        submenu = self.getSubmenuSymbology(submenu_name)
        if submenu is not None:
            return submenu
        else:
            submenu = QMenu(submenu_name, self)
            self.symbologyMenu.addMenu(submenu)
            self.symbologiesInSubmenus[submenu] = []
            return submenu

    def addEntTypeSymbologyinMenuBar(self, aType, nameOfSymbology, isBorder=False):
        if self.symbologyMenu is None:
            return False
        submenu_name = aType.name
        if isBorder:
            submenu_name = submenu_name + self.keyword_borderSubmenu
        # get the submenu (or create it if it doesn't exist yet)
        submenu = self.getOrCreateSubmenuSymbology(submenu_name)
        # create an element with checkbox
        item = QAction(nameOfSymbology, self, checkable=True)
        item.triggered.connect(self.menu_item_triggered)
        # add the submenu to the menu
        submenu.addAction(item)
        # add actions to the submenu
        self.symbologiesInSubmenus[submenu].append(item)

    def checkSymbologyinMenuBar(self, aType, nameOfSymbology, borderSymbology=False):
        """
        Checks and updates the symbology in the menu bar for the specified class definition.
        Args:
            aType: The class definition for which the symbology is being checked.
            nameOfSymbology (str): The name of the symbology to check.
            borderSymbology (bool): Indicates if the symbology is for a border (default: False).
        Returns:
            bool: False if the symbology menu is not initialized, otherwise None.
        """
        if self.symbologyMenu is None:
            return False
        if borderSymbology:
            name = aType.name + self.keyword_borderSubmenu
        else:
            name = aType.name
        symbologies = self.getSymbologiesOfSubmenu(name)
        for aSymbology in symbologies:
            if aSymbology.text() == nameOfSymbology:
                aSymbology.setChecked(True)
            else:
                if not borderSymbology:
                    aSymbology.setChecked(False)

    def menu_item_triggered(self):
        # get the triggered QAction object
        selectedSymbology = self.sender()
        # browse the dict to uncheck other symbologies
        for symbologies in self.symbologiesInSubmenus.values():
            if selectedSymbology in symbologies:
                [aSymbology.setChecked(False) for aSymbology in symbologies if aSymbology is not selectedSymbology]
        for aLegend in self.getLegends():
            aLegend.updateWithSymbologies(self.getAllCheckedSymbologies())
            # aLegend.updateWithSymbologies(self.getAllCheckedSymbologies(aLegend.grid.id))
        self.update()  # update all the interface display

    def getSymbologiesOfSubmenu(self, submenuName, borderSymbology=False):
        # return the  symbologies of a entity present in the menuBar
        submenu = self.getSubmenuSymbology(submenuName)
        return self.symbologiesInSubmenus.get(submenu)

    def getCheckedSymbologyOfEntity(self, name, borderSymbology=False):
        # return the name of the symbology which is checked for a given entity type. If no symbology is ckecked, returns None
        if self.symbologyMenu is None:
            return None
        if borderSymbology:
            name = name + self.keyword_borderSubmenu
        symbologies = self.getSymbologiesOfSubmenu(name)
        if symbologies is None:
            return None
        return next((aSymbology.text() for aSymbology in symbologies if aSymbology.isChecked()), None)

    def getAllCheckedSymbologies(self, grid=None):
        # return the active symbology of each type of entity
        if grid is None:
            gridObject = self.getGrids()[0]
            cellType = self.getCellType(gridObject)
            entityTypes = [cellType] + list(self.agentTypes.values())
        elif grid == "combined":
            entityTypes = []
            for aGrid in self.getGrids():
                cellType = self.getCellType(aGrid)
                entityTypes = entityTypes + [cellType]
            entityTypes = entityTypes + list(self.agentTypes.values())
        else:
            gridObject = self.getGrid_withID(grid)
            cellType = self.getCellType(gridObject)
            entityTypes = [cellType] + list(self.agentTypes.values())
        selectedSymbologies = {}
        for type in entityTypes:
            selectedSymbologies[type] = {
                'shape': self.getCheckedSymbologyOfEntity(type.name),
                'border': self.getCheckedSymbologyOfEntity(type.name, borderSymbology=True)
            }
        return selectedSymbologies

    def checkFirstSymbologyOfEntitiesInMenu(self):
        # return the name of the symbology which is checked for a given entity type. If no symbology is ckecked, returns None
        for aListOfSubmenuItems in self.symbologiesInSubmenus.values():
            aListOfSubmenuItems[0].setChecked(True)

    # ============================================================================
    # ENTITY MANAGEMENT METHODS
    # ============================================================================
    def __ENTITY_MANAGEMENT_METHODS__(self):
        pass

    def getSGEntity_withIdentfier(self, aIdentificationDict):
        # This method is used by updateServer to retrieve an entity (cell , agents) used has argument in a game action
        type = self.getEntityType(aIdentificationDict['name'])
        aId = aIdentificationDict['id']
        targetEntity = type.getEntity(aId)
        return targetEntity

    def getSGObject_withIdentifier(self, aIdentificationDict):
        # This method is used by updateServer to retrieve any type of SG object (eg. GameAction or Entity)
        className = aIdentificationDict['name']
        aId = aIdentificationDict['id']
        return next((aInst for aInst in eval(className).instances if aInst.id == aId), None)

    def generateCellsForGrid(self, grid, name, defaultCellColor, defaultCellImage):
        CellType = SGCellType(grid, grid.cellShape, grid.size, entDefAttributesAndValues=None, name=name, defaultColor=defaultCellColor, defaultImage=defaultCellImage)
        self.cellTypes[grid.id] = CellType
        for row in range(1, grid.rows + 1):
            for col in range(1, grid.columns + 1):
                CellType.newCell(col, row)
        return CellType

    def getGrid(self, anObject):
        if anObject.isCellType:
            return anObject.grid
        elif anObject.isAGrid:
            return anObject
        else:
            raise ValueError('Wrong object type')

    def getCellPovs(self, grid):
        return {key: value for dict in (self.cellTypes[grid.id]['ColorPOV'], self.cellTypes[grid.id]['BorderPOV']) for key, value in dict.items() if "selected" not in key and "BorderWidth" not in key}

    def getGrid_withID(self, aGridID):
        return next((item for item in self.getGrids() if item.id == aGridID), None)

    def getLegends(self):
        # To get all type of gameSpace who are legends
        return [aGameSpace for aGameSpace in list(self.gameSpaces.values()) if isinstance(aGameSpace, SGLegend)]

    def getControlPanels(self):
        return [aGameSpace for aGameSpace in list(self.gameSpaces.values()) if isinstance(aGameSpace, SGControlPanel)]

    def getAdminControlPanels(self):  # useful in case they are several admin control panels
        return [item for item in self.getControlPanels() if item.isAdminLegend()]

    def getSelectedLegendItem(self):
        return next((item.selected for item in self.getControlPanels() if item.isActiveAndSelected()), None)

    def getGameAction_withClassAndId(self, aClassName, aId):
        return next((item for item in self.getAllGameActions() if item.__class__.__name__ == aClassName and item.id == aId), None)

    def getSimVars(self):
        return self.simulationVariables

    def getTimeManager(self):
        return self.timeManager

    def getTextBoxHistory(self, TextBoxes):
        for aTextBox in TextBoxes:
            print(str(aTextBox.id) + ' : ' + str(aTextBox.history))

    def getAllPlayers(self):
        return list(self.players.values())

    def getPlayer(self, aUserName):
        if aUserName is None:
            raise ValueError('Username cannot be None')
        if aUserName == "Admin":
            return self.getAdminPlayer()
        if isinstance(aUserName, SGPlayer):
            return aUserName
        if aUserName in self.players:
            return self.players[aUserName]
        else:
            raise ValueError(f'No Player named {aUserName} exists')

    def getCurrentPlayer(self):
        if not self.currentPlayerName:
            raise ValueError('Current player is not defined')
        return self.getPlayer(self.currentPlayerName)

    def getPlayers(self):
        """
        Get all the players of the game
        Returns:
            list: list of players
        """
        return self.players.values()

    def getUsersName(self):
        aList = [aP.name for aP in list(self.players.values())]
        aList.append('Admin')
        return aList

    def getAdminPlayer(self):
        """Get the Admin player instance"""
        return self.players.get("Admin")

    def getUserControlPanelOrLegend(self, aUserName):
        self.getLegends()

    # To select only users with a control panel
    def getUsers_withControlPanel(self):
        selection = []
        for aP in self.players.values():
            if aP.name == 'Admin':
                # Admin: add if shouldDisplayAdminControlPanel OR if he has a controlPanel
                if self.shouldDisplayAdminControlPanel or aP.controlPanel != None:
                    selection.append(aP.name)
            else:
                # Other players: add if they have a controlPanel
                if aP.controlPanel != None:
                    selection.append(aP.name)
        return selection

    def getUsers_withGameActions(self):
        """
        Get list of players who have gameActions
        Returns:
            list: List of player names who have gameActions
        """
        selection = []
        for aP in self.players.values():
            if aP.name == 'Admin':
                # Admin: add if shouldDisplayAdminControlPanel OR if he has gameActions
                if self.shouldDisplayAdminControlPanel or len(aP.gameActions) > 0:
                    selection.append(aP.name)
            else:
                # Other players: add if they have gameActions
                if len(aP.gameActions) > 0:
                    selection.append(aP.name)
        return selection

    # To change the number of zoom we currently are
    def setNumberOfZoom(self, number):
        self.numberOfZoom = number

    # To set User list
    def setUsers(self, listOfUsers):
        self.users = listOfUsers

    def deleteTextBox(self, titleOfTheTextBox):
        del self.gameSpaces[titleOfTheTextBox]

    def checkAndUpdateWatchers(self):
        for aType in self.getEntityTypes():
            aType.updateAllWatchers()

    # ============================================================================
    # LAYOUT MANAGEMENT METHODS
    # ============================================================================
    def __LAYOUT_MANAGEMENT_METHODS__(self):
        pass

    def applyAutomaticLayout(self): 
        # Runtime polymorphism - each layout handles its own logic
        self.layoutOfModel.applyLayout(self.gameSpaces.values())

    def openLayoutOrderTableDialog(self):
        """
        Open the layoutOrder management dialog
        """
        if self.typeOfLayout == "enhanced_grid":
            from mainClasses.layout.SGLayoutOrderTableDialog import SGLayoutOrderTableDialog
            dialog = SGLayoutOrderTableDialog(self)
            dialog.exec_()

    def reorganizeEnhancedGridLayoutOrders(self):
        """
        Reorganize layoutOrders to eliminate gaps while preserving order

        This method is called during initialization to ensure sequential layoutOrder numbering
        for better column distribution in the Enhanced Grid Layout.
        """
        if self.typeOfLayout == "enhanced_grid":
            self.layoutOfModel.reorganizeLayoutOrdersSequentially()

    def checkLayoutIntersection(self, name, element, otherName, otherElement):
        if name != otherName and (element.geometry().intersects(otherElement.geometry()) or element.geometry().contains(otherElement.geometry())):
            return True
        return False

    def saveLayoutConfig(self, config_name=None):
        """
        Save current Enhanced Grid Layout configuration for reuse.

        Args:
            config_name (str, optional): Name for the saved configuration.
                                    If None, opens dialog for user input.

        Example:
            model.saveLayoutConfig()  # Opens dialog
            model.saveLayoutConfig("my_layout")  # Direct save
        """
        if self.typeOfLayout != "enhanced_grid":
            QMessageBox.warning(self, "Warning",
                            "Layout configuration can only be saved for Enhanced Grid Layout")
            return False

        if config_name is None:
            # Open dialog for user input
            try:
                from mainClasses.layout.SGLayoutConfigSaveDialog import SGLayoutConfigSaveDialog
                available_configs = self.getAvailableLayoutConfigs()

                dialog = SGLayoutConfigSaveDialog(self, available_configs)
                result = dialog.exec_()

                if result == QDialog.Accepted:
                    config_name = dialog.getConfigName()
                    if not config_name or config_name.strip() == "":
                        QMessageBox.warning(self, "Warning", "Configuration name cannot be empty")
                        return False
                else:
                    return False  # User cancelled
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open save dialog: {e}")
                return False

        config_manager = SGLayoutConfigManager(self)
        success = config_manager.saveConfig(config_name)

        if success:
            QMessageBox.information(self, "Success",
                                f"Layout configuration '{config_name}' saved successfully")
        else:
            QMessageBox.critical(self, "Error",
                            f"Failed to save layout configuration '{config_name}'")

        return success

    def applyLayoutConfig(self, config_name):
        """
        Apply a saved Enhanced Grid Layout configuration.

        This method memorizes the configuration name and applies it automatically
        at the end of initBeforeShowing() (called by launch()). This ensures all
        GameSpaces are created before applying the layout configuration.

        Args:
            config_name (str): Name of the configuration to apply

        Returns:
            bool: True if configuration name was memorized, False otherwise

        Example:
            # Apply a saved layout configuration (will be applied when launch() is called)
            model.applyLayoutConfig("my_layout")
            model.launch()  # Layout will be applied after all GameSpaces are created
            
            # Check before applying
            if model.hasLayoutConfig("setup1"):
                model.applyLayoutConfig("setup1")
        """
        if self.typeOfLayout != "enhanced_grid":
            return False

        # Verify the configuration exists before memorizing
        config_manager = SGLayoutConfigManager(self)
        if not config_manager.configExists(config_name):
            print(f"Layout config '{config_name}' does not exist")
            return False

        # Memorize the configuration name for loading at the end of initBeforeShowing
        self._pending_layout_config = config_name
        return True

    def hasLayoutConfig(self, config_name):
        """
        Check if a layout configuration exists.

        Args:
            config_name (str): Name of the configuration to check

        Returns:
            bool: True if configuration exists, False otherwise

        Example:
            if model.hasLayoutConfig("my_layout"):
                model.applyLayoutConfig("my_layout")
        """
        config_manager = SGLayoutConfigManager(self)
        return config_manager.configExists(config_name)

    def getAvailableLayoutConfigs(self):
        """
        Get list of available layout configurations.

        Returns:
            list: List of configuration names

        Example:
            configs = model.getAvailableLayoutConfigs()
            print(f"Available configs: {configs}")
        """
        config_manager = SGLayoutConfigManager(self)
        return config_manager.getAvailableConfigs()

    def hasThemeConfig(self, config_name: str) -> bool:
        """
        Check if a theme configuration exists.

        Args:
            config_name (str): Name of the configuration to check

        Returns:
            bool: True if configuration exists, False otherwise

        Example:
            if model.hasThemeConfig("my_config"):
                model.applyThemeConfig("my_config")
        """
        manager = SGThemeConfigManager(self)
        return manager.configExists(config_name)

    def getAvailableThemeConfigs(self) -> list:
        """
        Get list of available theme configurations for the current model.

        Returns:
            list: List of configuration names

        Example:
            configs = model.getAvailableThemeConfigs()
            print(f"Available configs: {configs}")
            # Output: ['setup1', 'setup2', 'default']
        """
        manager = SGThemeConfigManager(self)
        return manager.getAvailableConfigs()

    def openSaveLayoutConfigDialog(self):
        """Open the save layout configuration dialog."""
        self.saveLayoutConfig()  # This will open the dialog since config_name is None

    def openLayoutConfigManagerDialog(self):
        """
        Open the layout configuration manager dialog.

        This dialog allows users to view, rename, and delete saved configurations.
        """
        from mainClasses.layout.SGLayoutConfigManagerDialog import SGLayoutConfigManagerDialog
        dialog = SGLayoutConfigManagerDialog(self)
        dialog.exec_()

    # ============================================================================
    # GAME FLOW MANAGEMENT METHODS
    # ============================================================================
    def __GAME_FLOW_MANAGEMENT_METHODS__(self):
        pass

    # Trigger the next turn
    def nextTurn(self):
        self.timeManager.nextPhase()
        if self.mqttMajType in ["Phase", "Instantaneous"]:
            self.mqttManager.buildNextTurnMsgAndPublishToBroker()

    # Return all gameActions of all players
    def getAllGameActions(self):
        aList = []
        for player in self.players.values():
            aList.extend(player.gameActions)
        return aList

    def getAgentIDFromMessage(self, message, nbCells):
        """
        Get the Agent ID list from an update message
        args:
            - message (array of string) : decoded mqtt message
            - nbCells (int) : value in the message
        """
        majIDs = set()
        for j in range(len(message[nbCells + 2:-5])):
            agID = message[nbCells + 2 + j][0]
            majIDs.add(agID)
        return majIDs

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    def __UTILITY_METHODS__(self):
        pass

    def getAgentsPrivateID(self):
        agents = self.getAllAgents()
        agents_privateID = []
        for agent in agents:
            agents_privateID.append(agent.privateID)
        return agents_privateID

    def numberOfGrids(self):
        return len(self.cellTypes)

    def maj_coordonnees(self):
        pos_souris_globale = self.mapFromGlobal(QCursor.pos())
        coord_x, coord_y = pos_souris_globale.x(), pos_souris_globale.y()
        self.label.setText(f'Global Cursor Coordinates : ({coord_x}, {coord_y})')

    # To get a gameSpace in particular
    def getGameSpaceByName(self, name):
        return self.gameSpaces[name]

    def getGameSpaceByClass(self, aClass):
        gameSpaces = [aGameSpace for aName, aGameSpace in self.gameSpaces.items() if isinstance(aGameSpace, aClass)]
        return gameSpaces

    def getAllDataSinceInit(self):
        rounds = set([entry['round'] for entry in self.listData])
        print("rounds :: ", rounds)

    # ============================================================================
    # OBSOLETE/TO DELETE METHODS
    # ============================================================================
    def __OBSOLETE_DEVELOPER_METHODS__(self):
        pass
    # def show_contextMenu(self, point): #todo Obsolete - to delete
    # def setAllDataSinceInit(self): #todo Obsolete - to delete
    # def adjustGamespacesPosition(self): #todo Obsolete - to delete



    def __MODELER_METHODS__(self):
        pass
# ============================================================================
# MODELER METHODS
# ============================================================================

    def __MODELER_METHODS__NEW__(self):
        pass
# ============================================================================
# NEW/ADD METHODS
# ============================================================================
    # To create a grid
    def newCellsOnGrid(self, columns=10, rows=10, format="square", size=30, gap=0, backgroundColor=Qt.gray, borderColor=Qt.black, moveable=True, name=None, backGroundImage=None, defaultCellColor=Qt.white, defaultCellImage=None, neighborhood='moore', boundaries='open') -> SGCellType:
        """
        Create a grid that contains cells.
        
        For better clarity, consider using newGridWithCells() instead.

        Args:
            columns (int): number of columns (width).
            rows (int): number of rows (height).
            format ("square", "hexagonal"): shape of the cells.
                - Defaults to "square".
                - Note that the hexagonal grid is "Pointy-top hex grid with even-r offset".
            size (int, optional): size of the cells. Defaults to 30.
            gap (int, optional): gap size between cells. Defaults to 0.
            backgroundColor (Qt.Color, optional): background color of the grid. Defaults to Qt.gray.
            borderColor (Qt.Color, optional): border color of the grid. Defaults to Qt.black.
            moveable (bool) : grid can be moved by clic and drage. Defaults to "True".
            name (st): name of the grid.
            backGroundImage (QPixmap, optional): Background image for the grid as a QPixmap. If None, no background image is applied.
            defaultCellColor (Qt.Color, optional): Default color for each cell as a Qt.Color. If None, cells are displayed with background image.
            defaultCellImage (QPixmap, optional): Default image for each cell as a QPixmap. If None, cells are displayed with background colors.
            neighborhood ("moore","neumann"): Neighborhood type for cell os the grid. Defaults to "moore".
                - "moore": Moore neighborhood (8 neighbors for square cells, 6 for hexagonal cells).
                - "neumann": Von Neumann neighborhood (4 neighbors for square cells) , 3 or 4 for hexagonal cells, depending on orientation).
            boundaries ("mopen","closed"): Boundary condition of the grid. Defaults to "open".
                - "open": The grid is toroidal (no boundaries); edges are connected (wrap-around), so every cell has the same number of neighbors.
                - "closed": The grid has finite boundaries; Cells on the edge have fewer neighbors (no wrap-around).

        Returns:
            SGCellType: the cellDef (SGCellType) that defines the cells that have been placed on a grid. 
                       Note: This is NOT a SGGrid object, but the CellDef that manages the cells on the grid.
        """
        # process the name if not defined by the user. The name has to be uniquer, because it is used to reference the CellDef and the associated grid
        if name is None:
            name = f'grid{str(self.numberOfGrids()+1)}'
            if name in self.gameSpaces:
                name = name + 'bis'
        # Create a grid with default values (will be overridden by setters below)
        aGrid = SGGrid(self, name, columns, rows, format, gap, size, None, moveable, backGroundImage, neighborhood, boundaries)
        
        # Apply styles via modeler methods (ensures everything goes through gs_aspect)
        aGrid.setBackgroundColor(backgroundColor)
        aGrid.setBorderColor(borderColor)
        # Background image is already set in SGGrid.__init__ if provided

        # Create a CellDef and populate the grid with cells from the newly created CellDef
        aCellDef = self.generateCellsForGrid(aGrid,name, defaultCellColor, defaultCellImage)
        aGrid.cellDef =aCellDef

        self.gameSpaces[name] = aGrid

        # add the gamespace to the layout
        self.layoutOfModel.addGameSpace(aGrid)
        
        return aCellDef
    
    def newGridWithCells(self, columns=10, rows=10, format="square", size=30, gap=0, backgroundColor=Qt.gray, borderColor=Qt.black, moveable=True, name=None, backGroundImage=None, defaultCellImage=None, neighborhood='moore', boundaries='open') -> SGCellType:
        """
        Create a grid that contains cells.

        Args:
            columns (int): number of columns (width).
            rows (int): number of rows (height).
            format ("square", "hexagonal"): shape of the cells.
                - Defaults to "square".
                - Note that the hexagonal grid is "Pointy-top hex grid with even-r offset".
            size (int, optional): size of the cells. Defaults to 30.
            gap (int, optional): gap size between cells. Defaults to 0.
            backgroundColor (Qt.Color, optional): background color of the grid. Defaults to Qt.gray.
            borderColor (Qt.Color, optional): border color of the grid. Defaults to Qt.black.
            moveable (bool) : grid can be moved by clic and drage. Defaults to "True".
            name (st): name of the grid.
            backGroundImage (QPixmap, optional): Background image for the grid as a QPixmap. If None, no background image is applied.
            defaultCellImage (QPixmap, optional): Default image for each cell as a QPixmap. If None, cells are displayed with background colors.
            neighborhood ("moore","neumann"): Neighborhood type for cell os the grid. Defaults to "moore".
                - "moore": Moore neighborhood (8 neighbors for square cells, 6 for hexagonal cells).
                - "neumann": Von Neumann neighborhood (4 neighbors for square cells) , 3 or 4 for hexagonal cells, depending on orientation).
            boundaries ("mopen","closed"): Boundary condition of the grid. Defaults to "open".
                - "open": The grid is toroidal (no boundaries); edges are connected (wrap-around), so every cell has the same number of neighbors.
                - "closed": The grid has finite boundaries; Cells on the edge have fewer neighbors (no wrap-around).

        Returns:
            SGCellType: the cellDef (SGCellType) that defines the cells that have been placed on a grid. 
                       Note: This is NOT a SGGrid object, but the CellDef that manages the cells on the grid.
        """
        return self.newCellsOnGrid(columns, rows, format, size, gap, backgroundColor, borderColor, moveable, name, backGroundImage, defaultCellImage, neighborhood, boundaries)


    # To create a New kind of agents
    def newAgentType(self, name, shape, entDefAttributesAndValues=None, defaultSize=15, defaultColor=Qt.black, locationInEntity="random",defaultImage=None):
        """
        Create a new specie of Agents.

        Args:
            name (str) : the agentType name
            shape (str) : the agentType shape ("circleAgent","squareAgent", "ellipseAgent1","ellipseAgent2", "rectAgent1","rectAgent2", "triangleAgent1","triangleAgent2", "arrowAgent1","arrowAgent2","hexagonAgent")
            dictAttributes (dict) : all the agentType attributs with all the values
            defaultSize (int) : the agentType shape size (Default=10)
            locationInEntity (str, optional) : topRight, topLeft, center, bottomRight, bottomLeft, random 
            defaultImage (str, optional) : link to image
        Return:
            a agentType

        """
        if shape not in ["circleAgent","squareAgent", "ellipseAgent1","ellipseAgent2", "rectAgent1","rectAgent2", "triangleAgent1","triangleAgent2", "arrowAgent1","arrowAgent2","hexagonAgent"]:
            raise ValueError(f"Invalid shape: {shape}")
        aAgentType = SGAgentType(self, name, shape, defaultSize, entDefAttributesAndValues, defaultColor,locationInEntity,defaultImage)
        self.agentTypes[name]=aAgentType
        return aAgentType

    def newTileType(self, name, shape="rectTile", entDefAttributesAndValues=None, defaultSize=20, 
                    positionOnCell="center", defaultFace="front", frontImage=None, backImage=None, frontColor=Qt.lightGray, backColor=Qt.darkGray, colorForLegend=None,
                    stackRendering=None):
        """
        Create a new type of Tiles.
        
        This method creates a TileType factory that can be used to create Tile instances.
        All tiles of the same type share fixed properties like position on cell, default face,
        colors, images, and stack rendering configuration.
        
        Args:
            name (str): The tileType name (must be unique)
            shape (str, optional): The tileType shape. Must be one of:
                - "rectTile": Rectangular tile
                - "circleTile": Circular tile
                - "ellipseTile": Elliptical tile
                - "imageTile": Tile rendered only with an image (no geometric shape)
                Default: "rectTile"
            entDefAttributesAndValues (dict, optional): Default attributes and values for tiles of this type
            defaultSize (int, optional): The tileType shape size in pixels. Default: 20
            positionOnCell (str, optional): Fixed position on cell for all tiles of this type.
                Must be one of: "center", "topLeft", "topRight", "bottomLeft", "bottomRight", "full".
                Default: "center". Cannot be overridden when creating tiles.
            defaultFace (str, optional): Default face for new tiles ("front" or "back").
                Default: "front"
            frontImage (QPixmap, optional): Default image for the front face
            backImage (QPixmap, optional): Default image for the back face
            frontColor (QColor, optional): Color for the front face. Default: Qt.lightGray
            backColor (QColor, optional): Color for the back face. Default: Qt.darkGray
            colorForLegend (QColor, optional): Explicit color for legends/ControlPanels.
                If not specified, the color is determined dynamically from defaultFace:
                - Uses frontColor if defaultFace="front"
                - Uses backColor if defaultFace="back"
                This allows legends to show the color of the visible face by default.
            stackRendering (dict, optional): Stack rendering configuration. Dictionary with keys:
                - "mode" (str): Rendering mode. Must be one of:
                    - "topOnly": Only the top tile is visible
                    - "offset": Tiles are displayed with slight offsets (showing edges)
                - "maxVisible" (int, optional): Maximum number of tiles to display in a stack.
                    Always shows the top tiles when limiting. Default: 5
                - "offset" (int, optional): Pixel offset amount between tiles in offset rendering mode.
                    Each tile is offset by this amount multiplied by its position in the visible stack.
                    Only used when mode="offset". Default: 3
                - "showCounter" (bool, optional): Display a counter on the top tile showing stack size.
                    Default: False
                - "counterPosition" (str, optional): Position of the counter on the tile.
                    Must be one of: "topRight", "topLeft", "bottomRight", "bottomLeft", "center".
                    Default: "topRight"
                If None, defaults to {"mode": "offset", "maxVisible": 5, "offset": 3, "showCounter": False, "counterPosition": "topRight"}
        
        Returns:
            SGTileType: The created tile type factory
            
        Raises:
            ValueError: If shape is invalid, or if stackRendering parameters are invalid
            
        Example:
            # Create a simple tile type
            tileType = model.newTileType("Forest", shape="rectTile", frontColor=Qt.green)
            
            # Create a tile type with stack rendering
            cardType = model.newTileType(
                "Card",
                shape="rectTile",
                frontColor=Qt.blue,
                backColor=Qt.red,
                stackRendering={"mode": "offset", "showCounter": True, "counterPosition": "topLeft"}
            )
        """
        if shape not in ["rectTile", "circleTile", "ellipseTile", "imageTile"]:
            raise ValueError(f"Invalid shape: {shape}. Must be one of: rectTile, circleTile, ellipseTile, imageTile")
        
        # Set default stackRendering if not provided
        if stackRendering is None:
            stackRendering = {}
        
        # Validate and set defaults for stackRendering
        mode = stackRendering.get("mode", "offset")
        if mode not in ["topOnly", "offset"]:
            raise ValueError(f"Invalid stackRendering mode: {mode}. Must be one of: topOnly, offset")
        
        maxVisible = stackRendering.get("maxVisible", 5)
        if not isinstance(maxVisible, int) or maxVisible < 1:
            raise ValueError(f"stackRendering maxVisible must be a positive integer, got: {maxVisible}")
        
        offset = stackRendering.get("offset", 3)
        if not isinstance(offset, (int, float)) or offset < 0:
            raise ValueError(f"stackRendering offset must be a non-negative number, got: {offset}")
        
        showCounter = stackRendering.get("showCounter", False)
        if not isinstance(showCounter, bool):
            raise ValueError(f"stackRendering showCounter must be a boolean, got: {showCounter}")
        
        counterPosition = stackRendering.get("counterPosition", "topRight")
        valid_positions = ["topRight", "topLeft", "bottomRight", "bottomLeft", "center"]
        if counterPosition not in valid_positions:
            raise ValueError(f"stackRendering counterPosition must be one of {valid_positions}, got: {counterPosition}")
        
        # Pass colorForLegend=None to let SGTileType determine it dynamically from defaultFace
        # If colorForLegend is explicitly provided, it will be used (for custom legend colors)
        # Otherwise, SGTileType will use the color of defaultFace (frontColor or backColor)
        aTileType = SGTileType(self, name, shape, defaultSize, entDefAttributesAndValues, colorForLegend,
                              positionOnCell, defaultFace, frontImage, backImage, frontColor, backColor,
                              stackRendering)
        self.tileTypes[name] = aTileType
        return aTileType
    


    # To create a player
    def newPlayer(self, name,attributesAndValues=None):
        """"
        Create a new player

        Args:
            name (str) : name of the Player (will be displayed)
        """
        player = SGPlayer(self, name,attributesAndValues=attributesAndValues)
        
        # Auto-filter if distributed mode
        if self.isDistributed():
            assigned_player_name = self.distributedConfig.assigned_player_name
            
            if name != assigned_player_name:
                # This is a remote player (exists but not controlled here)
                player.isRemote = True
            else:
                # This is the assigned player for this instance
                player.isRemote = False
        
        self.players[name] = player
        self.users.append(player.name)
        return player

    # to create a new play phase
    def newPlayPhase(self, phaseName, activePlayers=None, modelActions=[], authorizedActions=None, autoForwardWhenAllActionsUsed=False, message_auto_forward=True, show_message_box_at_start=False):
        """
        Create a new play phase for the game.
        
        Args:
            phaseName (str): Name of the phase
            activePlayers (list): List of players active in this phase. Can contain:
                - Player instances (SGPlayer objects)
                - Player names (str) - will be automatically converted to instances
                - 'Admin' (str) - will be converted to the Admin player instance
                - None (default:all users)
            modelActions (list, optional): Actions the model performs at the beginning of the phase (add, delete, move...)
                - SGModelAction objects
                - lambda functions
                - list of SGModelAction objects or lambda functions
            authorizedActions (list, optional): List of game actions authorized in this phase. Can contain:
                - None (default): all actions are allowed
                - []: no actions are allowed
                - [action1, action2, ...]: only these actions are allowed
            autoForwardWhenAllActionsUsed (bool, optional): Whether to automatically forward to next phase when all players have used their actions
                - False (default): the phase will not be executed automatically when all players have used their actions
                - True: the phase will be executed automatically when all players have used their actions
            message_auto_forward (bool, optional): Whether to show a message when automatically forwarding to the next phase
                - True (default): a message will be displayed when auto-forwarding
                - False: no message will be displayed when auto-forwarding
            show_message_box_at_start (bool, optional): Whether to show a message box at the start of the phase
                - False (default): no message box will be shown at the start of the phase
                - True: a message box will be shown at the start of the phase
                
            
        Returns:
            The created play phase (an instance of SGPlayPhase)
        """
        return self.timeManager.newPlayPhase(phaseName, activePlayers, modelActions, authorizedActions, autoForwardWhenAllActionsUsed, message_auto_forward, show_message_box_at_start)


    # To create game actions

    def newCreateAction(self, entity_type, dictAttributes=None, uses_per_round='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[], label=None, create_several_at_each_click=False, writeAttributeInLabel=False, action_controler=None):
        """
        Add a Create GameAction to the game.

        Args:
        - entity_type : a type of entity (agentType, cellType or name of the entity type)
        - uses_per_round (int) : number of uses per round, could use "infinite"
        - dictAttributes (dict) : attribute with value concerned, could be None
        - label (str): custom label to display
        - create_several_at_each_click (bool): whether to create several entities at each click
        - writeAttributeInLabel (bool): whether to show attribute in label
        - action_controler (dict): Interaction modes configuration (controlPanel, contextMenu, directClick)

        """
        aType = self.getEntityType(entity_type)
        if aType is None : raise ValueError('Wrong format of entityDef')
        return SGCreate(aType, dictAttributes, uses_per_round, conditions, feedbacks, conditionsOfFeedback, label=label, create_several_at_each_click=create_several_at_each_click, writeAttributeInLabel=writeAttributeInLabel, action_controler=action_controler)

    def newModifyAction(self, entity_type, dictAttributes={}, uses_per_round='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[], label=None, writeAttributeInLabel=False, action_controler=None):
        """
        Add a Modify GameAction to the game.

        Args:
        - entity_type : a type of entity (agentType, cellType or name of the entity type)
        - uses_per_round (int) : number of uses per round, could use "infinite"
        - dictAttributes (dict) : attribute with value concerned, could be None
        - label (str): custom label to display
        - writeAttributeInLabel (bool): whether to show attribute in label
        - action_controler (dict): Interaction modes configuration (controlPanel, contextMenu, directClick)

        """
        aType = self.getEntityType(entity_type)
        if aType is None : raise ValueError('Wrong format of entityDef')
        return SGModify(aType, dictAttributes, uses_per_round, conditions, feedbacks, conditionsOfFeedback, label=label, writeAttributeInLabel=writeAttributeInLabel, action_controler=action_controler)

    def newModifyActionWithDialog(self, entity_type, attribute, uses_per_round='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[], label=None, writeAttributeInLabel=False, action_controler=None):
        """
        Add a Modify GameAction to the game that opens a dialog to ask for the value to use.
        
        Args:
            entity_type : a type of entity (agentType, cellType or name of the entity type)
            attribute (str): the attribute to modify
            uses_per_round (int): number of uses per round, could use "infinite"
            conditions (list): conditions that must be met
            feedbacks (list): actions to execute after modification
            conditionsOfFeedback (list): conditions for feedback execution
            label (str): custom label to display
            writeAttributeInLabel (bool): whether to show attribute in label
            action_controler (dict): Interaction modes configuration (controlPanel, contextMenu, directClick)
        """
        aType = self.getEntityType(entity_type)
        if aType is None:
            raise ValueError('Wrong format of entityDef')
        
        from mainClasses.gameAction.SGModify import SGModifyActionWithDialog
        return SGModifyActionWithDialog(aType, attribute, uses_per_round, conditions, feedbacks, conditionsOfFeedback, label=label, action_controler=action_controler, writeAttributeInLabel=writeAttributeInLabel)

    def newDeleteAction(self, entity_type, uses_per_round='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[], label=None, action_controler=None):
        """
        Add a Delete GameAction to the game.

        Args:
        - entity_type : a type of entity (agentType, cellType or name of the entity type)
        - uses_per_round (int) : number of uses per round, could use "infinite"
        - label (str): custom label to display
        - action_controler (dict): Interaction modes configuration (controlPanel, contextMenu, directClick)

        """
        aType = self.getEntityType(entity_type)
        if aType is None : raise ValueError('Wrong format of entityDef')
        return SGDelete(aType, uses_per_round, conditions, feedbacks, conditionsOfFeedback, label=label, action_controler=action_controler)

    def newMoveAction(self, agent_type, uses_per_round='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[], feedbacksAgent=[], conditionsOfFeedBackAgent=[], label=None, action_controler=None):
        """
        Add a MoveAction to the game.

        Args:
        - agent_type : a type of agent (agentType or name of the agent type)
        - uses_per_round (int) : number of uses per round, could use "infinite"
        - conditions (list of lambda functions) : conditions on the moving Entity
        - feedbacks (list): feedback actions
        - conditionsOfFeedback (list): conditions for feedback execution
        - feedbacksAgent (list): agent feedback actions
        - conditionsOfFeedBackAgent (list): conditions for agent feedback execution
        - label (str): custom label to display
        - action_controler (dict): Interaction modes configuration (controlPanel, contextMenu, directClick)
        """
        aType = self.getEntityType(agent_type)
        if aType is None : raise ValueError('Wrong format of entityDef')
        return SGMove(aType, uses_per_round, conditions, feedbacks, conditionsOfFeedback, feedbacksAgent, conditionsOfFeedBackAgent, label=label, action_controler=action_controler)

    def newFlipAction(self, tile_type, uses_per_round='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[], label=None, action_controler=None):
        """
        Create a new Flip action for tiles
        
        Args:
            tile_type: The tile type (SGTileType) to flip
            uses_per_round: Number of times the action can be used per round (default: 'infinite')
            conditions: List of conditions that must be met
            feedbacks: List of feedback actions
            conditionsOfFeedback: List of conditions for feedbacks
            label: Custom label to display (default: "🔄 Flip")
            action_controler (dict): Interaction modes configuration (controlPanel, contextMenu, directClick)
            
        Returns:
            SGFlip: The created flip action
        """
        from mainClasses.gameAction.SGFlip import SGFlip
        aFlipAction = SGFlip(tile_type, uses_per_round, conditions, feedbacks, conditionsOfFeedback, label=label, action_controler=action_controler)
        return aFlipAction

    def newActivateAction(self, object_type=None, method=None, uses_per_round='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[], label=None, action_controler=None):
        """Add a ActivateAction to the game
        Args:
        - object_type : the model itself or a type of entity (agentType, cellType or name of the entity type)
        - method (lambda function) : the method to activate
        - uses_per_round (int) : number of uses per round, could use "infinite"
        - conditions (list of lambda functions) : conditions on the activating entity
        - feedbacks (list of lambda functions) : feedbacks to execute after activation
        - conditionsOfFeedback (list of lambda functions) : conditions for feedback execution
        - label (str) : custom label to display
        - action_controler (dict): Interaction modes configuration (controlPanel, contextMenu, button, directClick)
            - button (bool): whether to create a button
            - buttonPosition (tuple, optional): coordinates of the button to set in the controller. If button=True but buttonPosition is not specified, a default position (50, 50) will be used.
        """
        #Case for action on the model
        if object_type is None or object_type == self:
            aType = self
        else:
            #Case for action on a Entity
            aType = self.getEntityType(object_type)

        # Handle button creation from action_controler
        if action_controler is None:
            action_controler = {}

        aActivateAction = SGActivate(aType, method, uses_per_round, conditions, feedbacks, conditionsOfFeedback, label=label, action_controler=action_controler)

        # Create button if specified
        if action_controler.get("button", False):
            # Use provided buttonPosition or default to (50, 50)
            buttonCoord = action_controler.get("buttonPosition", (50, 50))
            self.newButton(aActivateAction, aActivateAction.nameToDisplay, buttonCoord)
        
        return aActivateAction

    # To create a new model phase
    def newModelPhase(self, actions=None, condition=None, name='', auto_forward=False, message_auto_forward=True, show_message_box_at_start=False):
        """
        Create a new model phase for the game.
        
        Args:
            actions (SGModelAction, lambda function, or list of SGModelAction/lambda function, optional):
                The action(s) to be executed during the phase. Can be a single SGModelAction, a lambda function,
                or a list of either.
            condition (lambda function, optional):
                A function returning a boolean. Actions are performed only if this function returns True.
            name (str, optional):
                Name displayed on the TimeLabel.
            auto_forward (bool, optional):
                If True, this phase will be executed automatically. Default is False.
            message_auto_forward (bool, optional):
                If True, a message will be displayed when auto-forwarding. Default is True.
            show_message_box_at_start (bool, optional):
                If True, a message box will be shown at the start of the phase. Default is False.
            
        Returns:
            SGTimePhase: The created time phase
        """
        return self.timeManager.newModelPhase(actions, condition, name, auto_forward, message_auto_forward, show_message_box_at_start)

    # To create a modelAction
    def newModelAction(self, actions=[], conditions=[], feedbacks=[]):

        """
        To add a model action which can be executed during a modelPhase
        args:
            actions (lambda function): Actions the model performs during the phase (add, delete, move...)
            conditions (lambda function): Actions are performed only if the condition returns true  
            feedbacks (lambda function): feedback actions performed only if the actions are executed
        """
        aModelAction = SGModelAction(self,actions, conditions, feedbacks)
        self.id_modelActions += 1
        aModelAction.id = self.id_modelActions
        return aModelAction
    
    # To create a modelAction that executes on each cell
    def newModelAction_onCells(self, actions=[], conditions=[], feedbacks=[]):
        """
        To add a model action which can be executed during a modelPhase
        args:
            actions (lambda function): Actions the cell performs during the phase (add, delete, move...)
            conditions (lambda function): Actions are performed only if the condition returns true  
            feedbacks (lambda function): feedback actions performed only if the actions are executed
        """
        aModelAction = SGModelAction_OnEntities(self,actions, conditions, feedbacks,(lambda:self.getCells()))
        self.id_modelActions += 1
        aModelAction.id = self.id_modelActions
        return aModelAction
    
    # To create a modelAction that executes on each agent of a specific Specie
    def newModelAction_onAgents(self, specieName, actions=[], conditions=[], feedbacks=[]):
        """
        To add a model action which can be executed during a modelPhase
        args:
            actions (lambda function): Actions the agent performs during the phase (add, delete, move...)
            conditions (lambda function): Actions are performed only if the condition returns true  
            feedbacks (lambda function): feedback actions performed only if the actions are executed
        """
        specieName = normalize_type_name(specieName)
        aModelAction = SGModelAction_OnEntities(self,actions, conditions, feedbacks,(lambda:self.getAgentsOfType(specieName)))
        self.id_modelActions += 1
        aModelAction.id = self.id_modelActions
        return aModelAction

    # To create a new simulation variable
    def newSimVariable(self,name,initValue,color=Qt.black,isDisplay=True):
        aSimVar=SGSimulationVariable(self,initValue,name,color,isDisplay)
        self.simulationVariables.append(aSimVar)
        return aSimVar

# ============================================================================
# DISTRIBUTED GAME METHODS
# ============================================================================

    def enableDistributedGame(self,
                             num_players,
                             session_id=None,
                             shared_seed=None,
                             broker_host="localhost",
                             broker_port=1883,
                             mqtt_update_type="Instantaneous",
                             seed_sync_timeout=1.0):
        """
        Enable distributed multiplayer game mode.
        Opens minimal dialog for user to connect to broker and synchronize seed.
        Player selection happens later in completeDistributedGameSetup().
        
        IMPORTANT: Call this method BEFORE any random operations in your model script.
        The seed will be synchronized and applied immediately after this call returns.
        
        Args:
            num_players (int or tuple): Number of players. Can be:
                - int: Fixed number of players (e.g., 2)
                - tuple: Range of players (min, max) (e.g., (2, 4) for 2-4 players)
                Game can start when number of connected instances is within this range.
            session_id (str, optional): Session ID. Auto-generated if None.
            shared_seed (int, optional): Shared seed. Auto-generated and synced if None.
            broker_host (str): MQTT broker host (default: "localhost")
            broker_port (int): MQTT broker port (default: 1883)
            mqtt_update_type (str): "Instantaneous" or "Phase" (default: "Instantaneous")
            seed_sync_timeout (float, optional): Timeout in seconds to wait for existing seed 
                before becoming leader (default: 1.0). Increase this value if you need more time 
                to detect an existing seed from other instances.
        
        Returns:
            SGDistributedGameConfig or None: Configuration object if distributed mode enabled,
                                             None if cancelled or local mode.
        """
        # Create configuration
        config = SGDistributedGameConfig()
        config.set_num_players(num_players)
        config.broker_host = broker_host
        config.broker_port = broker_port
        config.mqtt_update_type = mqtt_update_type
        config.seed_sync_timeout = seed_sync_timeout
        
        # Generate session_id if not provided
        if session_id is None:
            config.generate_session_id()
        else:
            config.session_id = session_id
        
        # Store shared_seed if provided (will be synced later)
        if shared_seed is not None:
            config.shared_seed = shared_seed
        
        # Create session manager
        session_manager = SGDistributedSessionManager(self, self.mqttManager)
        
        # Open minimal dialog for connection and seed sync (NO player selection)
        from mainClasses.SGDistributedConnectionDialog import SGDistributedConnectionDialog
        dialog = SGDistributedConnectionDialog(self, config, self, session_manager)
        
        if dialog.exec_() == QDialog.Accepted:
            # Seed is already synchronized and applied by the dialog
            # Store references for later use in completeDistributedGameSetup()
            self.distributedConfig = config
            self.distributedSessionManager = session_manager
            
            return config
        else:
            # User cancelled
            return None
    
    def completeDistributedGameSetup(self):
        """
        Complete distributed game setup by selecting assigned player and registering on MQTT.
        This method should be called from initAfterOpening() after the main window is shown.
        
        Opens dialog for user to select assigned_player, registers player on MQTT,
        and opens connection status widget.
        
        Returns:
            bool: True if setup completed successfully, False if cancelled or not in distributed mode
        """
        if not self.isDistributed():
            return False
        
        config = self.distributedConfig
        session_manager = self.distributedSessionManager
        
        # Open dialog for user to select player
        from mainClasses.SGDistributedGameDialog import SGDistributedGameDialog
        dialog = SGDistributedGameDialog(self, config, self, session_manager)
        
        if dialog.exec_() == QDialog.Accepted:
            # User confirmed - get selected player
            assigned_player_name = dialog.getSelectedPlayerName()
            
            if not assigned_player_name:
                return False
            
            config.assigned_player_name = assigned_player_name
            
            # Update visibility for all GameSpaces now that assigned_player_name is set
            # This ensures that GameSpaces configured with setVisibilityForPlayers()
            # before assigned_player_name was set will now have correct visibility
            for gameSpace in self.gameSpaces.values():
                if hasattr(gameSpace, '_updateVisibility'):
                    gameSpace._updateVisibility()
            
            # Register player on MQTT
            session_manager.registerPlayer(
                config.session_id,
                assigned_player_name,
                config.num_players_min,
                config.num_players_max
            )
            
            # Open connection status widget
            from mainClasses.SGConnectionStatusWidget import SGConnectionStatusWidget
            connection_widget = SGConnectionStatusWidget(
                None,  # Separate window
                self,
                config,
                session_manager
            )
            connection_widget.show()
            
            # Store reference
            self.connectionStatusWidget = connection_widget
            
            return True
        else:
            # User cancelled
            return False

# ============================================================================
# NEW GAME SPACES (apart from grids)
# ============================================================================

    # To create a new dashboard
    def newDashBoard(self, title=None, borderColor=Qt.black, borderSize=1, backgroundColor=QColor(230, 230, 230), textColor=Qt.black, layout ='vertical'):
        """  Qt.lightGray
        Create the score board of the game

        Args:
        title (str) : title of the widget (default:"Phases&Rounds")
        backgroundColor (Qt Color) : color of the background (default : Qt.transparent)
        borderColor (Qt Color, default very light gray) : color of the border (default : Qt.black)
        textColor (Qt Color) : color of the text (default : Qt.black)
        """
        # Create with default values (will be overridden by setters below)
        aDashBoard = SGDashBoard(self, title, Qt.black, 1, QColor(230, 230, 230), Qt.black, layout)
        self.gameSpaces[aDashBoard.id] = aDashBoard
        
        # Apply styles via modeler methods (ensures everything goes through gs_aspect)
        aDashBoard.setBackgroundColor(backgroundColor)
        aDashBoard.setBorderColor(borderColor)
        aDashBoard.setBorderSize(borderSize)
        aDashBoard.setTextColor(textColor)

        # add the gamespace to the layout
        self.layoutOfModel.addGameSpace(aDashBoard)

        return aDashBoard

    # To create a new end game rule
    def newEndGameRule(self, title='EndGame Rules', numberRequired=1, displayRefresh='instantaneous', isDisplay=True, borderColor=Qt.black, backgroundColor=Qt.lightGray, layout="vertical", textColor=Qt.black):
        """
        Create the EndGame Rule Board of the game

        Args:
            title (str) : header of the board, displayed (default : EndGame Rules)
            numberRequired (int) : number of completed conditions to trigger EndGame
            displayRefresh (str) : refresh mode (default : instantaneous)
            isDisplay (bool) : whether to display (default : True)
            borderColor (QColor) : border color (default : Qt.black)
            backgroundColor (QColor) : background color (default : Qt.lightGray)
            layout (str) : layout orientation (default : vertical)
            textColor (QColor) : text color (default : Qt.black)
        """
        # Create with default values (will be overridden by setters below)
        aEndGameRule = SGEndGameRule(self, title, numberRequired, displayRefresh, isDisplay)
        self.gameSpaces[title] = aEndGameRule
        self.endGameRule = aEndGameRule

        # Apply styles via modeler methods (ensures everything goes through gs_aspect)
        aEndGameRule.setBackgroundColor(backgroundColor)
        aEndGameRule.setBorderColor(borderColor)
        aEndGameRule.setTextColor(textColor)

        # add the gamespace to the layout
        self.layoutOfModel.addGameSpace(aEndGameRule)

        return aEndGameRule

    # To create a new void widget
    def newVoid(self, name, sizeX=200, sizeY=200):
        """
        Create a void widget for layout management.

        Args:
            name (str): Name of the void widget
            sizeX (int): Width in pixels (default: 200)
            sizeY (int): Height in pixels (default: 200)
        """
        aVoid = SGVoid(self, name, sizeX, sizeY)
        self.gameSpaces[name] = aVoid

        # add the gamespace to the layout
        self.layoutOfModel.addGameSpace(aVoid)

        return aVoid

    
    # To create a new progress gauge
    def newProgressGauge(self,simVar,minimum=0,maximum=100, title=None,orientation="horizontal",colorRanges=None,unit="",
                         borderColor=Qt.black,backgroundColor=Qt.white,bar_width=25,bar_length=None,title_position='above',display_value_on_top=True
    ):
        """
        Create a progress gauge widget for monitoring simulation variables.
        This widget displays a progress bar (horizontal or vertical) that reflects the value of 
        a linked simulation variable.
        The gauge can also trigger callbacks when specific thresholds are crossed.
        It supports optional titles, value labels, units, color ranges for dynamic coloring, and custom sizes.

        Args:
            simVar (object): The simulation variable to be monitored.
            minimum (float or int, optional): Minimum value of the gauge. Defaults to 0.
            maximum (float or int, optional): Maximum value of the gauge. Defaults to 100.
            title (str, optional): The displayed title of the gauge. Defaults to None.
            orientation (str, optional): Either 'horizontal' or 'vertical'. Defaults to 'horizontal'.
            colorRanges (list of tuple, optional): Each tuple is 
                (min_value, max_value, css_color_string) defining dynamic color rules.
            unit (str, optional): Unit string to display next to the value. Defaults to "".
            borderColor (QColor or Qt.GlobalColor, optional): The border color of the gauge widget. Defaults to Qt.black.
            backgroundColor (QColor or Qt.GlobalColor, optional): The background color of the gauge widget. Defaults to Qt.white.
            bar_width (int, float, or str, optional): Width of the progress bar in pixels, or "fit title size" for vertical mode. Defaults to 25.
            bar_length (int, optional): Length of the progress bar in pixels. Defaults to 180 for horizontal and 160 for vertical.
            title_position (str, optional): "above" or "below" the gauge. Defaults to "above".
            display_value_on_top (bool, optional): Whether to display the numeric value on top of the progress bar. Defaults to True.

        methods:
            setThresholdValue(value, on_up=None, on_down=None):
                Allow to define callbacks to execute when a value threshold is crossed.
                ex. aGauge1.setThresholdValue(8, on_up= lambda: print("⚠️ Surchauffe détectée !"))
                ex. aGauge2.setThresholdValue(2, on_down= lambda: myAgents.moveRandomly()))
        Returns:
            SGProgressGauge: The created SGProgressGauge instance.
        """

        # Create the ProgressGauge with default style values (will be overridden by setters below)
        aProgressGauge = SGProgressGauge(
            parent=self,
            simVar=simVar,
            min_value=minimum,
            max_value=maximum,
            title=title,
            orientation=orientation,
            colorRanges=colorRanges,
            unit=unit,
            bar_width=bar_width,
            bar_length=bar_length,
            title_position=title_position,
            display_value_on_top=display_value_on_top
        )
        
        # Apply styles via modeler methods (ensures everything goes through gs_aspect)
        aProgressGauge.setBackgroundColor(backgroundColor)
        aProgressGauge.setBorderColor(borderColor)
        
        # Register the gauge in the model
        self.gameSpaces[title] = aProgressGauge

        # add the gamespace to the layout
        self.layoutOfModel.addGameSpace(aProgressGauge)

        # Initial refresh
        aProgressGauge.checkAndUpdate()

        return aProgressGauge



    # To create a Legend
    def newLegend(self, name='Legend', alwaysDisplayDefaultAgentSymbology=False):#, grid=None):
        """
        To create an Admin Legend (with all the cell and agent values)

        Args:
        Name (str): name of the Legend (default : Legend)
        alwaysDisplayDefaultAgentSymbology (bool) : display default symbology of agent, even if agents with attribute symbologies are shown (default : False)
        grid (str) : name of the grid or None (select the first grid) or "combined"

        """
        # selectedSymbologies=self.getAllCheckedSymbologies(grid)
        selectedSymbologies=self.getAllCheckedSymbologies()
        aLegend = SGLegend(self).initialize(self, name, selectedSymbologies, alwaysDisplayDefaultAgentSymbology)
        self.gameSpaces[name] = aLegend

        # add the gamespace to the layout
        self.layoutOfModel.addGameSpace(aLegend)

        return aLegend

    # To create a new user selector
    def newUserSelector(self, customListOfUsers=None, orientation='horizontal'):
        """
        To create a User Selector in your game. Functions automatically with the players declared in your model.
        
        Args:
            customListOfUsers(list, optional) : a custom list of users to be used instead of the automatic list generated by the model.
            orientation(str, optional) : layout orientation - 'horizontal' (default) or 'vertical'.
        """
        if customListOfUsers or (len(self.getUsers_withControlPanel()) > 1 and len(self.players) > 0):
            usersList = customListOfUsers if customListOfUsers else self.getUsers_withControlPanel()
            userSelector = SGUserSelector(self, usersList, orientation)
            # userSelector = SGUserSelector(self, self.getUsers_withControlPanel())
            self.userSelector = userSelector
            self.gameSpaces["userSelector"] = userSelector

            # add the gamespace to the layout
            self.layoutOfModel.addGameSpace(userSelector)
           
            return userSelector
        else:
            print(  f"The userSelector was not created because: \n"
                    f"  - nb of players : {len(self.players)} ({[player.name for player in self.players.values()]}). \n"
                    f"  - nb of users with control panel: {len(self.getUsers_withControlPanel())} ({[userName for userName in self.getUsers_withControlPanel()]}). \n"
                    f"  - you need to add more users with control panel for the userSelector to be created"
                )

        
    # To create a Time Label
    def newTimeLabel(self, title=None, backgroundColor=Qt.white, borderColor=Qt.black, textColor=Qt.black,
                     roundNumberFormat="Round Number : {roundNumber}",
                     phaseNumberFormat="Phase Number : {phaseNumber}",
                     phaseNameFormat="{phaseName}",
                     displayRoundNumber=None,
                     displayPhaseNumber=None,
                     displayPhaseName=None):
        """
        Create the visual time board of the game.
        
        Args:
            title (str): Name of the widget (default: None)
            backgroundColor (Qt Color): Color of the background (default: Qt.white)
            borderColor (Qt Color): Color of the border (default: Qt.black)
            textColor (Qt Color): Color of the text (default: Qt.black)
            roundNumberFormat (str): Format template for round number display.
                                    Use placeholders: {roundNumber}, {phaseNumber}, {phaseName}
                                    (default: "Round Number : {roundNumber}")
            phaseNumberFormat (str): Format template for phase number display.
                                     Use placeholders: {roundNumber}, {phaseNumber}, {phaseName}
                                     (default: "Phase Number : {phaseNumber}")
            phaseNameFormat (str): Format template for phase name display.
                                   Use placeholders: {roundNumber}, {phaseNumber}, {phaseName}
                                   (default: "{phaseName}")
            displayRoundNumber (bool): Whether to display the round number label.
                                       If None, defaults to True.
                                       If format is empty/None, defaults to False.
            displayPhaseNumber (bool): Whether to display the phase number label.
                                       If None, defaults to True if numberOfPhases() >= 2, else False.
                                       If format is empty/None, defaults to False.
            displayPhaseName (bool): Whether to display the phase name label.
                                     If None, defaults to True if numberOfPhases() >= 2, else False.
                                     If format is empty/None, defaults to False.
        """
        # Create with all parameters
        aTimeLabel = SGTimeLabel(self, title, backgroundColor, borderColor, textColor,
                                 roundNumberFormat, phaseNumberFormat, phaseNameFormat,
                                 displayRoundNumber, displayPhaseNumber, displayPhaseName)
        self.myTimeLabel = aTimeLabel
        self.gameSpaces[title] = aTimeLabel

        # Apply styles via modeler methods (ensures everything goes through gs_aspect)
        aTimeLabel.setBackgroundColor(backgroundColor)
        aTimeLabel.setBorderColor(borderColor)
        aTimeLabel.setTextColor(textColor)

        # add the gamespace to the layout
        self.layoutOfModel.addGameSpace(aTimeLabel)

        return aTimeLabel

    # To create a Text Box
    def newTextBox(self, textToWrite='', title='Text Box', width=None, height=None,
     borderColor=Qt.black, backgroundColor=Qt.lightGray, titleAlignment='left', shrinked=True, chronologicalOrder=True):
        """
        Create a text box with full customization options.

        Args:
            textToWrite (str): Displayed text in the widget (default: "Welcome in the game!")
            title (str): Name of the widget (default: "Text Box")
            width (int, optional): Width of the text box in pixels
            height (int, optional): Height of the text box in pixels
            borderColor (QColor): Border color of the text box (default: Qt.black)
            backgroundColor (QColor): Background color of the text box (default: Qt.lightGray)
            titleAlignment (str): Title alignment - 'left', 'center', or 'right' (default: 'left')
            shrinked (bool, optional): If True, the text box will be shrinked to fit content (default: True)
            chronologicalOrder (bool, optional): If True (default), new text is added at the bottom (chronological order).
                If False, new text is added at the top (reverse chronological order, newest first).

        Returns:
            SGTextBox: The created text box widget
        """
        
        # Create with default style values (will be overridden by setters below)
        aTextBox = SGTextBox(self, textToWrite, title, width, height, shrinked, Qt.black, Qt.lightGray, titleAlignment, chronologicalOrder)
        self.TextBoxes.append(aTextBox)
        self.gameSpaces[title] = aTextBox

        # Apply styles via modeler methods (ensures everything goes through gs_aspect)
        aTextBox.setBackgroundColor(backgroundColor)
        aTextBox.setBorderColor(borderColor)

        # add the gamespace to the layout
        self.layoutOfModel.addGameSpace(aTextBox)

        return aTextBox

     
    # To create a Text Box
    def newLabel(self, text, position=None, textStyle_specs="", borderStyle_specs="", backgroundColor_specs="", alignement="Left", fixedWidth=None, fixedHeight=None):
        """Display a text at a given position

        Args:
            text (str): The text to display.
            position (tuple): Coordinates (x, y) of the position of the text.
            textStyle_specs (str, optional): CSS-like specifications for the text style (font, size, color, etc.).
            borderStyle_specs (str, optional): CSS-like specifications for the border style (size, color, type).
            backgroundColor_specs (str, optional): CSS-like specifications for the background color.
            alignement (str, optional): Text alignment. Options include "Left", "Right", "HCenter", "Top", "Bottom", "VCenter", "Center", "Justify".
            fixedWidth (float, optional): Fixed width of the label in pixels. If specified, word wrap will be used in case the text is too long.
            fixedHeight (float, optional): Fixed height of the widget in pixels. If specified, the widget will have a fixed height and will not resize.

        Returns:
            SGLabel: An instance of SGLabel with the specified properties.
        """
        aLabel = SGLabel(self, text, textStyle_specs, borderStyle_specs, backgroundColor_specs, alignement, fixedWidth, fixedHeight)
        self.gameSpaces[aLabel.id] = aLabel
        self.layoutOfModel.addGameSpace(aLabel)
        if position: aLabel.moveToCoords(position[0], position[1])
        return aLabel

    # To create a new styled label
    def newLabel_stylised(self, text, position, font=None, size=None, color=None, text_decoration="none", font_weight="normal", font_style="normal", alignement= "Left", border_style="solid", border_size=0, border_color=None, background_color=None, fixedWidth=None, fixedHeight=None):
        #todo: could be obsolete since newLabel method has been plugged to the game spaces system
        """Display a text at a given position and allow setting the style of the text, border, and background.

        Args:
            text (str): The text to display.
            position (tuple): Coordinates (x, y) of the position of the text.
            font (str, optional): Font family. Options include "Times New Roman", "Georgia", "Garamond", "Baskerville", "Arial", "Helvetica", "Verdana", "Tahoma", "Trebuchet MS", "Courier New", "Lucida Console", "Monaco", "Consolas", "Comic Sans MS", "Papyrus", "Impact".
            size (int, optional): Font size in pixels.
            color (str, optional): Text color. Can be specified by name (e.g., "red", "orange", "navy", "gold"), hex code (e.g., "#FF0000", "#AB28F9"), RGB values (e.g., "rgb(127, 12, 0)"), or RGBA values for transparency (e.g., "rgba(154, 20, 8, 0.5)").
            text_decoration (str, optional): Text decoration style. Options include "none", "underline", "overline", "line-through", "blink".
            font_weight (str, optional): Font weight. Options include "normal", "bold", "bolder", "lighter", "100", "200", "300", "400", "500", "600", "700", "800", "900".
            font_style (str, optional): Font style. Options include "normal", "italic", "oblique".
            alignement (str, optional): Text alignment. Options include "Left", "Right, "HCenter", "Top", "Bottom", "VCenter", "Center", "Justify".
            border_style (str, optional): Border style. Options include "solid", "dotted", "dashed", "double", "groove", "ridge", "inset".
            border_size (int, optional): Border size in pixels.
            border_color (str, optional): Same options as color.
            background_color (str, optional): Same options as color.
            fixedWidth (float, optional): Fixed width of the label in pixels. If specified, word wrap will be used in case the text is too long.
            fixedHeight (float, optional): Fixed height of the widget in pixels.
        """
        # Create the text style
        text_specs = f"font-family: {font}; font-size: {size}px; color: {color}; text-decoration: {text_decoration}; font-weight: {font_weight}; font-style: {font_style};"
        
        # Create the border style
        border_specs = f"border: {border_size}px {border_style} {border_color};"
        
        # Create the background style
        background_specs = f"background-color: {background_color};"
        
        # Call the newLabel method with the created styles
        aLabel = self.newLabel(text, position, text_specs, border_specs, background_specs, alignement, fixedWidth, fixedHeight)
        return aLabel
    
    # To create a Push Button
    def newButton(self, method, text, position=None,
                    background_color='white',
                    background_image=None,
                    border_size=1,
                    border_color='lightgray',
                    border_style='solid',
                    border_radius=5,
                    text_color=None,
                    font_family=None,
                    font_size=None,
                    font_weight=None,
                    min_width=None,
                    min_height=None,
                    padding=2,
                    hover_text_color= None,
                    hover_background_color= '#c6eff7',
                    hover_border_color= '#6bd8ed',
                    pressed_color=None,
                    disabled_color=None,
                    word_wrap=False,
                    fixed_width=None):
        """Display a button with customizable style.
        Args:
            method (lambda function | SGAbstractAction ): Method to execute when button is pressed 
                - lambda function : une fonction/méthode appelée telle quelle
                - SGAbstractAction: l'action est exécutée via perform_with
            text (str): Text of the button
            position (tuple): Coordinates (x, y) of the button position
            background_color (str, optional): Background color. Can be name (e.g., "red"), hex (#FF0000), RGB (rgb(127,12,0)) or RGBA
            background_image (str, optional): Path to background image
            border_size (int, optional): Border size in pixels
            border_color (str, optional): Border color. Same format as background_color
            border_style (str, optional): Border style. Options include "solid", "dotted", "dashed", "double", "groove", "ridge", "inset".
            border_radius (int, optional): Border radius in pixels for rounded corners
            text_color (str, optional): Text color. Same format as background_color
            font_family (str, optional): Font family (e.g., "Arial", "Times New Roman", "Helvetica")
            font_size (int, optional): Font size in pixels
            font_weight (str, optional): Font weight ("normal", "bold", "100" to "900")
            min_width (int, optional): Minimum button width in pixels
            min_height (int, optional): Minimum button height in pixels
            padding (int, optional): Internal padding in pixels
            hover_color (str, optional): Background color on hover. Same format as background_color
            pressed_color (str, optional): Background color when pressed. Same format as background_color
            disabled_color (str, optional): Background color when disabled. Same format as background_color
        """

        aButton = SGButton(self, method, text,
                        background_color=background_color,
                        background_image=background_image,
                        border_size=border_size,
                        border_style=border_style,
                        border_color=border_color,
                        border_radius=border_radius,
                        text_color=text_color,
                        font_family=font_family,
                        font_size=font_size,
                        font_weight=font_weight,
                        min_width=min_width,
                        min_height=min_height,
                        padding=padding,
                        hover_text_color= hover_text_color,
                        hover_background_color= hover_background_color,
                        hover_border_color= hover_border_color,
                        pressed_color=pressed_color,
                        disabled_color=disabled_color,
                        word_wrap=word_wrap,
                        fixed_width=fixed_width)
        # Enregistrer comme un GameSpace et l'ajouter au layout
        self.gameSpaces[aButton.id] = aButton
        self.layoutOfModel.addGameSpace(aButton)
        if position: aButton.moveToCoords(position[0], position[1])
        return aButton


    # To create a void
    def createVoid(self, name, sizeX=200, sizeY=200):
        # Creation
        aVoid = SGVoid(self, name, sizeX, sizeY)
        self.gameSpaces[name] = aVoid

        # Realocation of the position thanks to the layout
        newPos = self.layoutOfModel.addGameSpace(aVoid)
        aVoid.setStartXBase(newPos[0])
        aVoid.setStartYBase(newPos[1])
        aVoid.move(aVoid.startXBase, aVoid.startYBase)
        return aVoid


    def newWarningPopUp(self,aTitle, aMessage):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(aTitle)
        msg.setText(aMessage)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        return
    
    def newPopUp(self, aTitle, aMessage):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(aTitle)
        msg.setText(aMessage)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        return

# ============================================================================
# SET METHODS
# ============================================================================
    def __MODELER_METHODS__SET__(self):
        pass

        
    def setCurrentPlayer(self, aUserName):
        """
        Set the Active Player at the initialisation

        Args:
            playerName (str): predefined playerName

        """
        if isinstance(aUserName,SGPlayer):
           aUserName = aUserName.name 
        if aUserName in self.getUsersName():
            self.currentPlayerName = aUserName
            #update the userSelector interface
            if self.userSelector is not None:
                self.userSelector.setCheckboxesWithSelection(aUserName)
            #update the ControlPanel and adminControlPanel interfaces
            # Use TimeManager's method to handle control panel activation based on phase type
            if hasattr(self, 'timeManager') and self.timeManager.numberOfPhases() > 0:
                self.timeManager.updateControlPanelsForCurrentPhase()
            else:
                # During initialization or before phases are created, use normal logic
                for aItem in self.getControlPanels():
                    aItem.setActivation(aItem.playerName == self.currentPlayerName)
    

    def set_gameSpaces_draggability(self, all_elements=None, include=None, exclude=None, value=True):
        """
        Met à jour l'état de "draggability" des éléments.
        
        :param all_elements: Si True, applique la valeur à tous les éléments.
        :param include: Liste des éléments spécifiques à modifier.
        :param exclude: Liste des éléments à exclure.
        :param value: Valeur à appliquer (True ou False).
        """
        all_game_spaces = self.gameSpaces.values()


        # Initialize the list of elements to modify
        elements_to_change = set()

        # Add all elements if all_elements is True
        if all_elements:
            elements_to_change.update(all_game_spaces)

        # Add elements specified in include
        if include:
            elements_to_change.update(include)

        # Exclude elements specified in exclude
        if exclude:
            elements_to_change.difference_update(exclude)

        # Update "draggability" for selected elements
        for element in elements_to_change:
            element.setDraggability(value)
# ============================================================================
# GET/NB METHODS
# ============================================================================
    def __MODELER_METHODS__GET__(self):
        pass

    def isDistributed(self):
        """
        Check if distributed game mode is enabled.
        
        Returns:
            bool: True if distributed mode is enabled, False otherwise
        """
        return hasattr(self, 'distributedConfig') and self.distributedConfig is not None

    def roundNumber(self):
        """Return the current ingame round number"""
        return self.timeManager.currentRoundNumber

    def phaseNumber(self):
        """Return the current ingame phase number"""
        return self.timeManager.currentPhaseNumber
    
    def getEntityTypes(self):
        return list(self.cellTypes.values()) + list(self.agentTypes.values()) + list(self.tileTypes.values())

    def getEntityType(self, name):
        if isinstance(name,SGEntityType):
            return name
        detectedType = next((aType for aType in self.getEntityTypes() if aType.name == name), None)
        if detectedType is None:
            existing_entities = [aType.name for aType in self.getEntityTypes()]
            raise ValueError(f"No EntityType found with the name '{name}'. Existing EntityTypes: {', '.join(existing_entities)}")
        return detectedType

    # To get the CellType corresponding to a Grid
    def getCellType(self, aGrid):
        if aGrid.isCellType: return aGrid
        return self.cellTypes[aGrid.id]

    def getAgentTypes(self):
        # send back a list of all the agent types Dict (agent type definition dict)
        return list(self.agentTypes.values())

    def getAgentType(self, aTypeName):
        # send back the agent type dict (agent type definition dict) that corresponds to aTypeName
        return self.agentTypes.get(aTypeName)

    def getAllEntities(self):
        # send back the cells of all the grids and the agents of all types
        aList= []
        for entType in self.cellTypes.values():
            aList.extend(entType.entities)
        for entType in self.getAgentTypes():
            aList.extend(entType.entities)
        return aList
    
    def getAllCells(self):
        # send back the cells of all the grids
        aList= []
        for entType in self.cellTypes.values():
            aList.extend(entType.entities)
        return aList
    
   

    # To get all the cells of the collection
    # If several grids, this method only returns the cells of the first grid
    def getCells(self,grid=None):
        if grid == None:
            grid = self.getGrids()[0]
        return self.getCellType(grid).entities
    
    # To get a cell in particular
    def getCell(self, aGrid, aId):
        result = list(filter(lambda cell: cell.id == aId, self.getCells(aGrid)))
        if len(result)!=1: raise ValueError("No cell with such Id!")
        return result[0]

    def getAllAgents(self):
        # send back the agents of all the types
        aList= []
        for entType in self.getAgentTypes():
            aList.extend(entType.entities)
        return aList

    def getAgentsOfType(self, aTypeName) -> list[SGAgent]:
        agentType = self.getAgentType(aTypeName)
        if agentType is None:  return None
        else: return agentType.entities[:]

    def getGrids(self):
        """Get all grids (gameSpaces that are SGGrid instances)"""
        return [aGameSpace for aGameSpace in list(self.gameSpaces.values()) if isinstance(aGameSpace, SGGrid)]

    def getGrids_withOwner(self, owner):
        """Get all grids that belong to a specific owner
        
        Args:
            owner: A player (SGPlayer instance) or player name (string)
        
        Returns:
            list: List of grids (SGGrid instances) owned by the specified owner
        """
        return [aGrid for aGrid in self.getGrids() if aGrid.isOwnedBy(owner)]
    
    def getGrid_withOwner(self, owner):
        """Get the first grid that belongs to a specific owner
        
        Args:
            owner: A player (SGPlayer instance) or player name (string)
        
        Returns:
            SGGrid or None: The first grid owned by the specified owner, or None if no grid is owned
        """
        grids = self.getGrids_withOwner(owner)
        return grids[0] if grids else None
    
# ============================================================================
# DELETE METHODS
# ============================================================================
    def __MODELER_METHODS__DELETE__(self):
        pass

    def deleteAllAgents(self):
        for aAgentType in self.getAgentTypes():
            aAgentType.deleteAllEntities()


    
# ============================================================================
# DO/DISPLAY METHODS
# ============================================================================
    def __MODELER_METHODS__DO_DISPLAY__(self):
        pass

    def applyThemeConfig(self, config_name: str) -> bool:
        """
        Apply a saved theme configuration to listed GameSpaces.
        
        This method memorizes the configuration name and applies it automatically
        at the end of initBeforeShowing() (called by launch()). This ensures all
        GameSpaces are created before applying themes.
        
        This method is silent (no dialog boxes) and designed for script usage.
        Use the UI dialog "Manage Theme Configurations" for interactive loading.
        
        Args:
            config_name (str): Name of the configuration to apply
        
        Returns:
            bool: True if configuration name was memorized, False otherwise
        
        Example:
            # Apply a saved theme configuration (will be applied when launch() is called)
            model.applyThemeConfig("my_theme_setup")
            model.launch()  # Theme will be applied after all GameSpaces are created
            
            # Check before applying
            if model.hasThemeConfig("setup1"):
                model.applyThemeConfig("setup1")
        """
        # Verify the configuration exists before memorizing
        manager = SGThemeConfigManager(self)
        if not manager.configExists(config_name):
            print(f"Theme config '{config_name}' does not exist")
            return False
        
        # Memorize the configuration name for loading at the end of initBeforeShowing
        self._pending_theme_config = config_name
        return True

    def setShowIconsInContextMenu(self, show=True):
        """
        Set whether to show icons in the context menu.
        
        Args:
            show (bool, optional): If True (default), icons will be displayed in context menus; if False, no icons will be shown.
        
        Example:
            # Disable icons in context menu
            myModel.setShowIconsInContextMenu(False)
        """
        self.showIconsInContextMenu = show
    
    def displayTimeInWindowTitle(self, setting=True):
        """
        Set whether to display the time (Round number and Phase number) in the window title.
        Args:
            setting (bool, optional): If True or not specified, the time will be displayed in the window title; if False, it will not.
        """
        self.isTimeDisplayedInWindowTitle = setting


#****************************************************

    def displayAdminControlPanel(self):
        """
        Display the Admin Control Panel
        """
        self.shouldDisplayAdminControlPanel = True
        if not self.timeManager.isInitialization():
            self.show_adminControlPanel()

    def exportGameActionLogs(self, filename=None, format="csv"):
        """
        Export gameAction logs to file
        
        Args:
            filename (str, optional): Output filename. If None, generates automatic filename
            format (str): Export format - "json" or "csv" (default: "csv")
            
        Returns:
            str: Path to exported file
        """
        if format not in ["json", "csv"]:
            raise ValueError("Format must be 'json' or 'csv'")
        
        # Generate filename if not provided
        if filename is None:
            timestamp = self._getCurrentTimestamp()
            filename = f"gameAction_logs_{timestamp}.{format}"
        
        # Get gameAction logs data
        logs_data = self._getGameActionLogsData()
        
        if format == "json":
            return self._exportGameActionLogsToJSON(logs_data, filename)
        elif format == "csv":
            return self._exportGameActionLogsToCSV(logs_data, filename)
    
    def enableAutoSaveGameActionLogs(self, format="csv", save_path=None):
        """
        Enable automatic saving of gameAction logs when the application is closed.
        
        Args:
            format (str): Export format - "json" or "csv" (default: "csv")
            save_path (str, optional): Directory path where to save the logs. If None, user will be prompted to choose.
        
        Examples:
            # Save automatically to a specific directory
            myModel.enableAutoSaveGameActionLogs(format="csv", save_path="/path/to/logs")
            
            # Save with user choosing the location
            myModel.enableAutoSaveGameActionLogs(format="json")
            
            # Save CSV to current directory
            myModel.enableAutoSaveGameActionLogs(save_path=".")
        """
        if format not in ["json", "csv"]:
            raise ValueError("Format must be 'json' or 'csv'")
        
        # Store both format and save_path in a dictionary
        self.autoSaveGameActionLogs = {
            "format": format,
            "save_path": save_path
        }
        
        if save_path:
            print(f"Auto-save of gameAction logs enabled (format: {format}, path: {save_path})")
        else:
            print(f"Auto-save of gameAction logs enabled (format: {format}, user will choose path)")

    def loadImagesFromDirectory(self, images_directory):
        """
        Load all valid images from a directory.
        Simple helper method for modelers to easily collect images.
        
        Args:
            images_directory (str or Path): Path to directory containing image files
            
        Returns:
            list: List of QPixmap objects (valid images only)
            
        Example:
            # Load images from directory
            images = myModel.loadImagesFromDirectory("./images")
            
            # Use random image for a tile
            import random
            tile = TileType.newTileOnCell(cell, backImage=random.choice(images))
        """
        from pathlib import Path
        from PyQt5.QtGui import QPixmap
        
        # Convert to Path if string
        images_dir = Path(images_directory) if isinstance(images_directory, str) else images_directory
        
        if not images_dir.exists():
            raise ValueError(f"Images directory not found: {images_dir}")
        
        # Load and validate image files (filter out invalid images)
        image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".svg"]
        all_files = []
        for ext in image_extensions:
            all_files.extend(list(images_dir.glob(f"*{ext}")))
            all_files.extend(list(images_dir.glob(f"*{ext.upper()}")))
        
        # Remove duplicates (in case filesystem is case-insensitive like Windows)
        seen_files = set()
        unique_files = []
        for img_file in all_files:
            normalized_path = str(img_file).lower()
            if normalized_path not in seen_files:
                seen_files.add(normalized_path)
                unique_files.append(img_file)
        
        # Validate images by trying to load them
        valid_images = []
        for img_file in sorted(unique_files):
            pixmap = QPixmap(str(img_file))
            if not pixmap.isNull() and pixmap.width() > 0 and pixmap.height() > 0:
                valid_images.append(pixmap)
        
        if len(valid_images) == 0:
            raise ValueError(f"No valid image files found in directory: {images_dir}")
        
        return valid_images


    