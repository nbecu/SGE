
from PyQt5 import QtWidgets
from PyQt5.QtSvg import * 
from PyQt5.QtGui import *
from PyQt5.QtCore import *


            
class SGLegend(QtWidgets.QWidget):
    def __init__(self,legendItems,sizeOfWord):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout() 
        self.setContentsMargins(25, 5, 25, 5)
        self.legendItems=legendItems
        self.sizeOfLongestWord=sizeOfWord
        self.intiAllLegendItems()
        self.setLayout(self.layout)
        
    
    #Drawing all the legend Item of the legend
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        """painter.setBrush(QBrush(Qt.gray, Qt.SolidPattern))"""
        painter.setPen(QPen(Qt.black,  1, Qt.SolidLine))
        painter.drawRect(40, 40, self.sizeOfLongestWord+15*2+60, len(self.legendItems)*20+25*2)
        painter.end()
        
    #Adding all legend Item into the legend 
    def intiAllLegendItems(self):
       for aLegenditem in self.legendItems:
           self.layout.addWidget(aLegenditem)