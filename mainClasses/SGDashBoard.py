from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null, true

from SGGameSpace import SGGameSpace
from SGIndicators import SGIndicators


#Class who is responsible of the Legend creation 
class SGDashBoard(SGGameSpace):
    def __init__(self,parent,title,displayRefresh='instantaneous',borderColor=Qt.black,backgroundColor=Qt.transparent,layout="vertical"):
        super().__init__(parent,0,60,0,0,true,backgroundColor)
        self.model=parent
        self.id=title
        self.indicatorNames=[]
        self.indicators=[]
        self.borderColor=borderColor
        self.backgroundColor=backgroundColor
        self.y=0
        self.isDisplay=True
        self.displayRefresh=displayRefresh
        self.IDincr=0
        if layout=='vertical':
            self.layout=QtWidgets.QVBoxLayout()
        elif layout=='horizontal':
            self.layout=QtWidgets.QHBoxLayout()



    def initUI(self):
        self.y=0
        self.setLayout(self.layout)
        for indicator in self.indicators:
            self.y=+1
            indicator.show()
            

    def checkDisplay(self):
        if self.isDisplay:
            return True
        else:
            return False
        

    def addIndicator(self,method,entity,attribut,value=None,indicatorName=None,color=Qt.black):
        indicator=SGIndicators(self,self.y,indicatorName,method,attribut,value,entity,color)
        self.indicatorNames.append(indicator.name)
        self.indicators.append(indicator)
        self.layout.addWidget(indicator)
        indicator.id=self.IDincr
        self.IDincr=+1

    def addIndicator_Sum(self,entity,attribut,value,indicatorName,color=Qt.black):
        method='sumAtt'
        indicator=SGIndicators(self,self.y,indicatorName,method,attribut,value,entity,color)
        self.indicatorNames.append(indicator.name)
        self.indicators.append(indicator)
        self.layout.addWidget(indicator)
        indicator.id=self.IDincr
        self.IDincr=+1
    
    def addIndicator_Avg(self,entity,attribut,value,indicatorName,color=Qt.black):
        method='avgAtt'
        indicator=SGIndicators(self,self.y,indicatorName,method,attribut,value,entity,color)
        self.indicatorNames.append(indicator.name)
        self.indicators.append(indicator)
        self.layout.addWidget(indicator)
        indicator.id=self.IDincr
        self.IDincr=+1

    def addIndicator_Min(self,entity,attribut,value,indicatorName,color=Qt.black):
        method='minAtt'
        indicator=SGIndicators(self,self.y,indicatorName,method,attribut,value,entity,color)
        self.indicatorNames.append(indicator.name)
        self.indicators.append(indicator)
        self.layout.addWidget(indicator)
        indicator.id=self.IDincr
        self.IDincr=+1

    def addIndicator_Max(self,entity,attribut,value,indicatorName,color=Qt.black):
        method='maxAtt'
        indicator=SGIndicators(self,self.y,indicatorName,method,attribut,value,entity,color)
        self.indicatorNames.append(indicator.name)
        self.indicators.append(indicator)
        self.layout.addWidget(indicator)
        indicator.id=self.IDincr
        self.IDincr=+1
    
    def addIndicator_EqualTo(self,entity,attribut,value,indicatorName,color=Qt.black):
        method='nbEqualTo'
        indicator=SGIndicators(self,self.y,indicatorName,method,attribut,value,entity,color)
        self.indicatorNames.append(indicator.name)
        self.indicators.append(indicator)
        self.layout.addWidget(indicator)
        indicator.id=self.IDincr
        self.IDincr=+1
    
    def addIndicator_WithLess(self,entity,attribut,value,indicatorName,color=Qt.black):
        method='nbWithLess'
        indicator=SGIndicators(self,self.y,indicatorName,method,attribut,value,entity,color)
        self.indicatorNames.append(indicator.name)
        self.indicators.append(indicator)
        self.layout.addWidget(indicator)
        indicator.id=self.IDincr
        self.IDincr=+1

    def addIndicator_WithMore(self,entity,attribut,value,indicatorName,color=Qt.black):
        method='nbWithMore'
        indicator=SGIndicators(self,self.y,indicatorName,method,attribut,value,entity,color)
        self.indicatorNames.append(indicator.name)
        self.indicators.append(indicator)
        self.layout.addWidget(indicator)
        indicator.id=self.IDincr
        self.IDincr=+1

    def addIndicator_Nb(self,entity,attribut,value,indicatorName,color=Qt.black):
        method='nb'
        indicator=SGIndicators(self,self.y,indicatorName,method,attribut,value,entity,color)
        self.indicatorNames.append(indicator.name)
        self.indicators.append(indicator)
        self.layout.addWidget(indicator)
        indicator.id=self.IDincr
        self.IDincr=+1
    

    #Functions to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        return 70+len(self.getLongest())*5+50
        
    def getSizeYGlobal(self):
        somme=30
        return somme+len(self.indicatorNames)
    
    def getLongest(self):
        print(self.indicatorNames)
        longestWord="bonjourjesuistreslong"
        """for indicator in self.indicatorNames :
            if len(indicator)>len(longestWord):
                longestWord=indicator"""
        return longestWord
