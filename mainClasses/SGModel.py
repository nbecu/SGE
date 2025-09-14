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
from PyQt5.QtWidgets import QAction, QMenu, QMainWindow, QMessageBox, QApplication, QActionGroup
from PyQt5 import QtWidgets
from paho.mqtt import client as mqtt_client
from pyrsistent import s
from screeninfo import get_monitors

# --- Project imports ---
from mainClasses.SGAgent import *
from mainClasses.SGCell import *
from mainClasses.SGControlPanel import *
from mainClasses.SGDashBoard import *
from mainClasses.SGDataRecorder import *
from mainClasses.SGEndGameRule import *
from mainClasses.SGEntity import *
from mainClasses.SGEntityView import *
from mainClasses.SGEntityDef import *
from mainClasses.SGGrid import *
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
from mainClasses.SGButton import*
from mainClasses.SGTimeLabel import *
from mainClasses.SGTimeManager import *
from mainClasses.SGTimePhase import *
from mainClasses.SGUserSelector import *
from mainClasses.SGVoid import *
from mainClasses.layout.SGGridLayout import *
from mainClasses.layout.SGHorizontalLayout import *
from mainClasses.layout.SGVerticalLayout import *
from mainClasses.gameAction.SGActivate import *
from mainClasses.gameAction.SGCreate import *
from mainClasses.gameAction.SGDelete import *
from mainClasses.gameAction.SGModify import *
from mainClasses.gameAction.SGMove import *
from mainClasses.SGEventHandlerGuide import *



# By default, use a relative path based on the project structure
path_icon = str(Path(__file__).parent.parent / 'icon')
# Alternative method: uncomment the following line, and use an absolute path
# Example of absolute path: 
# path_icon = '/Users/.../Documents/.../SGE/icon/'

