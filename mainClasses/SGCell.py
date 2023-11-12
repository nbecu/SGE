from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.gameAction.SGGameActions import SGGameActions
from mainClasses.SGEntity import SGEntity
# import time


   
#Class who is responsible of the declaration a cell
class SGCell(SGEntity):
    def __init__(self,classDef, x, y):
        super().__init__(classDef.grid,classDef,classDef.defaultsize,classDef.defaultShapeColor,attributesAndValues=None)
        #Basic initialize
        self.grid=classDef.grid
        self.x=x
        self.y=y
        self.gap=self.grid.gap
        #Save the basic value for the zoom ( temporary)
        self.saveGap=self.gap
        self.saveSize=classDef.defaultsize
        #We place the default pos
        self.startXBase=self.grid.startXBase
        self.startYBase=self.grid.startYBase
        #We allow the drops for the agents
        self.setAcceptDrops(True)
        self.agents=[]
        self.initUI()

    
    def initUI(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)
        
    def getId(self):
        return "cell"+str(self.x)+"-"+str(self.y)
    
    def paintEvent(self,event):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
        # print(time.localtime())
        if self.isDisplay==True:
            painter.setPen(QPen(self.getBorderColor(),self.getBorderWidth()))
            self.startXBase=0
            self.startYBase=0
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

    #Funtion to handle the zoom
    def zoomIn(self):
        oldSize=self.size
        self.size=self.grid.size
        self.gap=self.grid.gap
        self.update()
    
    def zoomOut(self):
        oldSize=self.size
        self.size=self.grid.size
        self.gap=self.grid.gap
        self.update()
        
    def zoomFit(self):
        self.size=self.grid.size
        self.gap=self.grid.gap
        self.update()

    def convert_coordinates(self, global_pos: QPoint) -> QPoint:
    # Convertit les coordonnées globales en coordonnées locales
        local_pos = self.mapFromGlobal(global_pos)
        return local_pos
        
    #Function to handle the drag of widget
    def dragEnterEvent(self, e):
        # I'm not sure to what this corresponds
        e.accept()
        
    def dropEvent(self, e):
        e.accept()
        oldAgent=e.source()
        self.moveAgentByRecreating_it(oldAgent)
        e.setDropAction(Qt.MoveAction)
        if self.model.mqttMajType == "Instantaneous":
            SGGameActions.sendMqttMessage(self)
                            
    #To handle the drag of the grid
    # def mouseMoveEvent(self, e): #CA N'A PAS DE RAISON D'ETRE
    #     if e.buttons() != Qt.LeftButton:
    #         return


    def moveAgentByRecreating_it(self,oldAgent):
        theAgent=self.grid.model.copyOfAgentAtCoord(self,oldAgent)
        self.updateIncomingAgent(theAgent)
        theAgent.show()
        oldAgent.deleteLater()

             
    #To get the pov
    def getPov(self):
        return self.grid.model.nameOfPov
       
             
    #To handle the selection of an element int the legend
    def mousePressEvent(self, event):
        return super().mousePressEvent(event)

                            
                                    
    #Apply the feedBack of a gameMechanics
    def feedBack(self, theAction,theAgentForMoveGM=None):
        booleanForFeedback=True
        booleanForFeedbackAgent=True
        for anCondition in theAction.conditionOfFeedBack :
            booleanForFeedback=booleanForFeedback and anCondition(self)
        if booleanForFeedback :
            for aFeedback in  theAction.feedback :
                aFeedback(self)
        if theAgentForMoveGM is not None :
            for anCondition in theAction.conditionOfFeedBackAgent :
                booleanForFeedbackAgent=booleanForFeedbackAgent and anCondition(self,theAgentForMoveGM)
            if booleanForFeedbackAgent :
                for aFeedback in  theAction.feedbackAgent :
                    aFeedback(theAgentForMoveGM)
            
                      
            
    #To handle the arrival of an agent on the cell (this is a private method)
    def updateIncomingAgent(self,anAgent):
        # anAgent.cell=self #Should be removed. Its the responsability of the agent
        self.agents.append(anAgent)
    
    #To handle the departure of an agent of the cell (this is a private method)
    def updateDepartureAgent(self,anAgent):
        self.agents.remove(anAgent)
        anAgent.cell=None

    def isDeleted(self):
        return not self.isDisplay
    
    # To show a menu
    def show_menu(self, point):
        menu = QMenu(self)
        text= "Agent count on this cell : "+str(len(self.agents))
        option1 = QAction(text, self)
        menu.addAction(option1)

        # for aAgent in self.model.getAgents():
        #     aAgent.cell.moveAgentByRecreating_it(aAgent)
        self.model.updateAgentsAtMAJ()  
        
        if self.rect().contains(point):
            menu.exec_(self.mapToGlobal(point))

