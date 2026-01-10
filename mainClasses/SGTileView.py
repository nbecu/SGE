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
        
        # saveSize is now read from model via property (no duplication)
        
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
        self.pending_move_action = None  # Store Move action for drag & drop
        self.pending_click_action = None  # Store non-Move action to execute on click
        
        # Calculate initial position
        self.getPositionInCell()
    
    def _shouldRenderTile(self):
        """
        Determine if this tile should be rendered based on stackRenderMode.
        
        Returns:
            tuple: (should_render: bool, offset_x: int, offset_y: int, stack_size: int)
                - should_render: True if tile should be rendered
                - offset_x: X offset for rendering (for offset mode)
                - offset_y: Y offset for rendering (for offset mode)
                - stack_size: Total number of tiles in the stack
        """
        if self.cell is None or not hasattr(self.cell, 'getStack'):
            return True, 0, 0, 1
        
        # Get the stack for this tile type
        stack = self.cell.getStack(self.tile_model.type)
        all_tiles = stack.tiles  # Already sorted by layer (lowest to highest)
        stack_size = len(all_tiles)
        
        if stack_size == 0:
            return True, 0, 0, 1
        
        render_mode = self.tile_model.type.stackRenderMode
        max_visible = self.tile_model.type.maxVisibleTiles
        
        if render_mode == "topOnly":
            # Only render if this is the top tile
            top_tile = stack.topTile()
            should_render = (top_tile is not None and top_tile == self.tile_model)
            return should_render, 0, 0, stack_size
        
        elif render_mode == "offset":
            # Render tiles with offset, but limit to maxVisibleTiles (top tiles)
            visible_tiles = all_tiles[-max_visible:] if stack_size > max_visible else all_tiles
            
            if self.tile_model not in visible_tiles:
                return False, 0, 0, stack_size
            
            # Calculate offset based on position in visible_tiles
            # visible_tiles is sorted from bottom to top, so index 0 is bottom, last is top
            index_in_visible = visible_tiles.index(self.tile_model)
            # Reverse index so top tile (last in list) has the largest offset
            reversed_index = len(visible_tiles) - 1 - index_in_visible
            # Offset: use configurable offset amount from tileType
            offset_amount = self.tile_model.type.stackOffsetAmount
            offset_x = reversed_index * offset_amount
            offset_y = reversed_index * offset_amount
            
            return True, offset_x, offset_y, stack_size
        
        else:
            # Default: render all tiles
            return True, 0, 0, stack_size
    
    def getPositionInCell(self):
        """
        Calculate the absolute position of the tile within its cell
        Similar to SGAgentView.updatePositionInEntity but for tiles
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
        # Use size from model (read via property)
        tile_size = self.size  # Property reads from model
        
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
        
        # Apply offset if needed (for offset rendering mode)
        self._applyOffsetIfNeeded()
        
        # Update the view position
        try:
            self.setGeometry(self.xCoord, self.yCoord, tile_size, tile_size)
        except RuntimeError:
            # Tile view has been deleted, ignore the error
            pass
    
    def _applyOffsetIfNeeded(self):
        """
        Apply geometric offset to tile position for offset rendering mode.
        This actually moves the widget position, not just the painter.
        """
        if self.cell is None or not hasattr(self.cell, 'getStack'):
            return
        
        # Get the stack for this tile type
        stack = self.cell.getStack(self.tile_model.type)
        all_tiles = stack.tiles  # Already sorted by layer (lowest to highest)
        stack_size = len(all_tiles)
        
        if stack_size == 0:
            return
        
        render_mode = self.tile_model.type.stackRenderMode
        max_visible = self.tile_model.type.maxVisibleTiles
        
        if render_mode == "offset":
            # Render tiles with offset, but limit to maxVisibleTiles (top tiles)
            visible_tiles = all_tiles[-max_visible:] if stack_size > max_visible else all_tiles
            
            if self.tile_model not in visible_tiles:
                return
            
            # Calculate offset based on position in visible_tiles
            # visible_tiles is sorted from bottom to top, so index 0 is bottom, last is top
            index_in_visible = visible_tiles.index(self.tile_model)
            # Reverse index so top tile (last in list) has the largest offset
            reversed_index = len(visible_tiles) - 1 - index_in_visible
            # Offset: use configurable offset amount from tileType
            offset_amount = self.tile_model.type.stackOffsetAmount
            offset_x = reversed_index * offset_amount
            offset_y = reversed_index * offset_amount
            
            # Apply offset to coordinates
            self.xCoord += offset_x
            self.yCoord += offset_y
    
    def updatePositionFromCell(self):
        """Update tile position when cell moves"""
        # Update the view's cell reference to match the model
        self.cell = self.tile_model.cell
        self.position = self.tile_model.position
        self.getPositionInCell()
    
    def paintEvent(self, event):
        """Paint the tile"""
        # Check if this tile should be rendered based on stackRenderMode
        should_render, offset_x, offset_y, stack_size = self._shouldRenderTile()
        
        if not should_render:
            # Don't render this tile (it's hidden by stackRenderMode)
            return
        
        painter = QPainter() 
        painter.begin(self)
        
        # Get image and color based on current face
        if self.tile_model.face == "front":
            image = self.frontImage if self.frontImage is not None else self.getImage()
            color = self.frontColor if self.frontColor is not None else self.getColor()
        else:  # back
            image = self.backImage if self.backImage is not None else self.getImage()
            color = self.backColor if self.backColor is not None else self.getColor()
        
        # Note: Offset is now applied geometrically in _applyOffsetIfNeeded()
        # No need to translate the painter anymore
        
        # Set clip region
        region = self.getRegion()
        painter.setClipRegion(region)
        
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
        tile_size = self.size  # Property reads from model
        
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
        
        # Draw stack counter if enabled (only on top tile)
        if self.tile_model.type.showCounter and stack_size > 1:
            # Check if this is the top tile
            stack = self.cell.getStack(self.tile_model.type)
            top_tile = stack.topTile()
            if top_tile is not None and top_tile == self.tile_model:
                # Draw counter text on top tile
                painter.setPen(QPen(Qt.black, 1))
                painter.setFont(QFont("Arial", max(8, tile_size // 6), QFont.Bold))
                counter_text = str(stack_size)
                text_rect = painter.fontMetrics().boundingRect(counter_text)
                
                # Position counter based on counterPosition setting
                counter_position = self.tile_model.type.counterPosition
                margin = 2
                
                if counter_position == "topRight":
                    text_x = tile_size - text_rect.width() - margin
                    text_y = text_rect.height() + margin
                    bg_x = text_x - 1
                    bg_y = 1
                elif counter_position == "topLeft":
                    text_x = margin
                    text_y = text_rect.height() + margin
                    bg_x = text_x - 1
                    bg_y = 1
                elif counter_position == "bottomRight":
                    text_x = tile_size - text_rect.width() - margin
                    text_y = tile_size - margin
                    bg_x = text_x - 1
                    bg_y = tile_size - text_rect.height() - 1
                elif counter_position == "bottomLeft":
                    text_x = margin
                    text_y = tile_size - margin
                    bg_x = text_x - 1
                    bg_y = tile_size - text_rect.height() - 1
                else:  # center
                    text_x = round((tile_size - text_rect.width()) / 2)
                    text_y = round((tile_size + text_rect.height()) / 2)
                    bg_x = text_x - 1
                    bg_y = text_y - text_rect.height() - 1
                
                # Draw background for text (white with slight transparency)
                bg_rect = QRect(int(bg_x), int(bg_y), text_rect.width() + 2, text_rect.height() + 2)
                painter.fillRect(bg_rect, QColor(255, 255, 255, 200))
                # Draw text
                painter.drawText(int(text_x), int(text_y), counter_text)
                
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
            # Let the parent handle right button clicks for context menu
            super().mousePressEvent(event)
            return
        
        # Check for pan in magnifier mode (Shift + LeftButton) - forward to grid
        if self._forwardPanEventToGrid(event, self.grid, 'press'):
            return
        
        # Only handle left button clicks
        if event.button() == Qt.LeftButton:
            # Reset drag state
            self.dragging = True
            self.drag_occurred = False
            self.press_position = event.pos()
            self.pending_move_action = None
            self.pending_click_action = None
            
            # Validate that the click is within the tile bounds
            click_pos = event.pos()
            tile_rect = self.rect()
            tolerance = 2  # 2 pixels tolerance
            
            # Check if click is within the tile boundaries with tolerance
            if (click_pos.x() < -tolerance or click_pos.x() > tile_rect.width() + tolerance or 
                click_pos.y() < -tolerance or click_pos.y() > tile_rect.height() + tolerance):
                return  # Exit if click is outside tile bounds
            
            # Find authorized Move action using helper method (same as agents)
            self.pending_move_action = self._findAuthorizedMoveAction(self.tile_model)
            
            # Find authorized click action using helper method (same as agents)
            self.pending_click_action = self._findAuthorizedClickAction(self.tile_model)
            
            # If no actions available, return
            if self.pending_move_action is None and self.pending_click_action is None:
                return
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        # Check for pan in magnifier mode (Shift + LeftButton) - forward to grid
        if self._forwardPanEventToGrid(event, self.grid, 'release'):
            return
        
        if event.button() == Qt.LeftButton:
            # If no drag occurred and we have a pending click action, execute it
            if not self.drag_occurred and self.pending_click_action is not None:
                # Check if this action was triggered via directClick
                action_was_directclick = (
                    hasattr(self.pending_click_action, 'action_controler') and
                    self.pending_click_action.action_controler.get("directClick") == True
                )
                
                # Execute the action
                self.pending_click_action.perform_with(self.tile_model)
                
                # If action was triggered via directClick, update ControlPanel selection
                if action_was_directclick:
                    self._updateControlPanelSelection(self.pending_click_action)
            
            # Reset state
            self.dragging = False
            self.pending_move_action = None
            self.pending_click_action = None
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
        # Check for pan in magnifier mode (Shift + LeftButton) - forward to grid
        if self._forwardPanEventToGrid(e, self.grid, 'move'):
            return
        
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

        # Use pending_move_action that was set in mousePressEvent (already authorized)
        # This matches the behavior of agents
        if self.pending_move_action is None:
            return  # No Move action available for drag
        
        move_action = self.pending_move_action
        
        # Mark that a drag is occurring
        self.drag_occurred = True
        
        # If Move action was triggered via directClick, update ControlPanel selection
        if (hasattr(move_action, 'action_controler') and
            move_action.action_controler.get("directClick") == True):
            self._updateControlPanelSelection(move_action)

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
    
    def dragEnterEvent(self, e):
        """Handle drag enter events"""
        e.acceptProposedAction()

    def dropEvent(self, e):    
        """Handle drop events"""
        # Reset dragging state when drop occurs
        self.dragging = False
        
        if hasattr(e.source(), 'tile_model') and self.tile_model.cell is not None:
            # Specific case: forward the drop to the cell
            self.tile_model.cell.dropEvent(e)
        else:
            # Fallback: delegate the drop handling to the parent model
            self.tile_model.model.dropEvent(e)
    
    def updateFromModel(self):
        """Update view properties from model"""
        if self.tile_model:
            # size and saveSize are now read from model via properties (no manual sync needed)
            self.frontImage = self.tile_model.frontImage
            self.backImage = self.tile_model.backImage
            self.frontColor = self.tile_model.frontColor
            self.backColor = self.tile_model.backColor
            self.layer = self.tile_model.layer
            self.position = self.tile_model.position
            self.update()
    

