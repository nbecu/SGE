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
        # self.saveHistoryValue()
        # print("1- self.dictAttributes[aAttribut]==aValue : ", self.dictAttributes[aAttribut] == aValue)
        # self.saveValueInHistory(aAttribut,aValue)    
        self.dictAttributes[aAttribut]=aValue
        self.saveValueInHistory(aAttribut,aValue)

        # print("2- self.dictAttributes[aAttribut]==aValue : ", self.dictAttributes[aAttribut]==aValue)

        self.classDef.updateWatchersOnAttribute(aAttribut) #This is for watchers on the wole pop of entities
        self.updateWatchersOnAttribute(aAttribut) #This is for watchers on this specific entity
        self.update()
        return True
    
    def value(self,att):
        """
        Return the value of a cell Attribut
        Args:
            att (str): Name of the attribute
        """
        return self.dictAttributes.get(att,None)
    
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
        if isinstance(self.value(aAttribut), int) and isinstance(aValue, int):
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

        if isinstance(self.value(aAttribut), int) and isinstance(aValue, int):
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