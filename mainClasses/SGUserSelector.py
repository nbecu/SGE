from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QHBoxLayout, QLabel
from mainClasses.SGGameSpace import SGGameSpace
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null, true


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
        layout.addWidget(title)
        self.updateUI(layout)
        self.setLayout(layout)

    def updateUI(self, layout):
        for user in self.users:
            checkbox = QCheckBox(user, self)
            if user == self.model.currentPlayer:
                checkbox.setChecked(True)
                # self.previousChecked = checkbox
            authorizedPlayers = self.getAuthorizedPlayers()
            if user not in authorizedPlayers:
                checkbox.setEnabled(False)
            checkbox.stateChanged.connect(self.checkboxChecked)
            for aCheckbox in self.checkboxes:
                if checkbox.text() == aCheckbox.text():
                    return
            self.checkboxes.append(checkbox)
            layout.addWidget(checkbox)
            layout.addSpacing(5)
    
    def setCheckboxesWithSelection(self, aUserName):
        for checkbox in self.checkboxes:
            checkbox.setChecked(checkbox.text() == aUserName)


    def checkboxChecked(self, state):
        sender = self.sender()
        if state == 2: #C'est quoi le state ?
            for checkbox in self.checkboxes:
                if checkbox is not sender:
                    checkbox.setChecked(False)
                else:
                    self.model.setCurrentPlayer(checkbox.text())

        selectedCheckboxText = sender.text() if sender.isChecked() else None

        self.model.setCurrentPlayer(selectedCheckboxText)
        self.model.update() # Pas sur qu'on ai besoin de ce update()

    def getAuthorizedPlayers(self):
        if self.model.timeManager.isInitialization():
            return self.model.users
        phase = self.model.timeManager.phases[self.model.getCurrentPhase()-1]
        authorizedPlayers = phase.authorizedPlayers
        # authorizedPlayers = []
        # for player in players:
        #     if player == 'Admin':
        #         authorizedPlayers.append('Admin')
        #     else:
        #         authorizedPlayers.append(player.name)
        return authorizedPlayers

    # Funtion to have the global size of a gameSpace
    def getSizeXGlobal(self):
        return 300

    def getSizeYGlobal(self):
        somme = 50
        return somme

    # Drawing the US
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
        # Draw the corner of the US
        self.setMinimumSize(self.getSizeXGlobal()+10, self.getSizeYGlobal()+10)
        painter.drawRect(0, 0, self.getSizeXGlobal(), self.getSizeYGlobal())

        painter.end()
