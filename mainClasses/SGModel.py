from asyncio.windows_events import NULL
import sys 
from pathlib import Path
from win32api import GetSystemMetrics

sys.path.insert(0, str(Path(__file__).parent))
from SGGrid import SGGrid
from SGLegend import SGLegend
from SGLegendItem import SGLegendItem
from SGLayout import SGLayout

from PyQt5 import QtWidgets
from PyQt5.QtSvg import * 
from PyQt5.QtWidgets import QApplication, QWidget,QFileDialog,QAction
from PyQt5.QtGui import *
from PyQt5.QtCore import *


            
class SGModel(QtWidgets.QMainWindow):
    def __init__(self,width,height,typeOfLayout="vertical",parent=None):
        super().__init__(parent)
        
        #Definition the size of the window ( temporary here)
        screensize = GetSystemMetrics(0),GetSystemMetrics(1)
        self.setGeometry(int((screensize[0]/2)-width/2),int((screensize[1]/2)-height/2),width,height)
        #Init of varaible of the Model
        self.name="Simulation of a boardGame"
        #Definition of the title of the window ( temporary) 
        self.setWindowTitle(self.name)
        #We allow the drag
        self.setAcceptDrops(True)
        #We create the layout
        self.SGLayout=SGLayout(typeOfLayout)
        #We initialize the Ui
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
        
        #Definition of the grid 
        self.Grid= SGGrid() 
        #To Be CHANGED ---------------------------------------------------
        self.layoutForLegend = QtWidgets.QVBoxLayout()
        self.layoutForLegend.addWidget(self.Grid) 
        self.layout.addLayout(self.layoutForLegend,1,1) 
        
        #We declare the basic legend
        self.allTheLegends={"God":NULL}
        #We set up all the legends needed when the modeler init a initial POV
        
        
        
        
    #Create the menu
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
        
      
    #Create all the action of the menu  
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
    
    #Trigger the next turn
    def zoomPlusModel(self):
        self.Grid.zoomIn()
    
    #Trigger the next turn
    def zoomLessModel(self):
        self.Grid.zoomOut()
    
    #Trigger the next turn
    def zoomFitModel(self):
        self.Grid.zoomFit()
     
    #Extract the actual gameboard into png   
    def extractPngFromWidget(self):
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
        self.Grid.move(position)

        e.setDropAction(Qt.MoveAction)
        e.accept()
        
    #Function to generate all the legends
    def generateTheLegends(self):
        stockName=[]
        for name in self.allTheLegends :
            stockName.append(name)
        for name in stockName :   
            self.generateTheLegend(name)
        
    #Function to genrate a legend
    def generateTheLegend(self,nameOfTheLegend):
        if self.allTheLegends[nameOfTheLegend]==NULL:
            #We consider that's the modeler whant all the possibilities
            #For the cells
            allValueOfCells = self.Grid.getCellsOfPov(self.Grid.actualPov).dictColor
            allLegendItem=[]
            longestWord=""
            for key in allValueOfCells:
                if key != "default" and allValueOfCells[key]!= Qt.gray:
                    allLegendItem.append(SGLegendItem(allValueOfCells[key],key))
                    if(len(key)>len(longestWord)):
                        longestWord=key
            #To be implented Personnal legend with the player  
            #
            #
            #
            #
            #
            #
            #
        #We Generate the legend
        self.allTheLegends[nameOfTheLegend]=SGLegend(allLegendItem,len(longestWord))
        
        
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
     
    #Funtion to set the window name   
    def setName(self,theName):
        self.name=theName
        self.setWindowTitle(self.name)
        
    
    #Funtion to display a legend in particular    
    def displayLegend(self,nameOfTheLegend):
        self.allTheLegends[nameOfTheLegend]
        
    #To choose the inital pov when the game start
    def setInitialPov(self,nameOfPov):
        self.Grid.actualPov=nameOfPov
        """self.generateTheLegends()
        self.layout.addWidget(self.allTheLegends["God"],1,0)"""
        
        
        
#Launch of the application  
"""if __name__ == '__main__':
    monApp=QtWidgets.QApplication([])
    win=SGModel()
    win.show() 
    sys.exit(monApp.exec_())"""