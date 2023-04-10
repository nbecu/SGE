
from email.policy import default
from logging.config import listen
import sys 
import copy
from pathlib import Path
from pyrsistent import s
from win32api import GetSystemMetrics
from paho.mqtt import client as mqtt_client
import threading ,queue
import random

sys.path.insert(0, str(Path(__file__).parent))
from SGAgent import SGAgent
from SGPlayer import SGPlayer
from SGTimeManager import SGTimeManager
from SGTimeLabel import SGTimeLabel
from SGMessageBox import SGMessageBox

from SGGrid import SGGrid
from SGVoid import SGVoid
from SGLegend import SGLegend

from gameAction.SGCreate import SGCreate
from gameAction.SGUpdate import SGUpdate
from gameAction.SGDelete import SGDelete
from gameAction.SGMove import SGMove

from layout.SGGridLayout import SGGridLayout
from layout.SGHorizontalLayout import SGHorizontalLayout
from layout.SGVerticalLayout import SGVerticalLayout


from PyQt5 import QtWidgets
from PyQt5.QtSvg import * 
from PyQt5.QtWidgets import  QAction
from PyQt5.QtGui import *
from PyQt5.QtCore import *


#Mother class of all the SGE System
class SGModel(QtWidgets.QMainWindow):
    def __init__(self,width,height,typeOfLayout=None,x=3,y=3,name="Simulation of a boardGame",windowTitle=None):
        """
        Declaration of a new model

        Args:
            width (int): width of the main window
            height (int): height of the main window
            typeOfLayout ("vertical", "horizontal" or "grid"): the type of layout used to position the different graphic elements of the simulation
            x (int, optional): used only for grid layout. defines the number layout grid width
            y (int, optional): used only for grid layout. defines the number layout grid height
            name (str, optional): the name of the model.
            windowTitle (str, optional): the title of the main window of the simulation.
        """
        super().__init__()
        #Definition the size of the window ( temporary here)
        screensize = GetSystemMetrics(0),GetSystemMetrics(1)
        self.setGeometry(int((screensize[0]/2)-width/2),int((screensize[1]/2)-height/2),width,height)
        #Init of variable of the Model
        self.name=name
        #Definition of the title of the window ( temporary) 
        if windowTitle is None:
            self.windowTitle = self.name
        else:
            self.windowTitle = windowTitle
        self.setWindowTitle(self.windowTitle)
        #We allow the drag in this widget
        self.setAcceptDrops(True)
        
        #Definition of variable
        #Definition for all gameSpaces
        self.gameSpaces={}
        self.messageBoxes=[]
        #Definition of the AgentCollection
        self.agentSpecies={}
        self.agents=self.getAgents() #cet attribut est à proscrire car agents n'est pas remis à jour après qu'il y ait eu un ajout ou une suppression d'un agent
        self.IDincr=0
        #We create the layout
        self.typeOfLayout=typeOfLayout
        if(typeOfLayout=="vertical"):
            self.layoutOfModel=SGVerticalLayout()
        elif(typeOfLayout=="horizontal"):
            self.layoutOfModel=SGHorizontalLayout()
        else:
            self.layoutOfModel=SGGridLayout(x,y)
        #To limit the number of zoom out of players
        self.numberOfZoom=2
        #To handle the selection of an item in a legend in a global way
        self.selected=[None]
        #To keep in memory all the povs already displayed in the menue
        self.listOfPovsForMenu=[]
        self.AgentPOVs=self.getAgentPOVs()
        #To handle the flow of time in the game
        self.timeManager=SGTimeManager(self)
        #List of players
        self.players={}
        #Wich instance is it 
        self.whoIAm="Admin"
        self.listOfSubChannel=[]
        self.timer= QTimer()
        self.haveToBeClose=False
        self.initUI()
        
    
    def initUI(self):
        #Definition of the view through the a widget
        self.window = QtWidgets.QWidget() 
        self.layout = QtWidgets.QGridLayout() 
        self.setCentralWidget(self.window) 
        self.window.setLayout(self.layout)
        #Definition of the toolbar via a menue and the ac
        self.createAction()
        self.createMenu()
        
        self.nameOfPov="default"

    #Create the menu of the menue 
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
        
        inspectMenu = self.menuBar().addMenu(QIcon("./icon/information.png"),"&inspectElement")
        """To be finished to be implementd"""
        
        self.povMenu = self.menuBar().addMenu(QIcon("./icon/pov.png"),"&pov")
        

        
        graphMenu = self.menuBar().addMenu(QIcon("./icon/graph.png"),"&graph")
        """To be finished to be implementd"""
        
        sep5 = QAction('|', self, enabled=False)
        self.menuBar().addAction(sep5)
        
        extractMenu = self.menuBar().addMenu(QIcon("./icon/extract.png"),"&Extract")
        extractMenu.addAction(self.extractPng)
        extractMenu.addAction(self.extractSvg)
        extractMenu.addAction(self.extractHtml)
        
       
    
    #Create all the action related to the menu  
    def createAction(self):
        self.openSave = QAction(QIcon("./icon/ouvrir.png")," &open", self)
        self.openSave.triggered.connect(self.openFromSave)
        
        self.save = QAction(QIcon("./icon/save.png")," &save", self)
        self.save.setShortcut("Ctrl+s")
        self.save.triggered.connect(self.saveTheGame)
        
        self.backward = QAction(QIcon("./icon/backwardArrow.png")," &backward", self)
        self.backward.triggered.connect(self.backwardAction)
        
        self.forward = QAction(QIcon("./icon/forwardArrow.png")," &forward", self)
        self.forward.triggered.connect(self.forwardAction)
        
        self.inspect = QAction(QIcon("./icon/inspect.png")," &inspectAll", self)
        self.inspect.triggered.connect(self.inspectAll)
        
        self.play = QAction(QIcon("./icon/play.png")," &play", self)
        self.play.triggered.connect(self.nextTurn)
        
        self.zoomPlus = QAction(QIcon("./icon/zoomPlus.png")," &zoomPlus", self)
        self.zoomPlus.triggered.connect(self.zoomPlusModel)
        
        self.zoomLess = QAction(QIcon("./icon/zoomLess.png")," &zoomLess", self)
        self.zoomLess.triggered.connect(self.zoomLessModel)
        
        self.zoomToFit = QAction(QIcon("./icon/zoomToFit.png")," &zoomToFit", self)
        self.zoomToFit.triggered.connect(self.zoomFitModel)
        
        self.extractPng = QAction(" &ToPNG", self)
        self.extractPng.triggered.connect(self.extractPngFromWidget)
        self.extractSvg = QAction(" &ToSVG", self)
        self.extractSvg.triggered.connect(self.extractSvgFromWidget)
        self.extractHtml = QAction(" &ToHtml", self)
        self.extractHtml.triggered.connect(self.extractHtmlFromWidget)
        
        self.changeThePov= QAction(" &default", self)
        
        
         
    #Create the function for the action of the menu
    #Loading a Save
    def openFromSave(self):
        """To be implemented"""
        return True
    
    #Save the game in a file
    def saveTheGame(self):
        """To be implemented"""
        return True
    
    #Inspect All of the variables of the game
    def inspectAll(self):
        """To be implemented"""
        return True
    
    #Make the game go to precedent state
    def backwardAction(self):
        """To be implemented"""
        return True
    
    #Make the game go to next step
    def forwardAction(self):
        """To be implemented"""
        return True
    
    
    #Trigger the next turn
    def nextTurn(self):
        self.timeManager.nextPhase()
        
    def closeEvent(self, event):
        print("trigger")
        self.haveToBeClose=True
        self.getMessageBoxHistory(self.messageBoxes)
        if hasattr(self, 'client'):
            self.client.disconnect()
        self.close()

            
    
    #Trigger the zoom in
    def zoomPlusModel(self):
        """NOT TESTED"""
        self.setNumberOfZoom(self.numberOfZoom+1)
        for aGameSpaceName in self.gameSpaces:
            self.gameSpaces[aGameSpaceName].zoomIn()
        self.update()


            
    
    #Trigger the zoom out
    def zoomLessModel(self):
        """NOT TESTED"""
        if self.numberOfZoom != 0 :
            for aGameSpaceName in self.gameSpaces:
                self.gameSpaces[aGameSpaceName].zoomOut()
            self.setNumberOfZoom(self.numberOfZoom-1)
        self.update()

    
    #Trigger the basic zoom
    def zoomFitModel(self):
        """NOT TESTED"""
        #if the window to display is to big we zoom out and reapply the layout
        if self.layoutOfModel.getMax()[0]>self.width() or self.layoutOfModel.getMax()[1]>self.height():
            while(self.layoutOfModel.getMax()[0]>self.width() or self.layoutOfModel.getMax()[1]>self.height()):
                self.zoomLessModel()
                self.applyPersonalLayout()
        else :
            #if the window to display is to small we zoom in and out when we over do it once and then reapply the layout
            while(self.layoutOfModel.getMax()[0]<(self.width()) or self.layoutOfModel.getMax()[1]<self.height()):
                self.zoomPlusModel()
                self.applyPersonalLayout()
                if self.layoutOfModel.getMax()[0]>(self.width()) and self.layoutOfModel.getMax()[1]>self.height():
                    self.zoomLessModel()
                    self.zoomLessModel()
                    self.applyPersonalLayout()
                    break
        self.update()


            
     
    #Extract the current gameboard into png   
    def extractPngFromWidget(self):
        """NOT TESTED"""
        #To be reworked
        self.window.grab().save("image.png")
    
    #Extract the current gameboard into svg 
    def extractSvgFromWidget(self):
        """NOT TESTED"""
        generator = QSvgGenerator()
        generator.setFileName("image.svg")
        painter = QPainter(generator)
        self.window.render( painter )
        painter.end()
    
    #Extract the current gameboard into html
    def extractHtmlFromWidget(self):
        """To be implemented"""
        return True
    
    
    #Event
    #wheel event we zoom in or out
    def wheelEvent(self,event):
        if(event.angleDelta().y()==120):
            self.zoomPlusModel()
        else :
            self.zoomLessModel()

    
    #Function to handle the drag of widget
    def dragEnterEvent(self, e):
        e.accept()
        
    def dropEvent(self, e):
        position = e.pos()
        position.setX(position.x()-int(e.source().getSizeXGlobal()/2))
        position.setY(position.y()-int(e.source().getSizeYGlobal()/2))
        e.source().move(position)

        e.setDropAction(Qt.MoveAction)
        e.accept()

    
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

