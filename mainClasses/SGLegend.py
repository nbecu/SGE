from typing import Hashable
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null, true

from SGGameSpace import SGGameSpace
from SGLegendItem import SGLegendItem
from SGCell import SGCell
from SGGrid import SGGrid
#from gameAction import SGCreate
#from SGCreate import getNumberUsed

#Class who is responsible of the Legend creation 
class SGLegend(SGGameSpace):
    def __init__(self,parent,name,elementPov,playerName,AgentList,showAgents=False,borderColor=Qt.black,backgroundColor=Qt.transparent):
        super().__init__(parent,0,60,0,0,true,backgroundColor)
        self.id=name
        self.model=parent
        self.elementsPov=elementPov
        self.AgentList=AgentList
        self.showAgents=showAgents
        self.playerName=playerName
        self.legendItems={}
        self.borderColor=borderColor
        self.haveADeleteButton=False
        self.y=0
        self.initUI()

    # CURRENT VERSION
    def initUI(self):
        self.y=0
        for aKeyOfGamespace in self.elementsPov :
            if aKeyOfGamespace in list(self.legendItems.keys()):
                if len(self.legendItems[aKeyOfGamespace]) !=0:
                    for anElement in reversed(range(len(self.legendItems[aKeyOfGamespace]))):
                        self.legendItems[aKeyOfGamespace][anElement].deleteLater()
                        del self.legendItems[aKeyOfGamespace][anElement]
            self.legendItems[aKeyOfGamespace]=[]
        self.y=self.y+1
        anItem=SGLegendItem(self,"None",self.y,self.id)
        self.legendItems["Title"]=[]
        self.legendItems["Title"].append(anItem)
        anItem.show()
        for aKeyOfGamespace in self.elementsPov :
            if aKeyOfGamespace=="deleteButton":
                added=set()
                item_key = "Delete"
                if item_key not in added:
                    self.y=self.y+1
                    anItem=SGLegendItem(self,"square",self.y,"Delete",Qt.darkGray,"coucou","world")
                    self.legendItems[aKeyOfGamespace].append(anItem)
                    added.add(item_key)
                    anItem.show()
            else:
                for entity in self.elementsPov[aKeyOfGamespace]:
                    if entity == 'cells':
                        added_items = set()
                        added_colors = set()
                        grid=self.model.getGameSpace(aKeyOfGamespace)
                        for aPov in self.elementsPov[aKeyOfGamespace]['cells'].keys():
                            if aPov == self.model.nameOfPov:
                                if aPov in grid.collectionOfCells.povs.keys():
                                    currentPov=aPov
                                    for aAttribut in self.elementsPov[aKeyOfGamespace]['cells'][currentPov]:
                                        for aValue in self.elementsPov[aKeyOfGamespace]['cells'][currentPov][aAttribut]:
                                            item_key=aAttribut +' '+ aValue
                                            color=self.elementsPov[aKeyOfGamespace]['cells'][currentPov][aAttribut][aValue]
                                            if item_key not in added_items and color not in added_colors and color != Qt.transparent:
                                                self.y=self.y+1
                                                anItem=SGLegendItem(self,self.model.getGameSpace(aKeyOfGamespace).format,self.y,aAttribut+" "+aValue,color,aValue,aAttribut)
                                                self.legendItems[aKeyOfGamespace].append(anItem)
                                                anItem.show()
                                                added_items.add(item_key)
                                                added_colors.add(color)
                                if aPov in grid.collectionOfCells.borderPovs.keys():
                                    currentPov=aPov
                                    for aAttribut in self.elementsPov[aKeyOfGamespace]['cells'][currentPov]:
                                        for aValue in self.elementsPov[aKeyOfGamespace]['cells'][currentPov][aAttribut]:
                                            item_key=aAttribut +' '+ aValue
                                            color=self.elementsPov[aKeyOfGamespace]['cells'][currentPov][aAttribut][aValue]
                                            if item_key not in added_items and color not in added_colors and color != Qt.transparent:
                                                self.y=self.y+1
                                                anItem=SGLegendItem(self,self.model.getGameSpace(aKeyOfGamespace).format,self.y,aAttribut+" "+aValue,color,aValue,aAttribut,True)
                                                self.legendItems[aKeyOfGamespace].append(anItem)
                                                anItem.show()
                                                added_items.add(item_key)
                                                added_colors.add(color)

                            else:
                                if aPov in grid.collectionOfCells.povs.keys():
                                    for aAtt in list(grid.collectionOfCells.povs[aPov].keys()):
                                        for aVal in list(grid.collectionOfCells.povs[aPov][aAtt].keys()):
                                            color=grid.collectionOfCells.povs[aPov][aAtt][aVal]
                                            item_key = aAtt + aVal
                                            if item_key not in added_items and color not in added_colors and color != Qt.transparent:
                                                self.y=self.y+1
                                                anItem=SGLegendItem(self,self.model.getGameSpace(aKeyOfGamespace).format,self.y,aAtt +" "+ aVal,color,aVal,aAtt)
                                                self.legendItems[aKeyOfGamespace].append(anItem)
                                                anItem.show()
                                                added_items.add(item_key)
                                                added_colors.add(color)
                                if aPov in grid.collectionOfCells.borderPovs.keys():
                                    for aAtt in list(grid.collectionOfCells.borderPovs[aPov].keys()):
                                        for aVal in list(grid.collectionOfCells.borderPovs[aPov][aAtt].keys()):
                                            color=grid.collectionOfCells.borderPovs[aPov][aAtt][aVal]
                                            item_key = aAtt + aVal
                                            if item_key not in added_items and color not in added_colors and color != Qt.black:
                                                self.y=self.y+1
                                                anItem=SGLegendItem(self,self.model.getGameSpace(aKeyOfGamespace).format,self.y,aAtt +" "+ aVal,color,aVal,aAtt,True)
                                                self.legendItems[aKeyOfGamespace].append(anItem)
                                                anItem.show()
                                                added_items.add(item_key)
                                                added_colors.add(color)                     

                    elif entity == 'agents':
                        for anAgent in self.AgentList:
                            for Species in self.elementsPov[aKeyOfGamespace]['agents'].keys():
                                if anAgent.species == Species:
                                    for aPov in self.elementsPov[aKeyOfGamespace]['agents'][Species].keys():
                                        if aPov == self.model.nameOfPov:
                                            print("current POV")
                                            added_items = set()
                                            for anAtt in self.elementsPov[aKeyOfGamespace]['agents'][Species][aPov].keys():
                                                for aValue in self.elementsPov[aKeyOfGamespace]['agents'][Species][aPov][anAtt].keys():
                                                    item_key = Species + anAtt + aValue
                                                    if item_key not in added_items:
                                                        text = Species +' : '+ anAtt +' : ' + aValue
                                                        self.y = self.y + 1
                                                        aColor = self.elementsPov[aKeyOfGamespace]['agents'][Species][aPov][anAtt][aValue]
                                                        anItem = SGLegendItem(self, anAgent.format, self.y, text, aColor, aValue, anAtt)
                                                        self.legendItems[aKeyOfGamespace].append(anItem)
                                                        anItem.show()
                                                        added_items.add(item_key)
                                                        print(added_items)
                                                        
                                                        
                                        else:
                                            print("other POV")
                                            item_key= Species
                                            text = Species
                                            existed=False
                                            print(added_items)
                                            print('text : '+text)
                                            for item in added_items:
                                                print('déjà dans set : '+item)
                                                if text in item:
                                                    existed=True
                                                    break
                                            print(existed)
                                            if item_key not in added_items and not existed:
                                                print('on ajoute : '+item_key)
                                                aColor = anAgent.color
                                                self.y=self.y+1
                                                anItem = SGLegendItem(self, anAgent.format, self.y, text, aColor, None,None)
                                                self.legendItems[aKeyOfGamespace].append(anItem)
                                                anItem.show()
                                                added_items.add(item_key)

                                            
            if self.showAgents==True and aKeyOfGamespace !="deleteButton":
                added_species=set()
                for Species in self.model.agentSpecies.keys():
                    item_key=Species
                    if item_key not in added_species:
                        aColor=self.model.agentSpecies[Species]["DefaultColor"]
                        text=Species
                        self.y=self.y+1
                        anItem=SGLegendItem(self,self.model.agentSpecies[Species]["Shape"],self.y,text,aColor,"empty","empty")
                        self.legendItems[aKeyOfGamespace].append(anItem)
                        anItem.show()
                        added_species.add(item_key)



        self.setMinimumSize(self.getSizeXGlobal(),10)

    
    """# Test VERSION
    def initUI(self):
        self.y=0
        print(self.elementsPov)
        for aKeyOfGamespace in self.elementsPov :
            if aKeyOfGamespace in list(self.legendItems.keys()):
                if len(self.legendItems[aKeyOfGamespace]) !=0:
                    ### LATER
                    for anElement in reversed(range(len(self.legendItems[aKeyOfGamespace]))):
                        self.legendItems[aKeyOfGamespace][anElement].deleteLater()
                        del self.legendItems[aKeyOfGamespace][anElement]
            self.legendItems[aKeyOfGamespace]=[]
        self.y=self.y+1
        anItem=SGLegendItem(self,"None",self.y,self.id)
        self.legendItems["Title"]=[]
        self.legendItems["Title"].append(anItem)
        anItem.show()
        for aKeyOfGamespace in self.elementsPov :
            for entity in self.elementsPov[aKeyOfGamespace]:
                if entity == 'cells':
                    added_items = set()
                    added_colors = set()
                    if self.model.nameOfPov in self.elementsPov[aKeyOfGamespace]['cells']:
                        if aKeyOfGamespace=="deleteButton":
                            self.y=self.y+1
                            anItem=SGLegendItem(self,"square",self.y,"Delete",Qt.red,"coucou","world")
                            self.legendItems[aKeyOfGamespace].append(anItem)
                            anItem.show()
                        else:
                            for aPov in self.elementsPov[aKeyOfGamespace]['cells'].keys():
                                if aPov == self.model.nameOfPov:
                                    currentPov=aPov
                                    for aAttribut in self.elementsPov[aKeyOfGamespace]['cells'][currentPov]:
                                        for aValue in self.elementsPov[aKeyOfGamespace]['cells'][currentPov][aAttribut]:
                                            item_key=aAttribut +' '+ aValue
                                            color=self.elementsPov[aKeyOfGamespace]['cells'][currentPov][aAttribut][aValue]
                                            if item_key not in added_items and color not in added_colors:
                                                self.y=self.y+1
                                                anItem=SGLegendItem(self,self.model.getGameSpace(aKeyOfGamespace).format,self.y,aAttribut+" "+aValue,color,aValue,aAttribut)
                                                self.legendItems[aKeyOfGamespace].append(anItem)
                                                anItem.show()
                                                added_items.add(item_key)
                                                added_colors.add(color)
                                else:
                                    item_key= 'Cell'
                                    if item_key not in added_items:
                                            text = 'Cell'
                                            aColor = Qt.white
                                            self.y=self.y+1
                                            anItem = SGLegendItem(self, self.model.getGameSpace(aKeyOfGamespace).format, self.y, text, aColor, "none", "none")
                                            self.legendItems[aKeyOfGamespace].append(anItem)
                                            anItem.show()
                                            added_items.add(item_key)
                elif entity == 'agents':
                    added_items = set()
                    for anAgent in self.AgentList:
                        for Species in self.elementsPov[aKeyOfGamespace]['agents'].keys():
                            if anAgent.species == Species:
                                for aPov in self.elementsPov[aKeyOfGamespace]['agents'][Species].keys():
                                    if aPov == self.model.nameOfPov:
                                        for anAtt in self.elementsPov[aKeyOfGamespace]['agents'][Species][aPov].keys():
                                            for aValue in self.elementsPov[aKeyOfGamespace]['agents'][Species][aPov][anAtt].keys():
                                                item_key = Species + anAtt + aValue
                                                if item_key not in added_items:
                                                    text = Species +' : '+ anAtt +' : ' + aValue
                                                    self.y = self.y + 1
                                                    aColor = self.elementsPov[aKeyOfGamespace]['agents'][Species][aPov][anAtt][aValue]
                                                    anItem = SGLegendItem(self, anAgent.format, self.y, text, aColor, aValue, anAtt)
                                                    self.legendItems[aKeyOfGamespace].append(anItem)
                                                    anItem.show()
                                                    added_items.add(item_key)
                                    else:
                                        item_key= Species
                                        if item_key not in added_items:
                                            text = Species
                                            aColor = anAgent.color
                                            self.y=self.y+1
                                            anItem = SGLegendItem(self, anAgent.format, self.y, text, aColor, "none", "none")
                                            self.legendItems[aKeyOfGamespace].append(anItem)
                                            anItem.show()
                                            added_items.add(item_key)


            self.setMinimumSize(self.getSizeXGlobal(),10)"""
    

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
        for key in self.legendItems :
            for element in self.legendItems[key] :
                if len(element.texte)>len(longestWord):
                    longestWord=element.texte
        return longestWord
    
    def getSizeYGlobal(self):
        somme=30
        for key in self.legendItems :
            somme= somme+ 27*len(self.legendItems[key])
        return somme
    
    #Funtion to handle the zoom
    def zoomIn(self):
        """IN PROGRESS"""
        return True
    
    def zoomOut(self):
        """IN PROGRESS"""
        return True
    
    #To handle the drag of the Legend
    def mouseMoveEvent(self, e):
    
        if e.buttons() != Qt.LeftButton:
            return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())

        drag.exec_(Qt.MoveAction)
    
    
        
    #Drawing the Legend
    def paintEvent(self,event):
        if self.checkDisplay():
            if len(self.elementsPov)!=0:
                painter = QPainter() 
                painter.begin(self)
                painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
                painter.setPen(QPen(self.borderColor,1));
                #Draw the corner of the Legend
                self.setMinimumSize(self.getSizeXGlobal()+3, self.getSizeYGlobal()+3)
                painter.drawRect(0,0,self.getSizeXGlobal(), self.getSizeYGlobal())     


                painter.end()

        
    #Check if it have to be displayed
    def checkDisplay(self):
        return self.model.whoIAm==self.playerName or self.forceDisplay 

    #Get from wich grid an Agent is from to create the legend
    def getFromWich(self,anAgentName):
        """NOT TESTED"""
        for aGameSpace in self.model.gameSpaces :
            if isinstance(self.model.gameSpaces[aGameSpace],SGGrid) == True :
                aResult = self.model.gameSpaces[aGameSpace].getAgentOfTypeForLegend(anAgentName)
                if aResult != null:
    
                    return aResult
        
    
    
        

