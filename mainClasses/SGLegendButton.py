from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QPushButton, QToolTip
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from math import inf


class SGLegendButton(QtWidgets.QWidget):
    """
    A button widget for legend items (e.g., model actions in ControlPanel).
    When clicked, it directly executes the associated gameAction with the model as target.
    """
    def __init__(self, parent, gameAction, text=None):
        super().__init__(parent)
        self.legend = parent
        self.gameAction = gameAction
        self.posY = self.legend.posYOfItems
        self.legend.posYOfItems += 1
        self.type = 'legendButton'  # For compatibility with legend system
        
        # Use action's nameToDisplay with icon if available
        if text is None:
            from mainClasses.gameAction.SGActivate import SGActivate
            icon = getattr(SGActivate, 'context_menu_icon', '⚡')
            text = f"{icon} {gameAction.nameToDisplay}"
        
        # Store text attribute for compatibility with legend system
        self.text = str(text)
        
        # Create the button
        self.button = QPushButton(text, self)
        self.button.clicked.connect(self._executeAction)
        
        # Style the button to look like a legend item
        self.button.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 2px 5px;
                border: 1px solid transparent;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border: 1px solid #999;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        
        # Set size to match legend items
        item_height = getattr(self.legend, 'heightOfLabels', 22)
        self.setFixedHeight(item_height)
        self.button.setFixedHeight(item_height - 2)
        
        # Position the widget (will be repositioned in paintEvent)
        left_pad = getattr(self.legend, 'leftPadding', 10)
        top_pad = getattr(self.legend, 'topPadding', 0)
        self.move(left_pad, top_pad + self.posY * item_height)
        
    def _executeAction(self):
        """Execute the model action with the model as target"""
        if self.gameAction is not None:
            # Execute with the model as target
            self.gameAction.perform_with(self.gameAction.model)
    
    def event(self, e):
        # Intercept tooltip event to show the number of remaining actions
        if e.type() == QEvent.ToolTip:
            if self.gameAction is not None:
                # Dynamically update tooltip
                aNumber = self.gameAction.getNbRemainingActions()
                if aNumber == inf:
                    text = f"∞ actions"
                else:
                    text = f"{self.gameAction.getNbRemainingActions()} actions remaining"
                QToolTip.showText(e.globalPos(), text, self)
            return True  # event handled
        return super().event(e)
    
    def resizeEvent(self, event):
        """Resize the button to fill the widget"""
        self.button.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)
    
    def paintEvent(self, event):
        """Reposition the widget to match legend item positioning"""
        if hasattr(self.legend, 'checkDisplay') and self.legend.checkDisplay():
            item_height = getattr(self.legend, 'heightOfLabels', 22)
            left_pad = getattr(self.legend, 'leftPadding', 10)
            top_pad = getattr(self.legend, 'topPadding', 0)
            self.move(left_pad, top_pad + self.posY * item_height)
            # Set width to match legend width
            try:
                content_width = self.legend.getSizeX_fromAllWidgets()
                if content_width > 0:
                    self.setFixedWidth(content_width)
            except:
                pass
        super().paintEvent(event)
    
    def isSelectable(self):
        """Legend buttons are not selectable (they execute directly)"""
        return False

