from PyQt5 import QtWidgets
from PyQt5.QtSvg import * 
from PyQt5.QtGui import *
from PyQt5.QtCore import *


            
class SGLegendItem(QtWidgets.QWidget):
    def __init__(self,aColor,aText,aForm="cell"):
        super().__init__()
        self.color = aColor
        self.Text=aText
        self.Form=aForm
        
        
        
        
        
    #Drawing the legend Item
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(self.color, Qt.SolidPattern))
        painter.drawRect(10, 10, 20, 20)
        painter.drawText(QRect(40,15, 200,200), Qt.AlignLeft, self.Text)
        painter.end()
        
        