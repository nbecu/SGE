from collections import defaultdict
import random
from mainClasses.AttributeAndValueFunctionalities import *

class SGEntityModel(AttributeAndValueFunctionalities):
    """
    Model class for SGEntity - contains all data and business logic
    Separated from the view to enable Model-View architecture
    """
    
    def __init__(self, classDef, size, attributesAndValues):
        """
        Initialize the entity model
        
        Args:
            classDef: The entity definition class
            size: Size of the entity
            attributesAndValues: Initial attributes and values
        """
        self.classDef = classDef
        self.id = self.classDef.nextId()
        self.privateID = self.classDef.entityName + str(self.id)
        self.model = self.classDef.model
        self.shape = self.classDef.shape
        self.size = size
        self.borderColor = self.classDef.defaultBorderColor
        self.isDisplay = True
        
        # Define variables to handle the history 
        self.history = {}
        self.history["value"] = defaultdict(list)
        self.watchers = {}
        
        # Set the attributes
        self.initAttributesAndValuesWith(attributesAndValues)
        self.owner = "admin"
        
        # Reference to the view
        self.view = None
    
    def initAttributesAndValuesWith(self, thisAgentAttributesAndValues):
        """Initialize attributes and values"""
        self.dictAttributes = {}
        if thisAgentAttributesAndValues is None: 
            thisAgentAttributesAndValues = {}
        
        for aAtt, aDefaultValue in self.classDef.attributesDefaultValues.items():
            if not aAtt in thisAgentAttributesAndValues.keys():
                thisAgentAttributesAndValues[aAtt] = aDefaultValue
        for aAtt, valueToSet in thisAgentAttributesAndValues.items():
            if callable(valueToSet):
                aValue = valueToSet()
                self.setValue(aAtt, aValue)
            else:
                self.setValue(aAtt, valueToSet)

    def getRandomAttributValue(self, aAgentSpecies, aAtt):
        """Get random attribute value"""
        if aAgentSpecies.dictAttributes is not None:
            values = list(aAgentSpecies.dictAttributes[aAtt])
            number = len(values)
            aRandomValue = random.randint(0, number - 1)          
        return aRandomValue

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
        return [{**{'entityType': self.classDef.entityType(), 'entityName': self.classDef.entityName, 'id': self.id}, **aStepData} for aStepData in aList]

    def isDeleted(self):
        """Check if entity is deleted"""
        return not self.isDisplay

    def doAction(self, aLambdaFunction):
        """Perform action on the entity"""
        aLambdaFunction(self)

    def entDef(self):
        """Returns the 'entity definition' class of the entity"""
        return self.classDef

    def getObjectIdentiferForJsonDumps(self):
        """Get object identifier for JSON serialization"""
        dict = {}
        dict['entityName'] = self.classDef.entityName
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
