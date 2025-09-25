from collections import defaultdict
import random
from mainClasses.AttributeAndValueFunctionalities import *

class SGEntity(AttributeAndValueFunctionalities):
    """
    SGEntity - Base class for all entities (cells and agents)
    Contains all data and business logic for entities
    Separated from the view to enable Model-View architecture
    """
    
    def __init__(self, type, size, attributesAndValues):
        """
        Initialize the entity model
        
        Args:
            type: The entity definition class
            size: Size of the entity
            attributesAndValues: Initial attributes and values
        """
        self.type = type
        self.id = self.type.nextId()
        self.privateID = self.type.name + str(self.id)
        self.model = self.type.model
        self.shape = self.type.shape
        self.size = size
        self.borderColor = self.type.defaultBorderColor
        self.isDisplay = True
        
        # Define variables to handle the history 
        self.history = {}
        self.history["value"] = defaultdict(list)
        self.watchers = {}
        
        # Set the attributes (will be called by child classes after view is created)
        # self.initAttributesAndValuesWith(attributesAndValues)
        self.owner = "admin"
        
        # Reference to the view
        self.view = None
    
    def initAttributesAndValuesWith(self, thisAgentAttributesAndValues):
        """Initialize attributes and values"""
        self.dictAttributes = {}
        if thisAgentAttributesAndValues is None: 
            thisAgentAttributesAndValues = {}
        
        for aAtt, aDefaultValue in self.type.attributesDefaultValues.items():
            if not aAtt in thisAgentAttributesAndValues.keys():
                thisAgentAttributesAndValues[aAtt] = aDefaultValue
        for aAtt, valueToSet in thisAgentAttributesAndValues.items():
            if callable(valueToSet):
                aValue = valueToSet()
                self.setValue(aAtt, aValue)
            else:
                self.setValue(aAtt, valueToSet)

    def readColorFromPovDef(self, aPovDef, aDefaultColor):
        """Read color from POV definition"""
        if aPovDef is None: 
            return aDefaultColor
        aAtt = list(aPovDef.keys())[0]
        aDictOfValueAndColor = list(aPovDef.values())[0]
        aColor = aDictOfValueAndColor.get(self.value(aAtt))
        return aColor if aColor is not None else aDefaultColor

    def readColorAndWidthFromBorderPovDef(self, aBorderPovDef, aDefaultColor, aDefaultWidth):
        """Read color and width from border POV definition"""
        if aBorderPovDef is None: 
            return {'color': aDefaultColor, 'width': aDefaultWidth}
        aAtt = list(aBorderPovDef.keys())[0]
        aDictOfValueAndColorWidth = list(aBorderPovDef.values())[0]
        dictColorAndWidth = aDictOfValueAndColorWidth.get(self.value(aAtt))
        if dictColorAndWidth is None:  # Vérification si la valeur n'existe pas
            raise ValueError(f'BorderPov cannot work because {self.privateID} has no value for attribute "{aAtt}"')
        if not isinstance(dictColorAndWidth, dict): 
            raise ValueError('wrong format')
        return dictColorAndWidth

    def getRandomAttributValue(self, aAgentSpecies, aAtt):
        """Get random attribute value"""
        if aAgentSpecies.dictAttributes is not None and aAtt in aAgentSpecies.dictAttributes:
            values = list(aAgentSpecies.dictAttributes[aAtt])
            number = len(values)
            aRandomValue = random.randint(0, number - 1)          
            return aRandomValue
        return None

    def addWatcher(self, aIndicator):
        """Add a watcher for attribute changes"""
        aAtt = aIndicator.attribute
        if aAtt not in self.watchers.keys():
            self.watchers[aAtt] = []
        self.watchers[aAtt].append(aIndicator)

    def updateWatchersOnAttribute(self, aAtt):
        """Update watchers when an attribute changes"""
        for watcher in self.watchers.get(aAtt, []):
            watcher.checkAndUpdate()

    def getListOfStepsData(self, startStep=None, endStep=None):
        """Get list of step data"""
        aList = self.getListOfUntagedStepsData(startStep, endStep)
        return [{**{'category': self.type.category(), 'name': self.type.name, 'id': self.id}, **aStepData} for aStepData in aList]

    def isDeleted(self):
        """Check if entity is deleted"""
        return not self.isDisplay

    def doAction(self, aLambdaFunction):
        """Perform action on the entity"""
        aLambdaFunction(self)

    def entDef(self):
        """Returns the 'entity definition' class of the entity"""
        return self.type

    def getObjectIdentiferForJsonDumps(self):
        """Get object identifier for JSON serialization"""
        dict = {}
        dict['entityName'] = self.type.name
        dict['id'] = self.id
        return dict

    def setView(self, view):
        """Set the view for this model"""
        self.view = view

    def getView(self):
        """Get the view for this model"""
        return self.view

    def updateView(self):
        """Update the view when model changes"""
        if self.view:
            self.view.update()

    # ============================================================================
    # LEGACY UI METHOD DELEGATION
    # ============================================================================
    
    def show(self):
        """Show the entity view"""
        if hasattr(self, 'view') and self.view:
            self.view.show()
    
    def hide(self):
        """Hide the entity view"""
        if hasattr(self, 'view') and self.view:
            self.view.hide()
    
    def update(self):
        """Update the entity view"""
        if hasattr(self, 'view') and self.view:
            self.view.update()
    
    #todo obsolete function
    #  def move(self, *args, **kwargs):
    #     """Move the entity view"""
    #     if hasattr(self, 'view') and self.view:
    #         self.view.move(*args, **kwargs)
    
    def setGeometry(self, *args, **kwargs):
        """Set geometry of the entity view"""
        if hasattr(self, 'view') and self.view:
            self.view.setGeometry(*args, **kwargs)
    
    def resize(self, *args, **kwargs):
        """Resize the entity view"""
        if hasattr(self, 'view') and self.view:
            self.view.resize(*args, **kwargs)
    
    def setVisible(self, *args, **kwargs):
        """Set visibility of the entity view"""
        if hasattr(self, 'view') and self.view:
            self.view.setVisible(*args, **kwargs)
    
    def isVisible(self):
        """Check if entity view is visible"""
        if hasattr(self, 'view') and self.view:
            return self.view.isVisible()
        return False
    
    def rect(self):
        """Get rectangle of the entity view"""
        if hasattr(self, 'view') and self.view:
            return self.view.rect()
        return None
    
    def mapToGlobal(self, *args, **kwargs):
        """Map to global coordinates"""
        if hasattr(self, 'view') and self.view:
            return self.view.mapToGlobal(*args, **kwargs)
        return None
    
    def setAcceptDrops(self, *args, **kwargs):
        """Set accept drops"""
        if hasattr(self, 'view') and self.view:
            self.view.setAcceptDrops(*args, **kwargs)
    
    def grab(self):
        """Grab the entity view"""
        if hasattr(self, 'view') and self.view:
            return self.view.grab()
        return None
    
    # Event delegation methods
    def paintEvent(self, event):
        """Paint event - delegates to view"""
        if hasattr(self, 'view') and self.view:
            self.view.paintEvent(event)
    
    def getRegion(self):
        """Get region - delegates to view"""
        if hasattr(self, 'view') and self.view:
            return self.view.getRegion()
        return None
    
    def mousePressEvent(self, event):
        """Mouse press event - delegates to view"""
        if hasattr(self, 'view') and self.view:
            self.view.mousePressEvent(event)