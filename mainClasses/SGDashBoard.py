from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null, true

from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGIndicators import SGIndicators


# Class who is responsible of the Legend creation
class SGDashBoard(SGGameSpace):

    def __init__(self, parent, title, displayRefresh='instantaneous', borderColor=Qt.black, backgroundColor=Qt.lightGray, titleColor=Qt.black, layout="vertical"):
        super().__init__(parent, 0, 60, 0, 0, true, backgroundColor)
        self.model = parent
        self.id = title
        self.indicatorNames = []
        self.indicators = []
        self.borderColor = borderColor
        self.backgroundColor = backgroundColor
        self.titleColor = titleColor
        self.y = 0
        self.isDisplay = True
        self.displayRefresh = displayRefresh
        self.IDincr = 0
        if layout == 'vertical':
            self.layout = QtWidgets.QVBoxLayout()
        elif layout == 'horizontal':
            self.layout = QtWidgets.QHBoxLayout()

    def showIndicators(self):
        # Delete all
        layout = self.layout

        title = QtWidgets.QLabel(self.id)
        font = QFont()
        font.setBold(True)
        title.setFont(font)
        color = QColor(self.titleColor)
        color_string = f"color: {color.name()};"
        title.setStyleSheet(color_string)
        layout.addWidget(title)

        for indicator in self.indicators:
            if indicator.isDisplay:
                layout.addLayout(indicator.indicatorLayout)

        # Create a QPushButton to update the text
        if self.displayRefresh == 'withButton':
            self.button = QtWidgets.QPushButton("Update Scores")
            self.button.clicked.connect(
                lambda: [indicator.updateText() for indicator in self.indicators])
            layout.addWidget(self.button)

        self.setLayout(layout)

        # Drawing the DB
    def paintEvent(self, event):
        if self.checkDisplay():
            if len(self.indicators) != 0:
                painter = QPainter()
                painter.begin(self)
                painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
                painter.setPen(QPen(self.borderColor, 1))
                # Draw the corner of the DB
                self.setMinimumSize(self.getSizeXGlobal()+10,
                                    self.getSizeYGlobal()+10)
                painter.drawRect(0, 0, self.getSizeXGlobal(),
                                 self.getSizeYGlobal())

                painter.end()

    def checkDisplay(self):
        if self.isDisplay:
            return True
        else:
            return False

    def addIndicator(self, method, entity, color=Qt.black, attribute=None, value=None, indicatorName=None, isDisplay=True):
        """
        Add an Indicator on the DashBoard.

        Args:
            method (str) : name of the method in ["sumAtt","avgAtt","minAtt","maxAtt","nb","nbWithLess","nbWithMore","nbEqualTo","score"].
            entity (str) : "cell" or "agent" or None (only for score)
            color (Qt.color) : text color
            attribute (str) : concerned attribute 
            value (str, optionnal) : concerned value
            indicatorName (str, optionnal) : name displayed on the dashboard
            isDisplay (bool) : display on the dashboard (default : True)

        """
        self.y = self.y+1
        indicator = SGIndicators(
            self, self.y, indicatorName, method, attribute, value, entity, color, isDisplay)
        self.indicatorNames.append(indicator.name)
        self.indicators.append(indicator)
        indicator.id = self.IDincr
        self.IDincr = +1
        if entity == 'cell':
            self.setCellWatchers(attribute, indicator)
        return indicator

    def setCellWatchers(self, attribut, indicator):
        grids = self.model.getGrids()
        for grid in grids:
            cellCollection = grid.collectionOfCells
            if attribut not in cellCollection.watchers.keys():
                cellCollection.watchers[attribut] = []
            cellCollection.watchers[attribut].append(indicator)

    def addIndicator_Sum(self, entity, attribut, value, indicatorName, isDisplay, color):
        """
        Add a sum indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            value (str, optionnal) : non required
            indicatorName (str, optionnal) : name displayed on the dashboard
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'sumAtt'
        indicator = self.addIndicator(
            method, entity, color, attribut, value, indicatorName, isDisplay)
        return indicator

    def addIndicator_Avg(self, entity, attribut, value, indicatorName, color):
        """
        Add a average indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            value (str, optionnal) : non required
            indicatorName (str, optionnal) : name displayed on the dashboard
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'avgAtt'
        indicator = self.addIndicator(
            method, entity, color, attribut, value, indicatorName)
        return indicator

    def addIndicator_Min(self, entity, attribut, value, indicatorName, color):
        """
        Add a minimum indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            value (str, optionnal) : non required
            indicatorName (str, optionnal) : name displayed on the dashboard
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'minAtt'
        indicator = self.addIndicator(
            method, entity, color, attribut, value, indicatorName)
        return indicator

    def addIndicator_Max(self, entity, attribut, value, indicatorName, color):
        """
        Add a maximum indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            value (str, optionnal) : non required
            indicatorName (str, optionnal) : name displayed on the dashboard
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'maxAtt'
        indicator = self.addIndicator(
            method, entity, color, attribut, value, indicatorName)
        return indicator

    def addIndicator_EqualTo(self, entity, attribut, value, indicatorName, color):
        """
        Add a equal to indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            value (str) : value to do the logical test
            indicatorName (str, optionnal) : name displayed on the dashboard
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'nbEqualTo'
        indicator = self.addIndicator(
            method, entity, color, attribut, value, indicatorName)
        return indicator

    def addIndicator_WithLess(self, entity, attribut, value, indicatorName, color):
        """
        Add a with less indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            value (str) : value to do the logical test
            indicatorName (str, optionnal) : name displayed on the dashboard
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'nbWithLess'
        indicator = self.addIndicator(
            method, entity, color, attribut, value, indicatorName)
        return indicator

    def addIndicator_WithMore(self, entity, attribut, value, indicatorName, color):
        """
        Add a with more indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            value (str) : for certain methods, a value is required
            indicatorName (str, optionnal) : name displayed on the dashboard
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'nbWithMore'
        indicator = self.addIndicator(
            method, entity, color, attribut, value, indicatorName)
        return indicator

    def addIndicator_Nb(self, entity, attribut, value, indicatorName, color):
        """
        Add a sum indicator
        Args :
            entity (str) : "cell" or "agent
            attribute (str) : concerned attribute 
            value (str, optionnal) : non required
            indicatorName (str, optionnal) : name displayed on the dashboard
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'nb'
        indicator = self.addIndicator(
            method, entity, color, attribut, value, indicatorName)
        return indicator

    # *Functions to have the global size of a gameSpace
    def getSizeXGlobal(self):
        return 70+len(self.getLongest())*5+50

    def getSizeYGlobal(self):
        somme = 100
        return somme+len(self.indicatorNames)

    def getLongest(self):
        # print(self.indicatorNames)
        longestWord = ""
        for indicatorName in self.indicatorNames:
            if len(indicatorName) > len(longestWord):
                longestWord = indicatorName
        return longestWord

    def mouseMoveEvent(self, e):

        if e.buttons() != Qt.LeftButton:
            return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())

        drag.exec_(Qt.MoveAction)
