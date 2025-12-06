from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog, QMessageBox, QDialog, QLabel, QVBoxLayout
from mainClasses.SGEventHandlerGuide import *

class SGEntityView(QtWidgets.QWidget, SGEventHandlerGuide):
    """
    View class for SGEntity - handles all UI and display logic
    Separated from the model to enable Model-View architecture
    """
    
    def __init__(self, entity_model, parent=None):
        """
        Initialize the entity view
        
        Args:
            entity_model: The SGEntity model instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.entity_model = entity_model
        self.type = entity_model.type
        self.id = entity_model.id
        self.privateID = entity_model.privateID
        self.model = entity_model.model
        self.shape = entity_model.shape
        self.size = entity_model.size
        self.borderColor = entity_model.borderColor
        self.isDisplay = entity_model.isDisplay
        
        # Define highlighting
        self.highlightEffect = None
        self.isHighlighted = False
        
        # Set the contextual and gameAction controller
        self.init_contextMenu()
    
    def getColor(self):
        """Get the color for display based on POV settings"""
        if self.isDisplay == False: 
            return Qt.transparent
            
        aChoosenPov = self.model.getCheckedSymbologyOfEntity(self.type.name)
        aPovDef = self.type.povShapeColor.get(aChoosenPov)
        aDefaultColor = self.type.defaultShapeColor
        return self.readColorFromPovDef(aPovDef, aDefaultColor)

    def getBorderColorAndWidth(self):
        """Get the border color and width for display"""
        if self.isDisplay == False: 
            return Qt.transparent
            
        aChoosenPov = self.model.getCheckedSymbologyOfEntity(self.type.name, borderSymbology=True)
        aBorderPovDef = self.type.povBorderColorAndWidth.get(aChoosenPov)
        aDefaultColor = self.type.defaultBorderColor
        aDefaultWidth = self.type.defaultBorderWidth
        return self.readColorAndWidthFromBorderPovDef(aBorderPovDef, aDefaultColor, aDefaultWidth)
    
    def getImage(self):
        """Get the image for display based on POV settings"""
        if self.isDisplay == False: 
            return None
            
        aChoosenPov = self.model.getCheckedSymbologyOfEntity(self.type.name)
        aPovDef = self.type.povShapeColor.get(aChoosenPov)
        if aPovDef is None: 
            return None
            
        aAtt = list(aPovDef.keys())[0]
        aDictOfValueAndImage = list(aPovDef.values())[0]
        aImage = aDictOfValueAndImage.get(self.entity_model.value(aAtt))     

        if aImage is not None and isinstance(aImage, QPixmap):
            return aImage 
        else:
            return None
    
    def rescaleImage(self, image):
        """Rescale image to fit entity size"""
        imageWidth = image.width()
        imageHeight = image.height()

        if imageWidth == 0 or imageHeight == 0: 
            raise ValueError('Image size is not valid')
            
        entityWidth = self.size
        entityHeight = self.size

        if (imageHeight / imageWidth) < (entityHeight / entityWidth):
            scaled_image = image.scaledToHeight(entityHeight, Qt.SmoothTransformation)
        else:
            scaled_image = image.scaledToWidth(entityWidth, Qt.SmoothTransformation)
            
        # Calculate target rectangle for drawing
        x_offset = (entityWidth - scaled_image.width()) // 2
        y_offset = (entityHeight - scaled_image.height()) // 2
        target_rect = QRect(x_offset, y_offset, scaled_image.width(), scaled_image.height())

        return target_rect, scaled_image

    def readColorFromPovDef(self, aPovDef, aDefaultColor):
        """Read color from POV definition"""
        if aPovDef is None: 
            return aDefaultColor
            
        aAtt = list(aPovDef.keys())[0]
        aDictOfValueAndColor = list(aPovDef.values())[0]
        aColor = aDictOfValueAndColor.get(self.entity_model.value(aAtt))
        return aColor if aColor is not None else aDefaultColor

    def readColorAndWidthFromBorderPovDef(self, aBorderPovDef, aDefaultColor, aDefaultWidth):
        """Read color and width from border POV definition"""
        if aBorderPovDef is None: 
            return {'color': aDefaultColor, 'width': aDefaultWidth}
            
        aAtt = list(aBorderPovDef.keys())[0]
        aDictOfValueAndColorWidth = list(aBorderPovDef.values())[0]
        
        # Check if the attribute exists in the model
        if not hasattr(self.entity_model, 'value') or not hasattr(self.entity_model, 'dictAttributes') or aAtt not in self.entity_model.dictAttributes:
            return {'color': aDefaultColor, 'width': aDefaultWidth}
            
        dictColorAndWidth = aDictOfValueAndColorWidth.get(self.entity_model.value(aAtt))
        
        if dictColorAndWidth is None:
            return {'color': aDefaultColor, 'width': aDefaultWidth}
        if not isinstance(dictColorAndWidth, dict): 
            raise ValueError('wrong format')
            
        return dictColorAndWidth

    # Handle the contextual menu and GameAction controller
    def init_contextMenu(self):
        """Initialize context menu"""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_contextMenu)
    
    def show_contextMenu(self, point):
        """Show context menu for the entity"""
        menu = QMenu(self)
        show_icons = getattr(self.model, 'showIconsInContextMenu', True)

        # Collect actions from current player (add these first - most important)
        actions_to_add = []
        try:
            player = self.model.getCurrentPlayer()
            if player != "Admin":        
                actions = player.getAllGameActionsOn(self.entity_model)
                for aAction in actions:
                    contextMenuEnabled = aAction.action_controler.get("contextMenu", False)
                    if contextMenuEnabled:
                        if aAction.checkAuthorization(self.entity_model):
                            actions_to_add.append(aAction)
        except ValueError:
            # Current player not defined - skip adding actions to menu
            # This can happen if setCurrentPlayer() was not called
            pass
        
        # Add action items with icons (actions first - most important)
        for aAction in actions_to_add:
            text = aAction.nameToDisplay
            if show_icons:
                # Get icon from the action class
                icon = getattr(aAction.__class__, 'context_menu_icon', "▶️ ")
                text = icon + text
            
            aMenuAction = QAction(text, self)
            aMenuAction.setCheckable(False)
            aMenuAction.triggered.connect(lambda _, a=aAction: a.perform_with(self.entity_model))
            menu.addAction(aMenuAction)

        # Add separator if we have both actions and attributes
        has_attributes = len(self.type.attributesToDisplayInContextualMenu) > 0
        if len(actions_to_add) > 0 and has_attributes:
            menu.addSeparator()

        # Add attribute information items (at the bottom - informational)
        for anItem in self.type.attributesToDisplayInContextualMenu:
            aAtt = anItem['att']
            aLabel = anItem['label']
            aValue = self.entity_model.value(aAtt)
            text = aLabel + str(aValue)
            if show_icons:
                text = "ℹ️ " + text  # Add info icon
            option = QAction(text, self)
            option.setEnabled(False)  # Make it non-clickable (informational only)
            menu.addAction(option)

        # Show menu if it's not empty
        # Note: point is in local coordinates relative to the widget
        # For tiles and agents, we should show the menu regardless of strict bounds checking
        # because the signal is only triggered when the click is on the widget
        if not menu.isEmpty():
            # Always show the menu - the signal customContextMenuRequested is only triggered
            # when the right-click occurs on the widget, so we can trust the point is valid
            menu.exec_(self.mapToGlobal(point))

    def getObjectIdentiferForJsonDumps(self):
        """Get object identifier for JSON serialization"""
        dict = {}
        dict['name'] = self.type.name
        dict['id'] = self.id
        return dict

    def isDeleted(self):
        """Check if entity is deleted"""
        return not self.isDisplay
    
    def _findAuthorizedMoveAction(self, entity_model):
        """
        Find an authorized Move action for the entity.
        
        This method searches for Move actions that:
        - Match the entity type
        - Are authorized for this specific entity (checkAuthorization passes)
        - Either have directClick=True OR are selected in ControlPanel
        
        Args:
            entity_model: The entity model (SGAgent or SGTile)
            
        Returns:
            SGMove: The first authorized Move action found, or None if none found
        """
        try:
            currentPlayer = entity_model.model.getCurrentPlayer()
            if currentPlayer == "Admin":
                return None
            
            entityDef = entity_model.type
            
            # Find Move action (for drag & drop)
            from mainClasses.gameAction.SGMove import SGMove
            for action in currentPlayer.gameActions:
                if (isinstance(action, SGMove) and
                    action.targetType == entityDef and
                    action.checkAuthorization(entity_model)):
                    # Check if directClick is enabled OR if action is selected in ControlPanel
                    aLegendItem = entity_model.model.getSelectedLegendItem()
                    is_selected = (aLegendItem is not None and aLegendItem.gameAction == action)
                    if (action.action_controler.get("directClick") == True or is_selected):
                        return action
        except (ValueError, AttributeError):
            # Current player not defined yet or not a valid player object, skip
            pass
        
        return None
    
    def _findAuthorizedClickAction(self, entity_model):
        """
        Find an authorized non-Move action for click events.
        
        This method searches for actions that:
        - Have directClick=True OR are selected in ControlPanel
        - Are not Move actions (Move is handled separately)
        - Are authorized for this specific entity (checkAuthorization passes)
        
        Args:
            entity_model: The entity model (SGAgent or SGTile)
            
        Returns:
            Action: The first authorized click action found, or None if none found
        """
        try:
            currentPlayer = entity_model.model.getCurrentPlayer()
            if currentPlayer == "Admin":
                return None
            
            # Find action with directClick=True (for click, like Activate, Flip, etc.)
            from mainClasses.gameAction.SGMove import SGMove
            click_action = currentPlayer.getAuthorizedActionWithDirectClick(entity_model)
            if click_action is not None:
                # Make sure it's not a Move action (already handled separately)
                if not isinstance(click_action, SGMove):
                    return click_action
            
            # Fall back to selected action from ControlPanel (if not Move)
            aLegendItem = entity_model.model.getSelectedLegendItem()
            if aLegendItem is not None:
                selected_action = aLegendItem.gameAction
                if selected_action is not None and not isinstance(selected_action, SGMove):
                    # Check authorization before returning
                    if selected_action.checkAuthorization(entity_model):
                        return selected_action
        except (ValueError, AttributeError):
            # Current player not defined yet or not a valid player object, skip
            pass
        
        return None
