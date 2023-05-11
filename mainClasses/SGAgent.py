from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
from PyQt5.QtWidgets import  QAction, QGraphicsRectItem, QGraphicsView, QGraphicsScene
import random
from gameAction.SGGameActions import SGGameActions

   
#Class who is responsible of the declaration a Agent
class SGAgent(QtWidgets.QWidget):
    instances=[]
    
#FORMAT of agent avalaible : circleAgent squareAgent ellipseAgent1 ellipseAgent2 rectAgent1 rectAgent2 triangleAgent1 triangleAgent2 arrowAgent1 arrowAgent2
    def __init__(self,parent,name,format,defaultsize,dictOfAttributs,id,me,uniqueColor=Qt.white,methodOfPlacement="random"):
        super().__init__(parent)
        #Basic initialize
        self.me=me
        if self.me=='agent':
            self.cell=parent
            self.model=self.cell.grid.model
        elif self.me=='collec':
            self.model=parent
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
        self.id=id
        self.species=0
        self.isDisplay=bool
        self.instances.append(self)
        self.color=uniqueColor
        

 


    def getWidget(self):
        scene = QGraphicsScene()
        rect = QGraphicsRectItem(0, 0, 10, 10)
        # rect.setPos(0, 0)
        brush = QBrush(Qt.red)
        rect.setBrush(brush)
        pen = QPen(Qt.cyan)
        pen.setWidth(1)
        rect.setPen(pen)

        scene.addItem(rect)
        view = QGraphicsView(scene)
        view.setRenderHint(QPainter.Antialiasing)
        return view

        # return QPolygon([
        #         QPoint(0, 0),
        #         QPoint(0,5),
        #         QPoint(5,0),
        #         QPoint(5,5)]) 

        # if(self.format=="circleAgent"):
        #         painter.drawEllipse(0,0,self.size,self.size)
        #     elif self.format=="squareAgent":
        #         painter.drawRect(0,0,self.size,self.size)
        #     elif self.format=="ellipseAgent1": 
        #         self.setGeometry(0,0,self.size*2+1,self.size+1)
        #         painter.drawEllipse(0,0,self.size*2,self.size)
        #     elif self.format=="ellipseAgent2": 
        #         self.setGeometry(0,0,self.size+1,self.size*2+1)
        #         painter.drawEllipse(0,0,self.size,self.size*2)
        #     elif self.format=="rectAgent1": 
        #         self.setGeometry(0,0,self.size*2+1,self.size+1)
        #         painter.drawRect(0,0,self.size*2,self.size)
        #     elif self.format=="rectAgent2": 
        #         self.setGeometry(0,0,self.size+1,self.size*2+1)
        #         painter.drawRect(0,0,self.size,self.size*2)
        #     elif self.format=="triangleAgent1": 
        #         self.setGeometry(0,0,self.size+1,self.size+1)
        #         points = QPolygon([
        #         QPoint(round(self.size/2),0),
        #         QPoint(0,self.size),
        #         QPoint(self.size,  self.size)
        #         ])
        #         painter.drawPolygon(points)
        #     elif self.format=="triangleAgent2": 
        #         self.setGeometry(0,0,self.size+1,self.size+1)
        #         points = QPolygon([
        #         QPoint(0,0),
        #         QPoint(self.size,0),
        #         QPoint(round(self.size/2),self.size)
        #         ])
        #         painter.drawPolygon(points)
        #     elif self.format=="arrowAgent1": 
        #         self.setGeometry(0,0,self.size+1,self.size+1)
        #         points = QPolygon([
        #         QPoint(round(self.size/2),0),
        #         QPoint(0,self.size),
        #         QPoint(round(self.size/2),round(self.size/3)*2),
        #         QPoint(self.size,  self.size)
        #         ])
        #         painter.drawPolygon(points)
        #     elif self.format=="arrowAgent2": 
        #         self.setGeometry(0,0,self.size+1,self.size+1)
        #         points = QPolygon([
        #         QPoint(0,0),
        #         QPoint(round(self.size/2),round(self.size/3)),
        #         QPoint(self.size,0),
        #         QPoint(round(self.size/2),self.size)
        #         ])
        #         painter.drawPolygon(points)
        # painter.end()   
        
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
        self.setGeometry(0,0,self.size+1,self.size+1)
        if self.isDisplay==True:
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
                self.setGeometry(20,20,self.size+1,self.size+1)
                points = QPolygon([
                QPoint(round(self.size/2),0),
                QPoint(0,self.size),
                QPoint(self.size,  self.size)
                ])
                painter.drawPolygon(points)
            elif self.format=="triangleAgent2": 
                self.setGeometry(40,40,self.size+1,self.size+1)
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

   #Funtion to handle the zoomIn
    def zoomIn(self,zoomFactor):
        """NOT TESTED"""
        self.size=round(self.size+(zoomFactor*10))
        self.update()

    #Funtion to handle the zoomOut
    def zoomOut(self,zoomFactor):
        """NOT TESTED"""
        self.size=round(self.size-(zoomFactor*10))
        self.update()


    #To manage the attribute system of an Agent
    def getColor(self):
        if self.isDisplay==False:
            return Qt.transparent
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


    #To get the pov
    def getPov(self):
        return self.model.nameOfPov
    
    # To get the pov via grid
    def getPov2(self):
        return self.cell.grid.getCurrentPOV()
        
    #To handle the selection of an element int the legend
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            #Something is selected
            if self.model.selected[0]!=None :
                authorisation=SGGameActions.getActionPermission(self)
                """#We search if the player have the rights
                thePlayer=self.model.getPlayerObject(self.model.getCurrentPlayer())
                authorisation=False
                theAction = None
                if thePlayer == "Admin":
                    authorisation=True

                elif thePlayer is not None and thePlayer != "Admin":
                    theAction=thePlayer.getGameActionOn(self)
                    if theAction is not None:
                        authorisation=theAction.getAuthorize(self)
                        if authorisation : 
                            theAction.use()"""
                #The delete Action
                if self.model.selected[2].split()[0]== "Delete" or self.model.selected[2].split()[0]== "Remove":
                    if  authorisation :
                        #We now check the feedBack of the actions if it have some
                        """if theAction is not None:
                                self.feedBack(theAction)"""
                        for i in reversed(range(len(self.cell.agents))):
                            if self.cell.agents[i] == self :
                                self.cell.agents[i].deleteLater()
                                del self.cell.agents[i]
                                if self.species in self.model.agentSpecies and 'AgentList' in self.model.agentSpecies[self.species]:
                                    self.model.agentSpecies[self.species]['AgentList'].pop('1', None)
                        self.update()
                #Change the value of agent   
                elif self.model.selected[1]== "circleAgent" or self.model.selected[1]=="squareAgent" or self.model.selected[1]== "ellipseAgent1" or self.model.selected[1]=="ellipseAgent2" or self.model.selected[1]== "rectAgent1" or self.model.selected[1]=="rectAgent2" or self.model.selected[1]== "triangleAgent1" or self.model.selected[1]=="triangleAgent2" or self.model.selected[1]== "arrowAgent1" or self.model.selected[1]=="arrowAgent2":
                    if  authorisation :
                        """if len(self.history["value"])==0:
                            self.history["value"].append([0,0,self.attributs])"""
                        #We now check the feedBack of the actions if it have some
                        """if theAction is not None:
                                self.feedBack(theAction)"""
                        aDictWithValue={self.model.selected[4]:self.model.selected[3]}    
                        """for aVal in list(aDictWithValue.keys()) :
                            if aVal in list(self.theCollection.povs[self.model.nameOfPov].keys()) :
                                    for anAttribute in list(self.theCollection.povs[self.model.nameOfPov].keys()):
                                        self.attributs.pop(anAttribute,None)
                                        self.history["value"].append([self.model.timeManager.currentRound,self.model.timeManager.currentPhase,self.attributs])
                        self.attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]"""
                        self.update()
                        

                    
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
        """thePlayer=self.model.getPlayerObject(self.model.getCurrentPlayer())
        authorisation=False
        theAction = None
        if thePlayer == "Admin":
            authorisation=True

        elif thePlayer is not None and thePlayer != "Admin":
            theAction=thePlayer.getMooveActionOn(self)  
            if theAction is not None:
                authorisation=theAction.getAuthorize(self)
                print('ok')
                if authorisation :
                    print('ok') 
                    theAction.use()"""
        
        if authorisation:
            print(str(self.x)+","+str(self.y))
            print([self.cell.x,self.cell.y])
            self.cell.updateDepartureAgent(self)
            mimeData = QMimeData()

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(e.pos() - self.rect().topLeft())

            drag.exec_(Qt.MoveAction)
     
            

