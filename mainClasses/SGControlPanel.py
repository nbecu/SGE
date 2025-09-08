from PyQt5.QtGui import *
from PyQt5.QtCore import *

from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.SGAspect import SGAspect

#Class who is responsible of the creation of a ControlPanel
#A ControlPanel is an interface that permits to operate the game actions of a player
class SGControlPanel(SGGameSpace):
    def __init__(self, aPlayer, panelTitle, backgroundColor=Qt.transparent, borderColor=Qt.black, defaultActionSelected=None):
        """
        Initialize a ControlPanel for a specific player.
        
        Args:
            aPlayer: The player who owns this control panel
            panelTitle: Title/name of the control panel
            backgroundColor: Background color (default: transparent)
            borderColor: Border color (default: black)
            defaultActionSelected: Default game action to select (optional)
        """
        # Initialize the parent SGGameSpace
        super().__init__(aPlayer.model, 0, 60, 0, 0, backgroundColor=backgroundColor)
        
        # Set control panel specific attributes
        self.isLegend = False
        self.isControlPanel = True
        self.id = panelTitle
        self.player = aPlayer
        self.playerName = self.player.name
        self.legendItems = []
        self.isActive = False
        self.selected = None  # To handle the selection of an item in the legend
        
        # Configure border using gs_aspect
        self.gs_aspect.border_color = borderColor
        self.gs_aspect.border_size = 1
        
        # Initialize theme aspects for different states
        self.inactive_aspect = SGAspect.inactive()
        self.haveADeleteButton = False
        
        # Initialize UI with game actions
        gameActions = aPlayer.gameActions
        self.initUI_withGameActions(gameActions)
        
        # Handle default action selection
        if defaultActionSelected is not None:
            from mainClasses.gameAction.SGAbstractAction import SGAbstractAction
            if not isinstance(defaultActionSelected, SGAbstractAction):
                raise ValueError(f'defaultActionSelected should be gameAction but {defaultActionSelected} is not one')
            self.defaultSelection = next((item for item in self.legendItems if item.gameAction == defaultActionSelected), None)
        elif len(self.getLegendItemsOfGameActions()) == 1:
            self.defaultSelection = self.getLegendItemsOfGameActions()[0]
        else:
            self.defaultSelection = None

    @classmethod
    def forPlayer(cls, aPlayer, panelTitle, backgroundColor=Qt.transparent, borderColor=Qt.black, defaultActionSelected=None):
        """
        Legacy class method for backward compatibility.
        Creates a ControlPanel using the new __init__ constructor.
        
        Args:
            aPlayer: The player who owns this control panel
            panelTitle: Title/name of the control panel
            backgroundColor: Background color (default: transparent)
            borderColor: Border color (default: black)
            defaultActionSelected: Default game action to select (optional)
            
        Returns:
            SGControlPanel: The created control panel instance
        """
        return cls(aPlayer, panelTitle, backgroundColor, borderColor, defaultActionSelected)


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

        self.update()  # Force repaint to reflect the new activation state

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
                # Use inactive theme instead of hardcoded color
                painter.setBrush(QBrush(self.inactive_aspect.getBackgroundColorValue(), Qt.SolidPattern))
            painter.setPen(QPen(self.gs_aspect.getBorderColorValue(), self.gs_aspect.getBorderSize()))
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
    


    def mousePressEvent(self, QMouseEvent):
        """Handle mouse press events for control panel items"""
        if QMouseEvent.button() == Qt.LeftButton:
            # Check if current player can use this control panel
            if self.playerName != self.model.currentPlayerName:
                # Still call parent for drag & drop functionality
                super().mousePressEvent(QMouseEvent)
                return # Exit because the currentPlayer cannot use this widget
            
            # Find the clicked item using childAt for more precise detection
            clickedItem = self.childAt(QMouseEvent.pos())
            
            # Check if the clicked item is a SGLegendItem and is in our legendItems list
            if clickedItem is None or not hasattr(clickedItem, 'gameAction') or clickedItem not in self.legendItems:
                # Still call parent for drag & drop functionality
                super().mousePressEvent(QMouseEvent)
                return # No valid item clicked
            
            # Check if the clicked item is selectable (has gameAction)
            if not clickedItem.isSelectable():
                # Still call parent for drag & drop functionality
                super().mousePressEvent(QMouseEvent)
                return # Exit because the item is not selectable (no gameAction)
            
            if self.selected == clickedItem:
                # Already selected - deselect
                self.selected = None
            else:
                # Selection of an item and suppression of already selected Item
                self.selected = clickedItem
            self.update()
        
        # Always call parent for drag & drop functionality
        super().mousePressEvent(QMouseEvent)

    def updateWithSymbologies(self, listOfSymbologies):
        """Override to prevent ControlPanel from changing with symbology changes"""
        # ControlPanels should not change when symbology changes
        # They should maintain their gameAction display
        pass

    # ============================================================================
    # MODELER METHODS
    # ============================================================================
    
    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================
    
    def setBorderColor(self, color):
        """
        Set the border color of the control panel.
        
        Args:
            color (QColor or Qt.GlobalColor): The border color
        """
        self.gs_aspect.border_color = color
        
    def setBorderSize(self, size):
        """
        Set the border size of the control panel.
        
        Args:
            size (int): The border size in pixels
        """
        self.gs_aspect.border_size = size
        
    def setInactiveThemeColor(self, color):
        """
        Set the inactive theme background color.
        
        Args:
            color (QColor or Qt.GlobalColor): The inactive background color
        """
        self.inactive_aspect.background_color = color


    
    
    