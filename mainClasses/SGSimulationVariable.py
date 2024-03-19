from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.AttributeAndValueFunctionalities import *


   
#Class who is responsible of indicator creation 
class SGSimulationVariable():
    def __init__(self,parent,initValue,name,color,isDisplay=True):
        #Basic initialize
        self.model=parent
        #self.value=initValue
        self.name=name
        self.color=color
        self.isDisplay=isDisplay
        self.watchers=[]
        self.history=[]
        self.setValue(initValue)

        

    def setValue(self,newValue):
        self.value=newValue
        self.saveValueInHistory(newValue)     
        for watcher in self.watchers:
            watcher.checkAndUpdate()

    def saveValueInHistory(self,aValue):
        self.history.append([self.model.timeManager.currentRoundNumber,self.model.timeManager.currentPhaseNumber,aValue])

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

    def getListOfStepsData(self):
        if self.history==[]: return []
        aList=[]
        tmpDict={}
        nbPhases = len(self.model.timeManager.phases)
        for aData in self.history:
            tmpDict[json.dumps([aData[0],aData[1]])]=aData[2]
        def keyfunction(dumped_item):
            item = json.loads(dumped_item)
            return item[0],item[1]
        sortedKeys = sorted(list(tmpDict.keys()),key=keyfunction)
        startTime=[json.loads(sortedKeys[0])[0],json.loads(sortedKeys[0])[1]]
        endTime=[json.loads(sortedKeys[-1])[0],json.loads(sortedKeys[-1])[1]]
        aDate = startTime
        endTime_reached=False
        while not endTime_reached:
            if aDate==endTime: endTime_reached=True
            aStepData = {
                'simVarName': self.name,
                'round': aDate[0],
                'phase': aDate[1]
                }
            aVal=tmpDict.get(json.dumps([aDate[0],aDate[1]]), 'no key recorded')
            if aVal == 'no key recorded': aVal =  aList[-1]['value']
            aStepData['value']=aVal
            aList.append(aStepData)
            if aDate[1]==nbPhases or aDate[0]==0 : aDate=[aDate[0]+1,1]
            else: aDate=[aDate[0],aDate[1]+1]
        return aList
    