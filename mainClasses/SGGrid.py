from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGModel import *

# Class who is responsible of the grid creation
class SGGrid(SGGameSpace):
    def __init__(self, parent, name, columns=10, rows=10,cellShape="square", gap=3, size=30, aColor=None, moveable=True, backGroundImage=None,neighborhood='moore',boundaries='open'):
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

        if aColor != "None":
            self.setColor(aColor)
        # Store background image via gs_aspect (supports both QPixmap and file path)
        if backGroundImage is not None:
            self.setBackgroundImage(backGroundImage)
    
    # Drawing the game board with the cell
    def paintEvent(self, event): 
        self.countPaintEvent += 1
        painter = QPainter()
        painter.begin(self)
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
        if radius > 0:
            painter.drawRoundedRect(0, 0, max(0, self.minimumWidth()-1), max(0, self.minimumHeight()-1), radius, radius)
        else:
            painter.drawRect(0, 0, self.minimumWidth()-1, self.minimumHeight()-1)
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
            
            if delta > 0:
                # Wheel up - zoom in
                self.newZoomIn()
            elif delta < 0:
                # Wheel down - zoom out
                self.newZoomOut()
            
            # Accept the event to prevent it from propagating
            event.accept()
        else:
            # Let the event propagate if mouse is not over this grid
            event.ignore()
    
    def newZoomIn(self):
        """
        Zoom in the grid by increasing zoom factor
        """
        self.zoom = min(self.zoom * 1.1, 3.0)  # Cap at 3x zoom
        self.updateGridSize()
        self.update()
    
    def newZoomOut(self):
        """
        Zoom out the grid by decreasing zoom factor
        """
        self.zoom = max(self.zoom * 0.9, 0.3)  # Cap at 0.3x zoom
        self.updateGridSize()
        self.update()
    
    def setZoomLevel(self, zoom_level):
        """
        Set specific zoom level
        """
        self.zoom = max(0.3, min(zoom_level, 3.0))  # Clamp between 0.3 and 3.0
        self.updateGridSize()
        self.update()
    
    def resetZoom(self):
        """
        Reset zoom to 1.0
        """
        self.zoom = 1.0
        self.updateGridSize()
        self.update()
    
    def updateGridSize(self):
        """
        Update grid size based on current zoom level
        """
        # Calculate zoomed size and gap from reference values
        self.size = round(self.saveSize * self.zoom)
        self.gap = round(self.saveGap * self.zoom)
        
        # Update minimum size for the grid widget
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
            
            # Force cell view to recalculate position
            cell.view.calculatePosition()  # Force position recalculation
            cell.view.update()
        
        # Force a complete repaint to ensure cells are repositioned
        self.update()
        
        # CRITICAL: Force cells to actually move to their new positions
        for cell in self.getCells():
            cell.view.move(cell.view.startX, cell.view.startY)
        
        # Now recreate agent views using CURRENT cell positions
        for cell in self.getCells():
            # RECREATION SOLUTION: Destroy and recreate agent views
            for agent in cell.getAgents():
                # Update agent model zoom
                agent.updateZoom(self.zoom)
                
                # Destroy existing agent view immediately
                if hasattr(agent, 'view') and agent.view:
                    agent.view.setParent(None)  # Remove from parent first
                    agent.view.deleteLater()
                    agent.view = None
                
                # Recreate agent view with current grid as parent
                from mainClasses.SGAgentView import SGAgentView
                agent_view = SGAgentView(agent, self)  # self = grid as parent
                
                # Link model and view
                agent.setView(agent_view)
                
                # Force the new view to be visible and positioned using CURRENT cell position
                agent_view.show()
                current_cell_position = (cell.view.x(), cell.view.y())
                agent_view.getPositionInEntity(current_cell_position)
        
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

    # To handle the drag of the grid
    def mouseMoveEvent(self, e):
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

    
