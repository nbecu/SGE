from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null


   
#Class who is responsible of creation legend item 
class SGLegendItem(QtWidgets.QWidget):
    def __init__(self,parent,type,y,texte="",color=Qt.black,valueOfAttribut="",nameOfAttribut=""):
        super().__init__(parent)
        #Basic initialize
        self.parent=parent
        self.type=type
        self.valueOfAttribut=valueOfAttribut
        self.nameOfAttribut=nameOfAttribut
        self.texte=texte
        self.y=y
        self.color=color
        
    #Drawing function
    def paintEvent(self,event):
        if self.parent.checkDisplay():
            painter = QPainter() 
            painter.begin(self)
            painter.setBrush(QBrush(self.color, Qt.SolidPattern))
            if self.parent.parent.selected[0] == self :
                painter.setPen(QPen(Qt.red,2));
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
                painter.drawText(QRect(15,0,self.parent.getSizeXGlobal()-50,20), Qt.AlignLeft, self.texte)
            else :
                painter.setFont(QFont("Verdana",8))
                painter.drawText(QRect(40,5,self.parent.getSizeXGlobal()-50,15), Qt.AlignLeft, self.texte)
            self.setMinimumSize(self.parent.getSizeXGlobal()-50,10)
            self.move(10,self.y*20+5*self.y)
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
            #Already selected
            if self.parent.parent.selected[0]==self :
                self.parent.parent.selected=[None]

            #Selection of an item and suppresion of already selected Item
            else :
                if self.type!="None":
                    self.parent.parent.selected=[None]
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
                    self.parent.parent.selected=selectedItem
                    self.parent.parent.update()
        self.update()
        
    #To handle the drag of the grid
    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.LeftButton:
            return
    
    #To test is it from the admin Legend
    def isFromAdmin(self):
        return self.parent.id=="adminLegend"
                    

        
    
        
    