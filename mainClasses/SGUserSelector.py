from PyQt5.QtWidgets import QCheckBox, QHBoxLayout, QLabel
from mainClasses.SGGameSpace import SGGameSpace
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true


class SGUserSelector(SGGameSpace):
    def __init__(self, parent, users):
        super().__init__(parent, 0, 60, 0, 0, true)
        self.model = parent
        self.users = users
        self.id = 'userSelector'
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        self.checkboxes = []
        title = QLabel("User Selector")
        font = QFont()
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        self.updateUI(layout)
        self.setLayout(layout)

    def updateUI(self, layout):
        for user in self.users:
            checkbox = QCheckBox(user, self)
            checkbox.stateChanged.connect(self.checkboxChecked)
            self.checkboxes.append(checkbox)
            layout.addWidget(checkbox)
            layout.addSpacing(5)
        for checkbox in self.checkboxes:
                if checkbox.text() !="Admin":
                    checkbox.setEnabled(False)
                    checkbox.setChecked(False)
    
    def updateOnNewPhase(self):
        players=self.getAuthorizedPlayers()
        alreadyChecked=False
        for checkbox in self.checkboxes:
            if checkbox.text() not in [aPlayer.name for aPlayer in players]:
                checkbox.setEnabled(False)
                checkbox.setChecked(False)
            else:
                checkbox.setEnabled(True)
                if not alreadyChecked:
                    checkbox.setChecked(True)
                    alreadyChecked=True
            
    def setCheckboxesWithSelection(self, aUserName):
        for checkbox in self.checkboxes:
            checkbox.setChecked(checkbox.text() == aUserName)


    def checkboxChecked(self, state):
        sender = self.sender()
        if state == 2:
            for checkbox in self.checkboxes:
                if checkbox is not sender:
                    checkbox.setChecked(False)
                else:
                    self.model.setCurrentPlayer(checkbox.text())

        selectedCheckboxText = sender.text() if sender.isChecked() else None

        self.model.setCurrentPlayer(selectedCheckboxText)
        self.model.update()

    def getAuthorizedPlayers(self):
        if self.model.timeManager.isInitialization():
            return self.model.users
        phase = self.model.timeManager.phases[self.model.phaseNumber()-1]
        authorizedPlayers = phase.authorizedPlayers
        return authorizedPlayers

    # Funtion to have the global size of a gameSpace
    def getSizeXGlobal(self):
        return 350

    def getSizeYGlobal(self):
        somme = 50
        return somme

    # Drawing the US
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QBrush(self.backgroundColor, Qt.SolidPattern))
        # Draw the corner of the US
        self.setMinimumSize(self.getSizeXGlobal()+15, self.getSizeYGlobal()+10)
        painter.drawRect(0, 0, self.getSizeXGlobal(), self.getSizeYGlobal())

        painter.end()
