from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGCell import SGCell
from mainClasses.SGAgent import SGAgent
from mainClasses.AttributeAndValueFunctionalities import *
from mainClasses.SGIndicator import SGIndicator
from mainClasses.SGModelAction import SGModelAction_OnEntities
from mainClasses.SGExtensions import *
import numpy as np
from collections import Counter, defaultdict
import random
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
        
        #Define variables to handle the history 
        self.history={}
        self.history["value"]=defaultdict(list)
        self.watchers = {}
        self.IDincr = 0
        self.entities = []
        self.initAttributes(entDefAttributesAndValues)
        self.listOfStepStats = []
        self.attributesToDisplayInContextualMenu = []
        # self.updateMenu = False #todo this is useless
        self.attributesToDisplayInUpdateMenu = []

    def nextId(self):
        self.IDincr +=1
        return self.IDincr
    
    def entityType(self):
        if isinstance(self,SGCellDef): return 'Cell'
        elif isinstance(self,SGAgentDef): return 'Agent'
        else: raise ValueError('Wrong or new entity type')

    ###Definition of the developer methods
    def addWatcher(self,aIndicator):
        if aIndicator.attribute is None:
            aAtt = 'nb'
        else: aAtt = aIndicator.attribute
        if aAtt not in self.watchers.keys():
            self.watchers[aAtt]=[]
        self.watchers[aAtt].append(aIndicator)

    def updateWatchersOnAttribute(self,aAtt):
        watchers_with_condition_on_entities = [item for sublist in self.watchers.values() for item in sublist if item.conditionsOnEntities]  # Filtrage des éléments
        watchers_of_the_changed_attribute = self.watchers.get(aAtt,[])
        for watcher in (watchers_of_the_changed_attribute + watchers_with_condition_on_entities):
            watcher.checkAndUpdate()

    def updateWatchersOnAllAttributes(self):
        for aAtt, listOfWatchers in self.watchers.items():
            if aAtt == 'nb': continue
            for watcher in listOfWatchers:
                watcher.checkAndUpdate()

    def updateWatchersOnPop(self):
        self.updateWatchersOnAttribute('nb')
    
    def updateAllWatchers(self):
        for listOfWatchers in self.watchers.values():
            for watcher in listOfWatchers:
                watcher.checkAndUpdate()
                    
    def  getColorOrColorandWidthOfFirstOccurenceOfAttAndValue(self, att, value):
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

    ###Definiton of the methods who the modeler will use
    def setDefaultValue(self, aAtt, aDefaultValue):
        self.attributesDefaultValues[aAtt] = aDefaultValue
    
    def setDefaultValues(self, aDictOfAttributesAndValues):
        for att, defValue in aDictOfAttributesAndValues.items():
            self.attributesDefaultValues[att] = defValue

    def setDefaultValues_randomChoice(self, mapping):
        """
        Convenience helper: set default values where each entry can be a scalar, a callable,
        or a list/tuple of choices. If a value is a list/tuple, it is converted to a lambda
        that returns random.choice(value).
        
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
        Convenience helper: set default numeric values from concise specs.
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


    #To set up a POV
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


    def addWidthInPovDictOfColors(self,borderWidth,dictOfColor):
        dictOfColorAndWidth ={}
        for aKey, aColor in dictOfColor.items():
            dictOfColorAndWidth[aKey] = {'color':aColor,'width':borderWidth}
        return dictOfColorAndWidth
    
    def reformatDictOfColorAndWidth(self,dictOfColorAndWidth):
        reformatedDict ={}
        for aKey, aListOfColorAndWidth in dictOfColorAndWidth.items():
            reformatedDict[aKey] = {'color':aListOfColorAndWidth[0],'width':aListOfColorAndWidth[1]}
        return reformatedDict
    

    def calculateAndRecordCurrentStepStats(self):        
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


    # To handle the info to be displayed in a contextual menu on entitis
    def setAttributeValueToDisplayInContextualMenu(self,aAttribut,aLabel=None):
        # todo add a check that aAttribut exists (in case of miss spelling) 
        aDict={}
        aDict['att']=aAttribut
        aDict['label']= (aLabel if aLabel is not None else aAttribut)
        self.attributesToDisplayInContextualMenu.append(aDict)
    
    # # To handle the attributes concerned by the contextual update menu
    # def setAttributesConcernedByUpdateMenu(self,aAttribut,aLabel=None):
    #     self.updateMenu=True
    #     aDict={}
    #     aDict['att']=aAttribut
    #     aDict['label']= (aLabel if aLabel is not None else aAttribut)
    #     self.attributesToDisplayInUpdateMenu.append(aDict)

# ********************************************************    
#* METHODS USED BY THE MODELER

# to get the entity matching a Id or at a specified coordinates
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

# to get all entities. a condition on the entity can be used to select only some entities
    def getEntities(self, condition=None):

        if condition is None: return self.entities[:]
        return [ent for ent in self.entities if condition(ent)]

    # -----------------------------
    # Model actions scoped on this EntityDef
    def newModelAction(self, actions=None, conditions=None, feedbacks=None):
        """Crée un SGModelAction_OnEntities ciblant les entités de cette définition.

        Args:
            actions (callable | list[callable]): action(s) de signature action(aEntity)
            conditions (callable | list[callable]): condition(s) de signature condition(aEntity)
            feedbacks (callable | list[callable] | SGModelAction): feedback(s)
        """
        actions = actions or []
        conditions = conditions or []
        feedbacks = feedbacks or []
        model_action = SGModelAction_OnEntities(sgModel=self.model, actions=actions, conditions=conditions, feedbacks=feedbacks, entities= (lambda: self.getEntities()))
        self.model.id_modelActions += 1
        model_action.id = self.model.id_modelActions
        return model_action

# to get all entities with a certain value
    def getEntities_withValue(self, att, val):
        return list(filter(lambda ent: ent.value(att)==val, self.entities))

# to get all entities not having a certain value
    def getEntities_withValueNot(self, att, val):
        return list(filter(lambda ent: ent.value(att)!=val, self.entities))

  # Return a random entity
    def getRandomEntity(self, condition=None, listOfEntitiesToPickFrom=None):
        """
        Return a random entity.
        """
        if listOfEntitiesToPickFrom == None:
            listOfEntitiesToPickFrom = self.entities
        if condition == None:
            listOfEntities = listOfEntitiesToPickFrom
        else:
            listOfEntities = [ent for ent in listOfEntitiesToPickFrom if condition(ent)]
        
        return random.choice(listOfEntities) if len(listOfEntities) > 0 else False

   # Return a random entity with a certain value
    def getRandomEntity_withValue(self, att, val, condition=None):
        """
        Return a random entity.
        """
        return self.getRandomEntity(condition=condition, listOfEntitiesToPickFrom=self.getEntities_withValue(att, val))


  # Return a random entity not having a certain value
    def getRandomEntity_withValueNot(self, att, val, condition=None):
        """
        Return a random entity.
        """
        return self.getRandomEntity(condition=condition, listOfEntitiesToPickFrom=self.getEntities_withValueNot(att, val))

    def getRandomEntities(self, aNumber, condition=None, listOfEntitiesToPickFrom=None):
        """
        Return a specified number of random entities.
        args:
            aNumber (int): a number of entities to be randomly selected
        """
        if listOfEntitiesToPickFrom == None:
            listOfEntitiesToPickFrom = self.entities
        if condition == None:
            listOfEntities = listOfEntitiesToPickFrom
        else:
            listOfEntities = [ent for ent in listOfEntitiesToPickFrom if condition(ent)]
        
        return random.sample(listOfEntities, min(aNumber,len(listOfEntities))) if len(listOfEntities) > 0 else []

    # Return random Entities with a certain value
    def getRandomEntities_withValue(self, aNumber, att, val, condition=None):
        """
        Return a specified number of random Entities.
        args:
            aNumber (int): a number of entities to be randomly selected
        """
        return self.getRandomEntities(aNumber, condition=condition, listOfEntitiesToPickFrom=self.getEntities_withValue(att, val))

    # Return random Entities not having a certain value
    def getRandomEntities_withValueNot(self, aNumber, att, val, condition=None):
        """
        Return a specified number of random Entities.
        args:
            aNumber (int): a number of entities to be randomly selected
        """
        return self.getRandomEntities(aNumber, condition=condition, listOfEntitiesToPickFrom=self.getEntities_withValueNot(att, val))


################

# To handle entDefAttributesAndValues
    # setter
    ## THIS METHOD IS COMMENTED BECAUSE IT IS ALREADY DEFINED IN AttributeAndValueFunctionalities 
    # def setValue(self,aAttribut,aValue):
    #     """
    #     Sets the value of an attribut
    #     Args:
    #         aAttribut (str): Name of the attribute
    #         aValue (str): Value to be set
    #     """

    #     if aAttribut in self.dictAttributes and self.dictAttributes[aAttribut]==aValue: return False #The attribute has already this value
    #     #self.saveHistoryValue()
    #     #print("name self : ", self.entities)
    #     self.dictAttributes[aAttribut]=aValue
    #     self.updateWatchersOnAttribute(aAttribut) #This is for watchers on this specific entity
    #     return True

    

    # To define a value for all entities
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

    # set the value of attribut to all entities in a specified column
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

    # set the value of attribut to all entities in a specified row
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

    # To apply a value to a random entity
    def setRandomEntity(self, aAttribute, aValue, condition=None):
        """
        Apply a value to a random entity

        Args:
            aAttribute (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
        """
        self.getRandomEntity(condition=condition).setValue(aAttribute, aValue)

    # To apply a value to a random entity with a certain value
    def setRandomEntity_withValue(self, aAttribut, aValue, conditionAtt, conditionVal, condition=None):
        """
        To apply a value to a random entity with a certain value

        Args:
            aAttribut (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
        """
        self.getRandomEntity_withValue(conditionAtt, conditionVal, condition).setValue(aAttribut, aValue)

   # To apply a value to a random entity not having a certain value
    def setRandomEntity_withValueNot(self, aAttribut, aValue, conditionAtt, conditionVal, condition=None):
        """
       To apply a value to a random entity not having a certain value

        Args:
            aAttribut (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
        """
        self.getRandomEntity_withValueNot(conditionAtt, conditionVal, condition).setValue(aAttribut, aValue)

    # To apply a value to some random entity
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

    # To apply a value to some random entities with a certain value
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

   # To apply a value to some random entities noty having a certain value
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
   
    # To delete all entities of a species
    def deleteAllEntities(self):
        """
        Delete all entities of the species.
        """
        for ent in self.entities[:]:
            self.deleteEntity(ent)

    # To copy a value from one attribute to another
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

