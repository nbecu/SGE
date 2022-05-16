from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *


   
#Class who is responsible of the declaration a cell
class SGLegendItem(QtWidgets.QWidget):
    def __init__(self,parent,type,y,texte="",color=Qt.black):
        super().__init__(parent)
        #Basic initialize
        self.parent=parent
        self.type=type
        self.texte=texte
        self.y=y
        self.color=color
        
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(self.color, Qt.SolidPattern))
        if self.parent.parent.selected[0] == self :
            painter.setPen(QPen(Qt.red,2));
        if(self.type=="square") :   
            painter.drawRect(10, 0, 20, 20)
        else:
            points = QPolygon([
               QPoint(20,  0),
               QPoint(30,  7),
               QPoint(30,  14),
               QPoint(20, 20),
               QPoint(10, 14),
               QPoint(10,  7)
            ])
            painter.drawPolygon(points)
        painter.drawText(QRect(40,5,150,15), Qt.AlignLeft, self.texte)
        self.setMinimumSize(200,200)
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
                self.parent.parent.selected=[None]
                selectedItem=[self]
                selectedItem.append(self.type)
                selectedItem.append(self.texte)
                self.parent.parent.selected=selectedItem
                self.parent.update()
        self.update()

        
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
    

        
    
        
    