from tkinter.ttk import Separator
from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from SGAgent import SGAgent
import re


   
#Class who is responsible of the declaration a cell
class SGCell(QtWidgets.QWidget):
    def __init__(self,parent,theCollection,x,y,format,size,gap,startXBase,startYBase):
        super().__init__(parent)
        #Basic initialize
        self.grid=parent
        self.theCollection=theCollection
        self.x=x
        self.y=y
        self.shape=format
        self.size=size
        self.gap=gap
        #Save the basic value for the zoom ( temporary)
        self.saveGap=gap
        self.saveSize=size
        #We place the default pos
        self.startXBase=startXBase
        self.startYBase=startYBase
        self.startX=int(self.startXBase+self.gap*(self.x)+self.size*(self.x)+self.gap) 
        self.startY=int(self.startYBase+self.gap*(self.y)+self.size*(self.y)+self.gap)
        self.isDisplay=True
        #We init the dict of Attribute
        self.attributs={}
        #We init the Collection for the futures Agents
        self.agents=[]
        #We allow the drops for the agents
        self.setAcceptDrops(True)
        #We define an owner
        self.owner="admin"
        #We define variables to handle the history 
        self.history={}
        self.history["value"]=[]
        self.borderColor=Qt.black
        self.color=Qt.white
  
    # to extract the format of the cell
    def getShape(self):
        return self.shape
        
    def paintEvent(self,event):
        self.startX=int(self.startXBase+self.gap*(self.x)+self.size*(self.x)+self.gap) 
        self.startY=int(self.startYBase+self.gap*(self.y)+self.size*(self.y)+self.gap)
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
            if(self.y%2!=1):
                # y paires /  sachant que la première valeur de y est 0
                self.move(self.startX  ,   int(self.startY-self.size/2*self.y +(self.gap/10+self.size/4)*self.y))
            else:
                self.move((self.startX+int(self.size/2)+int(self.gap/2) ), int(self.startY-self.size/2*self.y +(self.gap/10+self.size/4)*self.y))
                
        painter.end()
        
    def getId(self):
        return "cell"+str(self.x)+"-"+str(self.y)
    

    #Funtion to handle the zoom
    def zoomIn(self):
        """NOT TESTED"""
        oldSize=self.size
        self.size=self.grid.size
        self.gap=self.grid.gap
        self.update()
    
    def zoomOut(self):
        """NOT TESTED"""
        oldSize=self.size
        self.size=self.grid.size
        self.gap=self.grid.gap
        self.update()
        
    def zoomFit(self):
        """NOT TESTED"""
        self.size=self.grid.size
        self.gap=self.grid.gap
        self.update()

    def convert_coordinates(self, global_pos: QPoint) -> QPoint:
    # Convertit les coordonnées globales en coordonnées locales
        local_pos = self.mapFromGlobal(global_pos)
        return local_pos
        
    #Function to handle the drag of widget
    def dragEnterEvent(self, e):
        e.accept()
        
    def dropEvent(self, e):
        oldAgent=0
        AgentSpecie=0
        e.accept()
        thePlayer=self.grid.model.getCurrentPlayer()
        theAction=None
        if thePlayer is not None :
            theAction=thePlayer.getMooveActionOn(e.source())
            if not self.grid.model.whoIAm=="Admin":
                self.feedBack(theAction,e.source())
        oldAgent=e.source()

        for instance in SGAgent.instances:
            if instance.me=='collec' and instance.name==oldAgent.name:
                AgentSpecie=instance
                break

        theAgent=self.grid.model.newAgent(self.grid,AgentSpecie,self.x,self.y,oldAgent.id,self.grid.model.agentSpecies[str(AgentSpecie.name)]['AgentList'][str(oldAgent.id)]['attributs'])
        theAgent.cell=self
        theAgent.show()
        

        e.setDropAction(Qt.MoveAction)
        e.accept()
        e.source().deleteLater()
        
        
    #To manage the attribute system of a cell
    def getColor(self):
        if self.isDisplay==False:
            return Qt.transparent
    
        if self.grid.model.nameOfPov in self.theCollection.povs.keys():
            self.theCollection.povs['selectedPov']=self.theCollection.povs[self.getPov()]
            for aVal in list(self.theCollection.povs[self.grid.model.nameOfPov].keys()):
                if aVal in list(self.theCollection.povs[self.grid.model.nameOfPov].keys()):
                     self.color=self.theCollection.povs[self.getPov()][aVal][self.attributs[aVal]]
                     return self.theCollection.povs[self.getPov()][aVal][self.attributs[aVal]]
        
        else:
            if self.theCollection.povs['selectedPov'] is not None:
                for aVal in list(self.theCollection.povs['selectedPov'].keys()):
                    if aVal in list(self.theCollection.povs['selectedPov'].keys()):
                        self.color=self.theCollection.povs['selectedPov'][aVal][self.attributs[aVal]]
                        return self.theCollection.povs['selectedPov'][aVal][self.attributs[aVal]]
            else: 
                self.color=Qt.white
                return Qt.white
            
    def getBorderColor(self):
        if self.isDisplay==False:
            return Qt.transparent
    
        if self.grid.model.nameOfPov in self.theCollection.borderPovs.keys():
            self.theCollection.borderPovs['selectedBorderPov']=self.theCollection.borderPovs[self.getPov()]
            for aVal in list(self.theCollection.borderPovs[self.grid.model.nameOfPov].keys()):
                if aVal in list(self.theCollection.borderPovs[self.grid.model.nameOfPov].keys()):
                     self.borderColor=self.theCollection.borderPovs[self.getPov()][aVal][self.attributs[aVal]]
                     return self.theCollection.borderPovs[self.getPov()][aVal][self.attributs[aVal]]
        
        else:
            """if self.theCollection.borderPovs['selectedBorderPov'] is not None:
                for aVal in list(self.theCollection.borderPovs['selectedBorderPov'].keys()):
                    if aVal in list(self.theCollection.borderPovs['selectedBorderPov'].keys()):
                        self.borderColor=self.theCollection.borderPovs['selectedBorderPov'][aVal][self.attributs[aVal]]
                        if self.borderColor != None:
                            return self.theCollection.borderPovs['selectedBorderPov'][aVal][self.attributs[aVal]]
                        else:
                            return Qt.black
            else:""" 
            self.borderColor=Qt.black
            return Qt.black
    
    def getBorderWidth(self):
        if self.theCollection.borderPovs is not None and self.grid.model.nameOfPov in self.theCollection.borderPovs.keys():
                return int(self.theCollection.borderPovs["borderWidth"])
        
        return int(1)
                
    #To get the pov
    def getPov(self):
        return self.grid.model.nameOfPov
         
    #To handle the selection of an element int the legend
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print("hey")
            #Something is selected
            if self.grid.model.selected[0]!=None :
                print("ho")
                #We search if the player have the rights
                thePlayer=self.grid.model.getCurrentPlayer()
                print(thePlayer)
                authorisation=False
                theAction = None
                if self.grid.model.selected[0].isFromAdmin():
                    authorisation=True

                elif thePlayer is not None :
                    theAction=thePlayer.getGameActionOn(self)
                    print(theAction)
                    if theAction is not None:
                        authorisation=theAction.getAuthorize(self)
                        print(authorisation)
                        if authorisation : 
                            theAction.use()
         
                #The delete Action
                if self.grid.model.selected[2].split()[0]== "Delete" or self.grid.model.selected[2].split()[0]== "Remove" :
                    if authorisation : 
                        if len(self.history["value"])==0:
                            self.history["value"].append([0,0,self.attributs])
                        #We now check the feedBack of the actions if it have some
                        if theAction is not None:
                            self.feedBack(theAction)
                        if len(self.agents) !=0:
                            for i in reversed(range(len(self.collectionOfAgents.agents))):
                                self.agents[i].deleteLater()
                                del self.agents[i]
                        self.grid.collectionOfCells.removeVisiblityCell(self.getId())
                        self.history["value"].append([self.grid.model.timeManager.currentRound,self.grid.model.timeManager.currentPhase,"deleted"])
                        for watcher in self.grid.collectionOfCells.watchers[self.grid.model.selected[4]]:
                            watcher.dashboard.updateIndicator(watcher)
                        self.show()
                        self.repaint()    

                #The Replace cell and change value Action
                elif self.grid.model.selected[1]== "square" or self.grid.model.selected[1]=="hexagonal":
                    if  authorisation :
                        #We now check the feedBack of the actions if it have some
                        if len(self.history["value"])==0:
                            self.history["value"].append([0,0,self.attributs])
                        if theAction is not None:
                            self.feedBack(theAction)
                        if self.grid.model.selected[0].legend.id!="adminLegend":
                             self.owner=self.grid.model.currentPlayer
                        self.isDisplay=True
                        value =self.grid.model.selected[3]
                        theKey=""
                        for anAttribute in list(self.theCollection.povs[self.grid.model.nameOfPov].keys()):
                            if value in list(self.theCollection.povs[self.grid.model.nameOfPov][anAttribute].keys()) :
                                theKey=anAttribute
                                break
                        aDictWithValue={theKey:value}    
                        for aVal in list(aDictWithValue.keys()) :
                            if aVal in list(self.theCollection.povs[self.grid.model.nameOfPov].keys()) :
                                    for anAttribute in list(self.theCollection.povs[self.grid.model.nameOfPov].keys()):
                                        self.attributs.pop(anAttribute,None)
                        self.attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]  
                        self.history["value"].append([self.grid.model.timeManager.currentRound,self.grid.model.timeManager.currentPhase,self.attributs])
                        for watcher in self.grid.collectionOfCells.watchers[self.grid.model.selected[4]]:
                            watcher.dashboard.updateIndicator(watcher)
                        self.update()
                        

                #For agent placement         
                else :
                    if  authorisation :
                        aDictWithValue={self.grid.model.selected[4]:self.grid.model.selected[3]}
                        if self.grid.model.selected[4] =="empty" or self.grid.model.selected[3]=='empty':
                            Species=self.grid.model.selected[2]
                        else:
                            Species=re.search(r'\b(\w+)\s*:', self.grid.model.selected[5]).group(1)
                        if self.isDisplay==True :
                            #We now check the feedBack of the actions if it have some
                            #if theAction is not None:
                            #    self.feedBack(theAction)
                            theSpecies=SGAgent(self.grid.model,name=Species,format=self.grid.model.agentSpecies[Species]['Shape'],defaultsize=self.grid.model.agentSpecies[Species]['DefaultSize'],dictOfAttributs=self.grid.model.agentSpecies[Species]['AttributList'],id=None,me='collec')
                            self.grid.model.placeAgent(self,theSpecies,aDictWithValue)
                            self.update()
                            self.grid.model.update()

        if event.button() == Qt.RightButton:
            print(self.attributs)
                            
                                    
    #Apply the feedBack of a gameMechanics
    """def feedBack(self, theAction,theAgentForMoveGM=None):
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
                    aFeedback(theAgentForMoveGM)"""
            
                            
    #To handle the drag of the grid
    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.LeftButton:
            return
                        
            
    #To handle the arrival of an agent on the cell (this is a private method)
    def updateIncomingAgent(self,anAgent):
        anAgent.cell=self
        self.agents.append(anAgent)
    
    #To handle the departure of an agent of the cell (this is a private method)
    def updateDepartureAgent(self,anAgent):
        anAgent.cell=None
        self.agents.remove(anAgent)