################
    # INDICATORS

    # to get the nb of entities
    def nbOfEntities(self):
        return len(self.getEntities())

    # to get the nb of entities who respect certain value
    def nb_withValue(self, att, value):
        return len(self.getEntities_withValue(att, value))
    
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
    

    # def metricOn(cls, listOfEntities, metric, attribute, value):
    #     """
    #     Calculate a value based on the specified metric, attribute, and value for a given list of entities.

    #     Args:
    #         listOfEntities (list): The list of entities to process.
    #         metric (str): The metric to use for statistical evaluation. Possible values include:
    #             - 'nb': Count of entities whose specified attribute is equal to the specified value.
    #             - 'sumAtt': Sum of the specified attribute values.
    #             - 'avgAtt': Average of the specified attribute values.
    #             - 'minAtt': Minimum value of the specified attribute.
    #             - 'maxAtt': Maximum value of the specified attribute.
    #             - 'nbWithLess': Count of entities with attribute values less than the specified value.
    #             - 'nbWithMore': Count of entities with attribute values greater than the specified value.
    #             - 'nbEqualTo': Count of entities with attribute values equal to the specified value.
    #         attribute (str): The attribute to evaluate.
    #         value (optional): The value to compare against for certain metrics.

    #     Returns:
    #         float or int: The calculated value based on the s

