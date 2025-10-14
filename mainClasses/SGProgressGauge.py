from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QPainter, QPen, QBrush
from mainClasses.SGGameSpace import SGGameSpace

class SGProgressGauge(SGGameSpace):
    """
    A progress gauge widget for monitoring simulation variables.
    This widget displays a progress bar (horizontal or vertical) that reflects the value of 
    a linked simulation variable.
    The gauge can also trigger callbacks when specific thresholds are crossed.
    It supports optional titles, value labels, units, color ranges for dynamic coloring, and custom sizes. 

    Args:
        parent (QWidget): Parent widget.
        simVar (object): a simulation variable instance
        min_value (float or int, optional): Minimum value of the gauge. Defaults to 0.
        max_value (float or int, optional): Maximum value of the gauge. Defaults to 100.
        title (str, optional): Text label for the gauge. Defaults to None.
        orientation (str, optional): "horizontal" or "vertical". Defaults to "horizontal".
        colorRanges (list of tuple, optional): List of (min_value, max_value, color_string) for dynamic coloring. Defaults to None.
        unit (str, optional): Unit suffix for the displayed value. Defaults to "".
        borderColor (QColor or Qt.GlobalColor, optional): Border color of the widget. Defaults to Qt.black.
        backgroundColor (QColor or Qt.GlobalColor, optional): Background color of the widget. Defaults to Qt.white.
        bar_width (int, float, or str, optional): Width of the progress bar in pixels, or "fit title size" for vertical mode. Defaults to 25.
        bar_length (int, optional): Length of the progress bar in pixels. Defaults to 180 for horizontal and 160 for vertical.
        title_position (str, optional): "above" or "below" the gauge. Defaults to "above".
        display_value_on_top (bool, optional): Whether to display the numeric value on top of the progress bar. Defaults to True.

    Methods:
        setThresholdValue(value, on_up=None, on_down=None):
            Define callbacks to execute when a value threshold is crossed.
       
    """
    def __init__(self, parent, simVar, min_value=0, max_value=100, title = None, orientation='horizontal',
                 colorRanges=None, unit="", borderColor=Qt.black, backgroundColor=Qt.white,
                 bar_width=25,bar_length=None, title_position ='above',display_value_on_top = True):
        
        
        # Call SGGameSpace constructor with custom background color
        super().__init__(parent, 0, 60, 0, 0, True, backgroundColor)
        
        self.simVar = simVar
        self.title_text = title
        self.max_value = max_value
        self.min_value = min_value
        self.unit = unit
        self.orientation = orientation
        self.colorRanges = colorRanges or []
        self.thresholds = {}
        # Configure styles using gs_aspect instead of individual attributes
        self.gs_aspect.border_color = borderColor
        self.gs_aspect.border_size = 2
        self.gs_aspect.background_color = backgroundColor
        self.bar_width = bar_width if isinstance(bar_width,(int, float)) else None
        if bar_width == 'fit title size' and self.orientation == 'vertical' :
            if self.title_text is None : raise ValueError ('bar_width cannot be fit title size, if the title is None')
            self.bar_width_fit_title_size = True
        else:
            self.bar_width_fit_title_size = False
        if bar_length:
            self.bar_length = bar_length
        else:
            if self.orientation == 'horizontal':
                self.bar_length = 180
            elif self.orientation == 'vertical':
                self.bar_length = 160
        self.title_position = title_position
        self.display_value_on_top = display_value_on_top

        # Watch the variable
        self.simVar.addWatcher(self)

        # Init UI
        self.init_ui()

        # Apply text aspects to labels and compute initial size
        try:
            self.onTextAspectsChanged()
        except Exception:
            pass

        # Initial value update
        self.checkAndUpdate()

        # Prefer layout-based sizing
        try:
            if hasattr(self, 'layout') and self.layout is not None:
                self.updateSizeFromLayout(self.layout)
        except Exception:
            pass


    def init_ui(self):
        """Initialize the progress gauge UI components."""
        layout = QVBoxLayout() if self.orientation == 'vertical' else QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        # Marges cohérentes avec les autres GameSpaces
        try:
            layout.setContentsMargins(4, 0, self.rightMargin, self.verticalGapBetweenLabels)
            layout.setSpacing(self.verticalGapBetweenLabels)
        except Exception:
            pass

        # Title label
        if self.title_text is not None:
            self.title_label = QLabel(self.title_text)
            self.title_label.setAlignment(Qt.AlignCenter)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)

        if self.orientation == 'vertical':
            self.progress_bar.setOrientation(Qt.Vertical)
            self.progress_bar.setAlignment(Qt.AlignCenter)
            self.progress_bar.setFixedHeight(self.bar_length)
            if self.bar_width_fit_title_size:
                self.progress_bar.setFixedWidth(max(20, len(self.title_text) * 7))
            elif self.bar_width is not None:
                self.progress_bar.setFixedWidth(self.bar_width)
        else:
            self.progress_bar.setOrientation(Qt.Horizontal)
            self.progress_bar.setFixedWidth(self.bar_length)
            if self.bar_width is not None: self.progress_bar.setFixedHeight(self.bar_width)

        # Apply background color to the widget
        palette = self.progress_bar.palette()
        palette.setColor(QPalette.Base, self.gs_aspect.getBackgroundColorValue())
        self.progress_bar.setPalette(palette)

        # Value label
        if self.display_value_on_top:
            self.value_label = QLabel("0")
            self.value_label.setAlignment(Qt.AlignCenter)

        # Arrange layout
        if self.orientation == 'vertical':
            if self.title_text is not None and self.title_position == 'above' : layout.addWidget(self.title_label)
            layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)
            if self.display_value_on_top:
                progress_bar_layout = QVBoxLayout()
                #Removes the margins to handle cases where the text overflows the progress bar size.
                progress_bar_layout.setContentsMargins(0, 0, 0, 0)
                progress_bar_layout.addWidget(self.value_label)
                self.progress_bar.setLayout(progress_bar_layout)
            if self.title_text is not None and self.title_position == 'below' : layout.addWidget(self.title_label)


        else:
            vbox = QVBoxLayout()
            if self.title_text is not None and self.title_position == 'above' : vbox.addWidget(self.title_label)
            vbox.addWidget(self.progress_bar, alignment=Qt.AlignCenter)
            if self.display_value_on_top:
                progress_bar_layout = QVBoxLayout()
                #Removes the margins to handle cases where the text overflows the progress bar size.
                progress_bar_layout.setContentsMargins(0, 0, 0, 0)
                progress_bar_layout.addWidget(self.value_label)
                self.progress_bar.setLayout(progress_bar_layout)       
            if self.title_text is not None and self.title_position == 'below' : vbox.addWidget(self.title_label)
            layout.addLayout(vbox)

        # Conserver une référence pour updateSizeFromLayout
        self.layout = layout
        self.setLayout(layout)

    def paintEvent(self, event):
        """Custom container rendering: background (with transparency), border style and radius."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Background with transparency
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
        w = max(0, getattr(self, 'sizeXGlobal', self.width()) - 1)
        h = max(0, getattr(self, 'sizeYGlobal', self.height()) - 1)
        if radius > 0:
            painter.drawRoundedRect(0, 0, w, h, radius, radius)
        else:
            painter.drawRect(0, 0, w, h)

    def checkAndUpdate(self):
        """Update the progress bar according to the current SimVariable value."""
        val = self.simVar.value

        # Clamp values to range
        if val <= self.min_value:
            progress_val = 0
        elif val >= self.max_value:
            progress_val = 100
        else:
            progress_val = int(((val - self.min_value) /
                                (self.max_value - self.min_value)) * 100)

        self.progress_bar.setValue(progress_val)
        if self.display_value_on_top:
            self.value_label.setText(f"{val}{self.unit}")
            self.value_label.adjustSize()

        # Apply dynamic colors
        if self.colorRanges:
            for (low, high, color) in self.colorRanges:
                if low <= val <= high:
                    self.setBarColor(color)

        # Threshold callbacks
        for threshold_value, callbacks in self.thresholds.items():
            up_cb, down_cb = callbacks
            if val >= threshold_value and up_cb:
                up_cb()
            elif val < threshold_value and down_cb:
                down_cb()
    def setBarColor(self, color):
        """Set the fill color of the progress bar without altering widget border/background."""
        if not isinstance(color, str):
            color = QColor(color).name()  # Convert QColor or Qt.GlobalColor to CSS string
        # just modify the chunk so that it does not alter other colors
        self.progress_bar.setStyleSheet(
            f"""
            QProgressBar::chunk {{
                background-color: {color};
            }}
            """
        )

    def setThresholdValue(self, value, on_up=None, on_down=None):
        """Set callbacks for when the variable crosses a threshold."""
        self.thresholds[value] = (on_up, on_down)

    def getSizeXGlobal(self):
        """Return the global X size of the gauge."""
        return getattr(self, 'sizeXGlobal', self.width())

    def getSizeYGlobal(self):
        """Return the global Y size of the gauge."""
        return getattr(self, 'sizeYGlobal', self.height())

    # ============================================================================
    # MODELER METHODS
    # ============================================================================
    
    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================
    
    def setBorderColor(self, color):
        """
        Set the border color of the progress gauge.
        
        Args:
            color (QColor or Qt.GlobalColor): The border color
        """
        super().setBorderColor(color)
        
    def setBorderSize(self, size):
        """
        Set the border size of the progress gauge.
        
        Args:
            size (int): The border size in pixels
        """
        super().setBorderSize(size)
        
    def setBackgroundColor(self, color):
        """
        Set the background color of the progress gauge.
        
        Args:
            color (QColor or Qt.GlobalColor): The background color
        """
        super().setBackgroundColor(color)
        # Update the progress bar palette to reflect container background when relevant
        try:
            palette = self.progress_bar.palette()
            palette.setColor(QPalette.Base, self.gs_aspect.getBackgroundColorValue())
            self.progress_bar.setPalette(palette)
        except Exception:
            pass

    # =========================
    # STYLE/APPLY HOOKS
    # =========================
    def applyContainerAspectStyle(self):
        """Avoid QSS cascade; rely on paintEvent for container rendering."""
        pass

    def onTextAspectsChanged(self):
        # Title styling (title1_aspect)
        if hasattr(self, 'title_label') and self.title_label is not None:
            css_parts = []
            if self.title1_aspect.color:
                css_parts.append(f"color: {QColor(self.title1_aspect.color).name()}")
            td = getattr(self.title1_aspect, 'text_decoration', None)
            css_parts.append(f"text-decoration: {td}" if td and str(td).lower() != 'none' else "text-decoration: none")
            f = self.title_label.font()
            if self.title1_aspect.font:
                f.setFamily(self.title1_aspect.font)
            if self.title1_aspect.size:
                try:
                    f.setPixelSize(int(self.title1_aspect.size))
                except Exception:
                    pass
            if self.title1_aspect.font_weight:
                w = str(self.title1_aspect.font_weight).lower()
                if w == 'bold':
                    f.setBold(True)
                elif w == 'normal':
                    f.setBold(False)
                else:
                    try:
                        f.setWeight(int(self.title1_aspect.font_weight))
                    except Exception:
                        pass
            if self.title1_aspect.font_style:
                s = str(self.title1_aspect.font_style).lower()
                f.setItalic(s in ('italic', 'oblique'))
            self.title_label.setFont(f)
            self.title_label.setStyleSheet("; ".join(css_parts))

        # Value label styling (text1_aspect)
        if hasattr(self, 'value_label') and self.value_label is not None:
            css_parts = []
            if self.text1_aspect.color:
                css_parts.append(f"color: {QColor(self.text1_aspect.color).name()}")
            td = getattr(self.text1_aspect, 'text_decoration', None)
            css_parts.append(f"text-decoration: {td}" if td and str(td).lower() != 'none' else "text-decoration: none")
            f = self.value_label.font()
            if self.text1_aspect.font:
                f.setFamily(self.text1_aspect.font)
            if self.text1_aspect.size:
                try:
                    f.setPixelSize(int(self.text1_aspect.size))
                except Exception:
                    pass
            if self.text1_aspect.font_weight:
                w = str(self.text1_aspect.font_weight).lower()
                if w == 'bold':
                    f.setBold(True)
                elif w == 'normal':
                    f.setBold(False)
                else:
                    try:
                        f.setWeight(int(self.text1_aspect.font_weight))
                    except Exception:
                        pass
            if self.text1_aspect.font_style:
                s = str(self.text1_aspect.font_style).lower()
                f.setItalic(s in ('italic', 'oblique'))
            self.value_label.setFont(f)
            self.value_label.setStyleSheet("; ".join(css_parts))

        # Resize to content
        if hasattr(self, 'layout') and self.layout is not None:
            self.updateSizeFromLayout(self.layout)
        self.update()

    # =========================
    # SIZE UPDATE UTILITIES
    # =========================
    def updateLabelsandWidgetSize(self):
        if hasattr(self, 'layout') and self.layout is not None:
            self.updateSizeFromLayout(self.layout)
