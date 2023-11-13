from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
from PyQt5.QtWidgets import  QAction, QGraphicsRectItem, QGraphicsView, QGraphicsScene
import random
from mainClasses.gameAction.SGGameActions import SGGameActions
from mainClasses.SGEntity import SGEntity
from mainClasses.SGGrid import SGGrid
from mainClasses.SGGameSpace import SGGameSpace

   
#Class who is responsible of the declaration a Agent
class SGAgent(SGEntity):
    # instances=[]

#FORMAT of agent avalaible : circleAgent squareAgent ellipseAgent1 ellipseAgent2 rectAgent1 rectAgent2 triangleAgent1 triangleAgent2 arrowAgent1 arrowAgent2
    def __init__(self,parent,cell,size,attributesAndValues,shapeColor,classDef):
        from mainClasses.SGEntityDef import SGCellDef
        if isinstance(parent,SGGrid): aGrid = parent
        elif isinstance(parent,SGCellDef): aGrid = parent.grid
        else: raise ValueError("wrong parent")
        super().__init__(aGrid,classDef, size,shapeColor,attributesAndValues)
        self.cell=None
        if cell is not None:
            self.moveTo(cell)
        self.xPos=self.getRandomX()
        self.yPos=self.getRandomY()
        

        

        
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
        # self.setGeometry(0,0,self.size+1,self.size+1) #CELA PROVOQUE UNE Infinite Loop de paintEvent
        agentShape = self.classDef.shape
        x = self.xPos
        y = self.yPos
        if self.isDisplay==True:
            if(agentShape=="circleAgent"):
                self.setGeometry(x,y,self.size+1,self.size+1)
                painter.drawEllipse(x,y,self.size,self.size)
            elif agentShape=="squareAgent":
                self.setGeometry(x,y,self.size+1,self.size+1)
                painter.drawRect(x,y,self.size,self.size)
            elif agentShape=="ellipseAgent1": 
                self.setGeometry(x,y,self.size*2+1,self.size+1)
                painter.drawEllipse(0,0,self.size*2,self.size)
            elif agentShape=="ellipseAgent2": 
                self.setGeometry(x,y,self.size+1,self.size*2+1)
                painter.drawEllipse(0,0,self.size,self.size*2)
            elif agentShape=="rectAgent1": 
                self.setGeometry(x,y,self.size*2+1,self.size+1)
                painter.drawRect(0,0,self.size*2,self.size)
            elif agentShape=="rectAgent2": 
                self.setGeometry(x,y,self.size+1,self.size*2+1)
                painter.drawRect(0,0,self.size,self.size*2)
            elif agentShape=="triangleAgent1": 
                self.setGeometry(x,y,self.size+1,self.size+1)
                points = QPolygon([
                QPoint(round(self.size/2),0),
                QPoint(0,self.size),
                QPoint(self.size,  self.size)
                ])
                painter.drawPolygon(points)
            elif agentShape=="triangleAgent2": 
                self.setGeometry(x,y,self.size+1,self.size+1)
                points = QPolygon([
                QPoint(0,0),
                QPoint(self.size,0),
                QPoint(round(self.size/2),self.size)
                ])
                painter.drawPolygon(points)
            elif agentShape=="arrowAgent1": 
                self.setGeometry(x,y,self.size+1,self.size+1)
                points = QPolygon([
                QPoint(round(self.size/2),0),
                QPoint(0,self.size),
                QPoint(round(self.size/2),round(self.size/3)*2),
                QPoint(self.size,  self.size)
                ])
                painter.drawPolygon(points)
            elif agentShape=="arrowAgent2": 
                self.setGeometry(x,y,self.size+1,self.size+1)
                points = QPolygon([
                QPoint(0,0),
                QPoint(round(self.size/2),round(self.size/3)),
                QPoint(self.size,0),
                QPoint(round(self.size/2),self.size)
                ])
                painter.drawPolygon(points)
            painter.end()
    
    # def getColor(self):
    #     if self.isDisplay==False:
    #         return Qt.transparent
    #     actualPov= self.getPov()
    #     if actualPov in list(self.model.agentSpecies[self.species]['POV'].keys()):
    #         self.model.agentSpecies[self.species]['selectedPOV']=self.model.agentSpecies[self.species]['POV'][actualPov]
    #         for aAtt in list(self.model.agentSpecies[self.species]['POV'][actualPov].keys()):
    #             if aAtt in list(self.model.agentSpecies[self.species]['POV'][actualPov].keys()):
    #                 path=self.model.agentSpecies[self.species]['AgentList'][str(self.id)]['attributs'][aAtt]
    #                 theColor=self.model.agentSpecies[self.species]['POV'][str(actualPov)][str(aAtt)][path]
    #                 self.color=theColor
    #                 return theColor

    #     elif actualPov not in list(self.model.agentSpecies[self.species]['POV'].keys()):
    #         if self.model.agentSpecies[self.species]['selectedPOV'] is not None:
    #             for aAtt in list(self.model.agentSpecies[self.species]['selectedPOV'].keys()):
    #                 if aAtt in list(self.model.agentSpecies[self.species]['selectedPOV'].keys()):
    #                     path=self.model.agentSpecies[self.species]['AgentList'][str(self.id)]['attributs'][aAtt]
    #                     theColor=self.model.agentSpecies[self.species]['selectedPOV'][str(aAtt)][path]
    #                     self.color=theColor
    #             return theColor
            
    #         else:
    #             return self.color
    #     else:
    #         return self.color

   #Funtion to handle the zoomIn
    def zoomIn(self,zoomFactor):
        self.size=round(self.size+(zoomFactor*10))
        self.update()

    #Funtion to handle the zoomOut
    def zoomOut(self,zoomFactor):
        self.size=round(self.size-(zoomFactor*10))
        self.update()

    def getRandomXY(self):
        if self.me=='agent':
            maxSize=self.cell.size
            x = random.randint(1,maxSize-1)
            return x
        else:
            x=0
            return x
        
    def getRandomX(self):        
        maxSize=self.cell.size
        originPoint=self.cell.pos()
        x = random.randint(originPoint.x()+5,originPoint.x()+maxSize-10)
        return x
        
    
    def getRandomY(self): 
        maxSize=self.cell.size
        originPoint=self.cell.pos()
        y = random.randint(originPoint.y()+5,originPoint.y()+maxSize-10)
        return y
        




    #To get the pov
    def getPov(self):
        return self.model.nameOfPov
    
    # To get the pov via grid
    def getPov2(self):
        return self.cell.grid.getCurrentPOV()


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            #Something is selected
            aLegendItem = self.model.getSelectedLegendItem()
            if aLegendItem is None : return #Exit the method

            authorisation=SGGameActions.getActionPermission(self)
        
            #The delete Action
            if aLegendItem.type == 'delete' : #or self.grid.model.selected[2].split()[0]== "Remove" :
                if authorisation : 
                    #We now check the feedBack of the actions if it have some
                    """if theAction is not None:
                        self.feedBack(theAction)"""
                    self.classDef.deleteEntity(self)
                    self.updateMqtt()

            #The  change value on agent
            elif aLegendItem.isValueOnAgent() :
                if  authorisation :
                    self.setValue(aLegendItem.nameOfAttribut,aLegendItem.valueOfAttribut)     
                    # self.update()

    #To handle the selection of an element int the legend
    # def mousePressEvent(self, event):
    #     return super().mousePressEvent(event)
        # if event.button() == Qt.LeftButton:
        #     #Something is selected
        #     if self.model.selected[0]!=None :
        #         authorisation=SGGameActions.getActionPermission(self)
        #         #The delete Action
        #         if self.model.selected[2].split()[0]== "Delete" or self.model.selected[2].split()[0]== "Remove":
        #             if  authorisation :
        #                 #We now check the feedBack of the actions if it have some
        #                 """if theAction is not None:
        #                         self.feedBack(theAction)"""
        #                 self.model.deleteAgent(self.species,self.id)
        #                 if self.model.mqttMajType == "Instantaneous":
        #                     SGGameActions.sendMqttMessage(self)
        #                 self.update()
        #         #Change the value of agent
        #         # # ! à retravailler   
        #         elif self.model.selected[1] in ("circleAgent","squareAgent", "ellipseAgent1","ellipseAgent2", "rectAgent1","rectAgent2", "triangleAgent1","triangleAgent2", "arrowAgent1","arrowAgent2"):
        #             if  authorisation :
        #                 """if len(self.history["value"])==0:
        #                     self.history["value"].append([0,0,self.attributs])"""
        #                 #We now check the feedBack of the actions if it have some
        #                 """if theAction is not None:
        #                         self.feedBack(theAction)"""
        #                 aDictWithValue={self.model.selected[4]:self.model.selected[3]}
        #                 if self.model.mqttMajType == "Instantaneous":
        #                     SGGameActions.sendMqttMessage(self)  
        #                 """for aVal in list(aDictWithValue.keys()) :
        #                     if aVal in list(self.theCollection.povs[self.model.nameOfPov].keys()) :
        #                             for anAttribute in list(self.theCollection.povs[self.model.nameOfPov].keys()):
        #                                 self.attributs.pop(anAttribute,None)
        #                                 self.history["value"].append([self.model.timeManager.currentRound,self.model.timeManager.currentPhase,self.attributs])
        #                 self.attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]"""
        #                 self.update()
                        

                    
    #Apply the feedBack of a gameMechanics
    def feedBack(self, theAction):
        booleanForFeedback=True
        for anCondition in theAction.conditionOfFeedBack :
            booleanForFeedback=booleanForFeedback and anCondition(self)
        if booleanForFeedback :
            for aFeedback in  theAction.feedback :
                aFeedback(self)

    #To handle the drag of the agent
    def mouseMoveEvent(self, e):
    
        if e.buttons() != Qt.LeftButton:
            return
        authorisation = SGGameActions.getMovePermission(self)
        
        if authorisation:
            self.cell.updateDepartureAgent(self)
            mimeData = QMimeData()

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(e.pos() - self.rect().topLeft())

            drag.exec_(Qt.CopyAction | Qt.MoveAction)


    
    def addPovinMenuBar(self,nameOfPov):
        if nameOfPov not in self.model.listOfPovsForMenu :
            self.model.listOfPovsForMenu.append(nameOfPov)
            anAction=QAction(" &"+nameOfPov, self)
            self.model.povMenu.addAction(anAction)
            anAction.triggered.connect(lambda: self.model.setInitialPov(nameOfPov))


            

