
from PyQt5.QtSvg import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import (QAction,QMenu,QMainWindow,QMessageBox)
from PyQt5 import QtWidgets
from mainClasses.layout.SGVerticalLayout import*
from mainClasses.layout.SGHorizontalLayout import*
from mainClasses.layout.SGGridLayout import*
from mainClasses.gameAction.SGMove import*
from mainClasses.gameAction.SGDelete import*
from mainClasses.gameAction.SGUpdate import*
from mainClasses.gameAction.SGCreate import*
from mainClasses.SGAgent import*
from mainClasses.SGCell import*
from mainClasses.SGControlPanel import*
from mainClasses.SGDashBoard import*
from mainClasses.SGEndGameRule import*
from mainClasses.SGEntity import*
from mainClasses.SGEntityDef import*
from mainClasses.SGGrid import*
from mainClasses.SGLegend import*
from mainClasses.SGModelAction import*
from mainClasses.SGPlayer import*
from mainClasses.SGSimulationVariable import*
from mainClasses.SGTextBox import*
from mainClasses.SGTimeLabel import*
from mainClasses.SGTimeManager import*
from mainClasses.SGUserSelector import*
from mainClasses.SGVoid import*
import sys
from pathlib import Path
from pyrsistent import s
from win32api import GetSystemMetrics
from paho.mqtt import client as mqtt_client
import threading
import queue
import uuid
import re
import json

sys.path.insert(0, str(Path(__file__).parent))


