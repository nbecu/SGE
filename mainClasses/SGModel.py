from asyncio.windows_events import NULL
import sys 
from pathlib import Path
from win32api import GetSystemMetrics

sys.path.insert(0, str(Path(__file__).parent))
from SGGrid import SGGrid

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
    def __init__(self,width,height,typeOfLayout="vertical",parent=None):
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
        if(typeOfLayout=="vertical"):
            self.layoutOfModel=SGVerticalLayout()
        elif(typeOfLayout=="horizontal"):
            self.layoutOfModel=SGHorizontalLayout()
        else:
            self.layoutOfModel=SGGridLayout()
        
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
        #To be reimplemented
        return True
    
    #Create all the action related to the menu  
    def createAction(self):
        #To be reimplemented
        return True
    
    #Function to handle the drag of widget
    def dragEnterEvent(self, e):
        e.accept()
        
    def dropEvent(self, e):
        position = e.pos()

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
        aGrid.startXbase=newPos[0]
        aGrid.startYbase=newPos[1]
        print(aGrid.startXbase)
        print(aGrid.startYbase)
        aGrid.move(aGrid.startXbase,aGrid.startYbase)
        return aGrid
        
    #To get a gameSpace in particular
    def getGameSpace(self,name):
        return self.gameSpaces[name]
    
    #To get a gameSpace in particular
    def applyPersonalLayout(self):
        self.layoutOfModel.ordered()
        for anElement in self.gameSpaces :
            self.gameSpaces[anElement].move(self.gameSpaces[anElement].startXbase,self.gameSpaces[anElement].startYbase)
        
        
    #To set a different layout
    def setLayoutForModel(self,typeOfLayout):
        if(typeOfLayout=="vertical"):
            self.layoutOfModel=SGVerticalLayout()
            for anElement in self.gameSpaces :
                self.layoutOfModel.addGameSpace(self.gameSpaces[anElement])
        elif(typeOfLayout=="horizontal"):
            self.layoutOfModel=SGHorizontalLayout()
            for anElement in self.gameSpaces :
                self.layoutOfModel.addGameSpace(self.gameSpaces[anElement])    
        else:
            self.layoutOfModel=SGGridLayout()