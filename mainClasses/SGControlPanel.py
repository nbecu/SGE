from PyQt5.QtGui import *
from PyQt5.QtCore import *

from mainClasses.SGLegend import SGLegend
from mainClasses.SGLegendItem import SGLegendItem


#Class who is responsible of the creation of a ControlPanel
#A ControlPanel is an interface that permits to operate the game actions of a player
class SGControlPanel(SGLegend):
    @classmethod
    def forPlayer(cls, aPlayer,panelTitle,backgroundColor=Qt.transparent,borderColor=Qt.black):
        aModel=aPlayer.model
        aInstance = cls(aModel,backgroundColor)
        aInstance.id=panelTitle
        aInstance.player=aPlayer
        aInstance.playerName=aInstance.player.name
        aInstance.legendItems=[]
        aInstance.isActive=True
        aInstance.selected = None # To handle the selection of an item in the legend
        aInstance.borderColor=borderColor
        aInstance.haveADeleteButton=False
        aInstance.initUI_withGameActions(aInstance.player.gameActions)
        return aInstance


    def initUI_withGameActions(self,gameActions):
        self.posYOfItems = 0
        anItem=SGLegendItem(self,'Title1',self.id) #self.id is equivalent to name
        sortedGameActions = sorted(gameActions, key=lambda x: (0, x.targetEntDef.entityName) if x.targetEntDef.entityType() == 'Cell' else (1, x.targetEntDef.entityName))

        lastEntDefTitle = ''
        for aGameAction in sortedGameActions:
            if lastEntDefTitle != aGameAction.targetEntDef.entityName:
                anItem=SGLegendItem(self,'Title2',aGameAction.targetEntDef.entityName)
                self.legendItems.append(anItem)
                lastEntDefTitle = aGameAction.targetEntDef.entityName
            #case of UpdateAction
            listOfLegendItems = aGameAction.generateLegendItems(self)
            for anItem in listOfLegendItems:
                self.legendItems.append(anItem)

        for anItem in self.legendItems:
            anItem.show()
        self.setMinimumSize(self.getSizeXGlobal(),10)

    #Drawing the Legend
    def paintEvent(self,event):
        if self.checkDisplay():
            painter = QPainter() 
            painter.begin(self)
            if self.isActive:
                painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
            else:
                painter.setBrush(QBrush(Qt.darkGray, Qt.SolidPattern))
            painter.setPen(QPen(self.borderColor,1))
            #Draw the corner of the Legend
            self.setMinimumSize(self.getSizeXGlobal()+3, self.getSizeYGlobal()+3)
            painter.drawRect(0,0,self.getSizeXGlobal(), self.getSizeYGlobal())     

            painter.end()
    
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
        xC, yC = toCenter(self)

        drag.exec_(Qt.MoveAction)

        leftf, upf = getCPos(self)
        xCorr = xclic-xC
        yCorr = yclic-yC
        newX = leftf-xCorr
        newY = upf-yCorr

        self.move(newX, newY)
