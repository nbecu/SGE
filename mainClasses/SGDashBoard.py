from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGIndicator import SGIndicator
from mainClasses.SGEntityType import *
from mainClasses.SGEntity import SGEntity
from mainClasses.SGPlayer import SGPlayer
from mainClasses.SGCell import SGCell


# Class who is responsible of the Legend creation
class SGDashBoard(SGGameSpace):

    def __init__(self, parent, title, borderColor, borderSize, backgroundColor, titleColor, layout):
        super().__init__(parent, 0, 60, 0, 0, true, backgroundColor)
        # self.id = title
        self.indicators = []
        self.textTitle  = title
        self.displayTitle = self.textTitle is not None
        self.gs_aspect.border_color = borderColor
        self.gs_aspect.border_size = borderSize
        self.setTitlesColor(titleColor)
        self.posYOfItems = 0
        self.isDisplay = True
        self.IDincr = 0

        # Créer un layout
        if layout == 'vertical':
            self.layout = QtWidgets.QVBoxLayout()
        elif layout == 'horizontal':
            self.layout = QtWidgets.QHBoxLayout()
        # Set layout margins to include right/bottom space so frame doesn't crop text
        try:
            # Add 4px left margin so title and indicators aren't flush to the border
            self.layout.setContentsMargins(4, 0, self.rightMargin, self.verticalGapBetweenLabels)
            self.layout.setSpacing(self.verticalGapBetweenLabels)
        except Exception:
            pass
        
        self.initLabels()
        # self.updateLabelsandWidgetSize()

    def initLabels(self):
        self.labels =[]

        # ajouter le label du titre en premier
        if self.displayTitle:
            self.labelTitle = QtWidgets.QLabel(self)
            self.labelTitle.setText(self.textTitle)
            # Styles applied via onTextAspectsChanged
            self.labels.append(self.labelTitle)
            self.layout.addWidget(self.labelTitle)
            # The label of indicators are added afterwards
            self.updateLabelsandWidgetSize() # adjust sizes  
            #set layout
            self.setLayout(self.layout)
        # else:
        #     self.updateLabelsandWidgetSize()
        #     self.setLayout(self.layout)

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

        # Apply text aspects now that widgets exist
        self.onTextAspectsChanged()


    def addIndicator(self, name,method,attribute=None,value=None,color=Qt.black,logicOp=None,title=None,displayRefresh="instantaneous",onTimeConditions=None,isDisplay=True, displayName=True, conditionsOnEntities=[]):
        """
        Add an Indicator on the DashBoard.

        Args:
            name (str) :  aEntityType name, or aEntityType, of a List of EntityType or names, or None (only for score)
            method (str) : name of the method in ["sumAtt","avgAtt","minAtt","maxAtt","nb","nbWithLess","nbWithMore","nbEqualTo","thresoldToLogicOp","score"].
            attribute (str) : concerned attribute 
            value (str, optional) : concerned value
            color (Qt.color) : text color
            logicOp (str, optional) : only if method = thresoldToLogicOp, logical connector in ["greater","greater or equal","equal", "less or equal","less"]
            title (str, optional) : name displayed on the dashboard
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
        if isinstance(name,str) :
            resEntDef = self.model.getEntityType(name)
            if resEntDef is None: raise ValueError('Wrong type')  
            listOfEntTypes = [resEntDef]
        elif isinstance(name,SGEntityType) :
            listOfEntTypes = [name]
        elif name is None :
            listOfEntTypes = None
        elif isinstance(name,list) and isinstance(name[0],str) :
            listOfEntTypes = [self.model.getEntityType(aEntName) for aEntName in name]
        elif isinstance(name,list) and isinstance(name[0],SGEntityType) :
            listOfEntTypes = name
        elif issubclass(type(name), SGEntity): # A PRIORI CE CAS NE SE PRESENTE JAMAIS CAR dans ce genre cas, on utilise la méthode addIndicatorOnEntity()
            listOfEntTypes = name
        else:
            raise ValueError('Wrong type')
        
        indicator = SGIndicator(self, title, method, attribute, value, listOfEntTypes, logicOp, color,displayRefresh,onTimeConditions,isDisplay,displayName,conditionsOnEntities=conditionsOnEntities)
        self.indicators.append(indicator)
        indicator.id = self.IDincr
        self.IDincr = +1
        if method != "separator":
            for type in listOfEntTypes:
                type.addWatcher(indicator)
        return indicator
    

    def addIndicatorOnEntity(self, entity, attribute, color=Qt.black, value=None, logicOp=None, title=None, displayRefresh="instantaneous", onTimeConditions= None, isDisplay=True, displayName=True, conditionsOnEntities=[]):
        """
        Add an Indicator on a particular entity on the DashBoard.

        Two usages are possible:
         - Show the value of an attribute. Example: dashBoard.addIndicatorOnEntity(aEntity, 'landUse').
         - Show True or False depending on a logical test on an attribute value (logicOp and value need to be defined). Example: addIndicatorOnEntity(aEntity, 'landUse', logicOp='equal', value='forest').

        Args:
            entity (SGEntity): An entity (cell or agent).
            attribute (str): The concerned attribute.
            color (Qt.color): The text color (default is Qt.black).
            value (optional): The value to compare against for logical tests.
            logicOp (str, optional): The logical operator for the test performed. Possible values: "greater", "greater or equal", "equal", "less or equal", "less".
            threshold (str, optional): The threshold value for logical tests.
            title (str, optional): The name displayed on the dashboard.
            displayRefresh (str, optional): Determines how the display is refreshed (e.g., "instantaneous", "onTimeConditions").
            isDisplay (bool, optional): Whether to display on the dashboard (default is True).
        """
        if not isinstance(entity,(SGEntity,SGEntityType,SGPlayer,SGCell)): raise ValueError ('Wrong entity format')
        self.entity= entity

        if value is None:
            method = "display"
        else:
            if logicOp is not None:
                method = "thresoldToLogicOp"
            else:
                raise ValueError("You need to specify a logicOp")
        
        self.posYOfItems = self.posYOfItems+1
    
        # indicator = SGIndicator(self, title, method, attribute, value, entity, logicOp, color, displayRefresh, isDisplay, displayName, conditionsOnEntities)
        indicator = SGIndicator(self, title, method, attribute, value, entity, color=color,logicOp=None,displayRefresh=displayRefresh, onTimeConditions=onTimeConditions,isDisplay=isDisplay,displayName=displayName,conditionsOnEntities=conditionsOnEntities)
        self.indicators.append(indicator)
        indicator.id = self.IDincr
        self.IDincr = +1
        
        entity.addWatcher(indicator)

        return indicator

    def addIndicatorOnSimVariable(self,aSimulationVariable,displayRefresh="instantaneous", displayName=True, conditionsOnEntities=[]):
        self.posYOfItems = self.posYOfItems+1
        indicator=SGIndicator(self,aSimulationVariable.name,"simVar",None,aSimulationVariable.value,aSimulationVariable,None,aSimulationVariable.color,displayRefresh,None,aSimulationVariable.isDisplay,displayName=displayName,conditionsOnEntities=conditionsOnEntities)
        self.indicators.append(indicator)
        indicator.id = self.IDincr
        self.IDincr = +1

        aSimulationVariable.addWatcher(indicator)
    
        return indicator

    def addIndicator_Sum(self, entity, attribute,title=None, color=Qt.black, displayRefresh="instantaneous", isDisplay=True, displayName=True, conditionsOnEntities=[]):
        """
        Add a sum indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            title (str, optional) : name displayed on the dashboard
            color (Qt.color) : text color
            displayRefresh (str) :
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'sumAtt'
        indicator = self.addIndicator(entity,method,attribute,value=None,color=color,logicOp=None,title=title,displayRefresh=displayRefresh,isDisplay=isDisplay,displayName=displayName,conditionsOnEntities=conditionsOnEntities)
        return indicator

    def addIndicator_Avg(self, entity, attribute, title, color,displayRefresh="instantaneous",isDisplay=True, displayName=True, conditionsOnEntities=[]):
        """
        Add a average indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            title (str, optional) : name displayed on the dashboard
            color (Qt.color) : text color
            displayRefresh (str) :
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'avgAtt'
        indicator = self.addIndicator(entity,method,attribute,value=None,color=color,logicOp=None,title=title,displayRefresh=displayRefresh,isDisplay=isDisplay,displayName=displayName,conditionsOnEntities=conditionsOnEntities)
        return indicator

    def addIndicator_Min(self, entity, attribute, title, color,displayRefresh="instantaneous",isDisplay=True, displayName=True, conditionsOnEntities=[]):
        """
        Add a minimum indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            title (str, optional) : name displayed on the dashboard
            color (Qt.color) : text color
            displayRefresh (str) :
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'minAtt'
        indicator = self.addIndicator(entity,method,attribute,value=None,color=color,logicOp=None,title=title,displayRefresh=displayRefresh,isDisplay=isDisplay,displayName=displayName,conditionsOnEntities=conditionsOnEntities)
        return indicator

    def addIndicator_Max(self, entity, attribute,title, color,displayRefresh="instantaneous",isDisplay=True, displayName=True, conditionsOnEntities=[]):
        """
        Add a maximum indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            title (str, optional) : name displayed on the dashboard
            color (Qt.color) : text color
            displayRefresh (str) :
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'maxAtt'
        indicator = self.addIndicator(entity,method,attribute,value=None,color=color,logicOp=None,title=title,displayRefresh=displayRefresh,isDisplay=isDisplay,displayName=displayName,conditionsOnEntities=conditionsOnEntities)
        return indicator

    def addIndicator_EqualTo(self, entity, attribute, value, title, color,displayRefresh="instantaneous",isDisplay=True, displayName=True):
        """
        Add a equal to indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            value (str) : value to do the logical test
            title (str, optional) : name displayed on the dashboard
            color (Qt.color) : text color
            displayRefresh (str) :
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'nbEqualTo'
        indicator = self.addIndicator(entity,method,attribute,value,color,logicOp=None,title=title,displayRefresh=displayRefresh,isDisplay=isDisplay,displayName=displayName)
        return indicator

    def addIndicator_WithLess(self, entity, attribute, value, title, color,displayRefresh="instantaneous",isDisplay=True, displayName=True):
        """
        Add a with less indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            value (str) : value to do the logical test
            title (str, optional) : name displayed on the dashboard
            color (Qt.color) : text color
            displayRefresh (str) :
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'nbWithLess'
        indicator = self.addIndicator(entity,method,attribute,value,color,logicOp=None,title=title,displayRefresh=displayRefresh,isDisplay=isDisplay,displayName=displayName)
        return indicator

    def addIndicator_WithMore(self, entity, attribute, value, title, color,displayRefresh="instantaneous",isDisplay=True, displayName=True):
        """
        Add a with more indicator
        Args :
            entity (str) : "cell"
            attribute (str) : concerned attribute 
            value (str) : for certain methods, a value is required
            title (str, optional) : name displayed on the dashboard
            color (Qt.color) : text color
            displayRefresh (str) :
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'nbWithMore'
        indicator = self.addIndicator(entity,method,attribute,value,color,logicOp=None,title=title,displayRefresh=displayRefresh,isDisplay=isDisplay,displayName=displayName)
        return indicator

    def addIndicator_Nb(self, entity, attribute, value, title, color,displayRefresh="instantaneous",isDisplay=True, displayName=True):
        """
        Add a sum indicator
        Args :
            entity (str) : "cell" or "agent" or aAgentType
            attribute (str) : concerned attribute 
            title (str, optional) : name displayed on the dashboard
            color (Qt.color) : text color
            displayRefresh (str) :
            isDisplay (bool) : display on the dashboard (default : True)
        """
        method = 'nb'
        indicator = self.addIndicator(entity,method,attribute,value,color=color,logicOp=None,title=title,displayRefresh=displayRefresh,isDisplay=isDisplay,displayName=displayName)
        return indicator
    
    def addSeparator(self):
        separator=self.addIndicator(None,"separator")
        return separator


