from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null, true

from SGGameSpace import SGGameSpace
from SGLegendItem import SGLegendItem
from mainClasses.SGCell import SGCell
from SGGrid import SGGrid

#Class who is responsible of the grid creation
class SGLegende(SGGameSpace):
    def __init__(self,parent,name,elementPov,borderColor=Qt.black,backgroundColor=Qt.transparent):
        super().__init__(parent,0,60,0,0,true,backgroundColor)
        self.id=name
        self.parent=parent
        self.elementsPov=elementPov
        self.legendItemList={}
        self.borderColor=borderColor
        self.haveADeleteButton=False
        self.y=0
        self.initUI()

        
    def initUI(self):
        self.y=0
        for aKeyOfGamespace in self.elementsPov :
            self.legendItemList[aKeyOfGamespace]=[]
            """print("--------------------")
            print(self.id)
            print(self.elementsPov)"""
            if self.parent.nameOfPov != "default" and aKeyOfGamespace!="agents" :
                for element in self.elementsPov[aKeyOfGamespace][self.parent.nameOfPov]:
                    if aKeyOfGamespace=="deleteButton":
                        self.y=self.y+1
                        self.legendItemList[aKeyOfGamespace].append(SGLegendItem(self,"square",self.y,element,self.elementsPov[aKeyOfGamespace][self.parent.nameOfPov][element]))
                    else: 
                        for aValue in self.elementsPov[aKeyOfGamespace][self.parent.nameOfPov][element]:
                            self.y=self.y+1
                            self.legendItemList[aKeyOfGamespace].append(SGLegendItem(self,self.parent.getGameSpace(aKeyOfGamespace).format,self.y,element+" "+aValue,self.elementsPov[aKeyOfGamespace][self.parent.nameOfPov][element][aValue],element))
            elif aKeyOfGamespace=="agents":
                for anAgentName in self.elementsPov[aKeyOfGamespace]:
                    for aValue in self.elementsPov[aKeyOfGamespace][anAgentName][self.parent.nameOfPov][element]:
                        self.y=self.y+1
                        anAgent=self.getFromWich(anAgentName)
                        self.legendItemList[aKeyOfGamespace].append(SGLegendItem(self,anAgent.format,self.y,anAgent.name,self.elementsPov[aKeyOfGamespace][anAgentName][self.parent.nameOfPov][element][aValue],anAgent.name))
     
    
    #Funtion to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        if self.haveADeleteButton :
            if len(self.getLongest()) > len("delete"):
                return 70+len(self.getLongest())*5
            else:
                return 70+len("delete")*5
        else :
            return 70+len(self.getLongest())*5
    
    def getLongest(self):
        longestWord=""
        for key in self.legendItemList :
            for element in self.legendItemList[key] :
                if len(element.texte)>len(longestWord):
                    longestWord=element.texte
        return longestWord
    
    def getSizeYGlobal(self):
        somme=30
        for key in self.legendItemList :
            somme= somme+ 27*len(self.legendItemList[key])
        return somme
    
    #Funtion to handle the zoom
    def zoomIn(self):
        return True
    
    def zoomOut(self):
        return True
    
    #To handle the drag of the legende
    def mouseMoveEvent(self, e):
    
        if e.buttons() != Qt.LeftButton:
            return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())

        drag.exec_(Qt.MoveAction)
    
    
        
    #Drawing the legende
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
        painter.setPen(QPen(self.borderColor,1));
        #Draw the corner of the legende
        self.setMinimumSize(self.getSizeXGlobal()+3, self.getSizeYGlobal()+3)
        painter.drawRect(0,0,self.getSizeXGlobal(), self.getSizeYGlobal())        
        painter.end()
        
    #Get from wich grid an Agent is from to create the legend
    def getFromWich(self,anAgentName):
        for aGameSpace in self.parent.gameSpaces :
            if isinstance(self.parent.gameSpaces[aGameSpace],SGGrid) == True :
                aResult = self.parent.gameSpaces[aGameSpace].getAgentOfTypeForLegend(anAgentName)
                if aResult != null:
                    return aResult
        
    
    
        

#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

#To add Povs in a legend
    def addToTheLegende(self,aListOfElement):
        #For the grid value
        for aGameSpaceId in aListOfElement:
            for aPov in aListOfElement[aGameSpaceId]:
                for element in aListOfElement[aGameSpaceId][aPov] :
                    for value in aListOfElement[aGameSpaceId][aPov][element]:
                        self.elementsPov[aGameSpaceId][aPov][element][value]=aListOfElement[aGameSpaceId][aPov][element][value]
        self.initUI()
        
#Adding agent to the legend
    def addAgentToTheLegend(self,agentName):
        if "agents" not in list(self.elementsPov.keys()) :
            self.elementsPov["agents"]={}
        if agentName not in self.elementsPov["agents"]:
            if agentName not in list(self.elementsPov["agents"].keys()) :
                self.elementsPov["agents"][agentName]={}
            anAgentPovs=self.getFromWich(agentName).theCollection.povs
            for aPov in anAgentPovs :
                self.elementsPov["agents"][agentName][aPov]=anAgentPovs[aPov]
        self.initUI()
        
        
#Adding the delete Button
    def addDeleteButton(self):
        self.haveADeleteButton=True
        self.elementsPov["deleteButton"]={}
        for aGameSpaceId in self.elementsPov:
            for aPov in self.elementsPov[aGameSpaceId]:
                self.elementsPov["deleteButton"][aPov]={"delete":Qt.yellow}
        self.initUI()
        
        

        
                    
