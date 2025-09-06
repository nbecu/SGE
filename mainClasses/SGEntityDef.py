from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGCell import SGCell
from mainClasses.SGAgent import SGAgent
from mainClasses.SGEntity import SGEntity
from mainClasses.AttributeAndValueFunctionalities import *
from mainClasses.SGIndicator import SGIndicator
from mainClasses.SGModelAction import SGModelAction_OnEntities
from mainClasses.SGExtensions import *
import numpy as np
from collections import Counter, defaultdict
import random
from typing import Union
# Définition de SGEntityDef
class SGEntityDef(AttributeAndValueFunctionalities):
    def __init__(self, sgModel, entityName, shape, defaultsize, entDefAttributesAndValues, defaultShapeColor):
        self.model = sgModel
        self.entityName = entityName
        self.dictAttributes = entDefAttributesAndValues if entDefAttributesAndValues is not None else {}
        self.attributesDefaultValues = {}
        self.shape = shape
        self.defaultsize = defaultsize
        self.defaultShapeColor = defaultShapeColor
        self.defaultBorderColor = Qt.black
        self.defaultBorderWidth = 1
        self.povShapeColor = {}
        self.povBorderColorAndWidth = {}
        self.shapeColorClassif = {}  # Classif will replace pov
        self.borderColorClassif = {}  # Classif will replace pov
        
        # Type identification attributes
        self.isAgentDef = False
        self.isCellDef = False
        self.isAGrid = False
        
        #Define variables to handle the history 
        self.history={}
        self.history["value"]=defaultdict(list)
        self.watchers = {}
        self.IDincr = 0
        self.entities = []
        self.initAttributes(entDefAttributesAndValues)
        self.listOfStepStats = []
        self.attributesToDisplayInContextualMenu = []
        self.attributesToDisplayInUpdateMenu = []

    def nextId(self):
        """
        Generate and return the next available ID for entities.
        
        Returns:
            int: The next ID number
        """
        self.IDincr +=1
        return self.IDincr
    
    def entityType(self):
        """
        Return the type of entity this definition represents.
        
        Returns:
            str: 'Cell' for cell definitions, 'Agent' for agent definitions
            
        Raises:
            ValueError: If the entity type is not recognized
        """
        if self.isCellDef: return 'Cell'
        elif self.isAgentDef: return 'Agent'
        else: raise ValueError('Wrong or new entity type')

    # ============================================================================
    # DEVELOPER METHODS
    # ============================================================================
    def addWatcher(self, aIndicator):
        """
        Add a watcher (indicator) to monitor attribute changes.
        
        Args:
            aIndicator (SGIndicator): The indicator to add as a watcher
        """
        if aIndicator.attribute is None:
            aAtt = 'nb'
        else: aAtt = aIndicator.attribute
        if aAtt not in self.watchers.keys():
            self.watchers[aAtt]=[]
        self.watchers[aAtt].append(aIndicator)

    def updateWatchersOnAttribute(self, aAtt):
        """
        Update all watchers monitoring a specific attribute.
        
        Args:
            aAtt (str): The attribute name that changed
        """
        watchers_with_condition_on_entities = [item for sublist in self.watchers.values() for item in sublist if item.conditionsOnEntities]  # Filtrage des éléments
        watchers_of_the_changed_attribute = self.watchers.get(aAtt,[])
        for watcher in (watchers_of_the_changed_attribute + watchers_with_condition_on_entities):
            watcher.checkAndUpdate()

    def updateWatchersOnAllAttributes(self):
        """
        Update all watchers monitoring any attribute (except population).
        """
        for aAtt, listOfWatchers in self.watchers.items():
            if aAtt == 'nb': continue
            for watcher in listOfWatchers:
                watcher.checkAndUpdate()

    def updateWatchersOnPop(self):
        """
        Update watchers monitoring population changes.
        """
        self.updateWatchersOnAttribute('nb')
    
    def updateAllWatchers(self):
        """
        Update all watchers regardless of what they monitor.
        """
        for listOfWatchers in self.watchers.values():
            for watcher in listOfWatchers:
                watcher.checkAndUpdate()
                    
    def getColorOrColorandWidthOfFirstOccurenceOfAttAndValue(self, att, value):
        """
        Get the color or color+width for the first occurrence of an attribute-value pair.
        
        Args:
            att (str): Attribute name
            value: Attribute value
            
        Returns:
            QColor or dict: Color for shape POV, or dict with color+width for border POV
        """
        # Check first the shape colorDict 
        for aDictWith_Att_ColorDict in list(self.povShapeColor.values()):
            aAtt=list(aDictWith_Att_ColorDict.keys())[0]
            aColorDict=aDictWith_Att_ColorDict[aAtt]
            if aAtt == att:
                aColor = aColorDict.get(value)
                if aColor is not None: return aColor
        #Then check if there is a correspondance in the border colorDict
        for aDictWith_Att_ColorDict in list(self.povBorderColorAndWidth.values()):
            aAtt=list(aDictWith_Att_ColorDict.keys())[0]
            aDictOfDictsOfColorAndWidth=aDictWith_Att_ColorDict[aAtt]
            if aAtt == att:
                dictOfColorAndWidth = aDictOfDictsOfColorAndWidth.get(value)
                return dictOfColorAndWidth
        # If no matches are found, retunr the default color
        return self.defaultShapeColor

    def addWidthInPovDictOfColors(self, borderWidth, dictOfColor): 
        """
        Add width information to a dictionary of colors for border POV.
        
        Args:
            borderWidth (int): Width of the border
            dictOfColor (dict): Dictionary mapping values to colors
            
        Returns:
            dict: Dictionary mapping values to dicts with 'color' and 'width' keys
        """
        dictOfColorAndWidth ={}
        for aKey, aColor in dictOfColor.items():
            dictOfColorAndWidth[aKey] = {'color':aColor,'width':borderWidth}
        return dictOfColorAndWidth
    
    def reformatDictOfColorAndWidth(self, dictOfColorAndWidth):
        """
        Reformat a dictionary from list format to dict format for color and width.
        
        Args:
            dictOfColorAndWidth (dict): Dictionary with values as [color, width] lists
            
        Returns:
            dict: Dictionary with values as {'color': color, 'width': width} dicts
        """
        reformatedDict ={}
        for aKey, aListOfColorAndWidth in dictOfColorAndWidth.items():
            reformatedDict[aKey] = {'color':aListOfColorAndWidth[0],'width':aListOfColorAndWidth[1]}
        return reformatedDict

    def calculateAndRecordCurrentStepStats(self):
        """
        Calculate and record statistics for the current simulation step.
        
        Records quantitative and qualitative statistics for all entities,
        including population count, attribute statistics, and distributions.
        """
        currentRound =self.model.roundNumber()
        currentPhase = self.model.phaseNumber()
        quantiAttributesStats ={}
        qualiAttributesStats ={}
        if self.entities: 
            listQuantiAttributes = []
            listQualiAttributes = []
            for aAtt,aVal in self.entities[0].dictAttributes.items():  
                if type(aVal) in [int,float]:
                    listQuantiAttributes.append(aAtt)
                elif type(aVal) == str:
                    listQualiAttributes.append(aAtt) 
                # else:
                #     raise TypeError("Only int float and str are allowed")
            for aAtt in listQuantiAttributes:
                listOfValues = [aEnt.value(aAtt) for aEnt in self.entities]
                quantiAttributesStats[aAtt] = {
                    'sum': np.sum(listOfValues),
                    'mean': np.mean(listOfValues),
                    'min': np.min(listOfValues),
                    'max': np.max(listOfValues),
                    'stdev': np.std(listOfValues),
                    'histo':np.histogram(listOfValues, bins='auto')
                    }
            for aAtt in listQualiAttributes:
                listOfValues = [aEnt.value(aAtt) for aEnt in self.entities]
                qualiAttributesStats[aAtt]=Counter(listOfValues)
                type(dict(Counter(listOfValues)))

        aData = {
                'entityType': self.entityType(),
                'entityName': self.entityName,
                'round': currentRound,
                'phase': currentPhase,
                'population': len(self.entities),
                'entDefAttributes': dict(filter(lambda i: type(i[1]) in[int,float],self.dictAttributes.items())),
                'quantiAttributes': quantiAttributesStats,
                'qualiAttributes': qualiAttributesStats
                    }    
        self.listOfStepStats.append(aData)

    def discoverAttributesAndValues(self):
        """
        Discovers all attributes and their possible values using multiple sources:
        1. Existing entities (real data)
        2. POVs (Points of View) - more specific, defined by modeler
        3. Default values from entityDef - fallback values
        
        Returns:
            dict: {attribute_name: [list_of_possible_values]}
        """
        discoveredAttrs = {}
        
        # Step 1: Scan all existing entities to discover attributes and values
        if self.entities:
            for entity in self.entities:
                if hasattr(entity, 'dictAttributes'):
                    for attr, value in entity.dictAttributes.items():
                        if attr not in discoveredAttrs:
                            discoveredAttrs[attr] = set()
                        discoveredAttrs[attr].add(value)
        
        # Step 2: Complete with POVs (Points of View) - more specific, defined by modeler
        if hasattr(self, 'povShapeColor'):
            for povName, povData in self.povShapeColor.items():
                for attribute, valueColorDict in povData.items():
                    if attribute not in discoveredAttrs:
                        discoveredAttrs[attribute] = set()
                    # Add all values from POVs
                    for value in valueColorDict.keys():
                        discoveredAttrs[attribute].add(value)
        
        if hasattr(self, 'povBorderColorAndWidth'):
            for povName, povData in self.povBorderColorAndWidth.items():
                for attribute, valueColorWidthDict in povData.items():
                    if attribute not in discoveredAttrs:
                        discoveredAttrs[attribute] = set()
                    # Add all values from border POVs
                    for value in valueColorWidthDict.keys():
                        discoveredAttrs[attribute].add(value)
        
        # Step 3: Complete with default values from entityDef - fallback values
        if hasattr(self, 'attributesDefaultValues'):
            for attr, defaultVal in self.attributesDefaultValues.items():
                if attr not in discoveredAttrs:
                    discoveredAttrs[attr] = set()
                
                if callable(defaultVal):
                    # For callable defaults, only add None if no other values were discovered
                    if len(discoveredAttrs[attr]) == 0:
                        discoveredAttrs[attr].add(None)  # None means "any value"
                else:
                    # For non-callable defaults, always add the value
                    discoveredAttrs[attr].add(defaultVal)
        
        # Convert sets to lists
        result = {}
        for attr, values in discoveredAttrs.items():
            result[attr] = list(values)
        
        return result

    # ============================================================================
    # MODELER METHODS
    # ============================================================================
    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================
    def setDefaultValue(self, aAtt, aDefaultValue):
        """
        Set a default value for a specific attribute.
        
        Args:
            aAtt (str): Name of the attribute
            aDefaultValue: Default value for the attribute (can be a callable)
        """
        self.attributesDefaultValues[aAtt] = aDefaultValue
    
    def setDefaultValues(self, aDictOfAttributesAndValues):
        """
        Set default values for multiple attributes.
        
        Args:
            aDictOfAttributesAndValues (dict): Dictionary mapping attribute names to their default values
        """
        for att, defValue in aDictOfAttributesAndValues.items():
            self.attributesDefaultValues[att] = defValue

    def setDefaultValues_randomChoice(self, mapping):
        """
        Set default values with automatic random choice conversion for lists/tuples.
        
        This convenience helper sets default values where each entry can be a scalar, 
        a callable, or a list/tuple of choices. If a value is a list/tuple, it is 
        automatically converted to a lambda that returns random.choice(value).
        
        Args:
            mapping (dict): Dictionary mapping attribute names to values or choice lists
            
        Example:
            setDefaultValues_randomChoice({
                "health": ["good", "bad"],
                "hunger": ("good", "bad"),
                "speed": 3
            })
        is equivalent to:
            setDefaultValues({
                "health": lambda: random.choice(["good", "bad"]),
                "hunger": lambda: random.choice(("good", "bad")),
                "speed": 3
            })
        """
        import random
        prepared = {}
        for att, val in mapping.items():
            if isinstance(val, (list, tuple)):
                prepared[att] = (lambda choices=tuple(val): (lambda: random.choice(choices)))()
            else:
                prepared[att] = val
        self.setDefaultValues(prepared)

    def setDefaultValues_randomNumeric(self, mapping):
        """
        Set default numeric values with automatic random distribution conversion.
        
        This convenience helper sets default values with automatic conversion to random
        distribution functions based on concise specification formats.
        
        Args:
            mapping (dict): Dictionary mapping attribute names to distribution specs
            
        Supported specs per attribute:
          - (min, max) of ints  -> lambda: random.randint(min, max)
          - (min, max) of floats-> lambda: random.uniform(min, max)
          - range(start, stop[, step]) -> lambda: random.randrange(start, stop+step, step)  [stop is INCLUSIVE]
          - {"uniform": (a, b)} -> lambda: random.uniform(a, b)
          - {"randint": (a, b)} -> lambda: random.randint(a, b)
          - {"normal": (mu, sigma)} or {"gauss": (mu, sigma)} -> lambda: random.gauss(mu, sigma)
          - {"choice": [v1, v2, ...]} -> lambda: random.choice([...])
        Any other value is forwarded as-is (including already-callable values).

        Example:
            setDefaultValues_randomNumeric({
                "age": (10, 18),              # randint 10..18
                "speed": (0.5, 2.0),          # uniform 0.5..2.0
                "index": range(0, 100, 5),    # randrange with stop inclusive (includes 100 if aligned)
                "height": {"normal": (170, 10)},
                "state": {"choice": ["A", "B", "C"]},
            })
        """
        import random
        import numbers
        prepared = {}
        for att, spec in mapping.items():
            # range() → make stop inclusive by adding one step
            if isinstance(spec, range):
                start, stop, step = spec.start, spec.stop, spec.step
                if step == 0:
                    prepared[att] = spec
                else:
                    inclusive_stop = stop + step
                    prepared[att] = (lambda a=start, b=inclusive_stop, c=step: (lambda: random.randrange(a, b, c)))()
            # tuple/list of 2 -> randint or uniform
            elif isinstance(spec, (list, tuple)) and len(spec) == 2:
                lo, hi = spec[0], spec[1]
                if isinstance(lo, numbers.Integral) and isinstance(hi, numbers.Integral):
                    prepared[att] = (lambda a=int(lo), b=int(hi): (lambda: random.randint(a, b)))()
                elif isinstance(lo, numbers.Real) and isinstance(hi, numbers.Real):
                    prepared[att] = (lambda a=float(lo), b=float(hi): (lambda: random.uniform(a, b)))()
                else:
                    prepared[att] = spec
            # dict distribution spec
            elif isinstance(spec, dict) and len(spec) == 1:
                name, params = next(iter(spec.items()))
                if name == "uniform" and isinstance(params, (list, tuple)) and len(params) == 2:
                    a, b = float(params[0]), float(params[1])
                    prepared[att] = (lambda x=a, y=b: (lambda: random.uniform(x, y)))()
                elif name in ("randint", "randrange") and isinstance(params, (list, tuple)) and len(params) >= 2:
                    a, b = int(params[0]), int(params[1])
                    prepared[att] = (lambda x=a, y=b: (lambda: random.randint(x, y)))()
                elif name in ("gauss", "normal") and isinstance(params, (list, tuple)) and len(params) == 2:
                    mu, sigma = float(params[0]), float(params[1])
                    prepared[att] = (lambda m=mu, s=sigma: (lambda: random.gauss(m, s)))()
                elif name == "choice" and isinstance(params, (list, tuple)):
                    choices = tuple(params)
                    prepared[att] = (lambda ch=choices: (lambda: random.choice(ch)))()
                else:
                    prepared[att] = spec
            else:
                prepared[att] = spec
        self.setDefaultValues(prepared)

    def setEntities(self, aAttribute, aValue, condition=None):
        """
        Set the value of attribut value of all entities

        Args:
            aAttribute (str): Name of the attribute to set
            aValue (str): Value to set the attribute to
            condition (lambda function): a condition on the entity can be used to select only some entities
        """
        for ent in self.getEntities(condition):
            ent.setValue(aAttribute, aValue)

    def setEntities_withColumn(self, aAttribute, aValue, aColumnNumber):
        """
        Set the value of attribut to all entities in a specified column

        Args:
            aAttribute (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
            aColumnNumber (int): a column number

        """
        for ent in self.getEntities_withColumn(aColumnNumber):
            ent.setValue(aAttribute, aValue)

    def setEntities_withRow(self, aAttribute, aValue, aRowNumber):
        """
        Set the value of attribut to all entities in a specified row

        Args:
            aAttribute (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
            aRowNumber (int): a row number

        """
        for ent in self.getEntities_withRow(aRowNumber):
            ent.setValue(aAttribute, aValue)

    def setRandomEntity(self, aAttribute, aValue, condition=None):
        """
        Apply a value to a random entity

        Args:
            aAttribute (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
        """
        self.getRandomEntity(condition=condition).setValue(aAttribute, aValue)

    def setRandomEntity_withValue(self, aAttribut, aValue, conditionAtt, conditionVal, condition=None):
        """
        To apply a value to a random entity with a certain value

        Args:
            aAttribut (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
        """
        self.getRandomEntity_withValue(conditionAtt, conditionVal, condition).setValue(aAttribut, aValue)

    def setRandomEntity_withValueNot(self, aAttribut, aValue, conditionAtt, conditionVal, condition=None):
        """
       To apply a value to a random entity not having a certain value

        Args:
            aAttribut (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
        """
        self.getRandomEntity_withValueNot(conditionAtt, conditionVal, condition).setValue(aAttribut, aValue)

    def setRandomEntities(self, aAttribute, aValue, numberOfentities=1, condition=None):
        """
        Applies the same attribut value for a random number of entities

        Args:
            aAttribute (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
            numberOfentities (int): number of entities
        """
        aList = self.getRandomEntities(numberOfentities, condition)
        if aList == []:
            return False
        for ent in aList:
            ent.setValue(aAttribute, aValue)

    def setRandomEntities_withValue(self, aAttribut, aValue, numberOfentities, conditionAtt, conditionVal, condition=None):
        """
        To apply a value to some random entities with a certain value

        Args:
            aAttribut (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
            numberOfentities (int): number of entities
        """
        for ent in self.getRandomEntities_withValue(numberOfentities, conditionAtt, conditionVal, condition):
            ent.setValue(aAttribut, aValue)

    def setRandomEntities_withValueNot(self, aAttribut, aValue, numberOfentities, conditionAtt, conditionVal, condition=None):
        """
        To apply a value to some random entities noty having a certain value

        Args:
            aAttribut (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
            numberOfentities (int): number of entities
        """
        for ent in self.getRandomEntities_withValueNot(numberOfentities, conditionAtt, conditionVal, condition):
            ent.setValue(aAttribut, aValue)

    def copyEntitiesValue(self,  source_att, target_att,  condition=None):
        """
        Copy the value of an attribut (source_att) of the entities, in another attribute (target_att) of the entities
        Args:
            source_att (str): Name of the attribute copied
            target_att  (str): Name of the attribute set
            condition (lambda function): a condition on the entity can be used to select only some entities
        """
        for ent in self.getEntities(condition):
            ent.copyValue(source_att, target_att)

    # ============================================================================
    def newPov(self,nameOfPov,concernedAtt,dictOfColor):
        """
        Declare a new Point of View for the Species.

        Args:
            self (Species object): aSpecies
            nameOfPov (str): name of POV, will appear in the interface
            concernedAtt (str): name of the attribut concerned by the declaration
            DictofColors (dict): a dictionary with all the attribut values, and for each one a Qt.Color (https://doc.qt.io/archives/3.3/qcolor.html)
            
        """
        self.povShapeColor[nameOfPov]={str(concernedAtt):dictOfColor}
        self.model.addClassDefSymbologyinMenuBar(self,nameOfPov)
        if len(self.povShapeColor)==1:
            self.displayPov(nameOfPov)

    
    def newBorderPov(self, nameOfPov, concernedAtt, dictOfColor, borderWidth=3):
        """
        Declare a new Point of View (only for border color).
        Args:
            nameOfPov (str): name of POV, will appear in the interface
            aAtt (str): name of the attribut
            DictofColors (dict): a dictionary with all the attribut values, and for each one a Qt.Color (https://doc.qt.io/archives/3.3/qcolor.html)        """
        dictOfColorAndWidth = self.addWidthInPovDictOfColors(borderWidth,dictOfColor)
        self.povBorderColorAndWidth[nameOfPov]={str(concernedAtt):dictOfColorAndWidth}
        self.model.addClassDefSymbologyinMenuBar(self,nameOfPov,isBorder=True)

    def newBorderPovColorAndWidth(self, nameOfPov, concernedAtt, dictOfColorAndWidth):
        """
        Declare a new Point of View (only for border color).
        Args:
            nameOfPov (str): name of POV, will appear in the interface
            aAtt (str): name of the attribut
            DictofColorsAndWidth (dict): a dictionary with all the attribut values, and for each one a Qt.Color (https://doc.qt.io/archives/3.3/qcolor.html)
        """
        dictOfColorAndWidth = self.reformatDictOfColorAndWidth(dictOfColorAndWidth)
        self.povBorderColorAndWidth[nameOfPov]={str(concernedAtt):dictOfColorAndWidth}
        self.model.addClassDefSymbologyinMenuBar(self,nameOfPov,isBorder=True)


    # ============================================================================
    # GET/NB METHODS
    # ============================================================================
    def getEntity(self, x, y=None):
        """
        Return an entity identified by its id or its coordinates on a grid
        arg:
            id (int): id of the entity
        Alternativly, can return an entity identified by its if or coordinates on a grid 
             x (int): column number
            y (int):  row number
        """
        if isinstance(y, int):
            if x < 1 or y < 1 : return None
            aId= self.grid.cellIdFromCoords(x,y)
        else:
            aId=x
        return next(filter(lambda ent: ent.id==aId, self.entities),None)

    def getEntities(self, condition=None):
        """
        Get all entities, optionally filtered by a condition.
        
        Args:
            condition (callable, optional): Function that takes an entity and returns True if it should be included
            
        Returns:
            list: List of entities matching the condition, or all entities if condition is None
        """
        if condition is None: return self.entities[:]
        return [ent for ent in self.entities if condition(ent)]

    def getEntities_withValue(self, att, val):
        """
        Get all entities that have a specific attribute value.
        
        Args:
            att (str): Attribute name
            val: Value to match
            
        Returns:
            list: List of entities with the specified attribute value
        """
        return list(filter(lambda ent: ent.value(att)==val, self.entities))

    def getEntities_withValueNot(self, att, val):
        """
        Get all entities that do not have a specific attribute value.
        
        Args:
            att (str): Attribute name
            val: Value to exclude
            
        Returns:
            list: List of entities without the specified attribute value
        """
        return list(filter(lambda ent: ent.value(att)!=val, self.entities))

    def getRandomEntity(self, condition=None, listOfEntitiesToPickFrom=None):
        """
        Return a random entity from the available entities.
        
        Args:
            condition (callable, optional): Function that takes an entity and returns True if it should be considered
            listOfEntitiesToPickFrom (list, optional): Specific list of entities to pick from
            
        Returns:
            Entity or False: A random entity if available, False if no entities match
        """
        if listOfEntitiesToPickFrom == None:
            listOfEntitiesToPickFrom = self.entities
        if condition == None:
            listOfEntities = listOfEntitiesToPickFrom
        else:
            listOfEntities = [ent for ent in listOfEntitiesToPickFrom if condition(ent)]
        
        return random.choice(listOfEntities) if len(listOfEntities) > 0 else False

    def getRandomEntity_withValue(self, att, val, condition=None):
        """
        Return a random entity that has a specific attribute value.
        
        Args:
            att (str): Attribute name
            val: Value to match
            condition (callable, optional): Additional condition function
            
        Returns:
            Entity or False: A random entity with the specified value, False if none found
        """
        return self.getRandomEntity(condition=condition, listOfEntitiesToPickFrom=self.getEntities_withValue(att, val))

    def getRandomEntity_withValueNot(self, att, val, condition=None):
        """
        Return a random entity that does not have a specific attribute value.
        
        Args:
            att (str): Attribute name
            val: Value to exclude
            condition (callable, optional): Additional condition function
            
        Returns:
            Entity or False: A random entity without the specified value, False if none found
        """
        return self.getRandomEntity(condition=condition, listOfEntitiesToPickFrom=self.getEntities_withValueNot(att, val))

    def getRandomEntities(self, aNumber, condition=None, listOfEntitiesToPickFrom=None):
        """
        Return a specified number of random entities.
        
        Args:
            aNumber (int): Number of entities to return
            condition (callable, optional): Function that takes an entity and returns True if it should be considered
            listOfEntitiesToPickFrom (list, optional): Specific list of entities to pick from
            
        Returns:
            list: List of random entities (may be fewer than requested if not enough entities match)
        """
        if listOfEntitiesToPickFrom == None:
            listOfEntitiesToPickFrom = self.entities
        if condition == None:
            listOfEntities = listOfEntitiesToPickFrom
        else:
            listOfEntities = [ent for ent in listOfEntitiesToPickFrom if condition(ent)]
        
        return random.sample(listOfEntities, min(aNumber,len(listOfEntities))) if len(listOfEntities) > 0 else []

    def getRandomEntities_withValue(self, aNumber, att, val, condition=None):
        """
        Return a specified number of random entities that have a specific attribute value.
        
        Args:
            aNumber (int): Number of entities to return
            att (str): Attribute name
            val: Value to match
            condition (callable, optional): Additional condition function
            
        Returns:
            list: List of random entities with the specified value
        """
        return self.getRandomEntities(aNumber, condition=condition, listOfEntitiesToPickFrom=self.getEntities_withValue(att, val))

    def getRandomEntities_withValueNot(self, aNumber, att, val, condition=None):
        """
        Return a specified number of random entities that do not have a specific attribute value.
        
        Args:
            aNumber (int): Number of entities to return
            att (str): Attribute name
            val: Value to exclude
            condition (callable, optional): Additional condition function
            
        Returns:
            list: List of random entities without the specified value
        """
        return self.getRandomEntities(aNumber, condition=condition, listOfEntitiesToPickFrom=self.getEntities_withValueNot(att, val))

    def nbOfEntities(self):
        """
        Get the total number of entities in this definition.
        
        Returns:
            int: Total number of entities
        """
        return len(self.getEntities())

    def nb_withValue(self, att, value):
        """
        Get the number of entities that have a specific attribute value.
        
        Args:
            att (str): Attribute name
            value: Value to count
            
        Returns:
            int: Number of entities with the specified value
        """
        return len(self.getEntities_withValue(att, value))

   

    # ============================================================================
    # DELETE METHODS
    # ============================================================================
    def deleteAllEntities(self):
        """
        Delete all entities of the species.
        """
        for ent in self.entities[:]:
            self.deleteEntity(ent)

    # ============================================================================
    # DO/DISPLAY METHODS
    # ============================================================================
    def displayPov(self,nameOfPov):
        """
        Displays the symbology for the specified Point of View.
        Args:
            nameOfPov (str): The name of the Point of View to display.
        """
        self.model.checkSymbologyinMenuBar(self,nameOfPov)


    def displayBorderPov(self,nameOfBorderPov):
        """
        Displays the border symbology for the specified Point of View.
        Args:
            nameOfBorderPov (str): The name of the border Point of View to display.
        """
        self.model.checkSymbologyinMenuBar(self,nameOfBorderPov,borderSymbology=True)



    def setAttributeValueToDisplayInContextualMenu(self, aAttribut, aLabel=None):
        """
        Set an attribute to be displayed in the contextual menu.
        
        Args:
            aAttribut (str): Name of the attribute to display
            aLabel (str, optional): Custom label for the attribute (defaults to attribute name)
       
        """
        # Check that the attribute exists in dictAttributes
        if aAttribut not in self.dictAttributes:
            raise ValueError(f"Attribute '{aAttribut}' does not exist in dictAttributes. Available attributes: {list(self.dictAttributes.keys())}")
        
        aDict={}
        aDict['att']=aAttribut
        aDict['label']= (aLabel if aLabel is not None else aAttribut)
        self.attributesToDisplayInContextualMenu.append(aDict)

    def newModelAction(self, actions=None, conditions=None, feedbacks=None):
        """
        Create an SGModelAction_OnEntities targeting entities of this definition.

        Args:
            actions (callable | list[callable]): Action(s) with signature action(aEntity)
            conditions (callable | list[callable]): Condition(s) with signature condition(aEntity)
            feedbacks (callable | list[callable] | SGModelAction): Feedback action(s)
        """
        actions = actions or []
        conditions = conditions or []
        feedbacks = feedbacks or []
        model_action = SGModelAction_OnEntities(sgModel=self.model, actions=actions, conditions=conditions, feedbacks=feedbacks, entities= (lambda: self.getEntities()))
        self.model.id_modelActions += 1
        model_action.id = self.model.id_modelActions
        return model_action

    # ============================================================================
    # METRIC METHODS
    # ============================================================================
    def metricOnEntities(self, metric, attribute, value=None):
        """
        Get metrics for all entities.
        Args:
            metric (str): The metric to use for statistical evaluation. Possible values include:
                - 'sumAtt': Sum of the specified attribute values.
                - 'avgAtt': Average of the specified attribute values.
                - 'minAtt': Minimum value of the specified attribute.
                - 'maxAtt': Maximum value of the specified attribute.
                - 'nbWithLess': Count of entities with attribute values less than the specified value.
                - 'nbWithMore': Count of entities with attribute values greater than the specified value.
                - 'nbEqualTo': Count of entities with attribute values equal to the specified value.
            attribute (str): The attribute to evaluate.
            value (optional): The value to compare against for certain metrics.
        Returns:
            float or int: The calculated metric for all entities.
        """
        return SGIndicator.metricOn(self.getEntities(), metric, attribute, value)

    def metricOnEntitiesWithValue(self, attributeForSelection, valueForSelection, metric, attribute, value=None):
        """
        Get metrics for entities that have a specific attribute value.

        Args:
            attributeForSelection (str): The attribute used to filter entities for selection.
            valueForSelection: The value that the specified attribute must match for the entities to be included.
            metric (str): The metric to use for statistical evaluation. Possible values include:
                - 'sumAtt': Sum of the specified attribute values.
                - 'avgAtt': Average of the specified attribute values.
                - 'minAtt': Minimum value of the specified attribute.
                - 'maxAtt': Maximum value of the specified attribute.
                - 'nbWithLess': Count of entities with attribute values less than the specified value.
                - 'nbWithMore': Count of entities with attribute values greater than the specified value.
                - 'nbEqualTo': Count of entities with attribute values equal to the specified value.
            attribute (str): The attribute to evaluate.
            value: The value to compare against.
        Returns:
            float or int: The calculated metric for entities with the specified value.
        """
        entities_with_value = self.getEntities_withValue(attributeForSelection, valueForSelection)
        return SGIndicator.metricOn(entities_with_value, metric, attribute, value)

    def metricOnEntitiesWithValueNot(self, attributeForSelection, valueForSelection, metric, attribute, value=None):
        """
        Get metrics for entities that do not have a specific attribute value.
        Args:
            attributeForSelection (str): The attribute used to filter entities for selection.
            valueForSelection: The value that the specified attribute must not match for the entities to be included.
            metric (str): The metric to use for statistical evaluation. Possible values include:
                - 'sumAtt': Sum of the specified attribute values.
                - 'avgAtt': Average of the specified attribute values.
                - 'minAtt': Minimum value of the specified attribute.
                - 'maxAtt': Maximum value of the specified attribute.
                - 'nbWithLess': Count of entities with attribute values less than the specified value.
                - 'nbWithMore': Count of entities with attribute values greater than the specified value.
                - 'nbEqualTo': Count of entities with attribute values equal to the specified value.
            attribute (str): The attribute to evaluate.
            value: The value to compare against.
        Returns:
            float or int: The calculated metric for entities without the specified value.
        """
        entities_with_value_not = self.getEntities_withValueNot(attributeForSelection, valueForSelection)
        return SGIndicator.metricOn(entities_with_value_not, metric, attribute, value)

    # ============================================================================
    # SPECIALIZED CLASSES
    # ============================================================================

