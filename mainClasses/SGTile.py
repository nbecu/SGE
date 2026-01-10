from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGEntity import SGEntity
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mainClasses.SGCell import SGCell
    from mainClasses.SGAgent import SGAgent

class SGTile(SGEntity):
    """
    SGTile - Tile model class for grid-based simulations
    
    This class uses Model-View architecture:
    - Inherits from SGEntity for data and business logic
    - Delegates UI to SGTileView for display and interaction
    
    Tiles are placed on cells and can be stacked (multiple tiles of the same type on the same position).
    Each tile has two faces (front and back) that can be flipped.
    """
    
    def __init__(self, cell, size, attributesAndValues, shapeColor, type, position="center", 
                 face="front", frontImage=None, backImage=None, frontColor=None, backColor=None, layer=1):
        """
        Initialize the tile
        
        Args:
            cell: The cell where the tile is placed
            size: Size of the tile
            attributesAndValues: Initial attributes and values
            shapeColor: Shape color (default color)
            type: The tile definition class (SGTileType)
            position: Position on the cell ("center", "topLeft", "topRight", "bottomLeft", "bottomRight", "full")
            face: Current face visible ("front" or "back", default: "front")
            frontImage: Image for the front face (QPixmap, optional)
            backImage: Image for the back face (QPixmap, optional)
            frontColor: Color for the front face (optional, uses shapeColor if None)
            backColor: Color for the back face (optional, uses shapeColor if None)
            layer: Z-order/layer for rendering (default: 1, consistent with 1-based coordinate system)
        """
        super().__init__(type, size, attributesAndValues)
        
        # Type identification attributes
        self.isEntity = True
        self.isCell = False
        self.isAgent = False
        self.isTile = True
        
        # Tile-specific properties
        # Position and layer must be set before addTile to avoid AttributeError
        self.position = position
        self.layer = layer  # Layer must be set before addTile() which accesses stack.tiles
        
        self.cell = None
        if cell is not None:
            self.cell = cell
            # Register tile with cell (will be implemented in SGCell)
            if hasattr(cell, 'addTile'):
                cell.addTile(self)
        else:
            raise ValueError('Tile must be placed on a cell')
        
        # Two faces system
        self.face = face  # "front" or "back"
        
        # Define colors first (to avoid duplication)
        self.frontColor = frontColor if frontColor is not None else shapeColor
        self.backColor = backColor if backColor is not None else shapeColor
        
        # Fill transparent areas in images with corresponding colors
        from mainClasses.SGExtensions import fillTransparentAreas
        
        if frontImage is not None and isinstance(frontImage, QPixmap):
            self.frontImage = fillTransparentAreas(frontImage, self.frontColor)
        else:
            self.frontImage = frontImage
        
        if backImage is not None and isinstance(backImage, QPixmap):
            self.backImage = fillTransparentAreas(backImage, self.backColor)
        else:
            self.backImage = backImage
        
        # Save reference size for zoom calculations (like SGCell and SGAgent)
        self.saveSize = size
        
        # Initialize attributes
        self.initAttributesAndValuesWith(attributesAndValues)
        
        # View will be created and linked by the factory
        # Don't create view here to avoid duplication

    # ============================================================================
    # DEVELOPER METHODS
    # ============================================================================

    # ============================================================================
    # ZOOM METHODS
    # ============================================================================
    
    def updateZoom(self, zoom_factor):
        """
        Update tile size based on zoom factor
        
        Args:
            zoom_factor: The zoom factor to apply
        """
        # Calculate new size based on saved size and zoom
        self.size = round(self.saveSize * zoom_factor)
        
        # Update view if it exists (view reads size from model via property)
        if self.view:
            # Update position based on new size
            if hasattr(self.view, 'updatePositionFromCell'):
                self.view.updatePositionFromCell()
            elif hasattr(self.view, 'getPositionInCell'):
                self.view.getPositionInCell()
            # Force repaint with new size
            self.view.update()

    # Model-View specific methods
    def getView(self):
        """Get the tile view"""
        return self.view
    
    def setView(self, view):
        """Set the tile view"""
        self.view = view
        if view:
            view.tile_model = self
    
    def updateView(self):
        """Update the tile view"""
        if self.view:
            self.view.update()

    # ============================================================================
    # MODELER METHODS
    # ============================================================================

    def __MODELER_METHODS__NEW__(self):
        pass

    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================

    def setLayer(self, layer):
        """
        Set the layer (z-index) of this tile and update z-order rendering.
        
        Layers are 1-based, where 1 is the bottom layer and higher numbers are on top.
        This method automatically reorganizes the z-order of all tiles in the same stack
        to ensure correct visual stacking.
        
        Args:
            layer (int): The layer number (1-based, must be >= 1)
            
        Returns:
            self: The tile (for chaining operations)
        """
        if not isinstance(layer, int) or layer < 1:
            raise ValueError(f"Layer must be a positive integer, got: {layer}")
        self.layer = layer
        if self.view:
            # Update the view's layer property to keep it in sync
            self.view.layer = layer
            # Reorganize z-order for all tiles in the same cell
            self._updateZOrderInCell()
            self.view.update()
        return self
    
    def _updateZOrderInCell(self):
        """
        Update the z-order (stacking order) of all tiles in the same cell
        Lower layers are rendered first, higher layers are on top
        
        Uses SGStack to get tiles sorted by layer
        """
        if not self.cell or not hasattr(self.cell, 'getStack'):
            return
        
        # Get the stack for this tile type (all tiles of same type are at same position)
        stack = self.cell.getStack(self.type)
        tiles_in_stack = stack.tiles  # Already sorted by layer
        
        if not tiles_in_stack:
            return
        
        # Reorganize z-order: lower all tiles first, then raise them in layer order
        for tile in tiles_in_stack:
            if hasattr(tile, 'view') and tile.view:
                tile.view.lower()  # Start by lowering all tiles
        
        # Now raise tiles in order of their layer (higher layers on top)
        for tile in tiles_in_stack:
            if hasattr(tile, 'view') and tile.view:
                tile.view.raise_()
    
    def setFace(self, face):
        """
        Set the visible face of this tile.
        
        Args:
            face (str): "front" to show the front face, or "back" to show the back face
            
        Raises:
            ValueError: If face is not "front" or "back"
            
        Returns:
            self: The tile (for chaining operations)
        """
        if face not in ["front", "back"]:
            raise ValueError('Face must be "front" or "back"')
        self.face = face
        if self.view:
            self.view.update()
        return self

    # ============================================================================
    # DELETE METHODS
    # ============================================================================

    def __MODELER_METHODS__DELETE__(self):
        pass

    def delete(self):
        """
        Delete this tile from the game.
        
        This method:
        - Removes the tile from its cell (and reorganizes layers if needed)
        - Removes the tile from its type's entities list
        - Hides and deletes the tile's view
        - Clears all references
        
        After calling this method, the tile should not be used anymore.
        """
        # Remove from cell
        if self.cell and hasattr(self.cell, 'removeTile'):
            self.cell.removeTile(self)
        
        # Remove from type's entities list
        if self.type and hasattr(self.type, 'entities'):
            if self in self.type.entities:
                self.type.entities.remove(self)
        
        # Hide and delete view
        if self.view:
            self.view.hide()
            self.view.deleteLater()
        
        # Clear references
        self.cell = None
        self.view = None

    # ============================================================================
    # GET/NB METHODS
    # ============================================================================

    def __MODELER_METHODS__GET__(self):
        pass

    def getCell(self):
        """
        Get the cell where this tile is placed.
        
        Returns:
            SGCell: The cell containing this tile, or None if not placed
        """
        return self.cell
    
    def getCoords(self):
        """
        Get the grid coordinates of the cell where this tile is placed.
        
        Returns:
            tuple: (x, y) coordinates of the cell (1-indexed), or None if tile is not placed
        """
        if self.cell:
            return (self.cell.xCoord, self.cell.yCoord)
        return None
    
    def getLayer(self):
        """
        Get the layer (z-index) of this tile in its stack.
        
        Layers are 1-based, where 1 is the bottom layer and higher numbers are on top.
        In a stack, layers are always continuous from 1 to N (no gaps).
        
        Returns:
            int: The layer number (1-based)
        """
        return self.layer
    
    def getFace(self):
        """
        Get the currently visible face of this tile.
        
        Returns:
            str: "front" or "back" indicating which face is currently visible
        """
        return self.face
    
    def getAgentsHere(self):
        """
        Get all agents on the cell where this tile is placed.
        
        Returns:
            list: List of SGAgent objects on the same cell as this tile
        """
        if self.cell and hasattr(self.cell, 'agents'):
            return self.cell.agents
        return []

    # ============================================================================
    # IS/HAS METHODS
    # ============================================================================

    def __MODELER_METHODS__IS__(self):
        pass

    def isFaceFront(self):
        """
        Check if the front face is currently visible.
        
        Returns:
            bool: True if front face is visible, False if back face is visible
        """
        return self.face == "front"
    
    def isFaceBack(self):
        """
        Check if the back face is currently visible.
        
        Returns:
            bool: True if back face is visible, False if front face is visible
        """
        return self.face == "back"

    
    def isOccupied(self):
        """
        Check if the cell containing this tile is occupied by any agents.
        
        Returns:
            bool: True if at least one agent is on the same cell, False otherwise
        """
        agents = self.getAgentsHere()
        return len(agents) > 0

    # ============================================================================
    # DO/DISPLAY METHODS
    # ============================================================================

    def __MODELER_METHODS__DO_DISPLAY__(self):
        pass

    # @CATEGORY: DO
    def moveTo(self, aDestinationCell):
        """
        Move this tile to a specific cell.
        
        This method handles both initial placement and subsequent movements.
        Use this method for initial tile placement or when moving to a specific cell.
        
        Layer management:
        - On destination cell: If tiles of the same type already exist at the same position,
          this tile will be automatically stacked on top (layer = max_layer + 1).
          Otherwise, it uses layer 1 (default).
        - On source cell: When moving a tile from a stack, the remaining tiles of the same
          type at the same position will have their layers reorganized (compacted) to maintain
          a continuous sequence starting from 1.
        
        Args:
            aDestinationCell: The cell where the tile should move
            
        Returns:
            self: The tile (for chaining operations)
        """
        if aDestinationCell is None:
            raise ValueError('Cell cannot be None')
        
        if self.cell is None:
            # First placement
            # Determine appropriate layer on destination cell BEFORE adding to cell
            # Check if there are already tiles of the same type at the same position
            if hasattr(aDestinationCell, 'getStack'):
                stack = aDestinationCell.getStack(self.type)
                max_layer = stack.maxLayer()
                
                if max_layer > 0:
                    # There are tiles of the same type at this position
                    # Set layer to max_layer + 1 to stack on top
                    self.setLayer(max_layer + 1)
                else:
                    # No tiles of the same type at this position
                    # The tile is set to layer (1)
                    self.setLayer(1)
            
            # Set cell reference
            self.cell = aDestinationCell
            
            # Register with cell
            if hasattr(aDestinationCell, 'addTile'):
                aDestinationCell.addTile(self)
            
            # Adjust tile size if position is "full" to match cell size
            if self.position == "full" and hasattr(aDestinationCell, 'saveSize'):
                self.size = aDestinationCell.saveSize
                self.saveSize = aDestinationCell.saveSize  # Also update saveSize for zoom consistency
                # View reads size from model via property - no manual synchronization needed
            
            # Get grid reference for magnifier mode check
            grid = None
            if hasattr(aDestinationCell, 'type') and hasattr(aDestinationCell.type, 'grid'):
                grid = aDestinationCell.type.grid
            
            # Update zoom if in magnifier mode (must be done before updatePositionFromCell)
            if grid and hasattr(grid, 'zoomMode') and grid.zoomMode == "magnifier" and hasattr(grid, 'zoom'):
                self.updateZoom(grid.zoom)
            
            # Update view position
            if self.view:
                self.view.updatePositionFromCell()
                self.view.show()  # Ensure view is visible
                self.updateView()
                
                # Apply clipping if in magnifier mode
                if grid and hasattr(grid, 'zoomMode') and grid.zoomMode == "magnifier":
                    tile_x = self.view.xCoord
                    tile_y = self.view.yCoord
                    tile_size = self.size  # Read from model (view.size property reads from model)
                    grid._clipEntityToVisibleArea(self.view, tile_x, tile_y, tile_size)
            return self
        else:
            # Movement from one cell to another
            
            # Store current position and type for layer management
            old_cell = self.cell
            old_position = self.position
            tile_type = self.type
            
            # Check if moving to a different grid
            old_grid = old_cell.type.grid if hasattr(old_cell, 'type') and hasattr(old_cell.type, 'grid') else None
            new_grid = aDestinationCell.type.grid if hasattr(aDestinationCell, 'type') and hasattr(aDestinationCell.type, 'grid') else None
            
            if old_grid != new_grid and self.view is not None:
                # Change the parent of the view to the new grid
                self.view.setParent(new_grid)
            
            # Reorganize layers on source cell before removing this tile
            # Use SGStack to get tiles of the same type at the same position
            if hasattr(old_cell, 'getStack'):
                stack = old_cell.getStack(tile_type)
                all_tiles_in_stack = stack.tiles  # Already sorted by layer
                # Exclude this tile from the list
                remaining_tiles = [t for t in all_tiles_in_stack if t != self]
                
                # If there are remaining tiles, reorganize their layers (compact layers)
                if remaining_tiles:
                    # Reassign layers starting from 1, maintaining relative order
                    # Update layer without triggering z-order update for each tile individually
                    for i, tile in enumerate(remaining_tiles, start=1):
                        tile.layer = i
                        if tile.view:
                            tile.view.layer = i
                    
                    # Reorganize z-order once for all remaining tiles in the stack
                    # Lower all tiles first
                    for tile in remaining_tiles:
                        if tile.view:
                            tile.view.lower()
                    # Then raise them in layer order
                    for tile in remaining_tiles:
                        if tile.view:
                            tile.view.raise_()
            
            # Remove from current cell
            if hasattr(old_cell, 'removeTile'):
                old_cell.removeTile(self)
            
            # Move to new cell
            self.cell = aDestinationCell
            
            # Determine appropriate layer on destination cell BEFORE adding to cell
            # Check if there are already tiles of the same type at the same position
            if hasattr(aDestinationCell, 'getStack'):
                stack = aDestinationCell.getStack(tile_type)
                max_layer = stack.maxLayer()
                
                if max_layer > 0:
                    # There are tiles of the same type at this position
                    # Set layer to max_layer + 1 to stack on top
                    new_layer = max_layer + 1
                else:
                    # No tiles of the same type at this position
                    # Reset to default layer (1) for a clean start
                    new_layer = 1
            else:
                new_layer = 1
            
            # Set the layer BEFORE adding to cell, so stack.tiles and position calculations use the correct layer
            self.layer = new_layer
            if self.view:
                self.view.layer = new_layer
            
            # Register with new cell (now with correct layer)
            if hasattr(aDestinationCell, 'addTile'):
                aDestinationCell.addTile(self)
            
            # Adjust tile size if position is "full" to match cell size
            if self.position == "full" and hasattr(aDestinationCell, 'saveSize'):
                self.size = aDestinationCell.saveSize
                self.saveSize = aDestinationCell.saveSize  # Also update saveSize for zoom consistency
                # View reads size from model via property - no manual synchronization needed
            
            # Get grid reference for magnifier mode check
            grid = None
            if hasattr(aDestinationCell, 'type') and hasattr(aDestinationCell.type, 'grid'):
                grid = aDestinationCell.type.grid
            
            # Update zoom if in magnifier mode (must be done before updatePositionFromCell)
            if grid and hasattr(grid, 'zoomMode') and grid.zoomMode == "magnifier" and hasattr(grid, 'zoom'):
                self.updateZoom(grid.zoom)
            
            # Update z-order after adding to cell (so z-order update includes this tile)
            self._updateZOrderInCell()
            
            # Update view position
            if self.view:
                self.view.updatePositionFromCell()
                self.view.show()  # Ensure view is visible
                self.updateView()
                
                # Apply clipping if in magnifier mode
                if grid and hasattr(grid, 'zoomMode') and grid.zoomMode == "magnifier":
                    tile_x = self.view.xCoord
                    tile_y = self.view.yCoord
                    tile_size = self.size  # Read from model (view.size property reads from model)
                    grid._clipEntityToVisibleArea(self.view, tile_x, tile_y, tile_size)
            
            return self

    # @CATEGORY: DO
    def placeOn(self, cell):
        """
        Place the tile on a cell (alias for moveTo).
        
        This method is provided for modelers who prefer this syntax.
        It simply calls moveTo() internally.
        
        Args:
            cell: The cell to place the tile on
            
        Returns:
            self: The tile (for chaining operations)
        """
        return self.moveTo(cell)

    # @CATEGORY: DO
    def flip(self):
        """
        Flip the tile to show the other face.
        
        If the front face is currently visible, it switches to the back face.
        If the back face is currently visible, it switches to the front face.
        
        This method updates the view immediately to reflect the change.
        
        Returns:
            self: The tile (for chaining operations)
        """
        if self.face == "front":
            self.face = "back"
        else:
            self.face = "front"
        if self.view:
            self.view.update()
        return self

    # ============================================================================
    # OTHER MODELER METHODS
    # ============================================================================

    def __MODELER_METHODS__OTHER__(self):
        pass

