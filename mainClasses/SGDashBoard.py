from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null, true
from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGIndicator import SGIndicator
from mainClasses.SGEntityDef import *
from mainClasses.SGEntity import SGEntity
from mainClasses.SGPlayer import SGPlayer


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
        self.posYOfItems = 0
        self.isDisplay = True
        self.displayRefresh = displayRefresh
        self.IDincr = 0
        if layout == 'vertical':
            self.layout = QtWidgets.QVBoxLayout()
        elif layout == 'horizontal':
            self.layout = QtWidgets.QHBoxLayout()

    def showIndicators(self):
        """At the end of the configuration, permits to show the Indicators."""
        # Delete all
        layout = self.layout

        title = QtWidgets.QLabel(self.id)
        font = QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setPixelSize(14)
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

    def addIndicator(self, entityName,method,attribute=None,value=None,color=Qt.black,logicOp=None,title=None,timeReset=False,isDisplay=True):
        
        """
        Add an Indicator on the DashBoard.

        Args:
            entityName (str) :  aEntityDef name, or aEntityDef, of a List of EntityDef or names, or None (only for score)
            method (str) : name of the method in ["sumAtt","avgAtt","minAtt","maxAtt","nb","nbWithLess","nbWithMore","nbEqualTo","thresoldToLogicOp","score"].
            attribute (str) : concerned attribute 
            value (str, optionnal) : concerned value
            color (Qt.color) : text color
            logicOp (str, optionnal) : only if method = thresoldToLogicOp, logical connector in ["greater","greater or equal","equal", "less or equal","less"]
            title (str, optionnal) : name displayed on the dashboard
            timeReset (bool) : if True, the displayed result will be set to sero at each new round
            isDisplay (bool) : display on the dashboard (default : True)

        """
        self.posYOfItems = self.posYOfItems+1
        if isinstance(entityName,str) :
            res = self.model.getEntityDef(entityName)
            if res is None: raise ValueError('Wrong type')  
            listOfEntDef = [self.model.getEntityDef(entityName)]
        elif isinstance(entityName,SGEntityDef) :
            listOfEntDef = [entityName]
        elif entityName is None :
            listOfEntDef = None
        elif isinstance(entityName,list) and isinstance(entityName[0],str) :
            listOfEntDef = [self.model.getEntityDef(aEntName) for aEntName in entityName]
        elif isinstance(entityName,list) and isinstance(entityName[0],SGEntityDef) :
            listOfEntDef = entityName
        elif issubclass(type(entityName),SGEntity) : # A PRIORI CE CAS NE SE PRESENTE JAMAIS CAR dans ce genre cas, on utilise la méthode addIndicatorOnEntity()
            listOfEntDef = entityName
        else:
            raise ValueError('Wrong type')
        
        indicator = SGIndicator(self, title, method, attribute, value, listOfEntDef, logicOp, color,timeReset,isDisplay)
        self.indicatorNames.append(indicator.name)
        self.indicators.append(indicator)
        indicator.id = self.IDincr
        self.IDincr = +1
        if method != "separator":
            for entDef in listOfEntDef:
                entDef.addWatcher(indicator)
        return indicator
    

    def addIndicatorOnEntity(self, entity, attribute, color=Qt.black, value=None, logicOp=None, title=None, timeReset=False,isDisplay=True):
        """
        Add an Indicator on a particular entity on the DashBoard only two methods available : display (default) & thresoldToLogicOp (if a value and a logicOp defined).

        Args:
            entity (SGEntity) : an entity (cell, or agent)
            attribute (str) : concerned attribute 
            color (Qt.color) : text color
            logicOp (str, optionnal) : only if method = thresoldToLogicOp, logical connector in ["greater","greater or equal","equal", "less or equal","less"]
            thresold (str, optionnal) : only if method = thresoldToLogicOp, thresold value (default :None )
            title (str, optionnal) : name displayed on the dashboard
            timeReset (bool) : if True, the displayed result will be set to sero at each new round
            isDisplay (bool) : display on the dashboard (default : True)

        """
        if not isinstance(entity,(SGEntity,SGEntityDef,SGPlayer)): raise ValueError ('Wrong entity format')
        self.entity= entity

        if value is None:
            method = "display"
        else:
            if logicOp is not None:
                method = "thresoldToLogicOp"
            else:
                raise ValueError("You need to specify a logicOp")
        
        self.posYOfItems = self.posYOfItems+1
    
        indicator = SGIndicator(self, title, method, attribute, value, entity, logicOp, color, timeReset,isDisplay)
        self.indicatorNames.append(indicator.name)
        self.indicators.append(indicator)
        indicator.id = self.IDincr
        self.IDincr = +1
        
        entity.addWatcher(indicator)

        return indicator

    def addIndicatorOnSimVariable(self,aSimulationVariable,timeReset=False):
        self.posYOfItems = self.posYOfItems+1
        indicator=SGIndicator(self,aSimulationVariable.name,"simVar",None,aSimulationVariable.value,aSimulationVariable,timeReset,aSimulationVariable.color,False,aSimulationVariable.isDisplay)
        self.indicatorNames.append(indicator.name)
        self.indicators.append(indicator)
        indicator.id = self.IDincr
        self.IDincr = +1

        aSimulationVariable.addWatcher(indicator)
    
        return indicator

    def addIndicator_Sum(self, entity, attribute,title, color, timeReset=False, isDisplay=True):
        """
        Add a sum indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            title (str, optionnal) : name displayed on the dashboard
            color (Qt.color) : text color
            timeReset (bool) : if True, the displayed result will be set to sero at each new round
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'sumAtt'
        indicator = self.addIndicator(entity,method,attribute,value=None,color=color,logicOp=None,title=title,timeReset=timeReset,isDisplay=isDisplay)
        return indicator

    def addIndicator_Avg(self, entity, attribute, title, color,timeReset=False,isDisplay=True):
        """
        Add a average indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            title (str, optionnal) : name displayed on the dashboard
            color (Qt.color) : text color
            timeReset (bool) : if True, the displayed result will be set to sero at each new round
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'avgAtt'
        indicator = self.addIndicator(entity,method,attribute,value=None,color=color,logicOp=None,title=title,timeReset=timeReset,isDisplay=isDisplay)
        return indicator

    def addIndicator_Min(self, entity, attribute, title, color,timeReset=False,isDisplay=True):
        """
        Add a minimum indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            title (str, optionnal) : name displayed on the dashboard
            color (Qt.color) : text color
            timeReset (bool) : if True, the displayed result will be set to sero at each new round
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'minAtt'
        indicator = self.addIndicator(entity,method,attribute,value=None,color=color,logicOp=None,title=title,timeReset=timeReset,isDisplay=isDisplay)
        return indicator

    def addIndicator_Max(self, entity, attribute,title, color,timeReset=False,isDisplay=True):
        """
        Add a maximum indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            title (str, optionnal) : name displayed on the dashboard
            color (Qt.color) : text color
            timeReset (bool) : if True, the displayed result will be set to sero at each new round
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'maxAtt'
        indicator = self.addIndicator(entity,method,attribute,value=None,color=color,logicOp=None,title=title,timeReset=timeReset,isDisplay=isDisplay)
        return indicator

    def addIndicator_EqualTo(self, entity, attribute, value, title, color,timeReset=False,isDisplay=True):
        """
        Add a equal to indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            value (str) : value to do the logical test
            title (str, optionnal) : name displayed on the dashboard
            color (Qt.color) : text color
            timeReset (bool) : if True, the displayed result will be set to sero at each new round
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'nbEqualTo'
        indicator = self.addIndicator(entity,method,attribute,value,color,logicOp=None,title=title,timeReset=timeReset,isDisplay=isDisplay)
        return indicator

    def addIndicator_WithLess(self, entity, attribute, value, title, color,timeReset=False,isDisplay=True):
        """
        Add a with less indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            value (str) : value to do the logical test
            title (str, optionnal) : name displayed on the dashboard
            color (Qt.color) : text color
            timeReset (bool) : if True, the displayed result will be set to sero at each new round
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'nbWithLess'
        indicator = self.addIndicator(entity,method,attribute,value,color,logicOp=None,title=title,timeReset=timeReset,isDisplay=isDisplay)
        return indicator

    def addIndicator_WithMore(self, entity, attribute, value, title, color,timeReset=False,isDisplay=True):
        """
        Add a with more indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            value (str) : for certain methods, a value is required
            title (str, optionnal) : name displayed on the dashboard
            color (Qt.color) : text color
            timeReset (bool) : if True, the displayed result will be set to sero at each new round
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'nbWithMore'
        indicator = self.addIndicator(entity,method,attribute,value,color,logicOp=None,title=title,timeReset=timeReset,isDisplay=isDisplay)
        return indicator

    def addIndicator_Nb(self, entity, attribute, title, color,timeReset=False,isDisplay=True):
        """
        Add a sum indicator
        Args :
            entity (str) : "cell" or "agent" or aAgentSpecies
            attribute (str) : concerned attribute 
            title (str, optionnal) : name displayed on the dashboard
            color (Qt.color) : text color
            timeReset (bool) : if True, the displayed result will be set to sero at each new round
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'nb'
        indicator = self.addIndicator(entity,method,attribute,value=None,color=color,logicOp=None,title=title,timeReset=timeReset,isDisplay=isDisplay)
        return indicator
    
    def addSeparator(self):
        separator=self.addIndicator(None,"separator")
        return separator

    # *Functions to have the global size of a gameSpace
    def getSizeXGlobal(self):
        return 70+len(self.getLongest())*5+70

    def getSizeYGlobal(self):
        somme = 150
        return somme+len(self.indicatorNames)*20

    def getLongest(self):
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
