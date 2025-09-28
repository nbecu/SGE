import json
import numbers
#A class to be inherited, that handlse the attributs and values

class AttributeAndValueFunctionalities():

    def __init__(self):
        """Initialize the attribute and value functionalities"""
        # Initialize history for tracking attribute changes
        self.history = {"value": {}}

    # ============================================================================
    # DEVELOPER METHODS
    # ============================================================================

    def initAttributes(self, attributesAndValues):
        """Initialize attributes with given values"""
        self.dictAttributes = {}
        if attributesAndValues is None: 
            return
        for aAtt, valueToSet in attributesAndValues.items():
            if callable(valueToSet):
                self.setValue(aAtt, valueToSet())
            else:
                self.setValue(aAtt, valueToSet)

    # History management methods
    def saveValueInHistory(self, aAttribute, aValue):
        """Save attribute value in history for tracking changes"""
        self.history["value"][aAttribute].append([self.model.timeManager.currentRoundNumber, self.model.timeManager.currentPhaseNumber, aValue])
  
    def getDictOfAttributes_atRoundAndPhase(self, aRound, aPhase):
        """Get dictionary of attributes at specific round and phase - Should use the DataRecorder method"""
        raise SyntaxError('Should use the DataRecorder method')
    
    def getAttributeValue_atRoundAndPhase(self, aRound, aPhase, aAttribute):
        """Get attribute value at specific round and phase"""
        aItem = next((item for item in reversed(self.history["value"][aAttribute]) if item[0] == aRound and item[1] == aPhase), None)
        if aItem: 
            return aItem[2]
        else: 
            return self.getDictOfAttributes_atRoundAndPhase(aRound, aPhase)[aAttribute]

    def getInitialValue(self, aAttribute):
        """Get initial value of an attribute"""
        return self.getAttributeValue_atRoundAndPhase(0, 0, aAttribute)

    def getListOfUntagedStepsData(self, startStep=None, endStep=None):
        """Get list of untagged steps data for analysis"""
        if self.history["value"] == {}: 
            return []
        aList = []
        tmpDict = {}
        nbPhases = self.model.timeManager.numberOfPhases()

        # create a dict (tmpDict) of attribute values with keys as dates of the value updates of each attribute
        for aAtt, listOfData in self.history["value"].items():
            for aData in listOfData:
                tmpDict[json.dumps([aData[0], aData[1], aAtt])] = aData[2]

        # sort the keys of tmpDict that represent dates (or steps) in chronological order
        def keyfunction(dumped_item):
            item = json.loads(dumped_item)
            return item[0], item[1]
        sortedKeys = sorted(list(tmpDict.keys()), key=keyfunction)

        startDate = startStep or [json.loads(sortedKeys[0])[0], json.loads(sortedKeys[0])[1]]

        # endDate = endStep or [json.loads(sortedKeys[-1])[0],json.loads(sortedKeys[-1])[1]]
        #equivalent to
        # startTime = startStep if startStep is not None else [json.loads(sortedKeys[0])[0],json.loads(sortedKeys[0])[1]]
        # endTime = endStep if endStep is not None else [json.loads(sortedKeys[-1])[0],json.loads(sortedKeys[-1])[1]]
        # --> because if startStep is None or empty the 'or' will return the right hand value
        endDate = [self.model.roundNumber(), self.model.phaseNumber()]

        #In case no value exists in tmpDict at the startDate for a given attribute, adds a value that is equal to the previous known value of the attribute
        for aAtt in self.history["value"].keys():
            aVal = tmpDict.get(json.dumps([startDate[0], startDate[1], aAtt]), 'no key recorded')
            if aVal == 'no key recorded':
                datesForAtt = list(filter(lambda x: json.loads(x)[2] == aAtt, sortedKeys))
                datesForAtt.append(json.dumps(startDate))
                newSortedDatesForAtt = sorted(datesForAtt, key=keyfunction)
                previousDateWithValueForAtt = newSortedDatesForAtt[(newSortedDatesForAtt.index(json.dumps(startDate))) - 1]
                tmpDict[json.dumps([startDate[0], startDate[1], aAtt])] = tmpDict[previousDateWithValueForAtt]

        #Loop over all the dates in between startDate and endDate and fill a list of stepData with the values of each attribute
        aDate = startDate
        endTime_reached = False
        while not endTime_reached:
            if aDate == endDate: 
                endTime_reached = True
            aStepData = {
                'round': aDate[0],
                'phase': aDate[1],
                'dictAttributes': {}
            }
            for aAtt in self.history["value"].keys():
                aVal = tmpDict.get(json.dumps([aDate[0], aDate[1], aAtt]), 'no key recorded')
                if aVal == 'no key recorded': 
                    aVal = aList[-1]['dictAttributes'][aAtt]
                aStepData['dictAttributes'][aAtt] = aVal
            aList.append(aStepData)
            if aDate[1] == nbPhases or aDate[0] == 0: 
                aDate = [aDate[0] + 1, 1]
            else: 
                aDate = [aDate[0], aDate[1] + 1]
        return aList


    # Attribute access methods
    # @CATEGORY: GET
    def value(self, att):
        """
        Return the value of a cell Attribut
        Args:
            att (str): Name of the attribute
        """
        return self.dictAttributes.get(att, None)

    def hasAttribute(self, att):
        """
        Check if the entity has a specific attribute defined.
        
        Args:
            att (str): Name of the attribute to check
            
        Returns:
            bool: True if the attribute exists and has a value, False otherwise
        """
        return att in self.dictAttributes and self.dictAttributes[att] is not None

    
    # ============================================================================
    # MODELER METHODS
    # ============================================================================

    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================

    
    def setValue(self, aAttribut, valueToSet):
        """
        Sets the value of an attribut
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be set. If a value is callable, it will be invoked and its return value will be used
        """
        if callable(valueToSet):
            aValue = valueToSet()
        else:
            aValue = valueToSet
        if aAttribut in self.dictAttributes and self.dictAttributes[aAttribut] == aValue: 
            return False  # The attribute has already this value
        self.dictAttributes[aAttribut] = aValue
        self.saveValueInHistory(aAttribut, aValue)
        if hasattr(self, 'type'):  # This is to prevent the EntDef from executing the following line
            self.type.updateWatchersOnAttribute(aAttribut)  # This is for watchers on the whole pop of entities
        self.updateWatchersOnAttribute(aAttribut)  # This is for watchers on this specific entity
        if hasattr(self, 'update') and callable(getattr(self, 'update')):  # This is to prevent the EntDef from executing the following line
            self.update()
        return True
    
    def setValues(self, dictOfAttributesAndValues):
        """
        Set multiple attribute values at once.
        Args:
            dictOfAttributesAndValues (dict): mapping of attribute names to values (or callables).
        """
        for att, value in dictOfAttributesAndValues.items():
            self.setValue(att, value)

    # @CATEGORY: SET
    def incValue(self, aAttribut, valueToSet=1, max=None):
        """
        Increase the value of an attribut with an additional value
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be added to the current value of the attribute
        """
        if callable(valueToSet):
            aValue = valueToSet()
        else:
            aValue = valueToSet
        if isinstance(self.value(aAttribut), numbers.Number) and isinstance(aValue, numbers.Number):
            self.setValue(aAttribut,
                          (self.value(aAttribut) + aValue if max is None else min(self.value(aAttribut) + aValue, max)))

    # @CATEGORY: SET
    def decValue(self, aAttribut, valueToSet=1, min=None):
        """
        Decrease the value of an attribut with an additional value
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be subtracted to the current value of the attribute
        """
        if callable(valueToSet):
            aValue = valueToSet()
        else:
            aValue = valueToSet

        if isinstance(self.value(aAttribut), numbers.Number) and isinstance(aValue, numbers.Number):
            self.setValue(aAttribut, (self.value(aAttribut) - aValue if min is None else max(self.value(aAttribut) - aValue, min)))

    # @CATEGORY: SET
    def calcValue(self, aAttribut, aLambdaFunction):
        """
        Apply a calculation on the value of an attribut using a lambda function
        
        Args:
            aAttribut (str): Name of the attribute
            aLambda function(lambda) : a lambda function. ex (lambda x: x * 1.2 +5))
        """
        if callable(aLambdaFunction):
            currentValue = self.value(aAttribut)
            result = aLambdaFunction(currentValue)
            self.setValue(aAttribut, result)
        else: 
            raise ValueError('calcValue works with a lambda function')

    # @CATEGORY: SET
    def copyValue(self, source_att, target_att):
        """
        Copy the value of an attribut (source_att), in another attribute (target_att)
        Args:
            source_att (str): Name of the attribute copied
            target_att  (str): Name of the attribute set
        """
        if not hasattr(self, 'dictAttributes') or source_att not in self.dictAttributes:
            obj_id = getattr(self, 'privateID', None) or getattr(self, 'id', None) or '<SGObject>'
            raise ValueError(f'copyValue: attribute "{source_att}" does not exist on {obj_id}')
        self.setValue(target_att, self.value(source_att))

    # ============================================================================
    # DELETE METHODS
    # ============================================================================

    # (No specific DELETE methods in AttributeAndValueFunctionalities)

    # ============================================================================
    # GET/NB METHODS
    # ============================================================================

    def getValue(self, att):
        """
        Return the value of a cell Attribut
        Args:
            att (str): Name of the attribute
        """
        return self.value(att)

    # ============================================================================
    # IS/HAS METHODS
    # ============================================================================

    # @CATEGORY: IS
    def isValue(self, attribut_to_test, value_to_test):
        """
        Tests if the the value of an attribut if equal to a value
        Args:
            attribut_to_test (str): Name of the attribute
            value_to_test (str): Value to be set. If a value is callable, it will be invoked and its return value will be used
        """
        return self.getValue(attribut_to_test) == value_to_test

    # @CATEGORY: IS
    def isNotValue(self, attribut_to_test, value_to_test):
        """
        Tests if the the value of an attribut is not equal to a value
        Args:
            attribut_to_test (str): Name of the attribute
            value_to_test (str): Value to be set. If a value is callable, it will be invoked and its return value will be used
        """
        return self.getValue(attribut_to_test) != value_to_test

    # ============================================================================
    # DO/DISPLAY METHODS
    # ============================================================================

    # (No specific DO/DISPLAY methods in AttributeAndValueFunctionalities)

    # ============================================================================
    # OTHER MODELER METHODS
    # ============================================================================

    # (No specific OTHER MODELER methods in AttributeAndValueFunctionalities)

