from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null, true

from SGGameSpace import SGGameSpace
from SGIndicators import SGIndicators


#Class who is responsible of the Legend creation 
class SGDashBoard(SGGameSpace):
    def __init__(self,parent,title,displayRefresh='instantaneous',borderColor=Qt.black,backgroundColor=Qt.transparent):
        super().__init__(parent,0,60,0,0,true,backgroundColor)
        self.model=parent
        self.title=title
        self.indicators=[]
        self.borderColor=borderColor
        self.backgroundColor=backgroundColor
        self.y=0
        self.isDisplay=True
        self.displayRefresh=displayRefresh
        self.IDincr=0
        self.initUI()

    def initUI(self):
        self.y=0
        for indicator in self.indicators:
            self.y=+1
            indicator.show()
            


    def checkDisplay(self):
        if self.isDisplay:
            return True
        else:
            return False
        

    def addIndicator(self,indicatorName,method,attribut,value,entity='cell',color=Qt.black):
        indicator=SGIndicators(self,self.y,indicatorName,method,attribut,value,entity,color)
        self.indicators.append(indicator.name)
        indicator.id=self.IDincr
        self.IDincr=+1


    #Functions to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        return 70+len(self.getLongest())*5+50
        
    def getSizeYGlobal(self):
        somme=30
        return somme+len(self.indicators)
    
    def getLongest(self):
        longestWord=""
        for indicator in self.indicators :
            if len(indicator)>len(longestWord):
                longestWord=indicator
        return longestWord