# metricOn

# ********************************************************    

# Définition de SGCellDef
class SGCellDef(SGEntityDef):
    def __init__(self, grid, shape, defaultsize, entDefAttributesAndValues, defaultColor=Qt.white, entityName='Cell', defaultCellImage=None):
        super().__init__(grid.model, entityName, shape, defaultsize, entDefAttributesAndValues, defaultColor)
        self.grid = grid
        self.deletedCells = []
        self.defaultImage = defaultCellImage

    def newCell(self, x, y):
        ent = SGCell(self, x, y, self.defaultImage)
        self.entities.append(ent)
        ent.show()

    def setCell(self, x, y, aAttribute, aValue):
        ent = self.getCell(x, y).setValue(aAttribute, aValue)
        return ent

    
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


    def cellIdFromCoords(self, x, y):
        if x < 1 or y < 1:
            return None
        return (x - 1) + self.grid.columns * (y - 1)
        # return x + (self.grid.columns * (y - 1))


    # Return the cell at specified coordinates
    def getEntity(self, x, y=None):
        return self.getCell(x, y)

    def getEntities_withRow(self, aRowNumber):
        return self.grid.getCells_withRow(aRowNumber)

    def getEntities_withColumn(self, aColumnNumber):
        return self.grid.getCells_withColumn(aColumnNumber)

    def cellIdFromCoords(self,x,y):
        if x < 0 or y < 0 : return None
        return x + (self.grid.columns * (y -1))

    def deleteEntity(self, aCell):
        """
        Delete a given cell
        args:
            aCell (instance): the cell to de deleted
        """
        if len(aCell.agents) !=0:
            aCell.deleteAllAgents()
        self.deletedCells.append(aCell)
        aCell.isDisplay = False
        self.entities.remove(aCell)
        self.updateWatchersOnPop()
        self.updateWatchersOnAllAttributes()
        aCell.update()

    def reviveThisCell(self, aCell):
        self.entities.append(aCell)
        aCell.isDisplay = True
        self.deletedCells.remove(aCell)
        self.updateWatchersOnPop()
        self.updateWatchersOnAllAttributes()
        aCell.update()
        

