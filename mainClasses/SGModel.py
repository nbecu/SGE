
from PyQt5.QtSvg import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QAction,QMenu
from PyQt5 import QtWidgets
from mainClasses.layout.SGVerticalLayout import SGVerticalLayout
from mainClasses.layout.SGHorizontalLayout import SGHorizontalLayout
from mainClasses.layout.SGGridLayout import SGGridLayout
from mainClasses.gameAction.SGGameActions import SGGameActions
from mainClasses.gameAction.SGMove import SGMove
from mainClasses.gameAction.SGDelete import SGDelete
from mainClasses.gameAction.SGUpdate import SGUpdate
from mainClasses.gameAction.SGCreate import SGCreate
from mainClasses.SGLegend import SGLegend
from mainClasses.SGVoid import SGVoid
from mainClasses.SGCell import SGCell
from mainClasses.SGGrid import SGGrid
from mainClasses.SGModelAction import SGModelAction
from mainClasses.SGModelAction import SGModelAction_OnEntities
from mainClasses.SGEndGameRule import SGEndGameRule
from mainClasses.SGUserSelector import SGUserSelector
from mainClasses.SGDashBoard import SGDashBoard
from mainClasses.SGSimulationVariables import SGSimulationVariables
from mainClasses.SGTextBox import SGTextBox
from mainClasses.SGTimeLabel import SGTimeLabel
from mainClasses.SGTimeManager import SGTimeManager
from mainClasses.SGPlayer import SGPlayer
from mainClasses.SGAgent import SGAgent
from mainClasses.SGEntity import SGEntity
from mainClasses.SGEntityDef import *
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

sys.path.insert(0, str(Path(__file__).parent))