# Mother class of all the SGE System
class SGModel(QMainWindow, SGEventHandlerGuide):

    JsonManagedDataTypes=(dict,list,tuple,str,int,float,bool)

    def __init__(self, width=1800, height=900, typeOfLayout="grid", x=3, y=3, name=None, windowTitle=None, createAdminPlayer=True):
        """
        Declaration of a new model

        Args:
            width (int): width of the main window in pixels (default:1800)
            height (int): height of the main window in pixels (default:900)
            typeOfLayout ("vertical", "horizontal", "grid" or "enhanced_grid"): the type of layout used to position the different graphic elements of the simulation (default:"grid")
            x (int, optional): used for grid and enhanced_grid layouts. defines the number of columns (default:3)
            y (int, optional): used only for grid layout. defines the number layout grid height (default:3)
            name (str, optional): the name of the model. (default:"Simulation")
            windowTitle (str, optional): the title of the main window of the simulation (default:"myGame")
            createAdminPlayer (boolean, optional): Automatically create a Admin player (default:True), that can perform all possible gameActions
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
        # Definition of the title of the window
        self.windowTitle_prefix = (windowTitle or self.name or ' ') # if windowTitle  is None, the name of the model is used as prefix for window title
        self.setWindowTitle(self.windowTitle_prefix)
        # Option to display time (round and phase) in window title
        self.isTimeDisplayedInWindowTitle = False
        
        # We allow the drag in this widget
        self.setAcceptDrops(True)
        # Definition of variable
        # Definition for all gameSpaces
        self.gameSpaces = {}
        self.TextBoxes = []   # Why textBoxes are not in gameSpaces ?
        # list of graphs
        self.openedGraphs = []
        # Definition of the AgentDef and CellDef
        self.agentSpecies = {}
        self.cellOfGrids = {}
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
            self.layoutOfModel = SGEnhancedGridLayout(num_columns=x)
        else:
            self.layoutOfModel = SGGridLayout(x, y)
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

        self.actionsFromBrokerToBeExecuted=[]
        self.simulationVariablesAtMAJ=[] 

        self.dataRecorder=SGDataRecorder(self)

        self.initUI()

        self.initModelActions()
        # self.listData = []



    def initModelActions(self):
        self.id_modelActions = 0

    def initUI(self):
        # Definition of the view through the a widget
        self.window = QtWidgets.QWidget()
        self.layout = QtWidgets.QGridLayout()
        self.setCentralWidget(self.window)
        self.window.setLayout(self.layout)
        # Definition of the toolbar via a menu and the ac
        self.symbologyMenu=None #init in case no menu is created
        self.createMenu()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_contextMenu)

        self.nameOfPov = "default"

        testMode=QAction(" &"+"Cursor Position", self,checkable=True)
        self.settingsMenu.addAction(testMode)
        testMode.triggered.connect(lambda: self.showCursorCoords())
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(10, 10, 350, 30)
        self.label.move(300,0)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.maj_coordonnees)
        self.isLabelVisible = False
    
    def showCursorCoords(self):

        self.isLabelVisible = not self.isLabelVisible

        if self.isLabelVisible:
            self.label.show()
            self.timer.start(100)
        else:
            self.label.hide()
            self.timer.stop()

    def maj_coordonnees(self):
        pos_souris_globale = self.mapFromGlobal(QCursor.pos())
        coord_x, coord_y = pos_souris_globale.x(), pos_souris_globale.y()
        self.label.setText(f'Global Cursor Coordinates : ({coord_x}, {coord_y})')
    
    def createEGLMenu(self):
        """Create Enhanced Grid Layout submenu in Settings menu"""
        if self.typeOfLayout == "enhanced_grid":
            self.eglMenu = self.settingsMenu.addMenu("&Enhanced Grid Layout")
            
            # Edit layoutOrders action
            editPIDsAction = QAction("&Edit GameSpace Order...", self)
            editPIDsAction.triggered.connect(self.openPIDTableDialog)
            self.eglMenu.addAction(editPIDsAction)
            
            # Rearrange action
            rearrangeAction = QAction("&Restore Grid Layout", self)
            rearrangeAction.triggered.connect(self.applyEnhancedGridLayout)
            self.eglMenu.addAction(rearrangeAction)
            
            # Separator
            self.eglMenu.addSeparator()
            
            # Toggle layoutOrder tooltips action
            self.pidTooltipAction = QAction("&Show GameSpace order tooltip", self)
            self.pidTooltipAction.setCheckable(True)
            self.pidTooltipAction.setChecked(False)
            self.pidTooltipAction.triggered.connect(self.togglePIDTooltips)
            self.eglMenu.addAction(self.pidTooltipAction)
    
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
        entityDefs = self.getEntitiesDef()
        
        # Create submenus for each entity definition
        for entityDef in entityDefs:
            # Create submenu for this entity type
            entityMenu = self.tooltipMenu.addMenu(f"&{entityDef.entityName}")
            
            # Create action group for exclusive selection within this entity type
            actionGroup = QActionGroup(self)
            actionGroup.setExclusive(True)
            
            # Store reference to action group for this entity
            if not hasattr(self, 'tooltipActionGroups'):
                self.tooltipActionGroups = {}
            self.tooltipActionGroups[entityDef.entityName] = actionGroup
            
            # Create actions for each tooltip option
            for label, tooltipType, description in tooltipOptions:
                action = QAction(f"&{label}", self)
                action.setCheckable(True)
                action.setStatusTip(f"{description} for {entityDef.entityName}")
                action.setData(tooltipType)
                
                # Set default selection (none)
                if tooltipType == "none":
                    action.setChecked(True)
                
                action.triggered.connect(lambda checked, e=entityDef, t=tooltipType: self.setTooltipTypeForEntity(e, t))
                actionGroup.addAction(action)
                entityMenu.addAction(action)
            
            # Add custom tooltips defined by modeler
            for tooltipName in entityDef.customTooltips.keys():
                action = QAction(f"&{tooltipName}", self)
                action.setCheckable(True)
                action.setStatusTip(f"Custom tooltip: {tooltipName} for {entityDef.entityName}")
                action.setData(tooltipName)
                
                action.triggered.connect(lambda checked, e=entityDef, t=tooltipName: self.setTooltipTypeForEntity(e, t))
                actionGroup.addAction(action)
                entityMenu.addAction(action)
    
    def setTooltipTypeForEntity(self, entityDef, tooltipType):
        """Set tooltip type for a specific entity definition"""
        if hasattr(entityDef, 'displayTooltip'):
            entityDef.displayTooltip(tooltipType)
    
    def updateTooltipMenu(self):
        """Update tooltip menu when custom tooltips are added"""
        # Clear existing tooltip menu
        if hasattr(self, 'tooltipMenu'):
            self.tooltipMenu.clear()
            if hasattr(self, 'tooltipActionGroups'):
                del self.tooltipActionGroups
        
        # Recreate the menu
        self.createTooltipMenu()
    
    def initBeforeShowing(self):
        """Initialize components that need to be ready before the window is shown"""
        # Initialize tooltip menu with all entity definitions
        self.updateTooltipMenu()
        
        # Initialize EGL menu if using enhanced_grid layout
        self.createEGLMenu()
        
        # Reorganize EGL layoutOrders to eliminate gaps
        self.reorganizeEGLPIDs()
        
        
    
        
        # Show admin control panel if needed
        if self.shouldDisplayAdminControlPanel:
            self.show_adminControlPanel()
        
        # Set up dashboards
        self.setDashboards()
    
    def initAfterOpening(self):
        if self.currentPlayerName is None:
            possibleUsers = self.getUsers_withControlPanel()
            if possibleUsers != [] : self.setCurrentPlayer(possibleUsers[0])
            elif possibleUsers == [] : self.setCurrentPlayer('Admin')
        if not self.hasDefinedPositionGameSpace() : QTimer.singleShot(100, self.adjustGamespacesPosition)
        
        # Position all agents after grid layout is applied and window is shown
        # Use QApplication.processEvents() to ensure layouts are processed before positioning
        QApplication.processEvents()
        self.positionAllAgents()
        
    def hasDefinedPositionGameSpace(self):
        return any(aGameSpace.isPositionDefineByModeler() for aGameSpace in self.gameSpaces.values())


    def setDashboards(self):
        dashboards=self.getGameSpaceByClass(SGDashBoard)
        for aDashBoard in dashboards:
            aDashBoard.showIndicators()
    
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
        aAction .triggered.connect(self.zoomLessModel)
        self.menuBar().addAction(aAction)

        aAction  = QAction(QIcon(f"{path_icon}/zoomToFit.png"), " &zoomToFit", self)
        aAction .triggered.connect(self.zoomFitModel)
        self.menuBar().addAction(aAction)

        self.menuBar().addSeparator()

        self.symbologyMenu = self.menuBar().addMenu(QIcon(f"{path_icon}/symbology.png"), "&Symbology")
        self.symbologiesInSubmenus = {}
        self.keyword_borderSubmenu = ' border'

        self.settingsMenu = self.menuBar().addMenu(QIcon(f"{path_icon}/settings.png"), " &Settings")

        self.createGraphMenu()


    # Create all the action related to the menu

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
        pass

    def zoomLessModel(self):
        pass

    def zoomFitModel(self):
        pass


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

        
    # Loading a Save
    def openFromSave(self):
        """To be implemented"""
        return True
    # Save the game in a file
    def saveTheGame(self):
        """To be implemented"""
        return True

    # Inspect All of the variables of the game
    def inspectAll(self):
        """To be implemented"""
        return True

    # Make the game go to precedent state
    def backwardAction(self):
        """To be implemented"""
        return True

    # Make the game go to next step
    def forwardAction(self):
        """To be implemented"""
        return True

    # def setAllDataSinceInit(self):
    #     print("Test")
    #     for aEntity in self.getAllEntities():
    #         h = aEntity.getHistoryDataJSON()
    #         self.listData.append(h)

    def getAllDataSinceInit(self):
        rounds = set([entry['round'] for entry in self.listData])
        print("rounds :: ", rounds)

    # Trigger the next turn
    def nextTurn(self):
        self.timeManager.nextPhase()
        if self.mqttMajType in ["Phase","Instantaneous"]:
            self.buildNextTurnMsgAndPublishToBroker()


    def closeEvent(self, event):
        self.haveToBeClose = True
        self.getTextBoxHistory(self.TextBoxes)
        if hasattr(self, 'client'):
            self.client.disconnect()
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
            # msg_box.setText("A " + agent_model.classDef.entityName +" cannot be moved here")
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
        
        position.setX(position.x()-int(agent_size/2))
        position.setY(position.y()-int(agent_size/2))
        agent_model.move(position)

        e.setDropAction(Qt.MoveAction)
        e.accept()

    # Contextual Menu (opened on a right click)
    def show_contextMenu(self, point):
        menu = QMenu(self)

        option1 = QAction("LayoutCheck", self)
        option1.triggered.connect(self.adjustGamespacesPosition) #todo Pourquoi lancer cette méthode ici ???
                                        #todo ca parait très risque. D'autant plus qu'il n'y a pas la verif de   if not self.isMoveToCoordsUsed 
        menu.addAction(option1)

        if self.rect().contains(point):
            menu.exec_(self.mapToGlobal(point))

    # Handle window title
    def updateWindowTitle(self):
        # Update window title with the number of the round and number of the phase
        if self.isTimeDisplayedInWindowTitle :
            if self.timeManager.numberOfPhases() == 1:
                title = f"{self.windowTitle_prefix} {' - ' if self.windowTitle_prefix != ' ' else ''} Round {self.roundNumber()}"
            else:
                title = f"{self.windowTitle_prefix} {' - ' if self.windowTitle_prefix != ' ' else ''} Round {self.roundNumber()}, Phase {self.phaseNumber()}"

            self.setWindowTitle(title) 



# -----------------------------------------------------------------------------------------
# Definiton of the methods who the modeler will use

# For create elements
    # To create a grid
    def newCellsOnGrid(self, columns=10, rows=10, format="square", size=30, gap=0, color=Qt.gray,moveable=True,name=None,backGroundImage=None,defaultCellImage=None,neighborhood='moore',boundaries='open'):
        """
        Create a grid that contains cells

        Args:
            columns (int): number of columns (width).
            rows (int): number of rows (height).
            format ("square", "hexagonal"): shape of the cells.
                - Defaults to "square".
                - Note that the hexagonal grid is "Pointy-top hex grid with even-r offset".
            size (int, optional): size of the cells. Defaults to 30.
            gap (int, optional): gap size between cells. Defaults to 0.
            color (a color, optional): background color of the grid . Defaults to Qt.gray.
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
            aCellDef: the cellDef that defines the cells that have been placed on a grid
        """
        # process the name if not defined by the user. The name has to be uniquer, because it is used to reference the CellDef and the associated grid
        if name is None:
            name = f'grid{str(self.numberOfGrids()+1)}'
            if name in self.gameSpaces:
                name = name + 'bis'
        # Create a grid
        aGrid = SGGrid(self, name, columns, rows, format, gap, size, color, moveable,backGroundImage,neighborhood,boundaries)

        # Create a CellDef and populate the grid with cells from the newly created CellDef
        aCellDef = self.generateCellsForGrid(aGrid,defaultCellImage,name)
        aGrid.cellDef =aCellDef

        self.gameSpaces[name] = aGrid

        # Realocation of the position thanks to the layout
        aGrid.globalPosition()
        self.applyAutomaticLayout()
        
        return aCellDef
    
    def generateCellsForGrid(self,grid,defaultCellImage,entityName):
        CellDef = SGCellDef(grid, grid.cellShape,grid.size, entDefAttributesAndValues=None, defaultColor=Qt.white,entityName=entityName,defaultCellImage=defaultCellImage)
        self.cellOfGrids[grid.id] = CellDef
        for row in range(1, grid.rows + 1):
            for col in range(1, grid.columns + 1):
                CellDef.newCell(col, row)
        return CellDef

    # To get the CellDef corresponding to a Grid
    def getCellDef(self, aGrid):
        if aGrid.isCellDef: return aGrid
        return self.cellOfGrids[aGrid.id]


    # To get all the cells of the collection
    # If several grids, this method only returns the cells of the first grid
    def getCells(self,grid=None):
        if grid == None:
            grid = self.getGrids()[0]
        return self.getCellDef(grid).entities
    
    def getAllCells(self):
        # send back the cells of all the grids
        aList= []
        for entDef in self.cellOfGrids.values():
            aList.extend(entDef.entities)
        return aList
    
    def numberOfCellDef(self):
        return len(self.cellOfGrids)
    
    def numberOfGrids(self):
        return self.numberOfCellDef()

    def getAllEntities(self):
        # send back the cells of all the grids and the agents of all the species
        aList= []
        for entDef in self.cellOfGrids.values():
            aList.extend(entDef.entities)
        for entDef in self.getAgentSpeciesDict():
            aList.extend(entDef.entities)
        return aList
    
    # To get all the povs of the collection
    def getCellPovs(self,grid):
        return {key: value for dict in (self.cellOfGrids[grid.id]['ColorPOV'],self.cellOfGrids[grid.id]['BorderPOV']) for key, value in dict.items() if "selected" not in key and "BorderWidth" not in key}

    # To get a cell in particular
    def getCell(self, aGrid, aId):
        result = list(filter(lambda cell: cell.id == aId, self.getCells(aGrid)))
        if len(result)!=1: raise ValueError("No cell with such Id!")
        return result[0]

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
        # Realocation of the position thanks to the layout
        aLegend.globalPosition()
        self.applyAutomaticLayout()
        return aLegend
    
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
            # Realocation of the position thanks to the layout
            userSelector.globalPosition()
            self.applyAutomaticLayout()
            return userSelector
        else:
            print(  f"The userSelector was not created because: \n"
                    f"  - nb of players : {len(self.players)} ({[player.name for player in self.players.values()]}). \n"
                    f"  - nb of users with control panel: {len(self.getUsers_withControlPanel())} ({[userName for userName in self.getUsers_withControlPanel()]}). \n"
                    f"  - you need to add more users with control panel for the userSelector to be created"
                )

    # To create a New kind of agents
    def newAgentSpecies(self, name, shape, entDefAttributesAndValues=None, defaultSize=15, defaultColor=Qt.black, locationInEntity="random",defaultImage=None):
        """
        Create a new specie of Agents.

        Args:
            name (str) : the species name
            shape (str) : the species shape ("circleAgent","squareAgent", "ellipseAgent1","ellipseAgent2", "rectAgent1","rectAgent2", "triangleAgent1","triangleAgent2", "arrowAgent1","arrowAgent2")
            dictAttributes (dict) : all the species attributs with all the values
            defaultSize (int) : the species shape size (Default=10)
            locationInEntity (str, optional) : topRight, topLeft, center, bottomRight, bottomLeft, random 
            defaultImage (str, optional) : link to image
        Return:
            a nested dict for the species
            a species

        """
        if shape not in ["circleAgent","squareAgent", "ellipseAgent1","ellipseAgent2", "rectAgent1","rectAgent2", "triangleAgent1","triangleAgent2", "arrowAgent1","arrowAgent2"]:
            raise ValueError(f"Invalid shape: {shape}")
        aAgentSpecies = SGAgentDef(self, name, shape, defaultSize, entDefAttributesAndValues, defaultColor,locationInEntity,defaultImage)
        self.agentSpecies[name]=aAgentSpecies
        return aAgentSpecies

    def getDefaultAgentRandomValue(self, begin, end):
        #Cette methode etait utiliser dans exstep8 pour l'utiliser comme suit :
            #Sheeps.setDefaultValues({"health":(lambda: random.randint(0,10)*10)})
            #Sheeps.setDefaultValues({"health": (lambda: myModel.getDefaultAgentRandomValue(0, 10)*10)})
        return random.randint(begin, end)

    def getAgentSpeciesName(self):
        # send back a list of the names of all the species
        return list(self.agentSpecies.keys())
    
    def getAgentSpeciesDict(self):
        # send back a list of all the species Dict (specie definition dict)
        return list(self.agentSpecies.values())

    def getAgentSpecieDict(self, aSpecieName):
        # send back the specie dict (specie definition dict) that corresponds to aSpecieName
        return self.agentSpecies.get(aSpecieName)

    def getAgentsOfSpecie(self, aSpecieName) -> list[SGAgent]:
        agentDef = self.getAgentSpecieDict(aSpecieName)
        if agentDef is None:  return None
        else: return agentDef.entities[:]
    
    def positionAllAgents(self):
        """Position all agents after grid layout is applied"""
        for agent_species in self.getAgentSpeciesDict():
            for agent in agent_species.entities:
                if hasattr(agent, 'view') and agent.view:
                    # Show the agent view first
                    agent.view.show()
                    agent.view.raise_()  # Bring to front
                    # Then position it
                    agent.view.getPositionInEntity()
                    # Force update to ensure positioning is applied
                    agent.view.update()

    def getAllAgents(self):
        # send back the agents of all the species
        aList= []
        for entDef in self.getAgentSpeciesDict():
            aList.extend(entDef.entities)
        return aList
    
    def getEntitiesDef(self):
        return list(self.cellOfGrids.values()) + list(self.agentSpecies.values())

    def getEntityDef(self, entityName):
        if isinstance(entityName,SGEntityDef):
            return entityName
        return self.getEntityDefByName(entityName)
    
    def getEntityDefByName(self, entityName):
        entityDef = next((entDef for entDef in self.getEntitiesDef() if entDef.entityName == entityName), None)
        
        if entityDef is None:
            existing_entities = [entDef.entityName for entDef in self.getEntitiesDef()]
            raise ValueError(f"No EntityDef found with the name '{entityName}'. Existing EntityDefs: {', '.join(existing_entities)}")
        
        return entityDef

    #This method is used by updateServer to retrieve an entity (cell , agents) used has argument in a game action 
    def getSGEntity_withIdentfier(self, aIdentificationDict):
        entDef = self.getEntityDef(aIdentificationDict['entityName'])
        aId = aIdentificationDict['id']
        targetEntity = entDef.getEntity(aId)
        return targetEntity 

    #This method is used by updateServer to retrieve any type of SG object (eg. GameAction or Entity) 
    def getSGObject_withIdentifier(self, aIdentificationDict):
        className = aIdentificationDict['entityName']
        aId = aIdentificationDict['id']
        return next((aInst for aInst in eval(className).instances if aInst.id == aId), None)
        

    def deleteAllAgents(self):
        for aAgentDef in self.getAgentSpeciesDict():
            aAgentDef.deleteAllEntities()

    def updateIDincr(self, newValue):
        self.IDincr = newValue
        return self.IDincr
    
    def updateIDmemory(self, aSpecies):
        aSpecies.memoryID = aSpecies.memoryID+1


    def getIdFromPrivateId(self, aPrivateID, aSpeciesName):
        result=re.search(f'{aSpeciesName}(\d+)', aPrivateID)
        if result:
            anID=result.group(1)
            return anID
        raise ValueError("Check again!")
    
    def checkAndUpdateWatchers(self):
        for entDef in self.getEntitiesDef():
            entDef.updateAllWatchers()
        for aPlayer in self.getEntitiesDef():
            entDef.updateAllWatchers()
    
    def getAgentsPrivateID(self):
        agents=self.getAllAgents()
        agents_privateID=[]
        for agent in agents:
            agents_privateID.append(agent.privateID)
        return agents_privateID


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
        aModelAction = SGModelAction_OnEntities(self,actions, conditions, feedbacks,(lambda:self.getAgentsOfSpecie(specieName)))
        self.id_modelActions += 1
        aModelAction.id = self.id_modelActions
        return aModelAction

    # To create a player
    def newPlayer(self, name,attributesAndValues=None):
        """"
        Create a new player

        Args:
            name (str) : name of the Player (will be displayed)
        """
        player = SGPlayer(self, name,attributesAndValues=attributesAndValues)
        self.players[name] = player
        self.users.append(player.name)
        return player

    def getAllPlayers(self):
        return list(self.players.values())
        
    def getPlayer(self, aUserName):
        if aUserName is None:
            raise ValueError('Username cannot be None')
        if aUserName == "Admin":
            return self.getAdminPlayer()
        if isinstance(aUserName,SGPlayer):
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
    



    def getUsersName(self):
        aList = [aP.name for aP in list(self.players.values())]
        aList.append('Admin')
        return aList

    def getUserControlPanelOrLegend(self, aUserName):
        self.getLegends()

    # To select only users with a control panel
    def getUsers_withControlPanel(self):
        selection=[]
        if self.shouldDisplayAdminControlPanel:
            selection.append('Admin')     
        for aP in self.players.values():
            if aP.controlPanel !=  None:
                selection.append(aP.name) 
        return selection


    def displayTimeInWindowTitle(self, setting=True):
        """
        Set whether to display the time (Round number and Phase number) in the window title.
        Args:
            setting (bool, optional): If True or not specified, the time will be displayed in the window title; if False, it will not.
        """
        self.isTimeDisplayedInWindowTitle = setting
        
    # To create a Time Label
    def newTimeLabel(self, title=None, backgroundColor=Qt.white, borderColor=Qt.black, textColor=Qt.black):
        """
        Create the visual time board of the game.
        
        Args:
        title (str) : name of the widget (default:None)
        backgroundColor (Qt Color) : color of the background (default : Qt.white)
        borderColor (Qt Color) : color of the border (default : Qt.black)
        textColor (Qt Color) : color of the text (default : Qt.black)
        """
        aTimeLabel = SGTimeLabel(
            self, title, backgroundColor, borderColor, textColor)
        self.myTimeLabel = aTimeLabel
        self.gameSpaces[title] = aTimeLabel
        # Realocation of the position thanks to the layout
        aTimeLabel.globalPosition()
        self.applyAutomaticLayout()

        return aTimeLabel

    # To create a Text Box
    def newTextBox(self, textToWrite='Welcome in the game !', title='Text Box', sizeX=None, sizeY=None, borderColor=Qt.black, backgroundColor=Qt.lightGray):
        """
        Create a text box with full customization options.

        Args:
            textToWrite (str): Displayed text in the widget (default: "Welcome in the game!")
            title (str): Name of the widget (default: "Text Box")
            sizeX (int, optional): Manual width override for the text box
            sizeY (int, optional): Manual height override for the text box
            borderColor (QColor): Border color of the text box (default: Qt.black)
            backgroundColor (QColor): Background color of the text box (default: Qt.lightGray)

        Returns:
            SGTextBox: The created text box widget
        """
    def newTextBox(self, textToWrite='Welcome in the game !', title='Text Box', sizeX=None, sizeY=None, borderColor=Qt.black, backgroundColor=Qt.lightGray):
        """
        Create a text box with full customization options.

        Args:
            textToWrite (str): Displayed text in the widget (default: "Welcome in the game!")
            title (str): Name of the widget (default: "Text Box")
            sizeX (int, optional): Manual width override for the text box
            sizeY (int, optional): Manual height override for the text box
            borderColor (QColor): Border color of the text box (default: Qt.black)
            backgroundColor (QColor): Background color of the text box (default: Qt.lightGray)

        Returns:
            SGTextBox: The created text box widget
        """
        aTextBox = SGTextBox(self, textToWrite, title, sizeX, sizeY, borderColor, backgroundColor)
        self.TextBoxes.append(aTextBox)
        self.gameSpaces[title] = aTextBox
        # Realocation of the position thanks to the layout
        aTextBox.globalPosition()
        self.applyAutomaticLayout()

        return aTextBox
    
    # To create a Text Box
    def newLabel(self, text, position, textStyle_specs="", borderStyle_specs="", backgroundColor_specs="", alignement="Left", fixedWidth=None, fixedHeight=None):
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
        aLabel.move(position[0], position[1])
        return aLabel

    def newLabel_stylised(self, text, position, font=None, size=None, color=None, text_decoration="none", font_weight="normal", font_style="normal", alignement= "Left", border_style="solid", border_size=0, border_color=None, background_color=None, fixedWidth=None, fixedHeight=None):
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
    def newButton(self, method, text, position,
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
                    disabled_color=None):
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
                        disabled_color=disabled_color)
        # aButton = SGButton(self, method, text, textStyle_specs, borderStyle_specs, backgroundColor_specs, fixedWidth, fixedHeight)
        aButton.move(position[0], position[1])
        return aButton
    

    def set_gameSpaces_draggability(self, all_elements=None, include=None, exclude=None, value=True):
        """
        Met à jour l'état de "draggability" des éléments.
        
        :param all_elements: Si True, applique la valeur à tous les éléments.
        :param include: Liste des éléments spécifiques à modifier.
        :param exclude: Liste des éléments à exclure.
        :param value: Valeur à appliquer (True ou False).
        """
        all_game_spaces = self.gameSpaces.values()


        # Initialiser la liste des éléments à modifier
        elements_to_change = set()

        # Ajouter tous les éléments si all_elements est True
        if all_elements:
            elements_to_change.update(all_game_spaces)

        # Ajouter les éléments spécifiés dans include
        if include:
            elements_to_change.update(include)

        # Exclure les éléments spécifiés dans exclude
        if exclude:
            elements_to_change.difference_update(exclude)

        # Mettre à jour la "draggability" pour les éléments sélectionnés
        for element in elements_to_change:
            element.setDraggability(value)

#****************************************************

    def displayAdminControlPanel(self):
        """
        Display the Admin Control Panel
        """
        self.shouldDisplayAdminControlPanel = True
        if not self.timeManager.isInitialization():
            self.show_adminControlPanel()


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

    def deleteTextBox(self, titleOfTheTextBox):
        del self.gameSpaces[titleOfTheTextBox]

    def getTextBoxHistory(self, TextBoxes):
        for aTextBox in TextBoxes:
            print(str(aTextBox.id)+' : '+str(aTextBox.history))

    def newDashBoard(self, title=None, borderColor=Qt.black, borderSize=1, backgroundColor=QColor(230, 230, 230), textColor=Qt.black, layout ='vertical'):
        """  Qt.lightGray
        Create the score board of the game

        Args:
        title (str) : title of the widget (default:"Phases&Rounds")
        backgroundColor (Qt Color) : color of the background (default : Qt.transparent)
        borderColor (Qt Color, default very light gray) : color of the border (default : Qt.black)
        textColor (Qt Color) : color of the text (default : Qt.black)
        """
        aDashBoard = SGDashBoard(
            self, title, borderColor, borderSize, backgroundColor, textColor, layout)
        self.gameSpaces[aDashBoard.id] = aDashBoard
        # Realocation of the position thanks to the layout
        aDashBoard.globalPosition()
        self.applyAutomaticLayout()

        return aDashBoard

    def newEndGameRule(self, title='EndGame Rules', numberRequired=1):
        """
        Create the EndGame Rule Board of the game

        Args:
            title (str) : header of the board, displayed (default : EndGame Rules)
            numberRequired (int) : number of completed conditions to trigger EndGame
        """
        aEndGameRule = SGEndGameRule(self, title, numberRequired)
        self.gameSpaces[title] = aEndGameRule
        self.endGameRule = aEndGameRule
        # Realocation of the position thanks to the layout
        aEndGameRule.globalPosition()
        self.applyAutomaticLayout()

        return aEndGameRule

    def roundNumber(self):
        """Return the current ingame round number"""
        return self.timeManager.currentRoundNumber

    def phaseNumber(self):
        """Return the current ingame phase number"""
        return self.timeManager.currentPhaseNumber
    
    def newSimVariable(self,name,initValue,color=Qt.black,isDisplay=True):
        aSimVar=SGSimulationVariable(self,initValue,name,color,isDisplay)
        self.simulationVariables.append(aSimVar)
        return aSimVar
    
    def getSimVars(self):
        return self.simulationVariables

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

        # Create the ProgressGauge with same defaults as the class
        aProgressGauge = SGProgressGauge(
            parent=self,
            simVar=simVar,
            min_value=minimum,
            max_value=maximum,
            title=title,
            orientation=orientation,
            colorRanges=colorRanges,
            unit=unit,
            borderColor=borderColor,
            backgroundColor=backgroundColor,
            bar_width=bar_width,
            bar_length=bar_length,
            title_position=title_position,
            display_value_on_top=display_value_on_top
        )
        
        # Register the gauge in the model
        self.gameSpaces[title] = aProgressGauge

        # Position and layout adjustments
        aProgressGauge.globalPosition()
        self.applyAutomaticLayout()

        # Initial refresh
        aProgressGauge.checkAndUpdate()

        return aProgressGauge


# Layout
    # To get a gameSpace in particular

    def getGameSpaceByName(self, name):
        return self.gameSpaces[name]

    def getGameSpaceByClass(self,aClass):
        gameSpaces=[aGameSpace for aName,aGameSpace in self.gameSpaces.items() if isinstance(aGameSpace,aClass)]
        return gameSpaces
    
    # To apply the layout to all the current game spaces
    def applyAutomaticLayout(self): #todo basculer ce code dans les classes de layout
        # Polymorphisme à l'exécution - chaque layout gère sa propre logique
        self.layoutOfModel.applyLayout(self.gameSpaces.values())
                
    
    def applyEnhancedGridLayout(self):
        """
        Apply Enhanced Grid Layout (EGL) to all gameSpaces
        
        This method implements the complete EGL cycle:
        1. Organize gameSpaces in structured layout
        2. Record calculated positions
        3. Release the structured layout
        4. Allow free positioning while maintaining organization capability
        """
        if self.typeOfLayout == "enhanced_grid":
            # Trigger the EGL cycle
            self.layoutOfModel.rearrangeWithLayoutThenReleaseLayout()
            
            # Apply the calculated positions to gameSpaces
            for aGameSpace in self.gameSpaces.values():
                if not aGameSpace.isPositionDefineByModeler():
                    # Only move gameSpaces without explicit modeler positioning
                    if hasattr(aGameSpace, '_egl_calculated_position'):
                        aGameSpace.move(aGameSpace._egl_calculated_position[0], 
                                      aGameSpace._egl_calculated_position[1])
                    else:
                        # Fallback to standard positioning
                        aGameSpace.move(aGameSpace.startXBase, aGameSpace.startYBase)
    
    def openPIDTableDialog(self):
        """
        Open the layoutOrder management dialog
        """
        if self.typeOfLayout == "enhanced_grid":
            from mainClasses.layout.SGLayoutOrderTableDialog import SGLayoutOrderTableDialog
            dialog = SGLayoutOrderTableDialog(self)
            dialog.exec_()
    
    def togglePIDTooltips(self, checked):
        """
        Toggle layoutOrder tooltips for all gameSpaces
        
        Args:
            checked (bool): Whether to show layoutOrder tooltips
        """
        if self.typeOfLayout == "enhanced_grid":
            for gameSpace in self.gameSpaces.values():
                gameSpace._egl_pid_tooltip_enabled = checked
                
    
    def reorganizeEGLPIDs(self):
        """
        Reorganize layoutOrders to eliminate gaps while preserving order
        
        This method is called during initialization to ensure sequential layoutOrder numbering
        for better column distribution in the Enhanced Grid Layout.
        """
        if self.typeOfLayout == "enhanced_grid":
            self.layoutOfModel.reorganizePIDsSequentially()
    
    def checkLayoutIntersection(self,name,element,otherName,otherElement):
        if name!=otherName and (element.geometry().intersects(otherElement.geometry()) or element.geometry().contains(otherElement.geometry())):
            return True
        return False
    
    def adjustGamespacesPosition(self):
        for name,aGameSpace in self.gameSpaces.items():
            for otherName,otherElement in self.gameSpaces.items():
                while self.checkLayoutIntersection(name,aGameSpace,otherName,otherElement):
                    if aGameSpace.areaCalc() <= otherElement.areaCalc():
                        local_pos=aGameSpace.pos()
                        aGameSpace.move(local_pos.x()+10,local_pos.y()+10) #todo Ce code créé un décalage vertical meme lorsque qu'il n'y a pas de superposition
                    else:
                        local_pos=otherElement.pos()
                        otherElement.move(local_pos.x()+10,local_pos.y()+10)

    # ------
# Pov
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
            self.symbologiesInSubmenus[submenu]=[]
            return submenu
            
    def addClassDefSymbologyinMenuBar(self, aClassDef,nameOfSymbology,isBorder=False):
        if self.symbologyMenu is None: return False
        submenu_name= aClassDef.entityName
        if isBorder: submenu_name = submenu_name + self.keyword_borderSubmenu
        # get the submenu (or create it if it doesn't exist yet)
        submenu = self.getOrCreateSubmenuSymbology(submenu_name)
        # create an element with checkbox
        item = QAction(nameOfSymbology, self, checkable=True)
        item.triggered.connect(self.menu_item_triggered)
        # add the submenu to the menu
        submenu.addAction(item)
        # add actions to the submenu
        self.symbologiesInSubmenus[submenu].append(item)

    def checkSymbologyinMenuBar(self, aClassDef, nameOfSymbology, borderSymbology=False):
        """
        Checks and updates the symbology in the menu bar for the specified class definition.

        Args:
            aClassDef: The class definition for which the symbology is being checked.
            nameOfSymbology (str): The name of the symbology to check.
            borderSymbology (bool): Indicates if the symbology is for a border (default: False).

        Returns:
            bool: False if the symbology menu is not initialized, otherwise None.
        """
        if self.symbologyMenu is None:
            return False

        if borderSymbology:
            entityName = aClassDef.entityName + self.keyword_borderSubmenu
        else:
            entityName = aClassDef.entityName

        symbologies = self.getSymbologiesOfSubmenu(entityName)

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
        self.update() #update all the interface display

    def getSymbologiesOfSubmenu(self, submenuName, borderSymbology = False):
        # return the  symbologies of a entity present in the menuBar
        submenu = self.getSubmenuSymbology(submenuName)
        return self.symbologiesInSubmenus.get(submenu) 
    
    def getCheckedSymbologyOfEntity(self, entityName, borderSymbology = False):
        # return the name of the symbology which is checked for a given entity type. If no symbology is ckecked, returns None
        if self.symbologyMenu is None: return None
        if borderSymbology: entityName = entityName + self.keyword_borderSubmenu
        symbologies = self.getSymbologiesOfSubmenu(entityName)
        if symbologies is None: return None
        return next((aSymbology.text() for aSymbology in symbologies if aSymbology.isChecked()),None)

    def getAllCheckedSymbologies(self, grid=None):
        # return the active symbology of each type of entity
        if grid is None: 
            gridObject = self.getGrids()[0]
            cellDef = self.getCellDef(gridObject)
            entitiesDef=[cellDef] + list(self.agentSpecies.values())
        elif grid == "combined" :
            entitiesDef=[]
            for aGrid in self.getGrids():
                cellDef = self.getCellDef(aGrid)
                entitiesDef=entitiesDef+[cellDef]
            entitiesDef=entitiesDef+list(self.agentSpecies.values())
        else : 
            gridObject=self.getGrid_withID(grid)
            cellDef = self.getCellDef(gridObject)
            entitiesDef=[cellDef] + list(self.agentSpecies.values())

        selectedSymbologies={}
        for entDef in entitiesDef:
            selectedSymbologies[entDef]={
                'shape':self.getCheckedSymbologyOfEntity(entDef.entityName),
                'border': self.getCheckedSymbologyOfEntity(entDef.entityName, borderSymbology = True)
                }
        return selectedSymbologies

    def checkFirstSymbologyOfEntitiesInMenu(self):
        # return the name of the symbology which is checked for a given entity type. If no symbology is ckecked, returns None
        for aListOfSubmenuItems in self.symbologiesInSubmenus.values():
            aListOfSubmenuItems[0].setChecked(True)

    # -----------------------------------------------------------
    # TimeManager functions

    def getTimeManager(self):
        return self.timeManager

    # -----------------------------------------------------------
    # Game actions function

    def newCreateAction(self, anObjectType, dictAttributes=None, aNumber='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[],aNameToDisplay=None,create_several_at_each_click=False,writeAttributeInLabel=False):
        """
        Add a Create GameAction to the game.

        Args:
        - anObjectType : a AgentSpecies or the keyword "Cell"
        - a Number (int) : number of utilisation, could use "infinite"
        - dictAttributes (dict) : attribute with value concerned, could be None

        """
        aClassDef = self.getEntityDef(anObjectType)
        if aClassDef is None : raise ValueError('Wrong format of entityDef')
        return SGCreate(aClassDef,  dictAttributes, aNumber,conditions, feedbacks, conditionsOfFeedback,aNameToDisplay, create_several_at_each_click = create_several_at_each_click, writeAttributeInLabel=writeAttributeInLabel)

    def newModifyAction(self, anObjectType, dictAttributes={}, aNumber='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[],aNameToDisplay=None,setControllerContextualMenu=False,writeAttributeInLabel=False):
        """
        Add a Modify GameAction to the game.

        Args:
        - anObjectType : a AgentSpecies or the keyword "Cell"
        - a Number (int) : number of utilisation, could use "infinite"
        - dictAttributes (dict) : attribute with value concerned, could be None

        """
        aClassDef = self.getEntityDef(anObjectType)
        if aClassDef is None : raise ValueError('Wrong format of entityDef')
        return SGModify(aClassDef,  dictAttributes,aNumber, conditions, feedbacks, conditionsOfFeedback,aNameToDisplay,setControllerContextualMenu,writeAttributeInLabel=writeAttributeInLabel)

    def newModifyActionWithDialog(self, anObjectType, attribute, aNumber='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[], aNameToDisplay=None, setControllerContextualMenu=False, writeAttributeInLabel=False):
        """
        Add a ModifyActionWithDialog GameAction to the game.
        
        Args:
            anObjectType: an AgentSpecies or the keyword "Cell"
            attribute (str): the attribute to modify
            aNumber (int): number of utilisation, could use "infinite"
            conditions (list): conditions that must be met
            feedbacks (list): actions to execute after modification
            conditionsOfFeedback (list): conditions for feedback execution
            aNameToDisplay (str): custom name to display
            setControllerContextualMenu (bool): whether to show in contextual menu
            writeAttributeInLabel (bool): whether to show attribute in label
        """
        aClassDef = self.getEntityDef(anObjectType)
        if aClassDef is None:
            raise ValueError('Wrong format of entityDef')
        
        from mainClasses.gameAction.SGModify import SGModifyActionWithDialog
        return SGModifyActionWithDialog(aClassDef, attribute, aNumber, conditions, feedbacks, conditionsOfFeedback, aNameToDisplay, setControllerContextualMenu, writeAttributeInLabel)

    def newDeleteAction(self, anObjectType, aNumber='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[],aNameToDisplay=None,setControllerContextualMenu=False):
        """
        Add a Delete GameAction to the game.

        Args:
        - anObjectType : a AgentSpecies
        - a Number (int) : number of utilisation, could use "infinite"
        - dictAttributes (dict) : attribute with value concerned, could be None

        """
        aClassDef = self.getEntityDef(anObjectType)
        if aClassDef is None : raise ValueError('Wrong format of entityDef')
        return SGDelete(aClassDef, aNumber, conditions, feedbacks, conditionsOfFeedback,aNameToDisplay,setControllerContextualMenu)

    def newMoveAction(self, anObjectType, aNumber='infinite', conditions=[], feedbacks=[], conditionsOfFeedback=[], feedbacksAgent=[], conditionsOfFeedBackAgent=[],aNameToDisplay=None,setOnController=True):
        """
        Add a MoveAction to the game.

        Args:
        - anObjectType : a AgentSpecies
        - a Number (int) : number of utilisation, could use "infinite"
        - listOfConditions (list of lambda functions) : conditions on the moving Entity
        """
        aClassDef = self.getEntityDef(anObjectType)
        if aClassDef is None : raise ValueError('Wrong format of entityDef')
        return SGMove(aClassDef, aNumber, conditions, feedbacks, conditionsOfFeedback, feedbacksAgent, conditionsOfFeedBackAgent,aNameToDisplay,setOnController=setOnController)

    def newActivateAction(self,anObjectType,aMethod=None,aNumber='infinite',conditions=[],feedbacks=[],conditionsOfFeedback=[],aNameToDisplay=None,setControllerContextualMenu=False,setControllerButton =None) :
        """Add a ActivateAction to the game
        Args:
        - an ObjectType : a Entity
        - """
        #Case for action on the model
        if anObjectType is None or anObjectType ==self:
            aClassDef = self
        else:
            #Case for action on a Entity
            aClassDef = self.getEntityDef(anObjectType)
        # if aClassDef is None : raise ValueError('Wrong format of entityDef')
        # todo these 2 lines are useless
        # if isinstance(aClassDef,SGEntityDef) and setControllerContextualMenu:
        #     aClassDef.updateMenu=True

        aActivateAction = SGActivate(aClassDef, aMethod ,aNumber, conditions, feedbacks, conditionsOfFeedback,aNameToDisplay,setControllerContextualMenu)

        if setControllerButton:
            buttonCoord = setControllerButton
            self.newButton(aActivateAction, aActivateAction.nameToDisplay, buttonCoord)
        return aActivateAction

    def newPlayPhase(self, phaseName, activePlayers=None, modelActions=[], autoForwardWhenAllActionsUsed=False, message_auto_forward=True, show_message_box_at_start=False):
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
        return self.timeManager.newPlayPhase(phaseName, activePlayers, modelActions, autoForwardWhenAllActionsUsed, message_auto_forward, show_message_box_at_start)

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
    # -----------------------------------------------------------
    # Getter

    def getGrid(self,anObject):
        if anObject.isCellDef: return anObject.grid
        elif anObject.isAGrid: return anObject
        else: raise ValueError('Wrong object type')


    # To get all type of gameSpace who are grids
    def getGrids(self):
        return[aGameSpace for aGameSpace in list(self.gameSpaces.values()) if isinstance(aGameSpace, SGGrid)]
    
    def getGrid_withID(self, aGridID):
        return next((item for item in self.getGrids() if item.id==aGridID), None)
            
    # To get all type of gameSpace who are legends
    def getLegends(self):
        return[aGameSpace for aGameSpace in list(self.gameSpaces.values()) if isinstance(aGameSpace, SGLegend)]

    def getControlPanels(self):
        return[aGameSpace for aGameSpace in list(self.gameSpaces.values()) if isinstance(aGameSpace, SGControlPanel)]

    def getAdminControlPanels(self): #useful in case they are several admin control panels
        return [item for item in self.getControlPanels() if item.isAdminLegend()]

    def getAdminPlayer(self):
        """Get the Admin player instance"""
        return self.players.get("Admin")
    
    def getSelectedLegendItem(self):
        return next((item.selected for item in self.getControlPanels() if item.isActiveAndSelected()), None)

    def getGameAction_withClassAndId(self,aClassName,aId):
        return next((item for item in self.getAllGameActions() if item.__class__.__name__==aClassName and item.id==aId), None)
        
            
    # To change the number of zoom we currently are
    def setNumberOfZoom(self, number):
        self.numberOfZoom = number

    # To set User list
    def setUsers(self, listOfUsers):
        self.users = listOfUsers

    # To open and launch the game without a mqtt broker
    def  launch(self):
        """
        Launch the game.
        """
        self.initBeforeShowing()
        
        self.show()
        self.initAfterOpening()

    # To open and launch the game with a mqtt broker
    def launch_withMQTT(self,majType):
        """
        Set the mqtt protocol, then launch the game

        Args:
            majType (str): "Phase" or "Instantaneous"
        
        """
        self.clientId= uuid.uuid4().hex
        self.majTimer = QTimer(self)
        self.majTimer.timeout.connect(self.onMAJTimer)
        self.majTimer.start(100)
        self.initMQTT()
        self.mqttMajType=majType

        self.launch()

    # Return all gameActions of all players
    def getAllGameActions(self):
        aList= []
        for player in self.players.values():
            aList.extend(player.gameActions)
        return aList

    def getAgentIDFromMessage(self,message,nbCells):
        """
        Get the Agent ID list from an update message

        args:
            - message (array of string) : decoded mqtt message
            - nbCells (int) : value in the message
        """
        majIDs=set()
        for j in range(len(message[nbCells+2:-5])):
            agID = message[nbCells+2+j][0]
            majIDs.add(agID)
        return majIDs

    # MQTT Basic function to  connect to the broker
    def connect_mqtt(self):
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
        self.client = mqtt_client.Client(self.currentPlayerName)
        # self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, self.currentPlayerName) # for the new version of paho possible correction
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_log = on_log
        self.q = queue.Queue()
        self.t1 = threading.Thread(target=self.handleClientThread, args=())
        self.t1.start()
        self.timer.start(5)
        self.client.connect("localhost", 1883)
        self.client.user_data_set(self)

    # Thread that handle the listen of the client
    def handleClientThread(self):
        while True:
            self.client.loop(.1)
            if self.haveToBeClose == True:
                break

    # Init the MQTT client
    def initMQTT(self):
        def on_message(aClient, userdata, msg):
            userdata.q.put(msg.payload)
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
        msgTopic = 'nextTurn'
        msg_dict={}
        msg_dict['clientId']=self.clientId
        #eventually, one can add some more info about this nextTurn action
        # msg_dict['foo']= foo
        serializedMsg = json.dumps(msg_dict)
        if hasattr(self, 'client'):
            self.client.publish(msgTopic,serializedMsg)
        else: raise ValueError('Why does this case happens?')

    # Method to build a json_string 'Execution message' and publish it on the mqtt broker
    # A 'Execution message' is a message that will triger a specified method, of a specified object, to be executed with some specified arguments
    def buildExeMsgAndPublishToBroker(self,*args):
        #Check that a client is declared
        if not hasattr(self, 'client'): raise ValueError('Why does this case happens?')
        
        msgTopic = args[0] # The first arg is the topic of the msg
        objectAndMethodToExe = args[1] #Second arg is a dict that identifies the object and method to be executed. The dict has three keys: 'class_name', 'id', 'method' (method name called by the object )
        argsToSerialize= args[2:] # The third to the last arg, correspond to all the arguments for the method

        #build the message to publish
        msg_dict={}
        msg_dict['clientId']=self.clientId
        msg_dict['objectAndMethod']= objectAndMethodToExe
        listOfArgs=[]
        for arg in argsToSerialize:
            if isinstance(arg,SGModel.JsonManagedDataTypes):
                listOfArgs.append(arg)
            else:
                listOfArgs.append(['SGObjectIdentifer',arg.getObjectIdentiferForJsonDumps()])
        msg_dict['listOfArgs']= listOfArgs

        #serialize (encode) and publish the message
        serializedMsg = json.dumps(msg_dict)
        self.client.publish(msgTopic,serializedMsg)

    def processBrokerMsg_nextTrun(self, unserializedMsg):
        #eventually, one can add and process some more info about this nextTurn action
        self.actionsFromBrokerToBeExecuted.append({
            'action_type':'nextTurn'
             })
        
    #Method to process the incoming of a "gameAction_performed" msg
    def processBrokerMsg_gameAction_performed(self, unserializedMsg):
        msg = unserializedMsg
        objectAndMethod = msg['objectAndMethod']
        classOfObjectToExe = objectAndMethod['class_name']
        idOfObjectToExe = objectAndMethod['id']
        methodOfObjectToExe = objectAndMethod['method']
        if methodOfObjectToExe != 'perform_with': raise ValueError('This method only works for msg that should execute gameAction.perform_with(*args)')
        aGameAction = self.getGameAction_withClassAndId(classOfObjectToExe,idOfObjectToExe)
        listOfArgs=[]
        for aArgSpec in msg['listOfArgs']:
            if isinstance(aArgSpec, list) and len(aArgSpec)>0 and aArgSpec[0]== 'SGObjectIdentifer':
                aArg=self.getSGEntity_withIdentfier(aArgSpec[1])
            else:
                aArg= aArgSpec
            listOfArgs.append(aArg)
        self.actionsFromBrokerToBeExecuted.append({
            'action_type':'gameAction',
            'gameAction':aGameAction,
             'listOfArgs':listOfArgs
             })

    def processBrokerMsg_executeMethod(self, unserializedMsg):
        msg = unserializedMsg
        objectAndMethod = msg['objectAndMethod']
        classOfObjectToExe = objectAndMethod['class_name']
        idOfObjectToExe = objectAndMethod['id']
        methodNameToExe = objectAndMethod['method']

        aIdentificationDict={}
        aIdentificationDict['entityName']=classOfObjectToExe
        aIdentificationDict['id']=idOfObjectToExe 
        aSGObject = self.getSGObject_withIdentifier(aIdentificationDict)
        
        methodToExe = getattr(aSGObject,methodNameToExe) # this code retrieves the method to be executed and places it in the 'methodToExe' variable. This 'methodToExe' variable can now be used as if it were the method to be executed.
        #retrieve the arguments of the method to be executed
        listOfArgs=[]
        for aArgSpec in msg['listOfArgs']:
            if isinstance(aArgSpec, list) and len(aArgSpec)>0 and aArgSpec[0]== 'SGObjectIdentifer':
                aArg=self.getSGObject_withIdentifier(aArgSpec[1])
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
        self.executeGameActionsAfterBrokerMsg()
    
    def executeGameActionsAfterBrokerMsg(self):
        for item in self.actionsFromBrokerToBeExecuted:
            actionType = item['action_type']
            if actionType == 'gameAction':
                aGameAction = item['gameAction']
                listOfArgs = item['listOfArgs']
                aGameAction.perform_with(*listOfArgs,serverUpdate=False)
            elif actionType == 'nextTurn':
                self.timeManager.nextPhase()
            else: raise ValueError('No other possible choices')

        self.actionsFromBrokerToBeExecuted=[]

    def getEntityDefByName(self, entityName):
        entityDef = next((entDef for entDef in self.getEntitiesDef() if entDef.entityName == entityName), None)
        
        if entityDef is None:
            existing_entities = [entDef.entityName for entDef in self.getEntitiesDef()]
            raise ValueError(f"No EntityDef found with the name '{entityName}'. Existing EntityDefs: {', '.join(existing_entities)}")
        
        return entityDef
    


