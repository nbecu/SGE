from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox
from SGGameSpace import SGGameSpace
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null, true

class UserSelector(SGGameSpace):
    def __init__(self,parent, users):
        super().__init__()
        self.model=parent
        self.users = users
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        for user in self.user_list:
            checkbox = QCheckBox(user, self)
            layout.addWidget(checkbox)

        self.setLayout(layout)

    def mouseMoveEvent(self, e):
    
        if e.buttons() != Qt.LeftButton:
            return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())

        drag.exec_(Qt.MoveAction)