from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null, true

from SGGameSpace import SGGameSpace
from SGIndicators import SGIndicators


#Class who is responsible of the Legend creation 
class SGDashBoard(SGGameSpace):
    def __init__(self,parent,title,displayRefresh='instantaneous',borderColor=Qt.black,backgroundColor=Qt.lightGray,layout="vertical"):
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
        self.initUI()

    def initUI(self):
        self.y=0
        layout=self.layout
        self.y=self.y+1
        title=QtWidgets.QLabel(self.id,self)
        layout.addWidget(title)
    
    def showIndicators(self):
        # Delete all
        layout = self.layout
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            layout.removeWidget(widget)
            widget.deleteLater()
        
        title = QtWidgets.QLabel(self.id, self)
        font = QFont()
        font.setBold(True)
        font.setPointSize(16)
        title.setFont(font)
        layout.addWidget(title)
        
        for indicator in self.indicators:
            self.y=self.y+1
            layout.addWidget(indicator)
            indicator.show()

            #Drawing the DB
    def paintEvent(self,event):
        if self.checkDisplay():
            if len(self.indicators)!=0:
                painter = QPainter() 
                painter.begin(self)
                painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
                painter.setPen(QPen(self.borderColor,1))
                #Draw the corner of the DB
                self.setMinimumSize(self.getSizeXGlobal()+10, self.getSizeYGlobal()+10)
                painter.drawRect(0,0,self.getSizeXGlobal(), self.getSizeYGlobal())     


                painter.end()
            

    def checkDisplay(self):
        if self.isDisplay:
            return True
        else:
            return False
        

    def addIndicator(self,method,entity,attribut,value=None,indicatorName=None,color=Qt.black):
        self.y=self.y+1
        indicator=SGIndicators(self,self.y,indicatorName,method,attribut,value,entity,color)
        self.indicatorNames.append(indicator.name)
        self.indicators.append(indicator)
        layout = self.layout
        layout.addWidget(indicator)
        indicator.id=self.IDincr
        self.IDincr=+1

    def addIndicator_Sum(self,entity,attribut,value,indicatorName,color=Qt.black):
        method='sumAtt'
        self.addIndicator(method,entity,attribut,value,indicatorName,color)
    
    def addIndicator_Avg(self,entity,attribut,value,indicatorName,color=Qt.black):
        method='avgAtt'
        self.addIndicator(method,entity,attribut,value,indicatorName,color)

    def addIndicator_Min(self,entity,attribut,value,indicatorName,color=Qt.black):
        method='minAtt'
        self.addIndicator(method,entity,attribut,value,indicatorName,color)

    def addIndicator_Max(self,entity,attribut,value,indicatorName,color=Qt.black):
        method='maxAtt'
        self.addIndicator(method,entity,attribut,value,indicatorName,color)
    
    def addIndicator_EqualTo(self,entity,attribut,value,indicatorName,color=Qt.black):
        method='nbEqualTo'
        self.addIndicator(method,entity,attribut,value,indicatorName,color)
    
    def addIndicator_WithLess(self,entity,attribut,value,indicatorName,color=Qt.black):
        method='nbWithLess'
        self.addIndicator(method,entity,attribut,value,indicatorName,color)

    def addIndicator_WithMore(self,entity,attribut,value,indicatorName,color=Qt.black):
        method='nbWithMore'
        self.addIndicator(method,entity,attribut,value,indicatorName,color)

    def addIndicator_Nb(self,entity,attribut,value,indicatorName,color=Qt.black):
        method='nb'
        self.addIndicator(method,entity,attribut,value,indicatorName,color)
    

    # *Functions to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        return 70+len(self.getLongest())*5+50
        
    def getSizeYGlobal(self):
        somme=30
        return somme+len(self.indicatorNames)
    
    def getLongest(self):
        #print(self.indicatorNames)
        longestWord=""
        for indicatorName in self.indicatorNames :
            if len(indicatorName)>len(longestWord):
                longestWord=indicatorName
        return longestWord

    def mouseMoveEvent(self, e):
    
        if e.buttons() != Qt.LeftButton:
            return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())

        drag.exec_(Qt.MoveAction)