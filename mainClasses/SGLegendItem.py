from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMenu, QAction, QToolTip
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGExtensions import *
from math import inf


#Class who is responsible of creation legend item 
class SGLegendItem(QtWidgets.QWidget):
    def __init__(self,parent,type,text,classDefOrShape=None,color=Qt.black,nameOfAttribut="",valueOfAttribut="",isBorderItem=False,borderColorAndWidth=None,gameAction=None):
        super().__init__(parent)
        #Basic initialize
        self.legend=parent
        self.type=type
        self.posY=self.legend.posYOfItems
        self.legend.posYOfItems +=1
        self.text=str(text)
        if classDefOrShape == 'square' or classDefOrShape is None:
            self.shape= classDefOrShape
        else:
            self.classDef=classDefOrShape
            self.shape=self.classDef.shape
        self.color=color
        self.nameOfAttribut=nameOfAttribut
        self.valueOfAttribut=valueOfAttribut
        self.isBorderItem=isBorderItem
        if self.isBorderItem:
            self.borderColorAndWidth=borderColorAndWidth
            self.color= self.classDef.defaultShapeColor
        self.remainNumber=int
        self.gameAction= gameAction

    def event(self, e):
        # Intercept tooltip event to show the number of remaining acions for gameActions
        if e.type() == QEvent.ToolTip:
            if self.gameAction is not None:
                # Dynamically update tooltip
                aNumber = self.gameAction.getNbRemainingActions()
                if aNumber == inf:
                    text = f"∞ actions"
                else:
                    text = f"{self.gameAction.getNbRemainingActions()} actions remaining"
                QToolTip.showText(e.globalPos(), text, self)
            return True  # event handled
        return super().event(e)
    

    def isSelectable(self):
        # Title1 and Title2 items are not selectable
        # For SGLegend (pure legend), items should not be selectable unless they have a gameAction
        # For SGControlPanel (controller), items should be selectable if they have a gameAction
        if self.type in ['Title1','Title2']:
            return False
        # If this is a pure legend item (no gameAction), it should not be selectable
        if self.gameAction is None:
            return False
        # If this is a control panel item (has gameAction), it should be selectable
        return True
    
    def isSymbolOnCell(self):
        return self.type == 'symbol' and self.classDef.entityType() == 'Cell'#self.shape in ["square","hexagonal"]

    def isSymbolOnAgent(self):
        return self.type == 'symbol' and self.classDef.entityType() =='Agent' # in ("circleAgent","squareAgent", "ellipseAgent1","ellipseAgent2", "rectAgent1","rectAgent2", "triangleAgent1","triangleAgent2", "arrowAgent1","arrowAgent2")

    #Drawing function
    def paintEvent(self,event):
        if self.legend.checkDisplay():
            painter = QPainter() 
            painter.begin(self)
            painter.setBrush(QBrush(self.color, Qt.SolidPattern))
            if self.legend.selected == self :
                painter.setPen(QPen(Qt.red,2))
            if self.isBorderItem:
                painter.setPen(QPen(self.borderColorAndWidth['color'],self.borderColorAndWidth['width']))
                painter.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))
            #Square cell
            if(self.shape=="square") :   
                painter.drawRect(0, 0, 20, 20)
                if self.type == 'delete':
                    # draw a red cross inside
                    pen = QPen(Qt.red, 2)
                    painter.setPen(pen)
                    painter.drawLine(5, 5, 15, 15)
                    painter.drawLine(15, 5, 5, 15)
            #agent
            elif self.shape=="circleAgent":
                painter.drawEllipse(0, 0, 20, 20)
            elif self.shape=="squareAgent":
                painter.drawRect(0, 0, 20, 20)
            elif self.shape=="ellipseAgent1":
                painter.drawEllipse(0, 5, 20, 10)
            elif self.shape=="ellipseAgent2":
                painter.drawEllipse(5, 0, 10, 20)
            elif self.shape=="rectAgent1":
                painter.drawRect(0, 5, 20, 10)
            elif self.shape=="rectAgent2":
                painter.drawRect(5, 0, 10, 20)
            elif self.shape=="triangleAgent1": 
                points = QPolygon([
                QPoint(10,5),
                QPoint(5,15),
                QPoint(15,15)
                ])
                painter.drawPolygon(points)
            elif self.shape=="triangleAgent2": 
                points = QPolygon([           
                QPoint(15,5),
                QPoint(5,5),
                QPoint(10,15)
                ])
                painter.drawPolygon(points)
            elif self.shape=="arrowAgent1": 
                points = QPolygon([
                QPoint(20,7),
                QPoint(15,17),
                QPoint(20,14),
                QPoint(25,17)
                ])
                painter.drawPolygon(points)
            elif self.shape=="arrowAgent2": 
                points = QPolygon([           
                QPoint(25,7),
                QPoint(20,10),
                QPoint(15,7),
                QPoint(20,17)
                ])
                painter.drawPolygon(points)
            #Hexagonal square
            elif self.shape=="hexagonal":
                points = QPolygon([
                QPoint(20,  0),
                QPoint(30,  7),
                QPoint(30,  14),
                QPoint(20, 20),
                QPoint(10, 14),
                QPoint(10,  7)
                ])
                painter.drawPolygon(points)
            
            if self.type =="None":
                aFont=QFont("Verdana",10, underline=True)
                painter.drawTextAutoSized(15, 0, self.text, aFont, Qt.AlignLeft)
            elif self.type =="Title1":
                aFont = QFont()
                aFont.setBold(True)
                aFont.setPixelSize(14)
                painter.drawTextAutoSized(15, 0, self.text, aFont, Qt.AlignLeft)
            elif self.type =="Title2":
                aFont=QFont("Verdana",10)
                painter.drawTextAutoSized(10, 0, self.text, aFont, Qt.AlignLeft)
            elif self.type =='delete':
                aFont = QFont("Verdana",8)
                painter.drawTextAutoSized(30, 3, self.text, aFont, Qt.AlignLeft)
            else :
                font = QFont("Verdana",8)
                painter.drawTextAutoSized(30, 3, self.text, font, Qt.AlignLeft)
            self.setMinimumSize(self.legend.getSizeXGlobal()-40,10)
            self.move(10,self.posY * self.legend.heightOfLabels) #self.legend.heightOfLabels = 25 de base. mais pour CarbonPolis c'est 20
            painter.end()
            
    
    #Funtion to handle the zoom
    def zoomIn(self):
        self.size=self.parent.size
        self.gap=self.parent.gap
        self.update()
    
    def zoomOut(self):
        self.size=self.parent.size
        self.gap=self.parent.gap
        self.update()
        
    def zoomFit(self):
        self.size=self.parent.size
        self.gap=self.parent.gap
        self.update()
        
    # Note: mousePressEvent has been moved to SGControlPanel
    # SGLegendItem in pure legends should not have controller behavior
        
    #To handle the drag 
    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.LeftButton:
            return
    
    # Note: isFromAdmin() is obsolete - use SGControlPanel.isAdminLegend() instead




                    

        
    
        
    