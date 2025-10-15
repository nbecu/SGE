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
        
        # Apply initial stylesheet
        self.setStyleSheet(self.gs_aspect.getExtendedStyle())
        
        # Initialize theme aspects for different states
        self.inactive_aspect = SGAspect.inactive()
        self.haveADeleteButton = False
        # Paddings for panel rendering and item positioning
        self.topPadding = 8
        self.leftPadding = 10
        # Reduce right margin for this panel specifically
        try:
            self.rightMargin = 8
        except Exception:
            pass
        # Bottom padding to control space under last item
        self.bottomPadding = 3
        
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


    def initUI_withGameActions(self,gameActions):
        self.posYOfItems = 0
        self.legendItems = []
        # Vertical spacing between items; also controls top margin feel
        self.heightOfLabels = 22  # slightly larger to increase top margin perception
        anItem=SGLegendItem(self,'Title1',self.id) #self.id is equivalent to name
        # Ensure Title1 participates in width/size computations
        self.legendItems.append(anItem)
        
        # Filter out actions that can't be properly sorted (like model actions)
        sortableActions = []
        for action in gameActions:
            if hasattr(action, 'targetType') and action.targetType != 'model':
                sortableActions.append(action)
        
        # Sort actions by entity type and name
        sortedGameActions = sorted(sortableActions, key=lambda x: (0, x.targetType.name) if x.targetType.category() == 'Cell' else (1, x.targetType.name))

        lastEntDefTitle = ''
        for aGameAction in sortedGameActions:
            if "Move" == aGameAction.actionType and not aGameAction.setOnController or aGameAction.setControllerContextualMenu:
                continue
            if lastEntDefTitle != aGameAction.targetType.name:
                anItem=SGLegendItem(self,'Title2',aGameAction.targetType.name)
                self.legendItems.append(anItem)
                lastEntDefTitle = aGameAction.targetType.name
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
        """Compute content width from children min sizes (text-measured), not the previous geometry.

        This reduces the spurious extra right margin and adapts to text length.
        """
        try:
            if self.legendItems:
                widths = []
                for it in self.legendItems:
                    try:
                        w = it.minimumSize().width()
                    except Exception:
                        w = it.sizeHint().width()
                    widths.append(w)
                max_width = max(widths) if widths else 30
            else:
                max_width = 30
            return int(max_width)
        except Exception:
            return 60
    
    def getSizeYGlobal(self):
        return (self.heightOfLabels)*(len(self.legendItems)+1)

    #Drawing the Legend
    def paintEvent(self,event):
        if self.checkDisplay():
            painter = QPainter() 
            painter.begin(self)
            if self.isActive:
                bg_color = self.gs_aspect.getBackgroundColorValue()
                painter.setBrush(QBrush(bg_color, Qt.SolidPattern))
            else:
                # Use inactive theme instead of hardcoded color
                bg_color = self.inactive_aspect.getBackgroundColorValue()
                painter.setBrush(QBrush(bg_color, Qt.SolidPattern))
            painter.setPen(QPen(self.gs_aspect.getBorderColorValue(), self.gs_aspect.getBorderSize()))
            #Draw the corner of the Legend
            # self.setMinimumSize(self.getSizeXGlobal()+3, self.getSizeYGlobal()+3)
            # painter.drawRect(0,0,self.getSizeXGlobal(), self.getSizeYGlobal())
            # Compute width/height including paddings
            content_width = max(0, self.getSizeX_fromAllWidgets())
            drawn_width = int(self.leftPadding + content_width + max(0, getattr(self, 'rightMargin', 0)))
            # Height: use number of items (no extra +1 row) plus explicit bottom padding
            items_count = len(self.legendItems)
            content_height = int(self.heightOfLabels * items_count)
            drawn_height = int(self.topPadding + content_height + max(0, getattr(self, 'bottomPadding', 0)))
            self.setMinimumSize(drawn_width, drawn_height)
            painter.drawRect(0,0, drawn_width-1, drawn_height-1)

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
        self.setStyleSheet(self.gs_aspect.getExtendedStyle())
        self.update()
        
    def setBackgroundColor(self, color):
        """
        Set the background color of the control panel.
        
        Args:
            color (QColor or Qt.GlobalColor): The background color
        """
        self.gs_aspect.background_color = color
        self.setStyleSheet(self.gs_aspect.getExtendedStyle())
        self.update()
        
    def setBorderSize(self, size):
        """
        Set the border size of the control panel.
        
        Args:
            size (int): The border size in pixels
        """
        self.gs_aspect.border_size = size
        self.setStyleSheet(self.gs_aspect.getExtendedStyle())
        self.update()
        
    def setInactiveThemeColor(self, color):
        """
        Set the inactive theme background color.
        
        Args:
            color (QColor or Qt.GlobalColor): The inactive background color
        """
        self.inactive_aspect.background_color = color


    
    
    