from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGEntity import SGEntity
from mainClasses.SGCellModel import SGCellModel
from mainClasses.SGCellView import SGCellView
# from mainClasses.gameAction.SGCreate import *  # Commented to avoid circular import
# from mainClasses.gameAction.SGDelete import *   # Commented to avoid circular import
# from mainClasses.gameAction.SGModify import *   # Commented to avoid circular import
# from mainClasses.gameAction.SGMove import *     # Commented to avoid circular import
# from mainClasses.gameAction.SGActivate import * # Commented to avoid circular import
import random
# from mainClasses.gameAction.SGMove import SGMove
   
#Class who is responsible of the declaration a cell
class SGCell(SGCellModel):
    """
    SGCell - Cell class for grid-based simulations
    
    This class now uses Model-View architecture:
    - Inherits from SGCellModel for data and business logic
    - Delegates UI to SGCellView for display and interaction
    """
    
    def __init__(self, classDef, x, y, defaultImage):
        # Initialize the model part
        super().__init__(classDef, x, y, defaultImage)
        
        # Create and link the view
        self.view = SGCellView(self, classDef.grid)
        self.setView(self.view)
        
        # Type identification attributes
        self.isEntity = True
        self.isCell = True
        self.isAgent = False

    # Legacy UI method delegation
    def show(self):
        """Show the cell view"""
        self.view.show()
    
    def hide(self):
        """Hide the cell view"""
        self.view.hide()
    
    def update(self):
        """Update the cell view"""
        self.view.update()
    
    def setGeometry(self, *args, **kwargs):
        """Set geometry of the cell view"""
        self.view.setGeometry(*args, **kwargs)
    
    def move(self, *args, **kwargs):
        """Move the cell view and update all agent positions"""
        self.view.move(*args, **kwargs)
        
        # Update position of all agents in this cell
        for agent in self.agents:
            if hasattr(agent, 'view') and agent.view:
                agent.view.updatePositionFromCell()
    
    def resize(self, *args, **kwargs):
        """Resize the cell view"""
        self.view.resize(*args, **kwargs)
    
    def setVisible(self, *args, **kwargs):
        """Set visibility of the cell view"""
        self.view.setVisible(*args, **kwargs)
    
    def isVisible(self):
        """Check if cell view is visible"""
        return self.view.isVisible()
    
    def rect(self):
        """Get rectangle of the cell view"""
        return self.view.rect()
    
    def mapFromGlobal(self, *args, **kwargs):
        """Map from global coordinates"""
        return self.view.mapFromGlobal(*args, **kwargs)
    
    def setAcceptDrops(self, *args, **kwargs):
        """Set accept drops"""
        self.view.setAcceptDrops(*args, **kwargs)

    # Legacy compatibility methods that delegate to view
    def paintEvent(self, event):
        """Paint event - delegates to view"""
        self.view.paintEvent(event)
    
    def getRegion(self):
        """Get region - delegates to view"""
        return self.view.getRegion()
    
    def mousePressEvent(self, event):
        """Mouse press event - delegates to view"""
        self.view.mousePressEvent(event)

    def dropEvent(self, e):
        """Drop event - delegates to view"""
        self.view.dropEvent(e)

    # Model methods that are now inherited from SGCellModel
    # These are kept for backward compatibility but delegate to the model
    
    def getId(self):
        """Get cell ID - delegates to model"""
        return super().getId()
    
    def zoomIn(self):
        """Zoom in - delegates to model"""
        super().zoomIn()
        self.updateView()
    
    def zoomOut(self):
        """Zoom out - delegates to model"""
        super().zoomOut()
        self.updateView()
    
    def zoomFit(self):
        """Zoom fit - delegates to model"""
        super().zoomFit()
        self.updateView()
    
    def convert_coordinates(self, global_pos):
        """Convert coordinates - delegates to model"""
        return super().convert_coordinates(global_pos)

    # New Model-View specific methods
    def getView(self):
        """Get the cell view"""
        return self.view
    
    def setView(self, view):
        """Set the cell view"""
        self.view = view
        if view:
            view.cell_model = self
    
    def updateView(self):
        """Update the cell view"""
        if self.view:
            self.view.update()