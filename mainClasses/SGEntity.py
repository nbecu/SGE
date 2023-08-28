from tkinter.ttk import Separator
from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.gameAction.SGGameActions import SGGameActions
from sqlalchemy import true
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsView, QGraphicsScene
import random
import re

# Class who is in charged of entities : cells and agents
class SGEntity(QtWidgets.QWidget):
    def __init__(self,parent,shape,defaultsize,dictOfAttributs,id,me,gap,uniqueColor=Qt.white,methodOfPlacement="random"):
        super().__init__(parent)
        self.model=self.parent
        self.grid=self.model.grid
        self.me=me
        self.id=id
        self.dictOfAttributs=dictOfAttributs
        self.shape=shape
        self.isDisplay=True
        self.owner="admin"
        self.x=0
        self.y=0  
        if self.me=='agent' or self.me=='agCollec':
            self.species=str
            self.color=uniqueColor
            self.methodOfPlacement=methodOfPlacement
            self.size=defaultsize
            self.startXBase=0
            self.startYBase=0
        if self.me=='cell':
            self.gap=gap
            self.startXBase=self.grid.startXBase
            self.startYBase=self.grid.startYBase


    def paintEvent(self,event):
        if self.me=='agent' or self.me=='agCollec':
            painter = QPainter() 
            painter.begin(self)
            painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
            self.setGeometry(0,0,self.size+1,self.size+1)
            x = self.xPos
            y = self.yPos
            if self.isDisplay==True:
                if(self.shape=="circleAgent"):
                    painter.drawEllipse(x,y,self.size,self.size)
                elif self.shape=="squareAgent":
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

        if self.me == 'cell':
            self.startX=int(self.startXBase+self.gap*(self.x -1)+self.size*(self.x -1)+self.gap) 
            self.startY=int(self.startYBase+self.gap*(self.y -1)+self.size*(self.y -1)+self.gap)
            if (self.shape=="hexagonal"):
                self.startY=self.startY+self.size/4
            painter = QPainter() 
            painter.begin(self)
            painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
            painter.setPen(QPen(self.getBorderColor(),self.getBorderWidth()))
            #Base of the gameBoard
            if(self.shape=="square"):
                painter.drawRect(0,0,self.size,self.size)
                self.setMinimumSize(self.size,self.size+1)
                self.setGeometry(0,0,self.size+1,self.size+1)
                self.move(self.startX,self.startY)
            elif(self.shape=="hexagonal"):
                self.setMinimumSize(self.size,self.size)
                self.setGeometry(0,0,self.size+1,self.size+1)
                points = QPolygon([
                    QPoint(int(self.size/2), 0),
                    QPoint(self.size, int(self.size/4)),
                    QPoint(self.size, int(3*self.size/4)),
                    QPoint(int(self.size/2), self.size),
                    QPoint(0, int(3*self.size/4)),
                    QPoint(0, int(self.size/4))              
                ])
                painter.drawPolygon(points)
                if(self.y%2!=0):
                    # y impaires /  sachant que la première valeur de y est 1
                    self.move(self.startX , int(self.startY-self.size/2*self.y +(self.gap/10+self.size/4)*self.y))
                else:
                    self.move((self.startX+int(self.size/2)+int(self.gap/2) ), int(self.startY-self.size/2*self.y +(self.gap/10+self.size/4)*self.y))
                    
            painter.end()


        
    def getColor(self):
        if self.isDisplay==False:
            return Qt.transparent
        if self.me=='agent' or self.me=='agCollec':
            actualPov= self.getPov()
            if actualPov in list(self.model.agentSpecies[self.species]['POV'].keys()):
                self.model.agentSpecies[self.species]['selectedPOV']=self.model.agentSpecies[self.species]['POV'][actualPov]
                for aAtt in list(self.model.agentSpecies[self.species]['POV'][actualPov].keys()):
                    if aAtt in list(self.model.agentSpecies[self.species]['POV'][actualPov].keys()):
                        path=self.model.agentSpecies[self.species]['AgentList'][str(self.id)]['attributs'][aAtt]
                        theColor=self.model.agentSpecies[self.species]['POV'][str(actualPov)][str(aAtt)][str(path)]
                        self.color=theColor
                        return theColor

            else:
                if self.model.agentSpecies[self.species]['selectedPOV'] is not None:
                    for aAtt in list(self.model.agentSpecies[self.species]['selectedPOV'].keys()):
                        if aAtt in list(self.model.agentSpecies[self.species]['selectedPOV'].keys()):
                            path=self.model.agentSpecies[self.species]['AgentList'][str(self.id)]['attributs'][aAtt]
                            theColor=self.model.agentSpecies[self.species]['selectedPOV'][str(aAtt)][str(path)]
                            self.color=theColor
                    return theColor
                
                else:
                    return self.color
        if self.me == 'cell':
            if self.model.nameOfPov in self.theCollection.povs.keys():
                self.theCollection.povs['selectedPov']=self.theCollection.povs[self.getPov()]
                for aVal in list(self.theCollection.povs[self.model.nameOfPov].keys()):
                    if aVal in list(self.theCollection.povs[self.model.nameOfPov].keys()):
                        self.color=self.theCollection.povs[self.getPov()][aVal][self.dictOfAttributs[aVal]]
                        return self.theCollection.povs[self.getPov()][aVal][self.dictOfAttributs[aVal]]
            
            else:
                if self.theCollection.povs['selectedPov'] is not None:
                    for aVal in list(self.theCollection.povs['selectedPov'].keys()):
                        if aVal in list(self.theCollection.povs['selectedPov'].keys()):
                            self.color=self.theCollection.povs['selectedPov'][aVal][self.dictOfAttributs[aVal]]
                            return self.theCollection.povs['selectedPov'][aVal][self.dictOfAttributs[aVal]]
                else: 
                    self.color=Qt.white
                    return Qt.white
    
    #To get the pov
    def getPov(self):
        return self.model.nameOfPov