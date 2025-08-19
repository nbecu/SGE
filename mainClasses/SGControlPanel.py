from PyQt5.QtGui import *
from PyQt5.QtCore import *

from mainClasses.SGLegend import SGLegend
from mainClasses.SGLegendItem import SGLegendItem


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
            if "Move" == aGameAction.actionType and not aGameAction.setOnController or aGameAction.setControllerContextualMenu:
                continue
            if lastEntDefTitle != aGameAction.targetEntDef.entityName:
                anItem=SGLegendItem(self,'Title2',aGameAction.targetEntDef.entityName)
                self.legendItems.append(anItem)
                lastEntDefTitle = aGameAction.targetEntDef.entityName
            #case of ModifyAction
            listOfLegendItems = aGameAction.generateLegendItems(self)
            if listOfLegendItems is not None:
                for anItem in listOfLegendItems :
                    self.legendItems.append(anItem)

        for anItem in self.legendItems:
            anItem.show()
        self.setMinimumSize(self.getSizeXGlobal(),10)

    
    