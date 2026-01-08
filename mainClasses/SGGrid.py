from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGModel import *

# Class who is responsible of the grid creation
class SGGrid(SGGameSpace):
    def __init__(self, parent, name, columns=10, rows=10,cellShape="square", gap=3, size=30, aColor=None, moveable=True, backGroundImage=None,neighborhood='moore',boundaries='open', zoomMode="resize"):
        super().__init__(parent, 0, 60, 0, 0)
        # Type identification attributes
        self.isAGrid = True
        # Basic initialize
        self.zoom = 1
        self.model = parent
        self.id = name
        self.columns = columns
        self.rows = rows
        self.cellShape = cellShape
        self.gap = gap
        self.size = size
        self.moveable = moveable
        self.neighborhood = neighborhood
        self.boundary_condition = boundaries
        self.countPaintEvent=0
        self.frameMargin = 8

        self.currentPOV = {'Cell': {}, 'Agent': {}}

        self.saveGap = gap
        self.saveSize = size

        self.startXBase = 0
        self.startYBase = 0
        
        # Owners of the grid (can be a list of players or a single player)
        self.owners = []
        
        # Zoom mode: "resize" (default) or "magnifier"
        self.zoomMode = zoomMode
        # Viewport for magnifier mode (position of visible area in grid coordinates)
        self.viewportX = 0  # X offset of viewport in grid coordinates
        self.viewportY = 0  # Y offset of viewport in grid coordinates
        # Pan state for magnifier mode
        self.panning = False
        self.panStartX = 0
        self.panStartY = 0
        self.panViewportStartX = 0
        self.panViewportStartY = 0
        # Flag to prevent viewport reset during operations
        self._viewport_locked = False
        # Store original widget size for magnifier mode
        # Initialize with base size (will be set properly in updateGridSize if needed)
        if self.cellShape == "square":
            self.originalWidth = int(self.columns * self.saveSize + (self.columns + 1) * self.saveGap + 1) + 2 * self.frameMargin
            self.originalHeight = int(self.rows * self.saveSize + (self.rows + 1) * self.saveGap) + 1 + 2 * self.frameMargin
        elif self.cellShape == "hexagonal":
            adaptive_factor = self._calculate_hexagonal_adaptive_factor()
            hex_height = self.saveSize * adaptive_factor
            self.originalWidth = int(self.columns * self.saveSize + self.columns * self.saveGap + self.saveSize / 2 + 2 * self.frameMargin)
            self.originalHeight = int((self.rows - 1) * (hex_height + self.saveGap) + hex_height + 2 * self.frameMargin)
        else:
            self.originalWidth = None
            self.originalHeight = None

        if aColor != "None":
            self.setColor(aColor)
        # Store background image via gs_aspect (supports both QPixmap and file path)
        if backGroundImage is not None:
            self.setBackgroundImage(backGroundImage)
        
        # If in magnifier mode, set fixed size immediately
        if self.zoomMode == "magnifier":
            self.setFixedSize(self.originalWidth, self.originalHeight)
    
    # Drawing the game board with the cell
    def paintEvent(self, event): 
        self.countPaintEvent += 1
        painter = QPainter()
        painter.begin(self)
        # Enable antialiasing for better border rendering, especially for dashed lines
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        # In magnifier mode, set clipping to widget bounds to prevent rendering outside
        # TEMPORARILY DISABLED: Check if clipping is hiding the border
        # if self.zoomMode == "magnifier":
        #     # Clip to the visible area (excluding frame margin) for paintEvent drawing
        #     clip_rect = QRect(self.frameMargin, self.frameMargin, 
        #                      self.width() - 2 * self.frameMargin, 
        #                      self.height() - 2 * self.frameMargin)
        #     painter.setClipRect(clip_rect)
        
        # Background: prefer image (via gs_aspect), else color/pattern with transparency handling
        bg_pixmap = self.getBackgroundImagePixmap()
        if bg_pixmap is not None:
            rect = QRect(0, 0, self.width(), self.height())
            painter.drawPixmap(rect, bg_pixmap)
        else:
            if self.isActive:
                bg = self.gs_aspect.getBackgroundColorValue()
                painter.setBrush(QBrush(bg, Qt.SolidPattern) if bg.alpha() != 0 else Qt.NoBrush)
            else:
                painter.setBrush(QBrush(self.gs_aspect.getBackgroundColorValue_whenDisactivated(), self.gs_aspect.getBrushPattern_whenDisactivated()))

        # Pen with border style mapping
        pen = QPen(self.gs_aspect.getBorderColorValue(), self.gs_aspect.getBorderSize())
        style_map = {
            'solid': Qt.SolidLine,
            'dotted': Qt.DotLine,
            'dashed': Qt.DashLine,
            'double': Qt.SolidLine,
            'groove': Qt.SolidLine,
            'ridge': Qt.SolidLine,
            'inset': Qt.SolidLine,
        }
        bs = getattr(self.gs_aspect, 'border_style', None)
        if isinstance(bs, str) and bs.lower() in style_map:
            pen.setStyle(style_map[bs.lower()])
        painter.setPen(pen)
        # Base of the gameBoard
        # Only update widget size in paintEvent if NOT in magnifier mode
        # In magnifier mode, size is managed by updateGridSize()
        if self.zoomMode != "magnifier":
            if (self.cellShape == "square"):
                # We redefine the minimum size of the widget
                self.setMinimumSize(int(self.columns*self.size+(self.columns+1) * self.gap+1)+2*self.frameMargin,
                                    int(self.rows*self.size+(self.rows+1)*self.gap)+1+2*self.frameMargin)
            elif (self.cellShape == "hexagonal"):
                #Note: The hexagonal grid is "Pointy-top hex grid with even-r offset".
                # Width: columns * size + columns * gap + half hexagon for offset + frame margins
                # Height: rows * (size * 0.75) + gap + frame margins
                new_width = int(self.columns * self.size + self.columns * self.gap + self.size / 2 + 2 * self.frameMargin)
                # Mathematical calculation for "Pointy-top hex grid with even-r offset"
                adaptive_factor = self._calculate_hexagonal_adaptive_factor()
                hex_height = self.size * adaptive_factor  # Correct height for pointy-top hexagones
                new_height = int((self.rows - 1) * (hex_height + self.gap) + hex_height + 2 * self.frameMargin)
                self.setFixedSize(new_width, new_height)
        radius = getattr(self.gs_aspect, 'border_radius', None) or 0
        # In magnifier mode, use originalWidth/originalHeight (same values used for setFixedSize)
        # instead of self.width()/height() to ensure perfect alignment and avoid rendering artifacts
        # In resize mode, use minimumWidth/Height which are updated in paintEvent
        if self.zoomMode == "magnifier":
            border_width = int(self.originalWidth - 1)
            border_height = int(self.originalHeight - 1)
        else:
            border_width = int(self.minimumWidth() - 1)
            border_height = int(self.minimumHeight() - 1)
        
        if radius > 0:
            painter.drawRoundedRect(0, 0, border_width, border_height, radius, radius)
        else:
            painter.drawRect(0, 0, border_width, border_height)
        
        # In magnifier mode, we clip cells individually in _updatePositionsForViewport()
        # We don't use setMask() on the grid itself to avoid masking the border
        # Individual cell masks are applied in _updatePositionsForViewport()
        if self.zoomMode != "magnifier":
            # In resize mode, remove any existing mask from cells
            # (cells handle their own clipping in resize mode)
            pass
        
        painter.end()

    def _calculate_hexagonal_adaptive_factor(self):
        """
        Calculate adaptive factor for hexagonal grid height calculation.
        Based on number of rows to prevent clipping with few rows.
        
        Returns:
            float: Adaptive factor for hex_height calculation
        """
        if self.rows >= 10:
            return 0.78  # Stable value for grids with many rows
        else:
            return 0.78 + abs(10 - self.rows) * 0.025  # Progressive growth for few rows

    # ============================================================================
    # ZOOM FUNCTIONALITY
    # ============================================================================
    
    def wheelEvent(self, event):
        """
        Handle mouse wheel events for zoom functionality
        """
        # Only zoom if mouse is over this grid
        if self.rect().contains(event.pos()):
            # Get wheel delta (positive = up, negative = down)
            delta = event.angleDelta().y()
            
            if self.zoomMode == "magnifier":
                # Magnifier mode: zoom centered on mouse position
                mouse_pos = event.pos()
                if delta > 0:
                    self.newZoomIn(mouse_pos=mouse_pos)
                elif delta < 0:
                    self.newZoomOut(mouse_pos=mouse_pos)
            else:
                # Resize mode: standard zoom behavior
                if delta > 0:
                    self.newZoomIn()
                elif delta < 0:
                    self.newZoomOut()
            
            # Accept the event to prevent it from propagating
            event.accept()
        else:
            # Let the event propagate if mouse is not over this grid
            event.ignore()
    
    def newZoomIn(self, mouse_pos=None):
        """
        Zoom in the grid by increasing zoom factor
        
        Args:
            mouse_pos (QPoint, optional): Mouse position for magnifier mode (zoom centered on mouse)
        """
        old_zoom = self.zoom
        self.zoom = min(self.zoom * 1.1, 3.0)  # Cap at 3x zoom
        
        if self.zoomMode == "magnifier" and mouse_pos is not None:
            # Adjust viewport to keep mouse position fixed
            self._adjustViewportForZoom(old_zoom, self.zoom, mouse_pos)
        
        self.updateGridSize()
        self.update()
    
    def newZoomOut(self, mouse_pos=None):
        """
        Zoom out the grid by decreasing zoom factor
        
        Args:
            mouse_pos (QPoint, optional): Mouse position for magnifier mode (zoom centered on mouse)
        """
        old_zoom = self.zoom
        
        # In magnifier mode, minimum zoom is 1.0 (no zoom out if already at 1.0)
        if self.zoomMode == "magnifier":
            if self.zoom <= 1.0:
                return  # Already at minimum zoom
            self.zoom = max(self.zoom * 0.9, 1.0)  # Cap at 1.0x zoom
        else:
            self.zoom = max(self.zoom * 0.9, 0.3)  # Cap at 0.3x zoom for resize mode
        
        if self.zoomMode == "magnifier" and mouse_pos is not None:
            # Adjust viewport to keep mouse position fixed
            self._adjustViewportForZoom(old_zoom, self.zoom, mouse_pos)
        
        self.updateGridSize()
        self.update()
    
    def setZoomLevel(self, zoom_level, center_on_mouse=None):
        """
        Set specific zoom level
        
        Args:
            zoom_level (float): Zoom level to set (clamped between 0.3 and 3.0, or 1.0 and 3.0 for magnifier)
            center_on_mouse (QPoint, optional): For magnifier mode, center zoom on this mouse position
        """
        old_zoom = self.zoom
        # In magnifier mode, minimum zoom is 1.0
        if self.zoomMode == "magnifier":
            self.zoom = max(1.0, min(zoom_level, 3.0))  # Clamp between 1.0 and 3.0
        else:
            self.zoom = max(0.3, min(zoom_level, 3.0))  # Clamp between 0.3 and 3.0
        
        if self.zoomMode == "magnifier" and center_on_mouse is not None:
            self._adjustViewportForZoom(old_zoom, self.zoom, center_on_mouse)
        
        self.updateGridSize()
        self.update()
    
    def resetZoom(self):
        """
        Reset zoom to 1.0
        """
        self.zoom = 1.0
        if self.zoomMode == "magnifier":
            # Reset viewport to center
            self._resetViewport()
        self.updateGridSize()
        self.update()
    
    def _adjustViewportForZoom(self, old_zoom, new_zoom, mouse_pos):
        """
        Adjust viewport position to keep mouse position fixed during zoom
        
        Args:
            old_zoom (float): Previous zoom level
            new_zoom (float): New zoom level
            mouse_pos (QPoint): Mouse position in widget coordinates
        """
        if old_zoom == 0:
            return
        
        # Convert mouse position to grid coordinates
        grid_x = (mouse_pos.x() - self.frameMargin) / old_zoom + self.viewportX
        grid_y = (mouse_pos.y() - self.frameMargin) / old_zoom + self.viewportY
        
        # Calculate new viewport position to keep grid_x, grid_y under mouse
        self.viewportX = grid_x - (mouse_pos.x() - self.frameMargin) / new_zoom
        self.viewportY = grid_y - (mouse_pos.y() - self.frameMargin) / new_zoom
        
        # Clamp viewport to grid boundaries
        self._clampViewport()
    
    def _resetViewport(self):
        """Reset viewport to center of grid"""
        # Don't reset if viewport is locked (e.g., during pan)
        if hasattr(self, '_viewport_locked') and self._viewport_locked:
            return
        
        # getSizeXGlobal() and getSizeYGlobal() return dimensions WITHOUT frameMargin
        # (except getSizeYGlobal() which includes it, but we'll handle that)
        total_width = self.getSizeXGlobal()  # Without frameMargin
        # getSizeYGlobal() includes frameMargin, so subtract it for consistency
        total_height = self.getSizeYGlobal() - 2 * self.frameMargin  # Remove frameMargin for consistency
        
        # Use actual widget size if available, otherwise use original size
        widget_width = self.width() if self.width() > 0 else (self.originalWidth - 2 * self.frameMargin)
        widget_height = self.height() if self.height() > 0 else (self.originalHeight - 2 * self.frameMargin)
        
        # Adjust for frame margin (content area only)
        widget_width = widget_width - 2 * self.frameMargin
        widget_height = widget_height - 2 * self.frameMargin
        
        # Center viewport (all in coordinate space without frameMargin)
        self.viewportX = max(0, (total_width - widget_width / self.zoom) / 2)
        self.viewportY = max(0, (total_height - widget_height / self.zoom) / 2)
        
        self._clampViewport()
    
    def _clampViewport(self):
        """Clamp viewport to grid boundaries"""
        # getSizeXGlobal() returns without frameMargin, getSizeYGlobal() includes it
        total_width = self.getSizeXGlobal()  # Without frameMargin
        total_height = self.getSizeYGlobal() - 2 * self.frameMargin  # Remove frameMargin for consistency
        widget_width = self.width() - 2 * self.frameMargin
        widget_height = self.height() - 2 * self.frameMargin
        
        # Calculate maximum viewport position (all in coordinate space without frameMargin)
        # The viewport should not allow cells to extend beyond the visible area
        # When zoomed, visible_width = widget_width / zoom, so max_viewport = total_width - visible_width
        visible_width = widget_width / self.zoom
        visible_height = widget_height / self.zoom
        max_viewport_x = max(0, total_width - visible_width)
        max_viewport_y = max(0, total_height - visible_height)
        
        # Clamp viewport to ensure no cells extend beyond boundaries
        self.viewportX = max(0, min(self.viewportX, max_viewport_x))
        self.viewportY = max(0, min(self.viewportY, max_viewport_y))
    
    def _updatePositionsForViewport(self):
        """Update positions of all cells and agents based on viewport"""
        if self.zoomMode != "magnifier":
            return
        
        # Update all cells - first calculate their base positions, then apply viewport transform
        for cell in self.getCells():
            # Ensure cell has a view before processing
            if not hasattr(cell, 'view') or cell.view is None:
                continue
            
            # Calculate base position using same logic as calculatePosition but with saveSize/saveGap
            # This gives us the position in "grid coordinate space" (unzoomed, WITHOUT frameMargin)
            # frameMargin will be added only once at the end for widget coordinates
            # This matches getSizeXGlobal() and getSizeYGlobal() which don't include frameMargin
            base_x = 0
            base_y = 0
            
            if self.cellShape == "square":
                grid_x = base_x + (cell.xCoord - 1) * (self.saveSize + self.saveGap) + self.saveGap
                grid_y = base_y + (cell.yCoord - 1) * (self.saveSize + self.saveGap) + self.saveGap
            elif self.cellShape == "hexagonal":
                grid_x = base_x + (cell.xCoord - 1) * (self.saveSize + self.saveGap) + self.saveGap
                adaptive_factor = self._calculate_hexagonal_adaptive_factor()
                hex_height = self.saveSize * adaptive_factor
                grid_y = base_y + (cell.yCoord - 1) * (hex_height + self.saveGap) + self.saveGap
                if cell.yCoord % 2 == 0:
                    grid_x += self.saveSize / 2
            
            # Transform from grid coordinates to widget coordinates with viewport and zoom
            # viewportX and viewportY are in grid coordinate space (without frameMargin, matching getSizeXGlobal)
            # Add frameMargin only once at the end for widget coordinates
            widget_x = (grid_x - self.viewportX) * self.zoom + self.frameMargin
            widget_y = (grid_y - self.viewportY) * self.zoom + self.frameMargin
            
            # Calculate visible area bounds
            visible_left = self.frameMargin
            visible_right = self.width() - self.frameMargin
            visible_top = self.frameMargin
            visible_bottom = self.height() - self.frameMargin
            
            # Calculate cell bounds
            cell_size = self.size  # Current zoomed cell size
            cell_left = widget_x
            cell_right = widget_x + cell_size
            cell_top = widget_y
            cell_bottom = widget_y + cell_size
            
            # Only show and position cell if it's at least partially visible
            if (cell_right > visible_left and cell_left < visible_right and 
                cell_bottom > visible_top and cell_top < visible_bottom):
                # Move cell view
                cell.view.move(int(widget_x), int(widget_y))
                
                # Ensure cell view is visible (in case it wasn't shown during creation in magnifier mode)
                if not cell.view.isVisible():
                    cell.view.show()
                
                # Clip cell view to visible area using setMask to prevent overflow
                # Calculate intersection of cell with visible area
                # clip_x and clip_y are relative to the cell view (0,0 is top-left of cell)
                # We need to calculate what part of the cell is within the visible area
                clip_x = max(0, visible_left - cell_left)
                clip_y = max(0, visible_top - cell_top)
                clip_right_in_cell = min(cell_size, visible_right - cell_left)
                clip_bottom_in_cell = min(cell_size, visible_bottom - cell_top)
                clip_width = max(0, clip_right_in_cell - clip_x)
                clip_height = max(0, clip_bottom_in_cell - clip_y)
                
                # Apply clipping mask to cell view if cell overflows visible area
                if clip_x > 0 or clip_y > 0 or clip_width < cell_size or clip_height < cell_size:
                    # Cell overflows, create mask for visible portion
                    clip_rect = QRect(int(clip_x), int(clip_y), int(clip_width), int(clip_height))
                    cell.view.setMask(QRegion(clip_rect))
                else:
                    # No clipping needed, remove any existing mask
                    cell.view.clearMask()
            else:
                # Cell is completely outside visible area, hide it
                if cell.view.isVisible():
                    cell.view.hide()
            
            # Update agents on this cell
            for agent in cell.getAgents():
                if hasattr(agent, 'view') and agent.view:
                    # Update agent size to match zoom (if not already updated)
                    if not hasattr(agent.view, 'saveSize'):
                        agent.view.saveSize = agent.view.size
                    agent.view.size = round(agent.view.saveSize * self.zoom)
                    
                    # Calculate agent position relative to cell
                    grid_size = self.size  # Current zoomed size
                    agent_size = agent.view.size
                    
                    # Calculate relative position within cell (same logic as updatePositionInEntity)
                    location = agent.view.type.locationInEntity
                    if location == "random":
                        # For random, use stored random position
                        if not hasattr(agent.view, '_randomX') or not hasattr(agent.view, '_randomY'):
                            import random
                            agent.view._randomX = random.random()
                            agent.view._randomY = random.random()
                        relX = int(agent.view._randomX * (grid_size - agent_size))
                        relY = int(agent.view._randomY * (grid_size - agent_size))
                    elif location == "topRight":
                        relX = grid_size - agent_size
                        relY = 0
                    elif location == "topLeft":
                        relX = 0
                        relY = 0
                    elif location == "bottomLeft":
                        relX = 0
                        relY = grid_size - agent_size
                    elif location == "bottomRight":
                        relX = grid_size - agent_size
                        relY = grid_size - agent_size
                    elif location == "center":
                        relX = (grid_size - agent_size) / 2
                        relY = (grid_size - agent_size) / 2
                    else:
                        relX = 0
                        relY = 0
                    
                    # Calculate absolute position in widget coordinates
                    agent_widget_x = widget_x + round(relX)
                    agent_widget_y = widget_y + round(relY)
                    
                    # Update agent view coordinates (used by paintEvent)
                    agent.view.xCoord = int(agent_widget_x)
                    agent.view.yCoord = int(agent_widget_y)
                    
                    # Move agent and force update
                    agent.view.move(int(agent_widget_x), int(agent_widget_y))
                    agent.view.update()  # Force repaint to update geometry
            
            # Update tiles on this cell
            for tile in cell.getTilesHere():
                if hasattr(tile, 'view') and tile.view:
                    # Update tile position relative to cell
                    tile.updatePositionFromCell()
        
        self.update()
    
    def updateGridSize(self):
        """
        Update grid size based on current zoom level
        """
        # Calculate zoomed size and gap from reference values
        self.size = round(self.saveSize * self.zoom)
        self.gap = round(self.saveGap * self.zoom)
        
        if self.zoomMode == "magnifier":
            # Magnifier mode: keep widget size fixed at original size
            # originalWidth and originalHeight are initialized in __init__
            self.setFixedSize(self.originalWidth, self.originalHeight)
            
            # Clamp viewport to ensure it stays within bounds
            self._clampViewport()
        else:
            # Resize mode: change widget size based on zoom
            if self.cellShape == "square":
                new_width = int(self.columns * self.size + (self.columns + 1) * self.gap + 1) + 2 * self.frameMargin
                new_height = int(self.rows * self.size + (self.rows + 1) * self.gap) + 1 + 2 * self.frameMargin
            elif self.cellShape == "hexagonal":
                # Width: columns * size + columns * gap + half hexagon for offset + frame margins
                # Height: rows * (size * 0.75) + (rows-1) * gap + frame margins
                new_width = int(self.columns * self.size + self.columns * self.gap + self.size / 2 + 2 * self.frameMargin)
                # Mathematical calculation for "Pointy-top hex grid with even-r offset"
                adaptive_factor = self._calculate_hexagonal_adaptive_factor()
                hex_height = self.size * adaptive_factor  # Correct height for pointy-top hexagones
                new_height = int((self.rows - 1) * (hex_height + self.gap) + hex_height + 2 * self.frameMargin)
            
            self.setFixedSize(new_width, new_height)
        
        # Update all cells first
        for cell in self.getCells():
            # Update cell size to match grid zoom
            cell.size = self.size
            cell.gap = self.gap
            
            if self.zoomMode == "magnifier":
                # In magnifier mode, don't call calculatePosition() as it would reset positions
                # We'll position cells directly in _updatePositionsForViewport()
                pass
            else:
                # In resize mode, calculatePosition gives us the correct positions
                cell.view.calculatePosition()  # Force position recalculation
                cell.view.update()
        
        # Force a complete repaint to ensure cells are repositioned
        self.update()
        
        # CRITICAL: Force cells to actually move to their new positions
        if self.zoomMode == "magnifier":
            # In magnifier mode, position cells according to viewport
            # This must be done BEFORE recreating agents so agents can use correct cell positions
            # IMPORTANT: This calculates positions directly without using calculatePosition()
            self._updatePositionsForViewport()
        else:
            # In resize mode, use standard positioning from calculatePosition()
            for cell in self.getCells():
                cell.view.move(cell.view.startX, cell.view.startY)
        
        # Now recreate agent views using CURRENT cell positions
        for cell in self.getCells():
            # RECREATION SOLUTION: Destroy and recreate agent views
            for agent in cell.getAgents():
                # Update agent model zoom
                agent.updateZoom(self.zoom)
                
                if self.zoomMode == "magnifier":
                    # In magnifier mode, don't recreate agents - just update their size and position
                    # This preserves the viewport positioning
                    if hasattr(agent, 'view') and agent.view:
                        # Initialize saveSize if not already set
                        if not hasattr(agent.view, 'saveSize') or agent.view.saveSize is None:
                            # Use model's saveSize if available, otherwise use current size
                            if hasattr(agent, 'saveSize'):
                                agent.view.saveSize = agent.saveSize
                            else:
                                agent.view.saveSize = agent.view.size
                        # Update agent view size to match zoom
                        agent.view.size = round(agent.view.saveSize * self.zoom)
                        # Also update agent model size
                        if hasattr(agent, 'saveSize'):
                            agent.size = round(agent.saveSize * self.zoom)
                        # Position will be updated by _updatePositionsForViewport() call below
                else:
                    # In resize mode, recreate agents (original behavior)
                    # Destroy existing agent view immediately
                    if hasattr(agent, 'view') and agent.view:
                        agent.view.setParent(None)  # Remove from parent first
                        agent.view.deleteLater()
                        agent.view = None
                    
                    # Recreate agent view with current grid as parent
                    from mainClasses.SGAgentView import SGAgentView
                    agent_view = SGAgentView(agent, self)  # self = grid as parent
                    
                    # Update agent view size to match zoom
                    if hasattr(agent_view, 'saveSize'):
                        agent_view.size = round(agent_view.saveSize * self.zoom)
                    else:
                        agent_view.saveSize = agent_view.size
                        agent_view.size = round(agent_view.saveSize * self.zoom)
                    
                    # Link model and view
                    agent.setView(agent_view)
                    
                    # Force the new view to be visible and positioned using CURRENT cell position
                    agent_view.show()
                    current_cell_position = (cell.view.x(), cell.view.y())
                    agent_view.updatePositionInEntity(current_cell_position)
        
        # In magnifier mode, update agent positions after all agents are updated
        if self.zoomMode == "magnifier":
            self._updatePositionsForViewport()
        
        # Update tile positions and sizes when grid size changes
        # Collect all tiles from all cells
        all_tiles = []
        for cell in self.getCells():
            all_tiles.extend(cell.getTilesHere())
        
        # Sort tiles by layer (lower layers first, higher layers last)
        all_tiles.sort(key=lambda t: t.layer if hasattr(t, 'layer') else 0)
        
        # Update zoom for all tiles
        for tile in all_tiles:
            tile.updateZoom(self.zoom)
        
        # Ensure tiles are rendered in correct z-order (layer order)
        # Lower tiles first, then raise them in layer order
        for tile in all_tiles:
            if hasattr(tile, 'view') and tile.view:
                tile.view.lower()  # Start by lowering all tiles
        
        # Now raise tiles in order of their layer (higher layers on top)
        for tile in all_tiles:
            if hasattr(tile, 'view') and tile.view:
                tile.view.raise_()  # Raise tiles in layer order
        
        # Ensure agents are always on top of tiles (after tiles are positioned)
        for cell in self.getCells():
            for agent in cell.agents:
                if hasattr(agent, 'view') and agent.view:
                    agent.view.raise_()  # Bring agents to front, above tiles

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        # Check for pan in magnifier mode (Shift + LeftButton)
        if (self.zoomMode == "magnifier" and 
            event.button() == Qt.LeftButton and 
            event.modifiers() & Qt.ShiftModifier):
            # Start panning - lock viewport to prevent reset
            self.panning = True
            self._viewport_locked = True
            self.panStartX = event.x()
            self.panStartY = event.y()
            self.panViewportStartX = self.viewportX
            self.panViewportStartY = self.viewportY
            event.accept()
            return
        
        # Let parent handle other events (including normal drag & drop)
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if self.panning:
            # Final update of positions when pan ends
            self._updatePositionsForViewport()
            self.panning = False
            self._viewport_locked = False  # Unlock viewport
            event.accept()
            return
        
        # Let parent handle other events
        super().mouseReleaseEvent(event)
    
    # To handle the drag of the grid
    def mouseMoveEvent(self, e):
        # Handle pan in magnifier mode (Shift + LeftButton + drag)
        if self.zoomMode == "magnifier" and self.panning:
            if e.buttons() & Qt.LeftButton and e.modifiers() & Qt.ShiftModifier:
                # Calculate pan delta (mouse movement)
                # When mouse moves right, we want to see more of the right side (viewport moves left)
                delta_x = e.x() - self.panStartX
                delta_y = e.y() - self.panStartY
                
                # Convert screen delta to grid coordinate delta
                # When mouse moves right (positive delta_x), viewport should move left (negative)
                grid_delta_x = -delta_x / self.zoom
                grid_delta_y = -delta_y / self.zoom
                
                # Update viewport
                self.viewportX = self.panViewportStartX + grid_delta_x
                self.viewportY = self.panViewportStartY + grid_delta_y
                
                # Clamp viewport
                self._clampViewport()
                
                # Update cell and agent positions
                self._updatePositionsForViewport()
                
                e.accept()
                return
        
        # First, try the new drag & drop implementation from SGGameSpace
        if self.isDraggable and hasattr(self, 'dragging') and self.dragging:
            super().mouseMoveEvent(e)
            return

        # Fallback to the old implementation if moveable is True but not draggable
        if self.moveable == False:
            return
        if e.buttons() != Qt.LeftButton:
            return

        # To get the clic position in GameSpace
        def getPos(e):
            clic = QMouseEvent.windowPos(e)
            xclic = int(clic.x())
            yclic = int(clic.y())
            return xclic, yclic

        # To get the coordinate of the grid upleft corner in GameSpace
        def getCPos(self):
            left = self.x()
            up = self.y()
            return left, up

        # To convert the upleft corner to center coordinates
        def toCenter(self, left, up):
            xC = int(left+(self.columns/2*self.size) +
                     ((self.columns+1)/2*self.gap))
            yC = int(up+(self.rows/2*self.size)+((self.rows+1)/2*self.gap))
            return xC, yC

        mimeData = QMimeData()
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.pos())

        xclic, yclic = getPos(e)
        left, up = getCPos(self)
        xC, yC = toCenter(self, left, up)

        drag.exec_(Qt.MoveAction)

        leftf, upf = getCPos(self)
        xCorr = xclic-xC
        yCorr = yclic-yC

        newX = leftf-xCorr
        newY = upf-yCorr

        self.move(newX, newY)

    # Funtion to have the global size of a gameSpace

    def getSizeXGlobal(self):
        if (self.cellShape == "square"):
            return int(self.columns*self.size+(self.columns+1)*self.gap+1)
        if (self.cellShape == "hexagonal"):
            return int(self.columns*self.size + self.columns*self.gap + self.size/2)

    def getSizeYGlobal(self):
        if (self.cellShape == "square"):
            return int(self.rows*self.size+(self.rows+1)*self.gap + 2 * self.frameMargin)
        if (self.cellShape == "hexagonal"):
            adaptive_factor = self._calculate_hexagonal_adaptive_factor()
            hex_height = self.size * adaptive_factor  # Correct height for pointy-top hexagones
            return int((self.rows - 1) * (hex_height + self.gap) + hex_height + 2 * self.frameMargin)

    def sizeHint(self):
        """Return the recommended size for the grid widget"""
        if (self.cellShape == "square"):
            width = int(self.columns*self.size+(self.columns+1)*self.gap + 2*self.frameMargin)
            height = int(self.rows*self.size+(self.rows+1)*self.gap + 2*self.frameMargin)
        elif (self.cellShape == "hexagonal"):
            width = int(self.columns * self.size + self.columns * self.gap + self.size / 2 + 2 * self.frameMargin)
            adaptive_factor = self._calculate_hexagonal_adaptive_factor()
            hex_height = self.size * adaptive_factor  # Correct height for pointy-top hexagones
            height = int((self.rows - 1) * (hex_height + self.gap) + hex_height + 2 * self.frameMargin)
        else:
            width = height = 100  # Default fallback
        return QSize(width, height)

    def minimumSizeHint(self):
        """Return the minimum size for the grid widget"""
        return self.sizeHint()

    # To get all the values possible for Legend
    def getValuesForLegend(self):
        return self.model.getCellPovs(self)

