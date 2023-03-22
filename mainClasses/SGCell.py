from tkinter.ttk import Separator
from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *



   
#Class who is responsible of the declaration a cell
class SGCell(QtWidgets.QWidget):
    def __init__(self,parent,theCollection,x,y,format,size,gap,startXBase,startYBase):
        super().__init__(parent)
        #Basic initialize
        self.parent=parent
        self.model=parent.model
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
        self.size=self.parent.size
        self.gap=self.parent.gap
        for anAgent in self.collectionOfAgents.agents:
            coeffX=anAgent.x/oldSize
            anAgent.x=int(self.size*coeffX)
            coeffY=anAgent.y/oldSize
            anAgent.y=int(self.size*coeffY)
        self.update()
    
    def zoomOut(self):
        oldSize=self.size
        self.size=self.parent.size
        self.gap=self.parent.gap
        for anAgent in self.collectionOfAgents.agents:
            coeffX=anAgent.x/oldSize
            anAgent.x=int(self.size*coeffX)
            coeffY=anAgent.y/oldSize
            anAgent.y=int(self.size*coeffY)
        self.update()
        
    def zoomFit(self):
        self.size=self.parent.size
        self.gap=self.parent.gap
        self.update()

    def convert_coordinates(self, global_pos: QPoint) -> QPoint:
    # Convertit les coordonnées globales en coordonnées locales
        local_pos = self.mapFromGlobal(global_pos)
        return local_pos
        
    #Function to handle the drag of widget
    def dragEnterEvent(self, e):
        e.accept()
        
    def dropEvent(self, e):
        e.accept()
        if len(e.source().history["coordinates"])==0:
            e.source().history["coordinates"].append([0,0,e.source().parent.parent.id+"-"+str(e.source().parent.x)+"-"+str(e.source().parent.y)])           
        thePlayer=self.parent.parent.getPlayer()
        theAction=None
        if thePlayer is not None :
            theAction=thePlayer.getMooveActionOn(e.source())
            if not self.parent.parent.whoIAm=="Admin":
                self.feedBack(theAction,e.source())
        #We remove the agent of the actual cell
        e.source().deleteLater()
        #We add the agent to the new cell
        theAgent=self.parent.parent.newAgent(self.parent,e.source().species,self.x+1,self.y+1,e.source().id,self.parent.parent.AgentSpecies[str(e.source().species)]['AgentList'][str(e.source().id)]['attributs'])
        '''theAgent=self.parent.addOnXandY(e.source(),self.x+1,self.y+1)
        theAgent.x=e.pos().x()
        theAgent.y=e.pos().y()'''
        
        #theAgent.history['coordinates'].append([self.parent.parent.timeManager.actualRound,self.parent.parent.timeManager.actualPhase,self.parent.id+'-'+str(self.x)+'-'+str(self.y)])
        theAgent.show()
            

        e.setDropAction(Qt.MoveAction)
        e.accept()
        return theAgent
        
    #To manage the attribute system of a cell
    def getColor(self):
        if self.isDisplay==False:
            return Qt.transparent
        
        if self.parent.parent.nameOfPov in self.theCollection.povs.keys():
            self.theCollection.povs['selectedPov']=self.theCollection.povs[self.getPov()]
            for aVal in list(self.theCollection.povs[self.parent.parent.nameOfPov].keys()):
                if aVal in list(self.theCollection.povs[self.parent.parent.nameOfPov].keys()):
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
        return self.parent.parent.nameOfPov
         
    #To handle the selection of an element int the legend
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            #Something is selected
            if self.parent.parent.selected[0]!=None :
                #We shearch if the player have the rights
                thePlayer=self.parent.parent.getPlayer()
                authorisation=False
                theAction = None
                if self.parent.parent.selected[0].isFromAdmin():
                    authorisation=True

                elif thePlayer is not None :
                    theAction=thePlayer.getGameActionOn(self)
                    if theAction is not None:
                        authorisation=theAction.getAuthorize(self)
                        if authorisation : 
                            theAction.use()
         
                #The delete Action
                if self.parent.parent.selected[2].split()[0]== "Delete" or self.parent.parent.selected[2].split()[0]== "Remove" :
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
                        self.parent.collectionOfCells.removeVisiblityCell(self.getId())
                        self.history["value"].append([self.parent.parent.timeManager.actualRound,self.parent.parent.timeManager.actualPhase,"deleted"])
                        self.show()
                        self.repaint()

                #The Replace cell and change value Action
                elif self.parent.parent.selected[1]== "square" or self.parent.parent.selected[1]=="hexagonal":
                    if  authorisation :
                        #We now check the feedBack of the actions if it have some
                        if len(self.history["value"])==0:
                            self.history["value"].append([0,0,self.attributs])
                        if theAction is not None:
                            self.feedBack(theAction)
                        if self.parent.parent.selected[0].parent.id!="adminLegend":
                             self.owner=self.parent.parent.actualPlayer
                        self.isDisplay=True
                        value =self.parent.parent.selected[3]
                        theKey=""
                        for anAttribute in list(self.theCollection.povs[self.parent.parent.nameOfPov].keys()):
                            if value in list(self.theCollection.povs[self.parent.parent.nameOfPov][anAttribute].keys()) :
                                theKey=anAttribute
                                break
                        aDictWithValue={theKey:value}    
                        for aVal in list(aDictWithValue.keys()) :
                            if aVal in list(self.theCollection.povs[self.parent.parent.nameOfPov].keys()) :
                                    for anAttribute in list(self.theCollection.povs[self.parent.parent.nameOfPov].keys()):
                                        self.attributs.pop(anAttribute,None)
                        self.attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]  
                        self.history["value"].append([self.parent.parent.timeManager.actualRound,self.parent.parent.timeManager.actualPhase,self.attributs])
                        self.update()

                #For agent placement         
                else :
                    if  authorisation :
                        aDictWithValue={self.parent.parent.selected[4]:self.parent.parent.selected[3]}
                        if self.parent.parent.selected[5] in list(self.parent.collectionOfAcceptAgent.keys()):
                            anAgentName=str(self.parent.parent.selected[5])
                            if self.isDisplay==True :
                                #We now check the feedBack of the actions if it have some
                                if theAction is not None:
                                    self.feedBack(theAction)
                                anAgent=self.parent.addOnXandY(anAgentName,self.x+1,self.y+1,self.parent.parent.selected[3])
                                anAgent.attributs[list(aDictWithValue.keys())[0]]=list(aDictWithValue.values())[0]
                                anAgent.x=QMouseEvent.pos().x()-round(anAgent.size/2)
                                anAgent.y=QMouseEvent.pos().y()-round(anAgent.size/2)
                                if self.parent.parent.selected[0].parent.id!="adminLegend":
                                    anAgent.owner=self.parent.parent.actualPlayer
                                anAgent.history["value"].append([self.parent.parent.timeManager.actualRound,self.parent.parent.timeManager.actualPhase,anAgent.attributs])
                                anAgent.history["coordinates"].append([self.parent.parent.timeManager.actualRound,self.parent.parent.timeManager.actualPhase,self.parent.id+"-"+str(self.x)+"-"+str(self.y)])
                                anAgent.update()
                                anAgent.show()

                            
                                    
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
            if anAttribut in list(self.theCollection.povs[self.parent.parent.nameOfPov].keys()):
                for aVal in list(self.theCollection.povs[self.parent.parent.nameOfPov].keys()):
                    self.attributs[aVal]=[]
                for aVal in list(self.theCollection.povs[self.parent.parent.nameOfPov].keys()):
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
        self.parent.setForXandY(aDictOfValue,self.x+1,self.y+1)
        self.history["value"].append([self.parent.parent.timeManager.actualRound,self.parent.parent.timeManager.actualPhase,self.attributs])
     
    #To delete a kind of Agent on the cell   
    def deleteAgent(self,nameOfAgent,numberOfDelete=0,condition=[]):
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
        self.show()
    
        
    #To get all of a kind of agent on a cell 
    def getAgent(self,nameOfAgent,numberOfDelete=0,condition=[]):
        listOfAgent=[]
        for agent in self.collectionOfAgents.agents:
            if agent.name ==nameOfAgent:
                listOfAgent.append(agent)
        return  listOfAgent
    
    
    #To get the neighbor cells
    def getNeighborCell(self,type="moore",rangeNeighbor=1,emptyList=[]): 
        isFirst=False
        if len(emptyList)==0:
            isFirst=True
        """emptyList.append("cell"+str(self.x)+"-"+str(self.y))"""

        emptyList.append(self)
        listOfCell=[]
        if rangeNeighbor !=0:
            if self.shape=="hexagonal":
                if self.y%2==0 :
                    #Top Left
                    if self.x-1>=0 and self.y-1>=0:
                        cell=self.parent.getCell("cell"+str(self.x-1)+"-"+str(self.y-1))
                        if cell not in emptyList:
                            listOfCell.append(cell)
                    #Bottom Left
                    if self.x-1>=0 and self.y+1<=self.parent.rows:
                        cell=self.parent.getCell("cell"+str(self.x-1)+"-"+str(self.y+1))
                        if cell not in emptyList:
                            listOfCell.append(cell)
                    #Top
                    if  self.y-1>=0:
                        cell=self.parent.getCell("cell"+str(self.x)+"-"+str(self.y-1))
                        if cell not in emptyList:
                            listOfCell.append(cell)
                    #Left
                    if  self.x-1>=0:
                        cell=self.parent.getCell("cell"+str(self.x-1)+"-"+str(self.y))
                        if cell not in emptyList:
                            listOfCell.append(cell)
                    #Right
                    if  self.x+1<=self.parent.columns:
                        cell=self.parent.getCell("cell"+str(self.x+1)+"-"+str(self.y))
                        if cell not in emptyList:
                            listOfCell.append(cell)
                    #Bottom
                    if  self.y+1<=self.parent.rows:
                        cell=self.parent.getCell("cell"+str(self.x)+"-"+str(self.y+1))
                        if cell not in emptyList:
                            listOfCell.append(cell)
                else:
                    #Top Right
                    if self.x+1<=self.parent.columns and self.y-1>=0:
                        cell=self.parent.getCell("cell"+str(self.x+1)+"-"+str(self.y-1))
                        if cell not in emptyList:
                            listOfCell.append(cell)
                    #Bottom Right
                    if self.x+1<=self.parent.columns and self.y+1<=self.parent.rows:
                        cell=self.parent.getCell("cell"+str(self.x+1)+"-"+str(self.y+1))
                        if cell not in emptyList:
                            listOfCell.append(cell) 
                    #Top
                    if  self.y-1>=0:
                        cell=self.parent.getCell("cell"+str(self.x)+"-"+str(self.y-1))
                        if cell not in emptyList:
                            listOfCell.append(cell)
                    #Left
                    if  self.x-1>=0:
                        cell=self.parent.getCell("cell"+str(self.x-1)+"-"+str(self.y))
                        if cell not in emptyList:
                            listOfCell.append(cell)
                    #Right
                    if  self.x+1<=self.parent.columns:
                        cell=self.parent.getCell("cell"+str(self.x+1)+"-"+str(self.y))
                        if cell not in emptyList:
                            listOfCell.append(cell)
                    #Bottom
                    if  self.y+1<=self.parent.rows:
                        cell=self.parent.getCell("cell"+str(self.x)+"-"+str(self.y+1))
                        if cell not in emptyList:
                            listOfCell.append(cell)
                for cell in listOfCell:
                    cell.getNeighborCell(type,rangeNeighbor-1,emptyList)
                    
            else:
                if type=="moore":
                    #Top Left
                    if self.x-1>=0 and self.y-1>=0:
                        cell=self.parent.getCell("cell"+str(self.x-1)+"-"+str(self.y-1))
                        if cell not in emptyList:
                            cell.getNeighborCell(type,rangeNeighbor-1,emptyList)
                    #Top Right
                    if self.x+1<=self.parent.columns and self.y-1>=0:
                        cell=self.parent.getCell("cell"+str(self.x+1)+"-"+str(self.y-1))
                        if cell not in emptyList:
                            cell.getNeighborCell(type,rangeNeighbor-1,emptyList)
                    #Bottom Left
                    if self.x-1>=0 and self.y+1<=self.parent.rows:
                        cell=self.parent.getCell("cell"+str(self.x-1)+"-"+str(self.y+1))
                        if cell not in emptyList:
                            cell.getNeighborCell(type,rangeNeighbor-1,emptyList)
                    #Bottom Right
                    if self.x+1<=self.parent.columns and self.y+1<=self.parent.rows:
                        cell=self.parent.getCell("cell"+str(self.x+1)+"-"+str(self.y+1))
                        if cell not in emptyList:
                            cell.getNeighborCell(type,rangeNeighbor-1,emptyList) 
                    #Top
                    if  self.y-1>=0:
                        cell=self.parent.getCell("cell"+str(self.x)+"-"+str(self.y-1))
                        if cell not in emptyList:
                            cell.getNeighborCell(type,rangeNeighbor-1,emptyList)
                    #Left
                    if  self.x-1>=0:
                        cell=self.parent.getCell("cell"+str(self.x-1)+"-"+str(self.y))
                        if cell not in emptyList:
                            cell.getNeighborCell(type,rangeNeighbor-1,emptyList) 
                    #Right
                    if  self.x+1<=self.parent.columns:
                        cell=self.parent.getCell("cell"+str(self.x+1)+"-"+str(self.y))
                        if cell not in emptyList:
                            cell.getNeighborCell(type,rangeNeighbor-1,emptyList)
                    #Bottom
                    if  self.y+1<=self.parent.rows-1:
                        cell=self.parent.getCell("cell"+str(self.x)+"-"+str(self.y+1))
                        if cell not in emptyList:
                            cell.getNeighborCell(type,rangeNeighbor-1,emptyList)
                elif type=="neumann":
                    self.getNeumannNeighbor(rangeNeighbor,emptyList,origin="init")
            
        if isFirst :
            emptyList.remove(self)
        return emptyList
        """for oui in emptyList:
            if len(oui.getAgentsOfType("lac"))==0:
                oui.parent.addOnXandY("lac",oui.x+1,oui.y+1)"""
                    
    def getNeumannNeighbor(self,rangeNeighbor,emptyList=[],origin="init"):
        emptyList.append(self)
        if rangeNeighbor >0:
            if origin=="init":
                emptyList.remove(self)
                #Top
                if  self.y-1>=0:
                    cell=self.parent.getCell("cell"+str(self.x)+"-"+str(self.y-1))
                    if cell not in emptyList:
                        cell.getNeumannNeighbor(rangeNeighbor-1,emptyList,"top")
                #Left
                if  self.x-1>=0:
                    cell=self.parent.getCell("cell"+str(self.x-1)+"-"+str(self.y))
                    if cell not in emptyList:
                        cell.getNeumannNeighbor(rangeNeighbor-1,emptyList,"left") 
                #Right
                if  self.x+1<=self.parent.columns-1:
                    cell=self.parent.getCell("cell"+str(self.x+1)+"-"+str(self.y))
                    if cell not in emptyList:
                        cell.getNeumannNeighbor(rangeNeighbor-1,emptyList,'right')
                #Bottom
                if  self.y+1<=self.parent.rows-1:
                    cell=self.parent.getCell("cell"+str(self.x)+"-"+str(self.y+1))
                    if cell not in emptyList:
                        cell.getNeumannNeighbor(rangeNeighbor-1,emptyList,'bottom') 
            elif origin == "top":
                #Top
                if  self.y-1>=0:
                    cell=self.parent.getCell("cell"+str(self.x)+"-"+str(self.y-1))
                    if cell not in emptyList:
                        cell.getNeumannNeighbor(rangeNeighbor-1,emptyList,"top")
            elif origin=="bottom":
                #Bottom
                if  self.y+1<=self.parent.rows-1:
                    cell=self.parent.getCell("cell"+str(self.x)+"-"+str(self.y+1))
                    if cell not in emptyList:
                        cell.getNeumannNeighbor(rangeNeighbor-1,emptyList,'bottom') 
            elif origin =="right":
                #Right
                if  self.x+1<=self.parent.columns-1:
                    cell=self.parent.getCell("cell"+str(self.x+1)+"-"+str(self.y))
                    if cell not in emptyList:
                        cell.getNeumannNeighbor(rangeNeighbor-1,emptyList,'right')
            elif origin =='left':
                if  self.x-1>=0:
                    cell=self.parent.getCell("cell"+str(self.x-1)+"-"+str(self.y))
                    if cell not in emptyList:
                        cell.getNeumannNeighbor(rangeNeighbor-1,emptyList,"left") 
        
        
        
        
    #Function to check the ownership  of the cell          
    def isMine(self):
        return self.owner==self.parent.parent.actualPlayer
    
    #Function to check the ownership  of the cell          
    def isMineOrAdmin(self):
        return self.owner==self.parent.parent.actualPlayer or self.owner=="admin"
    
    #Function to change the ownership         
    def makeOwner(self,newOwner):
        self.owner=newOwner
        
    #Function get the ownership        
    def getProperty(self):
        self.owner=self.parent.parent.actualPlayer
        
        
    #Function get if the cell have change the value in       
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
    
    #Delete All the Agent       
    def deleteAllAgent(self):
        for i in reversed(range(len(self.collectionOfAgents.agents))):
            self.collectionOfAgents.agents[i].deleteLater()
            del self.collectionOfAgents.agents[i]
        self.update()