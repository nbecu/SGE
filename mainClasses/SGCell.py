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
            penColorAndWidth = self.getBorderColorAndWidth()
            painter.setPen(QPen(penColorAndWidth['color'],penColorAndWidth['width']))
            self.startXBase=self.grid.frameMargin
            self.startYBase=self.grid.frameMargin
            self.startX=int(self.startXBase+(self.x -1)*(self.size+self.gap)+self.gap) 
            self.startY=int(self.startYBase+(self.y -1)*(self.size+self.gap)+self.gap)
            if (self.shape=="hexagonal"):
                self.startY=self.startY+self.size/4
            #Base of the gameBoard
            if(self.shape=="square"):
                painter.drawRect(0,0,self.size,self.size)
                self.setMinimumSize(self.size,self.size+1)
                self.move(self.startX,self.startY)
            elif(self.shape=="hexagonal"):
                self.setMinimumSize(self.size,self.size)
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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            #Something is selected
            aLegendItem = self.model.getSelectedLegendItem()
            if aLegendItem is None : return #Exit the method

            # These next 7 lines need a bit of refactoring
            if aLegendItem.legend.isAdminLegend():
                authorisation= True
            else :
                aLegendItem.gameAction.perform_with(self)  #aLegendItem (aParameteHolder) is not send has arg anymore has it is not used and it complicates the updateServer
                return

            if not authorisation : return #Exit the method
        
            #The delete Action
            if aLegendItem.type == 'delete' : #or self.grid.model.selected[2].split()[0]== "Remove" :
                if authorisation : 
                    #We now check the feedBack of the actions if it have some
                    """if theAction is not None:
                        self.feedBack(theAction)"""
                    if not self.isDeleted() :self.classDef.deleteEntity(self)

            #The Replace cell and change value Action
            elif aLegendItem.isSymbolOnCell():
                if  authorisation :
                    #We now check the feedBack of the actions if it have some
                    if not aLegendItem.legend.isAdminLegend():
                        self.owner=self.grid.model.currentPlayer #ce concept de Owner est à enlever
                    if self.isDeleted() : self.classDef.reviveThisCell(self) 
                    self.setValue(aLegendItem.nameOfAttribut,aLegendItem.valueOfAttribut)     

            #For agent creation on cell         
            elif aLegendItem.isSymbolOnAgent() and self.isDisplay:
                if  authorisation :
                    aLegendItem.classDef
                    #We now check the feedBack of the actions if it have some
                    """if theAction is not None:
                        self.feedBack(theAction)"""
                    aDictWithValue ={aLegendItem.nameOfAttribut:aLegendItem.valueOfAttribut}
                    self.newAgentHere(aLegendItem.classDef,aDictWithValue)
        
    def dropEvent(self, e):
        e.accept()
        aAgent=e.source()
        
        aActiveLegend = self.model.getSelectedLegend() 
        aLegendItem = self.model.getSelectedLegendItem()
        if aActiveLegend.isAdminLegend(): # BUG in case there is no adminLegend and not player. Should use a similar test than in mousePressEvent() to correct the bug. Could also use  model.getUsers_withControlPanel()  to test if there is any cibtrolPanel or admiLegend defined
            aAgent.moveTo(self)
        elif aLegendItem is None : None #Exit the method
        else :
            aLegendItem.gameAction.perform_with(aAgent,self)   #aLegendItem (aParameteHolder) is not send has arg anymore has it is not used and it complicates the updateServer
        e.setDropAction(Qt.MoveAction)
                            
    # To handle the drag of the grid
    def mouseMoveEvent(self, e): #this method is used to prevent the drag of a cell
        if e.buttons() != Qt.LeftButton:
            return
                                            
    # Function to handle the drag of widget
    def dragEnterEvent(self, e):
        # this is event is called during an agent drag 
        e.accept()
       
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
        self.agents.append(anAgent)
    
    #To handle the departure of an agent of the cell (this is a private method)
    def updateDepartureAgent(self,anAgent):
        self.agents.remove(anAgent)
        anAgent.cell=None
    
    # To show a menu
    def show_menu(self, point):
        menu = QMenu(self)
        text= "Agent count on this cell : "+str(len(self.agents))
        option1 = QAction(text, self)
        menu.addAction(option1)

        # self.model.updateAgentsAtMAJ()  
        
        if self.rect().contains(point):
            menu.exec_(self.mapToGlobal(point))

#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use  
    
    #To get all of a kind of agent on a cell 
    def getAgents(self,specie=None):
        if specie != None:
            return self.getAgentsOfSpecie(specie)
        return  self.agents[:]
    
    def nbAgents(self,specie=None):
        if specie != None:
            listAgts = self.getAgentsOfSpecie(specie)
        else: listAgts = self.getAgents()
        return  len(listAgts)
 
    #To get all agents on the grid of a particular type
    def getAgentsOfSpecie(self,nameOfSpecie):
        return [aAgt for aAgt in self.agents if aAgt.classDef.entityName == nameOfSpecie]
    
    #To get the neighbor cells
    def getNeighborCells(self,rule='moore'):
        neighbors = []
        for i in range(self.x - 1, self.x + 2):
            for j in range(self.y - 1, self.y + 2):
                if i == self.x and j == self.y:
                    continue
                if rule=="moore":
                    c = self.classDef.getCell(i, j)
                elif rule=='neumann':
                    if (i == self.x or j == self.y) and (i != self.x or j != self.y):
                        c = self.classDef.getCell(i,j)
                    else:
                        c = None
                else:
                    print('Error in rule specification')
                    break
                if c is not None:
                    neighbors.append(c)
        return neighbors
        
    #To get the neighbor cell at cardinal
    def getNeighborN(self):
        return self.classDef.getCell(self.x,self.y-1)
    def getNeighborS(self):
        return self.classDef.getCell(self.x,self.y+1)
    def getNeighborE(self):
        return self.classDef.getCell(self.x+1,self.y)
    def getNeighborW(self):
        return self.classDef.getCell(self.x-1,self.y)

        
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
        return aAgentSpecies.newAgentOnCell(self,adictAttributes)

    #To perform action
    def doAction(self, aLambdaFunction):
        aLambdaFunction(self)

    