#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    #To verify if the cell contain the value pas in parametre through a dictionnary
    def checkValue(self,aDictOfValue):
        """NOT TESTED"""
        theKey=list(aDictOfValue.keys())[0] 
        if theKey in list(self.attributs.keys()):
            return aDictOfValue[theKey]==self.attributs[theKey]
        return False
    
    #To change the value
    def changeValue(self,aDictOfValue):
        """NOT TESTED"""
        if len(self.history["value"])==0:
            self.history["value"].append([0,0,self.attributs])
        self.grid.setForXandY(aDictOfValue,self.x+1,self.y+1)
        self.history["value"].append([self.grid.model.timeManager.currentRound,self.grid.model.timeManager.currentPhase,self.attributs])
     
    
    #To get all of a kind of agent on a cell 
    def getAgents(self):
        """NOT TESTED"""
        listOfAgents=[]
        for agent in self.agents:
           listOfAgents.append(agent)
        return  listOfAgents
 
    #To get all agents on the grid of a particular type
    def getAgentsOfSpecie(self,nameOfSpecie):
        """NOT TESTED"""
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
                    c = self.grid.getCellFromCoordinates(i, j)
                elif rule=='neumann':
                    if (i == self.x or j == self.y) and (i != self.x or j != self.y):
                        c = self.grid.getCellFromCoordinatesl(i,j)
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
    
    #Delete All the Agent       
    def deleteAllAgent(self):
        """NOT TESTED"""
        for i in reversed(range(len(self.collectionOfAgents.agents))):
            self.collectionOfAgents.agents[i].deleteLater()
            del self.collectionOfAgents.agents[i]
        self.update()