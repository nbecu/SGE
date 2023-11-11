from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null


   
#Class who is responsible of creation legend item 
class SGLegendItem(QtWidgets.QWidget):
    def __init__(self,parent,type,y,text="",color=Qt.black,valueOfAttribut="",nameOfAttribut="",border=False):
        super().__init__(parent)
        #Basic initialize
        self.legend=parent
        self.type=type
        self.valueOfAttribut=valueOfAttribut
        self.nameOfAttribut=nameOfAttribut
        self.text=text
        self.y=y
        self.color=color
        self.border=border
        self.remainNumber=int
        self.initUI()

    
    def initUI(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)

    # To show a menu
    def show_menu(self, point):
        menu = QMenu(self)
        number=self.updateRemainNumber()
        text= "Actions remaining : "+str(number)
        option1 = QAction(text, self)
        menu.addAction(option1)

        if self.rect().contains(point) and self.clickable:
            menu.exec_(self.mapToGlobal(point))
        
    
    def updateRemainNumber(self):
        thePlayer=self.legend.model.getPlayerObject(self.legend.playerName)
        self.crossAction(thePlayer)
        return self.remainNumber


    #Drawing function
    def paintEvent(self,event):
        if self.legend.checkDisplay():
            painter = QPainter() 
            painter.begin(self)
            painter.setBrush(QBrush(self.color, Qt.SolidPattern))
            if self.legend.model.selected[0] == self :
                painter.setPen(QPen(Qt.red,2));
            if self.border:
                painter.setPen(QPen(self.color,2))
                painter.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))
            #Square cell
            if(self.type=="square") :   
                painter.drawRect(10, 0, 20, 20)
            #agent
            elif self.type=="circleAgent":
                painter.drawEllipse(10, 0, 20, 20)
            elif self.type=="squareAgent":
                painter.drawRect(10, 0, 20, 20)
            elif self.type=="ellipseAgent1":
                painter.drawEllipse(10, 5, 20, 10)
            elif self.type=="ellipseAgent2":
                painter.drawEllipse(15, 0, 10, 20)
            elif self.type=="rectAgent1":
                painter.drawRect(10, 5, 20, 10)
            elif self.type=="rectAgent2":
                painter.drawRect(15, 0, 10, 20)
            elif self.type=="triangleAgent1": 
                points = QPolygon([
                QPoint(20,7),
                QPoint(15,17),
                QPoint(25,17)
                ])
                painter.drawPolygon(points)
            elif self.type=="triangleAgent2": 
                points = QPolygon([           
                QPoint(25,7),
                QPoint(15,7),
                QPoint(20,17)
                ])
                painter.drawPolygon(points)
            elif self.type=="arrowAgent1": 
                points = QPolygon([
                QPoint(20,7),
                QPoint(15,17),
                QPoint(20,14),
                QPoint(25,17)
                ])
                painter.drawPolygon(points)
            elif self.type=="arrowAgent2": 
                points = QPolygon([           
                QPoint(25,7),
                QPoint(20,10),
                QPoint(15,7),
                QPoint(20,17)
                ])
                painter.drawPolygon(points)
            #Hexagonal square
            elif self.type=="hexagonal":
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
                # aFont.setUnderline(True)
                painter.setFont(aFont)
                painter.drawText(QRect(10,0,self.legend.getSizeXGlobal()-50,20), Qt.AlignLeft, self.text)
            else :
                painter.setFont(QFont("Verdana",8))
                painter.drawText(QRect(40,3,self.legend.getSizeXGlobal()-50,20), Qt.AlignLeft, self.text)
            self.setMinimumSize(self.legend.getSizeXGlobal()-50,10)
            print ('y='+str(self.y) + ' '+self.type)
            self.move(10,self.y*25)#25
            painter.end()
            
    def getId(self):
        return "cell"+str(self.x)+str(self.y)
    

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
            if self.legend.playerName==self.legend.model.currentPlayer:
            #Already selected
                if self.legend.model.selected[0]==self :
                    self.legend.model.selected=[None]

                #Selection of an item and suppresion of already selected Item
                else :
                    if self.type!="None":
                        self.legend.model.selected=[None]
                        selectedItem=[self]
                        selectedItem.append(self.type) 
                        selectedItem.append(self.text)
                        if self.text.find('Remove ')!=-1 :
                            txt=self.text.replace("Remove ","")
                            txt=txt.replace(self.valueOfAttribut+" ","")
                            selectedItem.append(txt)
                            selectedItem.append(self.valueOfAttribut)
                        else: 
                            selectedItem.append(self.valueOfAttribut)
                            selectedItem.append(self.nameOfAttribut)
                        #selectedItem.append(self.text[0:self.text.find(self.nameOfAttribut)-1])
                        self.legend.model.selected=selectedItem
                        self.legend.model.update()
        self.update()
        
    #To handle the drag 
    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.LeftButton:
            return
    
    #To test is it from the admin Legend
    def isFromAdmin(self):
        return self.legend.id=="adminLegend"
    
    def crossAction(self,thePlayer):
        if thePlayer!="Admin":
            self.clickable=True
            for actionText in thePlayer.remainActions.keys():
                if actionText.find(self.text)!=-1:
                    self.remainNumber=thePlayer.remainActions[actionText]
                    break
        else:
            self.clickable=False




                    

        
    
        
    