# Définition de SGCellDef
class SGCellDef(SGEntityDef):
    def __init__(self, grid, shape, defaultsize, entDefAttributesAndValues, defaultColor=Qt.white, entityName='Cell', defaultCellImage=None):
        super().__init__(grid.model, entityName, shape, defaultsize, entDefAttributesAndValues, defaultColor)
        # Type identification attribute
        self.isCellDef = True
        self.grid = grid
        self.deletedCells = []
        self.defaultImage = defaultCellImage


    def newCellWithModelView(self, x, y):
        """
        Create a new cell using Model-View architecture
        
        Args:
            x (int): Column position in grid (1-indexed)
            y (int): Row position in grid (1-indexed)
            
        Returns:
            tuple: (cell_model, cell_view) - The cell model and view pair
        """
        from mainClasses.SGEntityFactory import SGEntityFactory
        
        # Create cell using factory
        cell_model, cell_view = SGEntityFactory.newCellWithModelView(self, x, y)
        
        # Add to entities list (store the model)
        self.entities.append(cell_model)
        
        # Update watchers
        self.updateWatchersOnPop()
        self.updateWatchersOnAllAttributes()
        
        # Show the view
        cell_view.show()
        
        return cell_model, cell_view

    def reviveThisCell(self, aCell): #todo this is a developer method
        self.entities.append(aCell)
        # Use the new setDisplay method to notify the view
        if hasattr(aCell, 'setDisplay'):
            aCell.setDisplay(True)
        else:
            # Fallback for old architecture
            aCell.isDisplay = True
        self.deletedCells.remove(aCell)
        self.updateWatchersOnPop()
        self.updateWatchersOnAllAttributes()
        aCell.update()

    def cellIdFromCoords(self, x, y):
        if x < 1 or y < 1:
            return None
        return (x - 1) + self.grid.columns * (y - 1)

    
    # ============================================================================
    # MODELER METHODS
    # ============================================================================
    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================
    
    def newCell(self, x, y):
        """
        Create a new cell using Model-View architecture (standard method)
        
        Args:
            x (int): Column position in grid (1-indexed)
            y (int): Row position in grid (1-indexed)
            
        Returns:
            cell_model: The cell model (for modelers)
        """
        # Utiliser la méthode Model-View
        result = self.newCellWithModelView(x, y)
        
        if result is None:
            return None
            
        # Extraire seulement le modèle du tuple
        cell_model, cell_view = result
        
        # Retourner seulement la cellule pour les modelers
        return cell_model

    def setCell(self, x, y, aAttribute, aValue):
        ent = self.getCell(x, y).setValue(aAttribute, aValue)
        return ent

    # ============================================================================
    # GET METHODS
    # ============================================================================
    def getCell(self, x, y=None):
        """
        Retrieve a cell object from the grid.

        Args:
            x (int, tuple, list, or cell ID):
                - If int and `y` is provided: interpreted as the column index (1-indexed).
                - If tuple or list of two ints: interpreted as (column, row) coordinates (1-indexed).
                - If int and `y` is None: interpreted directly as a cell ID.
            y (int, optional):
                Row index (1-indexed). Only used if `x` is an int representing a column.

        Returns:
            object or None: The cell object if found within the grid boundaries, otherwise None.

        Notes:
            - Coordinates are 1-indexed: valid ranges are 1 ≤ x ≤ grid.columns and 1 ≤ y ≤ grid.rows.
            - If coordinates are outside this range, returns None.
            - Supports passing coordinates as a tuple or list: e.g. getCell((4, 2)).
        """
        # Allow passing coordinates as a tuple or list: getCell((col, row))
        if isinstance(x, (tuple, list)) and len(x) == 2 and y is None:
            x, y = x

        if isinstance(y, int):
            # Return None if outside the grid (1-indexed coordinates)
            if x < 1 or x > self.grid.columns or y < 1 or y > self.grid.rows:
                return None
            aId = self.cellIdFromCoords(x, y)
        else:
            # Here 'x' is treated as the cell ID directly
            aId = x

        return next((ent for ent in self.entities if ent.id == aId), None)


   

    # Return the cell at specified coordinates
    def getEntity(self, x, y=None):
        """
        Get a single entity (cell) by coordinates.
        
        Args:
            x (int): X coordinate of the entity
            y (int, optional): Y coordinate of the entity. If None, x is treated as a cell ID string
            
        Returns:
            SGCell: The entity at the specified coordinates, or None if not found
        """
        return self.getCell(x, y)

    def getEntities_withRow(self, aRowNumber):
        """
        Get all entities (cells) in a specific row.
        
        Args:
            aRowNumber (int): Row number to retrieve entities from
            
        Returns:
            list[SGCell]: List of entities in the specified row
        """
        return self.grid.getCells_withRow(aRowNumber)

    def getEntities_withColumn(self, aColumnNumber):
        """
        Get all entities (cells) in a specific column.
        
        Args:
            aColumnNumber (int): Column number to retrieve entities from
            
        Returns:
            list[SGCell]: List of entities in the specified column
        """
        return self.grid.getCells_withColumn(aColumnNumber)


    def getRandomEntity(self, condition=None, listOfEntitiesToPickFrom=None) -> SGCell:
        """
        Return a random cell from this grid.
        
        Args:
            condition (callable, optional): Condition function to filter cells (signature: condition(cell))
            listOfEntitiesToPickFrom (list, optional): Specific list of entities to pick from
            
        Returns:
            SGCell: A random cell from the grid, or False if no cells found
        """
        return super().getRandomEntity(condition=condition, listOfEntitiesToPickFrom=listOfEntitiesToPickFrom)

    # ============================================================================
    # DELETE METHODS
    # ============================================================================

    def deleteEntity(self, aCell):
        """
        Delete a given cell
        args:
            aCell (instance): the cell to de deleted
        """
        if len(aCell.agents) !=0:
            aCell.deleteAllAgents()
        self.deletedCells.append(aCell)
        # Use the new setDisplay method to notify the view
        if hasattr(aCell, 'setDisplay'):
            aCell.setDisplay(False)
        else:
            # Fallback for old architecture
            aCell.isDisplay = False
        self.entities.remove(aCell)
        self.updateWatchersOnPop()
        self.updateWatchersOnAllAttributes()
        aCell.update()


        

