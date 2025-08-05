import json
import numbers
#A class to be inherited, that handlse the attributs and values

class AttributeAndValueFunctionalities():

    def initAttributes(self,attributesAndValues):
        self.dictAttributes={}
        if attributesAndValues is None: return
        for aAtt, valueToSet in attributesAndValues.items():
            if callable(valueToSet):
                self.setValue(aAtt,valueToSet())
            else:
                self.setValue(aAtt,valueToSet)
    
    def setValue(self,aAttribut,valueToSet):
        """
        Sets the value of an attribut
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be set
        """
        if callable(valueToSet):
            aValue = valueToSet()
        else:
            aValue = valueToSet
        if aAttribut in self.dictAttributes and self.dictAttributes[aAttribut]==aValue: return False #The attribute has already this value
        self.dictAttributes[aAttribut]=aValue
        self.saveValueInHistory(aAttribut,aValue)
        if hasattr(self, 'classDef'): # This is to prevent the EntDef from executing the following line
            self.classDef.updateWatchersOnAttribute(aAttribut) # This is for watchers on the whole pop of entities
        self.updateWatchersOnAttribute(aAttribut) #This is for watchers on this specific entity
        if hasattr(self, 'update') and callable(getattr(self, 'update')):  # This is to prevent the EntDef from executing the following line
            self.update()
        return True
    
    def value(self,att):
        """
        Return the value of a cell Attribut
        Args:
            att (str): Name of the attribute
        """
        return self.dictAttributes.get(att,None)
    
    def getValue(self,att):
        """
        Return the value of a cell Attribut
        Args:
            att (str): Name of the attribute
        """
        return self.value(att)
    
    def incValue(self,aAttribut,valueToSet=1,max=None):
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
        #self.setValue(aAttribut,(self.value(aAttribut)+aValue if max is None else min(self.value(aAttribut)+aValue,max)))
        # This method is equivalent to 
        # newValue = self.value(aAttribut)+aValue
        # if max is not None: newValue = min(newValue,max)    
        # self.setValue(aAttribut,newValue)

    def decValue(self,aAttribut,aValue=1,min=None):
        """
        Decrease the value of an attribut with an additional value
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be subtracted to the current value of the attribute
        """

        if isinstance(self.value(aAttribut), numbers.Number) and isinstance(aValue, numbers.Number):
            self.setValue(aAttribut,(self.value(aAttribut)-aValue if min is None else max(self.value(aAttribut)-aValue,min)))

    def calcValue(self,aAttribut,aLambdaFunction):
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
        else: raise ValueError ('calcValue works with a lambda function')

    def saveValueInHistory(self,aAttribute,aValue):
        self.history["value"][aAttribute].append([self.model.timeManager.currentRoundNumber,self.model.timeManager.currentPhaseNumber,aValue])
  
    def getDictOfAttributes_atRoundAndPhase(self,aRound,aPhase):
        ## Should use the DataRecorder method
        raise SyntaxError('Should use the DataRecorder method')
    
    def getAttributeValue_atRoundAndPhase(self,aRound,aPhase,aAttribute):
        aItem = next((item for item in reversed(self.history["value"][aAttribute])  if item[0] == aRound and item[1] == aPhase),None)
        if aItem: return aItem[2]
        else: return self.getDictOfAttributes_atRoundAndPhase(aRound,aPhase)[aAttribute]

    def getInitialValue(self,aAttribute):
        return self.getAttributeValue_atRoundAndPhase(0,0,aAttribute)


    def getListOfUntagedStepsData(self,startStep=None,endStep=None):
        if self.history["value"]=={}: return []
        aList=[]
        tmpDict={}
        nbPhases = self.model.timeManager.numberOfPhases()

        # create a dict (tmpDict) of attribute values with keys as dates of the value updates of each attribute
        for aAtt, listOfData in self.history["value"].items():
            for aData in listOfData:
                tmpDict[json.dumps([aData[0],aData[1],aAtt])]=aData[2]

        # sort the keys of tmpDict that represent dates (or steps) in chronological order
        def keyfunction(dumped_item):
            item = json.loads(dumped_item)
            return item[0],item[1]
        sortedKeys = sorted(list(tmpDict.keys()),key=keyfunction)

        startDate = startStep or [json.loads(sortedKeys[0])[0],json.loads(sortedKeys[0])[1]]

        # endDate = endStep or [json.loads(sortedKeys[-1])[0],json.loads(sortedKeys[-1])[1]]
        #equivalent to
        # startTime = startStep if startStep is not None else [json.loads(sortedKeys[0])[0],json.loads(sortedKeys[0])[1]]
        # endTime = endStep if endStep is not None else [json.loads(sortedKeys[-1])[0],json.loads(sortedKeys[-1])[1]]
        # --> because if startStep is None or empty the 'or' will return the right hand value
        endDate = [self.model.roundNumber(),self.model.phaseNumber()]

        #In case no value exists in tmpDict at the startDate for a given attribute, adds a value that is equal to the previous known value of the attribute
        for aAtt in self.history["value"].keys():
            aVal=tmpDict.get(json.dumps([startDate[0],startDate[1],aAtt]), 'no key recorded')
            if aVal == 'no key recorded':
                datesForAtt = list(filter(lambda x: json.loads(x)[2]== aAtt,sortedKeys))
                datesForAtt.append(json.dumps(startDate))
                newSortedDatesForAtt = sorted(datesForAtt,key=keyfunction)
                previousDateWithValueForAtt = newSortedDatesForAtt[(newSortedDatesForAtt.index(json.dumps(startDate))) -1]
                tmpDict[json.dumps([startDate[0],startDate[1],aAtt])]=tmpDict[previousDateWithValueForAtt]

        #Loop over all the dates in between startDate and endDate and fill a list of stepData with the values of each attribute
        aDate = startDate
        endTime_reached=False
        while not endTime_reached:
            if aDate==endDate: endTime_reached=True
            aStepData = {
                'round': aDate[0],
                'phase': aDate[1],
                'dictAttributes': {}
                }
            for aAtt in self.history["value"].keys():
                aVal=tmpDict.get(json.dumps([aDate[0],aDate[1],aAtt]), 'no key recorded')
                if aVal == 'no key recorded': aVal =  aList[-1]['dictAttributes'][aAtt]
                aStepData['dictAttributes'][aAtt]=aVal
            aList.append(aStepData)
            if aDate[1]==nbPhases or aDate[0]==0 : aDate=[aDate[0]+1,1]
            else: aDate=[aDate[0],aDate[1]+1]
        return aList

