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
        sortedGameActions = sorted(gameActions, key=lambda x: (0, x.targetEntDef.entityName) if x.targetEntDef.entityType() == 'Cell' else (1, x.targetEntDef.entityName))

        lastEntDefTitle = ''
        for aGameAction in sortedGameActions:
            if lastEntDefTitle != aGameAction.targetEntDef.entityName:
                anItem=SGLegendItem(self,'Title2',aGameAction.targetEntDef.entityName)
                self.legendItems.append(anItem)
                lastEntDefTitle = aGameAction.targetEntDef.entityName
            #case of UpdateAction
            listOfLegendItems = aGameAction.generateLegendItems(self)
            for anItem in listOfLegendItems:
                self.legendItems.append(anItem)

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
