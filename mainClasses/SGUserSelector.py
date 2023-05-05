from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QHBoxLayout, QLabel
from SGGameSpace import SGGameSpace
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null, true

class SGUserSelector(SGGameSpace):
    def __init__(self,parent,users):
        super().__init__(parent,0,60,0,0,true)
        self.model=parent
        self.users = users
        self.id='userSelector'
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        self.checkboxes = []
        title = QLabel("User Selector")
        layout.addWidget(title)


        for user in self.users:
            checkbox = QCheckBox(user, self)
            if user == self.model.currentPlayer:
                checkbox.setChecked(True)
                #self.previousChecked = checkbox
            checkbox.stateChanged.connect(self.checkstate)
            self.checkboxes.append(checkbox)
            layout.addWidget(checkbox)
            layout.addSpacing(5)

        self.setLayout(layout)

    def checkstate(self, state):
        sender = self.sender()
        if state == 2:
            for checkbox in self.checkboxes:
                if checkbox is not sender:
                    checkbox.setChecked(False)
                else:
                    self.model.currentPlayer = checkbox.text()
        self.model.update()
        print(self.model.currentPlayer)

    def mouseMoveEvent(self, e):
    
        if e.buttons() != Qt.LeftButton:
            return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())

        drag.exec_(Qt.MoveAction)

    #Funtion to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        return 300
    
    def getSizeYGlobal(self):
        somme=50
        return somme
    
    #Drawing the US
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
        #Draw the corner of the US
        self.setMinimumSize(self.getSizeXGlobal()+10, self.getSizeYGlobal()+10)
        painter.drawRect(0,0,self.getSizeXGlobal(), self.getSizeYGlobal())     


        painter.end()
            