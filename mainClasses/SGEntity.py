from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from collections import defaultdict
import random
from mainClasses.AttributeAndValueFunctionalities import *
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog, QMessageBox, QDialog, QLabel, QVBoxLayout
from mainClasses.SGEventHandlerGuide import *
from mainClasses.SGEntityModel import SGEntityModel
from mainClasses.SGEntityView import SGEntityView

# Class who is in charged of entities : cells and agents
class SGEntity(SGEntityModel):
    """
    SGEntity - Base class for all entities (cells and agents)
    
    This class now uses Model-View architecture:
    - Inherits from SGEntityModel for data and business logic
    - Delegates UI to SGEntityView for display and interaction
    """
    
    def __init__(self, parent, classDef, size, attributesAndValues):
        # Initialize the model part without calling setValue during initialization
        # to avoid calling update() before view is created
        super().__init__(classDef, size, attributesAndValues)
        
        # Create and link the view first
        self.view = SGEntityView(self, parent)
        self.setView(self.view)
        
        # Now initialize attributes (this will call setValue which calls update)
        self.initAttributesAndValuesWith(attributesAndValues)
        
        # Legacy compatibility: maintain direct access to view methods
        # These will be removed in future versions
        self._legacy_ui_methods = {
            'show': self.view.show,
            'hide': self.view.hide,
            'update': self.view.update,
            'setGeometry': self.view.setGeometry,
            'move': self.view.move,
            'resize': self.view.resize,
            'setVisible': self.view.setVisible,
            'isVisible': self.view.isVisible,
            'rect': self.view.rect,
            'mapToGlobal': self.view.mapToGlobal,
            'setContextMenuPolicy': self.view.setContextMenuPolicy,
            'customContextMenuRequested': self.view.customContextMenuRequested,
        }
        
        # Type identification attributes
        self.isEntity = True
        self.isCell = False
        self.isAgent = False

    # Legacy UI method delegation
    def show(self):
        """Show the entity view"""
        self.view.show()
    
    def hide(self):
        """Hide the entity view"""
        self.view.hide()
    
    def update(self):
        """Update the entity view"""
        self.view.update()
    
    def setGeometry(self, *args, **kwargs):
        """Set geometry of the entity view"""
        self.view.setGeometry(*args, **kwargs)
    
    def move(self, *args, **kwargs):
        """Move the entity view"""
        self.view.move(*args, **kwargs)
    
    def resize(self, *args, **kwargs):
        """Resize the entity view"""
        self.view.resize(*args, **kwargs)
    
    def setVisible(self, *args, **kwargs):
        """Set visibility of the entity view"""
        self.view.setVisible(*args, **kwargs)
    
    def isVisible(self):
        """Check if entity view is visible"""
        return self.view.isVisible()
    
    def rect(self):
        """Get rectangle of the entity view"""
        return self.view.rect()
    
    def mapToGlobal(self, *args, **kwargs):
        """Map to global coordinates"""
        return self.view.mapToGlobal(*args, **kwargs)
    
    def setContextMenuPolicy(self, *args, **kwargs):
        """Set context menu policy"""
        self.view.setContextMenuPolicy(*args, **kwargs)
    
    @property
    def customContextMenuRequested(self):
        """Get custom context menu requested signal"""
        return self.view.customContextMenuRequested

    # Legacy compatibility methods that delegate to view
    def getColor(self):
        """Get color - delegates to view"""
        return self.view.getColor()
    
    def getBorderColorAndWidth(self):
        """Get border color and width - delegates to view"""
        return self.view.getBorderColorAndWidth()
    
    def getImage(self):
        """Get image - delegates to view"""
        return self.view.getImage()
    
    def rescaleImage(self, image):
        """Rescale image - delegates to view"""
        return self.view.rescaleImage(image)
    
    def init_contextMenu(self):
        """Initialize context menu - delegates to view"""
        self.view.init_contextMenu()
    
    def show_context_menu(self, point):
        """Show context menu - delegates to view"""
        self.view.show_context_menu(point)
    
    # Legacy compatibility: maintain old method name
    def show_contextMenu(self, point):
        """Show context menu - legacy method name"""
        self.view.show_contextMenu(point)

    # Model methods that are now inherited from SGEntityModel
    # These are kept for backward compatibility but delegate to the model
    
    def getRandomAttributValue(self, aAgentSpecies, aAtt):
        """Get random attribute value - delegates to model"""
        return super().getRandomAttributValue(aAgentSpecies, aAtt)
    
    def readColorFromPovDef(self, aPovDef, aDefaultColor):
        """Read color from POV definition - delegates to model"""
        return super().readColorFromPovDef(aPovDef, aDefaultColor)
    
    def readColorAndWidthFromBorderPovDef(self, aBorderPovDef, aDefaultColor, aDefaultWidth):
        """Read color and width from border POV definition - delegates to model"""
        return super().readColorAndWidthFromBorderPovDef(aBorderPovDef, aDefaultColor, aDefaultWidth)
    
    def getObjectIdentiferForJsonDumps(self):
        """Get object identifier for JSON dumps - delegates to model"""
        return super().getObjectIdentiferForJsonDumps()
    
    def addWatcher(self, aIndicator):
        """Add watcher - delegates to model"""
        super().addWatcher(aIndicator)
    
    def updateWatchersOnAttribute(self, aAtt):
        """Update watchers on attribute - delegates to model"""
        super().updateWatchersOnAttribute(aAtt)
    
    def getListOfStepsData(self, startStep=None, endStep=None):
        """Get list of steps data - delegates to model"""
        return super().getListOfStepsData(startStep, endStep)
    
    def isDeleted(self):
        """Check if entity is deleted - delegates to model"""
        return super().isDeleted()
    
    def doAction(self, aLambdaFunction):
        """Do action - delegates to model"""
        super().doAction(aLambdaFunction)
    
    def entDef(self):
        """Get entity definition - delegates to model"""
        return super().entDef()

    # New Model-View specific methods
    def getView(self):
        """Get the entity view"""
        return self.view
    
    def setView(self, view):
        """Set the entity view"""
        self.view = view
        if view:
            view.entity_model = self
    
    def updateView(self):
        """Update the entity view"""
        if self.view:
            self.view.update()
    
