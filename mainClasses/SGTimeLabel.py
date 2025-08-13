from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true

from mainClasses.SGGameSpace import SGGameSpace


class SGTimeLabel(SGGameSpace):
    def __init__(self, parent, title, backgroundColor=Qt.darkGray, borderColor=Qt.black, textColor=Qt.red):
        super().__init__(parent, 0, 60, 0, 0, true, backgroundColor)
        self.id = title
        self.timeManager = self.model.timeManager
        self.gs_aspect.border_color = borderColor
        self.setTitlesAndTextsColor(textColor)
        self.moveable = True
        self.textTitle  = title
        self.displayTitle = self.textTitle is not None
        self.displayRoundNumber = True
        self.displayPhaseNumber = self.timeManager.numberOfPhases() >= 2
        self.displayPhaseName = self.timeManager.numberOfPhases() >= 2

        self.initLabels()

    
    def initLabels(self):
        self.labels =[]
 
        if self.displayTitle:
            self.labelTitle = QtWidgets.QLabel(self)
            self.labelTitle.setText(self.textTitle)
            self.labels.append(self.labelTitle)
        if self.displayRoundNumber:
            self.labelRoundNumber = QtWidgets.QLabel(self)
            self.labelRoundNumber.setText('Not yet started')
            self.labels.append(self.labelRoundNumber)
        if self.displayPhaseNumber:
            self.labelPhaseNumber = QtWidgets.QLabel(self)
            self.labels.append(self.labelPhaseNumber)
        if self.displayPhaseName:
            self.labelPhaseName = QtWidgets.QLabel(self)
            self.labels.append(self.labelPhaseName)

        for aLabel in self.labels:
            aLabel.setStyleSheet(self.text1_aspect.getTextStyle())
        if self.displayTitle:
            self.labelTitle.setStyleSheet(self.title1_aspect.getTextStyle())

        # Créer un layout vertical
        layout = QtWidgets.QVBoxLayout()
        for aLabel in self.labels:
            layout.addWidget(aLabel)
        self.setLayout(layout)

        self.show()
        self.updateLabelsandWidgetSize()


    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QBrush(self.gs_aspect.getBackgroundColorValue(), Qt.SolidPattern))
        painter.setPen(QPen(self.gs_aspect.getBorderColorValue(), self.gs_aspect.getBorderSize()))
        painter.drawRect(0, 0, self.getSizeXGlobal() -1, self.getSizeYGlobal() -1)
        painter.end()

    def updateTimeLabel(self):
        self.labelRoundNumber.setText('Round Number : {}'.format(
            self.timeManager.currentRoundNumber))
        if self.displayPhaseNumber:
            self.labelPhaseNumber.setText('Phase Number : {}'.format(
                self.timeManager.currentPhaseNumber))
            self.labelPhaseName.setText(self.timeManager.getCurrentPhase().name)

        self.updateLabelsandWidgetSize()


    def updateLabelsandWidgetSize(self):
        # Recalculer les dimensions en fonction du texte et du styleSheet utilisé dans les QLabel
        for aLabel in self.labels:
            aLabel.setFixedWidth(aLabel.fontMetrics().boundingRect(aLabel.text()).width())
            aLabel.setFixedHeight(aLabel.fontMetrics().boundingRect(aLabel.text()).height())
            aLabel.adjustSize()
        
        max_right = max(aLabel.geometry().right() for aLabel in self.labels)
        max_bottom = max(aLabel.geometry().bottom() for aLabel in self.labels)
        
        self.sizeXGlobal = max_right +self.rightMargin
        self.setFixedSize(QSize(self.getSizeXGlobal() , self.getSizeYGlobal()))
    

    def getSizeXGlobal(self):
        return self.sizeXGlobal
    
    
    def getSizeYGlobal(self):
        somme = 10
        for label in self.labels:
            somme += label.height()  + self.verticalGapBetweenLabels
        return somme