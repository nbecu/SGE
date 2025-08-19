from PyQt5.QtGui import *
from PyQt5.QtCore import *

from mainClasses.SGLegend import SGLegend
from mainClasses.SGLegendItem import SGLegendItem

#Class who is responsible of the creation of a ControlPanel
#A ControlPanel is an interface that permits to operate the game actions of a player
class SGControlPanel(SGLegend):
    @classmethod
    def forPlayer(cls, aPlayer,panelTitle,backgroundColor=Qt.transparent,borderColor=Qt.black,defaultActionSelected=None):
        aModel=aPlayer.model
        aControlPanel = cls(aModel,backgroundColor)
        aControlPanel.id=panelTitle
        aControlPanel.player=aPlayer
        aControlPanel.playerName=aControlPanel.player.name
        aControlPanel.legendItems=[]
        aControlPanel.isActive=False
        aControlPanel.selected = None # To handle the selection of an item in the legend
        aControlPanel.borderColor=borderColor
        aControlPanel.haveADeleteButton=False
        gameActions = aPlayer.gameActions
        aControlPanel.initUI_withGameActions(gameActions)
        if defaultActionSelected is not None:
            from mainClasses.gameAction.SGAbstractAction import SGAbstractAction
            if not isinstance(defaultActionSelected,SGAbstractAction): raise ValueError(f'defaultActionSelected should be gameAction but {defaultActionSelected} is not one')
            aControlPanel.defaultSelection = next((item for item in aControlPanel.legendItems if item.gameAction == defaultActionSelected)
                                                  ,None)  # None in case defaultActionSelected is not one of the game action of the controlPanel
        elif len(aControlPanel.getLegendItemsOfGameActions()) == 1 :
            aControlPanel.defaultSelection = aControlPanel.getLegendItemsOfGameActions()[0]
        else:
            aControlPanel.defaultSelection = None
        return aControlPanel


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

    def getLegendItemsOfGameActions(self):
        return [item for item in self.legendItems if item.gameAction is not None]

    def setActivation(self, aBoolean):
        previousValue = self.isActive
        self.isActive = aBoolean
        
        # case when it's just beeing activated
        if not previousValue and aBoolean and not self.selected and self.defaultSelection:
            self.selected = self.defaultSelection

        




    
    