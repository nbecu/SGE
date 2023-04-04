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
        #We allow the drops for the agents
        self.setAcceptDrops(True)
        #We define an owner
        self.owner="admin"
        #We define variables to handle the history 
        self.history={}
        self.history["value"]=[]
  
    # to extract the format of the cell
    def getShape(self):
        return self.shape
        
    def paintEvent(self,event):
        self.startX=int(self.startXBase+self.gap*(self.x)+self.size*(self.x)+self.gap) 
        self.startY=int(self.startYBase+self.gap*(self.y)+self.size*(self.y)+self.gap)
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
        if self.isDisplay==False:
            painter.setPen(QPen(Qt.transparent,1));
        else :
            painter.setPen(QPen(Qt.black,1));
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
        oldSize=self.size
        self.size=self.grid.size
        self.gap=self.grid.gap
        """for anAgent in self.collectionOfAgents.agents:
            coeffX=anAgent.x/oldSize
            anAgent.x=int(self.size*coeffX)
            coeffY=anAgent.y/oldSize
            anAgent.y=int(self.size*coeffY)"""
        self.update()
    
    def zoomOut(self):
        oldSize=self.size
        self.size=self.grid.size
        self.gap=self.grid.gap
        """for anAgent in self.collectionOfAgents.agents:
            coeffX=anAgent.x/oldSize
            anAgent.x=int(self.size*coeffX)
            coeffY=anAgent.y/oldSize
            anAgent.y=int(self.size*coeffY)"""
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
        '''for attribute, value in vars(oldAgent).items():
            print(f"{attribute}: {value}")'''

        for instance in SGAgent.instances:
            if instance.me=='collec' and instance.name==oldAgent.name:
                AgentSpecie=instance
                break

        #print(self.grid.model.AgentSpecies[str(AgentSpecie.name)]['AgentList'][str(oldAgent.id)]['attributs'])
        theAgent=self.grid.model.newAgent(self.grid,AgentSpecie,self.x+1,self.y+1,oldAgent.id,self.grid.model.AgentSpecies[str(AgentSpecie.name)]['AgentList'][str(oldAgent.id)]['attributs'])
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
                     return self.theCollection.povs[self.getPov()][aVal][self.attributs[aVal]]
        
        else:
            if self.theCollection.povs['selectedPov'] is not None:
                for aVal in list(self.theCollection.povs['selectedPov'].keys()):
                    if aVal in list(self.theCollection.povs['selectedPov'].keys()):
                        return self.theCollection.povs['selectedPov'][aVal][self.attributs[aVal]]
            else: 
                return Qt.white
                
    #To get the pov
    def getPov(self):
        return self.grid.model.nameOfPov
         
    #To handle the selection of an element int the legend
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            #Something is selected
            if self.grid.model.selected[0]!=None :
                #We shearch if the player have the rights
                thePlayer=self.grid.model.getCurrentPlayer()
                authorisation=False
                theAction = None
                if self.grid.model.selected[0].isFromAdmin():
                    authorisation=True

                elif thePlayer is not None :
                    theAction=thePlayer.getGameActionOn(self)
                    if theAction is not None:
                        authorisation=theAction.getAuthorize(self)
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
                        if len(self.collectionOfAgents.agents) !=0:
                            for i in reversed(range(len(self.collectionOfAgents.agents))):
                                self.collectionOfAgents.agents[i].deleteLater()
                                del self.collectionOfAgents.agents[i]
                        self.grid.collectionOfCells.removeVisiblityCell(self.getId())
                        self.history["value"].append([self.grid.model.timeManager.currentRound,self.grid.model.timeManager.currentPhase,"deleted"])
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
                             self.owner=self.grid.model.actualPlayer
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
                        self.update()

                #For agent placement         
                else :
                    if  authorisation :
                        aDictWithValue={self.grid.model.selected[4]:self.grid.model.selected[3]}
                        Species=re.search(r'\b(\w+)\s*:', self.grid.model.selected[5]).group(1)
                        if self.isDisplay==True :
                            #We now check the feedBack of the actions if it have some
                            if theAction is not None:
                                self.feedBack(theAction)
                            theSpecies=SGAgent(self.grid.model,name=Species,format=self.grid.model.AgentSpecies[Species]['Shape'],defaultsize=self.grid.model.AgentSpecies[Species]['DefaultSize'],dictOfAttributs=self.grid.model.AgentSpecies[Species]['AttributList'],id=None)
                            self.grid.model.addAgent(self.grid,theSpecies,aDictWithValue,method=None,cell=self)
                            #if self.grid.model.selected[0].legend.id!="adminLegend":
                            #    anAgent.owner=self.grid.model.actualPlayer
                            #anAgent.history["value"].append([self.grid.model.timeManager.currentRound,self.grid.model.timeManager.currentPhase,anAgent.attributs])
                            #anAgent.history["coordinates"].append([self.grid.model.timeManager.currentRound,self.grid.model.timeManager.currentPhase,self.grid.id+"-"+str(self.x)+"-"+str(self.y)])
                            self.update()
                            self.grid.model.update()

                            
                                    
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
            
                            
    #To handle the drag of the grid
    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.LeftButton:
            return
                        
    
    
        #Agent function 
    #To get all agents on the grid of a particular type
    def getAgentsOfType(self,aNameOfAgent):
        theList=[]
        for anAgentName in range(len(self.collectionOfAgents.agents)) :
            if self.collectionOfAgents.agents[anAgentName].name==aNameOfAgent:
                theList.append(self.collectionOfAgents.agents[anAgentName])
        return theList
            
    
    
        
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    def setUpCellValue(self,aDictOfValue):
        for anAttribut in aDictOfValue:
            if anAttribut in list(self.theCollection.povs[self.grid.model.nameOfPov].keys()):
                for aVal in list(self.theCollection.povs[self.grid.model.nameOfPov].keys()):
                    self.attributs[aVal]=[]
                for aVal in list(self.theCollection.povs[self.grid.model.nameOfPov].keys()):
                    del self.attributs[aVal]
                self.attributs[anAttribut]=aDictOfValue[anAttribut]

    #To verify if the cell contain the value pas in parametre through a dictionnary
    def checkValue(self,aDictOfValue):
        theKey=list(aDictOfValue.keys())[0] 
        if theKey in list(self.attributs.keys()):
            return aDictOfValue[theKey]==self.attributs[theKey]
        return False
    
    #To change the value
    def changeValue(self,aDictOfValue):
        if len(self.history["value"])==0:
            self.history["value"].append([0,0,self.attributs])
        self.grid.setForXandY(aDictOfValue,self.x+1,self.y+1)
        self.history["value"].append([self.grid.model.timeManager.currentRound,self.grid.model.timeManager.currentPhase,self.attributs])
     
    #To delete a kind of Agent on the cell   
    '''def deleteAgent(self,nameOfAgent,numberOfDelete=0,condition=[]):
        if len(self.collectionOfAgents.agents) !=0:
            nbrDelete=0
            count=0
            aListOfAgent = self.getAgent(nameOfAgent)
            if numberOfDelete ==0:
                numberOfDelete=len(aListOfAgent)
            while len(aListOfAgent) !=0 and numberOfDelete>nbrDelete and count!=len(aListOfAgent) :
                count=count+1
                aListOfAgent = self.getAgent(nameOfAgent)
                for agent in aListOfAgent:
                    if agent.name==nameOfAgent:
                        test=True
                        for cond in condition:
                            test = cond(self) and test
                        if test:
                            nbrDelete=nbrDelete+1
                            agent.deleteLater()
                            self.collectionOfAgents.agents.remove(agent)
                            del agent
                            break
            return nbrDelete
        self.show()'''
    
        
    #To get all of a kind of agent on a cell 
    def getAgent(self,nameOfAgent,numberOfDelete=0,condition=[]):
        listOfAgent=[]
        for agent in self.collectionOfAgents.agents:
            if agent.name ==nameOfAgent:
                listOfAgent.append(agent)
        return  listOfAgent
    
    
    #To get the neighbor cells
    """def getNeighborCells(self,type="moore",rangeNeighbor=1,neighborCells=[]): 
        isFirst=False
        if len(neighborCells)==0:
            isFirst=True

        neighborCells.append(self)
        listOfCell=[]
        if rangeNeighbor !=0:
            if self.shape=="hexagonal":
                if self.y%2==0 :
                    #Top Left
                    if self.x-1>=0 and self.y-1>=0:
                        cell=self.grid.getCell("cell"+str(self.x-1)+"-"+str(self.y-1))
                        if cell not in neighborCells:
                            listOfCell.append(cell)
                    #Bottom Left
                    if self.x-1>=0 and self.y+1<=self.grid.rows:
                        cell=self.grid.getCell("cell"+str(self.x-1)+"-"+str(self.y+1))
                        if cell not in neighborCells:
                            listOfCell.append(cell)
                    #Top
                    if  self.y-1>=0:
                        cell=self.grid.getCell("cell"+str(self.x)+"-"+str(self.y-1))
                        if cell not in neighborCells:
                            listOfCell.append(cell)
                    #Left
                    if  self.x-1>=0:
                        cell=self.grid.getCell("cell"+str(self.x-1)+"-"+str(self.y))
                        if cell not in neighborCells:
                            listOfCell.append(cell)
                    #Right
                    if  self.x+1<=self.grid.columns:
                        cell=self.grid.getCell("cell"+str(self.x+1)+"-"+str(self.y))
                        if cell not in neighborCells:
                            listOfCell.append(cell)
                    #Bottom
                    if  self.y+1<=self.grid.rows:
                        cell=self.grid.getCell("cell"+str(self.x)+"-"+str(self.y+1))
                        if cell not in neighborCells:
                            listOfCell.append(cell)
                else:
                    #Top Right
                    if self.x+1<=self.grid.columns and self.y-1>=0:
                        cell=self.grid.getCell("cell"+str(self.x+1)+"-"+str(self.y-1))
                        if cell not in neighborCells:
                            listOfCell.append(cell)
                    #Bottom Right
                    if self.x+1<=self.grid.columns and self.y+1<=self.grid.rows:
                        cell=self.grid.getCell("cell"+str(self.x+1)+"-"+str(self.y+1))
                        if cell not in neighborCells:
                            listOfCell.append(cell) 
                    #Top
                    if  self.y-1>=0:
                        cell=self.grid.getCell("cell"+str(self.x)+"-"+str(self.y-1))
                        if cell not in neighborCells:
                            listOfCell.append(cell)
                    #Left
                    if  self.x-1>=0:
                        cell=self.grid.getCell("cell"+str(self.x-1)+"-"+str(self.y))
                        if cell not in neighborCells:
                            listOfCell.append(cell)
                    #Right
                    if  self.x+1<=self.grid.columns:
                        cell=self.grid.getCell("cell"+str(self.x+1)+"-"+str(self.y))
                        if cell not in neighborCells:
                            listOfCell.append(cell)
                    #Bottom
                    if  self.y+1<=self.grid.rows:
                        cell=self.grid.getCell("cell"+str(self.x)+"-"+str(self.y+1))
                        if cell not in neighborCells:
                            listOfCell.append(cell)
                for cell in listOfCell:
                    cell.getNeighborCells(type,rangeNeighbor-1,neighborCells)
                    
            else:
                if type=="moore":
                    #Top Left
                    if self.x-1>=0 and self.y-1>=0:
                        cellName="cell"+str(self.x-1)+"-"+str(self.y-1)
                        cell=self.grid.getCell(cellName)
                        if cell not in neighborCells:
                            cell.getNeighborCells(type,rangeNeighbor-1,neighborCells)
                    #Top Right
                    if self.x+1<=self.grid.columns and self.y-1>=0:
                        cell=self.grid.getCell("cell"+str(self.x+1)+"-"+str(self.y-1))
                        if cell not in neighborCells:
                            cell.getNeighborCells(type,rangeNeighbor-1,neighborCells)
                    #Bottom Left
                    if self.x-1>=0 and self.y+1<=self.grid.rows:
                        cell=self.grid.getCell("cell"+str(self.x-1)+"-"+str(self.y+1))
                        if cell not in neighborCells:
                            cell.getNeighborCells(type,rangeNeighbor-1,neighborCells)
                    #Bottom Right
                    if self.x+1<=self.grid.columns and self.y+1<=self.grid.rows:
                        cell=self.grid.getCell("cell"+str(self.x+1)+"-"+str(self.y+1))
                        if cell not in neighborCells:
                            cell.getNeighborCells(type,rangeNeighbor-1,neighborCells) 
                    #Top
                    if  self.y-1>=0:
                        cell=self.grid.getCell("cell"+str(self.x)+"-"+str(self.y-1))
                        if cell not in neighborCells:
                            cell.getNeighborCells(type,rangeNeighbor-1,neighborCells)
                    #Left
                    if  self.x-1>=0:
                        cell=self.grid.getCell("cell"+str(self.x-1)+"-"+str(self.y))
                        if cell not in neighborCells:
                            cell.getNeighborCells(type,rangeNeighbor-1,neighborCells) 
                    #Right
                    if  self.x+1<=self.grid.columns:
                        cell=self.grid.getCell("cell"+str(self.x+1)+"-"+str(self.y))
                        if cell not in neighborCells:
                            cell.getNeighborCells(type,rangeNeighbor-1,neighborCells)
                    #Bottom
                    if  self.y+1<=self.grid.rows-1:
                        cell=self.grid.getCell("cell"+str(self.x)+"-"+str(self.y+1))
                        if cell not in neighborCells:
                            cell.getNeighborCells(type,rangeNeighbor-1,neighborCells)
                elif type=="neumann":
                    self.getNeumannNeighbor(rangeNeighbor,neighborCells,origin="init")
            
        if isFirst :
            neighborCells.remove(self)
        return neighborCells

                    
    def getNeumannNeighbor(self,rangeNeighbor,emptyList=[],origin="init"):
        emptyList.append(self)
        if rangeNeighbor >0:
            if origin=="init":
                emptyList.remove(self)
                #Top
                if  self.y-1>=0:
                    cell=self.grid.getCell("cell"+str(self.x)+"-"+str(self.y-1))
                    if cell not in emptyList:
                        cell.getNeumannNeighbor(rangeNeighbor-1,emptyList,"top")
                #Left
                if  self.x-1>=0:
                    cell=self.grid.getCell("cell"+str(self.x-1)+"-"+str(self.y))
                    if cell not in emptyList:
                        cell.getNeumannNeighbor(rangeNeighbor-1,emptyList,"left") 
                #Right
                if  self.x+1<=self.grid.columns-1:
                    cell=self.grid.getCell("cell"+str(self.x+1)+"-"+str(self.y))
                    if cell not in emptyList:
                        cell.getNeumannNeighbor(rangeNeighbor-1,emptyList,'right')
                #Bottom
                if  self.y+1<=self.grid.rows-1:
                    cell=self.grid.getCell("cell"+str(self.x)+"-"+str(self.y+1))
                    if cell not in emptyList:
                        cell.getNeumannNeighbor(rangeNeighbor-1,emptyList,'bottom') 
            elif origin == "top":
                #Top
                if  self.y-1>=0:
                    cell=self.grid.getCell("cell"+str(self.x)+"-"+str(self.y-1))
                    if cell not in emptyList:
                        cell.getNeumannNeighbor(rangeNeighbor-1,emptyList,"top")
            elif origin=="bottom":
                #Bottom
                if  self.y+1<=self.grid.rows-1:
                    cell=self.grid.getCell("cell"+str(self.x)+"-"+str(self.y+1))
                    if cell not in emptyList:
                        cell.getNeumannNeighbor(rangeNeighbor-1,emptyList,'bottom') 
            elif origin =="right":
                #Right
                if  self.x+1<=self.grid.columns-1:
                    cell=self.grid.getCell("cell"+str(self.x+1)+"-"+str(self.y))
                    if cell not in emptyList:
                        cell.getNeumannNeighbor(rangeNeighbor-1,emptyList,'right')
            elif origin =='left':
                if  self.x-1>=0:
                    cell=self.grid.getCell("cell"+str(self.x-1)+"-"+str(self.y))
                    if cell not in emptyList:
                        cell.getNeumannNeighbor(rangeNeighbor-1,emptyList,"left") """
    
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
        return self.owner==self.grid.model.actualPlayer
    
    #Function to check the ownership  of the cell          
    def isMineOrAdmin(self):
        return self.owner==self.grid.model.actualPlayer or self.owner=="admin"
    
    #Function to change the ownership         
    def makeOwner(self,newOwner):
        self.owner=newOwner
        
    #Function get the ownership        
    def getProperty(self):
        self.owner=self.grid.model.actualPlayer
        
        
    #Function get if the cell have change the value in       
    def haveChangeValue(self,numberOfRound=1):
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
        for i in reversed(range(len(self.collectionOfAgents.agents))):
            self.collectionOfAgents.agents[i].deleteLater()
            del self.collectionOfAgents.agents[i]
        self.update()