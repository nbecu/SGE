from PyQt6.QtGui import *
from PyQt6.QtCore import *
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

    # ------------------------------------------------------------------
    # Background image helper
    # ------------------------------------------------------------------
    def _drawBackgroundImagePortion(self, painter, cell_x, cell_y, cell_size,
                                    mode='stretch', zoom=1.0, viewportX=0, viewportY=0):
        """Draw the grid's background image portion that covers this cell.

        Qt6 clips the parent's paintEvent to exclude child widget areas, so
        transparent cells must paint their own background slice.

        In magnifier zoom mode, this respects the viewport offset and zoom level to ensure
        transparent cells show the same background image portion that would appear in those
        positions if the grid were scrolled and zoomed.

        Args:
            painter: QPainter for drawing
            cell_x: Cell position X in widget coordinates (after zoom/viewport transform)
            cell_y: Cell position Y in widget coordinates (after zoom/viewport transform)
            cell_size: Cell size in pixels
            mode: Background image mode ('stretch', 'cover', 'contain')
            zoom: Current zoom level (1.0 if no zoom)
            viewportX: Viewport offset X in grid coordinates
            viewportY: Viewport offset Y in grid coordinates
        """
        bg_pixmap = self.grid.getBackgroundImagePixmap()
        if bg_pixmap is None or bg_pixmap.isNull():
            return

        grid_w = self.grid.width()
        grid_h = self.grid.height()
        if grid_w <= 0 or grid_h <= 0:
            return

        img_w, img_h = bg_pixmap.width(), bg_pixmap.height()
        frame_margin = self.grid.frameMargin if hasattr(self.grid, 'frameMargin') else 0

        # Calculate base position in grid coordinate space (same logic as _updatePositionsForViewport)
        # This avoids rounding errors from converting widget coordinates
        base_x = 0
        base_y = 0

        if self.grid.cellShape == "square":
            grid_cell_x = base_x + (self.xCoord - 1) * (self.grid.saveSize + self.grid.saveGap) + self.grid.saveGap
            grid_cell_y = base_y + (self.yCoord - 1) * (self.grid.saveSize + self.grid.saveGap) + self.grid.saveGap
        elif self.grid.cellShape == "hexagonal":
            grid_cell_x = base_x + (self.xCoord - 1) * (self.grid.saveSize + self.grid.saveGap) + self.grid.saveGap
            hex_factor = self.grid._get_hexagonal_vertical_factor()
            hex_height = self.grid.saveSize * hex_factor
            grid_cell_y = base_y + (self.yCoord - 1) * (hex_height + self.grid.saveGap) + self.grid.saveGap
            if self.yCoord % 2 == 0:
                grid_cell_x += self.grid.saveSize / 2
        else:
            # Fallback: convert from widget coordinates
            grid_cell_x = (cell_x - frame_margin) / zoom + viewportX if zoom != 1.0 else cell_x
            grid_cell_y = (cell_y - frame_margin) / zoom + viewportY if zoom != 1.0 else cell_y

        grid_cell_size = self.grid.saveSize

        # Calculate base region based on mode (same logic as SGGrid.paintEvent)
        base_region_x = 0
        base_region_y = 0
        base_region_w = img_w
        base_region_h = img_h

        if mode == 'cover':
            # Cover mode: scale to cover, centered (crop from center)
            scale = max(grid_w / img_w, grid_h / img_h)
            scaled_w = int(img_w * scale)
            scaled_h = int(img_h * scale)
            offset_x = (scaled_w - grid_w) // 2
            offset_y = (scaled_h - grid_h) // 2
            base_region_x = int(offset_x / scale)
            base_region_y = int(offset_y / scale)
            base_region_w = int(grid_w / scale)
            base_region_h = int(grid_h / scale)

        elif mode == 'contain':
            # Contain mode: scale to fit, may have margins
            # base_region is entire image
            base_region_x = 0
            base_region_y = 0
            base_region_w = img_w
            base_region_h = img_h

        # Calculate grid bounds for proportional mapping
        bounds_w = self.grid.getGridBoundsWidth() if hasattr(self.grid, 'getGridBoundsWidth') else grid_w
        bounds_h = self.grid.getGridBoundsHeight() if hasattr(self.grid, 'getGridBoundsHeight') else grid_h

        # Calculate source region with viewport awareness
        if bounds_w > 0 and bounds_h > 0:
            # Map grid coordinates to base_region
            portion_x = int(grid_cell_x * base_region_w / bounds_w)
            portion_y = int(grid_cell_y * base_region_h / bounds_h)
            portion_w = max(1, int(grid_cell_size * base_region_w / bounds_w))
            portion_h = max(1, int(grid_cell_size * base_region_h / bounds_h))
        else:
            # Fallback to simple proportional sampling
            portion_x = int(grid_cell_x * base_region_w / grid_w) if grid_w > 0 else 0
            portion_y = int(grid_cell_y * base_region_h / grid_h) if grid_h > 0 else 0
            portion_w = max(1, int(grid_cell_size * base_region_w / grid_w)) if grid_w > 0 else base_region_w
            portion_h = max(1, int(grid_cell_size * base_region_h / grid_h)) if grid_h > 0 else base_region_h

        # Clamp portion to stay within base_region bounds
        portion_w = min(portion_w, base_region_w - portion_x)
        portion_h = min(portion_h, base_region_h - portion_y)

        # Convert to image coordinates
        src_x = base_region_x + portion_x
        src_y = base_region_y + portion_y
        src_w = portion_w
        src_h = portion_h

        # Clamp to image bounds
        src_x = max(0, min(src_x, img_w - 1))
        src_y = max(0, min(src_y, img_h - 1))
        src_w = min(src_w, img_w - src_x)
        src_h = min(src_h, img_h - src_y)

        if src_w > 0 and src_h > 0:
            painter.drawPixmap(
                QRect(0, 0, cell_size, cell_size),
                bg_pixmap,
                QRect(src_x, src_y, src_w, src_h),
            )

    def paintEvent(self, event):
        """Paint the cell"""
        painter = QPainter()
        painter.begin(self)
        region = self.getRegion()
        image = self.getImage()
        is_transparent = False

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
                color = self.getColor()
                qcolor = color if isinstance(color, QColor) else QColor(color)
                is_transparent = qcolor.alpha() == 0
                if not is_transparent:
                    painter.setBrush(QBrush(color, Qt.SolidPattern))
                # For transparent cells the brush is set to NoBrush below,
                # after calculatePosition() gives us the correct cell_x/cell_y.

            penColorAndWidth = self.getBorderColorAndWidth()
            painter.setPen(QPen(penColorAndWidth['color'], penColorAndWidth['width']))

            # Use current grid values for size
            current_size = self.grid.size

            # In magnifier mode, don't recalculate position or move cell
            # Position is managed by grid's _updatePositionsForViewport()
            if hasattr(self.grid, 'zoomMode') and self.grid.zoomMode == "magnifier":
                if is_transparent:
                    pos = self.pos()
                    mode = self.grid.gs_aspect.background_image_mode or 'stretch'
                    zoom = self.grid.zoom if hasattr(self.grid, 'zoom') else 1.0
                    viewportX = self.grid.viewportX if hasattr(self.grid, 'viewportX') else 0
                    viewportY = self.grid.viewportY if hasattr(self.grid, 'viewportY') else 0
                    self._drawBackgroundImagePortion(painter, pos.x(), pos.y(), current_size,
                                                      mode, zoom, viewportX, viewportY)
                    painter.setBrush(Qt.NoBrush)
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
                # In resize mode, calculate position first (needed for bg image sampling)
                self.calculatePosition()
                if is_transparent:
                    mode = self.grid.gs_aspect.background_image_mode or 'stretch'
                    self._drawBackgroundImagePortion(
                        painter, self.startX, self.startY, current_size, mode)
                    painter.setBrush(Qt.NoBrush)

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
            
            # Hexagonal Y position: use fixed factor (same as SGGrid calculations)
            # This ensures consistency with grid height calculations and prevents vertical spacing issues
            hex_factor = self.grid._get_hexagonal_vertical_factor()
            hex_height = grid_size * hex_factor
            self.startY = int(self.startYBase + (self.yCoord - 1) * (hex_height + grid_gap) + grid_gap)
            
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
        if self._forwardPanEventToGrid(event, self.grid, 'press'):
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
        if self._forwardPanEventToGrid(e, self.grid, 'move'):
            return
        
        # This method is used to prevent the drag of a cell
        if e.buttons() != Qt.LeftButton:
            return
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        # Check for pan in magnifier mode (Shift + LeftButton) - forward to grid
        if self._forwardPanEventToGrid(event, self.grid, 'release'):
            return
