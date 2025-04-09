from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from mainClasses.SGSimulationVariable import SGSimulationVariable

   
#Class who is responsible of indicator creation 
class SGIndicator():
    def __init__(self,parent,name,method,attribute,value,listOfEntDef,logicOp,color,displayRefresh,onTimeConditions,isDisplay,displayName,conditionsOnEntities):
    # def __init__(self,parent,name,method,attribute,value,listOfEntDef,logicOp,color=Qt.blue,displayRefresh="instantaneous",onTimeConditions=None,isDisplay=True,displayName=True,conditionsOnEntities=[]):
        self.dashboard=parent
        self.method=method
        if self.method=="thresoldToLogicOp":
            self.threshold= value
        else : 
            self.value=value
        self.methods=["sumAtt","avgAtt","minAtt","maxAtt","nb","nbWithLess","nbWithMore","nbEqualTo","thresoldToLogicOp"]
        self.listOfEntDef=listOfEntDef
        if self.method in ["display", "thresoldToLogicOp"]: self.entity=listOfEntDef  
        if self.method == "simVar": self.simVar=listOfEntDef  
        self.result=float
        self.name=name
        self.attribute=attribute
        self.posY = self.dashboard.posYOfItems
        self.dashboard.posYOfItems += 1
        self.color=color
        self.logicOp=logicOp
        self.isDisplay=isDisplay
        self.displayName=displayName
        self.displayRefresh=displayRefresh
        self.timeConditions=onTimeConditions 
        self.conditionsOnEntities=conditionsOnEntities
        self.initUI()
        

    def initUI(self):
        calcValue=self.byMethod()
        self.result=calcValue
        self.setName()
        self.label = QtWidgets.QLabel(self.name + str(calcValue))
        color = QColor(self.color)
        color_string = f"color: {color.name()};"
        self.label.setStyleSheet(color_string+"border: none;background-color: transparent;")

    def setName(self):
        if not self.displayName:
            self.name = ''
            return
        if self.name is not None:
            self.name = self.name + ' : '
            return 
        if self.method in ["nbWithLess","nbWithMore","nbEqualTo"]:
            aName= 'nb '+self.attribute+ ' '+self.method[2:]+" "+self.value+" : "
        elif self.attribute is not None:
                aName = self.method+' '+self.attribute+" : "
        elif self.method == 'nb':
            aName = self.method+' '+self.strOfEntitiesName()+' : '
        elif self.method == "separator":
            aName = ""
        else:
            aName = self.method+' : '
        self.name = aName

    def strOfEntitiesName(self):
        return ",".join([entDef.entityName for entDef in self.listOfEntDef])

    def checkAndUpdate(self):
        if self.getUpdatePermission():
            self.updateText()

    def updateText(self):
        newCalc=self.byMethod()
        self.result=newCalc
        newText= self.name + str(self.result)
        self.label.setText(newText)
        # ajout pour gérer le size
        self.label.setFixedWidth(self.label.fontMetrics().boundingRect(self.label.text()).width()+5)
        self.label.setFixedHeight(self.label.fontMetrics().boundingRect(self.label.text()).height())
        self.label.adjustSize()
        # self.label.update()

        self.dashboard.model.timeManager.updateEndGame()

    def setResult(self, aValue):
        """Function to configure a score in an Indicator"""
        self.result=aValue
        self.label.setText(self.name + str(self.result))
        # ajout pour gérer le size
        self.label.setFixedWidth(self.label.fontMetrics().boundingRect(self.label.text()).width()+5)
        self.label.setFixedHeight(self.label.fontMetrics().boundingRect(self.label.text()).height())
        self.label.adjustSize()
        # self.setMinimumSize(self.geometry().size())

        if isinstance(self.listOfEntDef,SGSimulationVariable):
            self.listOfEntDef.setValue_silently(aValue)

        self.dashboard.model.timeManager.updateEndGame()

    
    def getUpdatePermission(self):
        if self.displayRefresh=='instantaneous':
            return True
        if self.displayRefresh=='onTimeConditions':
            testResult=True
            for typeCondition,specifiedValue in self.timeConditions.items():
                if typeCondition == 'phaseName' :
                    aTest=self.updateOnPhaseName(specifiedValue) 
                if typeCondition == 'phaseNumber' :
                    aTest=self.updateOnPhaseNumber(specifiedValue)
                if typeCondition == 'roundNumber' :
                    aTest=self.updateOnRoundNumber(specifiedValue)
                if typeCondition == 'lambdaTestOnPhaseNumber' :
                    aTest=self.lambdaTestOnPhaseNumber(specifiedValue)
                if typeCondition == 'lambdaTestOnRoundNumber' :
                    aTest=self.lambdaTestOnRoundNumber(specifiedValue)
                testResult = testResult and aTest
            return testResult

    def updateOnPhaseName(self,specifiedValue):
        currentPhase=self.dashboard.model.timeManager.getCurrentPhase()
        if isinstance(specifiedValue,list):
            if currentPhase.name in specifiedValue:
                return True
        if isinstance(specifiedValue,str):
            if currentPhase.name == specifiedValue:
                return True
        return False

    def updateOnPhaseNumber(self,specifiedValue):
        currentPhaseNumber=self.dashboard.model.timeManager.currentPhaseNumber
        if isinstance(specifiedValue,list):
            if currentPhaseNumber in specifiedValue:
                return True
        if isinstance(specifiedValue,int):
            if currentPhaseNumber == specifiedValue:
                return True
        return False

    def updateOnRoundNumber(self,specifiedValue):
        currentRoundNumber=self.dashboard.model.timeManager.currentRoundNumber
        if isinstance(specifiedValue,list):
            if currentRoundNumber in specifiedValue:
                return True
        if isinstance(specifiedValue,int):
            if currentRoundNumber == specifiedValue:
                return True
        return False 
    
    def lambdaTestOnPhaseNumber(self,specifiedValue):
        res = True 
        currentPhaseNumber=self.dashboard.model.timeManager.currentPhaseNumber
        for aCondition in specifiedValue:
            res = res and (aCondition() if aCondition.__code__.co_argcount == 0 else aCondition(currentPhaseNumber))
        return res

    def lambdaTestOnRoundNumber(self,specifiedValue):
        res = True 
        currentRoundNumber=self.dashboard.model.timeManager.currentRoundNumber
        for aCondition in specifiedValue:
            res = res and (aCondition() if aCondition.__code__.co_argcount == 0 else aCondition(currentRoundNumber))
        return res

    
    def getListOfEntities(self):
        listOfAllEntities = [j for i in [entDef.entities for entDef in self.listOfEntDef] for j in i]  
        if self.conditionsOnEntities:
            entitiesSatisfyingConditions = []
            for aEnt in listOfAllEntities:
                for aCondition in self.conditionsOnEntities:
                    if aCondition(aEnt): entitiesSatisfyingConditions.append(aEnt)
            return entitiesSatisfyingConditions
        return listOfAllEntities
    
    
    
    def byMethod(self):
        if self.method == 'nb':
            if self.attribute is not None and self.value is not None:
                listEntities = self.getListOfEntities()
                return SGIndicator.metricOn(listEntities, 'nb', self.attribute, self.value)
            else:
                listEntities = self.getListOfEntities()
                return SGIndicator.metricOn(listEntities, 'nb', self.attribute)

        elif self.method in ["sumAtt", "avgAtt", "minAtt", "maxAtt", "nbWithLess", "nbWithMore", "nbEqualTo"]:
            listEntities = self.getListOfEntities()
            return SGIndicator.metricOn(listEntities, self.method, self.attribute, self.value)
      
        elif self.method=="simVar":
            return self.simVar.value
        
        elif self.method =="display":
            return self.entity.value(self.attribute)
        
        elif self.method=="separator":
            return "---------------"
        
        elif self.method=="thresoldToLogicOp":
            if self.logicOp =="greater":
                if self.entity.value(self.attribute) > self.threshold:
                    calcValue="greater than"+str(self.threshold)
                    return calcValue
            if self.logicOp =="greater or equal":
                if self.entity.value(self.attribute)>=self.threshold:
                    calcValue="greater than or equal to"+str(self.threshold)
                    return calcValue
            if self.logicOp =="equal":
                if self.entity.value(self.attribute)==self.threshold:
                    calcValue="equal to"+str(self.threshold)
                    return calcValue
            if self.logicOp =="less or equal":
                if self.entity.value(self.attribute)<=self.threshold:
                    calcValue="less than or equal to"+str(self.threshold)
                    return calcValue
            if self.logicOp =="less":
                if self.entity.value(self.attribute)<self.threshold:
                    calcValue="less than"+str(self.threshold)
                    return calcValue   

    def getMethods(self):
        print(self.methods)

    @classmethod
    def metricOn(cls, listOfEntities, metric, attribute, value):
        """
        Calculate a value based on the specified metric, attribute, and value for a given list of entities.

        Args:
            listOfEntities (list): The list of entities to process.
            metric (str): The metric to use for statistical evaluation. Possible values include:
                - 'nb': Count of entities whose specified attribute is equal to the specified value.
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
            float or int: The calculated value based on the specified metric.
        """
        calcValue = 0.0
        counter = 0
        
        if metric == 'nb':
            if attribute is not None and value is not None:
                filteredList = [entity for entity in listOfEntities if entity.value(attribute) == value]
                return len(filteredList)
            else:
                return len(listOfEntities)
        
        elif metric in ["sumAtt", "avgAtt", "minAtt", "maxAtt", "nbWithLess", "nbWithMore", "nbEqualTo"]:
            listOfValues = [aEnt.value(attribute) for aEnt in listOfEntities]
            if metric == 'sumAtt':
                return sum(listOfValues)
            if metric == 'avgAtt':
                return round(sum(listOfValues) / len(listOfValues), 2) if listOfValues else 0
            if metric == 'minAtt':
                return min(listOfValues) if listOfValues else 0
            if metric == 'maxAtt':
                return max(listOfValues) if listOfValues else 0
            if metric == 'nbWithLess':
                return len([x for x in listOfValues if x < value])
            if metric == 'nbWithMore':
                return len([x for x in listOfValues if x > value])
            if metric == 'nbEqualTo':
                return len([x for x in listOfValues if x == value])
        else:
            raise ValueError(f"Invalid metric: '{metric}'. Please provide a valid metric.")


            

