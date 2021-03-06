import random

from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true, values

from SGAgentCollection import SGAgentCollection


   
#Class who is responsible of the declaration a Agent
class SGAgent(QtWidgets.QWidget):
    
#FORMAT of agent avalaible : circleAgent squareAgent ellipseAgent1 ellipseAgent2 rectAgent1 rectAgent2 triangleAgent1 triangleAgent2 arrowAgent1 arrowAgent2
    def __init__(self,parent,name,format,size,methodOfPlacement="random"):
        super().__init__(parent)
        #Basic initialize
        self.parent=parent
        if(parent!=None):
            self.theCollection=parent.collectionOfAgents
        else:
            self.theCollection=SGAgentCollection(None)
        self.name=name
        self.format=format
        self.size=size
        #We place the default pos
        self.startXBase=0
        self.startYBase=0
        #We init the dict of Attribute
        self.attributs={}
        #For the placement of the agents
        self.methodOfPlacement=methodOfPlacement
        self.x=0
        self.y=0   
        #We define an owner by default
        self.owner="admin"    
        #We define variable to handle an history 
        self.history={}
        self.history["value"]=[]
        self.history["coordonates"]=[]
        

        
        
    #Drawing function
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
        self.setGeometry(0,0,self.size+1,self.size+1)
        if(self.format=="circleAgent"):
            painter.drawEllipse(0,0,self.size,self.size)
        elif self.format=="squareAgent":
            painter.drawRect(0,0,self.size,self.size)
        elif self.format=="ellipseAgent1": 
            self.setGeometry(0,0,self.size*2+1,self.size+1)
            painter.drawEllipse(0,0,self.size*2,self.size)
        elif self.format=="ellipseAgent2": 
            self.setGeometry(0,0,self.size+1,self.size*2+1)
            painter.drawEllipse(0,0,self.size,self.size*2)
        elif self.format=="rectAgent1": 
            self.setGeometry(0,0,self.size*2+1,self.size+1)
            painter.drawRect(0,0,self.size*2,self.size)
        elif self.format=="rectAgent2": 
            self.setGeometry(0,0,self.size+1,self.size*2+1)
            painter.drawRect(0,0,self.size,self.size*2)
        elif self.format=="triangleAgent1": 
            self.setGeometry(0,0,self.size+1,self.size+1)
            points = QPolygon([
               QPoint(round(self.size/2),0),
               QPoint(0,self.size),
               QPoint(self.size,  self.size)
            ])
            painter.drawPolygon(points)
        elif self.format=="triangleAgent2": 
            self.setGeometry(0,0,self.size+1,self.size+1)
            points = QPolygon([
               QPoint(0,0),
               QPoint(self.size,0),
               QPoint(round(self.size/2),self.size)
            ])
            painter.drawPolygon(points)
        elif self.format=="arrowAgent1": 
            self.setGeometry(0,0,self.size+1,self.size+1)
            points = QPolygon([
               QPoint(round(self.size/2),0),
               QPoint(0,self.size),
               QPoint(round(self.size/2),round(self.size/3)*2),
               QPoint(self.size,  self.size)
            ])
            painter.drawPolygon(points)
        elif self.format=="arrowAgent2": 
            self.setGeometry(0,0,self.size+1,self.size+1)
            points = QPolygon([
               QPoint(0,0),
               QPoint(round(self.size/2),round(self.size/3)),
               QPoint(self.size,0),
               QPoint(round(self.size/2),self.size)
            ])
            painter.drawPolygon(points)
            
        
        
        if self.x==0 and self.y==0 :
            if self.parent.format=="square":
                self.x= random.randint(0, self.parent.rect().bottomRight().x()-(round(self.size/2))*2)
                self.y= random.randint(0, self.parent.rect().bottomRight().y()-(round(self.size/2))*2)
            else :
                self.x=random.randint(0, self.parent.rect().bottomRight().x()-(round(self.size/3))*2)
                self.y=round(self.parent.size/3)+random.randint(0, self.parent.rect().bottomRight().y()-(round(self.parent.size/3))*2)
        self.move(self.x,self.y)
        painter.end()
    
    
    def getId(self):
        return "agent"+str(self.name)
    

    #Funtion to handle the zoom
    def zoomIn(self):
        #To be reworked
        return True
    
    def zoomOut(self):
        #To be reworked
        return True
        
    def zoomFit(self):
        #To be reworked
        return True
        
    #To manage the attribute system of an Agent
    def getColor(self):
        for aVal in list(self.theCollection.povs[self.parent.parent.parent.nameOfPov].keys()): 
            if aVal in list(self.attributs.keys()):
                return self.theCollection.povs[self.getPov()][aVal][self.attributs[aVal]]

           
    #To get the pov
    def getPov(self):
        return self.parent.parent.parent.nameOfPov
    
    #Set parent
    def setParent(self,parent):
        self.parent=parent
        self.theCollection=parent.collectionOfAgents
        
    #To handle the selection of an element int the legend
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            #Something is selected
            if self.parent.parent.parent.selected[0]!=None :
                #We shearch if the player have the rights
                thePlayer=self.parent.parent.parent.getPlayer()
                authorisation=False
                theAction=None
                if self.parent.parent.parent.selected[0].isFromAdmin():
                    authorisation=True
                elif thePlayer is not None :
                    theAction=thePlayer.getGameActionOn(self)
                    if theAction is not None:
                        authorisation=theAction.getAuthorize(self)
                        if authorisation : 
                            theAction.use()
                #The delete Action
                if self.parent.parent.parent.selected[2].split()[0]== "Delete" or self.parent.parent.parent.selected[2].split()[0]== "Remove":
                    if  authorisation :
                        #We now check the feedBack of the actions if it have some
                        if theAction is not None:
                                self.feedBack(theAction)
                        for i in reversed(range(len(self.parent.collectionOfAgents.agents))):
                            if self.parent.collectionOfAgents.agents[i] == self :
                                self.parent.collectionOfAgents.agents[i].deleteLater()
                                del self.parent.collectionOfAgents.agents[i]
                        self.update()
                #Change the value of agent   
                elif self.parent.parent.parent.selected[1]== "circleAgent" or self.parent.parent.parent.selected[1]=="squareAgent" or self.parent.parent.parent.selected[1]== "ellipseAgent1" or self.parent.parent.parent.selected[1]=="ellipseAgent2" or self.parent.parent.parent.selected[1]== "rectAgent1" or self.parent.parent.parent.selected[1]=="rectAgent2" or self.parent.parent.parent.selected[1]== "triangleAgent1" or self.parent.parent.parent.selected[1]=="triangleAgent2" or self.parent.parent.parent.selected[1]== "arrowAgent1" or self.parent.parent.parent.selected[1]=="arrowAgent2":
                    if  authorisation :
                        if len(self.history["value"])==0:
                            self.history["value"].append([0,0,self.attributs])
                        #We now check the feedBack of the actions if it have some
                        if theAction is not None:
                                self.feedBack(theAction)
                        aDictWithValue={self.parent.parent.parent.selected[4]:self.parent.parent.parent.selected[3]}    
                        for aVal in list(aDictWithValue.keys()) :
                            if aVal in list(self.theCollection.povs[self.parent.parent.parent.nameOfPov].keys()) :
                                    for anAttribute in list(self.theCollection.povs[self.parent.parent.parent.nameOfPov].keys()):
                                        self.attributs.pop(anAttribute,None)
                                        self.history["value"].append([self.parent.parent.parent.timeManager.actualRound,self.parent.parent.parent.timeManager.actualPhase,self.attributs])
                        self.attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]
                        self.update()
                        
                        
        self.parent.parent.parent.client.publish(self.parent.parent.parent.whoIAm,self.parent.parent.parent.submitMessage())
                    
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
        
        thePlayer=self.parent.parent.parent.getPlayer()
        authorisation=False
        theAction=None
        if self.parent.parent.parent.whoIAm=="Admin":
            authorisation=true
        elif thePlayer is not None :
            theAction=thePlayer.getMooveActionOn(self)
            if theAction is not None:
                authorisation=theAction.getAuthorize(self)
                if authorisation : 
                    theAction.use()
        
        if authorisation:

            mimeData = QMimeData()

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(e.pos() - self.rect().topLeft())

            drag.exec_(Qt.MoveAction) 
    
        
            

