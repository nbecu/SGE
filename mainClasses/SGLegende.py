from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true

from SGGameSpace import SGGameSpace
from SGLegendItem import SGLegendItem
from mainClasses.SGCell import SGCell

#Class who is responsible of the grid creation
class SGLegende(SGGameSpace):
    def __init__(self,parent,name,elementPov,borderColor=Qt.black,backgroundColor=Qt.transparent):
        super().__init__(parent,0,60,0,0,true,backgroundColor)
        self.id=name
        self.parent=parent
        self.elementsPov=elementPov
        self.legendItemList={}
        self.borderColor=borderColor
        self.haveADeleteButton=False
        self.initUI()

        
    def initUI(self):
        y=0
        for aKeyOfGamespace in self.elementsPov :
            self.legendItemList[aKeyOfGamespace]=[]
            if self.parent.nameOfPov != "default":
                for element in self.elementsPov[aKeyOfGamespace][self.parent.nameOfPov]:
                    if aKeyOfGamespace=="deleteButton":
                        y=y+1
                        self.legendItemList[aKeyOfGamespace].append(SGLegendItem(self,"square",y,element,self.elementsPov[aKeyOfGamespace][self.parent.nameOfPov][element]))
                    else: 
                        for aValue in self.elementsPov[aKeyOfGamespace][self.parent.nameOfPov][element]:
                            y=y+1
                            self.legendItemList[aKeyOfGamespace].append(SGLegendItem(self,self.parent.getGameSpace(aKeyOfGamespace).format,y,element+" "+aValue,self.elementsPov[aKeyOfGamespace][self.parent.nameOfPov][element][aValue]))
    
    #Funtion to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        if self.haveADeleteButton :
            if len(self.getLongest()) > len("delete"):
                return 70+len(self.getLongest())*5
            else:
                return 70+len("delete")*5
        else :
            return 70+len(self.getLongest())*5
    
    def getLongest(self):
        longestWord=""
        for key in self.legendItemList :
            for element in self.legendItemList[key] :
                if len(element.texte)>len(longestWord):
                    longestWord=element.texte
        return longestWord
    
    def getSizeYGlobal(self):
        somme=30
        for key in self.legendItemList :
            somme= somme+ 27*len(self.legendItemList[key])
        return somme
    
    #Funtion to handle the zoom
    def zoomIn(self):
        return True
    
    def zoomOut(self):
        return True
    
    #To handle the drag of the legende
    def mouseMoveEvent(self, e):
    
        if e.buttons() != Qt.LeftButton:
            return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())

        drag.exec_(Qt.MoveAction)
    
    
        
    #Drawing the legende
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
        painter.setPen(QPen(self.borderColor,1));
        #Draw the corner of the legende
        self.setMinimumSize(self.getSizeXGlobal()+3, self.getSizeYGlobal()+3)
        painter.drawRect(0,0,self.getSizeXGlobal(), self.getSizeYGlobal())        
        painter.end()
        
    
    
        

#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

#To add Povs in a legend
    def addToTheLegende(self,aListOfElement):
        #For the grid value
        for aGameSpaceId in aListOfElement:
            for aPov in aListOfElement[aGameSpaceId]:
                for element in aListOfElement[aGameSpaceId][aPov] :
                    for value in aListOfElement[aGameSpaceId][aPov][element]:
                        self.elementsPov[aGameSpaceId][aPov][element][value]=aListOfElement[aGameSpaceId][aPov][element][value]
        self.initUI()
        
#Adding the delete Button
    def addDeleteButton(self):
        self.haveADeleteButton=True
        self.elementsPov["deleteButton"]={}
        for aGameSpaceId in self.elementsPov:
            for aPov in self.elementsPov[aGameSpaceId]:
                self.elementsPov["deleteButton"][aPov]={"delete":Qt.yellow}
        self.initUI()
        
        

        
                    
