from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog, QMessageBox, QDialog, QLabel, QVBoxLayout, QToolTip
from PyQt5.QtGui import QCursor
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
        self.face = tile_model.face
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
        if self.face == "front":
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
                # For imageTile, we already drew the image, just draw border if needed
                if tileShape == "rectTile":
                    self.setGeometry(x, y, tile_size, tile_size)
                    painter.drawRect(0, 0, tile_size, tile_size)
                elif tileShape == "imageTile":
                    # Image already drawn, just set geometry
                    self.setGeometry(x, y, tile_size, tile_size)
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
    
    def updateFromModel(self):
        """Update view properties from model"""
        if self.tile_model:
            self.size = self.tile_model.size  # Update size from model (for zoom)
            self.saveSize = self.tile_model.saveSize
            self.face = self.tile_model.face
            self.frontImage = self.tile_model.frontImage
            self.backImage = self.tile_model.backImage
            self.frontColor = self.tile_model.frontColor
            self.backColor = self.tile_model.backColor
            self.layer = self.tile_model.layer
            self.position = self.tile_model.position
            self.update()

