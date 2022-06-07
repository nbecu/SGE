from itertools import count
from pickle import TRUE
import random
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import false, null, true

from SGGameSpace import SGGameSpace
from SGCellCollection import SGCellCollection
from SGAgent import SGAgent


from PyQt5.QtWidgets import QAction


import copy

#Class who is responsible of the grid creation
class SGGrid(SGGameSpace):
    def __init__(self,parent,name,rows=8, columns=8,format="square",gap=3,size=32,aColor=None):
        super().__init__(parent,0,60,0,0)
        #Basic initialize
        self.zoom=1
        self.parent=parent
        self.id=name
        self.rows=rows
        self.columns=columns
        self.format=format
        self.gap=gap
        self.size=size
        
        self.saveGap=gap
        self.saveSize=size
        
        self.startXBase=0
        self.startYBase=0
        
        if aColor != "None":
            self.setColor(aColor)
        #We initialize the user interface related to the grid
        self.initUI()
       
    #Initialize the user interface
    def initUI(self): 
        #Init the cellCollection
        self.collectionOfCells=SGCellCollection(self,self.columns,self.rows,self.format,self.size,self.gap,self.startXBase,self.startYBase)
        self.collectionOfAcceptAgent={}
        
        
    #Drawing the game board with the cell
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
        #Base of the gameBoard
        if(self.format=="square"):
            #We redefine the minimum size of the widget
            self.setMinimumSize(int(self.columns*self.size+(self.columns+1)*self.gap+1)+3, int(self.rows*self.size+(self.rows+1)*self.gap)+3)
            painter.drawRect(0,0, int(self.columns*self.size+(self.columns+1)*self.gap+1), int(self.rows*self.size+(self.rows+1)*self.gap))
        elif(self.format=="hexagonal"):
            self.setMinimumSize(int(self.columns*self.size+(self.columns+1)*self.gap+1)+int(self.size/2)+3,         int((self.rows+1)*(self.size/3)*2) +self.gap*2+3)
            painter.drawRect(0,0, int(self.columns*self.size+(self.columns+1)*self.gap+1)+int(self.size/2),       int((self.rows+1)*(self.size/3)*2) +self.gap*2) 
        painter.end()
        
    #Funtion to handle the zoom
    def zoomIn(self):
        self.zoom=self.zoom*1.1
        self.gap=round(self.gap+(self.zoom*1))
        self.size=round(self.size+(self.zoom*10))
        for cell in self.collectionOfCells.getCells() :
            self.collectionOfCells.getCell(cell).zoomIn() 
        self.update()
    
    def zoomOut(self):
        self.zoom=self.zoom*0.9
        self.size=round(self.size-(self.zoom*10))
        if(self.gap>2 and self.format=="square"):
            self.gap=round(self.gap-(self.zoom*1))
            for cell in self.collectionOfCells.getCells():
                self.collectionOfCells.getCell(cell).zoomOut()
        else:
            self.gap=round(self.gap-(self.zoom*1))
            for cell in self.collectionOfCells.getCells():
                self.collectionOfCells.getCell(cell).zoomOut()
        for cell in self.collectionOfCells.getCells() :
            self.collectionOfCells.getCell(cell).zoomOut() 
        self.update()
        
    #To handle the drag of the grid
    def mouseMoveEvent(self, e):
    
        if e.buttons() != Qt.LeftButton:
            return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())

        drag.exec_(Qt.MoveAction)
        
    #Funtion to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        if(self.format=="square"):
            return int(self.columns*self.size+(self.columns+1)*self.gap+1)
        if(self.format=="hexagonal"):
            return int(self.columns*self.size+(self.columns+1)*self.gap+1) +int(self.size/2)
    
    def getSizeYGlobal(self):
        if(self.format=="square"):
            return int(self.rows*self.size+(self.rows+1)*self.gap)
        if(self.format=="hexagonal"):
            return int((self.rows+1)*(self.size/3)*2) +self.gap*2
        
        
    #To get all the values possible for legende
    def getValuesForLegende(self):
        return self.collectionOfCells.getPovs()
        
    #Agent function 
    #To get all agents on the grid of a particular type
    def getAgentsOfType(self,aType):
        theList=[]
        for aCell in  self.collectionOfCells.cells:
            for anAgent in self.collectionOfCells.getCell(aCell).getAgentsOfType(aType):
                theList.append(anAgent)
        return theList
    
    #To get an agents on the grid of a particular type (use for the legendOnly)
    def getAgentOfTypeForLegend(self,aType):
        for anAgent in self.collectionOfAcceptAgent :
            if anAgent ==aType:
                return self.collectionOfAcceptAgent[anAgent]
        return null
                
        
    
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    #Retourn the cell
    def getCell(self,aName):
        return self.collectionOfCells.getCell(aName)
    
    #Retourn the from the coordonate
    def getCellFromCoordonate(self,x, y):
        return self.getCell("cell"+str(x-1)+'-'+str(y-1))
    
