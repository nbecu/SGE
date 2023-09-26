from tkinter.ttk import Separator
from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGAgent import SGAgent
from mainClasses.gameAction.SGGameActions import SGGameActions
from mainClasses.SGEntity import SGEntity
import re


   
#Class who is responsible of the declaration a cell
class SGCell(SGEntity):
    def __init__(self,grid,rows,columns,shape,defaultsize,gap):
        super().__init__(grid,shape,defaultsize,me='cell')
        #Basic initialize
        self.grid=grid
        self.theCollection=self.grid.model.cellCollection
        self.model=self.grid.model
        self.me='cell'
        self.x=columns
        self.y=rows
        self.name="cell"+str(columns)+'-'+str(rows)
        self.gap=gap
        #Save the basic value for the zoom ( temporary)
        self.saveGap=gap
        #*self.saveSize=size
        #We place the default pos
        self.startXBase=self.grid.startXBase
        self.startYBase=self.grid.startYBase
        self.isDisplay=True
        #We init the dict of Attribute
        self.dictOfAttributs={}
        #We init the Collection for the future Agents
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
        self.initUI()
  
    # to extract the format of the cell
    def getShape(self):
        return self.shape
    
    def initUI(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)
        
    def getId(self):
        return "cell"+str(self.x)+"-"+str(self.y)
    
    def paintEvent(self,event):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
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
        e.accept()
        
    def dropEvent(self, e):
        e.accept()
        oldAgent=e.source()
        self.moveAgentByRecreating_it(oldAgent)
        e.setDropAction(Qt.MoveAction)


    def moveAgentByRecreating_it(self,oldAgent):
        theAgent=self.grid.model.copyOfAgentAtCoord(self,oldAgent)
        self.updateIncomingAgent(theAgent)
        theAgent.show()
        oldAgent.deleteLater()

             
    #To get the pov
    def getPov(self):
        return self.grid.model.nameOfPov

    #To handle the attributs and values
    def setValue(self,aAttribut,aValue):
        """
        Sets the value of an attribut
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be set
        """       
        self.dictOfAttributs[aAttribut]=aValue
        
             
    #To handle the selection of an element int the legend
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            #Something is selected
            if self.grid.model.selected[0]!=None :
                authorisation=SGGameActions.getActionPermission(self)
         
                #The delete Action
                if self.grid.model.selected[2].split()[0]== "Delete" or self.grid.model.selected[2].split()[0]== "Remove" :
                    if authorisation : 
                        if len(self.history["value"])==0:
                            self.history["value"].append([0,0,self.dictOfAttributs])
                        #We now check the feedBack of the actions if it have some
                        """if theAction is not None:
                            self.feedBack(theAction)"""
                        if len(self.agents) !=0:
                            for i in reversed(range(len(self.collectionOfAgents.agents))):
                                self.agents[i].deleteLater()
                                del self.agents[i]
                        self.grid.removeVisiblityCell(self.getId())
                        self.history["value"].append([self.grid.model.timeManager.currentRound,self.grid.model.timeManager.currentPhase,"deleted"])
                        if self.grid.model.selected[4] == "delete":
                            updatePermit=True
                            for item in self.grid.model.cellCollection[self.grid.id]['watchers']:
                                for watcher in self.grid.model.cellCollection[self.grid.id]['watchers'][item]:
                                    watcher.updateText()
                        else:
                            for watcher in self.grid.model.cellCollection[self.grid.id]['watchers'][self.grid.model.selected[4]]:
                                updatePermit=watcher.getUpdatePermission()
                                if updatePermit:
                                    watcher.updateText()
                        self.show()
                        self.repaint()    

                #The Replace cell and change value Action
                elif self.grid.model.selected[1]== "square" or self.grid.model.selected[1]=="hexagonal":
                    if  authorisation :
                        #We now check the feedBack of the actions if it have some
                        if len(self.history["value"])==0:
                            self.history["value"].append([0,0,self.dictOfAttributs])
                        """if theAction is not None:
                            self.feedBack(theAction)"""
                        if self.grid.model.selected[0].legend.id!="adminLegend":
                             self.owner=self.grid.model.currentPlayer
                        self.isDisplay=True
                        value =self.grid.model.selected[3]
                        #attribut=self.grid.model.selected[2]
                        theKey=""
                        if self.grid.model.nameOfPov in list(self.model.cellCollection[self.grid.id]["ColorPOV"]):
                            # pov
                            for anAttribute in list(self.model.cellCollection[self.grid.id]["ColorPOV"][self.grid.model.nameOfPov].keys()):
                                if value in list(self.model.cellCollection[self.grid.id]["ColorPOV"][self.grid.model.nameOfPov][anAttribute].keys()) :
                                    theKey=anAttribute
                                    break
                            aDictWithValue={theKey:value}    
                            for aVal in list(aDictWithValue.keys()) :
                                if aVal in list(self.model.cellCollection[self.grid.id]["ColorPOV"][self.grid.model.nameOfPov].keys()) :
                                        for anAttribute in list(self.model.cellCollection[self.grid.id]["ColorPOV"][self.grid.model.nameOfPov].keys()):
                                            self.dictOfAttributs.pop(anAttribute,None)

                        elif self.grid.model.nameOfPov in list(self.model.cellCollection[self.grid.id]["BorderPOV"]):
                            # borderPov
                            for anAttribute in list(self.model.cellCollection[self.grid.id]["BorderPOV"][self.grid.model.nameOfPov].keys()):
                                if value in list(self.model.cellCollection[self.grid.id]["BorderPOV"][self.grid.model.nameOfPov][anAttribute].keys()) :
                                    theKey=anAttribute
                                    break
                            aDictWithValue={theKey:value}  
                            for aVal in list(aDictWithValue.keys()) :  
                                if aVal in list(self.model.cellCollection[self.grid.id]["BorderPOV"][self.grid.model.nameOfPov].keys()) :
                                    for anAttribute in list(self.model.cellCollection[self.grid.id]["BorderPOV"][self.grid.model.nameOfPov].keys()):
                                            self.dictOfAttributs.pop(anAttribute,None)
                        
                        self.dictOfAttributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]  
                        self.history["value"].append([self.grid.model.timeManager.currentRound,self.grid.model.timeManager.currentPhase,self.dictOfAttributs])
                        if self.grid.model.selected[4] in self.model.cellCollection[self.grid.id]["watchers"]:
                            for watcher in self.model.cellCollection[self.grid.id]["watchers"][self.grid.model.selected[4]]:
                                updatePermit=watcher.getUpdatePermission()
                                if updatePermit:
                                    watcher.updateText()
                        self.update()
                        

                #For agent placement         
                else :
                    if  authorisation :
                        aDictWithValue={self.grid.model.selected[4]:self.grid.model.selected[3]}
                        if self.grid.model.selected[4] =="empty" or self.grid.model.selected[3]=='empty':
                            Species=self.grid.model.selected[2]
                        elif self.grid.model.selected[4] ==None or self.grid.model.selected[3]==None:
                            Species=self.grid.model.selected[2]
                        elif ":" in self.grid.model.selected[2] :
                            selected=self.grid.model.selected[2]
                            chain=selected.split(' : ')
                            Species = chain[0]
                        else:
                            Species=re.search(r'\b(\w+)\s*:', self.grid.model.selected[5]).group(1)
                        if self.isDisplay==True :
                            #We now check the feedBack of the actions if it have some
                            """if theAction is not None:
                                self.feedBack(theAction)"""
                            theSpecies = self.model.getAgentSpecie(Species)
                            self.grid.model.newAgentAtCoords(self.grid, theSpecies, self.x, self.y, aDictWithValue,init=False)             #(self,theSpecies,aDictWithValue)
                            
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
                        
            
    #To handle the arrival of an agent on the cell (this is a private method)
    def updateIncomingAgent(self,anAgent):
        anAgent.cell=self
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

        # for aAgent in self.model.getAgents():
        #     aAgent.cell.moveAgentByRecreating_it(aAgent)
        
        if self.rect().contains(point):
            menu.exec_(self.mapToGlobal(point))