#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use


    
    #To verify if the cell contain the value pas in parametre through a dictionnary
    def checkValue(self,aDictOfValue):
        """NOT TESTED"""
        theKey=list(aDictOfValue.keys())[0] 
        if theKey in list(self.dictAttributes.keys()):
            return aDictOfValue[theKey]==self.dictAttributes[theKey]
        return False

    
    #To change the value
    def changeValue(self,aDictOfValue):
        """NOT TESTED"""
        if len(self.history["value"])==0:
            self.history["value"].append([0,0,self.attributs])
        self.grid.setForXandY(aDictOfValue,self.x+1,self.y+1)
        self.history["value"].append([self.grid.model.timeManager.currentRound,self.grid.model.timeManager.currentPhase,self.attributs])
     
    
    #To get all of a kind of agent on a cell 
    def getAgents(self,specie=None):
        if specie != None:
            return self.getAgentsOfSpecie(specie)
        listOfAgents=[]
        for agent in self.agents:
           listOfAgents.append(agent)
        return  listOfAgents
    
    def nbAgents(self,specie=None):
        if specie != None:
            listAgts = self.getAgentsOfSpecie(specie)
        else: listAgts = self.getAgents()
        return  len(listAgts)
 
    #To get all agents on the grid of a particular type
    def getAgentsOfSpecie(self,nameOfSpecie):
        listOfAgents=[]
        for agent in self.agents:
            if agent.name ==nameOfSpecie:
                listOfAgents.append(agent)
        return  listOfAgents
    
    #To get the neighbor cells
    def getNeighborCells(self,rule='moore'):
        neighbors = []
        for i in range(self.x - 1, self.x + 2):
            for j in range(self.y - 1, self.y + 2):
                if i == self.x and j == self.y:
                    continue
                if rule=="moore":
                    c = self.grid.getCell(i, j)
                elif rule=='neumann':
                    if (i == self.x or j == self.y) and (i != self.x or j != self.y):
                        c = self.grid.getCell(i,j)
                    else:
                        c = None
                else:
                    print('Error in rule specification')
                    break
                if c is not None:
                    neighbors.append(c)
        return neighbors
        
        
        
    #Function to check the ownership  of the cell          
    def isMine(self):
        """NOT TESTED"""
        return self.owner==self.grid.model.currentPlayer
    
    #Function to check the ownership  of the cell          
    def isMineOrAdmin(self):
        """NOT TESTED"""
        return self.owner==self.grid.model.currentPlayer or self.owner=="admin"
    
    #Function to change the ownership         
    def makeOwner(self,newOwner):
        """NOT TESTED"""
        self.owner=newOwner
        
    #Function get the ownership        
    def getProperty(self):
        """NOT TESTED"""
        self.owner=self.grid.model.currentPlayer
        
        
    #Function get if the cell have change the value in       
    def haveChangeValue(self,numberOfRound=1):
        """NOT TESTED"""
        haveChange=False
        if not len(self.history["value"]) ==0:
            for anItem in self.history["value"].reverse():
                if anItem.roundNumber> self.grid.model.timeManager.currentRound-numberOfRound:
                    if not anItem.thingsSave == self.attributs:
                        haveChange=True
                        break
                elif anItem.roundNumber== self.grid.model.timeManager.currentRound-numberOfRound:
                    if anItem.phaseNumber<=self.grid.model.timeManager.currentPhase:
                        if not anItem.thingsSave == self.attributs:
                            haveChange=True
                            break
        return haveChange
    
    #Delete all agents on the cell
    def deleteAllAgents(self):
        for agt in self.agents[:]:
            agt.classDef.deleteEntity(agt)
        self.update()

    #Create agents on the cell
    def newAgentHere(self, aAgentSpecies,adictAttributes=None):
        """
        Create a new Agent in the associated species.

        Args:
            aAgentSpecies (instance) : the species of your agent
            adictAttributes to set the values

        Return:
            a new agent"""
        return aAgentSpecies.newAgentAtCoords(self.grid, self.x, self.y,adictAttributes)

    #To perform action
    def doAction(self, aLambdaFunction):
        aLambdaFunction(self)

    