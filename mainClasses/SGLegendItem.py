from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null


   
#Class who is responsible of creation legend item 
class SGLegendItem(QtWidgets.QWidget):
    def __init__(self,parent,type,text,classDefOrShape=None,color=Qt.black,nameOfAttribut="",valueOfAttribut="",border=False,gameAction=None):
        super().__init__(parent)
        #Basic initialize
        self.legend=parent
        self.type=type
        self.posY=self.legend.posYOfItems
        self.legend.posYOfItems +=1
        self.text=str(text)
        if classDefOrShape == 'square' or classDefOrShape is None:
            self.shape= classDefOrShape
        else:
            self.classDef=classDefOrShape
            self.shape=self.classDef.shape
        self.color=color
        self.nameOfAttribut=nameOfAttribut
        self.valueOfAttribut=valueOfAttribut
        self.border=border
        self.remainNumber=int
        self.gameAction= gameAction
        self.initUI()

    
    def initUI(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)

    # To show a menu
    def show_menu(self, point):
        if self.gameAction is None: return
        menu = QMenu(self)
        # number=self.updateRemainNumber()
        number=self.gameAction.getNbRemainingActions()
        text= "Actions remaining : "+str(number)
        option1 = QAction(text, self)
        menu.addAction(option1)
        if self.rect().contains(point) and number is not None:
            menu.exec_(self.mapToGlobal(point))
        
    
    def updateRemainNumber(self): # A priori OBSOLETE
        thePlayer=self.legend.model.getPlayerObject(self.legend.playerName)
        self.crossAction(thePlayer)
        return self.remainNumber

    def isSelectable(self):
        #Title1 and Title2 items are not selectable
        return False if self.type in ['Title1','Title2'] else True
    
    def isValueOnCell(self):
        return self.type == 'symbol' and self.classDef.entityType() == 'Cell'#self.shape in ["square","hexagonal"]

    def isValueOnAgent(self):
        return self.type == 'symbol' and self.classDef.entityType() =='Agent' # in ("circleAgent","squareAgent", "ellipseAgent1","ellipseAgent2", "rectAgent1","rectAgent2", "triangleAgent1","triangleAgent2", "arrowAgent1","arrowAgent2")

    #Drawing function
    def paintEvent(self,event):
        if self.legend.checkDisplay():
            painter = QPainter() 
            painter.begin(self)
            painter.setBrush(QBrush(self.color, Qt.SolidPattern))
            if self.legend.selected == self :
                painter.setPen(QPen(Qt.red,2));
            if self.border:
                painter.setPen(QPen(self.color,2))
                painter.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))
            #Square cell
            if(self.shape=="square") :   
                painter.drawRect(10, 0, 20, 20)
            #agent
            elif self.shape=="circleAgent":
                painter.drawEllipse(10, 0, 20, 20)
            elif self.shape=="squareAgent":
                painter.drawRect(10, 0, 20, 20)
            elif self.shape=="ellipseAgent1":
                painter.drawEllipse(10, 5, 20, 10)
            elif self.shape=="ellipseAgent2":
                painter.drawEllipse(15, 0, 10, 20)
            elif self.shape=="rectAgent1":
                painter.drawRect(10, 5, 20, 10)
            elif self.shape=="rectAgent2":
                painter.drawRect(15, 0, 10, 20)
            elif self.shape=="triangleAgent1": 
                points = QPolygon([
                QPoint(20,7),
                QPoint(15,17),
                QPoint(25,17)
                ])
                painter.drawPolygon(points)
            elif self.shape=="triangleAgent2": 
                points = QPolygon([           
                QPoint(25,7),
                QPoint(15,7),
                QPoint(20,17)
                ])
                painter.drawPolygon(points)
            elif self.shape=="arrowAgent1": 
                points = QPolygon([
                QPoint(20,7),
                QPoint(15,17),
                QPoint(20,14),
                QPoint(25,17)
                ])
                painter.drawPolygon(points)
            elif self.shape=="arrowAgent2": 
                points = QPolygon([           
                QPoint(25,7),
                QPoint(20,10),
                QPoint(15,7),
                QPoint(20,17)
                ])
                painter.drawPolygon(points)
            #Hexagonal square
            elif self.shape=="hexagonal":
                points = QPolygon([
                QPoint(20,  0),
                QPoint(30,  7),
                QPoint(30,  14),
                QPoint(20, 20),
                QPoint(10, 14),
                QPoint(10,  7)
                ])
                painter.drawPolygon(points)
            
            if self.type =="None":
                aFont=QFont("Verdana",10)
                aFont.setUnderline(True)
                painter.setFont(aFont)
                painter.drawText(QRect(15,0,self.legend.getSizeXGlobal()-50,20), Qt.AlignLeft, self.text)
            elif self.type =="Title1":
                aFont=QFont("Verdana",10)
                aFont.setUnderline(True)
                painter.setFont(aFont)
                painter.drawText(QRect(15,0,self.legend.getSizeXGlobal()-50,20), Qt.AlignLeft, self.text)
            elif self.type =="Title2":
                aFont=QFont("Verdana",10)
                painter.setFont(aFont)
                painter.drawText(QRect(10,0,self.legend.getSizeXGlobal()-50,20), Qt.AlignLeft, self.text)
            elif self.type =='delete':
                painter.setFont(QFont("Verdana",10))
                painter.drawText(QRect(40,3,self.legend.getSizeXGlobal()-50,20), Qt.AlignLeft, self.text)
            else :
                painter.setFont(QFont("Verdana",8))
                painter.drawText(QRect(40,3,self.legend.getSizeXGlobal()-50,20), Qt.AlignLeft, self.text)
            self.setMinimumSize(self.legend.getSizeXGlobal()-50,10)
            self.move(10,self.posY*25)#25
            painter.end()
            
    
    #Funtion to handle the zoom
    def zoomIn(self):
        self.size=self.parent.size
        self.gap=self.parent.gap
        self.update()
    
    def zoomOut(self):
        self.size=self.parent.size
        self.gap=self.parent.gap
        self.update()
        
    def zoomFit(self):
        self.size=self.parent.size
        self.gap=self.parent.gap
        self.update()
        
    #To handle the selection of an element int the legend
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            if self.legend.playerName!=self.legend.model.currentPlayer:
                return #Exit because the currentPlayer cannot use this widget
            if not self.isSelectable():
                return #Exit because the currentPlayer cannot use this widget
            if self.legend.selected==self:
            #Already selected
                self.legend.selected=None
            #Selection of an item and suppresion of already selected Item
            else :
                self.legend.selected= self
                # self.legend.model.selected=[None]
                # selectedItem=[self]
                # selectedItem.append(self.type) 
                # selectedItem.append(self.text)
                # if self.text.find('Remove ')!=-1 :
                #     txt=self.text.replace("Remove ","")
                #     txt=txt.replace(self.valueOfAttribut+" ","")
                #     selectedItem.append(txt)
                #     selectedItem.append(self.valueOfAttribut)
                # else: 
                #     selectedItem.append(self.valueOfAttribut)
                #     selectedItem.append(self.nameOfAttribut)
                # #selectedItem.append(self.text[0:self.text.find(self.nameOfAttribut)-1])
                # self.legend.model.selected=selectedItem
                # self.legend.model.update()
            self.legend.update()
        
    #To handle the drag 
    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.LeftButton:
            return
    
    #To test is it from the admin Legend
    def isFromAdmin(self):
        return self.legend.id=="adminLegend"
    
    def crossAction(self,thePlayer): # A priori OBSOLETE
        if thePlayer!="Admin":
            self.clickable=True
            for actionText in thePlayer.remainActions.keys():
                if actionText.find(self.text)!=-1:
                    self.remainNumber=thePlayer.remainActions[actionText]
                    break
        else:
            self.clickable=False




                    

        
    
        
    