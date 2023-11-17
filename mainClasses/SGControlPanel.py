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
#A ControlPanel is an interface that permits to operate the game actions of a player
class SGControlPanel(SGLegend):
    # def __init__(self, aPlayer,panelTitle,backgroundColor=Qt.transparent,borderColor=Qt.black):
    #     self.model=aPlayer.model
    #     self.copyOf__init__(self.model,0,60,0,0,true,backgroundColor)
    #     self.id=panelTitle
    #     self.player=aPlayer
    #     self.playerName=self.player.name
    #     self.legendItems=[]
    #     self.isActive=True
    #     self.selected = None # To handle the selection of an item in the legend
    #     self.borderColor=borderColor
    #     self.haveADeleteButton=False
    #     self.initUI_withGameActions(self.player.gameActions)

    @classmethod
    def forPlayer(cls, aPlayer,panelTitle,backgroundColor=Qt.transparent,borderColor=Qt.black):
        aModel=aPlayer.model
        aInstance = cls(aModel,backgroundColor)
        aInstance.id=panelTitle
        aInstance.player=aPlayer
        aInstance.playerName=aInstance.player.name
        aInstance.legendItems=[]
        aInstance.isActive=True
        aInstance.selected = None # To handle the selection of an item in the legend
        aInstance.borderColor=borderColor
        aInstance.haveADeleteButton=False
        aInstance.initUI_withGameActions(aInstance.player.gameActions)
        return aInstance


    def initUI_withGameActions(self,gameActions):
        self.posYOfItems = 0
        anItem=SGLegendItem(self,'Title1',self.id) #self.id is equivalent to name
        for aGameAction in gameActions:
            entDef = aGameAction.anObject
            anItem=SGLegendItem(self,'Title2',entDef.entityName)
            self.legendItems.append(anItem)
            #case of UpdateAction
            listOfLegendItemps = aGameAction.generateLegendItems(self)
            for anItem in listOfLegendItemps:
                self.legendItems.append(anItem)
            # for aAtt, aValue in aGameAction.dictNewValues.items():
            #     aColor = entDef.getColorOfFirstOccurenceOfAttAndValue(aAtt,aValue)
            #     anItem=SGLegendItem(self,'symbol',aAtt+'->'+str(aValue),entDef,aColor,aAtt,aValue,gameAction=aGameAction)
            #     self.legendItems.append(anItem)
        # anItem=SGLegendItem(self,'delete',"Delete","square",Qt.darkGray)
        # self.legendItems.append(anItem)

        for anItem in self.legendItems:
            anItem.show()
        self.setMinimumSize(self.getSizeXGlobal(),10)


    def showLegendItem(self, typeOfPov, aAttribut, aValue, color, aKeyOfGamespace, added_items, added_colors):
        # OBSOLETE.   SHOULD REMOVE
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
                if self.isActive:
                    painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
                else:
                    painter.setBrush(QBrush(Qt.darkGray, Qt.SolidPattern))
                painter.setPen(QPen(self.borderColor,1))
                #Draw the corner of the Legend
                self.setMinimumSize(self.getSizeXGlobal()+3, self.getSizeYGlobal()+3)
                painter.drawRect(0,0,self.getSizeXGlobal(), self.getSizeYGlobal())     

                painter.end()
