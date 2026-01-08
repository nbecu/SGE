from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGEntityView import SGEntityView
from mainClasses.SGEntity import SGEntity

class SGCellView(SGEntityView):
    """
    View class for SGCell - handles all UI and display logic for cells
    Separated from the model to enable Model-View architecture
    """
    
    def __init__(self, cell_model, parent=None):
        """
        Initialize the cell view
        
        Args:
            cell_model: The SGCell model instance
            parent: Parent widget
        """
        super().__init__(cell_model, parent)
        self.cell_model = cell_model
        
        # Cell-specific properties
        self.grid = cell_model.grid
        self.xCoord = cell_model.xCoord
        self.yCoord = cell_model.yCoord
        self.gap = cell_model.gap
        self.saveGap = cell_model.saveGap
        self.saveSize = cell_model.saveSize
        self.startXBase = cell_model.startXBase
        self.startYBase = cell_model.startYBase
        self.defaultImage = cell_model.defaultImage
        
        # Allow drops for agents
        self.setAcceptDrops(True)
    
    
    def paintEvent(self, event):
        """Paint the cell"""
        painter = QPainter()
        painter.begin(self)
        region = self.getRegion()
        image = self.getImage()
        
        # Check if the cell should be displayed based on the model
        if self.cell_model.isDisplay == True:
            if self.defaultImage != None:
                rect, scaledImage = self.rescaleImage(self.defaultImage)
                painter.setClipRegion(region)
                painter.drawPixmap(rect, scaledImage)
            elif image != None:
                rect, scaledImage = self.rescaleImage(image)
                painter.setClipRegion(region)
                painter.drawPixmap(rect, scaledImage)
            else: 
                painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
                
            penColorAndWidth = self.getBorderColorAndWidth()
            painter.setPen(QPen(penColorAndWidth['color'], penColorAndWidth['width']))
            
            # Use current grid values for size
            current_size = self.grid.size
            
            # In magnifier mode, don't recalculate position or move cell
            # Position is managed by grid's _updatePositionsForViewport()
            if hasattr(self.grid, 'zoomMode') and self.grid.zoomMode == "magnifier":
                # Just draw the cell, position is managed by grid
                if(self.shape == "square"):
                    painter.drawRect(0, 0, current_size, current_size)
                    self.setMinimumSize(current_size, current_size + 1)
                elif(self.shape == "hexagonal"):
                    self.setMinimumSize(current_size, current_size)
                    points = QPolygon([
                        QPoint(int(current_size / 2), 0),
                        QPoint(current_size, int(current_size / 4)),
                        QPoint(current_size, int(3 * current_size / 4)),
                        QPoint(int(current_size / 2), current_size),
                        QPoint(0, int(3 * current_size / 4)),
                        QPoint(0, int(current_size / 4))              
                    ])
                    painter.drawPolygon(points)
            else:
                # In resize mode, calculate position and move cell
                # Calculate position based on current zoom
                self.calculatePosition()
                    
                # Base of the gameBoard
                if(self.shape == "square"):
                    painter.drawRect(0, 0, current_size, current_size)
                    self.setMinimumSize(current_size, current_size + 1)
                    self.move(self.startX, self.startY)
                elif(self.shape == "hexagonal"):
                    self.setMinimumSize(current_size, current_size)
                    points = QPolygon([
                        QPoint(int(current_size / 2), 0),
                        QPoint(current_size, int(current_size / 4)),
                        QPoint(current_size, int(3 * current_size / 4)),
                        QPoint(int(current_size / 2), current_size),
                        QPoint(0, int(3 * current_size / 4)),
                        QPoint(0, int(current_size / 4))              
                    ])
                    painter.drawPolygon(points)
                    self.move(self.startX, self.startY)
        else:
            # Cell is deleted/hidden, don't draw anything
            pass
                        
        painter.end()
    
    def calculatePosition(self):
        """
        Calculate cell position based on coordinates and current zoom
        """
        # Always use current values from grid (not cached copies)
        grid_size = self.grid.size
        grid_gap = self.grid.gap
        grid_frame_margin = self.grid.frameMargin
        
        # Calculate base position with current zoom values
        self.startXBase = grid_frame_margin
        self.startYBase = grid_frame_margin
        
        # Calculate position for square grids
        if self.shape == "square":
            self.startX = int(self.startXBase + (self.xCoord - 1) * (grid_size + grid_gap) + grid_gap)
            self.startY = int(self.startYBase + (self.yCoord - 1) * (grid_size + grid_gap) + grid_gap)
        
        # Calculate position for hexagonal grids
        elif self.shape == "hexagonal":
            # For hexagonal grids, we need to account for the offset pattern
            # Hexagonal grids use "Pointy-top hex grid with even-r offset"
            
            # Base position calculation (similar to square)
            self.startX = int(self.startXBase + (self.xCoord - 1) * (grid_size + grid_gap) + grid_gap)
            
            # Hexagonal Y position: each row is offset by 3/4 of hexagon height + gap
            self.startY = int(self.startYBase + (self.yCoord - 1) * (grid_size * 0.75 + grid_gap) + grid_gap)
            
            
            # Apply hexagonal horizontal offset for even-r offset pattern
            if self.yCoord % 2 == 0:
                # Even rows: shift right by half a hexagon width
                self.startX = int(self.startX + grid_size / 2)
    
    def getRegion(self):
        """Get the region for the cell shape"""
        cellShape = self.type.shape
        current_size = self.grid.size  # Use current grid size
        
        if cellShape == "square":
            region = QRegion(0, 0, current_size, current_size)
        if cellShape == "hexagonal":
            points = QPolygon([
                QPoint(int(current_size / 2), 0),
                QPoint(current_size, int(current_size / 4)),
                QPoint(current_size, int(3 * current_size / 4)),
                QPoint(int(current_size / 2), current_size),
                QPoint(0, int(3 * current_size / 4)),
                QPoint(0, int(current_size / 4))              
            ])
            region = QRegion(points)
        return region

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        # Check for pan in magnifier mode (Shift + LeftButton) - forward to grid
        if (hasattr(self.grid, 'zoomMode') and self.grid.zoomMode == "magnifier" and 
            event.button() == Qt.LeftButton and 
            event.modifiers() & Qt.ShiftModifier):
            # Convert coordinates from cell to grid
            grid_pos = self.mapTo(self.grid, event.pos())
            # Create a new event with grid coordinates
            from PyQt5.QtGui import QMouseEvent
            grid_event = QMouseEvent(
                event.type(),
                grid_pos,
                event.button(),
                event.buttons(),
                event.modifiers()
            )
            # Forward to grid's mousePressEvent
            self.grid.mousePressEvent(grid_event)
            event.accept()
            return
        
        if event.button() == Qt.LeftButton:
            # Validate that the click is within the cell bounds
            click_pos = event.pos()
            
            # Use rect() with a small tolerance to account for any offset issues
            cell_rect = self.rect()
            tolerance = 2  # 2 pixels tolerance
            
            # Check if click is within the cell boundaries with tolerance
            if (click_pos.x() < -tolerance or click_pos.x() > cell_rect.width() + tolerance or 
                click_pos.y() < -tolerance or click_pos.y() > cell_rect.height() + tolerance):
                return  # Exit if click is outside cell bounds
            
            # First, try to find an action with directClick=True (priority over ControlPanel selection)
            selected_action = None
            try:
                currentPlayer = self.cell_model.model.getCurrentPlayer()
                if currentPlayer != "Admin":
                    # Use helper method to find authorized action with directClick=True
                    selected_action = currentPlayer.getAuthorizedActionWithDirectClick(self.cell_model)
            except (ValueError, AttributeError):
                # Current player not defined yet or not a valid player object, skip directClick
                pass
            
            # If no directClick action found, fall back to selected action from ControlPanel
            if selected_action is None:
                aLegendItem = self.cell_model.model.getSelectedLegendItem()
                selected_action = aLegendItem.gameAction if aLegendItem is not None else None
            
            if selected_action is None:
                return  # No action available
            
            # Check if this action was triggered via directClick
            action_was_directclick = (
                hasattr(selected_action, 'action_controler') and
                selected_action.action_controler.get("directClick") == True
            )
            
            # Note: We removed the isDisplay check to allow actions on deleted cells
            # This allows create actions to work on deleted cells
            
            # Use the gameAction system for ALL players (including Admin)
            selected_action.perform_with(self.cell_model)
            
            # If action was triggered via directClick, update ControlPanel selection
            if action_was_directclick:
                self._updateControlPanelSelection(selected_action)
            return

    def _updateControlPanelSelection(self, action):
        """
        Update the ControlPanel selection to reflect the action that was just executed via directClick
        
        Args:
            action: The game action that was just executed
        """
        try:
            currentPlayer = self.cell_model.model.getCurrentPlayer()
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
    
    def dropEvent(self, e):
        """Handle drop events for agent and tile movement"""
        e.acceptProposedAction()
        sourceView = e.source()

        # Check if it's an agent or a tile
        entity = None
        if hasattr(sourceView, 'agent_model'):
            entity = sourceView.agent_model
        elif hasattr(sourceView, 'tile_model'):
            entity = sourceView.tile_model
        else:
            # Fallback: assume it's already a model
            entity = sourceView

        # Delegate type checking to the model
        if not self.cell_model.shouldAcceptDropFrom(entity):
            return
        
        currentPlayer = self.cell_model.model.getCurrentPlayer()
    
        # Get authorized move action from player
        authorizedMoveAction = currentPlayer.getAuthorizedMoveActionForDrop(entity, self.cell_model)
        
        # Execute the move action if found
        if authorizedMoveAction is not None:
            authorizedMoveAction.perform_with(entity, self.cell_model)
            e.setDropAction(Qt.MoveAction)
            return

    def dragEnterEvent(self, e):
        """Handle drag enter events"""
        # This event is called during an agent drag 
        e.accept()

    def mouseMoveEvent(self, e):
        """Handle mouse move events to prevent cell dragging"""
        # Check for pan in magnifier mode (Shift + LeftButton) - forward to grid
        if (hasattr(self.grid, 'zoomMode') and self.grid.zoomMode == "magnifier" and 
            hasattr(self.grid, 'panning') and self.grid.panning and
            e.buttons() & Qt.LeftButton and e.modifiers() & Qt.ShiftModifier):
            # Convert coordinates from cell to grid
            grid_pos = self.mapTo(self.grid, e.pos())
            # Create a new event with grid coordinates
            from PyQt5.QtGui import QMouseEvent
            grid_event = QMouseEvent(
                e.type(),
                grid_pos,
                e.button(),
                e.buttons(),
                e.modifiers()
            )
            # Forward to grid's mouseMoveEvent
            self.grid.mouseMoveEvent(grid_event)
            e.accept()
            return
        
        # This method is used to prevent the drag of a cell
        if e.buttons() != Qt.LeftButton:
            return
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        # Check for pan in magnifier mode (Shift + LeftButton) - forward to grid
        if (hasattr(self.grid, 'zoomMode') and self.grid.zoomMode == "magnifier" and 
            hasattr(self.grid, 'panning') and self.grid.panning and
            event.button() == Qt.LeftButton and event.modifiers() & Qt.ShiftModifier):
            # Convert coordinates from cell to grid
            grid_pos = self.mapTo(self.grid, event.pos())
            # Create a new event with grid coordinates
            from PyQt5.QtGui import QMouseEvent
            grid_event = QMouseEvent(
                event.type(),
                grid_pos,
                event.button(),
                event.buttons(),
                event.modifiers()
            )
            # Forward to grid's mouseReleaseEvent
            self.grid.mouseReleaseEvent(grid_event)
            event.accept()
            return
