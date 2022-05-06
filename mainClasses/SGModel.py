from asyncio.windows_events import NULL
import sys 
from pathlib import Path
from win32api import GetSystemMetrics

sys.path.insert(0, str(Path(__file__).parent))
from SGGrid import SGGrid
from SGVoid import SGVoid

from layout.SGGridLayout import SGGridLayout
from layout.SGHorizontalLayout import SGHorizontalLayout
from layout.SGVerticalLayout import SGVerticalLayout


from PyQt5 import QtWidgets
from PyQt5.QtSvg import * 
from PyQt5.QtWidgets import QApplication, QWidget,QFileDialog,QAction
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
        
        
    #Create the menu of the menue 
    def createMenue(self):
        self.menuBar().addAction(self.openSave)
        
        self.menuBar().addAction(self.save)
        
        self.menuBar().addAction(self.inspect)
        
        sep = QAction('|', self, enabled=False)
        self.menuBar().addAction(sep)
        
        self.menuBar().addAction(self.play)
        
        sep2 = QAction('|', self, enabled=False)
        self.menuBar().addAction(sep2)
        
        self.menuBar().addAction(self.zoomPlus)
        
        self.menuBar().addAction(self.zoomLess)
        
        self.menuBar().addAction(self.zoomToFit)
        
        sep3 = QAction('|', self, enabled=False)
        self.menuBar().addAction(sep3)
        
        inspectMenu = self.menuBar().addMenu(QIcon("./icon/information.png"),"&inspectElement")
        """To be finished to be implementd"""
        
        povMenu = self.menuBar().addMenu(QIcon("./icon/pov.png"),"&pov")
        """To be finished to be implementd"""
        
        graphMenu = self.menuBar().addMenu(QIcon("./icon/graph.png"),"&graph")
        """To be finished to be implementd"""
        
        sep4 = QAction('|', self, enabled=False)
        self.menuBar().addAction(sep4)
        
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
    
    #Trigger the next turn
    def nextTurn(self):
        """To be implemented"""
        return True
    
    #Trigger the zoom in
    def zoomPlusModel(self):
        for aGameSpace in self.gameSpaces:
            self.gameSpaces[aGameSpace].zoomIn()
            
    
    #Trigger the zoom out
    def zoomLessModel(self):
        for aGameSpace in self.gameSpaces:
            self.gameSpaces[aGameSpace].zoomOut()
    
    #Trigger the basic zoom
    def zoomFitModel(self):
        #To be reworked
        for aGameSpace in self.gameSpaces:
            self.gameSpaces[aGameSpace].zoomFit()
            
     
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
    #wheel event we zoom 
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

    #To create a grid
    def createGrid(self,name,rows=8, columns=8,format="square",gap=3,size=32):
        #Creation
        aGrid = SGGrid(self,name,rows, columns,format,gap,size)
        self.gameSpaces[name]=aGrid
        #Realocation of the position thanks to the layout
        newPos=self.layoutOfModel.addGameSpace(aGrid)
        aGrid.startXBase=newPos[0]
        aGrid.startYBase=newPos[1]
        if(self.typeOfLayout=="vertical"):
            aGrid.move(aGrid.startXBase,aGrid.startYBase+20*self.layoutOfModel.getNumberOfAnElement(aGrid))
        elif(self.typeOfLayout=="horizontal"):
            aGrid.move(aGrid.startXBase+20*self.layoutOfModel.getNumberOfAnElement(aGrid),aGrid.startYBase)    
        else:
            pos=self.layoutOfModel.foundInLayout(aGrid)
            aGrid.move(aGrid.startXBase+20*pos[0],aGrid.startYBase+20*pos[1])
        
        return aGrid
    
    #To create a void
    def createVoid(self,name,sizeX=200,sizeY=200):
        #Creation
        aVoid = SGVoid(self,name,sizeX,sizeY)
        self.gameSpaces[name]=aVoid
        
        #Realocation of the position thanks to the layout
        newPos=self.layoutOfModel.addGameSpace(aVoid)
        aVoid.startXBase=newPos[0]
        aVoid.startYBase=newPos[1]
        aVoid.move(aVoid.startXBase,aVoid.startYBase)
        return aVoid
        
    #To get a gameSpace in particular
    def getGameSpace(self,name):
        return self.gameSpaces[name]
    
    #To get a gameSpace in particular
    def applyPersonalLayout(self):
        aDict=self.layoutOfModel.ordered()
        for anElement in self.gameSpaces :
            if(self.typeOfLayout=="vertical"):
                self.gameSpaces[anElement].move(self.gameSpaces[anElement].startXBase,self.gameSpaces[anElement].startYBase+20*self.layoutOfModel.getNumberOfAnElement(self.gameSpaces[anElement]))
            elif(self.typeOfLayout=="horizontal"):
                self.gameSpaces[anElement].move(self.gameSpaces[anElement].startXBase+20*self.layoutOfModel.getNumberOfAnElement(self.gameSpaces[anElement]),self.gameSpaces[anElement].startYBase)    
            else:
                pos=self.layoutOfModel.foundInLayout(self.gameSpaces[anElement])
                self.gameSpaces[anElement].move(self.gameSpaces[anElement].startXBase+20*pos[0],self.gameSpaces[anElement].startYBase+20*pos[1])
        
        
    #To set a different layout
    def setLayoutForModel(self,typeOfLayout):
        if(typeOfLayout=="vertical"):
            self.typeOfLayout=typeOfLayout
            self.layoutOfModel=SGVerticalLayout()
            for anElement in self.gameSpaces :
                self.layoutOfModel.addGameSpace(self.gameSpaces[anElement])
        elif(typeOfLayout=="horizontal"):
            self.typeOfLayout=typeOfLayout
            self.layoutOfModel=SGHorizontalLayout()
            for anElement in self.gameSpaces :
                self.layoutOfModel.addGameSpace(self.gameSpaces[anElement])    
        else:
            self.typeOfLayout="grid"
            self.layoutOfModel=SGGridLayout()