#############################
        # Drawing the DB
    def paintEvent(self, event):
        if self.isDisplay:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing, True)
            # Background: prefer image, else color with transparency
            bg_pixmap = self.getBackgroundImagePixmap()
            if bg_pixmap is not None:
                rect = QRect(0, 0, self.width(), self.height())
                painter.drawPixmap(rect, bg_pixmap)
            else:
                bg = self.gs_aspect.getBackgroundColorValue()
                if bg.alpha() == 0:
                    painter.setBrush(Qt.NoBrush)
                else:
                    painter.setBrush(QBrush(bg, Qt.SolidPattern))
            # Border with style mapping
            pen = QPen(self.gs_aspect.getBorderColorValue(), self.gs_aspect.getBorderSize())
            style_map = {
                'solid': Qt.SolidLine,
                'dotted': Qt.DotLine,
                'dashed': Qt.DashLine,
                'double': Qt.SolidLine,
                'groove': Qt.SolidLine,
                'ridge': Qt.SolidLine,
                'inset': Qt.SolidLine,
            }
            bs = getattr(self.gs_aspect, 'border_style', None)
            if isinstance(bs, str) and bs.lower() in style_map:
                pen.setStyle(style_map[bs.lower()])
            painter.setPen(pen)
            radius = getattr(self.gs_aspect, 'border_radius', None) or 0
            w = max(0, self.getSizeXGlobal()-1)
            h = max(0, self.getSizeYGlobal()-1)
            if radius > 0:
                painter.drawRoundedRect(0, 0, w, h, radius, radius)
            else:
                painter.drawRect(0, 0, w, h)

    def updateLabelsandWidgetSize(self):
        # Prefer layout-based sizing to include layout margins/paddings
        if hasattr(self, 'layout') and self.layout is not None:
            self.updateSizeFromLayout(self.layout)
        else:
            self.updateSizeFromLabels(self.labels)
    

    def getSizeXGlobal(self):
        return getattr(self, 'sizeXGlobal', 10)
    
    def getSizeYGlobal(self):
        return getattr(self, 'sizeYGlobal', 10)

    # ============================================================================
    # MODELER METHODS
    # ============================================================================
    
    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================
    
    def setTitleText(self, text):
        """
        Set the title text of the dashboard.
        
        Args:
            text (str): The title text
        """
        self.textTitle = text
        if hasattr(self, 'labelTitle') and self.labelTitle:
            self.labelTitle.setText(text)
            self.labelTitle.adjustSize()
        self.update()

    # =========================
    # STYLE/APPLY HOOKS
    # =========================
    def applyContainerAspectStyle(self):
        """Avoid QSS cascade; rely on paintEvent for container rendering."""
        pass

    def onTextAspectsChanged(self):
        # Apply title1 to title
        def _apply_weight_to_font(font_obj: QFont, weight_value):
            try:
                self.applyFontWeightToQFont(font_obj, weight_value)
            except Exception:
                pass
        if hasattr(self, 'labelTitle') and self.labelTitle is not None:
            css_parts = []
            if self.title1_aspect.color:
                css_parts.append(f"color: {QColor(self.title1_aspect.color).name()}")
            td = getattr(self.title1_aspect, 'text_decoration', None)
            css_parts.append(f"text-decoration: {td}" if td and str(td).lower() != 'none' else "text-decoration: none")
            f = self.labelTitle.font()
            if self.title1_aspect.font:
                f.setFamily(self.title1_aspect.font)
            if self.title1_aspect.size:
                try:
                    f.setPixelSize(int(self.title1_aspect.size))
                except Exception:
                    pass
            _apply_weight_to_font(f, getattr(self.title1_aspect, 'font_weight', None))
            if self.title1_aspect.font_style:
                s = str(self.title1_aspect.font_style).lower()
                f.setItalic(s in ('italic', 'oblique'))
            self.labelTitle.setFont(f)
            self.labelTitle.setStyleSheet("; ".join(css_parts))
            # Alignment from title1_aspect
            try:
                al = getattr(self.title1_aspect, 'alignment', None)
                if isinstance(al, str) and al:
                    a = al.strip().lower()
                    align_map = {
                        'left': Qt.AlignLeft,
                        'right': Qt.AlignRight,
                        'center': Qt.AlignHCenter,
                        'hcenter': Qt.AlignHCenter,
                        'top': Qt.AlignTop,
                        'bottom': Qt.AlignBottom,
                        'vcenter': Qt.AlignVCenter,
                        'justify': Qt.AlignJustify,
                    }
                    if a in align_map:
                        self.labelTitle.setAlignment(align_map[a])
            except Exception:
                pass
        # Apply text1 to indicators labels
        for ind in self.indicators:
            if hasattr(ind, 'label') and ind.label:
                lbl = ind.label
                css_parts = []
                if self.text1_aspect.color:
                    css_parts.append(f"color: {QColor(self.text1_aspect.color).name()}")
                td = getattr(self.text1_aspect, 'text_decoration', None)
                css_parts.append(f"text-decoration: {td}" if td and str(td).lower() != 'none' else "text-decoration: none")
                f = lbl.font()
                if self.text1_aspect.font:
                    f.setFamily(self.text1_aspect.font)
                if self.text1_aspect.size:
                    try:
                        f.setPixelSize(int(self.text1_aspect.size))
                    except Exception:
                        pass
                _apply_weight_to_font(f, getattr(self.text1_aspect, 'font_weight', None))
                if self.text1_aspect.font_style:
                    s = str(self.text1_aspect.font_style).lower()
                    f.setItalic(s in ('italic', 'oblique'))
                lbl.setFont(f)
                lbl.setStyleSheet("; ".join(css_parts))
                # Alignment from text1_aspect
                try:
                    al = getattr(self.text1_aspect, 'alignment', None)
                    if isinstance(al, str) and al:
                        a = al.strip().lower()
                        align_map = {
                            'left': Qt.AlignLeft,
                            'right': Qt.AlignRight,
                            'center': Qt.AlignHCenter,
                            'hcenter': Qt.AlignHCenter,
                            'top': Qt.AlignTop,
                            'bottom': Qt.AlignBottom,
                            'vcenter': Qt.AlignVCenter,
                            'justify': Qt.AlignJustify,
                        }
                        if a in align_map:
                            lbl.setAlignment(align_map[a])
                except Exception:
                    pass

        # Resize
        self.updateLabelsandWidgetSize()
        self.update()
        
    def setDisplayTitle(self, display):
        """
        Set whether to display the title.
        
        Args:
            display (bool): Whether to display the title
        """
        self.displayTitle = display
        if hasattr(self, 'labelTitle') and self.labelTitle:
            self.labelTitle.setVisible(display)
        self.update()
        
    def setLayoutOrientation(self, orientation):
        """
        Set the layout orientation of the dashboard.
        
        Args:
            orientation (str): 'vertical' or 'horizontal'
        """
        if orientation in ['vertical', 'horizontal']:
            # Recreate layout with new orientation
            if orientation == 'vertical':
                self.layout = QtWidgets.QVBoxLayout()
            else:
                self.layout = QtWidgets.QHBoxLayout()
            
            # Re-add all widgets to new layout
            if self.displayTitle and hasattr(self, 'labelTitle'):
                self.layout.addWidget(self.labelTitle)
            for indicator in self.indicators:
                if indicator.isDisplay and hasattr(indicator, 'label'):
                    self.layout.addWidget(indicator.label)
            
            self.setLayout(self.layout)
            self.updateLabelsandWidgetSize()
        else:
            raise ValueError("Orientation must be 'vertical' or 'horizontal'")
        
    def setIndicatorStyle(self, style_dict):
        """
        Set the style of all indicators.
        
        Args:
            style_dict (dict): Dictionary of style properties for indicators
        """
        for indicator in self.indicators:
            if hasattr(indicator, 'label') and indicator.label:
                style_parts = []
                for key, value in style_dict.items():
                    if key == 'color':
                        style_parts.append(f"color: {value}")
                    elif key == 'font_size':
                        style_parts.append(f"font-size: {value}px")
                    elif key == 'font_family':
                        style_parts.append(f"font-family: {value}")
                    elif key == 'font_weight':
                        style_parts.append(f"font-weight: {value}")
                
                if style_parts:
                    indicator.label.setStyleSheet("; ".join(style_parts))
        self.updateLabelsandWidgetSize()
        self.update()

    