#To handle POV and placing on cell
    #To define a value for all cells
    def setValueForCells(self,aDictWithValue):
        for aCell in list(self.collectionOfCells.getCells().values()):
            for aVal in list(aDictWithValue.keys()) :
                if len(aCell.theCollection.povs) !=0:
                    if aVal in list(aCell.theCollection.povs[self.parent.nameOfPov].keys()) :
                            for anAttribute in list(aCell.theCollection.povs[self.parent.nameOfPov].keys()):
                                aCell.attributs.pop(anAttribute,None)
            
            aCell.attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]
            
    #To apply to a specific cell a value  
    def setForXandY(self,aDictWithValue,aValueX,aValueY):
        for aVal in list(aDictWithValue.keys()) :
            if len(self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(aValueY-1)).theCollection.povs) !=0:
                if aVal in list(self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(aValueY-1)).theCollection.povs[self.parent.nameOfPov].keys()) :
                    for anAttribute in list(self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(aValueY-1)).theCollection.povs[self.parent.nameOfPov].keys()):
                        self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(aValueY-1)).attributs.pop(anAttribute,None)
        self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(aValueY-1)).attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]
    
    #To apply to a all row of cell a value
    def setForX(self,aDictWithValue,aValueX):
        for y in range(self.rows):
            if len(self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(y)).theCollection.povs) !=0:
                for aVal in list(aDictWithValue.keys()) :
                    if aVal in list(self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(y)).theCollection.povs[self.parent.nameOfPov].keys()) :
                        for anAttribute in list(self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(y)).theCollection.povs[self.parent.nameOfPov].keys()):
                            self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(y)).attributs.pop(anAttribute,None)
            self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(y)).attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]
    
    #To apply to a all column of cell a value
    def setForY(self,aDictWithValue,aValueY):
        for x in range(self.columns):
            for aVal in list(aDictWithValue.keys()) :
                if len(self.collectionOfCells.getCell("cell"+str(x)+"-"+str(aValueY-1)).theCollection.povs) !=0:
                    if aVal in list(self.collectionOfCells.getCell("cell"+str(x)+"-"+str(aValueY-1)).theCollection.povs[self.parent.nameOfPov].keys()) :
                        for anAttribute in list(self.collectionOfCells.getCell("cell"+str(x)+"-"+str(aValueY-1)).theCollection.povs[self.parent.nameOfPov].keys()):
                            self.collectionOfCells.getCell("cell"+str(x)+"-"+str(aValueY-1)).attributs.pop(anAttribute,None)
            self.collectionOfCells.getCell("cell"+str(x)+"-"+str(aValueY-1)).attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]
    
    #To apply to some random cell a value
    def setForRandom(self,aDictWithValue,numberOfRandom):
        alreadyDone=list()
        while len(alreadyDone)!=numberOfRandom:
            aValueX=random.randint(0, self.columns-1)
            aValueY=random.randint(0, self.rows-1)
            if (aValueX,aValueY) not in alreadyDone:
                alreadyDone.append((aValueX,aValueY))
                for aVal in list(aDictWithValue.keys()) :
                    if len(self.collectionOfCells.getCell("cell"+str(aValueX)+"-"+str(aValueY)).theCollection.povs) !=0:
                        if aVal in list(self.collectionOfCells.getCell("cell"+str(aValueX)+"-"+str(aValueY)).theCollection.povs[self.parent.nameOfPov].keys()) :
                            for anAttribute in list(self.collectionOfCells.getCell("cell"+str(aValueX)+"-"+str(aValueY)).theCollection.povs[self.parent.nameOfPov].keys()):
                                self.collectionOfCells.getCell("cell"+str(aValueX)+"-"+str(aValueY)).attributs.pop(anAttribute,None)
                self.collectionOfCells.getCell("cell"+str(aValueX)+"-"+str(aValueY)).attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]
                