#For create elements
    #To create a grid
    def newGrid(self,columns=10,rows=10,format="square",color=Qt.gray,gap=0,size=30,name="",moveable=True):
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
        #Creation
        aGrid = SGGrid(self,name,rows, columns,format,gap,size,color,moveable)
        self.gameSpaces[name]=aGrid
        #Realocation of the position thanks to the layout
        newPos=self.layoutOfModel.addGameSpace(aGrid)
        aGrid.setStartXBase(newPos[0])
        aGrid.setStartYBase(newPos[1])
        if(self.typeOfLayout=="vertical"):
            aGrid.move(aGrid.getStartXBase(),aGrid.getStartYBase()+20*self.layoutOfModel.getNumberOfAnElement(aGrid))
        elif(self.typeOfLayout=="horizontal"):
            aGrid.move(aGrid.getStartXBase()+20*self.layoutOfModel.getNumberOfAnElement(aGrid),aGrid.getStartYBase())    
        else:
            pos=self.layoutOfModel.foundInLayout(aGrid)
            aGrid.move(aGrid.getStartXBase()+20*pos[0],aGrid.getStartYBase()+20*pos[1])
        return aGrid
    
    #To create a void
    def createVoid(self,name,sizeX=200,sizeY=200):
        #Creation
        aVoid = SGVoid(self,name,sizeX,sizeY)
        self.gameSpaces[name]=aVoid
        
        #Realocation of the position thanks to the layout
        newPos=self.layoutOfModel.addGameSpace(aVoid)
        aVoid.setStartXBase(newPos[0])
        aVoid.setStartYBase(newPos[1])
        aVoid.move(aVoid.getStartXBase(),aVoid.getStartYBase())
        return aVoid
    
    
    #To create a Legend
    def newLegendAdmin(self,Name='adminLegend'):
        """
        To create an Admin Legend (with all the cell and agent values)
        
        Args:
        Name (str): name of the Legend (default : adminLegend)

        """
        #Creation
        #We harvest all the case value
        CellElements={}
        for anElement in self.getGrids() :
            CellElements[anElement.id]=anElement.getValuesForLegend()
        agents=self.getAgents()
        AgentPOVs=self.getAgentPOVs()
        aLegend = SGLegend(self,Name,CellElements,"Admin",agents,AgentPOVs)
        self.gameSpaces["adminLegend"]=aLegend
        #Realocation of the position thanks to the layout
        newPos=self.layoutOfModel.addGameSpace(aLegend)
        aLegend.setStartXBase(newPos[0])
        aLegend.setStartYBase(newPos[1])
        if(self.typeOfLayout=="vertical"):
            aLegend.move(aLegend.startXBase,aLegend.startYBase+20*self.layoutOfModel.getNumberOfAnElement(aLegend))
        elif(self.typeOfLayout=="horizontal"):
            aLegend.move(aLegend.startXBase+20*self.layoutOfModel.getNumberOfAnElement(aLegend),aLegend.startYBase)    
        else:
            pos=self.layoutOfModel.foundInLayout(aLegend)
            aLegend.move(aLegend.startXBase+20*pos[0],aLegend.startYBase+20*pos[1])
        aLegend.addDeleteButton("Delete")
        self.applyPersonalLayout()
        return aLegend
    
    #To update the admin Legend when the modeler add a new pov after the creation of the Legend 
    def updateLegendAdmin(self):
        if "adminLegend" in list(self.gameSpaces.keys()):
            self.gameSpaces["adminLegend"].deleteLater()
            del self.gameSpaces["adminLegend"]
        aLegend=self.newLegendAdmin()
        aLegend.addDeleteButton('Delete')


    #To create a New kind of agents
    def newAgentSpecies(self,aSpeciesName,aSpeciesShape,dictOfAttributs=None,aSpeciesDefaultSize=10):
        """
        Create a new specie of Agents.

        Args:
            aSpeciesName (str) : the species name
            aSpeciesShape (str) : the species shape (see list in doc)
            dictofAttributs (dict) : all the species attributs with all the values
            aSpeciesDefaultSize (int) : the species shape size (Default=10)

        Return:
            a nested dict for the species
            a species
        
        """
        aAgentSpecies=SGAgent(self,aSpeciesName,aSpeciesShape,aSpeciesDefaultSize,dictOfAttributs,None)
        aAgentSpecies.me='collec'
        aAgentSpecies.isDisplay=False
        self.agentSpecies[str(aSpeciesName)]={"me":aAgentSpecies.me,"Shape":aSpeciesShape,"DefaultSize":aSpeciesDefaultSize,"AttributList":dictOfAttributs,'AgentList':{},'DefaultColor':Qt.white,'POV':{},'selectedPOV':None}
        return aAgentSpecies
    
    def updateIDincr(self,newValue):
        self.IDincr=newValue
        return self.IDincr

    def newAgent(self,aGrid,aAgentSpecies,ValueX=None,ValueY=None,aID=None,aDictofAttributs=None):
        """
        Create a new Agent in the associated species.

        Args:
            aGrid (instance) : the grid you want your agent in
            aAgentSpecies (instance) : the species of your agent
            ValueX (int) : Column position in grid (Default=Random)
            ValueY (int) : Row position in grid (Default=Random)

        Return:
            a new nest in the species dict for the agent
            a agent
        
        
        """
        if aID is None:
            anAgentID=self.IDincr+1
            newIDincr=self.IDincr+1
            self.updateIDincr(newIDincr)
            

        else:
            anAgentID=aID

        if aDictofAttributs is None:
            aDictofAttributs={}

        if ValueX==None:
            ValueX=random.randint(0, aGrid.columns)
            if ValueX<0:
                ValueX=+1
        if ValueY==None:
            ValueY=random.randint(0, aGrid.rows)
            if ValueY<0:
                ValueY=+1
        Cellparent=aGrid.getCellFromCoordinates(ValueX,ValueY)
        aAgent=SGAgent(Cellparent,aAgentSpecies.name,aAgentSpecies.format,aAgentSpecies.size,aAgentSpecies.dictOfAttributs,id=anAgentID)
        Cellparent.updateIncomingAgent(aAgent)
        aAgent.me='agent'
        aAgent.isDisplay=True
        aAgent.species=str(aAgentSpecies.name)
        self.agentSpecies[str(aAgentSpecies.name)]['AgentList'][str(anAgentID)]={"me":aAgent.me,'position':aAgent.cell,'species':aAgent.name,'size':aAgent.size,
                            'attributs':aDictofAttributs,"AgentObject":aAgent
                            }
        if aDictofAttributs is None:
            for key in aAgentSpecies.dictOfAttributs:
                val=list(aAgentSpecies.dictOfAttributs[key])[0]
                aAgent.updateAgentValue(key,val)
        
        return aAgent
    
    def getAgents(self,id=False,species=None):
        """
        Return the list of all Agents in the model
        """
        agent_list = []
        id_list=[]
        for animal, sub_dict in self.agentSpecies.items():
            for agent_id, agent_dict in sub_dict['AgentList'].items():
                agent_list.append(agent_dict['AgentObject'])
                id_list.append(agent_id)
        self.ids=id_list
        self.agents=agent_list
        # If we want only the agents of one specie
        if species is not None:
            agent_list=[]
            agent_objects=[]
            if species in self.agentSpecies.keys():
                animal = species
                subdict=self.agentSpecies[animal]["AgentList"]
                for agent in subdict:
                    agent_objects.append(subdict[agent]["AgentObject"])
                
                return agent_objects
        # If we want only the ids 
        if id==True:
            return self.ids
        # All agents in model
        return self.agents

    # To add an Agent with attributs values
    def addAgent(self,aGrid,aAgentSpecies,aDictOfAttributsWithValues,numberOfAgent=1):
        """
        Add a Agent after initialization

        args:
            aGrid (instance): the grid you want your Agent to be in
            aAgentSpecies (instance): the future Agent species
            aDictOfAttributsWithValues (dict): dict of the attributs with their values
            numberOfAgent(int): number of new Agents you want (default:1)
        """
        if aDictOfAttributsWithValues==None:
            aDictOfAttributsWithValues={}
        for i in range(numberOfAgent):
            incr=len(self.getAgents())
            self.IDincr=+incr
            anAgentID=self.IDincr+1
            akey = random.choice(list(aGrid.collectionOfCells.cells.keys()))
            Cellparent=aGrid.collectionOfCells.cells[akey]
            # OH LA LA . C'est vraiement pas beau ca !!
            # voici la bonne façon de récupérer une cell
            Cellparent=random.choice(list(aGrid.getCells()))
            # au passage, faut pas appeler la cell où est placé l'agent 'parent'. Tu peux l'appeler locationCell par ex.  

            anAgent=SGAgent(Cellparent,aAgentSpecies.name,aAgentSpecies.format,aAgentSpecies.size,aAgentSpecies.dictOfAttributs,id=anAgentID)
            anAgent.me='agent'
            Cellparent.updateIncomingAgent(anAgent) 
            anAgent.isDisplay=True
            anAgent.species=str(aAgentSpecies.name)

            #je pense que cette copie de l'agent est beaucoup trop compliqué. Il y a juste besoin de mettre la référence à l'agent lui même 
            self.agentSpecies[str(anAgent.name)]['AgentList'][str(anAgent.id)]={"me":anAgent.me,'position':anAgent.cell,'species':anAgent.name,'size':anAgent.size,
                            'attributs':aDictOfAttributsWithValues,"AgentObject":anAgent}
            
            for key in aAgentSpecies.dictOfAttributs:
                if key not in aDictOfAttributsWithValues:
                    val=list(aAgentSpecies.dictOfAttributs[key])[0]
                    anAgent.setValueAgent(key,val)

            anAgent.show()
            self.update()
            # print(self.agentSpecies)
        pass

    # To add an Agent with attributs values
    def placeAgent(self,aCell,aAgentSpecies,aDictOfAttributsWithValues):
        ## IL ME SEMBLE que cette méthode est obsolète
        """
        Place a Agent with legend

        args:
            aCell (instance): the grid you want your Agent to be in
            aAgentSpecies (instance): the future Agent species
            aDictOfAttributsWithValues (dict): dict of the attributs with their values
        """
        if aDictOfAttributsWithValues==None:
            aDictOfAttributsWithValues={}
        incr=len(self.getAgents())
        self.IDincr=+incr
        anAgentID=self.IDincr+1
        Cellparent=aCell
        anAgent=SGAgent(Cellparent,aAgentSpecies.name,aAgentSpecies.format,aAgentSpecies.size,aAgentSpecies.dictOfAttributs,id=anAgentID)
        anAgent.me='agent'
        anAgent.cell=Cellparent
        anAgent.isDisplay=True
        anAgent.species=str(aAgentSpecies.name)
        self.agentSpecies[str(anAgent.name)]['AgentList'][str(anAgent.id)]={"me":anAgent.me,'position':anAgent.cell,'species':anAgent.name,'size':anAgent.size,
                        'attributs':aDictOfAttributsWithValues,"AgentObject":anAgent}
        
        for key in aAgentSpecies.dictOfAttributs:
            if key not in aDictOfAttributsWithValues:
                val=list(aAgentSpecies.dictOfAttributs[key])[0]
                anAgent.updateAgentValue(key,val)

        anAgent.show()
        self.update()
        pass
    
    # To add an Agent on a particular Cell type

    """IN PROGRESS"""

    # To delete an Agent
    def deleteAgent(self,anAgentID):
        """
        Delete an Agent.
        
        args:
            anAgentID (int): the ID of the agent you want to delete
        """
        AgentPaths=[]
        if len(self.getAgents()) !=0:
            # harvest of all agents
            for animal, sub_dict in self.agentSpecies.items():
                for agent_id, agent_dict in sub_dict['AgentList'].items():
                    AgentPath={agent_id:agent_dict}
                    AgentPaths.append(AgentPath)
            # find the agent
            for paths in AgentPaths:
                for key in paths:
                    if anAgentID==str(key):
                        aAgent=paths[str(key)]['AgentObject']
                        print(aAgent)
                        break
            aAgent.cell.updateDepartureAgent(aAgent)
            aAgent.deleteLater()
            self.update()
            self.updateLegendAdmin()
        self.show()

    #To randomly move all agents
    def moveRandomlyAgents(self,aGrid,numberOfMovement):
        for aAgent in self.getAgents():
            aAgent.moveAgent(aGrid,numberOfMovement=numberOfMovement)
    

    #To get the player
    def getCurrentPlayer(self):
        if len(self.timeManager.phases) < self.timeManager.currentPhase:
            thePhase=self.timeManager.phases[self.timeManager.currentPhase]
            return thePhase.activePlayer
        else:
            return None
    
    #To create a Time Label
    def newTimeLabel(self,name='Rounds&Phases'):
        """
        Create the visual time board of the game

        Args:
        name (str) : name of the widget (default: "Rounds&Phases")
        """
        aTimeLabel=SGTimeLabel(self,name)
        self.myTimeLabel=aTimeLabel
        self.gameSpaces[name]=aTimeLabel
        #Realocation of the position thanks to the layout
        newPos=self.layoutOfModel.addGameSpace(aTimeLabel)
        aTimeLabel.setStartXBase(newPos[0])
        aTimeLabel.setStartYBase(newPos[1])
        if(self.typeOfLayout=="vertical"):
            aTimeLabel.move(aTimeLabel.startXBase,aTimeLabel.startYBase+20*self.layoutOfModel.getNumberOfAnElement(aTimeLabel))
        elif(self.typeOfLayout=="horizontal"):
            aTimeLabel.move(aTimeLabel.startXBase+20*self.layoutOfModel.getNumberOfAnElement(aTimeLabel),aTimeLabel.startYBase)    
        else:
            pos=self.layoutOfModel.foundInLayout(aTimeLabel)
            aTimeLabel.move(aTimeLabel.startXBase+20*pos[0],aTimeLabel.startYBase+20*pos[1])

        self.applyPersonalLayout()

        return aTimeLabel
    
    #To create a Message Box
    def newMessageBox(self,name='Message Box',textToWrite='Welcome in the game !'):
        """
        Create a message box

        Args:
        name (str) : name of the widget (default: "Message Box")
        textToWrite (str) : displayed text in the widget (default: "Welcome in the game!")
        """
        aMessageBox=SGMessageBox(self,name,textToWrite)
        self.messageBoxes.append(aMessageBox)
        self.gameSpaces[name]=aMessageBox
        #Realocation of the position thanks to the layout
        newPos=self.layoutOfModel.addGameSpace(aMessageBox)
        aMessageBox.setStartXBase(newPos[0])
        aMessageBox.setStartYBase(newPos[1])
        if(self.typeOfLayout=="vertical"):
            aMessageBox.move(aMessageBox.startXBase,aMessageBox.startYBase+20*self.layoutOfModel.getNumberOfAnElement(aMessageBox))
        elif(self.typeOfLayout=="horizontal"):
            aMessageBox.move(aMessageBox.startXBase+20*self.layoutOfModel.getNumberOfAnElement(aMessageBox),aMessageBox.startYBase)    
        else:
            pos=self.layoutOfModel.foundInLayout(aMessageBox)
            aMessageBox.move(aMessageBox.startXBase+20*pos[0],aMessageBox.startYBase+20*pos[1])
        
        self.applyPersonalLayout()

        return aMessageBox
    
    def getMessageBoxHistory(self,MessageBoxes):
        for aMessageBox in MessageBoxes:
            print(str(aMessageBox.id)+' : '+str(aMessageBox.history))
    
    
    def getCurrentRound(self):
        return self.timeManager.currentRound
    
    def getCurrentPhase(self):
        return self.timeManager.currentPhase
    



    

    
    #---------