# ********************************************************    


class SGAgentDef(SGEntityDef):
    def __init__(self, sgModel, entityName, shape, defaultsize, entDefAttributesAndValues, defaultColor=Qt.black, locationInEntity="random", defaultImage=None, popupImage=None):
        super().__init__(sgModel, entityName, shape, defaultsize, entDefAttributesAndValues, defaultColor)
        # Type identification attribute
        self.isAgentDef = True
        self.locationInEntity = locationInEntity
        self.defaultImage = defaultImage
        self.popupImage = popupImage

    # ===================NEW/ADD/SET METHODS DEVELOPER METHODS==============================================  
    def newAgentOnCellWithModelView(self, aCell, attributesAndValues=None, image=None, popupImage=None):
        """
        Create a new agent using Model-View architecture
        
        Args:
            aCell: The cell where the agent will be placed
            attributesAndValues: Initial attributes and values
            image: Default image for the agent
            popupImage: Popup image for the agent
            
        Returns:
            tuple: (agent_model, agent_view) - The agent model and view pair
        """
        if aCell == None: 
            return None
            
        from mainClasses.SGEntityFactory import SGEntityFactory
        
        # Create agent using factory
        agent_model, agent_view = SGEntityFactory.newAgentWithModelView(
            self, aCell, attributesAndValues, image, popupImage
        )
        
        # Add to entities list (store the model)
        self.entities.append(agent_model)
        
        # Update watchers
        self.updateWatchersOnPop()
        self.updateWatchersOnAllAttributes()
        
        # Position and show the agent
        agent_view.getPositionInEntity()
        agent_view.show()
        
        return agent_model, agent_view


    def newAgentsOnCellWithModelView(self, nbAgents, aCell, attributesAndValues=None): #todo this method is called only by test methods. Consider removing it.
        """
        Create a specific number of new Agents using Model-View architecture.
        
        Args:
            nbAgents (int): number of Agents 
            aCell: aCell located on a grid
            attributesAndValues: attributes and values of the new agent
            
        Return:
            list: List of tuples (agent_model, agent_view) for each created agent
        """
        agents = []
        for n in range(nbAgents):
            agent_model, agent_view = self.newAgentOnCellWithModelView(aCell, attributesAndValues)
            agents.append((agent_model, agent_view))
        return agents

    def newAgentAtCoordsWithModelView(self, cellDef_or_grid=None, xCoord=None, yCoord=None, attributesAndValues=None, image=None, popupImage=None):
        """
        Create a new Agent using Model-View architecture at specified coordinates.

        Args:
            cellDef_or_grid (instance): the cellDef or grid you want your agent in. If None, the first cellDef and grid will be used
            xCoord (int): Column position in grid (Default=Random)
            yCoord (int): Row position in grid (Default=Random)
            attributesAndValues (dict, optional): mapping of attribute names to values (or callables)
            image: Default image for the agent
            popupImage: Popup image for the agent
            
        Flexible calling patterns (backward compatible):
            - newAgentAtCoordsWithModelView(x, y, ...)
            - newAgentAtCoordsWithModelView((x, y), ...)
            - newAgentAtCoordsWithModelView(cellDef_or_grid, x, y, ...)
            
        Return:
            tuple: (agent_model, agent_view) - The agent model and view pair
        """
        # Normalize arguments to support calls like newAgentAtCoordsWithModelView(3,3) or newAgentAtCoordsWithModelView((3,3))
        if isinstance(cellDef_or_grid, (tuple, list)) and len(cellDef_or_grid) == 2 and xCoord is None and yCoord is None:
            xCoord, yCoord = int(cellDef_or_grid[0]), int(cellDef_or_grid[1])
            cellDef_or_grid = None
        elif isinstance(cellDef_or_grid, int) and isinstance(xCoord, int) and yCoord is None:
            # Called as newAgentAtCoordsWithModelView(x, y, ...)
            xCoord, yCoord = cellDef_or_grid, xCoord
            cellDef_or_grid = None
        elif isinstance(xCoord, (tuple, list)) and len(xCoord) == 2 and yCoord is None:
            # Called as newAgentAtCoordsWithModelView(cellDef_or_grid, (x, y), ...)
            xCoord, yCoord = int(xCoord[0]), int(xCoord[1])

        # Normalize argument cellDef_or_grid to support calls like newAgentAtCoordsWithModelView(Cell,3,3) or newAgentAtCoordsWithModelView(3,3) or newAgentAtCoordsWithModelView(aGrid,3,3)
        if not cellDef_or_grid:
            aCellDef = first_value(self.model.cellOfGrids, None)
        else: 
            aCellDef = self.model.getCellDef(cellDef_or_grid)
        if aCellDef == None: 
            return None
        aGrid = self.model.getGrid(aCellDef)

        if xCoord == None: 
            xCoord = random.randint(1, aGrid.columns)
        if yCoord == None: 
            yCoord = random.randint(1, aGrid.rows)
        locationCell = aCellDef.getCell(xCoord, yCoord)
        if locationCell is None:
            return None
            
        return self.newAgentOnCellWithModelView(locationCell, attributesAndValues, image, popupImage)

    def newAgentsAtCoordsWithModelView(self, nbAgents, cellDef_or_grid=None, xCoord=None, yCoord=None, attributesAndValues=None): #todo this method is called only by test methods. Consider removing it.
        """
        Create a specific number of new Agents using Model-View architecture at specified coordinates.

        Args:
            nbAgents (int): number of Agents
            cellDef_or_grid (instance, optional): the cellDef or grid you want your agent in. If None, the first cellDef/grid is used
            xCoord (int, optional): Column position in grid (1..columns)
            yCoord (int, optional): Row position in grid (1..rows)
            attributesAndValues (dict, optional): mapping of attribute names to values (or callables)
            
        Flexible calling patterns (backward compatible):
            - newAgentsAtCoordsWithModelView(7)
            - newAgentsAtCoordsWithModelView(7, {"health":"good"})
            - newAgentsAtCoordsWithModelView(7, 3, 3)
            - newAgentsAtCoordsWithModelView(7, (3, 3))
            - newAgentsAtCoordsWithModelView(7, cellDef_or_grid, 3, 3)
            - newAgentsAtCoordsWithModelView(7, cellDef_or_grid, (3, 3))
            - newAgentsAtCoordsWithModelView(7, 3, 3, {"health":"good"})
            - newAgentsAtCoordsWithModelView(7, cellDef_or_grid, 3, 3, {"health":"good"})
            
        Return:
            list: List of tuples (agent_model, agent_view) for each created agent
        """
        # Normalize attributes dict as second positional arg
        if isinstance(cellDef_or_grid, dict) and attributesAndValues is None and xCoord is None and yCoord is None:
            attributesAndValues = cellDef_or_grid
            cellDef_or_grid = None
        # Normalize coordinate tuple passed as second arg
        if isinstance(cellDef_or_grid, (tuple, list)) and len(cellDef_or_grid) == 2 and xCoord is None and yCoord is None:
            xCoord, yCoord = int(cellDef_or_grid[0]), int(cellDef_or_grid[1])
            cellDef_or_grid = None
        # Normalize when called as newAgentsAtCoordsWithModelView(7, x, y, ...)
        if isinstance(cellDef_or_grid, int) and isinstance(xCoord, int) and yCoord is None:
            xCoord, yCoord = cellDef_or_grid, xCoord
            cellDef_or_grid = None
        # Normalize when coordinates are provided as a tuple in xCoord
        if isinstance(xCoord, (tuple, list)) and len(xCoord) == 2 and yCoord is None:
            xCoord, yCoord = int(xCoord[0]), int(xCoord[1])
        
        agents = []
        for n in range(nbAgents):
            agent_model, agent_view = self.newAgentAtCoordsWithModelView(cellDef_or_grid, xCoord, yCoord, attributesAndValues)
            if agent_model is not None:  # Only add if creation was successful
                agents.append((agent_model, agent_view))
        return agents

    def newAgentAtRandomWithModelView(self, cellDef_or_grid=None, attributesAndValues=None, condition=None):
        """
        Create a new Agent using Model-View architecture and place it on a random cell.
        
        Args:
            cellDef_or_grid (instance): the cellDef or grid you want your agent in. If None, the first cellDef and grid will be used
            attributesAndValues (dict, optional): mapping of attribute names to values (or callables)
            condition (lambda function, optional): a condition that the destination cell should respect
            
        Flexible calling patterns (backward compatible):
            - newAgentAtRandomWithModelView()
            - newAgentAtRandomWithModelView({"health":"good"})
            - newAgentAtRandomWithModelView(cellDef_or_grid)
            - newAgentAtRandomWithModelView(cellDef_or_grid, {"health":"good"})
            
        Return:
            tuple: (agent_model, agent_view) - The agent model and view pair
        """
        # Normalize dict passed as first arg
        if isinstance(cellDef_or_grid, dict) and attributesAndValues is None:
            attributesAndValues = cellDef_or_grid
            cellDef_or_grid = None
            
        # Normalize argument cellDef_or_grid to support calls like newAgentAtRandomWithModelView(Cell) or newAgentAtRandomWithModelView() or newAgentAtRandomWithModelView(aGrid)
        if not cellDef_or_grid:
            aCellDef = first_value(self.model.cellOfGrids, None)
        else: 
            aCellDef = self.model.getCellDef(cellDef_or_grid)
        if aCellDef == None: 
            return None

        locationCell = aCellDef.getRandomEntity(condition=condition)
        if locationCell is None or locationCell is False:
            return None
            
        return self.newAgentOnCellWithModelView(locationCell, attributesAndValues)
        
    def newAgentsAtRandomWithModelView(self, aNumber, cellDef_or_grid=None, attributesAndValues=None, condition=None): #todo this method is called only by test methods. Consider removing it.
        """
        Create a number of Agents using Model-View architecture and place them on random cells.
        
        Args:
            aNumber (int): number of agents to be created
            cellDef_or_grid (instance): the cellDef or grid you want your agent in. If None, the first cellDef and grid will be used
            attributesAndValues (dict, optional): mapping of attribute names to values (or callables)
            condition (lambda function, optional): a condition that the destination cell should respect
            
        Flexible calling patterns (backward compatible):
            - newAgentsAtRandomWithModelView(7)
            - newAgentsAtRandomWithModelView(7, {"health":"good", "hunger":"bad"})
            - newAgentsAtRandomWithModelView(7, cellDef_or_grid)
            - newAgentsAtRandomWithModelView(7, cellDef_or_grid, attributesAndValues)
            
        Return:
            list: List of tuples (agent_model, agent_view) for each created agent
        """
        # Normalize arguments to support calls like newAgentsAtRandomWithModelView(7) or newAgentsAtRandomWithModelView(7, {..})
        if isinstance(cellDef_or_grid, dict) and attributesAndValues is None:
            attributesAndValues = cellDef_or_grid
            cellDef_or_grid = None
            
        # Normalize argument cellDef_or_grid to support calls like newAgentsAtRandomWithModelView(Cell) or newAgentsAtRandomWithModelView() or newAgentsAtRandomWithModelView(aGrid)
        if not cellDef_or_grid:
            aCellDef = first_value(self.model.cellOfGrids, None)
        else: 
            aCellDef = self.model.getCellDef(cellDef_or_grid)
        if aCellDef == None: 
            return []
        
        locationCells = aCellDef.getRandomEntities(aNumber, condition=condition)
        agents = []
        for aCell in locationCells:
            agent_model, agent_view = self.newAgentOnCellWithModelView(aCell, attributesAndValues)
            agents.append((agent_model, agent_view))
        return agents

    # ============================================================================
    # MODELER METHODS
    # ============================================================================
    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================
    def newAgentOnCell(self, aCell, attributesAndValues=None, image=None, popupImage=None) -> SGAgent:
        """
        Create a new agent on a specific cell.
        
        Args:
            aCell (SGCell): Cell where the agent will be placed
            attributesAndValues (dict, optional): Initial attributes and values for the agent
            image (str, optional): Image path for the agent
            popupImage (str, optional): Popup image path for the agent
            
        Returns:
            SGAgent: The created agent model, or None if creation failed
        """
        if aCell == None:
            return None

        # Utiliser la méthode Model-View
        result = self.newAgentOnCellWithModelView(aCell, attributesAndValues, image, popupImage)

        if result is None:
            return None

        # Extraire seulement le modèle du tuple
        agent_model, agent_view = result

        # Ajouter seulement le modèle à entities (pas le tuple)
        self.entities.append(agent_model)
        self.updateWatchersOnPop()
        self.updateWatchersOnAllAttributes()

        # Retourner seulement l'agent pour les modelers
        return agent_model


    def newAgentsOnCell(self, nbAgents, aCell, attributesAndValues=None):
        """
        Create a specific number of new Agents in the associated species on a specific cell.
        
        Args:
            nbAgents (int): Number of agents to create
            aCell (SGCell): Cell where the agents will be placed
            attributesAndValues (dict, optional): Initial attributes and values for the agents
            
        Returns:
            None: Agents are created and added to the species
        """
        for n in range(nbAgents):
            self.newAgentOnCell(aCell, attributesAndValues)
    
    

    def newAgentAtCoords(self, cellDef_or_grid=None, xCoord=None, yCoord=None, attributesAndValues=None, image=None, popupImage=None):
        """
        Create a new Agent using Model-View architecture at specified coordinates (standard method)
        
        Args:
            cellDef_or_grid (instance): the cellDef or grid you want your agent in. If None, the first cellDef and grid will be used
            xCoord (int): Column position in grid (Default=Random)
            yCoord (int): Row position in grid (Default=Random)
            attributesAndValues (dict, optional): mapping of attribute names to values (or callables)
            image: Default image for the agent
            popupImage: Popup image for the agent
            
        Flexible calling patterns (backward compatible):
            - newAgentAtCoords(x, y, ...)
            - newAgentAtCoords((x, y), ...)
            - newAgentAtCoords(cellDef_or_grid, x, y, ...)
            
        Return:
            agent_model: The agent model (for modelers)
        """
        # Utiliser la méthode Model-View
        result = self.newAgentAtCoordsWithModelView(cellDef_or_grid, xCoord, yCoord, attributesAndValues, image, popupImage)
        
        if result is None:
            return None
            
        # Extraire seulement le modèle du tuple
        agent_model, agent_view = result
        
        # Retourner seulement l'agent pour les modelers
        return agent_model

    def newAgentsAtCoords(self, nbAgents, cellDef_or_grid=None, xCoord=None, yCoord=None, attributesAndValues=None):
        """
        Create a specific number of new Agents in the associated species.

        Args:
            nbAgents (int): number of Agents
            cellDef_or_grid (instance, optional): the cellDef or grid you want your agent in. If None, the first cellDef/grid is used
            xCoord (int, optional): Column position in grid (1..columns)
            yCoord (int, optional): Row position in grid (1..rows)
            attributesAndValues (dict, optional): mapping of attribute names to values (or callables)
        Flexible calling patterns (backward compatible):
            - newAgentsAtCoords(7)
            - newAgentsAtCoords(7, {"health":"good"})
            - newAgentsAtCoords(7, 3, 3)
            - newAgentsAtCoords(7, (3, 3))
            - newAgentsAtCoords(7, cellDef_or_grid, 3, 3)
            - newAgentsAtCoords(7, cellDef_or_grid, (3, 3))
            - newAgentsAtCoords(7, 3, 3, {"health":"good"})
            - newAgentsAtCoords(7, cellDef_or_grid, 3, 3, {"health":"good"})
        Return:
            agents
        """
        # Normalize attributes dict as second positional arg
        if isinstance(cellDef_or_grid, dict) and attributesAndValues is None and xCoord is None and yCoord is None:
            attributesAndValues = cellDef_or_grid
            cellDef_or_grid = None
        # Normalize coordinate tuple passed as second arg
        if isinstance(cellDef_or_grid, (tuple, list)) and len(cellDef_or_grid) == 2 and xCoord is None and yCoord is None:
            xCoord, yCoord = int(cellDef_or_grid[0]), int(cellDef_or_grid[1])
            cellDef_or_grid = None
        # Normalize when called as newAgentsAtCoords(7, x, y, ...)
        if isinstance(cellDef_or_grid, int) and isinstance(xCoord, int) and yCoord is None:
            xCoord, yCoord = cellDef_or_grid, xCoord
            cellDef_or_grid = None
        # Normalize when coordinates are provided as a tuple in xCoord
        if isinstance(xCoord, (tuple, list)) and len(xCoord) == 2 and yCoord is None:
            xCoord, yCoord = int(xCoord[0]), int(xCoord[1])
        
        for n in range(nbAgents):
            self.newAgentAtCoords(cellDef_or_grid, xCoord, yCoord, attributesAndValues)


    def newAgentAtRandom(self, cellDef_or_grid=None, attributesAndValues=None, condition=None):
        """
        Create a new Agent and place it on a random cell (standard method)
        
        Args:
            cellDef_or_grid (instance): the cellDef or grid you want your agent in. If None, the first cellDef and grid will be used
            attributesAndValues (dict, optional): mapping of attribute names to values (or callables)
            condition (lambda function, optional): a condition that the destination cell should respect
            
        Flexible calling patterns (backward compatible):
            - newAgentAtRandom()
            - newAgentAtRandom({"health":"good"})
            - newAgentAtRandom(cellDef_or_grid)
            - newAgentAtRandom(cellDef_or_grid, {"health":"good"})
            
        Return:
            agent_model: The agent model (for modelers)
        """
        return self.newAgentAtRandomWithModelView(cellDef_or_grid, attributesAndValues, condition)



    def newAgentsAtRandom(self, aNumber, cellDef_or_grid=None, attributesAndValues=None, condition=None):
        """
        Create a number of Agents and place them on random cells (standard method)
        
        Args:
            aNumber (int): number of agents to be created
            cellDef_or_grid (instance): the cellDef or grid you want your agent in. If None, the first cellDef and grid will be used
            attributesAndValues (dict, optional): mapping of attribute names to values (or callables)
            condition (lambda function, optional): a condition that the destination cell should respect
            
        Flexible calling patterns (backward compatible):
            - newAgentsAtRandom(7)
            - newAgentsAtRandom(7, {"health":"good", "hunger":"bad"})
            - newAgentsAtRandom(7, cellDef_or_grid)
            - newAgentsAtRandom(7, cellDef_or_grid, attributesAndValues)
            
        Return:
            list: List of agent models (for modelers)
        """
        return self.newAgentsAtRandomWithModelView(aNumber, cellDef_or_grid, attributesAndValues, condition)

    
    # ============================================================================
    # GET METHODS
    # ============================================================================

    def getRandomEntity(self, condition=None, listOfEntitiesToPickFrom=None) -> SGAgent:
        """
        Return a random agent from this species.
        
        Returns:
            SGAgent: A random agent from the list
            bool: False if no agents found
        """
        return super().getRandomEntity(condition=condition, listOfEntitiesToPickFrom=listOfEntitiesToPickFrom)

    
    # ============================================================================
    # DELETE METHODS
    # ============================================================================

    def deleteEntity(self, aAgent):
        """
        Delete a given agent
        args:
            aAgent (instance): the agent to be deleted
        """
        # Remove agent from its cell using the new Model-View architecture
        if hasattr(aAgent.cell, 'removeAgent'):
            aAgent.cell.removeAgent(aAgent)
        else:
            # Fallback for old architecture
            aAgent.cell.updateDepartureAgent(aAgent)
        
        # Delete the view if it exists (Model-View architecture)
        if hasattr(aAgent, 'view') and aAgent.view:
            try:
                aAgent.view.deleteLater()
            except RuntimeError:
                # View already deleted, ignore the error
                pass
        else:
            # Fallback for old architecture
            aAgent.deleteLater()
            
        self.entities.remove(aAgent)
        self.updateWatchersOnPop()
        self.updateWatchersOnAllAttributes()
        #aAgent.update()


    # ============================================================================
    # DO/DISPLAY METHODS
    # ============================================================================
    def moveRandomly(self, numberOfMovement=1,condition=None):
        """
        All agents of the species move randomly.

        args:
            numberOfMovement (int): number of movements in one action
            condition (lambda function, optional): a condition that the destination cell should respect for the agent to move
        """
        for aAgent in self.entities[:]: # Need to iterate on a copy of the entities list, because , due to the moveByRecreating, the entities list changes during the loop
            aAgent.moveAgent(numberOfMovement=numberOfMovement,condition=condition)
