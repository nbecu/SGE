from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null, true
from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGIndicator import SGIndicator
from mainClasses.SGEntityDef import *
from mainClasses.SGEntity import SGEntity


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

    def addIndicator(self, method, entityName, color=Qt.black, attribute=None, value=None, logicOp= None, indicatorName=None, isDisplay=True):
        # TODO Changer l'ordre des varaibles --> entityName,method,attribute........ puis la suite
        # changer le nom indicatorName, par title, ou text
        """
        Add an Indicator on the DashBoard.

        Args:
            method (str) : name of the method in ["sumAtt","avgAtt","minAtt","maxAtt","nb","nbWithLess","nbWithMore","nbEqualTo","thresoldToLogicOp","score"].
            entityName (str) :  aEntityDef name, or aEntityDef, of a List of EntityDef or names, or None (only for score)
            color (Qt.color) : text color
            attribute (str) : concerned attribute 
            value (str, optionnal) : concerned value
            logicOp (str, optionnal) : only if method = thresoldToLogicOp, logical connector in ["greater","greater or equal","equal", "less or equal","less"]
            indicatorName (str, optionnal) : name displayed on the dashboard
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
        
        indicator = SGIndicator(self, indicatorName, method, attribute, value, listOfEntDef, logicOp, color, isDisplay)
        self.indicatorNames.append(indicator.name)
        self.indicators.append(indicator)
        indicator.id = self.IDincr
        self.IDincr = +1
 
        for entDef in listOfEntDef:
            entDef.addWatcher(indicator)
        return indicator
    

    def addIndicatorOnEntity(self, entity, attribute, color=Qt.black, value=None, logicOp=None, indicatorName=None, isDisplay=True):
        """
        Add an Indicator on a particular entity on the DashBoard only two methods available : display (default) & thresoldToLogicOp (if a value and a logicOp defined).

        Args:
            entity (SGEntity) : an entity (cell, or agent)
            attribute (str) : concerned attribute 
            color (Qt.color) : text color
            logicOp (str, optionnal) : only if method = thresoldToLogicOp, logical connector in ["greater","greater or equal","equal", "less or equal","less"]
            thresold (str, optionnal) : only if method = thresoldToLogicOp, thresold value (default :None )
            indicatorName (str, optionnal) : name displayed on the dashboard
            isDisplay (bool) : display on the dashboard (default : True)

        """
        if not isinstance(entity,(SGEntity,SGEntityDef)): raise ValueError ('Wrong entity format')
        self.entity= entity

        if value is None:
            method = "display"
        else:
            if logicOp is not None:
                method = "thresoldToLogicOp"
            else:
                raise ValueError("You need to specify a logicOp")
        
        self.posYOfItems = self.posYOfItems+1
    
        indicator = SGIndicator(self, indicatorName, method, attribute, value, entity, logicOp, color, isDisplay)
        self.indicatorNames.append(indicator.name)
        self.indicators.append(indicator)
        indicator.id = self.IDincr
        self.IDincr = +1
        
        entity.addWatcher(indicator)

        return indicator

    def addIndicatorOnSimVariable(self,aSimulationVariable):
        self.posYOfItems = self.posYOfItems+1
        indicator=SGIndicator(self,aSimulationVariable.name,"simVar",None,aSimulationVariable.value,aSimulationVariable,None,aSimulationVariable.color,aSimulationVariable.isDisplay)
        self.indicatorNames.append(indicator.name)
        self.indicators.append(indicator)
        indicator.id = self.IDincr
        self.IDincr = +1

        aSimulationVariable.addWatcher(indicator)
    
        return indicator

    # BASCULE COTE EntityDef
    # def setCellWatchers(self, attribut, indicator):
    #     grids = self.model.getGrids()
    #     for grid in grids:
    #         cellCollection = self.model.cellCollection[grid.id]
    #         if attribut not in cellCollection["watchers"].keys():
    #             cellCollection["watchers"][attribut] = []
    #         cellCollection["watchers"][attribut].append(indicator)
        
    # def setAgentWatchers(self,indicator):
    #     if indicator.attribut is None:
    #         aAtt = 'nb'
    #     else:
    #         aAtt = indicator.attribut
    #     if indicator.entity == 'agents':
    #         if 'agents' not in self.model.agentSpecies.keys():
    #             self.model.agentSpecies['agents']={'watchers':{}}
    #         watchersDict=self.model.agentSpecies['agents']['watchers']
    #     else:
    #          watchersDict=self.model.agentSpecies[indicator.entity]['watchers']

    #     if aAtt not in watchersDict.keys():
    #         watchersDict[aAtt]=[]
    #     watchersDict[aAtt].append(indicator)

    def addIndicator_Sum(self, entity, attribut, value, indicatorName, color, isDisplay=True):
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
        indicator = self.addIndicator(method, entity, color, attribut, value, indicatorName, isDisplay)
        return indicator

    def addIndicator_Avg(self, entity, attribut, value, indicatorName, color,isDisplay=True):
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
        indicator = self.addIndicator(method, entity, color, attribut, value, indicatorName,isDisplay)
        return indicator

    def addIndicator_Min(self, entity, attribut, value, indicatorName, color,isDisplay=True):
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
        indicator = self.addIndicator(method, entity, color, attribut, value, indicatorName,isDisplay)
        return indicator

    def addIndicator_Max(self, entity, attribut, value, indicatorName, color,isDisplay=True):
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
        indicator = self.addIndicator(method, entity, color, attribut, value, indicatorName,isDisplay)
        return indicator

    def addIndicator_EqualTo(self, entity, attribut, value, indicatorName, color,isDisplay=True):
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
        indicator = self.addIndicator(method, entity, color, attribut, value, indicatorName,isDisplay)
        return indicator

    def addIndicator_WithLess(self, entity, attribut, value, indicatorName, color,isDisplay=True):
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
        indicator = self.addIndicator(method, entity, color, attribut, value, indicatorName,isDisplay)
        return indicator

    def addIndicator_WithMore(self, entity, attribut, value, indicatorName, color,isDisplay=True):
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
        indicator = self.addIndicator(method, entity, color, attribut, value, indicatorName,isDisplay)
        return indicator

    def addIndicator_Nb(self, entity, attribut, value, indicatorName, color,isDisplay=True):
        """
        Add a sum indicator
        Args :
            entity (str) : "cell" or "agent" or aAgentSpecies
            attribute (str) : concerned attribute 
            value (str, optionnal) : non required
            indicatorName (str, optionnal) : name displayed on the dashboard
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'nb'
        indicator = self.addIndicator(method, entity, color, attribut, value, indicatorName,isDisplay)
        return indicator

    # *Functions to have the global size of a gameSpace
    def getSizeXGlobal(self):
        return 70+len(self.getLongest())*5+50

    def getSizeYGlobal(self):
        somme = 150
        return somme+len(self.indicatorNames)*20

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
