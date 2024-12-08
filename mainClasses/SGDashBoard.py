from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGIndicator import SGIndicator
from mainClasses.SGEntityDef import *
from mainClasses.SGEntity import SGEntity
from mainClasses.SGPlayer import SGPlayer


# Class who is responsible of the Legend creation
class SGDashBoard(SGGameSpace):

    def __init__(self, parent, title, borderColor=Qt.black, backgroundColor=Qt.lightGray, titleColor=Qt.black, layout="vertical"):
        super().__init__(parent, 0, 60, 0, 0, true, backgroundColor)
        self.id = title
        self.indicators = []
        self.textTitle  = title
        self.displayTitle = self.textTitle is not None
        self.gs_aspect.border_color = borderColor
        self.setTitlesColor(titleColor)
        self.posYOfItems = 0
        self.isDisplay = True
        self.IDincr = 0

        # Créer un layout
        if layout == 'vertical':
            self.layout = QtWidgets.QVBoxLayout()
        elif layout == 'horizontal':
            self.layout = QtWidgets.QHBoxLayout()
        
        self.initLabels()
        # self.updateLabelsandWidgetSize()

    def initLabels(self):
        self.labels =[]

        # ajouter le label du titre en premier
        if self.displayTitle:
            self.labelTitle = QtWidgets.QLabel(self)
            self.labelTitle.setText(self.textTitle)
            self.labelTitle.setStyleSheet(self.title1_aspect.getTextStyle())
            self.labelTitle.adjustSize()
            self.labels.append(self.labelTitle)
            self.layout.addWidget(self.labelTitle)

        # The label of indicators are added afterwards

        # adjust sizes       
        self.updateLabelsandWidgetSize()
        #set layout
        self.setLayout(self.layout)

    def showIndicators(self):
        """This method is called when the model is launched (after all indicators have been defined by the modeler"""
          
        # ajout des labels des indicateurs
        for indicator in self.indicators:
            if indicator.isDisplay:
                self.labels.append(indicator.label)
                self.layout.addWidget(indicator.label)

        # adjust sizes       
        self.updateLabelsandWidgetSize()
        #set layout
        self.setLayout(self.layout)


    def addIndicator(self, entityName,method,attribute=None,value=None,color=Qt.black,logicOp=None,title=None,displayRefresh="instantaneous",onTimeConditions=None,isDisplay=True):
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
            displayRefresh (str) : instantaneous (default) or onTimeConditions
            onTimeConditions (dict, only if displayRefresh=atSpecifiedPhase) : a type and a specifiedValue
                'onTimeConditions' a dict with type of conditions and specified value 
                phaseName   (str or list of str)
                phaseNumber (int or list of int)
                lambdaTestOnPhaseNumber (a lambda function with syntax [ phaseNumber : test with phaseNumber])
                roundNumber (int or list of int)
                lambdaTestOnRoundNumber   (a lambda function with syntax [ roundNumber : test with roundNumber])
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
        
        indicator = SGIndicator(self, title, method, attribute, value, listOfEntDef, logicOp, color,displayRefresh,onTimeConditions,isDisplay)
        self.indicators.append(indicator)
        indicator.id = self.IDincr
        self.IDincr = +1
        if method != "separator":
            for entDef in listOfEntDef:
                entDef.addWatcher(indicator)
        return indicator
    

    def addIndicatorOnEntity(self, entity, attribute, color=Qt.black, value=None, logicOp=None, title=None, displayRefresh="instantaneous",isDisplay=True):
        """
        Add an Indicator on a particular entity on the DashBoard only two methods available : display (default) & thresoldToLogicOp (if a value and a logicOp defined).

        Args:
            entity (SGEntity) : an entity (cell, or agent)
            attribute (str) : concerned attribute 
            color (Qt.color) : text color
            logicOp (str, optionnal) : only if method = thresoldToLogicOp, logical connector in ["greater","greater or equal","equal", "less or equal","less"]
            thresold (str, optionnal) : only if method = thresoldToLogicOp, thresold value (default :None )
            title (str, optionnal) : name displayed on the dashboard
            displayRefresh (str) :
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
    
        indicator = SGIndicator(self, title, method, attribute, value, entity, logicOp, color, displayRefresh,isDisplay)
        self.indicators.append(indicator)
        indicator.id = self.IDincr
        self.IDincr = +1
        
        entity.addWatcher(indicator)

        return indicator

    def addIndicatorOnSimVariable(self,aSimulationVariable,displayRefresh="instantaneous"):
        self.posYOfItems = self.posYOfItems+1
        indicator=SGIndicator(self,aSimulationVariable.name,"simVar",None,aSimulationVariable.value,aSimulationVariable,None,aSimulationVariable.color,displayRefresh,None,aSimulationVariable.isDisplay)
        self.indicators.append(indicator)
        indicator.id = self.IDincr
        self.IDincr = +1

        aSimulationVariable.addWatcher(indicator)
    
        return indicator

    def addIndicator_Sum(self, entity, attribute,title, color, displayRefresh="instantaneous", isDisplay=True):
        """
        Add a sum indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            title (str, optionnal) : name displayed on the dashboard
            color (Qt.color) : text color
            displayRefresh (str) :
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'sumAtt'
        indicator = self.addIndicator(entity,method,attribute,value=None,color=color,logicOp=None,title=title,displayRefresh=displayRefresh,isDisplay=isDisplay)
        return indicator

    def addIndicator_Avg(self, entity, attribute, title, color,displayRefresh="instantaneous",isDisplay=True):
        """
        Add a average indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            title (str, optionnal) : name displayed on the dashboard
            color (Qt.color) : text color
            displayRefresh (str) :
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'avgAtt'
        indicator = self.addIndicator(entity,method,attribute,value=None,color=color,logicOp=None,title=title,displayRefresh=displayRefresh,isDisplay=isDisplay)
        return indicator

    def addIndicator_Min(self, entity, attribute, title, color,displayRefresh="instantaneous",isDisplay=True):
        """
        Add a minimum indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            title (str, optionnal) : name displayed on the dashboard
            color (Qt.color) : text color
            displayRefresh (str) :
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'minAtt'
        indicator = self.addIndicator(entity,method,attribute,value=None,color=color,logicOp=None,title=title,displayRefresh=displayRefresh,isDisplay=isDisplay)
        return indicator

    def addIndicator_Max(self, entity, attribute,title, color,displayRefresh="instantaneous",isDisplay=True):
        """
        Add a maximum indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            title (str, optionnal) : name displayed on the dashboard
            color (Qt.color) : text color
            displayRefresh (str) :
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'maxAtt'
        indicator = self.addIndicator(entity,method,attribute,value=None,color=color,logicOp=None,title=title,displayRefresh=displayRefresh,isDisplay=isDisplay)
        return indicator

    def addIndicator_EqualTo(self, entity, attribute, value, title, color,displayRefresh="instantaneous",isDisplay=True):
        """
        Add a equal to indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            value (str) : value to do the logical test
            title (str, optionnal) : name displayed on the dashboard
            color (Qt.color) : text color
            displayRefresh (str) :
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'nbEqualTo'
        indicator = self.addIndicator(entity,method,attribute,value,color,logicOp=None,title=title,displayRefresh=displayRefresh,isDisplay=isDisplay)
        return indicator

    def addIndicator_WithLess(self, entity, attribute, value, title, color,displayRefresh="instantaneous",isDisplay=True):
        """
        Add a with less indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            value (str) : value to do the logical test
            title (str, optionnal) : name displayed on the dashboard
            color (Qt.color) : text color
            displayRefresh (str) :
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'nbWithLess'
        indicator = self.addIndicator(entity,method,attribute,value,color,logicOp=None,title=title,displayRefresh=displayRefresh,isDisplay=isDisplay)
        return indicator

    def addIndicator_WithMore(self, entity, attribute, value, title, color,displayRefresh="instantaneous",isDisplay=True):
        """
        Add a with more indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            value (str) : for certain methods, a value is required
            title (str, optionnal) : name displayed on the dashboard
            color (Qt.color) : text color
            displayRefresh (str) :
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'nbWithMore'
        indicator = self.addIndicator(entity,method,attribute,value,color,logicOp=None,title=title,displayRefresh=displayRefresh,isDisplay=isDisplay)
        return indicator

    def addIndicator_Nb(self, entity, attribute, title, color,displayRefresh="instantaneous",isDisplay=True):
        """
        Add a sum indicator
        Args :
            entity (str) : "cell" or "agent" or aAgentSpecies
            attribute (str) : concerned attribute 
            title (str, optionnal) : name displayed on the dashboard
            color (Qt.color) : text color
            displayRefresh (str) :
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'nb'
        indicator = self.addIndicator(entity,method,attribute,value=None,color=color,logicOp=None,title=title,displayRefresh=displayRefresh,isDisplay=isDisplay)
        return indicator
    
    def addSeparator(self):
        separator=self.addIndicator(None,"separator")
        return separator


#############################
        # Drawing the DB
    def paintEvent(self, event):
        if self.isDisplay and len(self.indicators) != 0:
            painter = QPainter()
            painter.begin(self)
            painter.setBrush(QBrush(self.gs_aspect.getBackgroundColor(), Qt.SolidPattern))
            painter.setPen(QPen(self.gs_aspect.getBorderColor(), self.gs_aspect.getBorderSize()))
            # Draw the corner of the DB
            # self.setMinimumSize(self.getSizeXGlobal(), self.getSizeYGlobal())
            painter.drawRect(0, 0, self.getSizeXGlobal()-1, self.getSizeYGlobal()-1)
            painter.end()

    def updateLabelsandWidgetSize(self):
        # Recalculer les dimensions en fonction du texte et du styleSheet utilisé dans les QLabel
        for aLabel in self.labels:
            aLabel.setFixedWidth(aLabel.fontMetrics().boundingRect(aLabel.text()).width()+5)
            aLabel.setFixedHeight(aLabel.fontMetrics().boundingRect(aLabel.text()).height())
            aLabel.adjustSize()
            
        max_width = max([aLabel.width() for aLabel in self.labels])
        self.sizeXGlobal = max_width +self.rightMargin
        self.sizeYGlobal = sum([aLabel.height() + self.verticalGapBetweenLabels for aLabel in self.labels])
        self.setFixedSize(QSize(self.getSizeXGlobal() , self.getSizeYGlobal()))
    

    def getSizeXGlobal(self):
        return self.sizeXGlobal
    
    def getSizeYGlobal(self):
        return self.sizeYGlobal
    
