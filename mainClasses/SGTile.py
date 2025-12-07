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
        self.cell = None
        if cell is not None:
            self.cell = cell
            # Register tile with cell (will be implemented in SGCell)
            if hasattr(cell, 'addTile'):
                cell.addTile(self)
        else:
            raise ValueError('Tile must be placed on a cell')
        
        # Position on the cell
        self.position = position
        
        # Two faces system
        self.face = face  # "front" or "back"
        self.frontImage = frontImage
        self.backImage = backImage
        self.frontColor = frontColor if frontColor is not None else shapeColor
        self.backColor = backColor if backColor is not None else shapeColor
        
        # Layer/z-index for stacking
        self.layer = layer
        
        # Blocking attributes
        self.blocksStacking = False
        self.blocksAgentPlacement = False
        
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
        
        # Update view if it exists (view.updateZoom will handle position update)
        if self.view:
            self.view.updateZoom(zoom_factor)

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
        """Set the layer/z-index of the tile"""
        self.layer = layer
        if self.view:
            self.view.update()
    
    def setFace(self, face):
        """
        Set the visible face
        
        Args:
            face: "front" or "back"
        """
        if face not in ["front", "back"]:
            raise ValueError('Face must be "front" or "back"')
        self.face = face
        if self.view:
            self.view.update()

    # ============================================================================
    # DELETE METHODS
    # ============================================================================

    def __MODELER_METHODS__DELETE__(self):
        pass

    def delete(self):
        """Delete the tile"""
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
        """Get the cell where this tile is placed"""
        return self.cell
    
    def getCoords(self):
        """Get the coordinates of the cell where this tile is placed"""
        if self.cell:
            return (self.cell.xCoord, self.cell.yCoord)
        return None
    
    def getLayer(self):
        """Get the layer/z-index of the tile"""
        return self.layer
    
    def getFace(self):
        """Get the current visible face"""
        return self.face
    
    def getAgentsHere(self):
        """Get all agents on the cell where this tile is placed"""
        if self.cell and hasattr(self.cell, 'agents'):
            return self.cell.agents
        return []

    # ============================================================================
    # IS/HAS METHODS
    # ============================================================================

    def __MODELER_METHODS__IS__(self):
        pass

    def isFaceFront(self):
        """Check if the front face is visible"""
        return self.face == "front"
    
    def isFaceBack(self):
        """Check if the back face is visible"""
        return self.face == "back"
    
    def doesBlockStacking(self):
        """Check if this tile blocks stacking of other tiles on top"""
        return self.blocksStacking
    
    def doesBlockAgentPlacement(self):
        """Check if this tile blocks agent placement"""
        return self.blocksAgentPlacement
    
    def isOccupied(self):
        """Check if the tile's cell is occupied by agents"""
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
            if hasattr(aDestinationCell, 'getMaxLayer'):
                max_layer = aDestinationCell.getMaxLayer(self.type)
                
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
            # Update view position
            if self.view:
                self.view.updatePositionFromCell()
                self.view.show()  # Ensure view is visible
                self.updateView()
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
            # Get all tiles of the same type at the same position on the source cell
            if hasattr(old_cell, 'getTilesAtPosition'):
                remaining_tiles = old_cell.getTilesAtPosition(old_position, tile_type)
                # Exclude this tile from the list
                remaining_tiles = [t for t in remaining_tiles if t != self]
                
                # If there are remaining tiles, reorganize their layers (compact layers)
                if remaining_tiles:
                    # Sort by current layer
                    remaining_tiles.sort(key=lambda t: t.layer)
                    # Reassign layers starting from 1, maintaining relative order
                    for i, tile in enumerate(remaining_tiles, start=1):
                        tile.setLayer(i)
            
            # Remove from current cell
            if hasattr(old_cell, 'removeTile'):
                old_cell.removeTile(self)
            
            # Move to new cell
            self.cell = aDestinationCell
            
            # Determine appropriate layer on destination cell
            # Check if there are already tiles of the same type at the same position
            if hasattr(aDestinationCell, 'getMaxLayer'):
                max_layer = aDestinationCell.getMaxLayer(tile_type)
                
                if max_layer > 0:
                    # There are tiles of the same type at this position
                    # Set layer to max_layer + 1 to stack on top
                    self.setLayer(max_layer + 1)
                else:
                    # No tiles of the same type at this position
                    # Reset to default layer (1) for a clean start
                    self.setLayer(1)
            
            # Register with new cell
            if hasattr(aDestinationCell, 'addTile'):
                aDestinationCell.addTile(self)
            
            # Update view position
            if self.view:
                self.view.updatePositionFromCell()
                self.view.show()  # Ensure view is visible
                self.updateView()
            
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
        """Flip the tile to show the other face"""
        if self.face == "front":
            self.face = "back"
        else:
            self.face = "front"
        if self.view:
            self.view.update()

    # ============================================================================
    # OTHER MODELER METHODS
    # ============================================================================

    def __MODELER_METHODS__OTHER__(self):
        pass

