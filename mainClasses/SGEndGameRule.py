from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true

from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGEndGameCondition import SGEndGameCondition
from mainClasses.SGAspect import SGAspect


class SGEndGameRule(SGGameSpace):

    def __init__(self, parent, title, numberRequired, displayRefresh='instantaneous', isDisplay=True, borderColor=Qt.black, backgroundColor=Qt.lightGray, layout="vertical", textColor=Qt.black,
                 endGameDisplayMode='highlight', endGameBannerText='Game over', endGameBannerColor=Qt.red, endGameBannerPosition='top',
                 endGameHighlightEnabled=True, endGameHighlightBorderColor=Qt.green, endGameHighlightBorderSize=4, endGameHighlightBackgroundColor=Qt.lightGreen,
                 endGameAnimationEnabled=False, endGameAnimationDuration=5):
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
        # Flag to track if displayEndGameConditions() has been called
        self._conditions_shown = False
        # Hide widget by default until displayEndGameConditions() is called
        self.setVisible(False)
        
        # End game display configuration
        self.endGameDisplayMode = endGameDisplayMode  # 'banner', 'highlight', 'highlight + banner', or 'none'
        self.endGameBannerText = endGameBannerText
        self.endGameBannerColor = endGameBannerColor
        self.endGameBannerPosition = endGameBannerPosition  # 'top' or 'bottom'
        self.endGameHighlightEnabled = endGameHighlightEnabled
        self.endGameHighlightBorderColor = endGameHighlightBorderColor
        self.endGameHighlightBorderSize = endGameHighlightBorderSize
        self.endGameHighlightBackgroundColor = endGameHighlightBackgroundColor
        self.endGameAnimationEnabled = endGameAnimationEnabled
        self.endGameAnimationDuration = endGameAnimationDuration
        self._game_ended = False  # Flag to track if game has ended
        self._highlight_animation = None  # QTimer for pulse effect
        self._animation_stop_timer = None  # QTimer to stop animation after duration
        
        if layout == 'vertical':
            self.layout = QtWidgets.QVBoxLayout()
        elif layout == 'horizontal':
            self.layout = QtWidgets.QHBoxLayout()


    def paintEvent(self, event):
        if self.checkDisplay():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing, True)

            # Background: prefer image, else color (support transparent)
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

            # Pen with style mapping
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

            width = max(0, self.getSizeXGlobal() - 1)
            height = max(0, self.getSizeYGlobal() - 1)
            radius = getattr(self.gs_aspect, 'border_radius', None) or 0
            if radius > 0:
                painter.drawRoundedRect(0, 0, width, height, radius, radius)
            else:
                painter.drawRect(0, 0, width, height)

    def checkDisplay(self):
        # Only display if isDisplay is True AND displayEndGameConditions() has been called
        if self.isDisplay and self._conditions_shown:
            return True
        else:
            return False
    
    def adjustSizeAfterLayout(self):
        """
        Adjust widget size after layout configuration.
        """
        if hasattr(self, 'layout') and self.layout:
            # Force layout to calculate its size
            self.layout.activate()
            size_hint = self.layout.sizeHint()
            if size_hint.isValid():
                # Add margins for border
                width = size_hint.width() + self.size_manager.right_margin + self.size_manager.border_padding
                height = size_hint.height() + self.size_manager.vertical_gap_between_labels + self.size_manager.border_padding
                
                # Apply calculated size
                self.setMinimumSize(width, height)
                self.resize(width, height)

    def applyContainerAspectStyle(self):
        """Avoid QSS cascade; rely on paintEvent for container rendering."""
        pass

    def onTextAspectsChanged(self):
        """Apply title and text aspects (color, font, size, weight, style, decoration, alignment)."""
        # Title styling from title1_aspect
        if hasattr(self, 'titleLabel') and self.titleLabel is not None:
            self._applyAspectToLabel(self.titleLabel, self.title1_aspect)

        # Apply text1_aspect to all other labels (conditions text)
        for lbl in self.findChildren(QtWidgets.QLabel):
            if hasattr(self, 'titleLabel') and lbl is self.titleLabel:
                continue
            self._applyAspectToLabel(lbl, self.text1_aspect)

        # Request layout/size update
        try:
            if hasattr(self, 'layout') and self.layout:
                self.layout.activate()
            self.adjustSizeAfterLayout()
        except Exception:
            pass
        self.update()

    # *Functions to have the global size of a gameSpace
    def getSizeXGlobal(self):
        # Use actual layout size if available
        if hasattr(self, 'layout') and self.layout:
            # Force layout to calculate its size
            self.layout.activate()
            size_hint = self.layout.sizeHint()
            if size_hint.isValid():
                return max(size_hint.width() + self.size_manager.right_margin, self.size_manager.min_width)
        
        # Fallback: calculation based on content
        if hasattr(self, 'endGameConditions') and self.endGameConditions:
            return self.calculateContentWidth(content_widgets=self.endGameConditions)
        return self.size_manager.min_width

    def getSizeYGlobal(self):
        # Use actual layout size if available
        if hasattr(self, 'layout') and self.layout:
            # Force layout to calculate its size
            self.layout.activate()
            size_hint = self.layout.sizeHint()
            if size_hint.isValid():
                return max(size_hint.height() + self.size_manager.vertical_gap_between_labels, self.size_manager.min_height)
        
        # Fallback: calculation based on content
        if hasattr(self, 'endGameConditions') and self.endGameConditions:
            return self.calculateContentHeight(content_items=self.endGameConditions)
        return self.size_manager.min_height

    
    def activateEndGameDisplay(self):
        """
        Activate the end game display (banner and/or highlight) when game ends.
        This is called automatically by SGTimeManager when checkStatus becomes True.
        """
        if self._game_ended:
            return  # Already activated
        
        self._game_ended = True
        
        # Activate banner if enabled
        if 'banner' in self.endGameDisplayMode:
            self.model._showEndGameBanner(self.endGameBannerText, self.endGameBannerColor, self.endGameBannerPosition)
        
        # Activate highlight if enabled
        if 'highlight' in self.endGameDisplayMode:
            self._activateHighlight()
    
    def _activateHighlight(self):
        """Activate the highlight effect on the widget."""
        # Store original styles
        if not hasattr(self, '_original_border_color'):
            self._original_border_color = self.gs_aspect.border_color
            self._original_border_size = self.gs_aspect.border_size
            self._original_background_color = self.gs_aspect.background_color
        
        # Apply highlight styles
        self.gs_aspect.border_color = self.endGameHighlightBorderColor
        self.gs_aspect.border_size = self.endGameHighlightBorderSize
        self.gs_aspect.background_color = self.endGameHighlightBackgroundColor
        
        # Start animation if enabled
        if self.endGameAnimationEnabled:
            self._startPulseAnimation()
        
        self.update()
    
    def _startPulseAnimation(self):
        """Start the pulse animation effect using QTimer."""
        from PyQt5.QtCore import QTimer
        
        if self._highlight_animation is not None:
            self._highlight_animation.stop()
        if self._animation_stop_timer is not None:
            self._animation_stop_timer.stop()
        
        # Store original border size
        if not hasattr(self, '_pulse_original_size'):
            self._pulse_original_size = self.endGameHighlightBorderSize
            self._pulse_direction = 1  # 1 for increasing, -1 for decreasing
            self._pulse_step = 1
        
        # Create timer for pulsing effect
        self._highlight_animation = QTimer()
        # Convert seconds to milliseconds for interval (20 steps per animation cycle)
        duration_ms = int(self.endGameAnimationDuration * 1000)
        interval = duration_ms // 20
        self._highlight_animation.timeout.connect(self._pulseStep)
        self._highlight_animation.start(interval)
        
        # Create timer to stop animation after specified duration
        self._animation_stop_timer = QTimer()
        self._animation_stop_timer.setSingleShot(True)  # Fire only once
        self._animation_stop_timer.timeout.connect(self._stopPulseAnimation)
        self._animation_stop_timer.start(duration_ms)  # Convert seconds to milliseconds
    
    def _pulseStep(self):
        """Perform one step of the pulse animation."""
        # Update border size
        new_size = self.gs_aspect.border_size + (self._pulse_direction * self._pulse_step)
        
        # Reverse direction at limits
        if new_size >= self._pulse_original_size + 3:
            self._pulse_direction = -1
            new_size = self._pulse_original_size + 3
        elif new_size <= self._pulse_original_size:
            self._pulse_direction = 1
            new_size = self._pulse_original_size
        
        self.gs_aspect.border_size = new_size
        self.update()
    
    def _stopPulseAnimation(self):
        """Stop the pulse animation and restore original border size."""
        if self._highlight_animation is not None:
            self._highlight_animation.stop()
            self._highlight_animation = None
        
        # Restore original border size
        if hasattr(self, '_pulse_original_size'):
            self.gs_aspect.border_size = self._pulse_original_size
            self.update()

    
    # ============================================================================
    # MODELER METHODS
    # ============================================================================
    def __MODELER_METHODS__(self):
        pass
    
    # ============================================================================
    # NEW/ADD METHODS
    # ============================================================================
    def __MODELER_METHODS__NEW__(self):
        pass

    # To add a condition to end the game
    def addEndGameCondition_onIndicator(self, indicator, logicalTest, objective, name="Indicator based condition", color=Qt.black, isDisplay=True, delay_rounds=0, final_phase=None):
        """
        Create an EndGame Condition with an Indicator

        Args:
            indicator (instance) : indicator concerned
            logicalTest (str): logical test concerned in ["greater","greater or equal","equal", "less or equal","less"]
            objective (int) : objective value to do logical test with
            name (str) : name of the end game condition, displayed (default : "Indicator based condition")
            color (Qt.color) : text color (default : black)
            isDisplay (bool) : is displayed in the EndGameRule board (default : True)
            delay_rounds (int): Number of remaining rounds after the condition is met before triggering the end of the game (default: 0).
            final_phase (int, str, or phase instance, optional): Final phase when the game should end. Can be:
                - int: phase number (1-indexed)
                - str: phase name or 'last phase' for the last phase of the round
                - phase instance: the phase object
                - None: use current phase when condition is met (default: None)
        """
        aCondition = SGEndGameCondition(self, name, entity=indicator, method=logicalTest, objective=objective,
                                        attribut=None, color=color, calcType="onIndicator", isDisplay=isDisplay,
                                        delay_rounds=delay_rounds, final_phase=final_phase)
        self.endGameConditions.append(aCondition)
        self.model.timeManager.conditionOfEndGame.append(aCondition)
        # Automatically adjust size after adding a condition
        self.adjustSizeToContent(content_widgets=self.endGameConditions)

    def addEndGameCondition_onEntity(self, aEntity, attribute, logicalTest, objective, name="Entity based condition",type_name=None, aGrid=None, color=Qt.black, isDisplay=True, delay_rounds=0, final_phase=None):
        """Create an EndGame Condition with an Entity

        Args:
            aEntity (SGCell or SGAgent) : the entity (cell, agent)
            attribute (str) : attribute concerned
            logicalTest (str): logical test concerned in ["greater","greater or equal","equal", "less or equal","less"]
            objective (int) : objective value to do logical test with
            name (str) : name of the end game condition, displayed (default : “Entity based condition")
            type_name (str) : name of the entity type (only if your entity is an Agent, default : None)
            aGrid (instance) : instance of the concerned grid (only if your entity is a Cell, default : None)
            color (Qt.color) : text color (default : black)
            isDisplay (bool) : is displayed in the EndGameRule board (default : True)
            delay_rounds (int): Number of remaining rounds after the condition is met before triggering the end of the game (default: 0).
            final_phase (int, str, or phase instance, optional): Final phase when the game should end. Can be:
                - int: phase number (1-indexed)
                - str: phase name or 'last phase' for the last phase of the round
                - phase instance: the phase object
                - None: use current phase when condition is met (default: None)
        """
      
        aCondition = SGEndGameCondition(self, name, entity=aEntity, method=logicalTest, objective=objective,
                                        attribut=attribute, color=color, calcType="onEntity", isDisplay=isDisplay,
                                        delay_rounds=delay_rounds, final_phase=final_phase)
        self.endGameConditions.append(aCondition)
        self.model.timeManager.conditionOfEndGame.append(aCondition)
        # Automatically adjust size after adding a condition
        self.adjustSizeToContent(content_widgets=self.endGameConditions)


    def addEndGameCondition_onGameRound(self, logicalTest, objective, name="Game round condition", color=Qt.black, isDisplay=True, delay_rounds=0, final_phase=None):
        """
        Create an EndGame Condition on the time (game rounds)

        Args:
            logicalTest (str): logical test concerned in ["greater","greater or equal","equal", "less or equal","less"]
            objective (int) : objective value to do logical test with
            name (str) : name of the end game condition, displayed (default : “Entity based condition")
            color (Qt.color) : text color (default : black)
            isDisplay (bool) : is displayed in the EndGameRule board (default : True)
            delay_rounds (int): Number of remaining rounds after the condition is met before triggering the end of the game (default: 0).
            final_phase (int, str, or phase instance, optional): Final phase when the game should end. Can be:
                - int: phase number (1-indexed)
                - str: phase name or 'last phase' for the last phase of the round
                - phase instance: the phase object
                - None: use current phase when condition is met (default: None)
        """
        aCondition = SGEndGameCondition(self, name, entity=None, method=logicalTest, objective=objective,
                                        attribut=None, color=color, calcType="onGameRound", isDisplay=isDisplay,
                                        delay_rounds=delay_rounds, final_phase=final_phase)
        self.endGameConditions.append(aCondition)
        self.model.timeManager.conditionOfEndGame.append(aCondition)
        # Automatically adjust size after adding a condition
        self.adjustSizeToContent(content_widgets=self.endGameConditions)

   

    def addEndGameCondition_onLambda(self, lambda_function, name="Lambda based condition", color=Qt.black, isDisplay=True, delay_rounds=0, final_phase=None):
        """
        Create an EndGame Condition based on a lambda function.

        Args:
            lambda_function (callable): A lambda function that returns a boolean indicating the end game condition.
            name (str): Name of the end game condition, displayed (default: "Lambda based condition").
            color (Qt.color): Text color (default: black).
            isDisplay (bool): Whether to display in the EndGameRule board (default: True).
            delay_rounds (int): Number of remaining rounds after the condition is met before triggering the end of the game (default: 0).
            final_phase (int, str, or phase instance, optional): Final phase when the game should end. Can be:
                - int: phase number (1-indexed)
                - str: phase name or 'last phase' for the last phase of the round
                - phase instance: the phase object
                - None: use current phase when condition is met (default: None)
        """
        aCondition = SGEndGameCondition(self, name, entity=None, method=lambda_function, objective=None,
                                        attribut=None, color=color, calcType="onLambda", isDisplay=isDisplay,
                                        delay_rounds=delay_rounds, final_phase=final_phase)
        self.endGameConditions.append(aCondition)
        self.model.timeManager.conditionOfEndGame.append(aCondition)
        # Automatically adjust size after adding a condition
        self.adjustSizeToContent(content_widgets=self.endGameConditions)

   
    # ============================================================================
    # SET METHODS
    # ============================================================================
    def __MODELER_METHODS__SET__(self):
        pass

        
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
    

    def setEndGameDisplay(self, mode='highlight', banner_text='Game over', 
                         banner_color=Qt.red, banner_position='top',
                         highlight_border_color=Qt.green, highlight_border_size=4,
                         highlight_background_color=Qt.lightGreen,
                         animation_enabled=False, animation_duration=5,
                         countdown_display_mode='rounds_and_phases', countdown_separator=' ➜ '):
        """
        Configure all end game display options in a single call.
        
        This is a convenience method that sets all display-related options at once.
        Individual SET methods can still be used for fine-tuning after this call.
        
        Args:
            mode (str): Display mode - 'banner', 'highlight', 'highlight + banner', or 'none' (default: 'highlight')
            banner_text (str): Banner text displayed when game ends (default: 'Game over')
            banner_color (QColor): Banner background color (default: Qt.red)
            banner_position (str): Banner position - 'top' or 'bottom' (default: 'top')
            highlight_border_color (QColor): Highlight border color (default: Qt.green)
            highlight_border_size (int): Highlight border size in pixels (default: 4)
            highlight_background_color (QColor): Highlight background color (default: Qt.lightGreen)
            animation_enabled (bool): Enable pulse animation (default: False)
            animation_duration (float): Animation duration in seconds (default: 5)
            countdown_display_mode (str): Countdown display mode - 'rounds_only' or 'rounds_and_phases' (default: 'rounds_and_phases')
            countdown_separator (str): Separator between condition name and countdown (default: ' ➜ ')
        """
        self.setEndGameDisplayMode(mode)
        self.setEndGameBannerText(banner_text)
        self.setEndGameBannerColor(banner_color)
        self.setEndGameBannerPosition(banner_position)
        self.setEndGameRuleHighlightBorderColor(highlight_border_color)
        self.setEndGameRuleHighlightBorderSize(highlight_border_size)
        self.setEndGameRuleHighlightBackgroundColor(highlight_background_color)
        self.setEndGameAnimationEnabled(animation_enabled)
        self.setEndGameAnimationDuration(animation_duration)
        self.setEndGameConditionCountdownDisplayMode(countdown_display_mode)
        self.setEndGameConditionCountdownSeparator(countdown_separator)
    
    def setEndGameDisplayMode(self, mode='highlight'):
        """
        Set the end game display mode.
        
        Args:
            mode (str): Display mode - 'banner', 'highlight', 'highlight + banner', or 'none'
        """
        valid_modes = ['banner', 'highlight', 'highlight + banner', 'none']
        if mode not in valid_modes:
            raise ValueError(f"Invalid display mode: {mode}. Must be one of {valid_modes}")
        self.endGameDisplayMode = mode
    
    def enableEndGameBanner(self):
        """Enable the end game banner display."""
        if self.endGameDisplayMode == 'none':
            self.endGameDisplayMode = 'banner'
        elif self.endGameDisplayMode == 'highlight':
            self.endGameDisplayMode = 'highlight + banner'
    
    def disableEndGameBanner(self):
        """Disable the end game banner display."""
        if self.endGameDisplayMode == 'highlight + banner':
            self.endGameDisplayMode = 'highlight'
        elif self.endGameDisplayMode == 'banner':
            self.endGameDisplayMode = 'none'
    
    def setEndGameBannerText(self, text):
        """Set the banner text displayed when game ends."""
        self.endGameBannerText = text
    
    def setEndGameBannerColor(self, color):
        """Set the banner background color."""
        self.endGameBannerColor = color
    
    def setEndGameBannerPosition(self, position='top'):
        """Set the banner position: 'top' or 'bottom'"""
        if position not in ['top', 'bottom']:
            raise ValueError("Banner position must be 'top' or 'bottom'")
        self.endGameBannerPosition = position
    
    def enableEndGameRuleHighlight(self):
        """Enable highlighting of the endGameRule widget when game ends."""
        if self.endGameDisplayMode == 'none':
            self.endGameDisplayMode = 'highlight'
        elif self.endGameDisplayMode == 'banner':
            self.endGameDisplayMode = 'highlight + banner'
    
    def disableEndGameRuleHighlight(self):
        """Disable highlighting of the endGameRule widget when game ends."""
        if self.endGameDisplayMode == 'highlight + banner':
            self.endGameDisplayMode = 'banner'
        elif self.endGameDisplayMode == 'highlight':
            self.endGameDisplayMode = 'none'
    
    def setEndGameRuleHighlightBorderColor(self, color):
        """Set the highlight border color when game ends."""
        self.endGameHighlightBorderColor = color
    
    def setEndGameRuleHighlightBorderSize(self, size):
        """Set the highlight border size when game ends."""
        self.endGameHighlightBorderSize = size
    
    def setEndGameRuleHighlightBackgroundColor(self, color):
        """Set the highlight background color when game ends."""
        self.endGameHighlightBackgroundColor = color
    
    def setEndGameAnimationEnabled(self, enabled=False):
        """Enable or disable the pulse animation when game ends."""
        self.endGameAnimationEnabled = enabled
    
    def setEndGameAnimationDuration(self, duration_seconds):
        """Set the animation duration in seconds."""
        self.endGameAnimationDuration = duration_seconds
    
    def setEndGameConditionCountdownSeparator(self, separator=' ➜ '):
        """Set the separator between condition name and countdown."""
        for condition in self.endGameConditions:
            condition.countdown_separator = separator
    
    def setEndGameConditionCountdownDisplayMode(self, mode='rounds_and_phases'):
        """
        Set the countdown display mode for all conditions.
        
        Args:
            mode (str): Display mode - 'rounds_only' or 'rounds_and_phases' (default: 'rounds_and_phases')
                - 'rounds_only': Shows only rounds remaining (e.g., "Last round (1 round remaining)")
                - 'rounds_and_phases': Shows both rounds and phases remaining (e.g., "Last round (1 round, 2 phases remaining)")
        """
        valid_modes = ['rounds_only', 'rounds_and_phases']
        if mode not in valid_modes:
            raise ValueError(f"Invalid countdown display mode: {mode}. Must be one of {valid_modes}")
        for condition in self.endGameConditions:
            condition.countdown_display_mode = mode

  
    # ============================================================================
    # DO/DISPLAY METHODS
    # ============================================================================
    def __MODELER_METHODS__DO_DISPLAY__(self):
        pass


    def displayEndGameConditions(self):
        """
        Configure and display the EndGameRule widget with all conditions.
        
        This method:
        1. Configures the widget layout (title, conditions list, optional button)
        2. Makes the widget visible immediately
        
        Behavior:
        - If called: Widget is displayed immediately and remains visible throughout the game
        - If not called: Widget will be displayed automatically when a condition is first detected
          (useful for games with delay_rounds to inform players they're entering the last round)
        
        In both cases, when the game actually ends (checkStatus=True), the banner and highlight
        will be activated according to the endGameDisplayMode configuration.
        
        Note: This method is optional. If you want the widget to appear only when a condition
        is detected, you can omit this call. The widget will appear automatically.
        """
        if self.isDisplay:
            layout = self.layout

            self.titleLabel = QtWidgets.QLabel(self.id)
            font = QFont()
            font.setBold(True)
            self.titleLabel.setFont(font)
            layout.addWidget(self.titleLabel)
            for condition in self.endGameConditions:
                layout.addLayout(condition.conditionLayout)

            # Create a QPushButton to update the text
            if self.displayRefresh == 'withButton':
                self.button = QtWidgets.QPushButton("Update Scores")
                self.button.clicked.connect(
                    lambda: [condition.updateText() for condition in self.endGameConditions])
                layout.addWidget(self.button)

            self.setLayout(layout)
            # Apply text aspects (title1/text1) now that widgets exist
            self.onTextAspectsChanged()
            # Adjust size after layout configuration
            self.adjustSizeAfterLayout()
            # Mark that conditions have been shown and make widget visible
            self._conditions_shown = True
            self.setVisible(True)
            self.show()