#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    def value(self,att):
        """to comment"""
        return self.dictOfAttributs[att]
    
    #To verify if the cell contain the value pas in parametre through a dictionnary
    def checkValue(self,aDictOfValue):
        """NOT TESTED"""
        theKey=list(aDictOfValue.keys())[0] 
        if theKey in list(self.dictOfAttributs.keys()):
            return aDictOfValue[theKey]==self.dictOfAttributs[theKey]
        return False
    
    def testCondition(self,aCondition):
        res = False 
        if callable(aCondition):
            res = aCondition(self)
        return res
    
    #To change the value
    def changeValue(self,aDictOfValue):
        """NOT TESTED"""
        if len(self.history["value"])==0:
            self.history["value"].append([0,0,self.attributs])
        self.grid.setForXandY(aDictOfValue,self.x+1,self.y+1)
        self.history["value"].append([self.grid.model.timeManager.currentRound,self.grid.model.timeManager.currentPhase,self.attributs])
     
    
    #To get all of a kind of agent on a cell 
    def getAgents(self):
        listOfAgents=[]
        for agent in self.agents:
           listOfAgents.append(agent)
        return  listOfAgents
 
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
    
    #Delete All the Agent       
    def deleteAllAgent(self):
        """NOT TESTED"""
        for i in reversed(range(len(self.collectionOfAgents.agents))):
            self.collectionOfAgents.agents[i].deleteLater()
            del self.collectionOfAgents.agents[i]
        self.update()

    def doAction(self, aLambdaFunction):
        aLambdaFunction(self)