#To handle the placing of agents
    #To apply to a specific cell a value  
    def addOnXandY(self,anAgentName,aValueX,aValueY,aValueForAgent=None):
        anAgent=SGAgent(self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(aValueY-1)),anAgentName,self.collectionOfAcceptAgent[anAgentName].format,self.collectionOfAcceptAgent[anAgentName].size)
        anAgent.theCollection.povs=self.collectionOfAcceptAgent[anAgentName].theCollection.povs
        anAgent.attributs=self.collectionOfAcceptAgent[anAgentName].attributs.copy()
        self.collectionOfCells.getCell("cell"+str(aValueX-1)+"-"+str(aValueY-1)).collectionOfAgents.addAgent(anAgent)
        if aValueForAgent is not None :
            for anAttribut in self.collectionOfCells.povs[self.parent.nameOfPov] :
                    if aValueForAgent in list(self.collectionOfCells.povs[self.parent.nameOfPov][anAttribut].keys()) :
                        anAgent.attributs[anAttribut]=aValueForAgent
        anAgent.show()
        self.update()
        return anAgent
    
    #to add agent on multiple cell depending of their value
    def addAgentOnValue(self,anAgentName,aDictValueForAgent,aValueForAgent=None):
        cells=self.getCellOfValue(aDictValueForAgent)
        for cell in cells :
            anAgent=SGAgent(cell,anAgentName,self.collectionOfAcceptAgent[anAgentName].format,self.collectionOfAcceptAgent[anAgentName].size)
            anAgent.theCollection.povs=self.collectionOfAcceptAgent[anAgentName].theCollection.povs
            anAgent.attributs=self.collectionOfAcceptAgent[anAgentName].attributs.copy()
            cell.collectionOfAgents.addAgent(anAgent)
            if aValueForAgent is not None :
                for anAttribut in self.collectionOfCells.povs[self.parent.nameOfPov] :
                        if aValueForAgent in list(self.collectionOfCells.povs[self.parent.nameOfPov][anAttribut].keys()) :
                            anAgent.attributs[anAttribut]=aValueForAgent
            anAgent.show()
            self.update()
        return anAgent
        
