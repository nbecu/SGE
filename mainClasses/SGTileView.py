from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog, QMessageBox, QDialog, QLabel, QVBoxLayout, QToolTip
from PyQt5.QtGui import QCursor, QDrag
from PyQt5.QtCore import QMimeData
from mainClasses.SGEntityView import SGEntityView
import random

class SGTileView(SGEntityView):
    """
    View class for SGTile - handles all UI and display logic for tiles
    Separated from the model to enable Model-View architecture
    """
    
    def __init__(self, tile_model, parent=None):
        """
        Initialize the tile view
        
        Args:
            tile_model: The SGTile model instance
            parent: Parent widget (should be the grid)
        """
        super().__init__(tile_model, parent)
        self.tile_model = tile_model
        
        # Type identification attributes
        self.isEntity = True
        self.isCell = False
        self.isAgent = False
        self.isTile = True
        
        # Tile-specific properties
        self.cell = tile_model.cell
        self.position = tile_model.position
        self.frontImage = tile_model.frontImage
        self.backImage = tile_model.backImage
        self.frontColor = tile_model.frontColor
        self.backColor = tile_model.backColor
        self.layer = tile_model.layer
        
        # Initialize position coordinates
        self.xCoord = 0
        self.yCoord = 0
        
        # Save reference size for zoom calculations
        self.saveSize = self.size
        
        # Get grid parent for positioning
        self.grid = None
        if self.cell and hasattr(self.cell, 'grid'):
            self.grid = self.cell.grid
        elif parent and hasattr(parent, 'grid'):
            self.grid = parent.grid
        
        # Allow drops
        self.setAcceptDrops(True)
        
        # Mouse interaction state for distinguishing click vs drag
        self.dragging = False
        self.drag_occurred = False  # Flag to track if a drag actually happened
        self.press_position = None  # Store initial mouse press position
        self.pending_action = None  # Store action to execute on click (if not Move)
        
        # Calculate initial position
        self.getPositionInCell()
    
    def getPositionInCell(self):
        """
        Calculate the absolute position of the tile within its cell
        Similar to SGAgentView.getPositionInEntity but for tiles
        """
        if self.cell is None or not hasattr(self.cell, 'view'):
            return
        
        current_cell = self.cell
        cell_view = current_cell.view
        
        if cell_view is None:
            return
        
        # Get cell position and size
        cell_x = cell_view.x()
        cell_y = cell_view.y()
        cell_size = self.grid.size if self.grid else current_cell.saveSize
        
        # Calculate relative position based on position attribute
        # Use size from model (updated by zoom)
        tile_size = self.entity_model.size if hasattr(self.entity_model, 'size') else self.size
        
        if self.position == "full":
            # Tile covers the entire cell
            relX = 0
            relY = 0
            tile_size = cell_size
        elif self.position == "center":
            relX = (cell_size - tile_size) / 2
            relY = (cell_size - tile_size) / 2
        elif self.position == "topLeft":
            relX = 0
            relY = 0
        elif self.position == "topRight":
            relX = cell_size - tile_size
            relY = 0
        elif self.position == "bottomLeft":
            relX = 0
            relY = cell_size - tile_size
        elif self.position == "bottomRight":
            relX = cell_size - tile_size
            relY = cell_size - tile_size
        else:
            # Default to center
            relX = (cell_size - tile_size) / 2
            relY = (cell_size - tile_size) / 2
        
        # Calculate absolute position
        self.xCoord = cell_x + round(relX)
        self.yCoord = cell_y + round(relY)
        
        # Update the view position
        try:
            self.setGeometry(self.xCoord, self.yCoord, tile_size, tile_size)
        except RuntimeError:
            # Tile view has been deleted, ignore the error
            pass
    
    def updatePositionFromCell(self):
        """Update tile position when cell moves"""
        # Update the view's cell reference to match the model
        self.cell = self.tile_model.cell
        self.position = self.tile_model.position
        self.getPositionInCell()
    
    def paintEvent(self, event):
        """Paint the tile"""
        painter = QPainter() 
        painter.begin(self)
        region = self.getRegion()
        painter.setClipRegion(region)
        
        # Get image and color based on current face
        if self.tile_model.face == "front":
            image = self.frontImage if self.frontImage is not None else self.getImage()
            color = self.frontColor if self.frontColor is not None else self.getColor()
        else:  # back
            image = self.backImage if self.backImage is not None else self.getImage()
            color = self.backColor if self.backColor is not None else self.getColor()
        
        # Draw image if available
        if image is not None:
            if isinstance(image, QPixmap):
                if image.width() == 0 or image.height() == 0: 
                    raise ValueError(f'Image size is not valid for {self.privateID}')
                rect, scaledImage = self.rescaleImage(image)
                painter.drawPixmap(rect, scaledImage)
            else:
                # If image is a string path, try to load it
                # For now, fall back to color
                painter.setBrush(QBrush(color, Qt.SolidPattern))
        else:
            painter.setBrush(QBrush(color, Qt.SolidPattern))
        
        # Get border color and width
        penColorAndWidth = self.getBorderColorAndWidth()
        painter.setPen(QPen(penColorAndWidth['color'], penColorAndWidth['width']))
        
        # Get tile shape from type
        tileShape = self.type.shape
        x = self.xCoord
        y = self.yCoord
        # Use size from model (updated by zoom)
        tile_size = self.entity_model.size if hasattr(self.entity_model, 'size') else self.size
        
        if self.isDisplay == True:
            if tileShape == "rectTile" or tileShape == "imageTile":
                self.setGeometry(x, y, tile_size, tile_size)
                if tileShape == "rectTile":
                    painter.drawRect(0, 0, tile_size, tile_size)
                elif tileShape == "imageTile":
                    # For imageTile, if no image was drawn, draw rectangle with color
                    if image is None or (isinstance(image, QPixmap) and image.isNull()):
                        painter.drawRect(0, 0, tile_size, tile_size)
                    # If image was drawn, we're done (image already drawn above)
            elif tileShape == "circleTile":
                self.setGeometry(x, y, tile_size, tile_size)
                painter.drawEllipse(0, 0, tile_size, tile_size)
            elif tileShape == "ellipseTile":
                self.setGeometry(x, y, tile_size, round(tile_size / 2))
                painter.drawEllipse(0, 0, tile_size, round(tile_size / 2))
            else:
                # Default to rectangle
                self.setGeometry(x, y, tile_size, tile_size)
                painter.drawRect(0, 0, tile_size, tile_size)
                
        painter.end()
    
    def getRegion(self):
        """Get the clipping region for the tile"""
        return QRegion(0, 0, self.size, self.size)
    
    def mousePressEvent(self, event):
        """Handle mouse press events on tiles"""
        # IMPORTANT: For right button clicks, always call super() FIRST to allow context menu to work
        # The context menu signal is triggered by Qt before mousePressEvent, but we need to ensure
        # the event is properly propagated
        if event.button() == Qt.RightButton:
            print(f"[SGTileView] Right button click detected on tile {self.tile_model.id}")
            # Let the parent handle right button clicks for context menu
            super().mousePressEvent(event)
            return
        
        # Only handle left button clicks
        if event.button() == Qt.LeftButton:
            # Reset drag state
            self.dragging = True
            self.drag_occurred = False
            self.press_position = event.pos()
            self.pending_action = None
            
            # Validate that the click is within the tile bounds
            click_pos = event.pos()
            tile_rect = self.rect()
            tolerance = 2  # 2 pixels tolerance
            
            # Check if click is within the tile boundaries with tolerance
            if (click_pos.x() < -tolerance or click_pos.x() > tile_rect.width() + tolerance or 
                click_pos.y() < -tolerance or click_pos.y() > tile_rect.height() + tolerance):
                return  # Exit if click is outside tile bounds
            
            # First, try to find an action with directClick=True (priority over ControlPanel selection)
            selected_action = None
            try:
                currentPlayer = self.tile_model.model.getCurrentPlayer()
                if currentPlayer != "Admin":
                    # Use helper method to find authorized action with directClick=True
                    selected_action = currentPlayer.getAuthorizedActionWithDirectClick(self.tile_model)
            except (ValueError, AttributeError):
                # Current player not defined yet or not a valid player object, skip directClick
                pass
            
            # If no directClick action found, fall back to selected action from ControlPanel
            if selected_action is None:
                aLegendItem = self.tile_model.model.getSelectedLegendItem()
                selected_action = aLegendItem.gameAction if aLegendItem is not None else None
            
            if selected_action is None:
                return  # No action available
            
            # Use the gameAction system for ALL players (including Admin)
            # Check if the action is a Move action (tiles can be moved via drag & drop)
            from mainClasses.gameAction.SGMove import SGMove
            if isinstance(selected_action, SGMove):
                # For Move actions, allow drag & drop (like agents)
                # Don't execute the action here, let drag & drop handle it
                # Store the action for potential use in mouseMoveEvent
                self.pending_action = selected_action
                return
            
            # For other actions (like Flip), store the action to execute on release
            # This allows us to distinguish between click and drag
            self.pending_action = selected_action
            return
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.LeftButton:
            # If no drag occurred and we have a pending action (non-Move), execute it
            if not self.drag_occurred and self.pending_action is not None:
                from mainClasses.gameAction.SGMove import SGMove
                # Only execute if it's not a Move action (Move is handled by drag & drop)
                if not isinstance(self.pending_action, SGMove):
                    # Check if this action was triggered via directClick
                    action_was_directclick = (
                        hasattr(self.pending_action, 'action_controler') and
                        self.pending_action.action_controler.get("directClick") == True
                    )
                    
                    # Execute the action
                    self.pending_action.perform_with(self.tile_model)
                    
                    # If action was triggered via directClick, update ControlPanel selection
                    if action_was_directclick:
                        self._updateControlPanelSelection(self.pending_action)
            
            # Reset state
            self.dragging = False
            self.pending_action = None
            self.press_position = None
    
    def _updateControlPanelSelection(self, action):
        """
        Update the ControlPanel selection to reflect the action that was just executed via directClick
        
        Args:
            action: The game action that was just executed
        """
        try:
            currentPlayer = self.tile_model.model.getCurrentPlayer()
            if currentPlayer is None or currentPlayer == "Admin":
                return
            
            # Find the ControlPanel for the current player
            controlPanel = currentPlayer.controlPanel
            if controlPanel is None:
                return
            
            # Find the SGLegendItem corresponding to this action
            legend_item = next(
                (item for item in controlPanel.legendItems 
                 if hasattr(item, 'gameAction') and item.gameAction == action),
                None
            )
            
            # Update the selection
            if legend_item is not None:
                controlPanel.selected = legend_item
                controlPanel.update()  # Refresh the display
        except (ValueError, AttributeError):
            # Current player not defined or other error, skip update
            pass
    
    def mouseMoveEvent(self, e):
        """Handle mouse move events for dragging tiles"""
        if e.buttons() != Qt.LeftButton:
            # If no button is pressed, reset dragging state
            if self.dragging:
                self.dragging = False
            return

        # Check if we've moved enough to start a drag operation
        # Use QApplication.startDragDistance() to determine minimum movement
        from PyQt5.QtWidgets import QApplication
        if self.press_position is None:
            return
        distance = (e.pos() - self.press_position).manhattanLength()
        if distance < QApplication.startDragDistance():
            # Not enough movement yet, wait for more
            return

        # If pending_action is a non-Move action (like Flip with directClick=True),
        # prevent drag from occurring - the action will execute on mouseReleaseEvent instead
        from mainClasses.gameAction.SGMove import SGMove
        if self.pending_action is not None and not isinstance(self.pending_action, SGMove):
            # Don't allow drag for non-Move actions - they should execute on click release
            return

        # Try to find a Move action (Move actions use drag & drop)
        move_action = None
        
        # First check pending_action (from selected action in ControlPanel)
        if self.pending_action is not None and isinstance(self.pending_action, SGMove):
            move_action = self.pending_action
        else:
            # If no pending action or not Move, try to find Move actions with directClick=True
            # This allows automatic drag & drop only if directClick is enabled
            try:
                currentPlayer = self.tile_model.model.getCurrentPlayer()
                if currentPlayer != "Admin":
                    entityDef = self.tile_model.type
                    for action in currentPlayer.gameActions:
                        if (isinstance(action, SGMove) and
                            action.targetType == entityDef):
                            # Only allow automatic drag & drop if directClick is True
                            # If directClick is False, the action must be selected in ControlPanel
                            if action.action_controler.get("directClick") == True:
                                move_action = action
                                break
            except (ValueError, AttributeError):
                # Current player not defined yet or not a valid player object, skip
                pass
        
        if move_action is None:
            return  # No Move action available for drag
        
        # Mark that a drag is occurring
        self.drag_occurred = True
        self.pending_action = move_action  # Store for dropEvent

        mimeData = QMimeData()
        drag = QDrag(self)
        drag.setMimeData(mimeData)

        # Take a snapshot of the widget (the tile)
        pixmap = self.grab()

        # Make the pixmap semi-transparent
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QColor(0, 0, 0, 128))  # 128 = 50% opacity
        painter.end()

        # Set the pixmap as the drag preview
        drag.setPixmap(pixmap)

        # Keep the cursor aligned with the click point
        drag.setHotSpot(e.pos())

        # Start the drag operation
        result = drag.exec_(Qt.CopyAction | Qt.MoveAction)
        
        # Reset dragging state after drag operation completes
        self.dragging = False
    
    def updateFromModel(self):
        """Update view properties from model"""
        if self.tile_model:
            self.size = self.tile_model.size  # Update size from model (for zoom)
            self.saveSize = self.tile_model.saveSize
            self.frontImage = self.tile_model.frontImage
            self.backImage = self.tile_model.backImage
            self.frontColor = self.tile_model.frontColor
            self.backColor = self.tile_model.backColor
            self.layer = self.tile_model.layer
            self.position = self.tile_model.position
            self.update()
    
    # ============================================================================
    # ZOOM METHODS
    # ============================================================================
    
    def updateZoom(self, zoom_factor):
        """
        Update tile zoom based on zoom factor (like SGAgentView)
        
        Args:
            zoom_factor: The zoom factor to apply
        """
        # Calculate zoomed size from reference value
        self.size = round(self.saveSize * zoom_factor)
        # Update position based on new size
        self.updatePositionFromCell()
        self.update()

