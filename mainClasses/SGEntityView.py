from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog, QMessageBox, QDialog, QLabel, QVBoxLayout
from mainClasses.SGEventHandlerGuide import *

class SGEntityView(QtWidgets.QWidget, SGEventHandlerGuide):
    """
    View class for SGEntity - handles all UI and display logic
    Separated from the model to enable Model-View architecture
    """
    
    def __init__(self, entity_model, parent=None):
        """
        Initialize the entity view
        
        Args:
            entity_model: The SGEntity model instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.entity_model = entity_model
        self.type = entity_model.type
        self.id = entity_model.id
        self.privateID = entity_model.privateID
        self.model = entity_model.model
        self.shape = entity_model.shape
        self.size = entity_model.size
        self.borderColor = entity_model.borderColor
        self.isDisplay = entity_model.isDisplay
        
        # Define highlighting
        self.highlightEffect = None
        self.isHighlighted = False
        
        # Set the contextual and gameAction controller
        self.init_contextMenu()
    
    def getColor(self):
        """Get the color for display based on POV settings"""
        if self.isDisplay == False: 
            return Qt.transparent
            
        aChoosenPov = self.model.getCheckedSymbologyOfEntity(self.type.name)
        aPovDef = self.type.povShapeColor.get(aChoosenPov)
        aDefaultColor = self.type.defaultShapeColor
        return self.readColorFromPovDef(aPovDef, aDefaultColor)

    def getBorderColorAndWidth(self):
        """Get the border color and width for display"""
        if self.isDisplay == False: 
            return Qt.transparent
            
        aChoosenPov = self.model.getCheckedSymbologyOfEntity(self.type.name, borderSymbology=True)
        aBorderPovDef = self.type.povBorderColorAndWidth.get(aChoosenPov)
        aDefaultColor = self.type.defaultBorderColor
        aDefaultWidth = self.type.defaultBorderWidth
        return self.readColorAndWidthFromBorderPovDef(aBorderPovDef, aDefaultColor, aDefaultWidth)
    
    def getImage(self):
        """Get the image for display based on POV settings"""
        if self.isDisplay == False: 
            return None
            
        aChoosenPov = self.model.getCheckedSymbologyOfEntity(self.type.name)
        aPovDef = self.type.povShapeColor.get(aChoosenPov)
        if aPovDef is None: 
            return None
            
        aAtt = list(aPovDef.keys())[0]
        aDictOfValueAndImage = list(aPovDef.values())[0]
        aImage = aDictOfValueAndImage.get(self.entity_model.value(aAtt))     

        if aImage is not None and isinstance(aImage, QPixmap):
            return aImage 
        else:
            return None
    
    def rescaleImage(self, image):
        """Rescale image to fit entity size"""
        imageWidth = image.width()
        imageHeight = image.height()

        if imageWidth == 0 or imageHeight == 0: 
            raise ValueError('Image size is not valid')
            
        entityWidth = self.size
        entityHeight = self.size

        if (imageHeight / imageWidth) < (entityHeight / entityWidth):
            scaled_image = image.scaledToHeight(entityHeight, Qt.SmoothTransformation)
        else:
            scaled_image = image.scaledToWidth(entityWidth, Qt.SmoothTransformation)
            
        # Calculate target rectangle for drawing
        x_offset = (entityWidth - scaled_image.width()) // 2
        y_offset = (entityHeight - scaled_image.height()) // 2
        target_rect = QRect(x_offset, y_offset, scaled_image.width(), scaled_image.height())

        return target_rect, scaled_image

    def readColorFromPovDef(self, aPovDef, aDefaultColor):
        """Read color from POV definition"""
        if aPovDef is None: 
            return aDefaultColor
            
        aAtt = list(aPovDef.keys())[0]
        aDictOfValueAndColor = list(aPovDef.values())[0]
        aColor = aDictOfValueAndColor.get(self.entity_model.value(aAtt))
        return aColor if aColor is not None else aDefaultColor

    def readColorAndWidthFromBorderPovDef(self, aBorderPovDef, aDefaultColor, aDefaultWidth):
        """Read color and width from border POV definition"""
        if aBorderPovDef is None: 
            return {'color': aDefaultColor, 'width': aDefaultWidth}
            
        aAtt = list(aBorderPovDef.keys())[0]
        aDictOfValueAndColorWidth = list(aBorderPovDef.values())[0]
        
        # Check if the attribute exists in the model
        if not hasattr(self.entity_model, 'value') or not hasattr(self.entity_model, 'dictAttributes') or aAtt not in self.entity_model.dictAttributes:
            return {'color': aDefaultColor, 'width': aDefaultWidth}
            
        dictColorAndWidth = aDictOfValueAndColorWidth.get(self.entity_model.value(aAtt))
        
        if dictColorAndWidth is None:
            return {'color': aDefaultColor, 'width': aDefaultWidth}
        if not isinstance(dictColorAndWidth, dict): 
            raise ValueError('wrong format')
            
        return dictColorAndWidth

    # Handle the contextual menu and GameAction controller
    def init_contextMenu(self):
        """Initialize context menu"""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_contextMenu)
    
    def show_contextMenu(self, point):
        """Show context menu for the entity"""
        menu = QMenu(self)

        for anItem in self.type.attributesToDisplayInContextualMenu:
            aAtt = anItem['att']
            aLabel = anItem['label']
            aValue = self.entity_model.value(aAtt)
            text = aLabel + "=" + str(aValue)
            option = QAction(text, self)
            menu.addAction(option)

        player = self.model.getCurrentPlayer()
        if not player == "Admin":        
            actions = player.getAllGameActionsOn(self.entity_model)
            for aAction in actions:
                if aAction.setControllerContextualMenu:
                    if aAction.checkAuthorization(self.entity_model):
                        aMenuAction = QAction(aAction.nameToDisplay, self)
                        aMenuAction.setCheckable(False)
                        aMenuAction.triggered.connect(lambda _, a=aAction: a.perform_with(self.entity_model))
                        menu.addAction(aMenuAction)

        if not menu.isEmpty() and self.rect().contains(point):
            menu.exec_(self.mapToGlobal(point))

    def getObjectIdentiferForJsonDumps(self):
        """Get object identifier for JSON serialization"""
        dict = {}
        dict['name'] = self.type.name
        dict['id'] = self.id
        return dict

    def isDeleted(self):
        """Check if entity is deleted"""
        return not self.isDisplay

    def entDef(self): #todo to remove (obsolete)
        """Returns the 'entity definition' class of the entity"""
        return self.type
