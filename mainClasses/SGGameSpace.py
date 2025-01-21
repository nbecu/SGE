from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGAspect import *


            
class SGGameSpace(QtWidgets.QWidget):
    def __init__(self,parent,startXBase,startYBase,posXInLayout,posYInLayout,isDraggable=True,backgroundColor=Qt.gray,forceDisplay=False):
        super().__init__(parent)
        self.model=parent
        self.posXInLayout=posXInLayout
        self.posYInLayout=posYInLayout
        self.positionDefineByModeler = None
        self.startXBase=startXBase
        self.startYBase=startYBase
        self.isDraggable = isDraggable
        self.forceDisplay = forceDisplay
        self.rightMargin = 9
        self.verticalGapBetweenLabels = 5
        self.gs_aspect = SGAspect.baseBorder()
        self.gs_aspect.background_color = backgroundColor
        self.title1_aspect = SGAspect.title1()
        self.title2_aspect = SGAspect.title2()
        self.title3_aspect = SGAspect.title3()
        self.text1_aspect = SGAspect.text1()
        self.text2_aspect = SGAspect.text2()
        self.text3_aspect = SGAspect.text3()
        
               
    #Funtion to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        pass
    
    def getSizeYGlobal(self):
        pass
    
    #Funtion to handle the zoom
    def zoomIn(self):
        pass
    
    def zoomOut(self):
        pass
    
    #To choose the inital pov when the game start
    def displayPov(self,nameOfPov):
        pass
    
    
    #The setters
    def setStartXBase(self,number):
        self.startXBase = number
    
    def setStartYBase(self,number):
        self.startYBase = number
    
    def isPositionDefineByModeler(self):
        return self.positionDefineByModeler != None
    
    #Calculate the area
    def areaCalc(self):
        self.area = float(self.width() * self.height())
        return self.area

    # global positionning function
    def globalPosition(self):
        newPos = self.model.layoutOfModel.addGameSpace(self)
        self.setStartXBase(newPos[0])
        self.setStartYBase(newPos[1])

    def mouseMoveEvent(self, e):

        if e.buttons() != Qt.LeftButton:
            return

        # To get the clic position in GameSpace
        def getPos(e):
            clic = QMouseEvent.windowPos(e)
            xclic = int(clic.x())
            yclic = int(clic.y())
            return xclic, yclic

        # To get the coordinate of the grid upleft corner in GameSpace
        def getCPos(self):
            left = self.x()
            up = self.y()
            return left, up

        # To convert the upleft corner to center coordinates
        def toCenter(self):
            xC = self.x()+int(self.width()/2)
            yC = self.y()+int(self.height()/2)
            return xC, yC

        mimeData = QMimeData()
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.pos())

        xclic, yclic = getPos(e)
        left, up = getCPos(self)
        xC, yC = toCenter(self)

        drag.exec_(Qt.MoveAction)

        leftf, upf = getCPos(self)
        xCorr = xclic-xC
        yCorr = yclic-yC

        newX = leftf-xCorr
        newY = upf-yCorr

        self.move(newX, newY)

#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    #Funtion to have the global size of a gameSpace  
    def setDraggability(self,aBoolean):
        self.isDraggable=aBoolean
        
        
    #Function to change the order in the layout
    def setInPosition(self,x,y):
        x=x-1
        y=y-1
        self.posXInLayout=x
        self.posYInLayout=y

    #Function to move a GameSpace in the model window
    def moveToCoords(self,x,y=None):
        """
        Permits to move a GameSpace at a specific coordinate based on the left upper corner

        Args:
            x (int) : x-axis coordinate in pixels
            y (int) : y-axis coordinate in pixels
        """
        if y is None :
            if not isinstance(x, tuple):
                raise ValueError('Wrong format: x must be a coordinate tuple (x,y).')
            else:
                y = x[1]
                x = x[0]
                
        if x < self.model.width() + self.width() or x < 0:
            if y < self.model.height() + self.height() or y < 0:
                self.positionDefineByModeler=(x,y)
                self.move(x,y)
            else:
                raise ValueError('The y value is too high or negative')
        else:
            raise ValueError('The x value is too high or negative')
    
    #Funtion to set the color of the background of the gameSpace 
    def setColor(self,aColor):
        self.gs_aspect.background_color=aColor
        
        
    def setTitlesAndTextsColor(self, textColor):
        self.setTitlesColor(textColor)
        self.setTextsColor(textColor)

    # Application de textColor à chaque titre
    def setTitlesColor(self, textColor):
        for aspect in [self.title1_aspect, self.title2_aspect, self.title3_aspect]:
            aspect.color = textColor  

    # Application de textColor à chaque texte
    def setTextsColor(self, textColor):
        for aspect in [self.text1_aspect, self.text2_aspect, self.text3_aspect]:
            aspect.color = textColor 