# -----------------------------------------------------------------------------------------
# Definiton of the methods who the modeler will use


# ============================================================================
# MODELER METHODS
# ============================================================================
    def __MODELER_METHODS__(self):
        pass
# ============================================================================
# SET METHODS
# ============================================================================
    def __MODELER_METHODS__SET__(self):
        pass

    def setOwners(self, owners):
        """
        Set the owners of this grid.
        
        Args:
            owners: Can be:
                - A single player (SGPlayer instance or player name string)
                - A list of players (list of SGPlayer instances or player name strings)
                - None to clear owners
        
        Examples:
            grid.setOwners(player1)  # Single owner
            grid.setOwners([player1, player2])  # Multiple owners
            grid.setOwners("Player 1")  # Single owner by name
            grid.setOwners(["Player 1", "Player 2"])  # Multiple owners by name
        """
        if owners is None:
            self.owners = []
            return
        
        # Convert to list if single owner provided
        if not isinstance(owners, list):
            owners = [owners]
        
        # Normalize owners: convert player names to player instances if needed
        normalized_owners = []
        for owner in owners:
            if isinstance(owner, str):
                # Try to get player instance from name
                try:
                    player_instance = self.model.getPlayer(owner)
                    normalized_owners.append(player_instance)
                except ValueError:
                    # If player not found, keep as string (might be used later)
                    normalized_owners.append(owner)
            else:
                # Already a player instance or other object
                normalized_owners.append(owner)
        
        self.owners = normalized_owners
    
    def setZoomMode(self, zoomMode):
        """
        Set the zoom mode for this grid.
        
        Args:
            zoomMode (str): "resize" or "magnifier"
                - "resize": Zoom changes the physical size of the grid widget (default)
                - "magnifier": Zoom creates a magnifying glass effect, keeping widget size fixed
        
        Examples:
            grid.setZoomMode("magnifier")  # Enable magnifier mode
            grid.setZoomMode("resize")    # Use default resize mode
        """
        if zoomMode not in ["resize", "magnifier"]:
            raise ValueError(f"zoomMode must be 'resize' or 'magnifier', got '{zoomMode}'")
        
        old_mode = self.zoomMode
        self.zoomMode = zoomMode
        
        if zoomMode == "magnifier" and old_mode == "resize":
            # Switching to magnifier: reset viewport
            self._resetViewport()
        elif zoomMode == "resize" and old_mode == "magnifier":
            # Switching to resize: reset viewport offset
            self.viewportX = 0
            self.viewportY = 0
        
        self.updateGridSize()
        self.update()
    