#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    #To set up a POV
    def newPov(self,nameofPOV,concernedAtt,dictOfColor):
        """
        Declare a new Point of View for the Species.

        Args:
            self (Species object): aSpecies
            nameOfPov (str): name of POV, will appear in the interface
            concernedAtt (str): name of the attribut concerned by the declaration
            DictofColors (dict): a dictionary with all the attribut values, and for each one a Qt.Color (https://doc.qt.io/archives/3.3/qcolor.html)
            
        """
        if self.model.agentSpecies[str(self.name)]['me']=='collec':
            self.model.agentSpecies[str(self.name)]["POV"][str(nameofPOV)]={str(concernedAtt):dictOfColor}
            self.addPovinMenuBar(nameofPOV)
        else:
            print("Warning, a POV can be only define on a Species")

    def addPovinMenuBar(self,nameOfPov):
        if nameOfPov not in self.model.listOfPovsForMenu :
            self.model.listOfPovsForMenu.append(nameOfPov)
            anAction=QAction(" &"+nameOfPov, self)
            self.model.povMenu.addAction(anAction)
            anAction.triggered.connect(lambda: self.model.setInitialPov(nameOfPov))
        

    def setValueAgent(self,attribut,value):
        """
        Update a Agent attribut value

        Args:
            attribut (str): attribut concerned by the update
            value (str): value previously declared in the species, to update
        """
        if self.me=='agent':
            self.model.agentSpecies[str(self.species)]['AgentList'][str(self.id)]['attributs'][str(attribut)]=str(value)
        elif self.me=='collec':
            dict=self.model.agentSpecies[self.name]['AgentList']
            for agent in dict.keys():
                dict[agent]['attributs'][str(attribut)]=str(value)
            

    def moveAgent(self,aGrid,valueX=None,valueY=None,numberOfMovement=1):
        """
        Model action to move an Agent.

        args:
            aGrid (instance): the grid where the action take place
            valueX / value Y (int): coordinates of the cell
            numberOfMouvement (int): number of movement in one action
        """
        for i in range(numberOfMovement):
            if i>0:
                oldAgent=theAgent
            else:
                oldAgent=self
            if valueX == None and valueY==None:
                # à partir du round 2 / 3, oldAgent.cell = None (lié à updateDepartureAgent() malgré l'update de OldAgentà chaque itération)
                neighbors=oldAgent.cell.getNeighborCells(oldAgent.cell.grid.rule)
                newCell=random.choice(neighbors)

            else:
                newCell=aGrid.getCellFromCoordinates(valueX,valueY)

            theAgent = self.updateMoveAgent(oldAgent,oldAgent.cell,newCell)
        pass

    def updateMoveAgent(self,anAgent,departureCell,incomingCell):
            departureCell.updateDepartureAgent(anAgent)
            anAgent.deleteLater()
            aGrid=incomingCell.grid
            for instance in SGAgent.instances:
                if instance.me=='collec' and instance.name==anAgent.name:
                    AgentSpecie=instance
            theAgent=aGrid.model.newAgent(aGrid,AgentSpecie,incomingCell.x,incomingCell.y,anAgent.id,aGrid.model.agentSpecies[str(AgentSpecie.name)]['AgentList'][str(anAgent.id)]['attributs']) 
            incomingCell.updateIncomingAgent(theAgent)
            theAgent.show()
            return theAgent
                
    #Function to check the ownership  of the agent          
    def isMine(self):
        return self.owner==self.model.actualPlayer
    
    def getId(self):
        return self.id
    
    #Function to check the ownership  of the agent          
    def isMineOrAdmin(self):
        """NOT TESTED"""
        return self.owner==self.model.actualPlayer or self.owner=="admin"
    
    #Function to change the ownership         
    def makeOwner(self,newOwner):
        self.owner=newOwner
        
    #Function get the ownership        
    def getProperty(self):
        self.owner=self.model.actualPlayer
    
        
    #Function to check the old value of an Agent       
    def checkPrecedenteValue(self,precedentValue):
        """NOT TESTED"""
        if not len(self.history["value"]) ==0:
            for aVal in list(self.history["value"][len(self.history["value"])].thingsSave.keys()) :
                if aVal in list(self.theCollection.povs[self.model.nameOfPov].keys()) :
                    return self.history["value"][len(self.history["value"])].thingsSave[aVal]
        else: 
            for aVal in list(self.attributs.keys()) :
                if aVal in list(self.theCollection.povs[self.model.nameOfPov].keys()) :
                    return self.attributs[aVal]