#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

#To add Povs in a legend
    def addToTheLegend(self,aListOfElement,aDictOfAcceptedValue={}):
        """NOT TESTED"""
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
                        #If we take all
                        if len(aDictOfAcceptedValue)==0:
                            self.elementsPov[aGameSpaceId][aPov][element][value]=aListOfElement[aGameSpaceId][aPov][element][value]
                        #If we apply a filter
                        else :
                            for anElement in aDictOfAcceptedValue:
                                if anElement == element :
                                    if len(self.elementsPov[aGameSpaceId][aPov][anElement])==0 :
                                        self.elementsPov[aGameSpaceId][aPov][anElement]={}
                                    if value in aDictOfAcceptedValue[anElement]:
                                        self.elementsPov[aGameSpaceId][aPov][element][value]=aListOfElement[aGameSpaceId][aPov][element][value]
            self.initUI()
        
        
#Adding the delete Button
    def addDeleteButton(self,name,elementsAllowed="all"):
        self.haveADeleteButton=True
        if "deleteButton" not in self.elementsPov:
            self.elementsPov["deleteButton"]={}
            
        if elementsAllowed == "all":
            for aGameSpaceId in self.elementsPov:
                for aPov in self.elementsPov[aGameSpaceId]:
                    self.elementsPov["deleteButton"][aPov]={name+" "+elementsAllowed:["all",Qt.yellow]}
        else:
            for aGameSpaceId in self.elementsPov:
                if aGameSpaceId != "agents" and aGameSpaceId!= "deleteButton":
                    for aPov in self.model.getGameSpace(aGameSpaceId).collectionOfCells.povs:
                        for elementOriginal in self.model.getGameSpace(aGameSpaceId).collectionOfCells.povs[aPov]:
                            for elementFound in elementsAllowed:
                                if elementFound == elementOriginal :
                                    if aPov not in self.elementsPov["deleteButton"]:
                                        self.elementsPov["deleteButton"][aPov]={}
                                    for val in elementsAllowed[elementFound] :
                                        self.elementsPov["deleteButton"][aPov][str(name)+" "+str(elementFound)+" "+str(val)]=[str(elementFound),Qt.yellow]
        self.initUI()
        
        

        
                    