# ********************************************************    


class SGAgentDef(SGEntityDef):
    def __init__(self, sgModel, entityName, shape, defaultsize, entDefAttributesAndValues, defaultColor=Qt.black, locationInEntity="random", defaultImage=None, popupImage=None):
        super().__init__(sgModel, entityName, shape, defaultsize, entDefAttributesAndValues, defaultColor)
        self.locationInEntity = locationInEntity
        self.defaultImage = defaultImage
        self.popupImage = popupImage

    def newAgentOnCell(self, aCell, attributesAndValues=None, image=None, popupImage=None):
        if aCell == None : return
        if image is None:
            image = self.defaultImage
        if popupImage is None:
            popupImage = self.popupImage
        aAgent = SGAgent(aCell, self.defaultsize, attributesAndValues, self.defaultShapeColor, classDef=self, defaultImage=image, popupImage=popupImage)
        self.entities.append(aAgent)
        self.updateWatchersOnPop()
        self.updateWatchersOnAllAttributes()
        aAgent.show()
        return aAgent

    
    def newAgentsOnCell(self, nbAgents, aCell, attributesAndValues=None):
        """
        Create a specific number of new Agents in the associated species.
        Args:
            nbAgents (int) : number of Agents 
            aCell : aCell located on a grid
            attributesAndValues : attributes and values of the new agent
        Return:
            agents
        """
        for n in range(nbAgents):
            self.newAgentOnCell(aCell,attributesAndValues)



    def newAgentAtCoords(self, cellDef_or_grid=None, xCoord=None, yCoord=None, attributesAndValues=None,image=None,popupImage=None):
        """
        Create a new Agent in the associated species.

        Args:
            cellDef_or_grid (instance) : the cellDef or grid you want your agent in. If its None, the first cellDef and grid will be used
            ValueX (int) : Column position in grid (Default=Random)
            ValueY (int) : Row position in grid (Default=Random)
        Flexible calling patterns (backward compatible):
            - newAgentAtCoords(x, y, ...)
            - newAgentAtCoords((x, y), ...)
            - newAgentAtCoords(cellDef_or_grid, x, y, ...)
        Return:
            a agent
        """
        # Normalize arguments to support calls like newAgentAtCoords(3,3) or newAgentAtCoords((3,3))
        if isinstance(cellDef_or_grid, (tuple, list)) and len(cellDef_or_grid) == 2 and xCoord is None and yCoord is None:
            xCoord, yCoord = int(cellDef_or_grid[0]), int(cellDef_or_grid[1])
            cellDef_or_grid = None
        elif isinstance(cellDef_or_grid, int) and isinstance(xCoord, int) and yCoord is None:
            # Called as newAgentAtCoords(x, y, ...)
            xCoord, yCoord = cellDef_or_grid, xCoord
            cellDef_or_grid = None
        elif isinstance(xCoord, (tuple, list)) and len(xCoord) == 2 and yCoord is None:
            # Called as newAgentAtCoords(cellDef_or_grid, (x, y), ...)
            xCoord, yCoord = int(xCoord[0]), int(xCoord[1])

        # Normalize argument cellDef_or_grid to support calls like newAgentAtCoords(Cell,3,3) or newAgentAtCoords(3,3) or newAgentAtCoords(aGrid,3,3)
        if not cellDef_or_grid:
            aCellDef = first_value(self.model.cellOfGrids,None)
        else: 
            aCellDef = self.model.getCellDef(cellDef_or_grid)
        if aCellDef == None : return
        aGrid = self.model.getGrid(aCellDef)


        if xCoord == None: xCoord = random.randint(1, aGrid.columns)
        if yCoord == None: yCoord = random.randint(1, aGrid.rows)
        locationCell = aCellDef.getCell(xCoord, yCoord)
        return self.newAgentOnCell(locationCell, attributesAndValues,image,popupImage)

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

    def newAgentAtRandom(self, cellDef_or_grid=None, attributesAndValues=None,condition=None):
        """
        Create a new Agent in the associated species a place it on a random cell.
        Args:
            cellDef_or_grid (instance): the cellDef or grid you want your agent in. If its None, the first cellDef and grid will be used
            attributesAndValues (dict, optional): mapping of attribute names to values (or callables)
        Flexible calling patterns (backward compatible):
            - newAgentAtRandom()
            - newAgentAtRandom({"health":"good"})
            - newAgentAtRandom(cellDef_or_grid)
            - newAgentAtRandom(cellDef_or_grid, {"health":"good"})
        Return:
            a agent
            """
        # Normalize dict passed as first arg
        if isinstance(cellDef_or_grid, dict) and attributesAndValues is None:
            attributesAndValues = cellDef_or_grid
            cellDef_or_grid = None
        # Normalize argument cellDef_or_grid to support calls like newAgentAtRandom(Cell) or newAgentAtRandom() or newAgentAtRandom(aGrid)
        if not cellDef_or_grid:
            aCellDef = first_value(self.model.cellOfGrids,None)
        else: 
            aCellDef = self.model.getCellDef(cellDef_or_grid)
        if aCellDef == None : return

        locationCell=aCellDef.getRandomEntity(condition=condition)
        return self.newAgentOnCell(locationCell, attributesAndValues)

    def newAgentsAtRandom(self, aNumber, cellDef_or_grid=None, attributesAndValues=None,condition=None):
        """
        Create a number of Agents in the associated species and place them on random cells.
        Args:
            aNumber(int) : number of agents to be created
            cellDef_or_grid (instance) : the cellDef or grid you want your agent in. If its None, the first cellDef and grid will be used
            attributesAndValues (dict, optional): mapping of attribute names to values (or callables)
        Flexible calling patterns (backward compatible):
            - newAgentsAtRandom(7)
            - newAgentsAtRandom(7, {"health":"good", "hunger":"bad"})
            - newAgentsAtRandom(7, cellDef_or_grid)
            - newAgentsAtRandom(7, cellDef_or_grid, attributesAndValues)
        Return:
            a list of agents
            """ 
        
        # Normalize arguments to support calls like newAgentsAtRandom(7) or newAgentsAtRandom(7, {..})
        if isinstance(cellDef_or_grid, dict) and attributesAndValues is None:
            attributesAndValues = cellDef_or_grid
            cellDef_or_grid = None
            
        # Normalize argument cellDef_or_grid to support calls like newAgentAtRandom(Cell) or newAgentAtRandom() or newAgentAtRandom(aGrid)
        if not cellDef_or_grid:
            aCellDef = first_value(self.model.cellOfGrids,None)
        else: 
            aCellDef = self.model.getCellDef(cellDef_or_grid)
        if aCellDef == None : return
        
        locationCells=aCellDef.getRandomEntities(aNumber, condition=condition)
        alist =[]
        for aCell in locationCells:
            alist.append(self.newAgentOnCell(aCell, attributesAndValues))
        return alist


    # To randomly move all agents
    def moveRandomly(self, numberOfMovement=1,condition=None):
        """
        All agents of the species move randomly.

        args:
            numberOfMovement (int): number of movements in one action
            condition (lambda function, optional): a condition that the destination cell should respect for the agent to move
        """
        for aAgent in self.entities[:]: # Need to iterate on a copy of the entities list, because , due to the moveByRecreating, the entities list changes during the loop
            aAgent.moveAgent(numberOfMovement=numberOfMovement,condition=condition)



    def deleteEntity(self, aAgent):
        """
        Delete a given agent
        args:
            aAgent (instance): the agent to de deleted
        """
        aAgent.cell.updateDepartureAgent(aAgent)
        aAgent.deleteLater()
        self.entities.remove(aAgent)
        self.updateWatchersOnPop()
        self.updateWatchersOnAllAttributes()
        #aAgent.update()

    

