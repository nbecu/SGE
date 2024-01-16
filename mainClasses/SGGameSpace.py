from PyQt5 import QtWidgets

from PyQt5.QtGui import *
from PyQt5.QtCore import *


            
class SGGameSpace(QtWidgets.QWidget):
    def __init__(self,parent,startXBase,startYBase,posXInLayout,posYInLayout,isDraggable=True,backgroudColor=Qt.gray,forceDisplay=False):
        super().__init__(parent)
        self.model=parent
        self.posXInLayout=posXInLayout
        self.posYInLayout=posYInLayout
        self.startXBase=startXBase
        self.startYBase=startYBase
        self.isDraggable = isDraggable
        self.backgroudColor = backgroudColor
        self.forceDisplay = forceDisplay
    
    def copyOf__init__(self,parent,startXBase,startYBase,posXInLayout,posYInLayout,isDraggable=True,backgroudColor=Qt.gray,forceDisplay=False,moveable=True):
        super().__init__(parent)
        self.model=parent
        self.posXInLayout=posXInLayout
        self.posYInLayout=posYInLayout
        self.startXBase=startXBase
        self.startYBase=startYBase
        self.isDraggable = isDraggable
        self.backgroudColor = backgroudColor
        self.forceDisplay = forceDisplay
        self.moveable=moveable   
        
         
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
    def setInitialPov(self,nameOfPov):
        pass
    
    
    #The getter and setter
    def getStartXBase(self):
        return self.startXBase
    
    def getStartYBase(self):
        return self.startYBase
    
    def setStartXBase(self,number):
        self.startXBase = number
    
    def setStartYBase(self,number):
        self.startYBase = number
    
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

        if self.moveable == False:
            return
        if e.buttons() != Qt.LeftButton:
            return

        # To get the clic position in GameSpace
        def getPos(e):
            clic = QMouseEvent.windowPos(e)
            xclic = int(clic.x())
            yclic = int(clic.y())
            return xclic, yclic

        # To get the coordinate of the grid upleft corner in GameSpace
        #! TO DO : sometimes self.y is not callable: check why
        def getCPos(self):
            left = self.x()
            up = self.y()
            return left, up

        # To convert the upleft corner to center coordinates
        #! TO DO : this function is for SGGrid, need refractoring
        def toCenter(self, left, up):
            xC = int(left+(self.columns/2*self.size) +
                     ((self.columns+1)/2*self.gap))
            yC = int(up+(self.rows/2*self.size)+((self.rows+1)/2*self.gap))
            return xC, yC

        mimeData = QMimeData()
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.pos())

        xclic, yclic = getPos(e)
        left, up = getCPos(self)
        xC, yC = toCenter(self, left, up)

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
        
    #Funtion to have the global size of a gameSpace  
    def setColor(self,aColor):
        self.backgroudColor=aColor
        
        
    #Function to change the order in the layout
    def setInPosition(self,x,y):
        x=x-1
        y=y-1
        self.posXInLayout=x
        self.posYInLayout=y

    #Function to move a GameSpace in the model window
    def moveToCoords(self,x,y):
        """
        Permits to move a GameSpace at a specific coordinate based on the left upper corner

        Args:
            x (int) : x-axis corrdinate in pixels
            y (int) : y-axis corrdinate in pixels
        """
        if x < self.model.width() + self.width() or x < 0:
            if y < self.model.height() + self.height() or y < 0:
                self.move(x,y)
                self.model.isMoveToCoordsUsed = True
            else:
                raise ValueError('The y value is too high or negative')
        else:
            raise ValueError('The x value is too high or negative')
        
    