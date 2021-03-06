
from email.policy import default
from logging.config import listen
import sys 
import copy
from pathlib import Path
from win32api import GetSystemMetrics
from paho.mqtt import client as mqtt_client
import threading ,queue



sys.path.insert(0, str(Path(__file__).parent))
from SGAgent import SGAgent
from SGPlayer import SGPlayer
from SGTimeManager import SGTimeManager

from SGGrid import SGGrid
from SGVoid import SGVoid
from SGLegende import SGLegende

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
    def __init__(self,width,height,typeOfLayout="vertical",x=3,y=3,parent=None):
        super().__init__()
        
        #Definition the size of the window ( temporary here)
        screensize = GetSystemMetrics(0),GetSystemMetrics(1)
        self.setGeometry(int((screensize[0]/2)-width/2),int((screensize[1]/2)-height/2),width,height)
        #Init of variable of the Model
        self.name="Simulation of a boardGame"
        #Definition of the title of the window ( temporary) 
        self.setWindowTitle(self.name)
        #We allow the drag in this widget
        self.setAcceptDrops(True)
        
        #Definition of variable
        #Definition for all gameSpaces
        self.gameSpaces={}
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
        #To handle the flow of time in the game
        self.timeManager=SGTimeManager(self)
        #List of players
        self.collectionOfPlayers={}
        self.actualPlayer=None
        #Wich instance is it 
        self.whoIAm=""
        self.listOfSubChannel=[]
        self.timer= QTimer()
        self.timer.timeout.connect(self.eventTime)
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
        self.createMenue()
        
        self.nameOfPov="default"

    #Create the menu of the menue 
    def createMenue(self):
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
        self.client.disconnect()
        self.close()

            
    
    #Trigger the zoom in
    def zoomPlusModel(self):
        self.setNumberOfZoom(self.numberOfZoom+1)
        for aGameSpaceName in self.gameSpaces:
            self.gameSpaces[aGameSpaceName].zoomIn()
        self.update()


            
    
    #Trigger the zoom out
    def zoomLessModel(self):
        if self.numberOfZoom != 0 :
            for aGameSpaceName in self.gameSpaces:
                self.gameSpaces[aGameSpaceName].zoomOut()
            self.setNumberOfZoom(self.numberOfZoom-1)
        self.update()

    
    #Trigger the basic zoom
    def zoomFitModel(self):
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


            
     
    #Extract the actual gameboard into png   
    def extractPngFromWidget(self):
        #To be reworked
        self.window.grab().save("image.png")
    
    #Extract the actual gameboard into svg 
    def extractSvgFromWidget(self):
        generator = QSvgGenerator()
        generator.setFileName("image.svg")
        painter = QPainter(generator)
        self.window.render( painter )
        painter.end()
    
    #Extract the actual gameboard into html
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
    def createGrid(self,name,rows=8, columns=8,format="square",color=Qt.gray,gap=3,size=30):
        #Creation
        aGrid = SGGrid(self,name,rows, columns,format,gap,size,color)
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
    
    
    #To create a legende
    def createLegendeAdmin(self):
        #Creation
        #We harvest all the case value
        allElements={}
        for anElement in self.getGrids() :
            allElements[anElement.id]=anElement.getValuesForLegende()
        aLegende = SGLegende(self,"adminLegende",allElements,"Admin")
        for aGrid in self.getGrids() :
            for anAgent in aGrid.collectionOfAcceptAgent :
                aLegende.addAgentToTheLegend(anAgent)
        self.gameSpaces["adminLegende"]=aLegende
        #Realocation of the position thanks to the layout
        newPos=self.layoutOfModel.addGameSpace(aLegende)
        aLegende.setStartXBase(newPos[0])
        aLegende.setStartYBase(newPos[1])
        if(self.typeOfLayout=="vertical"):
            aLegende.move(aLegende.startXBase,aLegende.startYBase+20*self.layoutOfModel.getNumberOfAnElement(aLegende))
        elif(self.typeOfLayout=="horizontal"):
            aLegende.move(aLegende.startXBase+20*self.layoutOfModel.getNumberOfAnElement(aLegende),aLegende.startYBase)    
        else:
            pos=self.layoutOfModel.foundInLayout(aLegende)
            aLegende.move(aLegende.startXBase+20*pos[0],aLegende.startYBase+20*pos[1])
        aLegende.addDeleteButton("Delete")
        return aLegende
    
    #To update the admin legende when the modeler add a new pov after the creation of the legende 
    def updateLegendeAdmin(self):
        if "adminLegende" in list(self.gameSpaces.keys()):
            self.gameSpaces["adminLegende"].deleteLater()
            del self.gameSpaces["adminLegende"]
        aLegende=self.createLegendeAdmin()
        aLegende.addDeleteButton()
    
    
    #To create a legende
    def createLegendeForPlayer(self,name,aListOfElement,playerName):
        #Creation        
        aLegende = SGLegende(self,name,aListOfElement,playerName)
        self.gameSpaces[name]=aLegende
        #Realocation of the position thanks to the layout
        newPos=self.layoutOfModel.addGameSpace(aLegende)
        aLegende.setStartXBase(newPos[0])
        aLegende.setStartYBase(newPos[1])
        if(self.typeOfLayout=="vertical"):
            aLegende.move(aLegende.startXBase,aLegende.startYBase+20*self.layoutOfModel.getNumberOfAnElement(aLegende))
        elif(self.typeOfLayout=="horizontal"):
            aLegende.move(aLegende.startXBase+20*self.layoutOfModel.getNumberOfAnElement(aLegende),aLegende.startYBase)    
        else:
            pos=self.layoutOfModel.foundInLayout(aLegende)
            aLegende.move(aLegende.startXBase+20*pos[0],aLegende.startYBase+20*pos[1])
        return aLegende
    
            
    #To create a New kind of agents
    def newAgent(self,anAgentName,anAgentFormat,listOfAcceptGrid,size=10):
        for aGrid in listOfAcceptGrid:
            anAgent=SGAgent(None,anAgentName,anAgentFormat,size)
            self.gameSpaces[aGrid.id].collectionOfAcceptAgent[anAgentName]=anAgent
        return anAgent
            
    
    #To create a newPlayer
    def newPlayer(self,name):
        player=SGPlayer(self,name)
        self.collectionOfPlayers[name]=player
        return player
        
    #To get a player
    def getAPlayer(self,name):
        return self.collectionOfPlayers[name]
    
    #To get the player
    def getPlayer(self):
        return self.actualPlayer

            
    
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
    def setInitialPovGlobal(self,nameOfPov):
        self.nameOfPov=nameOfPov
        for anGameSpace in self.getLegends():
            self.gameSpaces[anGameSpace.id].initUI()
        self.update()
        
    
    #To add a new POV and apply a value to cell
    def setUpCellValueAndPov(self,aNameOfPov,aDict,items,defaultAttributForPov=None,DefaultValueAttribut=None,listOfGridToApply=None):
        if not isinstance(items,list):
            items=[items]
        for anItem in items :
            if(isinstance(anItem,SGGrid)==True):
                anItem.collectionOfCells.povs[aNameOfPov]=aDict
                for aCell in list(anItem.collectionOfCells.getCells().values()) :
                        if aCell.attributs is None :
                            aCell.attributs = {}
                        if defaultAttributForPov ==None :
                            for anAttributeIndex in range(len(list(aDict.keys()))) :
                                if aNameOfPov not in aCell.attributs.keys() :
                                    aCell.attributs[list(aDict.keys())[anAttributeIndex]]=list(aDict[list(aDict.keys())[anAttributeIndex]].keys())[0]       
                        elif defaultAttributForPov and DefaultValueAttribut is None:
                            for anAttributeIndex in range(len(list(aDict.keys()))) :
                                if aNameOfPov not in aCell.attributs.keys() :
                                    aCell.attributs[defaultAttributForPov]=list(aDict[defaultAttributForPov].keys())[0]
                        else :
                            for anAttributeIndex in range(len(list(aDict.keys()))) :
                                if aNameOfPov not in aCell.attributs.keys() :
                                    aCell.attributs[defaultAttributForPov]=DefaultValueAttribut
            elif(isinstance(anItem,str)==True):
                for aGrid in listOfGridToApply:
                    for anAgent in aGrid.collectionOfAcceptAgent :
                        if aGrid.collectionOfAcceptAgent[anAgent].name ==anItem:
                            aGrid.collectionOfAcceptAgent[anAgent].theCollection.povs[aNameOfPov]=aDict
                            if defaultAttributForPov ==None :
                                for anAttributeIndex in range(len(list(aDict.keys()))) :
                                    aGrid.collectionOfAcceptAgent[anAgent].attributs[list(aDict.keys())[anAttributeIndex]]={}
                                    aGrid.collectionOfAcceptAgent[anAgent].attributs[list(aDict.keys())[anAttributeIndex]]=list(aDict[list(aDict.keys())[anAttributeIndex]].keys())[0]           
                            elif defaultAttributForPov and DefaultValueAttribut is None:
                                for anAttributeIndex in range(len(list(aDict.keys()))) :
                                    aGrid.collectionOfAcceptAgent[anAgent].attributs[defaultAttributForPov]={}
                                    aGrid.collectionOfAcceptAgent[anAgent].attributs[defaultAttributForPov]=list(aDict[defaultAttributForPov].keys())[0]
                            else :
                                for anAttributeIndex in range(len(list(aDict.keys()))) :
                                    aGrid.collectionOfAcceptAgent[anAgent].attributs[defaultAttributForPov]={}
                                    aGrid.collectionOfAcceptAgent[anAgent].attributs[defaultAttributForPov]=DefaultValueAttribut
            #Adding the Pov to the menue bar
            if aNameOfPov not in self.listOfPovsForMenu :
                self.listOfPovsForMenu.append(aNameOfPov)
                anAction=QAction(" &"+aNameOfPov, self)
                self.povMenu.addAction(anAction)
                anAction.triggered.connect(lambda: self.setInitialPovGlobal(aNameOfPov))
                
                
    #To add a new POV and apply a value to cell
    def setUpPov(self,aNameOfPov,aDict,items,listOfGridToApply=None):
        if not isinstance(items,list):
            items=[items]
        for anItem in items :
            if(isinstance(anItem,SGGrid)==True):
                anItem.collectionOfCells.povs[aNameOfPov]=aDict
            elif(isinstance(anItem,str)==True):
                for aGrid in listOfGridToApply:
                    for anAgent in aGrid.collectionOfAcceptAgent :
                        if aGrid.collectionOfAcceptAgent[anAgent].name ==anItem:
                            aGrid.collectionOfAcceptAgent[anAgent].theCollection.povs[aNameOfPov]=aDict
            #Adding the Pov to the menue bar
            if aNameOfPov not in self.listOfPovsForMenu :
                self.listOfPovsForMenu.append(aNameOfPov)
                anAction=QAction(" &"+aNameOfPov, self)
                self.povMenu.addAction(anAction)
                anAction.triggered.connect(lambda: self.setInitialPovGlobal(aNameOfPov))
                
                        
                    
                
        
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
    
    def createMooveAction(self,anObjectType,aNumber,aDictOfAcceptedValue={},listOfRestriction=[],feedBack=[],conditionOfFeedBack=[],feedbackAgent=[],conditionOfFeedBackAgent=[]):
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
        listOfLegende=[]
        for aGameSpace in list(self.gameSpaces.values()) :
            if isinstance(aGameSpace,SGLegende):
                listOfLegende.append(aGameSpace)
        return listOfLegende 

    
    #To change the number of zoom we actually are
    def setNumberOfZoom(self,number):
        self.numberOfZoom = number    
        
    #To change the number of zoom we actually are
    def iAm(self,aNameOfPlayer):
        self.whoIAm=aNameOfPlayer
        
    #To open and launch the game
    def launch(self):
        self.initMQTT()
        self.show()
        
    #Dunction that process the message
    def handleMessageMainThread(self):
            msg = str(self.q.get())
            print(msg)
            info=eval(str(msg)[2:-1])
            print("process un message")
            if len(info)==1:
                if msg not in self.listOfSubChannel:
                    self.listOfSubChannel.append(info[0])
                self.client.subscribe(info[0])
                self.client.publish(self.whoIAm,self.submitMessage())
            else:
                if info[2]!= self.whoIAm:
                    allCells=[]
                    for aGrid in self.getGrids():
                        for aCell in list(aGrid.collectionOfCells.getCells().values()):
                            allCells.append(aCell)
                        
                    for i in range(len(info[0])):
                        allCells[i].isDisplay=info[0][i][0]
                        allCells[i].attributs=info[0][i][1]
                        allCells[i].owner=info[0][i][2]
                        allCells[i].history=info[0][i][3]
                        if allCells[i].x==0 and allCells[i].y==0:
                            if allCells[i].parent.haveAgents():
                                for aCell in allCells[i].parent.collectionOfCells.getCells().values():
                                    aCell.deleteAllAgent()
                        if len(info[0][i][4]) !=0:
                            for j in range(len(info[0][i][4])):
                                agent=allCells[i].parent.addOnXandY(info[0][i][4][j][0],allCells[i].x+1,allCells[i].y+1)
                                agent.attributs=info[0][i][4][j][1]
                                agent.owner=info[0][i][4][j][2]
                                agent.history=info[0][i][4][j][3]
                                agent.x=info[0][i][4][j][4]
                                agent.y=info[0][i][4][j][5]
                    #We change the time manager
                    self.timeManager.actualPhase=info[1][0]
                    self.timeManager.actualRound=info[1][1]
                    #We subscribe 
                    for sub in info[3]:
                        if sub != self.whoIAm:
                            self.client.subscribe(sub)
                    if self.timeManager.actualPhase==0:
                        #We reset GM
                        for gm in self.getGM():
                            gm.reset()
                    
        
    #MQTT BAsic function to  connect to the broker
    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)
                
        print("connectMQTT")
        self.client = mqtt_client.Client(self.whoIAm)
        self.client.on_connect = on_connect
        self.q = queue.Queue()
        self.t1 = threading.Thread(target=self.handleClientThread,args=())
        self.t1.start()
        self.timer.start(100)
        self.client.connect("localhost", 1883)
        self.client.user_data_set(self)
    
    #Thread that handle the listen of the client 
    def handleClientThread(self):
        while True:
            self.client.loop(.1)
            if self.haveToBeClose==True:
                break
    
     
    #Init the MQTT client   
    def initMQTT(self):
        def on_message(client, userdata, msg):
            userdata.q.put(msg.payload)
            
        
        
        self.connect_mqtt()
        
        #IF not admin Request which channel to sub
        if self.whoIAm!="Admin":
            print("on est notAdmin")
            self.client.subscribe("Admin")
            print("onSub a Admin")
            self.client.on_message = on_message
            self.listOfSubChannel.append(self.whoIAm)
            self.client.publish("newPlayer",str([self.whoIAm]))
        #If Admin
        else:
            print("On Est admin")
            self.client.subscribe("newPlayer")
            print("onSub a newPlayer")
            self.client.on_message = on_message
            

            
    
            
        
    #Send a message                   
    def submitMessage(self):
        print(self.whoIAm+" send un message")
        message="["
        allCells=[]
        for aGrid in self.getGrids():
            for aCell in list(aGrid.collectionOfCells.getCells().values()):
                allCells.append(aCell)
        for i in range(len(allCells)):
            message=message+"["
            message=message+str(allCells[i].isDisplay)
            message=message+","
            message=message+str(allCells[i].attributs)
            message=message+","
            message=message+"'"+str(allCells[i].owner)+"'"
            message=message+","
            message=message+str(allCells[i].history)
            message=message+","
            message=message+"["
            theAgents =allCells[i].collectionOfAgents.getAgents()
            for j in range(len(theAgents)):
                print("envoie agent "+str(j))
                message=message+"["
                message=message+"'"+str(theAgents[j].name)+"'"
                message=message+","
                message=message+str(theAgents[j].attributs)
                message=message+","
                message=message+"'"+str(theAgents[j].owner)+"'"
                message=message+","
                message=message+str(theAgents[j].history)
                message=message+","
                message=message+str(theAgents[j].x)
                message=message+","
                message=message+str(theAgents[j].y)
                message=message+"]"
                if j != len(theAgents):
                    message=message+","
            message=message+"]"
            message=message+"]"
            if i != len(allCells):
                message=message+","
        message=message+"]"
        message=message+","
        message=message+"["
        message=message+str(self.timeManager.actualPhase)
        message=message+","
        message=message+str(self.timeManager.actualRound)
        message=message+","
        message=message+"]"
        message=message+","
        message=message+"["
        message=message+"'"+str(self.whoIAm)+"'"
        message=message+"]"
        message=message+","
        message=message+str(self.listOfSubChannel)
        print(message)
        return message
        
    #Event that append at every end of the timer ( litteral )  
    def eventTime(self):
        if not self.q.empty():
            self.handleMessageMainThread()
     
     #Return all the GM of players 
    def getGM(self):
        listOfGm=[]
        for player in self.collectionOfPlayers.values() :
            for gm in player.gameActions:
                listOfGm.append(gm)
        return listOfGm
    
    
            
        
    

    