# Mother class of all the SGE System
class SGModel(QMainWindow):

    JsonManagedDataTypes=(dict,list,tuple,str,int,float,bool)

    def __init__(self, width=1800, height=900, typeOfLayout="grid", x=3, y=3, name="Simulation of a boardGame", windowTitle="myGame"):
        """
        Declaration of a new model

        Args:
            width (int): width of the main window in pixels (default:1800)
            height (int): height of the main window in pixels (default:900)
            typeOfLayout ("vertical", "horizontal" or "grid"): the type of layout used to position the different graphic elements of the simulation (default:"grid")
            x (int, optional): used only for grid layout. defines the number layout grid width (default:3)
            y (int, optional): used only for grid layout. defines the number layout grid height (default:3)
            name (str, optional): the name of the model. (default:"Simulation")
            windowTitle (str, optional): the title of the main window of the simulation (default :"myGame")
        """
        super().__init__()
        # Definition the size of the window ( temporary here)
        screensize = GetSystemMetrics(0), GetSystemMetrics(1)
        self.setGeometry(
            int((screensize[0]/2)-width/2), int((screensize[1]/2)-height/2), width, height)
        # Init of variable of the Model
        self.name = name
        # Definition of the title of the window
        self.setWindowTitle(self.name) if windowTitle is None else self.setWindowTitle(windowTitle)
        # We allow the drag in this widget
        self.setAcceptDrops(True)

        # Definition of variable
        # Definition for all gameSpaces
        self.gameSpaces = {}
        self.TextBoxes = []
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
        else:
            self.layoutOfModel = SGGridLayout(x, y)
        self.isMoveToCoordsUsed = False
        # To limit the number of zoom out of players
        self.numberOfZoom = 2
        # To keep in memory all the povs already displayed in the menu
        self.listOfPovsForMenu = []
        # To handle the flow of time in the game
        self.users = ["Admin"]
        self.timeManager = SGTimeManager(self)
        # List of players
        self.players = {}
        self.currentPlayer = None

        self.userSelector = None
        self.myTimeLabel = None

        self.listOfSubChannel = []
        self.listOfMajs = []
        self.processedMAJ = set()
        self.timer = QTimer()
        self.haveToBeClose = False
        self.mqtt=False #--> TO BE DELETED?
        self.mqttMajType=None

        self.dictAgentsAtMAJ={} #--> TO BE DELETED?
        self.actionsFromBrokerToBeExecuted=[]
        self.simulationVariablesAtMAJ=[] 

        self.initUI()

        self.initModelActions()

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
        self.customContextMenuRequested.connect(self.show_menu)

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
    
    def initAfterOpening(self):
        QTimer.singleShot(100, self.updateFunction)
        if self.currentPlayer is None:
            possibleUsers = self.getUsers_withControlPanel()
            if possibleUsers != [] : self.setCurrentPlayer(possibleUsers[0])
        if not self.isMoveToCoordsUsed : QTimer.singleShot(100, self.moveWidgets)
        
    
    def updateFunction(self):
        aList = self.getAllAgents()
        if not aList : return False
        for aAgent in aList:
            aAgent.updateAgentByRecreating_it()

    def setDashboards(self):
        dashboards=self.getGameSpaceByClass(SGDashBoard)
        for aDashBoard in dashboards:
            aDashBoard.showIndicators()
    
    # Create the menu of the menu
    def createMenu(self):
        aAction = QAction(QIcon("./icon/play.png"), " &play", self)
        aAction.triggered.connect(self.nextTurn)
        self.menuBar().addAction(aAction)

        self.menuBar().addSeparator()

        aAction = QAction(QIcon("./icon/zoomPlus.png"), " &zoomPlus", self)
        aAction.triggered.connect(self.zoomPlusModel)
        self.menuBar().addAction(aAction)

        aAction = QAction(QIcon("./icon/zoomLess.png"), " &zoomLess", self)
        aAction .triggered.connect(self.zoomLessModel)
        self.menuBar().addAction(aAction)

        aAction  = QAction(QIcon("./icon/zoomToFit.png"), " &zoomToFit", self)
        aAction .triggered.connect(self.zoomFitModel)
        self.menuBar().addAction(aAction)

        self.menuBar().addSeparator()

        self.symbologyMenu = self.menuBar().addMenu(QIcon("./icon/symbology.png"), "&Symbology")
        self.symbologiesInSubmenus = {}
        self.keyword_borderSubmenu = ' border'

        self.settingsMenu = self.menuBar().addMenu(QIcon("./icon/settings.png"), " &Settings")

    # Create all the action related to the menu

    def createAction(self): #--> To be DELETED?
        self.save = QAction(QIcon("./icon/save.png"), " &save", self)
        self.save.setShortcut("Ctrl+s")
        self.save.triggered.connect(self.saveTheGame)

        self.backward = QAction(
            QIcon("./icon/backwardArrow.png"), " &backward", self)
        self.backward.triggered.connect(self.backwardAction)

        self.forward = QAction(
            QIcon("./icon/forwardArrow.png"), " &forward", self)
        self.forward.triggered.connect(self.forwardAction)

        self.inspect = QAction(
            QIcon("./icon/inspect.png"), " &inspectAll", self)
        self.inspect.triggered.connect(self.inspectAll)

        self.extractPng = QAction(" &ToPNG", self)
        self.extractPng.triggered.connect(self.extractPngFromWidget)
        self.extractSvg = QAction(" &ToSVG", self)
        self.extractSvg.triggered.connect(self.extractSvgFromWidget)
        self.extractHtml = QAction(" &ToHtml", self)
        self.extractHtml.triggered.connect(self.extractHtmlFromWidget)

        self.changeThePov = QAction(" &default", self)

    # Zoom
    
    def zoomPlusModel(self):
        pass

    def zoomLessModel(self):
        pass

    def zoomFitModel(self):
        pass

    # Create the function for the action of the menu
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
        if isinstance(e.source(),SGEntity):
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Warning Message")
            msg_box.setText("A " + e.source().classDef.entityName +" cannot be moved here")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.setDefaultButton(QMessageBox.Ok)
            msg_box.exec_()
            return
        position = e.pos()
        position.setX(position.x()-int(e.source().getSizeXGlobal()/2))
        position.setY(position.y()-int(e.source().getSizeYGlobal()/2))
        e.source().move(position)

        e.setDropAction(Qt.MoveAction)
        e.accept()

    # Contextual Menu
    def show_menu(self, point):
        menu = QMenu(self)

        option1 = QAction("LayoutCheck", self)
        option1.triggered.connect(self.moveWidgets)
        menu.addAction(option1)

        if self.rect().contains(point):
            menu.exec_(self.mapToGlobal(point))


# -----------------------------------------------------------------------------------------
# Definiton of the methods who the modeler will use