# ============================================================================
# GET/NB METHODS
# ============================================================================

    def __MODELER_METHODS__GET__(self):
        pass

    def getOwners(self):
        """Get the owners of this grid"""
        return self.owners
    
    def getOwner(self):
        """Get the first owner of this grid"""
        return self.owners[0]

    def getCellType(self):
        """Get the cell type of this grid"""
        return self.model.getCellType(self)

    def getCells(self):
        """Get the cells of this grid"""
        return self.model.getCellType(self).entities

    def getCell_withId(self, cell_id):
        """Get the cell with the given id"""
        return self.model.getCell(self,cell_id)

    def cellIdFromCoords(self,x,y):
        return self.model.getCellType(self).cellIdFromCoords(x,y)
    
    def getCell_withCoords(self,x,y):
        """Get the cell with the given coordinates"""
        return self.getCell_withId(self.cellIdFromCoords(x,y))

   # Return the cells at a specified column
    def getCells_withColumn(self, columnNumber):
        """
        Return the cells at a specified column.
        args:
            columnNumber (int): column number
        """
        return [ cell for cell in self.model.getCells(self) if cell.xCoord== columnNumber]
        
  # Return the cells at a specified row
    def getCells_withRow(self, rowNumber):
        """
        Return the cells at a specified column.
        args:
            rowNumber (int): row number
        """
        return [ cell for cell in self.model.getCells(self) if cell.yCoord== rowNumber]

    
    # ============================================================================
    # IS/HAS METHODS
    # ============================================================================
    
    # @CATEGORY: IS
    def isOwnedBy(self, user):
        """
        Check if this grid is owned by a user.
        
        Args:
            user: A player (SGPlayer instance) or player name (string)
        
        Returns:
            bool: True if the grid is owned by the user, False otherwise
        
        Examples:
            grid.isOwnedBy(player1)  # Check by player instance
            grid.isOwnedBy("Player 1")  # Check by player name
        """
        if not self.owners:
            return False
        
        # Normalize user to player instance if it's a string
        if isinstance(user, str):
            try:
                user = self.model.getPlayer(user)
            except ValueError:
                # Player not found, can't be owner
                return False
        
        # Check if user is in owners list
        return user in self.owners
    
    # ============================================================================
    # DO/DISPLAY METHODS
    # ============================================================================
    
    def setMagnifierOnArea(self, cellA, cellB):
        """
        Set the magnifier viewport to show a rectangular area between two cells.
        
        Args:
            cellA (SGCell): First cell defining the area
            cellB (SGCell): Second cell defining the area
        
        Examples:
            cellA = grid.getCell_withCoords(5, 5)
            cellB = grid.getCell_withCoords(15, 15)
            grid.setMagnifierOnArea(cellA, cellB)
        """
        if self.zoomMode != "magnifier":
            raise ValueError("setMagnifierOnArea() can only be used in magnifier mode. Use setZoomMode('magnifier') first.")
        
        # Get cell positions in grid coordinates
        x1 = min(cellA.xCoord, cellB.xCoord)
        x2 = max(cellA.xCoord, cellB.xCoord)
        y1 = min(cellA.yCoord, cellB.yCoord)
        y2 = max(cellA.yCoord, cellB.yCoord)
        
        # Get cell views to calculate actual positions
        cell1 = self.getCell_withCoords(x1, y1)
        cell2 = self.getCell_withCoords(x2, y2)
        
        if not (hasattr(cell1, 'view') and hasattr(cell2, 'view')):
            return
        
        # Calculate area bounds in grid coordinates (using same logic as _updatePositionsForViewport)
        # Use saveSize/saveGap to get unzoomed positions
        base_x = self.frameMargin
        base_y = self.frameMargin
        
        if self.cellShape == "square":
            cell1_grid_x = base_x + (cell1.xCoord - 1) * (self.saveSize + self.saveGap) + self.saveGap
            cell1_grid_y = base_y + (cell1.yCoord - 1) * (self.saveSize + self.saveGap) + self.saveGap
            cell2_grid_x = base_x + (cell2.xCoord - 1) * (self.saveSize + self.saveGap) + self.saveGap
            cell2_grid_y = base_y + (cell2.yCoord - 1) * (self.saveSize + self.saveGap) + self.saveGap
        elif self.cellShape == "hexagonal":
            cell1_grid_x = base_x + (cell1.xCoord - 1) * (self.saveSize + self.saveGap) + self.saveGap
            adaptive_factor = self._calculate_hexagonal_adaptive_factor()
            hex_height = self.saveSize * adaptive_factor
            cell1_grid_y = base_y + (cell1.yCoord - 1) * (hex_height + self.saveGap) + self.saveGap
            if cell1.yCoord % 2 == 0:
                cell1_grid_x += self.saveSize / 2
            cell2_grid_x = base_x + (cell2.xCoord - 1) * (self.saveSize + self.saveGap) + self.saveGap
            cell2_grid_y = base_y + (cell2.yCoord - 1) * (hex_height + self.saveGap) + self.saveGap
            if cell2.yCoord % 2 == 0:
                cell2_grid_x += self.saveSize / 2
        
        area_min_x = min(cell1_grid_x, cell2_grid_x)
        area_max_x = max(cell1_grid_x + self.saveSize, cell2_grid_x + self.saveSize)
        area_min_y = min(cell1_grid_y, cell2_grid_y)
        area_max_y = max(cell1_grid_y + self.saveSize, cell2_grid_y + self.saveSize)
        
        area_width = area_max_x - area_min_x
        area_height = area_max_y - area_min_y
        
        # Calculate widget dimensions
        widget_width = self.width() - 2 * self.frameMargin
        widget_height = self.height() - 2 * self.frameMargin
        
        # Calculate zoom level to fit area
        zoom_x = widget_width / area_width if area_width > 0 else 1.0
        zoom_y = widget_height / area_height if area_height > 0 else 1.0
        target_zoom = min(zoom_x, zoom_y, 3.0)  # Cap at 3x
        
        # Set zoom (minimum is 1.0 in magnifier mode)
        self.zoom = max(1.0, target_zoom)
        
        # Center viewport on area
        self.viewportX = area_min_x - (widget_width / self.zoom - area_width) / 2
        self.viewportY = area_min_y - (widget_height / self.zoom - area_height) / 2
        
        # Clamp viewport
        self._clampViewport()
        
        # Update grid
        self.updateGridSize()
        self.update()
    
    def setMagnifierToCoverAllCellsWith(self, condition):
        """
        Adjust magnifier zoom and position to show all cells matching a condition.
        
        Args:
            condition (callable): Function that takes a cell and returns True if it should be included
        
        Examples:
            # Show all cells with terrain="forest"
            grid.setMagnifierToCoverAllCellsWith(lambda cell: cell.isValue("terrain", "forest"))
            
            # Show all cells with agents
            grid.setMagnifierToCoverAllCellsWith(lambda cell: cell.hasAgent())
        """
        if self.zoomMode != "magnifier":
            raise ValueError("setMagnifierToCoverAllCellsWith() can only be used in magnifier mode. Use setZoomMode('magnifier') first.")
        
        # Find all cells matching condition
        matching_cells = [cell for cell in self.getCells() if condition(cell)]
        
        if not matching_cells:
            # No cells match, reset viewport
            self._resetViewport()
            self.updateGridSize()
            self.update()
            return
        
        # Calculate bounding box of matching cells
        min_x = min(cell.xCoord for cell in matching_cells)
        max_x = max(cell.xCoord for cell in matching_cells)
        min_y = min(cell.yCoord for cell in matching_cells)
        max_y = max(cell.yCoord for cell in matching_cells)
        
        # Get corner cells
        cell_min = self.getCell_withCoords(min_x, min_y)
        cell_max = self.getCell_withCoords(max_x, max_y)
        
        # Use setMagnifierOnArea to show the area
        self.setMagnifierOnArea(cell_min, cell_max)

    