#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    #To set the value of an agent without the pov
    def setUpAgentValue(self,aDictOfValue):
        for anAttribut in aDictOfValue:
            if anAttribut in list(self.theCollection.povs[self.parent.parent.parent.nameOfPov].keys()):
                for aVal in list(self.theCollection.povs[self.parent.parent.parent.nameOfPov].keys()):
                    self.attributs[aVal]=[]
                for aVal in list(self.theCollection.povs[self.parent.parent.parent.nameOfPov].keys()):
                    del self.attributs[aVal]
                self.attributs[anAttribut]=aDictOfValue[anAttribut]
                
    #Function to check the ownership  of the agent          
    def isMine(self):
        return self.owner==self.parent.parent.parent.actualPlayer
    
    #Function to check the ownership  of the agent          
    def isMineOrAdmin(self):
        return self.owner==self.parent.parent.parent.actualPlayer or self.owner=="admin"
    
    #Function to change the ownership         
    def makeOwner(self,newOwner):
        self.owner=newOwner
        
    #Function get the ownership        
    def getProperty(self):
        self.owner=self.parent.parent.parent.actualPlayer
        
    #Function to change the value      
    def changeValue(self,aDictOfValue):
        if len(self.history["value"])==0:
            self.history["value"].append([0,0,self.attributs])
        for aVal in list(aDictOfValue.keys()) :
            if aVal in list(self.theCollection.povs[self.parent.parent.parent.nameOfPov].keys()) :
                    for anAttribute in list(self.theCollection.povs[self.parent.parent.parent.nameOfPov].keys()):
                        self.attributs.pop(anAttribute,None)
        self.attributs[list(aDictOfValue.keys())[0]]=aDictOfValue[list(aDictOfValue.keys())[0]]
        self.history["value"].append([self.parent.parent.parent.timeManager.actualRound,self.parent.parent.parent.timeManager.actualPhase,self.attributs])
        
        
    #Function to check the value      
    def checkValue(self,aDictOfValue):
        if list(aDictOfValue.keys())[0] in list(self.attributs.keys()) :
            return self.attributs[list(aDictOfValue.keys())[0]]==list(aDictOfValue.values())[0]
        return False
    
    
    #Function get if the agent have change the value in       
    def haveChangeValue(self,numberOfRound=1):
        haveChange=False
        if not len(self.history["value"]) ==0:
            for anItem in self.history["value"].reverse():
                if anItem.roundNumber> self.parent.parent.timeManager.actualRound-numberOfRound:
                    if not anItem.thingsSave == self.attributs:
                        haveChange=True
                        break
                elif anItem.roundNumber== self.parent.parent.timeManager.actualRound-numberOfRound:
                    if anItem.phaseNumber<=self.parent.parent.timeManager.actualPhase:
                        if not anItem.thingsSave == self.attributs:
                            haveChange=True
                            break
        return haveChange
    
    #Function get if the agent have change the value in       
    def haveMoove(self,numberOfRound=1):
        haveChange=False
        if not len(self.history["coordonates"]) ==0:
            for anItem in self.history["coordonates"].reverse():
                if anItem.roundNumber> self.parent.parent.timeManager.actualRound-numberOfRound:
                    if not anItem.thingsSave == self.attributs:
                        haveChange=True
                        break
                elif anItem.roundNumber== self.parent.parent.timeManager.actualRound-numberOfRound:
                    if anItem.phaseNumber<=self.parent.parent.timeManager.actualPhase:
                        if not anItem.thingsSave == self.attributs:
                            haveChange=True
                            break
        return haveChange
        
    #Function to check the old value of an Agent       
    def checkPrecedenteValue(self,precedentValue):
        if not len(self.history["value"]) ==0:
            for aVal in list(self.history["value"][len(self.history["value"])].thingsSave.keys()) :
                if aVal in list(self.theCollection.povs[self.parent.parent.parent.nameOfPov].keys()) :
                    return self.history["value"][len(self.history["value"])].thingsSave[aVal]
        else: 
            for aVal in list(self.attributs.keys()) :
                if aVal in list(self.theCollection.povs[self.parent.parent.parent.nameOfPov].keys()) :
                    return self.attributs[aVal]