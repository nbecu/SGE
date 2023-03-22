from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
from PyQt5.QtWidgets import  QAction

   
#Class who is responsible of the declaration a Agent
class SGAgent(QtWidgets.QWidget):
    
#FORMAT of agent avalaible : circleAgent squareAgent ellipseAgent1 ellipseAgent2 rectAgent1 rectAgent2 triangleAgent1 triangleAgent2 arrowAgent1 arrowAgent2
    def __init__(self,parent,name,format,defaultsize,dictOfAttributs,id,methodOfPlacement="random"):
        super().__init__(parent)
        #Basic initialize
        self.parent=parent
        self.name=name
        self.format=format
        self.size=defaultsize
        #We place the default pos
        self.startXBase=0
        self.startYBase=0
        #We init the dict of Attribute
        self.dictOfAttributs=dictOfAttributs
        #For the placement of the agents
        self.methodOfPlacement=methodOfPlacement
        self.x=0
        self.y=0   
        #We define an owner by default
        self.owner="admin"    
        #We define variable to handle an history 
        self.history={}
        self.history["value"]=[]
        self.history["coordinates"]=[]
        #We define the identification parameters
        self.me=0
        self.id=id
        self.species=0
        self.isDisplay=bool
        

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
        painter.end()

        
    #To manage the attribute system of an Agent
    def getColor(self):
        if self.isDisplay==False:
            return Qt.transparent
        actualPov= self.getPov()
        if actualPov in list(self.parent.parent.parent.AgentSpecies[self.species]['POV'].keys()):
            self.parent.parent.parent.AgentSpecies[self.species]['selectedPOV']=self.parent.parent.parent.AgentSpecies[self.species]['POV'][actualPov]
            for aAtt in list(self.parent.parent.parent.AgentSpecies[self.species]['POV'][actualPov].keys()):
                if aAtt in list(self.parent.parent.parent.AgentSpecies[self.species]['POV'][actualPov].keys()):
                    path=self.parent.parent.parent.AgentSpecies[self.species]['AgentList'][str(self.id)]['attributs'][aAtt]
                    theColor=self.parent.parent.parent.AgentSpecies[self.species]['POV'][str(actualPov)][str(aAtt)][str(path)]
                    return theColor

        else:
            if self.parent.parent.parent.AgentSpecies[self.species]['selectedPOV'] is not None:
                for aAtt in list(self.parent.parent.parent.AgentSpecies[self.species]['selectedPOV'].keys()):
                    if aAtt in list(self.parent.parent.parent.AgentSpecies[self.species]['selectedPOV'].keys()):
                        path=self.parent.parent.parent.AgentSpecies[self.species]['AgentList'][str(self.id)]['attributs'][aAtt]
                        theColor=self.parent.parent.parent.AgentSpecies[self.species]['selectedPOV'][str(aAtt)][str(path)]
                return theColor
            
            else:
                return Qt.white


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
                #We search if the player have the rights
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
                        
                        
        self.parent.parent.parent.publishEntitiesState()
                    
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
            print(str(self.x)+","+str(self.y))
            mimeData = QMimeData()

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(e.pos() - self.rect().topLeft())

            drag.exec_(Qt.MoveAction)
     
            

#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    #To set up a POV
    def setUpPov(self,nameofPOV,concernedAtt,dictOfColor):
        if self.parent.AgentSpecies[str(self.name)]['me']=='collec':
            self.parent.AgentSpecies[str(self.name)]["POV"][str(nameofPOV)]={str(concernedAtt):dictOfColor}
            self.addPovinMenuBar(nameofPOV)
        else:
            print("Warning, a POV can be only define on a Species")

    def addPovinMenuBar(self,nameOfPov):
        if nameOfPov not in self.parent.listOfPovsForMenu :
            self.parent.listOfPovsForMenu.append(nameOfPov)
            anAction=QAction(" &"+nameOfPov, self)
            self.parent.povMenu.addAction(anAction)
            anAction.triggered.connect(lambda: self.parent.setInitialPov(nameOfPov))
        

    def updateAgentValue(self,attribut,value):
        if self.parent.parent.parent.AgentSpecies[str(self.species)]['AgentList'][str(self.id)]['me']=='agent':
            self.parent.parent.parent.AgentSpecies[str(self.species)]['AgentList'][str(self.id)]['attributs'][str(attribut)]=str(value)
        else:
            print("Warning")

            #self.AgentSpecies={str(aAgentSpecies.name): {'AgentList':{str(anAgentID):{"me":aAgent.me

                
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
    
    #Function get if the agent have change the value in       
    def haveMoove(self,numberOfRound=1):
        haveChange=False
        if not len(self.history["coordinates"]) ==0:
            for anItem in self.history["coordinates"].reverse():
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