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
                 face="front", frontImage=None, backImage=None, frontColor=None, backColor=None, layer=0):
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
            layer: Z-order/layer for rendering (default: 0)
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

    # Position and placement methods
    def getCell(self):
        """Get the cell where this tile is placed"""
        return self.cell
    
    def getCoords(self):
        """Get the coordinates of the cell where this tile is placed"""
        if self.cell:
            return (self.cell.xCoord, self.cell.yCoord)
        return None
    
    def placeOn(self, cell, position=None):
        """
        Place the tile on a cell
        
        Args:
            cell: The cell to place the tile on
            position: Position on the cell (optional, uses current position if None)
        """
        if cell is None:
            raise ValueError('Cell cannot be None')
        
        # Remove from old cell if any
        if self.cell and hasattr(self.cell, 'removeTile'):
            self.cell.removeTile(self)
        
        # Place on new cell
        self.cell = cell
        if position is not None:
            self.position = position
        
        # Register with new cell
        if hasattr(cell, 'addTile'):
            cell.addTile(self)
        
        # Update view position
        if self.view:
            self.view.updatePositionFromCell()
    
    def moveTo(self, cell, position=None):
        """
        Move the tile to another cell (alias for placeOn)
        
        Args:
            cell: The cell to move the tile to
            position: Position on the cell (optional)
        """
        self.placeOn(cell, position)
    
    # Layer management methods
    def setLayer(self, layer):
        """Set the layer/z-index of the tile"""
        self.layer = layer
        if self.view:
            self.view.update()
    
    def getLayer(self):
        """Get the layer/z-index of the tile"""
        return self.layer
    
    # Face management methods
    def flip(self):
        """Flip the tile to show the other face"""
        if self.face == "front":
            self.face = "back"
        else:
            self.face = "front"
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
    
    def getFace(self):
        """Get the current visible face"""
        return self.face
    
    def isFaceFront(self):
        """Check if the front face is visible"""
        return self.face == "front"
    
    def isFaceBack(self):
        """Check if the back face is visible"""
        return self.face == "back"
    
    # Blocking methods
    def doesBlockStacking(self):
        """Check if this tile blocks stacking of other tiles on top"""
        return self.blocksStacking
    
    def doesBlockAgentPlacement(self):
        """Check if this tile blocks agent placement"""
        return self.blocksAgentPlacement
    
    # Agent interaction methods
    def getAgentsHere(self):
        """Get all agents on the cell where this tile is placed"""
        if self.cell and hasattr(self.cell, 'agents'):
            return self.cell.agents
        return []
    
    def isOccupied(self):
        """Check if the tile's cell is occupied by agents"""
        agents = self.getAgentsHere()
        return len(agents) > 0
    
    # Delete method
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

