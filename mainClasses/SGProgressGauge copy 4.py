from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QPainter, QPen, QBrush
from mainClasses.SGGameSpace import SGGameSpace

class SGProgressGauge(SGGameSpace):
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
        self.borderColor = borderColor
        self.backgroundColor = backgroundColor
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

        # Initial value update
        self.checkAndUpdate()

    def init_ui(self):
        """Initialize the progress gauge UI components."""
        layout = QVBoxLayout() if self.orientation == 'vertical' else QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(5, 5, 5, 5)  # margin for border

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
        palette.setColor(QPalette.Base, QColor(self.backgroundColor))
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
                progress_bar_layout.setContentsMargins(0, 0, 0, 0)  # Supprime les marges pour gérer le cas où le texte déborde de la taille de la progressBar
                progress_bar_layout.addWidget(self.value_label)
                self.progress_bar.setLayout(progress_bar_layout)
            if self.title_text is not None and self.title_position == 'below' : layout.addWidget(self.title_label)
            # layout.addWidget(self.value_label)
            # self.value_label.setParent(self.progress_bar)
            # self.value_label.move(int(self.progress_bar.width()/2)-5,int(self.progress_bar.height()/2))


        else:
            vbox = QVBoxLayout()
            if self.title_text is not None and self.title_position == 'above' : vbox.addWidget(self.title_label)
            vbox.addWidget(self.progress_bar)
            if self.display_value_on_top:
                progress_bar_layout = QVBoxLayout()
                progress_bar_layout.setContentsMargins(0, 0, 0, 0)  # Supprime les marges pour gérer le cas où le texte déborde de la taille de la progressBar
                progress_bar_layout.addWidget(self.value_label)
                self.progress_bar.setLayout(progress_bar_layout)       
            if self.title_text is not None and self.title_position == 'below' : vbox.addWidget(self.title_label)
            layout.addLayout(vbox)
            
            # vbox = QVBoxLayout()
            # vbox.addWidget(self.label_widget)
            # self.value_label.setParent(self.progress_bar)
            # value_label_y_coord = int(self.progress_bar.height()/4) if self.progress_bar.height() >= 25 else 0
            # self.value_label.move(int(self.progress_bar.width()/2),value_label_y_coord)
            # vbox.addWidget(self.progress_bar)
            # layout.addLayout(vbox)

        self.setLayout(layout)

    def paintEvent(self, event):
        """Custom paint to draw a border around the widget."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(self.borderColor))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(QBrush(Qt.NoBrush))
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))

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
                    break

        # Threshold callbacks
        for threshold_value, callbacks in self.thresholds.items():
            up_cb, down_cb = callbacks
            if val >= threshold_value and up_cb:
                up_cb()
            elif val < threshold_value and down_cb:
                down_cb()

    def setBarColor(self, color):
        """Set the progress bar's color."""
        palette = self.progress_bar.palette()
        palette.setColor(QPalette.Highlight, QColor(color))
        self.progress_bar.setPalette(palette)

    def setThresholdValue(self, value, on_up=None, on_down=None):
        """Set callbacks for when the variable crosses a threshold."""
        self.thresholds[value] = (on_up, on_down)

    def getSizeXGlobal(self):
        """Return the global X size of the gauge."""
        return self.width()

    def getSizeYGlobal(self):
        """Return the global Y size of the gauge."""
        return self.height()
