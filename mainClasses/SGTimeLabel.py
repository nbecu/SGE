from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true

from mainClasses.SGGameSpace import SGGameSpace


# Class who is responsible of the Legend creation
class SGTimeLabel(SGGameSpace):
    def __init__(self, parent, title, backgroundColor=Qt.darkGray, borderColor=Qt.black, textColor=Qt.red):
        super().__init__(parent, 0, 60, 0, 0, true, backgroundColor)
        self.id = title
        self.timeManager = parent.timeManager
        self.borderColor = borderColor
        self.textColor = textColor
        self.y = 0
        self.labels = 0
        self.moveable = True
        self.displayPhaseNumber = False
        self.displayPhaseName = False
        self.displayRoundNumber = True
        self.displayTitle = True
        self.initUI()

    def initUI(self):

        # Créer deux labels
        self.labelTitle = QtWidgets.QLabel(self)
        self.label1 = QtWidgets.QLabel(self)
        self.label2 = QtWidgets.QLabel(self)
        self.label3 = QtWidgets.QLabel(self)

        if self.id is not None:
            self.labelTitle.setText(self.id)
        self.label1.setText('Round Number: Not started')
        self.label2.setText('Phase Number: Not started')
        currentPhase = self.timeManager.phases[int(
            self.timeManager.currentPhase)-1]
        self.label3.setText(currentPhase.name)

        color = QColor(self.textColor)
        color_string = f"color: {color.name()};"
        self.labelTitle.setStyleSheet(color_string)
        self.label1.setStyleSheet(color_string)
        self.label2.setStyleSheet(color_string)
        self.label3.setStyleSheet(color_string)

        self.labels = ['IN-GAME TIME', 'Round number: 0',
                       'Phase number: 0', 'Phase name']

        self.label1.setFixedHeight(
            self.label1.fontMetrics().boundingRect(self.label1.text()).height())
        self.label1.setFixedWidth(
            self.label1.fontMetrics().boundingRect(self.label1.text()).width())

        self.label2.setFixedHeight(
            self.label2.fontMetrics().boundingRect(self.label2.text()).height())
        self.label2.setFixedWidth(
            self.label2.fontMetrics().boundingRect(self.label2.text()).width())

        self.label3.setFixedHeight(
            self.label3.fontMetrics().boundingRect(self.label3.text()).height())
        self.label3.setFixedWidth(
            self.label3.fontMetrics().boundingRect(self.label3.text()).width())

        self.labelTitle.setFixedHeight(
            self.labelTitle.fontMetrics().boundingRect(self.labelTitle.text()).height())
        self.labelTitle.setFixedWidth(
            self.labelTitle.fontMetrics().boundingRect(self.labelTitle.text()).width())

        # Créer un layout vertical
        layout = QtWidgets.QVBoxLayout()

        # Ajouter les widgets au layout avec un espace de 10 pixels entre eux
        layout.addWidget(self.labelTitle)
        layout.addSpacing(10000)
        layout.addWidget(self.label1)
        layout.addSpacing(10000)
        layout.addWidget(self.label2)
        layout.addSpacing(10000)
        layout.addWidget(self.label3)

        # Définir le layout pour le widget
        self.setLayout(layout)
        self.displayUpdate()
        self.show()

    # Function to have the global size of a gameSpace
    def getSizeXGlobal(self):
        return 70+len(self.getLongest())*5

    def getLongest(self):
        longest_word = ''
        for word in self.labels:
            if len(word) > len(longest_word):
                longest_word = word
        return longest_word

    def getSizeYGlobal(self):
        somme = 30
        for word in self.labels:
            somme = somme + 2*len(word)
        return somme

    def paintEvent(self, event):
        if len(self.labels) != 0:
            painter = QPainter()
            painter.begin(self)
            painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
            painter.setPen(QPen(self.borderColor, 1))
            # Draw the corner of the Legend
            self.setMinimumSize(self.getSizeXGlobal()+3,
                                self.getSizeYGlobal()+3)
            painter.drawRect(0, 0, self.getSizeXGlobal(),
                             self.getSizeYGlobal())

            painter.end()

    def updateTimeLabel(self):
        self.label1.setText('Round Number : {}'.format(
            self.timeManager.currentRound))
        self.label2.setText('Phase Number : {}'.format(
            self.timeManager.currentPhase))
        currentPhase = self.timeManager.phases[int(
            self.timeManager.currentPhase)]
        self.label3.setText(currentPhase.name)

        self.label1.setFixedHeight(
            self.label1.fontMetrics().boundingRect(self.label1.text()).height())
        self.label1.setFixedWidth(
            self.label1.fontMetrics().boundingRect(self.label1.text()).width())

        self.label2.setFixedHeight(
            self.label2.fontMetrics().boundingRect(self.label2.text()).height())
        self.label2.setFixedWidth(
            self.label2.fontMetrics().boundingRect(self.label2.text()).width())

        self.label3.setFixedHeight(
            self.label3.fontMetrics().boundingRect(self.label3.text()).height())
        self.label3.setFixedWidth(
            self.label3.fontMetrics().boundingRect(self.label3.text()).width())

    def displayUpdate(self):
        if len(self.model.timeManager.phases) > 2:
            self.displayPhaseName = True
            self.displayPhaseNumber = True
        self.label3.setVisible(self.displayPhaseName)
        self.label2.setVisible(self.displayPhaseNumber)
        self.label1.setVisible(self.displayRoundNumber)
        self.labelTitle.setVisible(self.displayTitle)

    # To handle the drag of the widget

    def mouseMoveEvent(self, e):

        if self.moveable == False:
            return
        if e.buttons() != Qt.LeftButton:
            return

        mimeData = QMimeData()
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.pos())
        drag.exec_(Qt.MoveAction)
