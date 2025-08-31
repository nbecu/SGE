from PyQt5.QtGui import *
from PyQt5.QtCore import *

from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGLegendItem import SGLegendItem

#Class who is responsible of the creation of a ControlPanel
#A ControlPanel is an interface that permits to operate the game actions of a player
class SGControlPanel(SGGameSpace):
    @classmethod #todo change to the normal way to create a ControlPanel
    def forPlayer(cls, aPlayer,panelTitle,backgroundColor=Qt.transparent,borderColor=Qt.black,defaultActionSelected=None):
        aModel=aPlayer.model
        aControlPanel = cls(aModel,0,60,0,0,backgroundColor=backgroundColor)
        aControlPanel.isLegend=False
        aControlPanel.isControlPanel=True
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
        self.legendItems = []
        self.heightOfLabels = 20
        anItem=SGLegendItem(self,'Title1',self.id) #self.id is equivalent to name
        
        # Filter out actions that can't be properly sorted (like model actions)
        sortableActions = []
        for action in gameActions:
            if hasattr(action, 'targetEntDef') and action.targetEntDef != 'model':
                sortableActions.append(action)
        
        # Sort actions by entity type and name
        sortedGameActions = sorted(sortableActions, key=lambda x: (0, x.targetEntDef.entityName) if x.targetEntDef.entityType() == 'Cell' else (1, x.targetEntDef.entityName))

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

    def isAdminLegend(self):
        """Check if this control panel belongs to an admin player"""
        return hasattr(self, 'player') and hasattr(self.player, 'isAdmin') and self.player.isAdmin


    def setActivation(self, aBoolean):
        previousValue = self.isActive
        self.isActive = aBoolean
        
        # case when it's just beeing activated
        if not previousValue and aBoolean and not self.selected and self.defaultSelection:
            self.selected = self.defaultSelection


    def isActiveAndSelected(self):
        return self.isActive and self.selected is not None

    #Function to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        listOfLengths = [len(item.text) for item in self.legendItems]
        listOfLengths.append(len(self.id))
        if len(listOfLengths)==0:
            return 250
        lMax= sorted(listOfLengths,reverse=True)[0]
        return lMax*12+10
    
    def getSizeX_fromAllWidgets(self):
        if self.legendItems:  # Vérifier si la liste n'est pas vide
            max_size_item = max(self.legendItems, key=lambda item: item.geometry().size().width())
            max_width = max_size_item.geometry().size().width()
        else:
            max_width = 30  # Ou une autre valeur par défaut
        return max_width + 10
    
    def getSizeYGlobal(self):
        return (self.heightOfLabels)*(len(self.legendItems)+1)

    #Drawing the Legend
    def paintEvent(self,event):
        if self.checkDisplay():
            painter = QPainter() 
            painter.begin(self)
            if self.isActive:
                painter.setBrush(QBrush(self.gs_aspect.getBackgroundColorValue(), Qt.SolidPattern))
            else:
                painter.setBrush(QBrush(Qt.darkGray, Qt.SolidPattern))
            painter.setPen(QPen(self.borderColor,1))
            #Draw the corner of the Legend
            # self.setMinimumSize(self.getSizeXGlobal()+3, self.getSizeYGlobal()+3)
            # painter.drawRect(0,0,self.getSizeXGlobal(), self.getSizeYGlobal())     
            self.setMinimumSize(self.getSizeX_fromAllWidgets(), self.getSizeYGlobal()+3)
            painter.drawRect(0,0,self.getSizeX_fromAllWidgets()-1, self.getSizeYGlobal())

            painter.end()

    #Check if it have to be displayed
    def checkDisplay(self):
        if self.playerName in self.model.users :
            return True
    

        
    #obsolete function
    # def checkViability(self,text):
    #     thePlayer=self.model.players[self.playerName]
    #     for action in thePlayer.gameActions:
    #         if isinstance(action,SGCreate) or isinstance(action,SGDelete): 
    #             if action.dictAttributs is not None: # case of att+val agents WITH attribut info in Action
    #                 stringAttributs = " : ".join([f"{key} : {value}" for key, value in action.dictAttributs.items()])
    #                 if stringAttributs in text : 
    #                     return True
    #     return False

    def mousePressEvent(self, QMouseEvent):
        """Handle mouse press events for control panel items"""
        if QMouseEvent.button() == Qt.LeftButton:
            # Check if current player can use this control panel
            if self.playerName != self.model.currentPlayerName:
                return # Exit because the currentPlayer cannot use this widget
            
            # Find the clicked item using childAt for more precise detection
            clickedItem = self.childAt(QMouseEvent.pos())
            
            # Check if the clicked item is a SGLegendItem and is in our legendItems list
            if clickedItem is None or not hasattr(clickedItem, 'gameAction') or clickedItem not in self.legendItems:
                return # No valid item clicked
            
            # Check if the clicked item is selectable (has gameAction)
            if not clickedItem.isSelectable():
                return # Exit because the item is not selectable (no gameAction)
            
            if self.selected == clickedItem:
                # Already selected - deselect
                self.selected = None
            else:
                # Selection of an item and suppression of already selected Item
                self.selected = clickedItem
            self.update()

    def updateWithSymbologies(self, listOfSymbologies):
        """Override to prevent ControlPanel from changing with symbology changes"""
        # ControlPanels should not change when symbology changes
        # They should maintain their gameAction display
        pass
   



    
    