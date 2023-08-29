from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import random

# Class who is in charged of entities : cells and agents
class SGEntity(QtWidgets.QWidget):
    def __init__(self,parent,shape,defaultsize,dictOfAttributs,me,uniqueColor=Qt.white):
        super().__init__(parent)
        self.model=self.parent
        self.me=me
        self.dictOfAttributs=dictOfAttributs
        self.shape=shape
        self.isDisplay=True
        self.owner="admin"
        self.x=0
        self.y=0 
        self.size=defaultsize
        self.color=uniqueColor

    def paintEvent(self):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
        painter.setPen(QPen(self.getBorderColor(),self.getBorderWidth())) # ! getBorderColor / get BorderWidth for agents
        if self.isDisplay==True:
            if self.me=='agent':           
                self.setGeometry(0,0,self.size+1,self.size+1)
                x = self.getRandomXY()
                y = self.getRandomXY()
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

            if self.me == 'cell':
                self.startXBase=self.grid.startXBase
                self.startYBase=self.grid.startYBase
                self.startX=int(self.startXBase+self.gap*(self.x -1)+self.size*(self.x -1)+self.gap) 
                self.startY=int(self.startYBase+self.gap*(self.y -1)+self.size*(self.y -1)+self.gap)
                if (self.shape=="hexagonal"):
                    self.startY=self.startY+self.size/4
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
        if self.me=='agent':
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
            grid=self.grid
            if self.model.nameOfPov in self.cellCollection[grid.id]["ColorPOV"].keys():
                self.cellCollection[grid.id]["ColorPOV"]['selectedPov']=self.cellCollection[grid.id]["ColorPOV"][self.getPov()]
                for aVal in list(self.cellCollection[grid.id]["ColorPOV"][self.model.nameOfPov].keys()):
                    if aVal in list(self.cellCollection[grid.id]["ColorPOV"][self.model.nameOfPov].keys()):
                        self.color=self.cellCollection[grid.id]["ColorPOV"][self.getPov()][aVal][self.dictOfAttributs[aVal]]
                        return self.cellCollection[grid.id]["ColorPOV"][self.getPov()][aVal][self.dictOfAttributs[aVal]]
            
            else:
                if self.cellCollection[grid.id]["ColorPOV"]['selectedPov'] is not None:
                    for aVal in list(self.cellCollection[grid.id]["ColorPOV"]['selectedPov'].keys()):
                        if aVal in list(self.cellCollection[grid.id]["ColorPOV"]['selectedPov'].keys()):
                            self.color=self.cellCollection[grid.id]["ColorPOV"]['selectedPov'][aVal][self.dictOfAttributs[aVal]]
                            return self.cellCollection[grid.id]["ColorPOV"]['selectedPov'][aVal][self.dictOfAttributs[aVal]]
                else: 
                    self.color=Qt.white
                    return Qt.white
                
    
    def getBorderColor(self):
        if self.isDisplay==False:
            return Qt.transparent
        if self.me == 'agent':
            return Qt.black
        if self.me == 'cell':
            grid=self.grid
            if self.grid.model.nameOfPov in self.cellCollection[grid.id]["BorderPOV"].keys():
                self.cellCollection[grid.id]["BorderPOV"]['selectedBorderPov']=self.cellCollection[grid.id]["BorderPOV"][self.getPov()]
                for aVal in list(self.cellCollection[grid.id]["BorderPOV"][self.grid.model.nameOfPov].keys()):
                    if aVal in list(self.cellCollection[grid.id]["BorderPOV"][self.grid.model.nameOfPov].keys()):
                        self.borderColor=self.cellCollection[grid.id]["BorderPOV"][self.getPov()][aVal][self.attributs[aVal]]
                        return self.cellCollection[grid.id]["BorderPOV"][self.getPov()][aVal][self.attributs[aVal]]
            
            else:
                self.borderColor=Qt.black
                return Qt.black
    
    def getBorderWidth(self):
        if self.me == 'agent':
            return int(1)
        if self.me == 'cell':
            grid=self.grid
            if self.cellCollection[grid.id]["BorderPOV"] is not None and self.grid.model.nameOfPov in self.cellCollection[grid.id]["BorderPOV"].keys():
                    return int(self.cellCollection[grid.id]["BorderPOV"]["BorderWidth"])
            return int(1)
    
    #To get the pov
    def getPov(self):
        return self.model.nameOfPov

    def getRandomXY(self):
        x = 0
        maxSize=self.cell.size
        x = random.randint(1,maxSize-1)
        return x
