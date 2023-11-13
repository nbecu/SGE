from typing import Hashable
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null, true

from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGLegend import SGLegend
from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.SGCell import SGCell
from mainClasses.SGGrid import SGGrid
from mainClasses.SGAgent import SGAgent
from mainClasses.gameAction.SGDelete import SGDelete
from mainClasses.gameAction.SGUpdate import SGUpdate
from mainClasses.gameAction.SGCreate import SGCreate
from mainClasses.gameAction.SGMove import SGMove


#Class who is responsible of the creation of a ControlPanel
#A ControlPanel is a interface that permits to operate the game actions of a player
class SGControlPanel(SGLegend):
    def __init__(self, aPlayer,panelTitle,backgroundColor=Qt.transparent,borderColor=Qt.black):
        self.model=aPlayer.model
        self.copyOf__init__(self.model,0,60,0,0,true,backgroundColor)
        self.id=panelTitle
        self.player=aPlayer
        self.playerName=self.player.name
        self.legendItems=[]
        self.isActive=True
        self.selected = None # To handle the selection of an item in the legend
        self.borderColor=borderColor
        self.haveADeleteButton=False
        self.initUI()

        
    def initUI(self):
        y = 0
        anItem=SGLegendItem(self,'Title1',y,self.id) #self.id is equivalent to name
        y+=1
        for aGameAction in self.player.gameActions:
            entDef = aGameAction.anObject
            anItem=SGLegendItem(self,'Title2',y,entDef.entityName)
            y +=1
            self.legendItems.append(anItem)
            #case of UpdateAction
            for aAtt, aValue in aGameAction.dictNewValues.items():
                aColor = entDef.getColorOfFirstOccurenceOfAttAndValue(aAtt,aValue)
                anItem=SGLegendItem(self,'symbol',y,aAtt+'->'+str(aValue),entDef,aColor,aAtt,aValue)
                y +=1
                self.legendItems.append(anItem)
        anItem=SGLegendItem(self,'delete',y,"Delete","square",Qt.darkGray)
        y +=1
        self.legendItems.append(anItem)

        for anItem in self.legendItems:
            anItem.show()
        self.setMinimumSize(self.getSizeXGlobal(),10)

    def initUI_OLD(self):
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
                            Species=self.model.getAgentSpecie(split[1])
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
                            grid=self.model.getGameSpace(aKeyOfGamespace)
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
            anItem=SGLegendItem(self,self.model.getGameSpace(aKeyOfGamespace).format,self.y,aAttribut+" "+str(aValue),color,aValue,aAttribut)
            if typeOfPov == "BorderPOV" :
                anItem.border = True
            self.legendItems[aKeyOfGamespace].append(anItem)
            anItem.show()
            added_items.add(item_key)
            added_colors.append(color)

    #Drawing the Legend
    def paintEvent(self,event):
        if self.checkDisplay():
            # if len(self.elementsPov)!=0:
                painter = QPainter() 
                painter.begin(self)
                if self.model.currentPlayer==self.playerName or self.playerName =="Admin":
                    painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
                else:
                    painter.setBrush(QBrush(Qt.darkGray, Qt.SolidPattern))
                painter.setPen(QPen(self.borderColor,1))
                #Draw the corner of the Legend
                self.setMinimumSize(self.getSizeXGlobal()+3, self.getSizeYGlobal()+3)
                painter.drawRect(0,0,self.getSizeXGlobal(), self.getSizeYGlobal())     


                painter.end()