# For create elements
    # To create a grid
    def newCellsOnGrid(self, columns=10, rows=10, format="square", size=30, gap=0, color=Qt.gray,moveable=True,name=""):
        """
        Create a grid that contains cells

        Args:
            columns (int): number of columns (width).
            rows (int): number of rows (height).
            format ("square", "hexagonal"): shape of the cells. Defaults to "square".
            size (int, optional): size of the cells. Defaults to 30.
            gap (int, optional): gap size between cells. Defaults to 0.
            color (a color, optional): background color of the grid . Defaults to Qt.gray.
            moveable (bool) : grid can be moved by clic and drage. Defaults to "True".
            name (st): name of the grid.

        Returns:
            aCellDef: the cellDef that defines the cells that have been placed on a grid
        """
        # Create a grid
        aGrid = SGGrid(self, name, columns, rows, format, gap, size, color, moveable)

        # Create a CellDef populate the grid with it
        aCellDef = self.newCellsFromGrid(aGrid)
        aGrid.cellDef =aCellDef

        self.gameSpaces[name] = aGrid

        # Realocation of the position thanks to the layout
        aGrid.globalPosition()
        return aCellDef
    
    def newCellsFromGrid(self,grid):
        CellDef = SGCellDef(grid, grid.cellShape,grid.size,defaultColor=Qt.white,entDefAttributesAndValues=None)
        self.cellOfGrids[grid.id] = CellDef
        for lin in range(1, grid.rows + 1):
            for col in range(1, grid.columns + 1):
                CellDef.newCell(col, lin)
        return CellDef

    # To get the CellDef corresponding to a Grid
    def getCellDef(self, aGrid):
        if isinstance(aGrid,SGCellDef): return aGrid
        return self.cellOfGrids[aGrid.id]


    # To get all the cells of the collection
    # If several grids, this method only returns the cells of the first grid
    def getCells(self,grid=None):
        if grid == None:
            grid = self.getGrids()[0]
        return self.getCellDef(grid).entities
    
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
        aVoid.move(aVoid.getStartXBase(), aVoid.getStartYBase())
        return aVoid

    # To create a Legend
    def newLegend(self, name='Legend', showAgentsWithNoAtt=False):
        """
        To create an Admin Legend (with all the cell and agent values)

        Args:
        Name (str): name of the Legend (default : Legend)
        showAgentsWithNoAtt (bool) : display of non attribute dependant agents (default : False)

        """
        selectedSymbologies=self.getAllCheckedSymbologies()
        aLegend = SGLegend(self).initialize(self, name, selectedSymbologies, 'Admin', showAgentsWithNoAtt)
        self.gameSpaces[name] = aLegend
        # Realocation of the position thanks to the layout
        aLegend.globalPosition()
        self.applyPersonalLayout()
        return aLegend
    
    def newUserSelector(self):
        """
        To create a User Selector in your game. Functions automatically with the players declared in your model. 

        """
        if len(self.getUsers_withControlPanel()) > 1 and len(self.players) > 0:
            userSelector = SGUserSelector(self, self.getUsers_withControlPanel())
            self.userSelector = userSelector
            self.gameSpaces["userSelector"] = userSelector
            # Realocation of the position thanks to the layout
            userSelector.globalPosition()
            self.applyPersonalLayout()
            return userSelector
        else:
            print('You need to add players to the game')

    # To create a New kind of agents
    def newAgentSpecies(self, name, shape, entDefAttributesAndValues=None, defaultSize=15, defaultColor=Qt.black, locationInEntity="random"):
        """
        Create a new specie of Agents.

        Args:
            name (str) : the species name
            shape (str) : the species shape ("circleAgent","squareAgent", "ellipseAgent1","ellipseAgent2", "rectAgent1","rectAgent2", "triangleAgent1","triangleAgent2", "arrowAgent1","arrowAgent2")
            dictAttributes (dict) : all the species attributs with all the values
            defaultSize (int) : the species shape size (Default=10)
            locationInEntity (str, optionnal) : topRight, topLeft, center, bottomRight, bottomLeft, random 
        Return:
            a nested dict for the species
            a species

        """
        aAgentSpecies = SGAgentDef(self, name, shape, defaultSize, entDefAttributesAndValues, defaultColor,locationInEntity)
        self.agentSpecies[name]=aAgentSpecies
        return aAgentSpecies

    def getAgentSpeciesName(self):
        # send back a list of the names of all the species
        return list(self.agentSpecies.keys())
    
    def getAgentSpeciesDict(self):
        # send back a list of all the species Dict (specie definition dict)
        return list(self.agentSpecies.values())

    def getAgentSpecieDict(self, aSpecieName):
        # send back the specie dict (specie definition dict) that corresponds to aSpecieName
        return self.agentSpecies.get(aSpecieName)

    def getAgentsOfSpecie(self, aSpecieName):
        agentDef = self.getAgentSpecieDict(aSpecieName)
        if agentDef is None:  return None
        else: return agentDef.entities[:]

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
        return next((entDef for entDef in self.getEntitiesDef() if entDef.entityName == entityName), None)

    #This method is used by updateServer to retrieve an entity (cell , agents) used has argument in a game action 
    def getSGEntity_withIdentfier(self, aIdentificationDict):
        entDef = self.getEntityDef(aIdentificationDict['entityName'])
        aId = aIdentificationDict['id']
        targetEntity = entDef.getEntity(aId)
        return targetEntity 

    #This method is used by updateServer to retrieve any type of SG object (eg. GameAction or Entity) 
    def getSGObject_withIdentfier(self, aIdentificationDict):
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
    
    def newAgent_ADMINONLY(self, aGrid, aAgtDef, ValueX, ValueY, adictAttributes, anAgentID):
        """
        Do not use.
        """
        locationCell = aGrid.getCell_withCoords(int(ValueX), int(ValueY))
        aAgent = SGAgent(locationCell, aAgtDef.defaultsize,adictAttributes, aAgtDef.defaultShapeColor, aAgtDef)
        aAgent.isDisplay = True
        aAgent.id = anAgentID
        aAgtDef.entities.append(aAgent)
        aAgent.show()
        return aAgent


    def getIdFromPrivateId(self, aPrivateID, aSpeciesName):
        result=re.search(f'{aSpeciesName}(\d+)', aPrivateID)
        if result:
            anID=result.group(1)
            return anID
        raise ValueError("Check again!")
    
    def checkAndUpdateWatchers(self):
        for entDef in self.getEntitiesDef():
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
            actions (lambda function): Actions the cell performs during the phase (add, delete, move...)
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

    def getPlayerObject(self, playerName): # TO BE RENAMED?
        if playerName == "Admin":
            return playerName
        else:
            return self.players[playerName]
    
    def setCurrentPlayer(self, aUserName):
        """
        Set the Active Player at the initialisation

        Args:
            playerName (str): predefined playerName

        """
        if aUserName in self.getUsersName():
            self.currentPlayer = aUserName
            #update the userSelector interface
            if self.userSelector is not None:
                self.userSelector.setCheckboxesWithSelection(aUserName)
            #update the ControlPanel and adminLegend interfaces
            for aItem in self.getControlPanels()+self.getAdminLegends() :
                aItem.isActive = (aItem.playerName == self.currentPlayer)
                aItem.update()
    



    def getUsersName(self):
        aList = [aP.name for aP in list(self.players.values())]
        aList.append('Admin')
        return aList

    def getUserControlPanelOrLegend(self, aUserName):
        self.getLegends()

    # To select only users with a control panel
    def getUsers_withControlPanel(self):
        selection=[]
        if self.getAdminLegend() != None:
            selection.append('Admin')     
        for aP in self.players.values():
            if aP.controlPanel !=  None:
                selection.append(aP.name) 
        return selection

    # To create a Time Label
    def newTimeLabel(self, title=None, backgroundColor=Qt.white, borderColor=Qt.black, textColor=Qt.black):
        """
        Create the visual time board of the game
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
        self.applyPersonalLayout()

        return aTimeLabel

    # To create a Text Box
    def newTextBox(self, textToWrite='Welcome in the game !', title='Text Box'):
        """
        Create a text box

        Args:
        textToWrite (str) : displayed text in the widget (default: "Welcome in the game!")
        title (str) : name of the widget (default: "Text Box")

        """
        aTextBox = SGTextBox(self, textToWrite, title)
        self.TextBoxes.append(aTextBox)
        self.gameSpaces[title] = aTextBox
        # Realocation of the position thanks to the layout
        aTextBox.globalPosition()
        self.applyPersonalLayout()

        return aTextBox

    def deleteTextBox(self, titleOfTheTextBox):
        del self.gameSpaces[titleOfTheTextBox]

    def getTextBoxHistory(self, TextBoxes):
        for aTextBox in TextBoxes:
            print(str(aTextBox.id)+' : '+str(aTextBox.history))

    def newDashBoard(self, title='DashBoard', borderColor=Qt.black, backgroundColor=Qt.transparent, textColor=Qt.black):
        """
        Create the score board of the game

        Args:
        title (str) : title of the widget (default:"Phases&Rounds")
        backgroundColor (Qt Color) : color of the background (default : Qt.transparent)
        borderColor (Qt Color) : color of the border (default : Qt.black)
        textColor (Qt Color) : color of the text (default : Qt.black)
        """
        aDashBoard = SGDashBoard(
            self, title, borderColor, backgroundColor, textColor)
        self.gameSpaces[title] = aDashBoard
        # Realocation of the position thanks to the layout
        aDashBoard.globalPosition()
        self.applyPersonalLayout()

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
        self.applyPersonalLayout()

        return aEndGameRule

    def round(self):
        """Return the actual ingame round"""
        return self.timeManager.currentRoundNumber

    def getCurrentPhase(self):
        """Return the actual ingame phase"""
        return self.timeManager.currentPhaseNumber
    
    def newSimVariable(self,name,initValue,color=Qt.black,isDisplay=True):
        aSimVar=SGSimulationVariable(self,initValue,name,color,isDisplay)
        self.simulationVariables.append(aSimVar)
        return aSimVar

    # ---------
# Layout

    # To get a gameSpace in particular

    def getGameSpaceByName(self, name):
        return self.gameSpaces[name]

    def getGameSpaceByClass(self,aClass):
        gameSpaces=[aGameSpace for aName,aGameSpace in self.gameSpaces.items() if isinstance(aGameSpace,aClass)]
        return gameSpaces
    
    # To apply the layout to all the current game spaces
    def applyPersonalLayout(self):
        self.layoutOfModel.ordered()
        for anElement in self.gameSpaces:
            if (self.typeOfLayout == "vertical"):
                self.gameSpaces[anElement].move(self.gameSpaces[anElement].startXBase, self.gameSpaces[anElement].startYBase +
                                                20*self.layoutOfModel.getNumberOfAnElement(self.gameSpaces[anElement]))
            elif (self.typeOfLayout == "horizontal"):
                self.gameSpaces[anElement].move(self.gameSpaces[anElement].startXBase+20*self.layoutOfModel.getNumberOfAnElement(
                    self.gameSpaces[anElement]), self.gameSpaces[anElement].startYBase)
            else:
                pos = self.layoutOfModel.foundInLayout(
                    self.gameSpaces[anElement])
                self.gameSpaces[anElement].move(
                    self.gameSpaces[anElement].startXBase+20*pos[0], self.gameSpaces[anElement].startYBase+20*pos[1])
                
    
    def checkLayoutIntersection(self,name,element,otherName,otherElement):
        if name!=otherName and (element.geometry().intersects(otherElement.geometry()) or element.geometry().contains(otherElement.geometry())):
            return True
        return False
    
    def moveWidgets(self):
        for name,element in self.gameSpaces.items():
            for otherName,otherElement in self.gameSpaces.items():
                while self.checkLayoutIntersection(name,element,otherName,otherElement):
                    if element.areaCalc() <= otherElement.areaCalc():
                        local_pos=element.pos()
                        element.move(local_pos.x()+10,local_pos.y()+10)
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

    def checkSymbologyinMenuBar(self, aClassDef,nameOfSymbology):
        if self.symbologyMenu is None: return False
        symbologies = self.getSymbologiesOfSubmenu(aClassDef.entityName)
        for aSymbology in symbologies:
            if aSymbology.text() == nameOfSymbology:
                aSymbology.setChecked(True)
            else: aSymbology.setChecked(False)

    def menu_item_triggered(self):
        # get the triggered QAction object
        selectedSymbology = self.sender()
        # browse the dict to uncheck other symbologies
        for symbologies in self.symbologiesInSubmenus.values():
            if selectedSymbology in symbologies:
                [aSymbology.setChecked(False) for aSymbology in symbologies if aSymbology is not selectedSymbology]
        for aLegend in self.getAdminLegends():
            aLegend.updateWithSymbologies(self.getAllCheckedSymbologies())
        self.update() #update all the interface display

    def getSymbologiesOfSubmenu(self, submenuName):
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
        # It is supposed to be for a given Grid
        # for the moment we assume that its for the main (first) grid
        if grid is None: grid = self.getGrids()[0]
        cellDef = self.getCellDef(grid)
        selectedSymbologies={}
        entitiesDef=[cellDef] + list(self.agentSpecies.values())
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

    # To get the list of Agent POV
    def getAgentPOVs(self): #--> To be DELETED?
        list_POV = {}
        for specieName, agentDef in self.agentSpecies.items():
            list_POV[specieName]= agentDef.povShapeColor
        return list_POV

    def getPovWithAttribut(self, attribut):  #--> To be DELETED?
        for aGrid in self.getGrids():
            for aPov in self.cellOfGrids[aGrid.id]["ColorPOV"]:
                for anAttribut in self.cellOfGrids[aGrid.id]["ColorPOV"][aPov].keys():
                    if attribut == anAttribut:
                        return aPov

    def getBorderPovWithAttribut(self, attribut):  #--> To be DELETED?
        for aGrid in self.getGrids():
            for aBorderPov in self.cellOfGrids[aGrid.id]["BorderPOV"]:
                for anAttribut in self.cellOfGrids[aGrid.id]["BorderPOV"][aBorderPov].keys():
                    if attribut == anAttribut:
                        return aBorderPov

    # -----------------------------------------------------------
    # TimeManager functions

    def getTimeManager(self):
        return self.timeManager

    # -----------------------------------------------------------
    # Game mechanics function

    def newCreateAction(self, anObjectType, dictAttributes=None, aNumber='infinite', listOfRestriction=[], feedback=[], conditionOfFeedback=[]):
        """
        Add a Create GameAction to the game.

        Args:
        - anObjectType : a AgentSpecies or the keyword "Cell"
        - a Number (int) : number of utilisation, could use "infinite"
        - dictAttributes (dict) : attribute with value concerned, could be None

        """
        aClassDef = self.getEntityDef(anObjectType)
        if aClassDef is None : raise ValueError('Wrong format of entityDef')
        if aNumber == "infinite": aNumber = 9999999
        return SGCreate(aClassDef,  dictAttributes, aNumber,listOfRestriction, feedback, conditionOfFeedback)

    def newUpdateAction(self, anObjectType, dictAttributes={}, aNumber='infinite',listOfRestriction=[], feedback=[], conditionOfFeedback=[]):
        """
        Add a Update GameAction to the game.

        Args:
        - anObjectType : a AgentSpecies or the keyword "Cell"
        - a Number (int) : number of utilisation, could use "infinite"
        - dictAttributes (dict) : attribute with value concerned, could be None

        """
        aClassDef = self.getEntityDef(anObjectType)
        if aClassDef is None : raise ValueError('Wrong format of entityDef')
        if aNumber == "infinite": aNumber = 9999999
        return SGUpdate(aClassDef,  dictAttributes,aNumber, listOfRestriction, feedback, conditionOfFeedback)

    def newDeleteAction(self, anObjectType, aNumber='infinite', listOfConditions=[], feedback=[], conditionOfFeedback=[]):
        """
        Add a Delete GameAction to the game.

        Args:
        - anObjectType : a AgentSpecies
        - a Number (int) : number of utilisation, could use "infinite"
        - dictAttributes (dict) : attribute with value concerned, could be None

        """
        aClassDef = self.getEntityDef(anObjectType)
        if aClassDef is None : raise ValueError('Wrong format of entityDef')
        if aNumber == "infinite": aNumber = 9999999
        return SGDelete(aClassDef, aNumber, listOfConditions, feedback, conditionOfFeedback)

    def newMoveAction(self, anObjectType, aNumber='infinite', listOfConditions=[], feedback=[], conditionOfFeedback=[], feedbackAgent=[], conditionOfFeedBackAgent=[]):
        """
        Add a MoveAction to the game.

        Args:
        - anObjectType : a AgentSpecies
        - a Number (int) : number of utilisation, could use "infinite"
        - listOfConditions (list of lambda functions) : conditions on the moving Entity
        """
        aClassDef = self.getEntityDef(anObjectType)
        if aClassDef is None : raise ValueError('Wrong format of entityDef')
        if aNumber == "infinite": aNumber = 9999999
        return SGMove(aClassDef, aNumber, listOfConditions, feedback, conditionOfFeedback, feedbackAgent, conditionOfFeedBackAgent)

    # -----------------------------------------------------------
    # Getter

    def getGrid(self,anObject):
        if isinstance(anObject,SGCellDef): return anObject.grid
        elif isinstance(anObject,SGGrid): return anObject
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

    def getAdminLegend(self):
        return next((item for item in self.getLegends() if item.isAdminLegend()), None)

    def getAdminLegends(self): #useful in case they are several admin legends
        return [item for item in self.getLegends() if item.isAdminLegend()]
    
    def getSelectedLegend(self):
        return next((item for item in self.getLegends() if item.isActive), None)

    def getSelectedLegendItem(self):
        return next((item.selected for item in self.getLegends() if item.isActiveAndSelected()), None)

    def getGameAction_withClassAndId(self,aClassName,aId):
        return next((item for item in self.getAllGameActions() if item.__class__.__name__==aClassName and item.id==aId), None)
        
            
    # To change the number of zoom we currently are
    def setNumberOfZoom(self, number):
        self.numberOfZoom = number

    # To set User list
    def setUsers(self, listOfUsers):
        self.users = listOfUsers

    # To open and launch the game without a mqtt broker
    def launch(self):
        """
        Launch the game.
        """
        self.setDashboards()
        self.show()
        self.initAfterOpening()

    # To open and launch the game
    def launch_withMQTT(self,majType):
        """
        Launch the game with mqtt protocol

        Args:
            majType (str): "Phase" or "Instantaneous"
        
        """
        self.clientId= uuid.uuid4().hex
        self.majTimer = QTimer(self)
        self.majTimer.timeout.connect(self.onMAJTimer)
        self.majTimer.start(100)
        self.initMQTT()
        self.mqttMajType=majType
        self.setDashboards()
        self.show()
        self.initAfterOpening()

    # Return all gameActions of all players
    def getAllGameActions(self):
        aList= []
        for player in self.players.values():
            aList.extend(player.gameActions)
        return aList

    # Function that process the message
    def handleMessageMainThread(self,msg_list): # --> TO BE DELETED?
        processedMajs=set()
        # CELL MANAGEMENT
        gridNumber=0
        for aGrid in self.getGrids():
            cellCount=int(msg_list[1][gridNumber])
            allCells = []
            for aCell in list(self.getCells(aGrid)):
                allCells.append(aCell)
            for i in range(len(msg_list[2:cellCount+1])):
                allCells[i].isDisplay = msg_list[2+i][0]
                allCells[i].dictAttributes = msg_list[2+i][1]
                allCells[i].owner = msg_list[2+i][2]
            gridNumber+=1

        # AGENT MANAGEMENT
        nbToStart=sum(msg_list[1])
        for j in range(len(msg_list[nbToStart+2:-5])):
            entityName=msg_list[nbToStart+2+j][0]
            id=msg_list[nbToStart+2+j][1]
            dictAttributes=msg_list[nbToStart+2+j][2]
            owner=msg_list[nbToStart+2+j][3]
            agentX=msg_list[nbToStart+2+j][4]
            agentY=msg_list[nbToStart+2+j][5]
            grid=msg_list[nbToStart+2+j][6]
            theGrid=self.getGrid_withID(grid)
            aAgtDef=self.getEntityDef(entityName)

            self.dictAgentsAtMAJ[j]=[theGrid,aAgtDef,agentX,agentY,dictAttributes,id]
        
        # AGENT SPECIES MEMORY ID
        agentDef_IDincr=msg_list[-5][0]
        for entityName, aIDincr in dict(agentDef_IDincr).items():
            aAgtDef=self.getEntityDef(entityName)
            aAgtDef.IDincr=aIDincr

        # TIME MANAGEMENT
        self.timeManager.currentPhaseNumber = msg_list[-4][0]
        self.timeManager.currentRoundNumber = msg_list[-4][1]
        if self.myTimeLabel is not None:
            self.myTimeLabel.updateTimeLabel()
        if self.timeManager.currentPhaseNumber == 0:
            # We reset GM
            for gm in self.getAllGameActions():
                gm.reset()

        # SIMULATION VARIABLES
        self.simulationVariablesAtMAJ=msg_list[-3]

        self.update()
        print("Update processed !")

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
        self.client = mqtt_client.Client(self.currentPlayer)
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
            if msg_list[0][0] != self.clientId: #This test should be unnecessary now --> TO BE DELETED?
                self.deleteAllAgents()
                self.handleMessageMainThread(msg_list)
            else:
                print("Own update, no action required.")   

        self.connect_mqtt()
        self.mqtt=True #--> TO BE DELETED?

        self.client.subscribe("Gamestates") #--> TO BE DELETED?
        self.client.subscribe("gameAction_performed")
        self.client.subscribe("nextTurn")
        self.client.subscribe("execute_method")
        self.client.on_message = on_message
        self.listOfSubChannel.append("Gamestates") #--> TO BE DELETED?
        
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
        aSGObject = self.getSGObject_withIdentfier(aIdentificationDict)
        
        methodToExe = getattr(aSGObject,methodNameToExe) # this code retrieves the method to be executed and places it in the 'methodToExe' variable. This 'methodToExe' variable can now be used as if it were the method to be executed.
        #retrieve the arguments of the method to be executed
        listOfArgs=[]
        for aArgSpec in msg['listOfArgs']:
            if isinstance(aArgSpec, list) and len(aArgSpec)>0 and aArgSpec[0]== 'SGObjectIdentifer':
                aArg=self.getSGObject_withIdentfier(aArgSpec[1])
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

    # Send a message
    def submitMessage(self):   #--> TO BE DELETED?
        print(self.currentPlayer+" send a message")
            

        # First infos : identifiers of the message [clientId,majID,currentPlayer]
        message = "[['"+self.clientId+"',"
        message += self.currentPlayer+"'],"

        # Next infos : Cells of the different grids
        allCells = []
        listCellsByGrid=[]
        theAgents = self.getAllAgents()
        
        # speciesMemoryIdDict={}
        
        for aGrid in self.getGrids():
            for aCell in list(self.getCells(aGrid)):
                allCells.append(aCell)
            listCellsByGrid.append(len(allCells))
        message = message+str(listCellsByGrid)+","
        for aNumberOfCells in listCellsByGrid:
            for i in range(aNumberOfCells):
                message = message+"["
                message = message+str(allCells[i].isDisplay)
                message = message+","
                message = message+str(allCells[i].dictAttributes)
                message = message+","
                message = message+"'"+str(allCells[i].owner)+"'"
                message = message+"]"
                if i != aNumberOfCells:
                    message = message+","

        # Next : Agents
        for aAgent in theAgents:
            message = message+"["
            message = message+"'"+str(aAgent.classDef.entityName)+"'"
            message = message+","
            message = message+"'"+str(aAgent.id)+"'"
            message = message+","
            message = message+str(aAgent.dictAttributes)
            message = message+","
            message = message+"'"+str(aAgent.owner)+"'"
            message = message+","
            message = message+"'"+str(aAgent.cell.xPos)+"'"
            message = message+","
            message = message+"'"+str(aAgent.cell.yPos)+"'"
            message = message+","
            message = message+"'"+str(aAgent.cell.grid.id)+"'"
            message = message+"]"
            message = message+","

        agentDef_IDincr={}
        for aAgtDef in self.getAgentSpeciesDict():
            agentDef_IDincr[aAgtDef.entityName]=aAgtDef.IDincr

        message = message+"["
        message = message+str(agentDef_IDincr)
        message = message+"]"
        message = message+","
        message = message+"["
        message = message+str(self.timeManager.currentPhaseNumber)
        message = message+","
        message = message+str(self.timeManager.currentRoundNumber)
        message = message+"]"
        message = message+","
        message = message+"["
        for k in range(len(self.simulationVariables)):
            message = message+str({self.simulationVariables[k].name:self.simulationVariables[k].value})
            if k != len(self.simulationVariables):
                message = message+","
        message = message+"]"
        message = message+","
        message = message+"["
        message = message+"'"+str(self.currentPlayer)+"'" # To be deleted
        message = message+"]"
        message = message+","
        message = message+str(self.listOfSubChannel) # To be deleted
        message = message+"]"
        print(message)
        return message
    
    def onMAJTimer(self):
        self.executeGameActionsAfterBrokerMsg()
        
    def updateAgentsAtMAJ(self):  #--> TO BE DELETED?
        for j in self.dictAgentsAtMAJ.keys():
            newAgent=self.newAgent_ADMINONLY(self.dictAgentsAtMAJ[j][0],self.dictAgentsAtMAJ[j][1],self.dictAgentsAtMAJ[j][2],self.dictAgentsAtMAJ[j][3],self.dictAgentsAtMAJ[j][4],self.dictAgentsAtMAJ[j][5])
            newAgent.cell.updateIncomingAgent(newAgent)
        self.dictAgentsAtMAJ={}
    
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
    

    def updateScoreAtMAJ(self):  #--> TO BE DELETED?
        for aGameSpace in self.gameSpaces:
            if isinstance(aGameSpace,SGDashBoard):
                for aIndicator in aGameSpace.indicators:
                    if isinstance(aIndicator.entity,SGSimulationVariable):
                        for aDictOfSimVar in self.simulationVariablesAtMAJ:
                            if aIndicator.entity.name == aDictOfSimVar.keys():
                                aIndicator.updateByMqtt(aDictOfSimVar.values())
        self.simulationVariablesAtMAJ=[]

