from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QToolTip
from mainClasses.SGAspect import *
from mainClasses.SGGameSpaceSizeManager import SGGameSpaceSizeManager
from mainClasses.SGEventHandlerGuide import *


            
class SGGameSpace(QtWidgets.QWidget,SGEventHandlerGuide):
    def __init__(self,parent,startXBase,startYBase,posXInLayout,posYInLayout,isDraggable=True,backgroundColor=Qt.gray,forceDisplay=False):
        super().__init__(parent)
        self.model=parent
        
        # Type identification attributes
        self.isCellType = False
        self.isAgentType = False
        self.isAGrid = False

        self.posXInLayout=posXInLayout
        self.posYInLayout=posYInLayout
        self.positionDefineByModeler = None
        self.startXBase=startXBase
        self.startYBase=startYBase
        self.isDraggable = isDraggable
        self.isActive = True
        self.forceDisplay = forceDisplay
        
        # Enable drag and drop functionality
        self.setAcceptDrops(True)
        self.drag_start_position = None
        self.dragging = False
        self._drag_mode_changed = False  # Flag to track if mode was changed during current drag
        self.rightMargin = 9
        self.verticalGapBetweenLabels = 5
        self.gs_aspect = SGAspect.baseBorder()
        self.gs_aspect.background_color = backgroundColor
        self.title1_aspect = SGAspect.title1()
        self.title2_aspect = SGAspect.title2()
        self.title3_aspect = SGAspect.title3()
        self.text1_aspect = SGAspect.text1()
        self.text2_aspect = SGAspect.text2()
        self.text3_aspect = SGAspect.text3()
        # Size manager for game_spaces
        self.size_manager = SGGameSpaceSizeManager()
        # Assign the unique ID to the instance
        self.id = self.__class__.nextId()
        # QSS object name (avoid '#') for id-specific styling on container only
        self._qss_object_name = self.id.replace('#', '_')
        self.setObjectName(self._qss_object_name)
        # Theme tracking
        self.current_theme_name = None
        self.theme_overridden = False
        
        # Enhanced Grid Layout system
        self.layoutOrder = None  # Position ID for Enhanced Grid Layout
        self.is_layout_repositioned = False  # Flag for manual repositioning after automatic layout
        self._positionType = "layoutOrder"  # State: "absolute", "mixed", or "layoutOrder"
        self._enhanced_grid_tooltip_enabled = False  # Flag for layoutOrder tooltip display
        

    @classmethod
    def nextId(cls):
        """
        Generates the next unique identifier for this type of GameSpace.
        
        Returns:
            str: A unique identifier in the form 'TypeGameSpace#N'
        """
        if not hasattr(cls, '_nextId'):
            cls._nextId = 0
        cls._nextId += 1
        return f"{cls.__name__}#{cls._nextId}"
               
    #Funtion to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        pass
    
    def getSizeYGlobal(self):
        pass
    
    #Funtion to handle the zoom
    def zoomIn(self):
        pass
    
    def zoomOut(self):
        pass
    
    #To choose the inital pov when the game start
    def displayPov(self,nameOfPov):
        pass
    
    
    #The setters
    def setStartXBase(self,number):
        self.startXBase = number
    
    def setStartYBase(self,number):
        self.startYBase = number
    
    def isPositionDefineByModeler(self):
        return self.positionDefineByModeler != None
    
    #Calculate the area
    def areaCalc(self):
        self.area = float(self.width() * self.height())
        return self.area


    def mousePressEvent(self, event):
        """
        Handle mouse press events for drag initiation.
        """
        if event.button() == Qt.LeftButton and self.isDraggable:
            # Store the initial click position relative to the widget
            self.drag_start_position = event.pos()
            self.dragging = True
        else:
            self.dragging = False

    def mouseReleaseEvent(self, event):
        """
        Handle mouse release events to end drag operation.
        """
        if event.button() == Qt.LeftButton and self.isDraggable:
            self.dragging = False
            # Reset the drag mode change flag for next drag operation
            self._drag_mode_changed = False
    
    def event(self, event):
        """
        Handle events including tooltip display for layoutOrder
        """
        if event.type() == QEvent.ToolTip:
            # Check if layoutOrder tooltips are enabled
            if (hasattr(self, '_enhanced_grid_tooltip_enabled') and 
                self._enhanced_grid_tooltip_enabled and 
                self.layoutOrder is not None):
                
                # Show layoutOrder tooltip
                if self.layoutOrder == "manual_position":
                    QToolTip.showText(event.globalPos(), "Position set manually")
                else:
                    QToolTip.showText(event.globalPos(), f"Order: {self.layoutOrder}")
                return True
            else:
                # Let parent handle tooltip (for entity tooltips)
                return super().event(event)
        
        return super().event(event)

    def mouseMoveEvent(self, event):
        """
        Handle mouse move events for dragging gameSpaces.
        """
        # Only proceed if left button is pressed and widget is draggable
        if not (event.buttons() == Qt.LeftButton and self.isDraggable and self.dragging):
            return

        # Check if we've moved enough to start a drag operation
        # Calculate distance moved
        distance = (event.pos() - self.drag_start_position).manhattanLength()
        if distance < QtWidgets.QApplication.startDragDistance():
            return

        # Check if this is the first significant movement and we need to change mode
        if not self._drag_mode_changed and self._positionType == "layoutOrder":
            # GameSpace was in layoutOrder mode and is being dragged manually
            self.setToMixed()
            self._drag_mode_changed = True

        # Get the global mouse position
        global_mouse_pos = QtWidgets.QApplication.desktop().cursor().pos()
        
        # Convert to parent coordinates
        if self.parent():
            parent_pos = self.parent().mapFromGlobal(global_mouse_pos)
            
            # Calculate new position accounting for the click offset
            new_x = parent_pos.x() - self.drag_start_position.x()
            new_y = parent_pos.y() - self.drag_start_position.y()
            
            # Move the widget
            self.move(new_x, new_y)
            
            # Update the gameSpace's base position
            self.setStartXBase(new_x)
            self.setStartYBase(new_y)

        # Don't reset dragging here - keep it true for continuous movement


