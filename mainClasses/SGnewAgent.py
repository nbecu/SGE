from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
from PyQt5.QtWidgets import  QAction, QGraphicsRectItem, QGraphicsView, QGraphicsScene
import random
from mainClasses.gameAction.SGGameActions import SGGameActions
from mainClasses.SGGameSpace import SGGameSpace

class SGnewAgent(SGGameSpace):
    instances=[]

    def __init__(self, parent, id, shape, defaultsize=10, dictOfAttributs=None, me='agent', uniqueColor=Qt.white, methodOfPlacement="random"):
        super().__init__(parent, 0, 60, 0, 0, true, uniqueColor)

        self.me=me
        self.model=parent
        self.id=id
        self.shape=shape
        self.size=defaultsize
        self.dictOfAttributs=dictOfAttributs
        self.xPos=800#self.getRandomX()
        self.yPos=600#self.getRandomY()
        self.instances.append(self)
        self.color=uniqueColor
        self.isDisplay=bool
    
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(self.color, Qt.SolidPattern))
        self.setGeometry(0,0,self.size+1,self.size+1)
        x = self.xPos
        y = self.yPos
        if self.isDisplay==True:
            if(self.shape=="circleAgent"):
                self.setGeometry(x,y,self.size+1,self.size+1)
                painter.drawEllipse(x,y,self.size,self.size)
            elif self.shape=="squareAgent":
                self.setGeometry(x,y,self.size+1,self.size+1)
                painter.drawRect(x,y,self.size,self.size)
            elif self.shape=="ellipseAgent1": 
                self.setGeometry(x,y,self.size*2+1,self.size+1)
                painter.drawEllipse(0,0,self.size*2,self.size)
            elif self.shape=="ellipseAgent2": 
                self.setGeometry(x,y,self.size+1,self.size*2+1)
                painter.drawEllipse(0,0,self.size,self.size*2)
            elif self.shape=="rectAgent1": 
                self.setGeometry(x,y,self.size*2+1,self.size+1)
                painter.drawRect(0,0,self.size*2,self.size)
            elif self.shape=="rectAgent2": 
                self.setGeometry(x,y,self.size+1,self.size*2+1)
                painter.drawRect(0,0,self.size,self.size*2)
            elif self.shape=="triangleAgent1": 
                self.setGeometry(x,y,self.size+1,self.size+1)
                points = QPolygon([
                QPoint(round(self.size/2),0),
                QPoint(0,self.size),
                QPoint(self.size,  self.size)
                ])
                painter.drawPolygon(points)
            elif self.shape=="triangleAgent2": 
                self.setGeometry(x,y,self.size+1,self.size+1)
                points = QPolygon([
                QPoint(0,0),
                QPoint(self.size,0),
                QPoint(round(self.size/2),self.size)
                ])
                painter.drawPolygon(points)
            elif self.shape=="arrowAgent1": 
                self.setGeometry(x,y,self.size+1,self.size+1)
                points = QPolygon([
                QPoint(round(self.size/2),0),
                QPoint(0,self.size),
                QPoint(round(self.size/2),round(self.size/3)*2),
                QPoint(self.size,  self.size)
                ])
                painter.drawPolygon(points)
            elif self.shape=="arrowAgent2": 
                self.setGeometry(x,y,self.size+1,self.size+1)
                points = QPolygon([
                QPoint(0,0),
                QPoint(round(self.size/2),round(self.size/3)),
                QPoint(self.size,0),
                QPoint(round(self.size/2),self.size)
                ])
                painter.drawPolygon(points)
            painter.end()

