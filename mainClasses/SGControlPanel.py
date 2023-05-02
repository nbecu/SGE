from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null, true

from SGGameSpace import SGGameSpace
from SGControlPanelItem import SGControlPanelItem

#Class who is responsible of the Legend creation 
class SGControlPanel(SGGameSpace):
    def __init__(self,parent,player,borderColor=Qt.black,backgroundColor=Qt.transparent,layout="vertical"):
        super().__init__(parent,0,60,0,0,true,backgroundColor)
        self.model=parent
        self.player=player
        self.id=self.player.name+'ControlPanel'
        self.actionfromPlayer=self.getActions()
        
        self.actionItems=[]
        self.actionItemsNames=[]
        self.IDincr=0
        self.y=0

        self.controlPanelItems={}
        self.borderColor=borderColor
        
        if layout=='vertical':
            self.layout=QtWidgets.QVBoxLayout()
        elif layout=='horizontal':
            self.layout=QtWidgets.QHBoxLayout()


    #Funtion to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        return 70+len(self.getLongest())*5+150
    
    def getLongest(self):
        longestWord=""
        for key in self.controlPanelItems :
            for element in self.controlPanelItems[key] :
                if len(element.texte)>len(longestWord):
                    longestWord=element.texte
        return longestWord
    
    def getSizeYGlobal(self):
        somme=100
        for key in self.controlPanelItems :
            somme= somme+ 27*len(self.controlPanelItems[key])
        return somme
    
    def display(self):
        layout = self.layout
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if isinstance(item, (QtWidgets.QSpacerItem, QtWidgets.QWidgetItem, QtWidgets.QHBoxLayout)):
                layout.removeItem(item)
                del item
        title=QtWidgets.QLabel(self.id)
        font = QFont()
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        layout.addSpacing(10)
        self.addActionItems()
        if self.actionItems is not None:
            for action in self.actionItems :
                layout.addLayout(action.actionItemLayout)
                layout.addSpacing(10)
            self.setLayout(layout)

    def getActions(self):
        return self.player.gameActions
    

    
    def addActionItems(self):
        for action in self.actionfromPlayer:
            self.y=self.y+1
            actionItem=SGControlPanelItem(self,action.anObject.format,self.y,"Test pouet1")
            self.actionItemsNames.append(actionItem.texte)
            self.actionItems.append(actionItem)
            actionItem.id=self.IDincr
            self.IDincr=+1

    def updateActionItem(self,item):
        theIndex=None
        for index, objet in enumerate(self.actionItems):
            if objet==item:
                theIndex=index
                break
        if theIndex is not None:
            newItem=SGControlPanelItem(self)
            self.actionItems[theIndex]=newItem
            self.actionItemsNames[theIndex]=newItem.texte
            newItem.id=item.id
    
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

    #To handle the selection of an element int the control panel
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            #Already selected
            if self.player.model.selected[0]==self :
                self.player.model.selected=[None]

            #Selection of an item and suppresion of already selected Item
            else :
                if isinstance(self.id,int):
                    self.player.model.selected=[None]
                    selectedItem=[self]
                    selectedItem.append(self.type) 
                    selectedItem.append(self.texte)
                    if self.texte.find('Remove ')!=-1 :
                        txt=self.texte.replace("Remove ","")
                        txt=txt.replace(self.valueOfAttribut+" ","")
                        selectedItem.append(txt)
                        selectedItem.append(self.valueOfAttribut)
                    else: 
                        selectedItem.append(self.valueOfAttribut)
                        selectedItem.append(self.nameOfAttribut)
                    selectedItem.append(self.texte[0:self.texte.find(self.nameOfAttribut)-1])
                    self.player.model.selected=selectedItem
                    self.player.model.update()
        self.update()
        
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
    

    



        
                    