# Mother class of all the SGE System
class SGModel(QtWidgets.QMainWindow):
    def __init__(self, width=1800, height=900, typeOfLayout="grid", x=3, y=3, name="Simulation of a boardGame", windowTitle="myGame",testMode=False):
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
        # Definition of the title of the window ( temporary)
        if windowTitle is None:
            self.windowTitle = self.name
        else:
            self.windowTitle = windowTitle
        self.setWindowTitle(self.windowTitle)
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
        # To handle the selection of an item in a legend in a global way
        self.selected = [None]
        # To keep in memory all the povs already displayed in the menu
        self.listOfPovsForMenu = []
        # To handle the flow of time in the game
        self.users = ["Admin"]
        self.timeManager = SGTimeManager(self)
        # List of players
        self.players = {}
        self.currentPlayer = "Admin"
        self.adminLegend = None

        self.myUserSelector = None
        self.myTimeLabel = None

        self.listOfSubChannel = []
        self.listOfMajs = []
        self.processedMAJ = set()
        self.timer = QTimer()
        self.haveToBeClose = False
        # self.randomSeed=42
        # random.seed(self.randomSeed)
        self.mqtt=False
        self.mqttMajType=None
        self.testMode=testMode
        self.dictAgentsAtMAJ={}
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
        # Definition of the toolbar via a menue and the ac
        self.createAction()
        self.createMenu()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)

        self.nameOfPov = "default"

        if self.testMode:
            self.label = QtWidgets.QLabel(self)
            self.label.setGeometry(10, 10, 350, 30)

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.maj_coordonnees)
            self.timer.start(100)

        self.singletimer = QTimer.singleShot(1000, self.updateFunction)

    def maj_coordonnees(self):
        pos_souris_globale = QCursor.pos()
        coord_x, coord_y = pos_souris_globale.x(), pos_souris_globale.y()
        self.label.setText(f'Coordonnées Globales de la Souris : ({coord_x}, {coord_y})')
    
    def updateFunction(self):
        for aAgent in self.getAgents():
            aAgent.cell.moveAgentByRecreating_it(aAgent)
        self.show()

    # Create the menu of the menue
    def createMenu(self):
        self.menuBar().addAction(self.openSave)

        self.menuBar().addAction(self.save)

        self.menuBar().addAction(self.inspect)

        sep = QAction('|', self, enabled=False)
        self.menuBar().addAction(sep)
        self.menuBar().addAction(self.backward)

        self.menuBar().addAction(self.forward)

        sep2 = QAction('|', self, enabled=False)
        self.menuBar().addAction(sep2)

        self.menuBar().addAction(self.play)

        sep3 = QAction('|', self, enabled=False)
        self.menuBar().addAction(sep3)

        self.menuBar().addAction(self.zoomPlus)

        self.menuBar().addAction(self.zoomLess)

        self.menuBar().addAction(self.zoomToFit)

        sep4 = QAction('|', self, enabled=False)
        self.menuBar().addAction(sep4)

        inspectMenu = self.menuBar().addMenu(QIcon("./icon/information.png"), "&inspectElement")
        """To be finished to be implementd"""

        self.symbologyMenu = self.menuBar().addMenu(QIcon("./icon/symbology.png"), "&Symbology")
        # dictionnaire pour stocker les actions du sous-menu Symbology
        self.submenuSymbology_actions = {}

        self.povMenu = self.menuBar().addMenu(QIcon("./icon/pov.png"), "&pov")

        graphMenu = self.menuBar().addMenu(QIcon("./icon/graph.png"), "&graph")
        """To be finished to be implementd"""

        sep5 = QAction('|', self, enabled=False)
        self.menuBar().addAction(sep5)

        extractMenu = self.menuBar().addMenu(QIcon("./icon/extract.png"), "&Extract")
        extractMenu.addAction(self.extractPng)
        extractMenu.addAction(self.extractSvg)
        extractMenu.addAction(self.extractHtml)

    # Create all the action related to the menu

    def createAction(self):
        self.openSave = QAction(QIcon("./icon/ouvrir.png"), " &open", self)
        self.openSave.triggered.connect(self.openFromSave)

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

        self.play = QAction(QIcon("./icon/play.png"), " &play", self)
        self.play.triggered.connect(self.nextTurn)

        self.zoomPlus = QAction(
            QIcon("./icon/zoomPlus.png"), " &zoomPlus", self)
        self.zoomPlus.triggered.connect(self.zoomPlusModel)

        self.zoomLess = QAction(
            QIcon("./icon/zoomLess.png"), " &zoomLess", self)
        self.zoomLess.triggered.connect(self.zoomLessModel)

        self.zoomToFit = QAction(
            QIcon("./icon/zoomToFit.png"), " &zoomToFit", self)
        self.zoomToFit.triggered.connect(self.zoomFitModel)

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
        self.timeManager.nextPhase()
        # self.eventTime()

    def closeEvent(self, event):
        print("trigger")
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
    def newGrid(self, columns=10, rows=10, format="square", color=Qt.gray, gap=0, size=30, name="", moveable=True):
        """
        Create a grid that contains cells

        Args:
            columns (int): number of columns (width).
            rows (int): number of rows (height).
            format ("square", "hexagonal"): shape of the cells. Defaults to "square".
            color (a color, optional): background color of the grid . Defaults to Qt.gray.
            gap (int, optional): gap size between cells. Defaults to 0.
            size (int, optional): size of the cells. Defaults to 30.
            name (st): name of the grid.
            moveable (bool) : grid can be moved by clic and drage. Defaults to "True".

        Returns:
            aGrid: the grid created with its cells
        """
        # Creation
        aGrid = SGGrid(self, name, columns, rows, format, gap, size, color, moveable)
        self.gameSpaces[name] = aGrid
        # Realocation of the position thanks to the layout
        newPos = self.layoutOfModel.addGameSpace(aGrid)
        aGrid.setStartXBase(newPos[0])
        aGrid.setStartYBase(newPos[1])
        if (self.typeOfLayout == "vertical"):
            aGrid.move(aGrid.getStartXBase(), aGrid.getStartYBase() +
                       20*self.layoutOfModel.getNumberOfAnElement(aGrid))
        elif (self.typeOfLayout == "horizontal"):
            aGrid.move(aGrid.getStartXBase(
            )+20*self.layoutOfModel.getNumberOfAnElement(aGrid), aGrid.getStartYBase())
        else:
            pos = self.layoutOfModel.foundInLayout(aGrid)
            aGrid.move(aGrid.getStartXBase()+20 *
                       pos[0], aGrid.getStartYBase()+20*pos[1])
        return self.getCellDef(aGrid)
    
    def newCellsFromGrid(self,grid):
        CellDef = SGCellDef(grid, grid.cellShape,grid.size,defaultColor=Qt.white )
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
    def getCells(self,grid=None):
        if grid == None:
            grid = self.getGrids()[0]
        return self.getCellDef(grid).entities
    
    # To get all the povs of the collection
    def getCellPovs(self,grid):
        return {key: value for dict in (self.cellOfGrids[grid.id]['ColorPOV'],self.cellOfGrids[grid.id]['BorderPOV']) for key, value in dict.items() if "selected" not in key and "BorderWidth" not in key}

    # To get a cell in particular
    def getCell(self, aGrid, aId):
        result = filter(lambda cell: cell.id == aId, self.cellOfGrids[aGrid.id].entities)
        [cell for cell in self.cellOfGrids[aGrid.id].entities if cell.id == aId]
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
    def newLegendAdmin(self, Name='Legend', showAgentsWithNoAtt=False):
        """
        To create an Admin Legend (with all the cell and agent values)

        Args:
        Name (str): name of the Legend (default : Legend)
        showAgentsWithNoAtt (bool) : display of non attribute dependant agents (default : False)

        """
        # Creation
        # We harvest all the case value
        CellElements = {}
        AgentPOVs = self.getAgentPOVs()
        for anElement in self.getGrids():
            CellElements[anElement.id] = {}
            CellElements[anElement.id]['cells'] = anElement.getValuesForLegend()
            CellElements[anElement.id]['agents'] = {}
        for grid in CellElements:
            CellElements[grid]['agents'].update(AgentPOVs)
        agents = self.getAgents()
        aLegend = SGLegend(self, Name, CellElements,
                           "Admin", agents, showAgentsWithNoAtt)  # ICI -> Il faut comprendre qu'est ce qui est attendu en arguments dans cette fonction
        self.gameSpaces[Name] = aLegend
        self.adminLegend=aLegend
        # Realocation of the position thanks to the layout
        newPos = self.layoutOfModel.addGameSpace(aLegend)
        aLegend.setStartXBase(newPos[0])
        aLegend.setStartYBase(newPos[1])
        if (self.typeOfLayout == "vertical"):
            aLegend.move(aLegend.startXBase, aLegend.startYBase +
                         20*self.layoutOfModel.getNumberOfAnElement(aLegend))
        elif (self.typeOfLayout == "horizontal"):
            aLegend.move(aLegend.startXBase+20 *
                         self.layoutOfModel.getNumberOfAnElement(aLegend), aLegend.startYBase)
        else:
            pos = self.layoutOfModel.foundInLayout(aLegend)
            aLegend.move(aLegend.startXBase+20 *
                         pos[0], aLegend.startYBase+20*pos[1])
        aLegend.addDeleteButton("Delete")
        self.applyPersonalLayout()
        return aLegend

    # To update the admin Legend when the modeler add a new pov after the creation of the Legend
    # TO BE REMOVED. IT IS a useless method
    def updateLegendAdmin(self):
        if "adminLegend" in list(self.gameSpaces.keys()):
            aLegend = self.gameSpaces["adminLegend"]
            aLegend.initUI()
            aLegend.update()
    
    def newUserSelector(self):
        """
        To create an User Selector in your game. Functions automatically with the players declared in your model. 

        """
        if len(self.users_withControlPanel()) > 1 and len(self.players) > 0:
            userSelector = SGUserSelector(self, self.users_withControlPanel())
            self.myUserSelector = userSelector
            self.gameSpaces["userSelector"] = userSelector
            # Realocation of the position thanks to the layout
            newPos = self.layoutOfModel.addGameSpace(userSelector)
            userSelector.setStartXBase(newPos[0])
            userSelector.setStartYBase(newPos[1])
            if (self.typeOfLayout == "vertical"):
                userSelector.move(userSelector.startXBase, userSelector.startYBase +
                                  20*self.layoutOfModel.getNumberOfAnElement(userSelector))
            elif (self.typeOfLayout == "horizontal"):
                userSelector.move(userSelector.startXBase+20*self.layoutOfModel.getNumberOfAnElement(
                    userSelector), userSelector.startYBase)
            else:
                pos = self.layoutOfModel.foundInLayout(userSelector)
                userSelector.move(userSelector.startXBase +
                                  20*pos[0], userSelector.startYBase+20*pos[1])
            self.applyPersonalLayout()
            return userSelector
        else:
            print('You need to add players to the game')

    # To create a New kind of agents
    def newAgentSpecies(self, aSpeciesName, aSpeciesShape, dictAttributes=None, aSpeciesDefaultSize=10, uniqueColor=Qt.white):
        """
        Create a new specie of Agents.

        Args:
            aSpeciesName (str) : the species name
            aSpeciesShape (str) : the species shape ("circleAgent","squareAgent", "ellipseAgent1","ellipseAgent2", "rectAgent1","rectAgent2", "triangleAgent1","triangleAgent2", "arrowAgent1","arrowAgent2")
            dictAttributes (dict) : all the species attributs with all the values
            aSpeciesDefaultSize (int) : the species shape size (Default=10)
        Return:
            a nested dict for the species
            a species

        """
        aAgentSpecies = SGAgentDef(self, aSpeciesName, aSpeciesShape, aSpeciesDefaultSize,
                                dictAttributes, uniqueColor)
        # aAgentSpecies.isDisplay = False
        # aAgentSpecies.species=aSpeciesName
        # self.agentSpecies[str(aSpeciesName)] = {"me": aAgentSpecies.me, "Shape": aSpeciesShape, "DefaultSize": aSpeciesDefaultSize, "AttributList": dictAttributes, 'AgentList': {}, 'DefaultColor': uniqueColor, 'POV': {}, 'selectedPOV': None, "defSpecies": aAgentSpecies, "watchers":{}}
        # if 'agents' not in self.agentSpecies: self.agentSpecies['agents'] = {"watchers":{}}
        self.agentSpecies[aSpeciesName]=aAgentSpecies
        return aAgentSpecies

    def getAgentSpecieDict(self, aStrSpecie):
        # send back the specie dict (specie definition dict) that corresponds to aStrSpecie
        return self.agentSpecies[aStrSpecie]

    def getAgentSpeciesName(self):
        # send back a list of the names of all the species
        return [x for x in self.agentSpecies.keys() if x != 'agents']
    
    def getAgentSpeciesDict(self):
        # send back a list of all the species Dict (specie definition dict)
        return [x for x in self.agentSpecies if x != 'agents']

    def getAgentSpecie(self, aStrSpecie):
        AgentSpecie = None
        for instance in SGAgent.instances:
            if instance.me == 'collec' and instance.name == aStrSpecie:
                AgentSpecie = instance
                break
        return AgentSpecie

    def getAgentSpecies(self):
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

    # def newAgentAtCoords(self, aGrid, aAgentSpecies, ValueX=None, ValueY=None, adictAttributes=None):
    #     # OBSOLETE   This method shoudl e called by a  AgentDef
    #     """
    #     Create a new Agent in the associated species.

    #     Args:
    #         aGrid (instance) : the grid you want your agent in
    #         aAgentSpecies (instance) : the species of your agent
    #         ValueX (int) : Column position in grid (Default=Random)
    #         ValueY (int) : Row position in grid (Default=Random)

    #     Return:
    #         a new nest in the species dict for the agent
    #         a agent


    #     """
    #     anAgentID = str(aAgentSpecies.memoryID)
    #     self.updateIDmemory(aAgentSpecies)


    #     if ValueX == None:
    #         ValueX = random.randint(1, aGrid.columns)
    #     if ValueY == None:
    #         ValueY = random.randint(1, aGrid.rows)
    #         if ValueY < 1:
    #             ValueY = +1
    #     locationCell = aGrid.getCell(ValueX, ValueY)

    #     if self.agentSpecies[str(aAgentSpecies.name)]['DefaultColor'] is not None:
    #         uniqueColor = self.agentSpecies[str(aAgentSpecies.name)]['DefaultColor']
    #     aAgent = SGAgent(aGrid,locationCell, aAgentSpecies.name, aAgentSpecies.format, aAgentSpecies.size,adictAttributes, id=anAgentID, me='agent', uniqueColor=uniqueColor)
    #     aAgent.isDisplay = True
    #     aAgent.species = str(aAgentSpecies.name)
    #     aAgent.privateID = str(aAgentSpecies.name)+aAgent.id
        
    #     if aAgentSpecies.dictAttributes is not None:
    #         for aAtt in aAgentSpecies.dictAttributes.keys():
    #             if aAgent.dictAttributes is None:
    #                 aAgent.dictAttributes={}
    #                 aAgent.dictAttributes[aAtt]=None
    #                 aAgent.manageAttributeValues(aAgentSpecies,aAtt)
    #             else :
    #                 if aAtt in aAgent.dictAttributes.keys():
    #                     if aAgent.dictAttributes[aAtt] is None:
    #                         aAgent.manageAttributeValues(aAgentSpecies,aAtt)
    #                 else:
    #                     aAgent.dictAttributes[aAtt]=None
    #                     aAgent.manageAttributeValues(aAgentSpecies,aAtt)

    #     self.agentSpecies[str(aAgentSpecies.name)]['AgentList'][str(anAgentID)] = {"me": aAgent.me, 'position': aAgent.cell, 'species': aAgent.name, 'size': aAgent.size,'attributs': adictAttributes, "AgentObject": aAgent}
    #     # C'est très curieux que le dictOfAttributes soit à la fois dans l'instance d'agent et dans la lise agentSpecies[str(aAgentSpecies.name)]['AgentList'][str(anAgentID)]
    #     # C'est un doublon, qui ne devrait pas exister 
    #     aAgent.show()
    #     return aAgent
    
    def newAgent_ADMINONLY(self, aGrid, aAgentSpecies, ValueX, ValueY, adictAttributes, aPrivateID):
        """
        Do not use.
        """
        locationCell = aGrid.getCell(int(ValueX), int(ValueY))
        if self.agentSpecies[str(aAgentSpecies.name)]['DefaultColor'] is not None:
            uniqueColor = self.agentSpecies[str(aAgentSpecies.name)]['DefaultColor']
        anAgentID= self.getIdFromPrivateId(aPrivateID,aAgentSpecies.name)
        aAgent = SGAgent(aGrid,locationCell, aAgentSpecies.name, aAgentSpecies.format, aAgentSpecies.size,adictAttributes, id=anAgentID, me='agent', uniqueColor=uniqueColor)
        aAgent.isDisplay = True
        aAgent.species = str(aAgentSpecies.name)
        aAgent.privateID = aPrivateID
        self.agentSpecies[str(aAgentSpecies.name)]['AgentList'][str(anAgentID)] = {"me": aAgent.me, 'position': aAgent.cell, 'species': aAgent.name, 'size': aAgent.size,'attributs': adictAttributes, "AgentObject": aAgent}
        aAgent.show()
        return aAgent


    def getIdFromPrivateId(self, aPrivateID, aSpeciesName):
        result=re.search(f'{aSpeciesName}(\d+)', aPrivateID)
        if result:
            anID=result.group(1)
            return anID
        raise ValueError("Check again!")


    def getAgents(self, species=None):
        """
        Return the list of all Agents in the model
        """
        # Need Refactoring
        agent_list = []
        for aSpecie, sub_dict in self.agentSpecies.items():
            # if aSpecie != 'agents' : # 'agents' entry is a specific one used for watchers on the whole population of agents
               if species is None or species == aSpecie: 
                    agent_list += sub_dict.entities

                    # for agent_id, agent_dict in sub_dict['AgentList'].items():
                    #     agent_list.append(agent_dict['AgentObject'])
        # # If we want only the agents of one specie
        # if species is not None:
        #     agent_list = []
        #     agent_objects = []
        #     if species in self.agentSpecies.keys():
        #         aSpecie = species
        #         subdict = self.agentSpecies[aSpecie]["AgentList"]
        #         for agent in subdict:
        #             agent_objects.append(subdict[agent]["AgentObject"])

        #         return agent_objects
        # # All agents in model
        return agent_list
    
    def getAgentsPrivateID(self):
        agents=self.getAgents()
        agents_privateID=[]
        for agent in agents:
            agents_privateID.append(agent.privateID)
        return agents_privateID

    def getAgent(self,aSpecies,aID):
        """Function to get an Agent with a Species and an ID.
        
        Args:
            aSpecies (str): the name of the concerned species
            anID (str): species related identificator of the agent
            """
        agent_list=self.getAgents(species=aSpecies.name)
        for aAgent in agent_list:
            if aAgent.id==aID:
                return aAgent


    # To copy an Agent to make a move // THIS METHOD SHOULD BE OVED TO AgentDef
    def copyOfAgentAtCoord(self, aCell, oldAgent):
        newAgent = SGAgent(aCell.grid,aCell, oldAgent.size,oldAgent.dictAttributes,oldAgent.color,oldAgent.classDef)
        newAgent.isDisplay = True
        # newAgent.species = oldAgent.species
        # newAgent.color = oldAgent.color
        newAgent.privateID = oldAgent.privateID
        newAgent.classDef.entities.remove(oldAgent)
        newAgent.classDef.entities.append(newAgent)
        # self.agentSpecies[str(newAgent.name)]['AgentList'][str(newAgent.id)] = {"me": newAgent.me, 'position': newAgent.cell, 'species': newAgent.name, 'size': newAgent.size,'attributs': oldAgent.dictAttributes, "AgentObject": newAgent}                                                                           
        newAgent.update()
        newAgent.show()
        self.update()
        return newAgent
    
    # To add an Agent on a particular Cell type

    """IN PROGRESS"""

    # To delete an Agent
    def deleteAgent(self, aSpeciesName, anAgentID):
        """
        Delete an Agent.

        args:
            aSpeciesName (str): name of the AgentSpecies
            anAgentID (int, optional): the ID of the agent you want to delete. If None, a random agent.
        """
        if anAgentID is None:
            theSpecies=self.getAgentSpecie(aSpeciesName)
            anAgentID=random.randint(1,theSpecies.memoryID)
        aAgent = self.agentSpecies[aSpeciesName]['AgentList'][anAgentID]["AgentObject"]
        aAgent.cell.updateDepartureAgent(aAgent)
        aAgent.deleteLater()
        del self.agentSpecies[aSpeciesName]['AgentList'][anAgentID]
        self.update()
        # self.updateLegendAdmin()    --> Removed. This is a useless method
        self.show()

    # To delete all Agents of a species
    def deleteAgents(self, speciesName=None):
        """
        Delete all aAgents of a species.
        args:
            speciesName (str, optional): name of the AgentSpecies. If None, all species will be deleted
        """
        if speciesName is None: list_species = self.getAgentSpeciesName()
        else:  list_species = [speciesName]
        for aSpeciesName in list_species:
            for anAgentSpec in self.agentSpecies[aSpeciesName]['AgentList'].values():
                aAgent = anAgentSpec["AgentObject"]
                aAgent.cell.updateDepartureAgent(aAgent)
                aAgent.deleteLater()
            self.agentSpecies[aSpeciesName]['AgentList']={} 
        self.update()
        self.show()

    def setAgents(self, aSpeciesName, aAttribute, aValue):
        """
        Set the value of attribut value of all agents of a given specie

        Args:
            aAttribute (str): Name of the attribute to set
            aValue : Value to set the attribute to
        """
        for aAgt in self.getAgents(aSpeciesName):
            aAgt.setValue(aAttribute, aValue)


    # To randomly move all agents
    def moveRandomlyAgents(self, aGrid, numberOfMovement):
        for aAgent in self.getAgents():
            aAgent.moveAgent(aGrid, numberOfMovement=numberOfMovement)

    # To create a modelAction
    def newModelAction(self, actions=[], conditions=[], feedbacks=[]):
        """
        To add a model action which can be executed during a modelPhase
        args:
            actions (lambda function): Actions the model performs during the phase (add, delete, move...)
            conditions (lambda function): Actions are performed only if the condition returns true  
            feedbacks (lambda function): feedback actions performed only if the actions are executed
        """
        aModelAction = SGModelAction(actions, conditions, feedbacks)
        self.id_modelActions += 1
        aModelAction.id = self.id_modelActions
        aModelAction.model = self
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
        aModelAction = SGModelAction_OnEntities(actions, conditions, feedbacks,(lambda:self.getCells()))
        self.id_modelActions += 1
        aModelAction.id = self.id_modelActions
        aModelAction.model = self
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
        aModelAction = SGModelAction_OnEntities(actions, conditions, feedbacks,(lambda:self.getAgents(specieName)))
        self.id_modelActions += 1
        aModelAction.id = self.id_modelActions
        aModelAction.model = self
        return aModelAction

    # To create a player
    def newPlayer(self, name):
        """"
        Create a new player

        Args:
            name (str) : name of the Player (will be displayed)
        """
        player = SGPlayer(self, name)
        self.players[name] = player
        self.users.append(player.name)
        return player

    # To get the current player

    def getCurrentPlayer(self):
        return self.currentPlayer

    def getPlayerObject(self, playerName):
        if playerName == "Admin":
            return playerName
        else:
            return self.players[playerName]
    
    def setCurrentPlayer(self, playerName):
        """
        Set the Active Player at the initialisation

        Args:
            playerName (str): predefined playerName

        """
        if playerName in self.players.keys():
            self.currentPlayer = playerName
            if self.myUserSelector is not None:
                self.myUserSelector.initSelector(playerName)

    # To get all the players
    def getPlayer(self, playerName):
        return self.players[playerName]
    
    # To select only users with a control panel
    def users_withControlPanel(self):
        selection=[]
        if self.adminLegend != None:
            selection.append('Admin')     
        for aP in self.players.values():
            if aP.controlPanel !=  None:
                selection.append(aP.name) 
        return selection

    # To create a Time Label
    def newTimeLabel(self, name="Phases&Rounds", backgroundColor=Qt.white, borderColor=Qt.black, textColor=Qt.black):
        """
        Create the visual time board of the game

        Args:
        name (str) : name of the widget (default:"Phases&Rounds")
        backgroundColor (Qt Color) : color of the background (default : Qt.white)
        borderColor (Qt Color) : color of the border (default : Qt.black)
        textColor (Qt Color) : color of the text (default : Qt.black)
        """
        aTimeLabel = SGTimeLabel(
            self, name, backgroundColor, borderColor, textColor)
        self.myTimeLabel = aTimeLabel
        self.gameSpaces[name] = aTimeLabel
        # Realocation of the position thanks to the layout
        newPos = self.layoutOfModel.addGameSpace(aTimeLabel)
        aTimeLabel.setStartXBase(newPos[0])
        aTimeLabel.setStartYBase(newPos[1])
        if (self.typeOfLayout == "vertical"):
            aTimeLabel.move(aTimeLabel.startXBase, aTimeLabel.startYBase +
                            20*self.layoutOfModel.getNumberOfAnElement(aTimeLabel))
        elif (self.typeOfLayout == "horizontal"):
            aTimeLabel.move(aTimeLabel.startXBase+20 *
                            self.layoutOfModel.getNumberOfAnElement(aTimeLabel), aTimeLabel.startYBase)
        else:
            pos = self.layoutOfModel.foundInLayout(aTimeLabel)
            aTimeLabel.move(aTimeLabel.startXBase+20 *
                            pos[0], aTimeLabel.startYBase+20*pos[1])

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
        newPos = self.layoutOfModel.addGameSpace(aTextBox)
        aTextBox.setStartXBase(newPos[0])
        aTextBox.setStartYBase(newPos[1])
        if (self.typeOfLayout == "vertical"):
            aTextBox.move(aTextBox.startXBase, aTextBox.startYBase +
                          20*self.layoutOfModel.getNumberOfAnElement(aTextBox))
        elif (self.typeOfLayout == "horizontal"):
            aTextBox.move(aTextBox.startXBase+20 *
                          self.layoutOfModel.getNumberOfAnElement(aTextBox), aTextBox.startYBase)
        else:
            pos = self.layoutOfModel.foundInLayout(aTextBox)
            aTextBox.move(aTextBox.startXBase+20 *
                          pos[0], aTextBox.startYBase+20*pos[1])

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
        newPos = self.layoutOfModel.addGameSpace(aDashBoard)
        aDashBoard.setStartXBase(newPos[0])
        aDashBoard.setStartYBase(newPos[1])
        if (self.typeOfLayout == "vertical"):
            aDashBoard.move(aDashBoard.startXBase, aDashBoard.startYBase +
                            20*self.layoutOfModel.getNumberOfAnElement(aDashBoard))
        elif (self.typeOfLayout == "horizontal"):
            aDashBoard.move(aDashBoard.startXBase+20 *
                            self.layoutOfModel.getNumberOfAnElement(aDashBoard), aDashBoard.startYBase)
        else:
            pos = self.layoutOfModel.foundInLayout(aDashBoard)
            aDashBoard.move(aDashBoard.startXBase+20 *
                            pos[0], aDashBoard.startYBase+20*pos[1])

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
        newPos = self.layoutOfModel.addGameSpace(aEndGameRule)
        aEndGameRule.setStartXBase(newPos[0])
        aEndGameRule.setStartYBase(newPos[1])
        if (self.typeOfLayout == "vertical"):
            aEndGameRule.move(aEndGameRule.startXBase, aEndGameRule.startYBase +
                              20*self.layoutOfModel.getNumberOfAnElement(aEndGameRule))
        elif (self.typeOfLayout == "horizontal"):
            aEndGameRule.move(aEndGameRule.startXBase+20*self.layoutOfModel.getNumberOfAnElement(
                aEndGameRule), aEndGameRule.startYBase)
        else:
            pos = self.layoutOfModel.foundInLayout(aEndGameRule)
            aEndGameRule.move(aEndGameRule.startXBase+20 *
                              pos[0], aEndGameRule.startYBase+20*pos[1])

        self.applyPersonalLayout()

        return aEndGameRule

    def getCurrentRound(self):
        """Return the actual ingame round"""
        return self.timeManager.currentRound

    def getCurrentPhase(self):
        """Return the actual ingame phase"""
        return self.timeManager.currentPhase
    
    def newSimVariable(self,initValue,name,color=Qt.black,isDisplay=True):
        aSimVar=SGSimulationVariables(self,initValue,name,color,isDisplay)
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

    # To choose the global inital pov when the game start

    def setInitialPov(self, nameOfPov):
        self.nameOfPov = nameOfPov
        for aGameSpace in self.getLegends():
            self.gameSpaces[aGameSpace.id].initUI()
        self.update() #  Un update()  relance le calcul de l'affichage de l'ensemble de l'interface !!

    # Adding the Pov to the menu bar
    def addPovinMenuBar(self, nameOfPov): #OBSOLETE
        if nameOfPov not in self.listOfPovsForMenu: #OBSOLETE
            self.listOfPovsForMenu.append(nameOfPov)
            anAction = QAction(" &"+nameOfPov, self)
            self.povMenu.addAction(anAction)
            anAction.triggered.connect(lambda: self.setInitialPov(nameOfPov))
        # if this is the pov is the first pov to be declared, than set it as the initial pov
        if len(self.listOfPovsForMenu) == 1:
            self.setInitialPov(nameOfPov)

    def getSubmenuSymbology(self, entityName):
        # renvoie le sous-menu 
        # selectionList = [submenu for submenu in self.submenuSymbology_actions.keys() if submenu.title() == entityName]
        # return selectionList[0] if selectionList else None
        return next((item for item in self.submenuSymbology_actions.keys() if item.title() == entityName), None)

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
            self.submenuSymbology_actions[submenu]=[]
            return submenu
            
    def addClassDefSymbologyinMenuBar(self, aClassDef,nameOfSymbology):
        submenu_name= aClassDef.entityName
        # récupérer le sous-menu (avec création du sous-menu si il n'existe pas encore)
        submenu = self.getOrCreateSubmenuSymbology(submenu_name)
        # Créez un élément de menu avec une case à cocher
        item = QAction(nameOfSymbology, self, checkable=True)
        item.triggered.connect(self.menu_item_triggered)
        # Ajouter le sous-menu au menu principal
        submenu.addAction(item)
        # Ajouter les actions de sous-menu au dictionnaire pour accès facile
        self.submenuSymbology_actions[submenu].append(item)

        
    def menu_item_triggered(self):
        # Obtener l'objet QAction qui a été déclenché
        action = self.sender()
        # Parcourer le dictionnaire pour décocher les autres éléments du même sous-menu
        for submenu, actions in self.submenuSymbology_actions.items():
            if action in actions:
                for other_action in actions:
                    if other_action is not action:
                        other_action.setChecked(False)
                break
        if action.isChecked():
            print(f"{action.text()} est sélectionné dans {submenu.title()}")
            self.update()
        else:
            print(f"{action.text()} est désélectionné dans {submenu.title()}")
            self.update()

    def getCheckedSymbologyOfEntityName(self, entityName):
        # return the name of the symbology which is checked for a given entity type. If no symbology is ckecked, returns None
        submenu = self.getSubmenuSymbology(entityName)
        submenu_items = self.submenuSymbology_actions[submenu]    
        return next((item.text() for item in submenu_items if item.isChecked()),None)



    # To add a new POV
    # def newPov(self, nameOfPov, aAtt, DictofColors, listOfGridsToApply=None):
    #     """
    #     Declare a new Point of View for cells.

    #     Args:
    #         nameOfPov (str): name of POV, will appear in the interface
    #         aAtt (str): name of the attribut
    #         DictofColors (dict): a dictionary with all the attribut values, and for each one a Qt.Color (https://doc.qt.io/archives/3.3/qcolor.html)
    #         listOfGridsToApply (list): list of grid names where the POV applies (default:None)

    #     """
    #     if listOfGridsToApply == None:
    #         # get the fisrt value of the dict
    #         listOfGridsToApply = [list(self.gameSpaces.values())[0]]
    #     if not isinstance(listOfGridsToApply, list):
    #         listOfGridsToApply = [listOfGridsToApply]
    #     for aGrid in listOfGridsToApply:
    #         if (isinstance(aGrid, SGGrid) == True):
    #             self.cellOfGrids[aGrid.id]["ColorPOV"][nameOfPov] = {aAtt: DictofColors}
    #     self.addPovinMenuBar(nameOfPov)

    # def newBorderPov(self, nameOfPov, aAtt, DictofColors, borderWidth=4, listOfGridsToApply=None):
    #     """
    #     Declare a new Point of View for cells (only for border color).

    #     Args:
    #         nameOfPov (str): name of POV, will appear in the interface
    #         aAtt (str): name of the attribut
    #         DictofColors (dict): a dictionary with all the attribut values, and for each one a Qt.Color (https://doc.qt.io/archives/3.3/qcolor.html)
    #         listOfGridsToApply (list): list of grid names where the POV applies (default:None)

    #     """
    #     if listOfGridsToApply == None:
    #         # get the fisrt value of the dict
    #         listOfGridsToApply = [list(self.gameSpaces.values())[0]]
    #     if not isinstance(listOfGridsToApply, list):
    #         listOfGridsToApply = [listOfGridsToApply]
    #     for aGrid in listOfGridsToApply:
    #         if (isinstance(aGrid, SGGrid) == True):
    #             self.cellOfGrids[aGrid.id]["BorderPOV"][nameOfPov] = {
    #                 aAtt: DictofColors}
    #             self.cellOfGrids[aGrid.id]["BorderPOV"]["BorderWidth"] = borderWidth
    #     self.addPovinMenuBar(nameOfPov)

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
        if aNumber == "infinite":
            aNumber = 9999999
        return SGCreate(anObjectType, aNumber, aDictOfAcceptedValue, listOfRestriction, feedback, conditionOfFeedback)

    def newUpdateAction(self, anObjectType, aNumber, aDictOfAcceptedValue={}, listOfRestriction=[], feedback=[], conditionOfFeedback=[]):
        """
        Add a Update GameAction to the game.

        Args:
        - anObjectType : a AgentSpecies or the keyword "Cell"
        - a Number (int) : number of utilisation, could use "infinite"
        - aDictOfAcceptedValue (dict) : attribute with value concerned, could be None

        """
        if anObjectType == 'Cell':
            anObjectType = SGCell
        if aNumber == "infinite":
            aNumber = 9999999
        return SGUpdate(anObjectType, aNumber, aDictOfAcceptedValue, listOfRestriction, feedback, conditionOfFeedback)

    def newDeleteAction(self, anObjectType, aNumber, aDictOfAcceptedValue=None, listOfRestriction=[], feedback=[], conditionOfFeedback=[]):
        """
        Add a Delete GameAction to the game.

        Args:
        - anObjectType : a AgentSpecies
        - a Number (int) : number of utilisation, could use "infinite"
        - aDictOfAcceptedValue (dict) : attribute with value concerned, could be None

        """
        if aNumber == "infinite":
            aNumber = 9999999
        if anObjectType == 'Cell':
            anObjectType = SGCell
        return SGDelete(anObjectType, aNumber, aDictOfAcceptedValue, listOfRestriction, feedback, conditionOfFeedback)

    def newMoveAction(self, anObjectType, aNumber, aDictOfAcceptedValue=None, listOfRestriction=[], feedback=[], conditionOfFeedback=[], feedbackAgent=[], conditionOfFeedBackAgent=[]):
        """
        Add a MoveAction to the game.

        Args:
        - anObjectType : a AgentSpecies
        - a Number (int) : number of utilisation, could use "infinite"
        - aDictOfAcceptedValue (dict) : attribute with value concerned, could be None

        """
        if aNumber == "infinite":
            aNumber = 9999999
        return SGMove(anObjectType, aNumber, aDictOfAcceptedValue, listOfRestriction, feedback, conditionOfFeedback, feedbackAgent, conditionOfFeedBackAgent)

    # -----------------------------------------------------------
    # Getter

    def getGrid(self,anObject):
        if isinstance(anObject,SGCellDef): return anObject.grid
        elif isinstance(anObject,SGGrid): return anObject
        else: raise ValueError('Wrong object type')


    # To get all type of gameSpace who are grids
    def getGrids(self):
        listOfGrid = []
        for aGameSpace in list(self.gameSpaces.values()):
            if isinstance(aGameSpace, SGGrid):
                listOfGrid.append(aGameSpace)
        return listOfGrid
    
    def getGrid_withID(self, aGridID):
        Grids=self.getGrids()
        for aGrid in Grids:
            if aGrid.id==aGridID:
                return aGrid

    def getGrid_withID(self, aGridID):
        Grids=self.getGrids()
        for aGrid in Grids:
            if aGrid.id==aGridID:
                return aGrid
            
    # To get all type of gameSpace who are legends
    def getLegends(self):
        listOfLegend = []
        for aGameSpace in list(self.gameSpaces.values()):
            if isinstance(aGameSpace, SGLegend):
                listOfLegend.append(aGameSpace)
        return listOfLegend

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
        self.majTimer.start(1000)
        self.initMQTT()
        self.mqttMajType=majType
        self.show()

    # Return all the GM of players
    def getGM(self):
        listOfGm = []
        for player in self.players.values():
            for gm in player.gameActions:
                listOfGm.append(gm)
        return listOfGm

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
            privateID=msg_list[nbToStart+2+j][0]
            speciesName=msg_list[nbToStart+2+j][1]
            dictAttributes=msg_list[nbToStart+2+j][2]
            owner=msg_list[nbToStart+2+j][3]
            agentX=msg_list[nbToStart+2+j][4][-3]
            agentY=msg_list[nbToStart+2+j][4][-1]
            grid=msg_list[nbToStart+2+j][5]
            theGrid=self.getGrid_withID(grid)
            aAgentSpecies=self.getAgentSpecie(speciesName)

            self.dictAgentsAtMAJ[j]=[theGrid,aAgentSpecies,agentX,agentY,dictAttributes,privateID]
        
        # AGENT SPECIES MEMORY ID
        speciesMemoryIdDict=msg_list[-5][0]
        for aSpeciesName, speciesMemoryID in dict(speciesMemoryIdDict).items():
            theSpecies=self.getAgentSpecie(aSpeciesName)
            theSpecies.memoryID=speciesMemoryID

        # TIME MANAGEMENT
        self.timeManager.currentPhase = msg_list[-4][0]
        self.timeManager.currentRound = msg_list[-4][1]
        if self.myTimeLabel is not None:
            self.myTimeLabel.updateTimeLabel()
        if self.timeManager.currentPhase == 0:
            # We reset GM
            for gm in self.getGM():
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
        def on_message(client, userdata, msg):
            userdata.q.put(msg.payload)
            print("message received " + msg.topic)
            message = self.q.get()
            msg_decoded = message.decode("utf-8")
            msg_list = eval(msg_decoded)
            if msg_list[0][0] != self.clientId:
                for aAgent in self.getAgents():
                    self.deleteAgent(aAgent.species,aAgent.id)
                    self.handleMessageMainThread(msg_list)
            else:
                print("Own update, no action required.")   

        self.connect_mqtt()
        self.mqtt=True

        self.client.subscribe("Gamestates")
        self.client.on_message = on_message
        self.listOfSubChannel.append("Gamestates")
        

    # publish on mqtt broker the state of all entities of the world
    def publishEntitiesState(self):
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
        theAgents = self.getAgents()
        theSpecies = self.getAgentSpecies()
        speciesMemoryIdDict={}
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
            message = message+"'"+str(aAgent.privateID)+"'"
            message = message+","
            message = message+"'"+str(aAgent.species)+"'"
            message = message+","
            message = message+str(aAgent.dictAttributes)
            message = message+","
            message = message+"'"+str(aAgent.owner)+"'"
            message = message+","
            message = message+"'"+str(aAgent.cell.name)+"'"
            message = message+","
            message = message+"'"+str(aAgent.cell.grid.id)+"'"
            message = message+"]"
            message = message+","

        for aSpecies in theSpecies:
            speciesMemoryIdDict[aSpecies.name]=aSpecies.memoryID

        message = message+"["
        message = message+str(speciesMemoryIdDict)
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
        self.updateAgentsAtMAJ()
        self.updateScoreAtMAJ()
        self.timeManager.checkDashBoard()
        self.timeManager.checkEndGame()
        
    def updateAgentsAtMAJ(self):
        for j in self.dictAgentsAtMAJ.keys():
            newAgent=self.newAgent_ADMINONLY(self.dictAgentsAtMAJ[j][0],self.dictAgentsAtMAJ[j][1],self.dictAgentsAtMAJ[j][2],self.dictAgentsAtMAJ[j][3],self.dictAgentsAtMAJ[j][4],self.dictAgentsAtMAJ[j][5])
            newAgent.cell.updateIncomingAgent(newAgent)
        self.dictAgentsAtMAJ={}
    
    def updateScoreAtMAJ(self):
        for aGameSpace in self.gameSpaces:
            if isinstance(aGameSpace,SGDashBoard):
                for aIndicator in aGameSpace.indicators:
                    if isinstance(aIndicator.entity,SGSimulationVariables):
                        for aDictOfSimVar in self.simulationVariablesAtMAJ:
                            if aIndicator.entity.name == aDictOfSimVar.keys():
                                aIndicator.updateByMqtt(aDictOfSimVar.values())
        self.simulationVariablesAtMAJ=[]

