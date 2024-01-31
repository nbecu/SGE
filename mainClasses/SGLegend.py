from typing import Hashable
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null, true

from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.SGCell import SGCell
from mainClasses.SGGrid import SGGrid
from mainClasses.SGAgent import SGAgent
from mainClasses.gameAction.SGDelete import SGDelete
from mainClasses.gameAction.SGUpdate import SGUpdate
from mainClasses.gameAction.SGCreate import SGCreate
from mainClasses.gameAction.SGMove import SGMove


#Class who is responsible of the Legend creation 
class SGLegend(SGGameSpace):
    def __init__(self, parent,backgroundColor=Qt.transparent):
        super().__init__(parent,0,60,0,0,true,backgroundColor)
    
    # basic init method. Use ex. SGLegend(parent).init1(model,name,elementPov,playerName,agents)
    def init1(self, model,name,elementPov,playerName,AgentList,showAgents=False,borderColor=Qt.black,legendType="global"):
        #OBSOLETE / To be removed
        self.id=name
        self.model=model
        self.elementsPov=elementPov
        self.AgentList=AgentList
        self.showAgents=showAgents
        self.playerName=playerName
        self.legendItems=[]
        self.borderColor=borderColor
        self.haveADeleteButton=False
        self.y=0
        self.legendType=legendType
        self.initUI()      
        return self
    
    def init2(self, model, legendName,listOfSymbologies,playerName,showAgents=False,borderColor=Qt.black):
        self.id=legendName
        self.model=model
        self.playerName=playerName
        self.showAgents=showAgents
        self.legendItems={}
        self.isActive=True
        self.selected = None # To handle the selection of an item in the legend
        self.borderColor=borderColor
        self.haveADeleteButton=False
        self.updateWithSymbologies(listOfSymbologies)
        return self

    def isActiveAndSelected(self):
        return self.isActive and self.selected is not None
    
    def isAdminLegend(self):
        return self.playerName=='Admin'
    
    def clearAllLegendItems(self):
        for aItem in self.legendItems:
            aItem.deleteLater()
        self.legendItems=[]
        
    def updateWithSymbologies(self,listOfSymbologies):
        self.clearAllLegendItems()
        self.listOfSymbologies=listOfSymbologies
        self.posYOfItems = 0
        anItem=SGLegendItem(self,'Title1',self.id) #self.id is equivalent to name
        for entDef, aDictOfSymbology in self.listOfSymbologies.items():
            anItem=SGLegendItem(self,'Title2',entDef.entityName)
            self.legendItems.append(anItem)
            # aDictOfSymbology is a dict with keys 'shape' and 'border'
            aShapeSymbology = aDictOfSymbology['shape']
            aBorderSymbology = aDictOfSymbology['border']
            if aShapeSymbology is None and aBorderSymbology is None:
                #In this case, it should return the default shape Symbology
                anItem=SGLegendItem(self,'symbol','default',entDef,entDef.defaultShapeColor)
                self.legendItems.append(anItem)
                continue
            if aShapeSymbology is not None:
                aAtt = list(entDef.povShapeColor[aShapeSymbology].keys())[0]
                dictSymbolNameAndColor= list(entDef.povShapeColor[aShapeSymbology].values())[0]
                for aSymbolName, aColor in dictSymbolNameAndColor.items():
                    anItem=SGLegendItem(self,'symbol',aSymbolName,entDef,aColor,aAtt,aSymbolName)
                    self.legendItems.append(anItem)
            if aBorderSymbology is not None:
                aPovBorderDef = entDef.povBorderColorAndWidth.get(aBorderSymbology)
                aAtt = list(aPovBorderDef.keys())[0]
                dictSymbolNameAndColorAndWidth= list(aPovBorderDef.values())[0]
                for aSymbolName, aDictColorAndWidth in dictSymbolNameAndColorAndWidth.items():
                    anItem=SGLegendItem(self,'symbol',aSymbolName,entDef,nameOfAttribut=aAtt,valueOfAttribut=aSymbolName,isBorderItem=True,borderColorAndWidth=aDictColorAndWidth)
                    self.legendItems.append(anItem)
        anItem=SGLegendItem(self,'delete',"Delete","square",Qt.darkGray)
        self.legendItems.append(anItem)

        for anItem in self.legendItems:
            anItem.show()
        self.setMinimumSize(self.getSizeXGlobal(),10)

    def initUI(self):
        if self.legendType=='player':
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
                if aKeyOfGamespace=="deleteButton" or aKeyOfGamespace=="deleteButtons":
                    if aKeyOfGamespace=="deleteButton":
                        added=set()
                        item_key = "Delete"
                        if item_key not in added:
                            self.y=self.y+1
                            anItem=SGLegendItem(self,"square",self.y,"Delete",Qt.darkGray,"playerDelete","playerDelete")
                            self.legendItems[aKeyOfGamespace].append(anItem)
                            added.add(item_key)
                            anItem.show()
                    if aKeyOfGamespace=="deleteButtons":
                        aList=self.elementsPov[aKeyOfGamespace]
                        added=set()
                        for aButton in aList:
                            item_key = aButton
                            split=item_key.split()
                            Species=self.model.getAgentsOfSpecie(split[1])
                            if  Species is not None:
                                shape=Species.format
                            else:
                                shape='square'
                            if item_key not in added:
                                self.y=self.y+1
                                anItem=SGLegendItem(self,shape,self.y,item_key,Qt.darkGray,"playerDelete","playerDelete")
                                self.legendItems[aKeyOfGamespace].append(anItem)
                                added.add(item_key)
                                anItem.show()

                else:
                    for entity in self.elementsPov[aKeyOfGamespace]:
                        if entity == 'cells':
                            added_items = set()
                            added_colors = []
                            grid=self.model.getGameSpaceByName(aKeyOfGamespace)
                            for aPov in self.elementsPov[aKeyOfGamespace]['cells'].keys():
                                if aPov in self.model.cellCollection[grid.id]["ColorPOV"].keys():
                                    currentPov=aPov
                                    for aAttribut in self.elementsPov[aKeyOfGamespace]['cells'][currentPov]:
                                        aValue=self.elementsPov[aKeyOfGamespace]['cells'][currentPov][aAttribut]
                                        color=self.model.cellCollection[grid.id]["ColorPOV"][currentPov][aAttribut][aValue]
                                        self.showLegendItem("ColorPOV", aAttribut, aValue, color, aKeyOfGamespace, added_items, added_colors)
                                if aPov in self.model.cellCollection[grid.id]["BorderPOV"].keys():
                                    currentPov=aPov
                                    for aAttribut in self.elementsPov[aKeyOfGamespace]['cells'][currentPov]:
                                        aDictValue=self.elementsPov[aKeyOfGamespace]['cells'][currentPov][aAttribut]
                                        if isinstance(aDictValue,dict):
                                            for aValue in list(aDictValue.keys()):
                                                color=self.model.cellCollection[grid.id]["BorderPOV"][currentPov][aAttribut][aValue]
                                                self.showLegendItem("BorderPOV", aAttribut, aValue, color, aKeyOfGamespace, added_items, added_colors)

                        elif entity == 'agents':
                            added_items = set()
                            for anAgent in self.AgentList:
                                for Species in self.elementsPov[aKeyOfGamespace]['agents'].keys():
                                    if anAgent.species == Species:
                                        for aPov in self.elementsPov[aKeyOfGamespace]['agents'][Species].keys():
                                            for anAtt in self.elementsPov[aKeyOfGamespace]['agents'][Species][aPov].keys():
                                                for aValue in self.elementsPov[aKeyOfGamespace]['agents'][Species][aPov][anAtt].keys():
                                                    item_key = Species + anAtt + aValue
                                                    if item_key not in added_items:
                                                        text = Species +' : '+ anAtt +' : ' + str(aValue)
                                                        if self.checkViability(text):
                                                            self.y = self.y + 1
                                                            aColor = self.elementsPov[aKeyOfGamespace]['agents'][Species][aPov][anAtt][aValue]
                                                            anItem = SGLegendItem(self, anAgent.format, self.y, text, aColor, aValue, anAtt)
                                                            added_items.add(item_key)
                                                            self.legendItems[aKeyOfGamespace].append(anItem)
                                                            anItem.show()
                                                
                if self.showAgents==True and aKeyOfGamespace !="deleteButton" and aKeyOfGamespace != "deleteButtons":
                    added_species=set()
                    for Species in self.model.getAgentSpeciesName():
                        item_key=Species
                        if self.checkSpecie(item_key,self.legendItems[aKeyOfGamespace]) and (item_key not in added_species):
                            aColor=self.model.agentSpecies[Species]["DefaultColor"]
                            text=Species
                            self.y=self.y+1
                            anItem=SGLegendItem(self,self.model.agentSpecies[Species]["Shape"],self.y,text,aColor,"empty","empty")
                            self.legendItems[aKeyOfGamespace].append(anItem)
                            anItem.show()
                            added_species.add(item_key)

            thePlayer=self.model.getPlayerObject(self.playerName)
            for item in self.legendItems[aKeyOfGamespace]:
                item.crossAction(thePlayer)
        self.setMinimumSize(self.getSizeXGlobal(),10)

    def showLegendItem(self, typeOfPov, aAttribut, aValue, color, aKeyOfGamespace, added_items, added_colors):
        item_key=aAttribut +' '+ str(aValue)
        if item_key not in added_items and color not in added_colors and color != Qt.transparent:
            self.y=self.y+1
            anItem=SGLegendItem(self,self.model.getGameSpaceByName(aKeyOfGamespace).format,self.y,aAttribut+" "+str(aValue),color,aValue,aAttribut)
            if typeOfPov == "BorderPOV" :
                anItem.border = True
            self.legendItems[aKeyOfGamespace].append(anItem)
            anItem.show()
            added_items.add(item_key)
            added_colors.append(color)


    #Funtion to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        listOfLengths = [len(item.text) for item in self.legendItems ]
        if len(listOfLengths)==0:
            return 250
        lMax= sorted(listOfLengths,reverse=True)[0]
        if self.haveADeleteButton :
            if lMax > len("delete"):
                return lMax*5+50
            else:
                return len("delete")*5+50
        else :
            return lMax*10+60
    
    def getLongest(self): #A priori Obsolete
        longestWord=""
        for key in self.legendItems :
            for element in self.legendItems[key] :
                if len(element.text)>len(longestWord):
                    longestWord=element.text
        return longestWord
    
    def getSizeYGlobal(self):
        return 25*(len(self.legendItems)+1)
    
    #Funtion to handle the zoom
    def zoomIn(self):
        """IN PROGRESS"""
        return True
    
    def zoomOut(self):
        """IN PROGRESS"""
        return True 
        
    #Drawing the Legend
    def paintEvent(self,event):
        if self.checkDisplay():
            # if len(self.elementsPov)!=0:
                painter = QPainter() 
                painter.begin(self)
                if self.isActive:
                    painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
                else:
                    painter.setBrush(QBrush(Qt.darkGray, Qt.SolidPattern))
                painter.setPen(QPen(self.borderColor,1))
                #Draw the corner of the Legend
                self.setMinimumSize(self.getSizeXGlobal()+3, self.getSizeYGlobal()+3)
                painter.drawRect(0,0,self.getSizeXGlobal(), self.getSizeYGlobal())     


                painter.end()

        
    #Check if it have to be displayed
    def checkDisplay(self):
        if self.playerName in self.model.users :
            return True
        

    #Get from wich grid an Agent is from to create the legend
    def getFromWich(self,anAgentName):
        """NOT TESTED"""
        for aGameSpace in self.model.gameSpaces :
            if isinstance(self.model.gameSpaces[aGameSpace],SGGrid) == True :
                aResult = self.model.gameSpaces[aGameSpace].getAgentOfTypeForLegend(anAgentName)
                if aResult != null:
    
                    return aResult
    
    def checkViability(self,text):
        thePlayer=self.model.players[self.playerName]
        for action in thePlayer.gameActions:
            if isinstance(action,SGCreate) or isinstance(action,SGDelete): 
                if action.dictAttributs is not None: # case of att+val agents WITH attribut info in Action
                    stringAttributs = " : ".join([f"{key} : {value}" for key, value in action.dictAttributs.items()])
                    if stringAttributs in text : 
                        return True
        return False
    
    def checkSpecie(self,item_key,items):
        for legendItem in items:
            if item_key in legendItem.text:
                return False
        return True