#To add a specific pov 
    def setUpPov(self,aNameOfPov,aDictOfValue,theTypeOfObjectToApply="cells",theNameOfTheAgent="circleAgent"):
        #We apply the news pov
        if(theTypeOfObjectToApply=="cells"):
            self.collectionOfCells.povs[aNameOfPov]=aDictOfValue
        elif theTypeOfObjectToApply == "agents":
            for anAgentIt in self.collectionOfAcceptAgent :
                if self.collectionOfAcceptAgent[anAgentIt].name ==theNameOfTheAgent:
                    self.collectionOfAcceptAgent[anAgentIt].theCollection.povs[aNameOfPov]=aDictOfValue
        self.parent.updateLegendeAdmin()
        #Adding the Pov to the menue bar
        if aNameOfPov not in self.parent.listOfPovsForMenu :
            self.parent.listOfPovsForMenu.append(aNameOfPov)
            anAction=QAction(" &"+aNameOfPov, self)
            self.parent.povMenu.addAction(anAction)
            anAction.triggered.connect(lambda: self.parent.setInitialPovGlobal(aNameOfPov))
            
    #To define a value for all Agents
    def setValueForAgents(self,typeOfAgent,aDictWithValue):
        for aCell in list(self.collectionOfCells.getCells().values()):
            for anAgent in aCell.getAgentsOfType(typeOfAgent):
                for aVal in list(aDictWithValue.keys()) :
                    if aVal in list(anAgent.theCollection.povs[self.parent.nameOfPov].keys()) :
                        for anAttribute in list(anAgent.theCollection.povs[self.parent.nameOfPov].keys()):
                            anAgent.attributs.pop(anAttribute,None)
                anAgent.attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]
                
    #To define a value for the model of an Agent
    def setValueForModelAgents(self,typeOfAgent,aDictWithValue):
            anAgent=self.collectionOfAcceptAgent[typeOfAgent]
            #On cherche la pov et on suppr les valeur deja existante de la pov
            for aPov in list(anAgent.theCollection.povs.keys()):
                if list(aDictWithValue.keys())[0] in list(anAgent.theCollection.povs[aPov].keys()):
                    for anAttribut in list(anAgent.theCollection.povs[aPov].keys()):
                        anAgent.attributs.pop(anAttribut,None)
            anAgent.attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]
            
    #To define a value for all Agents of a cell
    def setValueAgentsOnCell(self,typeOfAgent,aDictWithValue,aCellId):        
        aCell=self.getCell(aCellId)
        for anAgent in aCell.collectionOfAgents.agents:
            if anAgent.format == typeOfAgent:
                #On cherche la pov et on suppr les valeur deja existante de la pov
                for aPov in list(anAgent.theCollection.povs.keys()):
                    if list(aDictWithValue.keys())[0] in list(anAgent.theCollection.povs[aPov].keys()):
                        for anAttribut in list(anAgent.theCollection.povs[aPov].keys()):
                            anAgent.attributs.pop(anAttribut,None)
                anAgent.attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]]
    
    #To change the value of an unique agent on a cell
    def setForAnAgentOfCell(self,typeOfAgent,aDictWithValue,aCellId):        
        aCell=self.getCell(aCellId)
        for anAgent in aCell.collectionOfAgents.agents:
            if anAgent.name == typeOfAgent:
                #On cherche la pov et on suppr les valeur deja existante de la pov
                for aPov in list(anAgent.theCollection.povs.keys()):
                    
                    if list(aDictWithValue.keys())[0] in list(anAgent.theCollection.povs[aPov].keys()):
                        for anAttribut in list(anAgent.theCollection.povs[aPov].keys()):
                            if anAttribut ==list(aDictWithValue.keys())[0]:
                                if anAgent.attributs[anAttribut] == list(aDictWithValue.values())[0]: 
                                    continue;
                                else:
                                    anAgent.attributs.pop(anAttribut,None)
                                    anAgent.attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]] 
                                    return True
                            else:
                                anAgent.attributs.pop(anAttribut,None)
                                anAgent.attributs[list(aDictWithValue.keys())[0]]=aDictWithValue[list(aDictWithValue.keys())[0]] 
                                return True
        return False   
    
    #To get a cell of the grid
    def getACell(self):        
        return self.collectionOfCells.getCells()[list(self.collectionOfCells.getCells().keys())[0]]
     
     
    #To grow all attributs of cells of one type
    def makeEvolve(self,listOfAttributsToMakeEvolve):
        for aCell in list(self.collectionOfCells.getCells().values()) :
            for anAttribut in listOfAttributsToMakeEvolve:
                if anAttribut in list(aCell.attributs.keys()) :
                    for aPov in aCell.theCollection.povs:
                        found=list(aCell.theCollection.povs[aPov][anAttribut].keys()).index(aCell.attributs[anAttribut])
                        if found!=-1 and found+1 != len(aCell.theCollection.povs[aPov][anAttribut]):
                            aCell.attributs[anAttribut]=list(aCell.theCollection.povs[aPov][anAttribut].keys())[found+1]
                            
    #To decrease all attributs of cells of one type
    def makeDecrease(self,listOfAttributsToMakeDecrease):
        for aCell in list(self.collectionOfCells.getCells().values()) :
            for anAttribut in listOfAttributsToMakeDecrease:
                if anAttribut in list(aCell.attributs.keys()) :
                    for aPov in aCell.theCollection.povs:
                        found=list(aCell.theCollection.povs[aPov][anAttribut].keys()).index(aCell.attributs[anAttribut])
                        if found!=-1 and found != 0:
                            aCell.attributs[anAttribut]=list(aCell.theCollection.povs[aPov][anAttribut].keys())[found-1]
                            
    #to get all cells who respect certain value
    def getCellOfValue(self,aDictValueForAgent):
        result=[]
        for cell in list(self.collectionOfCells.cells.values()):
            aKey= list(aDictValueForAgent.keys())[0]
            if aKey in cell.attributs :
                if aDictValueForAgent[aKey]==cell.attributs[aKey]:
                    result.append(cell)
        return result
    
    #to move all of a kind of agent radomly
    def moveRadomlyAgent(self,anAgentName):
        listOfAgentToMove=[]
        listCells=self.collectionOfCells.getCellsDisplay()
        for cell in listCells:
            for anAgent in cell.getAgentsOfType(anAgentName):
                listOfAgentToMove.append(anAgent)
        while len(listOfAgentToMove)!=0 :
            agent=listOfAgentToMove.pop()
            oldPlace=agent.parent
            newPlace=oldPlace
            while newPlace==oldPlace:
                newPlace=listCells[random.randint(0,len(listCells)-1)]
            #We remove the agent of the actual cell
            agent.parent.collectionOfAgents.agents.pop(agent.parent.collectionOfAgents.agents.index(agent))
            agent.deleteLater()
            #We add the agent to the new cell
            theAgent=self.addOnXandY(agent.name,newPlace.x+1,newPlace.y+1)
            theAgent.x=agent.x
            theAgent.y=agent.y
            theAgent.attributs=agent.attributs
            theAgent.show()
            
    #To delete a kind of Agent on hte grid  
    def deleteAgent(self,nameOfAgent,numberOfDelete=0,condition=[]):
        aListOfAgent= self.getAgentsOfType(nameOfAgent)
        count=0
        nbrDelete=0
        if numberOfDelete==0:
            numberOfDelete=len(aListOfAgent)
        while numberOfDelete>nbrDelete and len(aListOfAgent)!=0 and count!=len(aListOfAgent):
            nbr=aListOfAgent[count].parent.deleteAgent(nameOfAgent,numberOfDelete,condition)
            nbrDelete=nbrDelete+nbr
            count=count+1
        self.show()

                    
       
     
                
        
                
    
    
  
            
    