#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    # def setValue(self,attribut,value):
    #     #OBSOLETE    should use setValue()
    #     """
    #     Update a Agent attribut value

    #     Args:
    #         attribut (str): attribut concerned by the update
    #         value (str): value previously declared in the species, to update
    #     """
    #     # cette méthode semble etre utilisé pour set la defaultValue, et si c'est le cas la façon d'appeler est à reprendre  Entity
    #     #sinon supprimer cette méthode car elle est remplaé par setValue de Entity
    #     if self.me=='agent':
    #         self.dictAttributes[attribut]=value 
    
    def initDefaultAttValue(self,Att,Val):
        """
        Initialize a default attribute value in a species

        Args:
            Att : concerned attribute
            Val : default value

        """
        # cette méthode est à remonter au niveau de Entity
        if self.me=='collec' and self.dictAttributes is not None:
            self.dictOfAttributesDefaultValues[Att]=Val
        else:
            raise ValueError("A default attribute value needs to be on a Species.")
    
    def moveTo(self, aDestinationCell):
        if self.cell != None:
            self.cell.updateDepartureAgent(self)
        self.cell = aDestinationCell
        aDestinationCell.updateIncomingAgent(self)



    def moveAgent(self,method="random",direction=None,cellID=None,numberOfMovement=1):
        """
        Model action to move an Agent.

        args:
            method (str): random, cell, cardinal
            direction (str): if cardinal; North, South, West, East
            cellID (str): if cell; cellx-y
            numberOfMouvement (int): number of movement in one action
        """
        for i in range(numberOfMovement):

            if i>0:
                oldAgent=theAgent
                originCell=oldAgent.cell
            else:
                oldAgent=self
                originCell=self.cell

            aGrid=originCell.grid

            if method == "random":
                neighbors=originCell.getNeighborCells(aGrid.rule)
                newCell=random.choice(neighbors)

            if method == "cell" or cellID is not None:
                newCell=aGrid.getCell_withId(aGrid,cellID)

            if method == "cardinal" or direction is not None:
                if direction =="North":
                    newCell=aGrid.getCell(originCell.x,originCell.y-1)
                if direction =="South":
                    newCell=aGrid.getCell(originCell.x,originCell.y+1)
                if direction =="East":
                    newCell=aGrid.getCell(originCell.x+1,originCell.y)
                if direction =="West":
                    newCell=aGrid.getCell(originCell.x-1,originCell.y)
            
            if newCell is None:
                pass
            else:
                theAgent = self.model.copyOfAgentAtCoord(newCell,oldAgent)
                oldAgent.deleteLater()
        pass
                
    #Function to check the ownership  of the agent          
    def isMine(self):
        return self.owner==self.model.currentPlayer
    
    def getId(self):
        return self.id
    
    def getPrivateId(self):
        return self.privateID 
    
    #Function to check the ownership  of the agent          
    def isMineOrAdmin(self):
        return self.owner==self.model.currentPlayer or self.owner=="admin"
    
    #Function to change the ownership         
    def makeOwner(self,newOwner):
        self.owner=newOwner
        
    #Function get the ownership        
    def getProperty(self):
        self.owner=self.model.currentPlayer
    
        
    #Function to check the old value of an Agent       
    def checkPrecedenteValue(self,precedentValue):
        """OBSOLETE"""
        if not len(self.history["value"]) ==0:
            for aVal in list(self.history["value"][len(self.history["value"])].thingsSave.keys()) :
                if aVal in list(self.theCollection.povs[self.model.nameOfPov].keys()) :
                    return self.history["value"][len(self.history["value"])].thingsSave[aVal]
        else: 
            for aVal in list(self.attributs.keys()) :
                if aVal in list(self.theCollection.povs[self.model.nameOfPov].keys()) :
                    return self.attributs[aVal]