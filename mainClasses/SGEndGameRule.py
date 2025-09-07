from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true

from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGEndGameCondition import SGEndGameCondition
from mainClasses.SGAspect import SGAspect


class SGEndGameRule(SGGameSpace):

    def __init__(self, parent, title, numberRequired, displayRefresh='instantaneous', isDisplay=True, borderColor=Qt.black, backgroundColor=Qt.lightGray, layout="vertical", textColor=Qt.black):
        super().__init__(parent, 0, 60, 0, 0, true, backgroundColor)
        self.model = parent
        self.id = title
        self.displayRefresh = displayRefresh
        self.isDisplay = True
        # Configure styles using gs_aspect instead of individual attributes
        self.gs_aspect.border_color = borderColor
        self.gs_aspect.border_size = 1
        self.gs_aspect.background_color = backgroundColor
        # Configure text colors using the aspect system
        self.setTitlesAndTextsColor(textColor)
        # Initialize theme aspects for different states
        self.success_aspect = SGAspect.success()
        self.endGameConditions = []
        self.numberRequired = numberRequired
        self.isDisplay = isDisplay
        if layout == 'vertical':
            self.layout = QtWidgets.QVBoxLayout()
        elif layout == 'horizontal':
            self.layout = QtWidgets.QHBoxLayout()

    def showEndGameConditions(self):
        """
        At the end of the configuration, permits to show the EndGameConditions.
        """
        if self.isDisplay:
            layout = self.layout

            title = QtWidgets.QLabel(self.id)
            font = QFont()
            font.setBold(True)
            title.setFont(font)
            layout.addWidget(title)
            for condition in self.endGameConditions:
                layout.addLayout(condition.conditionLayout)

            # Create a QPushButton to update the text
            if self.displayRefresh == 'withButton':
                self.button = QtWidgets.QPushButton("Update Scores")
                self.button.clicked.connect(
                    lambda: [condition.updateText() for condition in self.endGameConditions])
                layout.addWidget(self.button)

            self.setLayout(layout)
            self.show()

    # To add a condition to end the game
    def addEndGameCondition_onIndicator(self, indicator, logicalTest, objective, name="Indicator based condition", color=Qt.black, isDisplay=True):
        """
        Create an EndGame Condition with an Indicator

        Args:
            indicator (instance) : indicator concerned
            logicalTest (str): logical test concerned in ["greater","greater or equal","equal", "less or equal","less"]
            objective (int) : objective value to do logical test with
            name (str) : name of the end game condition, displayed (default : "Indicator based condition")
            color (Qt.color) : text color (default : black)
            isDisplay (bool) : is displayed in the EndGameRule board (default : True)
        """
        aCondition = SGEndGameCondition(self, name, entity=indicator, method=logicalTest, objective=objective,
                                        attribut=None, color=color, calcType="onIndicator", isDisplay=isDisplay)
        self.endGameConditions.append(aCondition)
        self.model.timeManager.conditionOfEndGame.append(aCondition)

    def addEndGameCondition_onEntity(self, aEntity, attribute, logicalTest, objective, name="Entity based condition",speciesName=None, aGrid=None, color=Qt.black, isDisplay=True):
        """Create an EndGame Condition with an Entity

        Args:
            aEntity (SGCell or SGAgent) : the entity (cell, agent)
            attribute (str) : attribute concerned
            logicalTest (str): logical test concerned in ["greater","greater or equal","equal", "less or equal","less"]
            objective (int) : objective value to do logical test with
            name (str) : name of the end game condition, displayed (default : “Entity based condition")
            speciesName (str) : name of the AgentSpecies (only if your entity is an Agent, default : None)
            aGrid (instance) : instance of the concerned grid (only if your entity is a Cell, default : None)
            color (Qt.color) : text color (default : black)
            isDisplay (bool) : is displayed in the EndGameRule board (default : True)
        """
      
        aCondition = SGEndGameCondition(self, name, entity=aEntity, method=logicalTest, objective=objective,
                                        attribut=attribute, color=color, calcType="onEntity", isDisplay=isDisplay)
        self.endGameConditions.append(aCondition)
        self.model.timeManager.conditionOfEndGame.append(aCondition)


    def addEndGameCondition_onGameRound(self, logicalTest, objective, name="Game round condition", color=Qt.black, isDisplay=True):
        """
        Create an EndGame Condition on the time (game rounds)

        Args:
            logicalTest (str): logical test concerned in ["greater","greater or equal","equal", "less or equal","less"]
            objective (int) : objective value to do logical test with
            name (str) : name of the end game condition, displayed (default : “Entity based condition")
            color (Qt.color) : text color (default : black)
            isDisplay (bool) : is displayed in the EndGameRule board (default : True)
        """
        aCondition = SGEndGameCondition(self, name, entity=None, method=logicalTest, objective=objective,
                                        attribut=None, color=color, calcType="onGameRound", isDisplay=isDisplay)
        self.endGameConditions.append(aCondition)
        self.model.timeManager.conditionOfEndGame.append(aCondition)

   

    def addEndGameCondition_onLambda(self, lambda_function, name="Lambda based condition", color=Qt.black, isDisplay=True):
        """
        Create an EndGame Condition based on a lambda function.

        Args:
            lambda_function (callable): A lambda function that returns a boolean indicating the end game condition.
            name (str): Name of the end game condition, displayed (default: "Lambda based condition").
            color (Qt.color): Text color (default: black).
            isDisplay (bool): Whether to display in the EndGameRule board (default: True).
        """
        aCondition = SGEndGameCondition(self, name, entity=None, method=lambda_function, objective=None,
                                        attribut=None, color=color, calcType="onLambda", isDisplay=isDisplay)
        self.endGameConditions.append(aCondition)
        self.model.timeManager.conditionOfEndGame.append(aCondition)

    def paintEvent(self, event):
        if self.checkDisplay():
            painter = QPainter()
            painter.begin(self)
            painter.setBrush(QBrush(self.gs_aspect.getBackgroundColorValue(), Qt.SolidPattern))
            painter.setPen(QPen(self.gs_aspect.getBorderColorValue(), self.gs_aspect.getBorderSize()))
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

    # *Functions to have the global size of a gameSpace
    def getSizeXGlobal(self):
        return 150

    def getSizeYGlobal(self):
        return 150

    # ============================================================================
    # MODELER METHODS
    # ============================================================================
    
    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================
    
    def setBorderColor(self, color):
        """
        Set the border color of the end game rule.
        
        Args:
            color (QColor or Qt.GlobalColor): The border color
        """
        self.gs_aspect.border_color = color
        
    def setBorderSize(self, size):
        """
        Set the border size of the end game rule.
        
        Args:
            size (int): The border size in pixels
        """
        self.gs_aspect.border_size = size
        
    def setBackgroundColor(self, color):
        """
        Set the background color of the end game rule.
        
        Args:
            color (QColor or Qt.GlobalColor): The background color
        """
        self.gs_aspect.background_color = color
        
    def setTextColor(self, color):
        """
        Set the text color of the end game rule.
        
        Args:
            color (QColor or Qt.GlobalColor): The text color
        """
        self.setTitlesAndTextsColor(color)
        
    def setSuccessThemeColor(self, color):
        """
        Set the success theme color for completed conditions.
        
        Args:
            color (QColor or Qt.GlobalColor): The success color
        """
        self.success_aspect.color = color