#Layout
        
    #To get a gameSpace in particular
    def getGameSpace(self,name):
        return self.gameSpaces[name]
    
    #To apply the layout to all the current game spaces
    def applyPersonalLayout(self):
        self.layoutOfModel.ordered()
        for anElement in self.gameSpaces :
            if(self.typeOfLayout=="vertical"):
                self.gameSpaces[anElement].move(self.gameSpaces[anElement].startXBase,self.gameSpaces[anElement].startYBase+20*self.layoutOfModel.getNumberOfAnElement(self.gameSpaces[anElement]))
            elif(self.typeOfLayout=="horizontal"):
                self.gameSpaces[anElement].move(self.gameSpaces[anElement].startXBase+20*self.layoutOfModel.getNumberOfAnElement(self.gameSpaces[anElement]),self.gameSpaces[anElement].startYBase)    
            else:
                pos=self.layoutOfModel.foundInLayout(self.gameSpaces[anElement])
                self.gameSpaces[anElement].move(self.gameSpaces[anElement].startXBase+20*pos[0],self.gameSpaces[anElement].startYBase+20*pos[1])
        

            
        
            
    #------
#Pov

    #To choose the global inital pov when the game start
    def setInitialPov(self,nameOfPov):
        self.nameOfPov=nameOfPov
        for aGameSpace in self.getLegends():
            self.gameSpaces[aGameSpace.id].initUI()
        self.update()
          
    #Adding the Pov to the menu bar
    def addPovinMenuBar(self,nameOfPov):
        if nameOfPov not in self.listOfPovsForMenu :
            self.listOfPovsForMenu.append(nameOfPov)
            anAction=QAction(" &"+nameOfPov, self)
            self.povMenu.addAction(anAction)
            anAction.triggered.connect(lambda: self.setInitialPov(nameOfPov))
        #if this is the pov is the first pov to be declared, than set it as the initial pov 
        if len(self.listOfPovsForMenu) == 1:
             self.setInitialPov(nameOfPov) 


    #To add a new POV 
    def newPov(self,nameOfPov,aAtt,DictofColors,listOfGridsToApply=None):
        """
        Declare a new Point of View for cells.

        Args:
            nameOfPov (str): name of POV, will appear in the interface
            aAtt (str): name of the attribut
            DictofColors (dict): a dictionary with all the attribut values, and for each one a Qt.Color (https://doc.qt.io/archives/3.3/qcolor.html)
            listOfGridsToApply (list): list of grid names where the POV applies (default:None)
            
        """
        if listOfGridsToApply==None:
            listOfGridsToApply = [list(self.gameSpaces.values())[0]] #get the fisrt value of the dict
        if not isinstance(listOfGridsToApply,list):
            listOfGridsToApply=[listOfGridsToApply]
        for aGrid in listOfGridsToApply :
            if(isinstance(aGrid,SGGrid)==True):
                aGrid.collectionOfCells.povs[nameOfPov]={aAtt:DictofColors}
        self.addPovinMenuBar(nameOfPov)

    # To get the list of Agent POV
    def getAgentPOVs(self):
        list_POV={}
        for species in self.agentSpecies.keys():
            if "POV" in self.agentSpecies[species]:
                list_POV[species]=self.agentSpecies[species]['POV']
        self.AgentPOVs=list_POV
        return self.AgentPOVs
 
    #-----------------------------------------------------------  
    #TimeManager functions
    
    def getTimeManager(self):
        return self.timeManager

    #-----------------------------------------------------------  
    #Game mechanics function 
    
    def createCreateAction(self,anObjectType,aNumber,aDictOfAcceptedValue={},listOfRestriction=[],feedBack=[],conditionOfFeedBack=[]):
        return SGCreate(anObjectType,aNumber,aDictOfAcceptedValue,listOfRestriction,feedBack,conditionOfFeedBack) 
    
    def createUpdateAction(self,anObjectType,aNumber,aDictOfAcceptedValue={},listOfRestriction=[],feedBack=[],conditionOfFeedBack=[]):
        return SGUpdate(anObjectType,aNumber,aDictOfAcceptedValue,listOfRestriction,feedBack,conditionOfFeedBack) 
    
    def createDeleteAction(self,anObjectType,aNumber,aDictOfAcceptedValue={},listOfRestriction=[],feedBack=[],conditionOfFeedBack=[]):
        return SGDelete(anObjectType,aNumber,aDictOfAcceptedValue,listOfRestriction,feedBack,conditionOfFeedBack) 
    
    def createMoveAction(self,anObjectType,aNumber,aDictOfAcceptedValue={},listOfRestriction=[],feedBack=[],conditionOfFeedBack=[],feedbackAgent=[],conditionOfFeedBackAgent=[]):
        return SGMove(anObjectType,aNumber,aDictOfAcceptedValue,listOfRestriction,feedBack,conditionOfFeedBack,feedbackAgent,conditionOfFeedBackAgent) 
    
    #-----------------------------------------------------------  
    #Getter
    
    #To get all type of gameSpace who are grids
    def getGrids(self):
        listOfGrid=[]
        for aGameSpace in list(self.gameSpaces.values()) :
            if isinstance(aGameSpace,SGGrid):
                listOfGrid.append(aGameSpace)
        return listOfGrid 
    
    #To get all type of gameSpace who are legends
    def getLegends(self):
        listOfLegend=[]
        for aGameSpace in list(self.gameSpaces.values()) :
            if isinstance(aGameSpace,SGLegend):
                listOfLegend.append(aGameSpace)
        return listOfLegend 

    
    #To change the number of zoom we currently are
    def setNumberOfZoom(self,number):
        self.numberOfZoom = number    
        
    #To change the number of zoom we currently are
    def iAm(self,aNameOfPlayer):
        self.whoIAm=aNameOfPlayer

    #To open and launch the game without a mqtt broker
    def launch_withoutMqtt(self):
        self.show()


     

    #Return all the GM of players 


    def getGM(self):
        listOfGm=[]
        for player in self.players.values() :
            for gm in player.gameActions:
                listOfGm.append(gm)
        return listOfGm
    
    
            
        
    

    