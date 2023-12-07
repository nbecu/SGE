
from PyQt5.QtSvg import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import (QAction,QMenu,QMainWindow,QMenuBar,QToolBar)
from PyQt5 import QtWidgets
from mainClasses.layout.SGVerticalLayout import*
from mainClasses.layout.SGHorizontalLayout import*
from mainClasses.layout.SGGridLayout import*
from mainClasses.gameAction.SGGameActions import* # This one might be obsolete
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
from email.policy import default
from logging.config import listen
import sys
import copy
from pathlib import Path
from pyrsistent import s
from win32api import GetSystemMetrics
from paho.mqtt import client as mqtt_client
import threading
import queue
import random
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
        self.TextBoxes = []   # Why textBoxes are not in gameSpaces ?
        # Definition of the AgentDef and CellDef
        self.agentSpecies = {}
        self.cellOfGrids = {}
        # Definition of simulation variables
        self.simulationVariables = []
        # self.IDincr = 0     TO BE REMOVED
        # We create the layout
        self.typeOfLayout = typeOfLayout
        if (typeOfLayout == "vertical"):
            self.layoutOfModel = SGVerticalLayout()
        elif (typeOfLayout == "horizontal"):
            self.layoutOfModel = SGHorizontalLayout()
        else:
            self.layoutOfModel = SGGridLayout(x, y)
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
        self.mqtt=False
        self.mqttMajType=None

        self.dictAgentsAtMAJ={}
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

        testMode=QAction(" &"+"Cursor Position", self)
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
        self.label.setText(f'Coordonnées Globales de la Souris : ({coord_x}, {coord_y})')
    
    def initAfterOpening(self):
        QTimer.singleShot(100, self.updateFunction)
        if self.currentPlayer is None:
            possibleUsers = self.getUsers_withControlPanel()
            if possibleUsers != [] : self.setCurrentPlayer(possibleUsers[0])
    
    
    def updateFunction(self):
        #This method will need to be modified so that agent are placed at the right place right from the start
        aList = self.getAllAgents()
        if not aList : return False
        for aAgent in aList:
            aAgent.updateAgentByRecreating_it()
        # self.show()

    
    # Create the menu of the menue
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
        # dictionnaire pour stocker les actions du sous-menu Symbology
        self.symbologiesInSubmenus = {}
        self.keyword_borderSubmenu = ' border'

        self.povMenu = self.menuBar().addMenu(QIcon("./icon/pov.png"), "&pov")

        self.settingsMenu = self.menuBar().addMenu(QIcon("./icon/settings.png"), " &Settings")

    # Create all the action related to the menu

    def createAction(self):
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

    # Create the function for the action of the menu
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

    # Trigger the next turn

    def nextTurn(self):
        # Eventually we can add here some conditions to allow to execute nextTurn (ex. be an Admin)
        self.timeManager.nextPhase()
        if self.mqttMajType in ["Phase","Instantaneous"]:
            self.buildNextTurnMsgAndPublishToBroker()
        # self.eventTime()

    def closeEvent(self, event):
        self.haveToBeClose = True
        self.getTextBoxHistory(self.TextBoxes)
        if hasattr(self, 'client'):
            self.client.disconnect()
        self.close()

    # Trigger the zoom in

    def zoomPlusModel(self):
        """NOT TESTED"""
        self.setNumberOfZoom(self.numberOfZoom+1)
        for aGameSpaceName in self.gameSpaces:
            self.gameSpaces[aGameSpaceName].zoomIn()
        self.update()

    # Trigger the zoom out

    def zoomLessModel(self):
        """NOT TESTED"""
        if self.numberOfZoom != 0:
            for aGameSpaceName in self.gameSpaces:
                self.gameSpaces[aGameSpaceName].zoomOut()
            self.setNumberOfZoom(self.numberOfZoom-1)
        self.update()

    # Trigger the basic zoom

    def zoomFitModel(self):
        """NOT TESTED"""
        # if the window to display is to big we zoom out and reapply the layout
        if self.layoutOfModel.getMax()[0] > self.width() or self.layoutOfModel.getMax()[1] > self.height():
            while (self.layoutOfModel.getMax()[0] > self.width() or self.layoutOfModel.getMax()[1] > self.height()):
                self.zoomLessModel()
                self.applyPersonalLayout()
        else:
            # if the window to display is to small we zoom in and out when we over do it once and then reapply the layout
            while (self.layoutOfModel.getMax()[0] < (self.width()) or self.layoutOfModel.getMax()[1] < self.height()):
                self.zoomPlusModel()
                self.applyPersonalLayout()
                if self.layoutOfModel.getMax()[0] > (self.width()) and self.layoutOfModel.getMax()[1] > self.height():
                    self.zoomLessModel()
                    self.zoomLessModel()
                    self.applyPersonalLayout()
                    break
        self.update()

    # Extract the current gameboard into png

    def extractPngFromWidget(self):
        """NOT TESTED"""
        # To be reworked
        self.window.grab().save("image.png")

    # Extract the current gameboard into svg
    def extractSvgFromWidget(self):
        """NOT TESTED"""
        generator = QSvgGenerator()
        generator.setFileName("image.svg")
        painter = QPainter(generator)
        self.window.render(painter)
        painter.end()

    # Extract the current gameboard into html
    def extractHtmlFromWidget(self):
        """To be implemented"""
        return True

    # Event
    # wheel event we zoom in or out
    def wheelEvent(self, event):
        if (event.angleDelta().y() == 120):
            self.zoomPlusModel()
        else:
            self.zoomLessModel()

    # Function to handle the drag of widget

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
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
        # This is an equivalent Expression
        # result = [cell for cell in self.getCells(aGrid) if cell.id == aId]
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
        #It is supposed to a legend for a given Grid
        # for the moment we assume that its a legend for the main (first) grid
        """
        To create an Admin Legend (with all the cell and agent values)

        Args:
        Name (str): name of the Legend (default : Legend)
        showAgentsWithNoAtt (bool) : display of non attribute dependant agents (default : False)

        """
        #For the active symbology to be the first one for each Entity
        # self.checkFirstSymbologyOfEntitiesInMenu()
        
        selectedSymbologies=self.getAllCheckedSymbologies()
        aLegend = SGLegend(self).init2(self, name, selectedSymbologies, 'Admin', showAgentsWithNoAtt)
        self.gameSpaces[name] = aLegend
        # Realocation of the position thanks to the layout
        aLegend.globalPosition()
        self.applyPersonalLayout()
        return aLegend
    
    def newUserSelector(self):
        """
        To create an User Selector in your game. Functions automatically with the players declared in your model. 

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
    def newAgentSpecies(self, name, shape, entDefAttributesAndValues=None, defaultSize=15, defaultColor=Qt.black):
        """
        Create a new specie of Agents.

        Args:
            name (str) : the species name
            shape (str) : the species shape ("circleAgent","squareAgent", "ellipseAgent1","ellipseAgent2", "rectAgent1","rectAgent2", "triangleAgent1","triangleAgent2", "arrowAgent1","arrowAgent2")
            dictAttributes (dict) : all the species attributs with all the values
            defaultSize (int) : the species shape size (Default=10)
        Return:
            a nested dict for the species
            a species

        """
        aAgentSpecies = SGAgentDef(self, name, shape, defaultSize, entDefAttributesAndValues, defaultColor)
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

    def getAgentSpeciesOLD(self):
        # ATTENTION
        # Il y a un soucis dans la façon dont les infos sur les species sont stockés, car il y a une partie qui sont dans les clés du dico self.agentSpecies[NomDeLaSpecie] et une autre partie qui est dans l'instance d'Agent (dont me='collec' et species= 'NomDeLaSpecie') qui est stockée dans self.agentSpecies[NomDeLaSpecie]['defSpecies']
        # Il faut que toutes les infos soient rassemblées au meme endroit.
        # Le plus propre serait de créer une Class SGEntityDef  qui portera toutes les infos de la specie  
        # (peut être qu'il faudra faire un SGCellDef et un SGAgentDef)
        #       voici les info pour un SGAgentDef (name, watchers, colorPov, borderPov, attributList , size, defaultSize, defaultColor, shape,  format, instancesDeCetteSpecie, methodOfPlacement)
        #       voici les info pour un SGCellDef (grid, watchers, colorPov, borderPov)  -->    apparameent ca ne stock pas les autres infos comme ( attributList , size, defaultSize, defaultColor, shape,  format)  Ces infos st peut etre ds la grid
        species=[]
        for instance in SGAgent.instances:
            if instance.me == 'collec':
                species.append(instance)
        return species

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
            # si ca ne s'affiche pas correctement, penser à essayer avec update()
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
    def newPlayer(self, name,attributesAndValues):
        """"
        Create a new player

        Args:
            name (str) : name of the Player (will be displayed)
        """
        player = SGPlayer(self, name,attributesAndValues=attributesAndValues)
        self.players[name] = player
        self.users.append(player.name)
        return player

    def getPlayerObject(self, playerName):
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

    def newDashBoard(self, title='DashBoard', displayRefresh='instantaneous', borderColor=Qt.black, backgroundColor=Qt.transparent, textColor=Qt.black):
        """
        Create the score board of the game

        Args:
        title (str) : title of the widget (default:"Phases&Rounds")
        displayRefresh (str) : type of refresh in ['instantaneous', 'withButton'] (default:'instantaneous') 
        backgroundColor (Qt Color) : color of the background (default : Qt.transparent)
        borderColor (Qt Color) : color of the border (default : Qt.black)
        textColor (Qt Color) : color of the text (default : Qt.black)
        """
        aDashBoard = SGDashBoard(
            self, title, displayRefresh, borderColor, backgroundColor, textColor)
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
        return self.timeManager.currentRound

    def getCurrentPhase(self):
        """Return the actual ingame phase"""
        return self.timeManager.currentPhase
    
    def newSimVariable(self,name,initValue,color=Qt.black,isDisplay=True):
        aSimVar=SGSimulationVariable(self,initValue,name,color,isDisplay)
        self.simulationVariables.append(aSimVar)
        return aSimVar

    # ---------
# Layout

    # To get a gameSpace in particular

    def getGameSpace(self, name):
        return self.gameSpaces[name]

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
    
    def checkLayout(self,name,element,otherName,otherElement):
        if name!=otherName and (element.geometry().intersects(otherElement.geometry()) or element.geometry().contains(otherElement.geometry())):
            #print(f"{name} intersects or contains {otherName}.")
            return True
        return False
    
    def moveWidgets(self):
        for name,element in self.gameSpaces.items():
            for otherName,otherElement in self.gameSpaces.items():
                while self.checkLayout(name,element,otherName,otherElement):
                    if element.areaCalc() <= otherElement.areaCalc():
                                local_pos=element.pos()
                                element.move(local_pos.x()+10,local_pos.y()+10)
                    else:
                        local_pos=otherElement.pos()
                        otherElement.move(local_pos.x()+10,local_pos.y()+10)

    def moveToCoords(self,gameSpaceName,x,y):
        """
        Permits to move a GameSpace at a specific coordinate based on the left upper corner

        Args:
            gameSpaceName (str) : name of the GameSpace you want to move
            x (int) : x-axis corrdinate in pixels
            y (int) : y-axis corrdinate in pixels
        """
        for name,element in self.gameSpaces.items():
            if name==gameSpaceName:
                theGameSpace=element
                break
        if theGameSpace is None:
            raise ValueError("This name doesn't exist. Please check.")
        if x < self.width() + theGameSpace.width() or x < 0:
            if y < self.height() + theGameSpace.height() or y < 0:
                theGameSpace.move(x,y)
            else:
                raise ValueError('The y value is too high or negative')
        else:
            raise ValueError('The x value is too high or negative')
        
        

    # ------
# Pov
    def getSubmenuSymbology(self, submenuName):
        # renvoie le sous-menu 
        return next((item for item in self.symbologiesInSubmenus.keys() if item.title() == submenuName), None)
        # Above code is equivalent to the following
        # if any((match := item).title() == entityName for item in self.submenuSymbology_actions.keys()):
        #     return match
        # else: return None

        # if not any((matchitem := item).title() == entityName for item in self.submenuSymbology_actions.keys()):
        #     matchitem = None
        # return matchitem


    def getOrCreateSubmenuSymbology(self, submenu_name):
        # renvoie le sous-menu (et création du sous-menu si il n'existe pas encore)
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
        # récupérer le sous-menu (avec création du sous-menu si il n'existe pas encore)
        submenu = self.getOrCreateSubmenuSymbology(submenu_name)
        # Créez un élément de menu avec une case à cocher
        item = QAction(nameOfSymbology, self, checkable=True)
        item.triggered.connect(self.menu_item_triggered)
        # Ajouter le sous-menu au menu principal
        submenu.addAction(item)
        # Ajouter les actions de sous-menu au dictionnaire pour accès facile
        self.symbologiesInSubmenus[submenu].append(item)

    def setCheckedSymbologyinMenuBar(self, aClassDef,nameOfSymbology,checkValue=True):
        #This method is not used. Could be discard
        symbologies = self.getSymbologiesOfSubmenu(aClassDef.entityName)
        if any((match := item).text() == nameOfSymbology for item in symbologies):
            match.setChecked(checkValue)
        # Above code is identical to
        # for aSymbology in symbologies:
        #     if aSymbology.text() == nameOfSymbology:
        #         aSymbology.setChecked(True)

    def checkSymbologyinMenuBar(self, aClassDef,nameOfSymbology):
        if self.symbologyMenu is None: return False
        symbologies = self.getSymbologiesOfSubmenu(aClassDef.entityName)
        for aSymbology in symbologies:
            if aSymbology.text() == nameOfSymbology:
                aSymbology.setChecked(True)
            else: aSymbology.setChecked(False)

    def menu_item_triggered(self):
        # Obtener l'objet QAction qui a été déclenché
        selectedSymbology = self.sender()
        # Parcourer le dictionnaire pour décocher les autres éléments du même sous-menu
        for symbologies in self.symbologiesInSubmenus.values():
            if selectedSymbology in symbologies:
                [aSymbology.setChecked(False) for aSymbology in symbologies if aSymbology is not selectedSymbology]
                # Above code is identical to      
                # for aSymbology in symbologies :
                #     if aSymbology is not selectedSymbology:
                #         aSymbology.setChecked(False)
                # break
        for aLegend in self.getAdminLegends():
            aLegend.updateWithSymbologies(self.getAllCheckedSymbologies())
        self.update() #rafraichi l'ensemble de l'affichage de l'interface'

    def getSymbologiesOfSubmenu(self, submenuName):
        # return the  symbologies of a entity present in tyhe menuBar
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
        #It is supposed to be for a given Grid
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
    def getAgentPOVs(self):
        list_POV = {}
        for specieName, agentDef in self.agentSpecies.items():
            list_POV[specieName]= agentDef.povShapeColor
        return list_POV

    def getPovWithAttribut(self, attribut):
        for aGrid in self.getGrids():
            for aPov in self.cellOfGrids[aGrid.id]["ColorPOV"]:
                for anAttribut in self.cellOfGrids[aGrid.id]["ColorPOV"][aPov].keys():
                    if attribut == anAttribut:
                        return aPov

    def getBorderPovWithAttribut(self, attribut):
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

    def newCreateAction(self, anObjectType, aNumber, aDictOfAcceptedValue=None, listOfRestriction=[], feedback=[], conditionOfFeedback=[]):
        """
        Add a Create GameAction to the game.

        Args:
        - anObjectType : a AgentSpecies or the keyword "Cell"
        - a Number (int) : number of utilisation, could use "infinite"
        - aDictOfAcceptedValue (dict) : attribute with value concerned, could be None

        """
        aClassDef = self.getEntityDef(anObjectType)
        if aClassDef is None : raise ValueError('Wrong format of entityDef')
        if aNumber == "infinite": aNumber = 9999999
        return SGCreate(aClassDef, aNumber, aDictOfAcceptedValue, listOfRestriction, feedback, conditionOfFeedback)

    def newUpdateAction(self, anObjectType, aNumber, aDictOfAcceptedValue={}, listOfRestriction=[], feedback=[], conditionOfFeedback=[]):
        """
        Add a Update GameAction to the game.

        Args:
        - anObjectType : a AgentSpecies or the keyword "Cell"
        - a Number (int) : number of utilisation, could use "infinite"
        - aDictOfAcceptedValue (dict) : attribute with value concerned, could be None

        """
        aClassDef = self.getEntityDef(anObjectType)
        if aClassDef is None : raise ValueError('Wrong format of entityDef')
        if aNumber == "infinite": aNumber = 9999999
        return SGUpdate(aClassDef, aNumber, aDictOfAcceptedValue, listOfRestriction, feedback, conditionOfFeedback)

    def newDeleteAction(self, anObjectType, aNumber, listOfConditions=[], feedback=[], conditionOfFeedback=[]):
        """
        Add a Delete GameAction to the game.

        Args:
        - anObjectType : a AgentSpecies
        - a Number (int) : number of utilisation, could use "infinite"
        - aDictOfAcceptedValue (dict) : attribute with value concerned, could be None

        """
        aClassDef = self.getEntityDef(anObjectType)
        if aClassDef is None : raise ValueError('Wrong format of entityDef')
        if aNumber == "infinite": aNumber = 9999999
        return SGDelete(aClassDef, aNumber, listOfConditions, feedback, conditionOfFeedback)

    def newMoveAction(self, anObjectType, aNumber, listOfConditions=[], feedback=[], conditionOfFeedback=[], feedbackAgent=[], conditionOfFeedBackAgent=[]):
        #! TO DO : rajouter la possibilité de mettre une condition sur l'entité de destination 
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
        self.show()
        self.initAfterOpening()

    # Return all gameActions of all players
    def getAllGameActions(self):
        aList= []
        for player in self.players.values():
            aList.extend(player.gameActions)
        return aList

    # Function that process the message
    def handleMessageMainThread(self,msg_list):
        processedMajs=set()
        if msg_list[0][0] not in processedMajs:
            print("Update processing...")
        else:
            # Ce n'arrive jamais car la Maj n'est jamais ajouté à la list processedMajs
            # Du coup, il faut supprimer cette vérification qui ne sert rien
            return print("Maj already processed !")
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
        # speciesMemoryIdDict=msg_list[-5][0]
        # for aSpeciesName, speciesMemoryID in dict(speciesMemoryIdDict).items():
        #     theSpecies=self.getAgentsOfSpecie(aSpeciesName)
        #     theSpecies.memoryID=speciesMemoryID
        agentDef_IDincr=msg_list[-5][0]
        for entityName, aIDincr in dict(agentDef_IDincr).items():
            aAgtDef=self.getEntityDef(entityName)
            aAgtDef.IDincr=aIDincr

        # TIME MANAGEMENT
        self.timeManager.currentPhase = msg_list[-4][0]
        self.timeManager.currentRound = msg_list[-4][1]
        if self.myTimeLabel is not None:
            self.myTimeLabel.updateTimeLabel()
        if self.timeManager.currentPhase == 0:
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
            if msg_list[0][0] != self.clientId: #This test should be unnecessary now
                self.deleteAllAgents()
                self.handleMessageMainThread(msg_list)
            else:
                print("Own update, no action required.")   

        self.connect_mqtt()
        self.mqtt=True

        self.client.subscribe("Gamestates")
        self.client.subscribe("gameAction_performed")
        self.client.subscribe("nextTurn")
        self.client.subscribe("execute_method")
        self.client.on_message = on_message
        self.listOfSubChannel.append("Gamestates") #Je ne pense pas que ce soit utile
        
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

        
    #Method to process the incoming of a "execute_method" message
    # cette méthode est une généralisation de process game_action et process nextTurn.
    # Pour l'instant cette méthode n'est pas utilisé mais elle permet de pouvoir demander l'execution coté client, de n'importe quelle méthode executé coté server
    # pour cela il suffit de mettre coté server un code du type :
    # self.model.buildExeMsgAndPublishToBroker('execute_method',dictAvec_class_name_id_method, *args (les arguments les uns apres les autres) )
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
        
        methodToExe = getattr(aSGObject,methodNameToExe) # ce code récupère la méthode a exécuter et la met dans la variable  'methodToExe'. Cette variable 'methodToExe' peut à présent etre utilisé comme si il s'agissait de la méthode à exécuter
        #récuprération des arguments de la méthode à exécuter
        listOfArgs=[]
        for aArgSpec in msg['listOfArgs']:
            if isinstance(aArgSpec, list) and len(aArgSpec)>0 and aArgSpec[0]== 'SGObjectIdentifer':
                aArg=self.getSGObject_withIdentfier(aArgSpec[1])
            else:
                aArg= aArgSpec
            listOfArgs.append(aArg)

        #execution de la méthode avec ces arguments
        methodToExe(*listOfArgs)

        # le code ci-dessous peut etre utilsié pour différer l'execution de la méthode au thread en dehors du thread de lecture mqtt
        # self.actionsFromBrokerToBeExecuted.append({
        #     'action_type':'execute_method',
        #     'boundMethod':methodToExe,     # une bound method   est une méthod déjà associé à l'objet qui va l'executer
        #      'listOfArgs':listOfArgs
        #      })


    # publish on mqtt broker the state of all entities of the world
    def publishEntitiesState(self):
        #JUst to test another mqqt method, I skip this instruction temporarily
        return
        if hasattr(self, 'client'):
            self.client.publish('Gamestates', self.submitMessage())


    # Send a message
    def submitMessage(self):
        print(self.currentPlayer+" send a message")
            # Il faudra changer le format du message
            #   Utiliser un dict plutôt qu'une list
            #   Et utiliser les key pour identifier les différents types d'info, plutôt que de se baser sur les index de la list comme c'est le cas actuellement dans la méthode handleMessageMainThread (qu'il faudra aussi refaire)
            #  ex. du format {'msg identifers':[clientId,majID,currentPlayer], 'cells':[.....], 'agents':[.....], 'time manager':[.....], 'simulation variables':[.....], 'players':[.....], 'gameActions':[.....], 'chat box':[.....]}    

        # First infos : identifiers of the message [clientId,majID,currentPlayer]
        message = "[['"+self.clientId+"',"
        majID = self.getMajID() #getMajID et majID est a priori plus utilisé. A priori, à retirer
        message += str(majID)+",'"
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
                message = message+"[" # A refactorer !!!!   Utiliser +=  et rassembler les lignes en trop
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
            message = message+"'"+str(aAgent.cell.x)+"'"
            message = message+","
            message = message+"'"+str(aAgent.cell.y)+"'"
            message = message+","
            message = message+"'"+str(aAgent.cell.grid.id)+"'"
            message = message+"]"
            message = message+","

        # for aSpecies in theSpecies:
        #     speciesMemoryIdDict[aSpecies.name]=aSpecies.memoryID
        agentDef_IDincr={}
        for aAgtDef in self.getAgentSpeciesDict():
            agentDef_IDincr[aAgtDef.entityName]=aAgtDef.IDincr

        message = message+"["
        # message = message+str(speciesMemoryIdDict)
        message = message+str(agentDef_IDincr)
        message = message+"]"
        message = message+","
        message = message+"["
        message = message+str(self.timeManager.currentPhase)
        message = message+","
        message = message+str(self.timeManager.currentRound)
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
        message = message+"'"+str(self.currentPlayer)+"'" # Cette info est déjà présente tout au début du message (dans la première lis). A retirer
        message = message+"]"
        message = message+","
        message = message+str(self.listOfSubChannel) # Cette info est déjà présente dans le message topic. A retirer
        message = message+"]"
        print(message)
        self.listOfMajs.append(str(majID)+"-"+self.currentPlayer)
        return message

    def getMajID(self):
        majID = len(self.listOfMajs)
        return majID
    
    def onMAJTimer(self):
        self.executeGameActionsAfterBrokerMsg()
#The instructions below have been commented temporarily to test a new process for broker msg 
        # self.updateAgentsAtMAJ()
        # self.updateScoreAtMAJ()
        # self.checkAndUpdateWatchers()
        # self.timeManager.checkEndGame()
        
    def updateAgentsAtMAJ(self):
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
    

    def updateScoreAtMAJ(self):
        for aGameSpace in self.gameSpaces:
            if isinstance(aGameSpace,SGDashBoard):
                for aIndicator in aGameSpace.indicators:
                    if isinstance(aIndicator.entity,SGSimulationVariable):
                        for aDictOfSimVar in self.simulationVariablesAtMAJ:
                            if aIndicator.entity.name == aDictOfSimVar.keys():
                                aIndicator.updateByMqtt(aDictOfSimVar.values())
        self.simulationVariablesAtMAJ=[]

