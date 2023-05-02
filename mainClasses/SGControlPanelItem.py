from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null


   
#Class who is responsible of creation controlPanel.player item 
class SGControlPanelItem(QtWidgets.QWidget):
    def __init__(self,parent,type,y,texte="",color=Qt.black,valueOfAttribut="",nameOfAttribut=""):
        super().__init__(parent)
        #Basic initialize
        self.controlPanel=parent
        self.type=type
        self.valueOfAttribut=valueOfAttribut
        self.nameOfAttribut=nameOfAttribut
        self.texte=texte
        self.y=y
        self.color=color
        self.id=int
        self.initUI()

    def initUI(self):
        self.actionItemLayout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(self.texte)
        self.actionItemLayout.addWidget(self.label)
        
    #Drawing function
    def paintEvent(self,event):
        if self.controlPanel.checkDisplay():
            painter = QPainter() 
            painter.begin(self)
            painter.setBrush(QBrush(self.color, Qt.SolidPattern))
            if self.controlPanel.player.model.selected[0] == self :
                painter.setPen(QPen(Qt.red,2))
            #Square cell
            if(self.type=="square") :   
                painter.drawRect(10, 0, 20, 20)
            #agent
            elif self.type=="circleAgent":
                painter.drawEllipse(10, 0, 20, 20)
            elif self.type=="squareAgent":
                painter.drawRect(10, 0, 20, 20)
            elif self.type=="ellipseAgent1":
                painter.drawEllipse(10, 5, 20, 10)
            elif self.type=="ellipseAgent2":
                painter.drawEllipse(15, 0, 10, 20)
            elif self.type=="rectAgent1":
                painter.drawRect(10, 5, 20, 10)
            elif self.type=="rectAgent2":
                painter.drawRect(15, 0, 10, 20)
            elif self.type=="triangleAgent1": 
                points = QPolygon([
                QPoint(20,7),
                QPoint(15,17),
                QPoint(25,17)
                ])
                painter.drawPolygon(points)
            elif self.type=="triangleAgent2": 
                points = QPolygon([           
                QPoint(25,7),
                QPoint(15,7),
                QPoint(20,17)
                ])
                painter.drawPolygon(points)
            elif self.type=="arrowAgent1": 
                points = QPolygon([
                QPoint(20,7),
                QPoint(15,17),
                QPoint(20,14),
                QPoint(25,17)
                ])
                painter.drawPolygon(points)
            elif self.type=="arrowAgent2": 
                points = QPolygon([           
                QPoint(25,7),
                QPoint(20,10),
                QPoint(15,7),
                QPoint(20,17)
                ])
                painter.drawPolygon(points)
            #Hexagonal square
            elif self.type=="hexagonal":
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
                aFont=QFont("Verdana",10)
                aFont.setUnderline(True)
                painter.setFont(aFont)
                #painter.drawText(QRect(15,0,self.controlPanel.getSizeXGlobal()-50,20), Qt.AlignLeft, self.texte)
            else :
                painter.setFont(QFont("Verdana",8))
                #painter.drawText(QRect(40,5,self.controlPanel.getSizeXGlobal()-50,15), Qt.AlignLeft, self.texte)
            self.setMinimumSize(self.controlPanel.getSizeXGlobal()-50,10)
            self.move(0,self.y*30)
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
        
    #To handle the drag 
    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.LeftButton:
            return

                    

        
    
        
    