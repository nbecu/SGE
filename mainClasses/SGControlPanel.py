from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null, true

from SGGameSpace import SGGameSpace
from SGControlPanelItem import SGControlPanelItem

#Class who is responsible of the Legend creation 
class SGControlPanel(SGGameSpace):
    def __init__(self,parent,player,actionItems,borderColor=Qt.black,backgroundColor=Qt.transparent,layout="vertical"):
        super().__init__(parent,0,60,0,0,true,backgroundColor)
        self.model=parent
        self.actionItems=actionItems
        self.player=player
        self.controlPanelItems={}
        self.borderColor=borderColor
        self.y=0
        self.id=self.player.name+'ControlPanel'
        if layout=='vertical':
            self.layout=QtWidgets.QVBoxLayout()
        elif layout=='horizontal':
            self.layout=QtWidgets.QHBoxLayout()
        self.initUI()

    # CURRENT VERSION
    def initUI(self):
        self.y=0
        layout=self.layout
        self.y=self.y+1
        title=QtWidgets.QLabel(self.player.name+' :')
        layout.addWidget(title)
    
    #Funtion to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        return 70+len(self.getLongest())*5+50
    
    def getLongest(self):
        longestWord=""
        for key in self.controlPanelItems :
            for element in self.controlPanelItems[key] :
                if len(element.texte)>len(longestWord):
                    longestWord=element.texte
        return longestWord
    
    def getSizeYGlobal(self):
        somme=30
        for key in self.controlPanelItems :
            somme= somme+ 27*len(self.controlPanelItems[key])
        return somme
    
    def display(self):
        if self.actionItems is not None:
            for action in self.actionItems :
                if action in list(self.controlPanelItems.keys()):
                    if len(self.controlPanelItems[action]) !=0:
                        for anElement in reversed(range(len(self.controlPanelItems[action]))):
                            self.controlPanelItems[action][anElement].deleteLater()
                            del self.controlPanelItems[action][anElement]
                self.controlPanelItems[action]=[]
            self.y=self.y+1
            anItem=SGControlPanelItem(self,"None",self.y,self.id)
            self.controlPanelItems["Title"]=[]
            self.controlPanelItems["Title"].append(anItem)
            anItem.show()
        self.setMinimumSize(self.getSizeXGlobal(),10)

    
    #To handle the drag of the Control Panel
    def mouseMoveEvent(self, e):
    
        if e.buttons() != Qt.LeftButton:
            return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())

        drag.exec_(Qt.MoveAction)
    
    
        
    #*Drawing the Control Panel
    def paintEvent(self,event):
        #if self.checkDisplay():
            #if len(self.actionItems)!=0:
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
        pen=QPen(Qt.black)
        pen.setWidth(1)
        painter.setPen(pen)
        #*Draw the corner of the Control Panel
        self.setMinimumSize(self.getSizeXGlobal()+3, self.getSizeYGlobal()+3)
        painter.drawRect(0,0,self.getSizeXGlobal(), self.getSizeYGlobal())     

        painter.end()

        
    #Check if it have to be displayed
    def checkDisplay(self):
        if self.player.name==self.model.whoIAm or self.model.whoIAm=='Admin':
            return True
        else:
            return False

    def setInactiveDisplay(self):
        return

    def setTitle(self,title):
        self.id=title   
    

    



        
                    