#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use

    #Funtion to have the global size of a gameSpace  
    def setDraggability(self,aBoolean):
        self.isDraggable=aBoolean
        
        
    #Function to change the order in the layout
    def setInPosition(self,x,y):
        x=x-1
        y=y-1
        self.posXInLayout=x
        self.posYInLayout=y

    #Function to move a GameSpace in the model window
    def moveToCoords(self,x,y=None):
        """
        Permits to move a GameSpace at a specific coordinate based on the left upper corner

        Args:
            x (int) : x-axis coordinate in pixels
            y (int) : y-axis coordinate in pixels
        """
        if y is None :
            if not isinstance(x, tuple):
                raise ValueError('Wrong format: x must be a coordinate tuple (x,y).')
            else:
                y = x[1]
                x = x[0]
                
        if x < self.model.width() + self.width() or x < 0:
            if y < self.model.height() + self.height() or y < 0:
                self.positionDefineByModeler=(x,y)
                self.move(x,y)
                
                # If using Enhanced Grid Layout, set to absolute position type
                if (hasattr(self.model, 'typeOfLayout') and 
                    self.model.typeOfLayout == "enhanced_grid" and
                    hasattr(self.model, 'layoutOfModel')):
                    self.setToAbsolute()
            else:
                raise ValueError('The y value is too high or negative')
        else:
            raise ValueError('The x value is too high or negative')
    
    #Function to set the color of the background of the gameSpace 
    def setColor(self,aColor):
        self.gs_aspect.background_color=aColor
        self.theme_overridden = True
        
        
    def setTitlesAndTextsColor(self, textColor):
        self.setTitlesColor(textColor)
        self.setTextsColor(textColor)
        self.theme_overridden = True

    # Apply textColor to each title
    def setTitlesColor(self, textColor):
        for aspect in [self.title1_aspect, self.title2_aspect, self.title3_aspect]:
            aspect.color = textColor  
        self.theme_overridden = True

    # Apply textColor to each text
    def setTextsColor(self, textColor):
        for aspect in [self.text1_aspect, self.text2_aspect, self.text3_aspect]:
            aspect.color = textColor 
        self.theme_overridden = True
    
    # ============================================================================
    # SIZE MANAGEMENT METHODS
    # ============================================================================
    
    def adjustSizeToContent(self, content_widgets=None, content_items=None, text_content=None, font=None):
        """
        Adjust game_space size to its content using the size_manager.
        
        Args:
            content_widgets (list, optional): Content widgets
            content_items (list, optional): Content items  
            text_content (str, optional): Text content
            font (QFont, optional): Font to use for text height calculation
        """
        self.size_manager.adjust_game_space_to_content(
            self, content_widgets, content_items, text_content, font
        )
    
    def calculateContentWidth(self, content_widgets=None, text_content=None):
        """
        Calculate necessary width for content.
        
        Args:
            content_widgets (list, optional): Content widgets
            text_content (str, optional): Text content
            
        Returns:
            int: Calculated width in pixels
        """
        if content_widgets:
            return self.size_manager.calculate_content_width(content_widgets)
        elif text_content:
            return self.size_manager.calculate_text_width(text_content)
        else:
            return self.size_manager.min_width
    
    def calculateContentHeight(self, content_items=None, text_content=None, font=None):
        """
        Calculate necessary height for content.
        
        Args:
            content_items (list, optional): Content items
            text_content (str, optional): Text content
            font (QFont, optional): Font to use for text height calculation
            
        Returns:
            int: Calculated height in pixels
        """
        if content_items:
            return self.size_manager.calculate_content_height(content_items)
        elif text_content:
            return self.size_manager.calculate_text_height(text_content, font)
        else:
            return self.size_manager.min_height
    
    def setSizeManagerMargin(self, margin):
        """
        Set right margin of size_manager.
        
        Args:
            margin (int): New margin in pixels
        """
        self.size_manager.set_right_margin(margin)
    
    def setLayoutOrder(self, order):
        """
        Set the layoutOrder for this gameSpace in Enhanced Grid Layout.
        
        Args:
            order (int or str): The layout order value. Use None for auto-assignment.
                               Use "manual_position" for manually positioned gameSpaces.
        
        Example:
            grid.setLayoutOrder(1)  # Set grid as first in layout
            legend.setLayoutOrder(3)  # Set legend as third in layout
            dashboard.setLayoutOrder(None)  # Reset to auto-assignment
        """
        if order is None:
            # Reset to auto-assignment
            self.layoutOrder = None
            self._positionType = "layoutOrder"
            self.is_layout_repositioned = False
        elif order == "manual_position":
            # Mark as manually positioned
            self.setToAbsolute()
        else:
            # Set specific layoutOrder
            self.setToLayoutOrder(order)

    def setToAbsolute(self):
        """
        Set gameSpace to absolute positioning mode.
        """
        self.layoutOrder = "manual_position"
        self._positionType = "absolute"
        self.is_layout_repositioned = False
        self.positionDefineByModeler = [self.x(), self.y()]

    def setToLayoutOrder(self, order, update_layout_tracking=True):
        """
        Set gameSpace to layout order positioning mode.
        
        Args:
            order (int): The layout order value
            update_layout_tracking (bool): Whether to update layout tracking (default True)
        """
        self.layoutOrder = order
        self._positionType = "layoutOrder"
        self.is_layout_repositioned = False
        self.positionDefineByModeler = None
        
        # Update the layout's tracking if we have a model and tracking is enabled
        if update_layout_tracking and hasattr(self, 'model') and self.model and hasattr(self.model, 'layoutOfModel'):
            if hasattr(self.model.layoutOfModel, 'used_layoutOrders'):
                self.model.layoutOfModel.used_layoutOrders.add(order)
                # Update next_layoutOrder counter
                if hasattr(self.model.layoutOfModel, 'next_layoutOrder'):
                    self.model.layoutOfModel.next_layoutOrder = max(
                        self.model.layoutOfModel.next_layoutOrder, 
                        order + 1
                    )
                
                # Trigger layout recalculation
                if hasattr(self.model, 'applyAutomaticLayout'):
                    self.model.layoutOfModel.reorderByLayoutOrder()
                    self.model.applyAutomaticLayout()

    def setToMixed(self):
        """
        Set gameSpace to mixed positioning mode (repositioned after automatic layout).
        """
        self._positionType = "mixed"
        self.is_layout_repositioned = True

    def getPositionType(self):
        """
        Get the current position type of the gameSpace.
        
        Returns:
            str: "absolute", "mixed", or "layoutOrder"
        """
        return self._positionType

    def setSizeManagerVerticalGap(self, gap):
        """
        Set vertical spacing of size_manager.
        
        Args:
            gap (int): New spacing in pixels
        """
        self.size_manager.set_vertical_gap(gap)

    # ============================================================================
    # MODELER METHODS
    # ============================================================================
    
    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================
    
    def setBorderColor(self, color):
        """
        Set the border color of the gameSpace.
        
        Args:
            color (QColor or Qt.GlobalColor): The border color
        """
        self.gs_aspect.border_color = color
        self.applyContainerAspectStyle()
        self.update()
        self.theme_overridden = True
        
    def setBorderSize(self, size):
        """
        Set the border size of the gameSpace.
        
        Args:
            size (int): The border size in pixels
        """
        self.gs_aspect.border_size = size
        self.applyContainerAspectStyle()
        self.update()
        self.theme_overridden = True
        
    def setBackgroundColor(self, color):
        """
        Set the background color of the gameSpace.
        
        Args:
            color (QColor or Qt.GlobalColor): The background color
        """
        self.gs_aspect.background_color = color
        self.applyContainerAspectStyle()
        self.update()
        self.theme_overridden = True
        
    def setTextColor(self, color):
        """
        Set the text color of the gameSpace.
        
        Args:
            color (QColor or Qt.GlobalColor): The text color
        """
        self.gs_aspect.color = color
        self.setTitlesAndTextsColor(color)
        self.update()
        self.theme_overridden = True
        
    def setTitleAlignment(self, alignment):
        """
        Set the title alignment of the gameSpace.
        
        Args:
            alignment (str): The title alignment ('left', 'center', 'right')
        """
        self.gs_aspect.alignment = alignment
        self.update()
        self.theme_overridden = True
        
    def setFontFamily(self, font_family):
        """
        Set the font family of the gameSpace.
        
        Args:
            font_family (str): The font family name
        """
        for aspect in [self.title1_aspect, self.title2_aspect, self.title3_aspect, 
                      self.text1_aspect, self.text2_aspect, self.text3_aspect]:
            aspect.font = font_family
        self.update()
        self.theme_overridden = True
        
    def setFontSize(self, size):
        """
        Set the font size of the gameSpace.
        
        Args:
            size (int): The font size in pixels
        """
        self.gs_aspect.size = size
        for aspect in [self.title1_aspect, self.title2_aspect, self.title3_aspect, 
                      self.text1_aspect, self.text2_aspect, self.text3_aspect]:
            aspect.size = size
        self.update()
        self.theme_overridden = True
        
    def setFontWeight(self, weight):
        """
        Set the font weight of the gameSpace.
        
        Args:
            weight (str): The font weight ('normal', 'bold', etc.)
        """
        self.gs_aspect.font_weight = weight
        for aspect in [self.title1_aspect, self.title2_aspect, self.title3_aspect, 
                      self.text1_aspect, self.text2_aspect, self.text3_aspect]:
            aspect.font_weight = weight
        self.update()
        self.theme_overridden = True
        
    def setFontStyle(self, style):
        """
        Set the font style of the gameSpace.
        
        Args:
            style (str): The font style ('normal', 'italic', 'oblique')
        """
        for aspect in [self.title1_aspect, self.title2_aspect, self.title3_aspect, 
                      self.text1_aspect, self.text2_aspect, self.text3_aspect]:
            aspect.font_style = style
        self.update()
        self.theme_overridden = True
        
    def setBorderRadius(self, radius):
        """
        Set the border radius of the gameSpace.
        
        Args:
            radius (int): The border radius in pixels
        """
        self.gs_aspect.border_radius = radius
        self.applyContainerAspectStyle()
        self.update()
        self.theme_overridden = True
        
    def setPadding(self, padding):
        """
        Set the padding of the gameSpace.
        
        Args:
            padding (int): The padding in pixels
        """
        self.gs_aspect.padding = padding
        self.applyContainerAspectStyle()
        self.update()
        self.theme_overridden = True
        
    def setMinWidth(self, width):
        """
        Set the minimum width of the gameSpace.
        
        Args:
            width (int): The minimum width in pixels
        """
        self.gs_aspect.min_width = width
        self.update()
        self.theme_overridden = True
        
    def setMinHeight(self, height):
        """
        Set the minimum height of the gameSpace.
        
        Args:
            height (int): The minimum height in pixels
        """
        self.gs_aspect.min_height = height
        self.update()
        self.theme_overridden = True
        
    def setWordWrap(self, wrap):
        """
        Set the word wrap of the gameSpace.
        
        Args:
            wrap (bool): Whether to enable word wrap
        """
        self.gs_aspect.word_wrap = wrap
        self.update()
        self.theme_overridden = True
        
    def setBackgroundImage(self, image_path):
        """
        Set the background image of the gameSpace.
        
        Args:
            image_path (str): The path to the background image
        """
        self.gs_aspect.background_image = image_path
        self.update()
        self.theme_overridden = True
        
    def setStyle(self, style_dict):
        """
        Set multiple style properties at once.
        
        Args:
            style_dict (dict): Dictionary of style properties
        """
        for key, value in style_dict.items():
            if hasattr(self, f'set{key.title()}'):
                getattr(self, f'set{key.title()}')(value)
            elif key == 'border_color':
                self.setBorderColor(value)
            elif key == 'border_size':
                self.setBorderSize(value)
            elif key == 'background_color':
                self.setBackgroundColor(value)
            elif key == 'text_color':
                self.setTextColor(value)
            elif key == 'title_alignment':
                self.setTitleAlignment(value)
            elif key == 'font_family':
                self.setFontFamily(value)
            elif key == 'font_size':
                self.setFontSize(value)
            elif key == 'font_weight':
                self.setFontWeight(value)
            elif key == 'font_style':
                self.setFontStyle(value)
            elif key == 'border_radius':
                self.setBorderRadius(value)
            elif key == 'padding':
                self.setPadding(value)
            elif key == 'min_width':
                self.setMinWidth(value)
            elif key == 'min_height':
                self.setMinHeight(value)
            elif key == 'word_wrap':
                self.setWordWrap(value)
            elif key == 'background_image':
                self.setBackgroundImage(value)
        self.applyContainerAspectStyle()
        self.update()

    # =========================
    # SIZE UPDATE UTILITIES
    # =========================
    def updateSizeFromLayout(self, layout):
        """Generic helper to resize the GameSpace from a Qt layout sizeHint.

        Adds margins using SGGameSpaceSizeManager when available, otherwise
        falls back to local attributes (rightMargin, verticalGapBetweenLabels).
        """
        if not layout:
            return
        try:
            layout.activate()
            size_hint = layout.sizeHint()
            if size_hint and size_hint.isValid():
                right_margin = getattr(getattr(self, 'size_manager', None), 'right_margin', getattr(self, 'rightMargin', 0))
                vertical_gap = getattr(getattr(self, 'size_manager', None), 'vertical_gap_between_labels', getattr(self, 'verticalGapBetweenLabels', 0))
                border_padding = getattr(getattr(self, 'size_manager', None), 'border_padding', 0)
                width = size_hint.width() + right_margin + border_padding
                height = size_hint.height() + vertical_gap + border_padding
                # Propagate computed sizes to attributes used by paintEvent/getters
                self.sizeXGlobal = width
                self.sizeYGlobal = height
                self.setMinimumSize(width, height)
                self.resize(width, height)
        except Exception:
            pass

    def updateSizeFromLabels(self, labels):
        """Generic helper to resize the GameSpace from a list of QLabel/QWidget.

        Mirrors SGTimeLabel.updateLabelsandWidgetSize().
        """
        if not labels:
            return
        try:
            for w in labels:
                if hasattr(w, 'fontMetrics') and hasattr(w, 'text'):
                    fm = w.fontMetrics()
                    br = fm.boundingRect(w.text())
                    w.setFixedWidth(br.width())
                    w.setFixedHeight(br.height())
                if hasattr(w, 'adjustSize'):
                    w.adjustSize()

            try:
                max_right = max(w.geometry().right() for w in labels)
            except Exception:
                max_right = sum((w.sizeHint().width() for w in labels if w.sizeHint().isValid()), 0)

            try:
                total_height = sum((w.height() for w in labels))
            except Exception:
                total_height = sum((w.sizeHint().height() for w in labels if w.sizeHint().isValid()), 0)

            right_margin = getattr(self, 'rightMargin', getattr(getattr(self, 'size_manager', None), 'right_margin', 0))
            vertical_gap = getattr(self, 'verticalGapBetweenLabels', getattr(getattr(self, 'size_manager', None), 'vertical_gap_between_labels', 0))
            num = len([w for w in labels])

            width = max_right + right_margin
            # Add vertical gap between rows and a bottom margin (gap) similar to previous behavior
            height = total_height + vertical_gap * (num + 1)
            # Propagate computed sizes to attributes used by paintEvent/getters
            self.sizeXGlobal = width
            self.sizeYGlobal = height
            self.setFixedSize(QSize(width, height))
        except Exception:
            pass
    def _getContainerStyle(self):
        """Build Qt stylesheet string limited to container (no text/font properties)."""
        style_parts = []
        # Background
        if self.gs_aspect.background_color:
            css_color = SGAspect()._qt_color_to_css(self.gs_aspect.background_color)
            style_parts.append(f"background-color: {css_color}")
        else:
            # Force transparency to avoid default black background when only border is set
            style_parts.append("background-color: transparent")
        if self.gs_aspect.background_image:
            style_parts.append(f"background-image: url({self.gs_aspect.background_image})")
        # Border
        if self.gs_aspect.border_size and self.gs_aspect.border_style and self.gs_aspect.border_color:
            css_color = SGAspect()._qt_color_to_css(self.gs_aspect.border_color)
            style_parts.append(f"border: {self.gs_aspect.border_size}px {self.gs_aspect.border_style} {css_color}")
        if self.gs_aspect.border_radius:
            style_parts.append(f"border-radius: {self.gs_aspect.border_radius}px")
        # Dimensions/padding
        if self.gs_aspect.min_width:
            style_parts.append(f"min-width: {self.gs_aspect.min_width}px")
        if self.gs_aspect.min_height:
            style_parts.append(f"min-height: {self.gs_aspect.min_height}px")
        if self.gs_aspect.padding:
            style_parts.append(f"padding: {self.gs_aspect.padding}px")
        return "; ".join(style_parts)

    def _applyContainerStyle(self):
        style = self._getContainerStyle()
        if style:
            self.setStyleSheet(f"#{self._qss_object_name} {{{style}}}")
        else:
            self.setStyleSheet("")

    def applyContainerAspectStyle(self):
        """Hook to apply container style; subclasses may override to no-op."""
        self._applyContainerStyle()
        self.theme_overridden = True
        
    def applyTheme(self, theme_name):
        """
        Apply a predefined theme to the gameSpace.
        
        Args:
            theme_name (str): The name of the theme ('modern', 'minimal', 'colorful', 'blue', 'green', 'gray')
        """
        from mainClasses.SGAspect import SGAspect
        
        theme_methods = {
            'modern': SGAspect.modern,
            'minimal': SGAspect.minimal,
            'colorful': SGAspect.colorful,
            'blue': SGAspect.blue,
            'green': SGAspect.green,
            'gray': SGAspect.gray
        }
        # Merge runtime registered themes if provided on model
        model = getattr(self, 'model', None)
        if model is not None and hasattr(model, '_runtime_themes'):
            for tname, spec in model._runtime_themes.items():
                def _factory(spec_dict=spec):
                    inst = SGAspect()
                    base = spec_dict.get('base', spec_dict)
                    inst.background_color = base.get('background_color')
                    inst.border_color = base.get('border_color')
                    inst.border_size = base.get('border_size')
                    inst.border_style = base.get('border_style')
                    inst.color = base.get('color')
                    inst.font = base.get('font')
                    inst.size = base.get('size')
                    inst.font_weight = base.get('font_weight')
                    inst.border_radius = base.get('border_radius')
                    inst.padding = base.get('padding')
                    return inst
                theme_methods[tname] = _factory
        
        if theme_name in theme_methods:
            theme_aspect = theme_methods[theme_name]()
            # Apply theme properties to gs_aspect
            self.gs_aspect.background_color = theme_aspect.background_color
            self.gs_aspect.border_color = theme_aspect.border_color
            self.gs_aspect.border_size = theme_aspect.border_size
            self.gs_aspect.border_style = theme_aspect.border_style
            self.gs_aspect.border_radius = theme_aspect.border_radius
            self.gs_aspect.padding = theme_aspect.padding
            
            # Apply theme properties to text aspects
            for aspect in [self.title1_aspect, self.title2_aspect, self.title3_aspect, 
                          self.text1_aspect, self.text2_aspect, self.text3_aspect]:
                aspect.color = theme_aspect.color
                aspect.font = theme_aspect.font
                aspect.size = theme_aspect.size
                aspect.font_weight = theme_aspect.font_weight
            # If runtime theme includes text_aspects overrides, apply them
            if model is not None and hasattr(model, '_runtime_themes') and theme_name in model._runtime_themes:
                text_specs = model._runtime_themes[theme_name].get('text_aspects', {})
                mapping = {
                    'title1': self.title1_aspect,
                    'title2': self.title2_aspect,
                    'title3': self.title3_aspect,
                    'text1': self.text1_aspect,
                    'text2': self.text2_aspect,
                    'text3': self.text3_aspect,
                }
                for key, asp in mapping.items():
                    spec = text_specs.get(key)
                    if not spec:
                        continue
                    if 'color' in spec:
                        asp.color = spec['color']
                    if 'font' in spec:
                        asp.font = spec['font']
                    if 'size' in spec:
                        asp.size = spec['size']
                    if 'font_weight' in spec:
                        asp.font_weight = spec['font_weight']
                    if 'font_style' in spec:
                        asp.font_style = spec['font_style']
                    if 'text_decoration' in spec:
                        asp.text_decoration = spec['text_decoration']
                
            # Track current theme name for UI dialogs (e.g., Edit Themes)
            self.current_theme_name = theme_name
            self.theme_overridden = False

            # Apply container-only style (no text cascade to children)
            if hasattr(self, '_applyContainerStyle'):
                self._applyContainerStyle()

            self.update()
        else:
            raise ValueError(f"Unknown theme: {theme_name}. Available themes: {list(theme_methods.keys())}")

    