from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null
# import numpy as np
from mainClasses.SGCell import SGCell
from mainClasses.SGAgent import SGAgent
from mainClasses.AttributeAndValueFunctionalities import *


   
#Class who is responsible of indicator creation 
class SGSimulationVariable():
    def __init__(self,parent,initValue,name,color,isDisplay=True):
        #Basic initialize
        self.model=parent
        self.value=initValue
        self.name=name
        self.color=color
        self.isDisplay=isDisplay
        self.watchers=[]
        

    def setValue(self,newValue):
        self.value=newValue
        for watcher in self.watchers:
            watcher.checkAndUpdate()
    
    def incValue(self,aValue=1,max=None):
        """
        Increase the value with an additional value
        Args:
            aValue (str): Value to be added to the current value of the attribute
        """       
        self.setValue(self.value+aValue if max is None else min(self.value+aValue,max))

    def decValue(self,aValue=1,min=None):
        """
        Decrease the value with an additional value
        Args:
            aValue (str): Value to be subtracted to the current value of the attribute
        """       
        self.setValue(self.value-aValue if min is None else max(self.value-aValue,min))

    def calcValue(self,aLambdaFunction):
        """
        Apply a calculation on the value using a lambda function
        
        Args:
            aLambda function(lambda) : a lambda function. ex (lambda x: x * 1.2 +5))
        """
        if callable(aLambdaFunction):
            result = aLambdaFunction(self.value)
            self.setValue(result)
        else: raise ValueError ('calcValue works with a lambda function')

    
    def addWatcher(self,aIndicator):
        self.watchers.append(aIndicator)
    
    
    # eventuellement un jour ajouter la fonctionnalité pour le modeler 
        # def resetValueAtEachRound(self,aAttribut,valueToBeSetAtEachRound):
        #     self.setValue(aAttribut, result)