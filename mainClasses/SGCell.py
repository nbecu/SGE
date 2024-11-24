from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGEntity import SGEntity
   
#Class who is responsible of the declaration a cell
class SGCell(SGEntity):
    def __init__(self,classDef, x, y):
        super().__init__(classDef.grid,classDef,classDef.defaultsize,attributesAndValues=None)
        #Basic initialize
        self.grid=classDef.grid
        self.xPos=x
        self.yPos=y
        self.gap=self.grid.gap
        #Save the basic value for the zoom (temporary)
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
        return "cell"+str(self.xPos)+"-"+str(self.yPos)
    
    def paintEvent(self,event):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
        if self.isDisplay==True:
            penColorAndWidth = self.getBorderColorAndWidth()
            painter.setPen(QPen(penColorAndWidth['color'],penColorAndWidth['width']))
            self.startXBase=self.grid.frameMargin
            self.startYBase=self.grid.frameMargin
            self.startX=int(self.startXBase+(self.xPos -1)*(self.size+self.gap)+self.gap) 
            self.startY=int(self.startYBase+(self.yPos -1)*(self.size+self.gap)+self.gap)
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
                if(self.yPos%2!=0):
                    self.move(self.startX , int(self.startY-self.size/2*self.yPos +(self.gap/10+self.size/4)*self.yPos))
                else:
                    self.move((self.startX+int(self.size/2)+int(self.gap/2) ), int(self.startY-self.size/2*self.yPos +(self.gap/10+self.size/4)*self.yPos))
                        
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
    # Convert global coordinates to local coordinates
        local_pos = self.mapFromGlobal(global_pos)
        return local_pos

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            #Something is selected
            aLegendItem = self.model.getSelectedLegendItem()
            if aLegendItem is None : return #Exit the method

            if aLegendItem.legend.isAdminLegend():
                authorisation= True
            else :
                aLegendItem.gameAction.perform_with(self) #aLegendItem (aParameterHolder) is not send has arg anymore has it is not used and it complicates the updateServer
                return

            if not authorisation : return #Exit the method
        
            #The delete Action
            if aLegendItem.type == 'delete' :
                if authorisation : 
                    #We now check the feedBack of the actions if it have some
                    """if theAction is not None:
                        self.feedBack(theAction)"""
                    if not self.isDeleted() :self.classDef.deleteEntity(self)

            #The Replace cell and change value Action
            elif aLegendItem.isSymbolOnCell():
                if  authorisation :
                    #We now check the feedBack of the actions if it have some
                    if self.isDeleted() : self.classDef.reviveThisCell(self) 
                    self.setValue(aLegendItem.nameOfAttribut,aLegendItem.valueOfAttribut)     

            #For agent creation on cell         
            elif aLegendItem.isSymbolOnAgent() and self.isDisplay:
                if  authorisation :
                    aLegendItem.classDef
                    aDictWithValue ={aLegendItem.nameOfAttribut:aLegendItem.valueOfAttribut}
                    self.newAgentHere(aLegendItem.classDef,aDictWithValue)
        
    def dropEvent(self, e):
        e.accept()
        aAgent=e.source()
        
        aActiveLegend = self.model.getSelectedLegend() 
        aLegendItem = self.model.getSelectedLegendItem()
        if aActiveLegend.isAdminLegend(): 
            aAgent.moveTo(self)
        elif aLegendItem is None : None #Exit the method
        else :
            aLegendItem.gameAction.perform_with(aAgent,self)   #aLegendItem (aParameterHolder) is not send has arg anymore has it is not used and it complicates the updateServer
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
        pass

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
 
    def isEmpty(self,specie=None):
        return self.hasAgents(specie)
    
    def hasAgents(self,specie=None):
        return self.nbAgents(specie) == 0

    #To get all agents on the grid of a particular type
    def getAgentsOfSpecie(self,nameOfSpecie):
        return [aAgt for aAgt in self.agents if aAgt.classDef.entityName == nameOfSpecie]
    
    #To get the neighbor cells
    def getNeighborCells(self,rule='moore'):
        neighbors = []
        for i in range(self.xPos - 1, self.xPos + 2):
            for j in range(self.yPos - 1, self.yPos + 2):
                if i == self.xPos and j == self.yPos:
                    continue
                if rule=="moore":
                    c = self.classDef.getCell(i, j)
                elif rule=='neumann':
                    if (i == self.xPos or j == self.yPos) and (i != self.xPos or j != self.yPos):
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
        return self.classDef.getCell(self.xPos,self.yPos-1)
    def getNeighborS(self):
        return self.classDef.getCell(self.xPos,self.yPos+1)
    def getNeighborE(self):
        return self.classDef.getCell(self.xPos+1,self.yPos)
    def getNeighborW(self):
        return self.classDef.getCell(self.xPos-1,self.yPosPos)        
            
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