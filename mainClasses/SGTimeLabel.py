from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null, true

from SGGameSpace import SGGameSpace
from SGTimeManager import SGTimeManager
from SGTimePhase import SGTimePhase
from SGGrid import SGGrid

#Class who is responsible of the Legend creation 
class SGTimeLabel(SGGameSpace):
    def __init__(self,parent,name,borderColor=Qt.black,backgroundColor=Qt.darkGray):
        super().__init__(parent,0,60,0,0,true,backgroundColor)
        self.id=name
        self.parent=parent
        self.borderColor=borderColor
        self.y=0
        self.round=0
        self.phase=0
        self.listOfLabels=0
        self.moveable=True
        self.initUI()
        

    def initUI(self):
        
        # Créer deux labels
        self.labelTitle = QtWidgets.QLabel(self)
        self.label1 = QtWidgets.QLabel(self)
        self.label2 = QtWidgets.QLabel(self)
        

        self.labelTitle.setText('IN-GAME TIME')
        self.label1.setText('Round Number: 1')
        self.label2.setText('Phase Number: 1')

        self.listOfLabels=['IN-GAME TIME','Round number: 0','Phase number: 0']

        self.label1.setFixedHeight(self.label1.fontMetrics().boundingRect(self.label1.text()).height())
        self.label1.setFixedWidth(self.label1.fontMetrics().boundingRect(self.label1.text()).width())

        self.label2.setFixedHeight(self.label2.fontMetrics().boundingRect(self.label2.text()).height())
        self.label2.setFixedWidth(self.label2.fontMetrics().boundingRect(self.label2.text()).width())

        self.labelTitle.setFixedHeight(self.labelTitle.fontMetrics().boundingRect(self.labelTitle.text()).height())
        self.labelTitle.setFixedWidth(self.labelTitle.fontMetrics().boundingRect(self.labelTitle.text()).width())

        # Créer un layout vertical
        layout = QtWidgets.QVBoxLayout()

        # Ajouter les widgets au layout avec un espace de 10 pixels entre eux
        layout.addWidget(self.labelTitle)
        layout.addSpacing(10000)
        layout.addWidget(self.label1)
        layout.addSpacing(10000)
        layout.addWidget(self.label2)

        # Définir le layout pour le widget
        self.setLayout(layout)
        self.show()
#Funtion to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        return 70+len(self.getLongest())*5
    
    def getLongest(self):
        longest_word = ''
        for word in self.listOfLabels:
            if len(word) > len(longest_word):
                longest_word = word
        return longest_word
    
    def getSizeYGlobal(self):
        somme=30
        for word in self.listOfLabels :
            somme= somme+ 2*len(word)
        return somme
    
    def paintEvent(self,event):
        if len(self.listOfLabels)!=0:
            painter = QPainter() 
            painter.begin(self)
            painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
            painter.setPen(QPen(self.borderColor,1));
            #Draw the corner of the Legend
            self.setMinimumSize(self.getSizeXGlobal()+3, self.getSizeYGlobal()+3)
            painter.drawRect(0,0,self.getSizeXGlobal(), self.getSizeYGlobal())     


            painter.end()
        
    def updateTimeLabel(self,actualRound,actualPhase):
        self.label1.setText('Round Number : {}'.format(actualRound))
        self.label2.setText('Phase Number : {}'.format(actualPhase))

        self.label1.setFixedHeight(self.label1.fontMetrics().boundingRect(self.label1.text()).height())
        self.label1.setFixedWidth(self.label1.fontMetrics().boundingRect(self.label1.text()).width())

        self.label2.setFixedHeight(self.label2.fontMetrics().boundingRect(self.label2.text()).height())
        self.label2.setFixedWidth(self.label2.fontMetrics().boundingRect(self.label2.text()).width())


    #To handle the drag of the grid
    def mouseMoveEvent(self, e):

        if self.moveable==False:
            return
        if e.buttons() != Qt.LeftButton:
            return
        
        mimeData = QMimeData()
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.pos())
        drag.exec_(Qt.MoveAction)