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
        
        
    def setTitlesAndTextsColor(self, textColor):
        self.setTitlesColor(textColor)
        self.setTextsColor(textColor)

    # Apply textColor to each title
    def setTitlesColor(self, textColor):
        for aspect in [self.title1_aspect, self.title2_aspect, self.title3_aspect]:
            aspect.color = textColor  

    # Apply textColor to each text
    def setTextsColor(self, textColor):
        for aspect in [self.text1_aspect, self.text2_aspect, self.text3_aspect]:
            aspect.color = textColor 
    
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

    