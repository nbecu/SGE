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
            #On efface ceux deja existant
            if aKeyOfGamespace in list(self.legendItemList.keys()):
                if len(self.legendItemList[aKeyOfGamespace]) !=0:
                    for anElement in reversed(range(len(self.legendItemList[aKeyOfGamespace]))):
                        self.legendItemList[aKeyOfGamespace][anElement].deleteLater()
                        del self.legendItemList[aKeyOfGamespace][anElement]
            self.legendItemList[aKeyOfGamespace]=[]
            #On affiche les nouveaux
            #On affiche le nom de la legende
        self.y=self.y+1
        anItem=SGLegendItem(self,"None",self.y,self.id)
        self.legendItemList["Title"]=[]
        self.legendItemList["Title"].append(anItem)
        anItem.show()
        for aKeyOfGamespace in self.elementsPov :
            if self.parent.nameOfPov != "default" and aKeyOfGamespace!="agents" :
                if self.parent.nameOfPov in self.elementsPov[aKeyOfGamespace]:
                    for element in self.elementsPov[aKeyOfGamespace][self.parent.nameOfPov]:
                        if aKeyOfGamespace=="deleteButton":
                            self.y=self.y+1
                            anItem=SGLegendItem(self,"square",self.y,element,self.elementsPov[aKeyOfGamespace][self.parent.nameOfPov][element])
                            self.legendItemList[aKeyOfGamespace].append(anItem)
                            anItem.show()
                        else: 
                            for aValue in self.elementsPov[aKeyOfGamespace][self.parent.nameOfPov][element]:
                                self.y=self.y+1
                                anItem=SGLegendItem(self,self.parent.getGameSpace(aKeyOfGamespace).format,self.y,element+" "+aValue,self.elementsPov[aKeyOfGamespace][self.parent.nameOfPov][element][aValue],element)
                                self.legendItemList[aKeyOfGamespace].append(anItem)
                                anItem.show()
            elif aKeyOfGamespace=="agents":
                for anAgentName in self.elementsPov[aKeyOfGamespace]:
                    if self.parent.nameOfPov in self.elementsPov[aKeyOfGamespace][anAgentName]:
                        for element in self.elementsPov[aKeyOfGamespace][anAgentName][self.parent.nameOfPov]:
                            for aValue in self.elementsPov[aKeyOfGamespace][anAgentName][self.parent.nameOfPov][element]:
                                self.y=self.y+1
                                anAgent=self.getFromWich(anAgentName)
                                anItem=SGLegendItem(self,anAgent.format,self.y,anAgent.name+" "+aValue,self.elementsPov[aKeyOfGamespace][anAgentName][self.parent.nameOfPov][element][aValue],anAgent.name)
                                self.legendItemList[aKeyOfGamespace].append(anItem)
                                anItem.show()
            self.setMinimumSize(self.getSizeXGlobal(),10)

     
    
    #Funtion to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        if self.haveADeleteButton :
            if len(self.getLongest()) > len("delete"):
                return 70+len(self.getLongest())*5+50
            else:
                return 70+len("delete")*5+50
        else :
            return 70+len(self.getLongest())*5+50
    
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
        if len(self.elementsPov)!=0:
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
            if aGameSpaceId not in list(self.elementsPov.keys()):
                self.elementsPov[aGameSpaceId]={}
            for aPov in aListOfElement[aGameSpaceId]:
                if aPov not in list(self.elementsPov[aGameSpaceId].keys()):
                    self.elementsPov[aGameSpaceId][aPov]={}
                for element in aListOfElement[aGameSpaceId][aPov] :
                    if element not in list(self.elementsPov[aGameSpaceId][aPov].keys()):
                        self.elementsPov[aGameSpaceId][aPov][element]={}
                    for value in aListOfElement[aGameSpaceId][aPov][element]:
                        self.elementsPov[aGameSpaceId][aPov][element][value]=aListOfElement[aGameSpaceId][aPov][element][value]
        self.initUI()
        
#Adding agent to the legend
    def addAgentToTheLegend(self,agentName,aDictOfAcceptedValue={}):
        if "agents" not in list(self.elementsPov.keys()) :
            self.elementsPov["agents"]={}
        if agentName not in self.elementsPov["agents"]:
            if agentName not in list(self.elementsPov["agents"].keys()) :
                self.elementsPov["agents"][agentName]={}
            anAgentPovs=self.getFromWich(agentName).theCollection.povs
            for aPov in anAgentPovs :
                #If we take all
                if len(aDictOfAcceptedValue)==0:
                    self.elementsPov["agents"][agentName][aPov]=anAgentPovs[aPov]
                #If we apply a filter
                else :
                    for anAttribut in anAgentPovs[aPov]:
                        for anElement in aDictOfAcceptedValue:
                            if anElement == anAttribut :
                                if aPov not in self.elementsPov["agents"][agentName]:
                                    self.elementsPov["agents"][agentName][aPov]={}
                                self.elementsPov["agents"][agentName][aPov][anElement]={}
                                for aValue in anAgentPovs[aPov][anAttribut]:
                                    if aValue in aDictOfAcceptedValue[anAttribut]:
                                        self.elementsPov["agents"][agentName][aPov][anElement][aValue]=anAgentPovs[aPov][anAttribut][aValue]
        self.initUI()
        
        
#Adding the delete Button
    def addDeleteButton(self):
        self.haveADeleteButton=True
        self.elementsPov["deleteButton"]={}
        for aGameSpaceId in self.elementsPov:
            for aPov in self.elementsPov[aGameSpaceId]:
                self.elementsPov["deleteButton"][aPov]={"delete":Qt.yellow}
        self.initUI()
        
        

        
                    
