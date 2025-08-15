from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QProgressBar

from mainClasses.SGGameSpace import SGGameSpace


class SGProgressGauge(SGGameSpace):
    def __init__(
        self, parent, simVar, title, maximum, minimum,
        dictOfMappedValues=None, orientation="horizontal",
        colorRanges=None, borderColor=Qt.black, backgroundColor=Qt.lightGray
    ):
        super().__init__(parent, 0, 60, 0, 0, True, backgroundColor)
        self.title = title
        self.id = title
        self.model = parent
        self.simVar = simVar
        self.maximum = maximum
        self.minimum = minimum
        self.borderColor = borderColor
        self.backgroundColor = backgroundColor
        self.simVar.addWatcher(self)  # Attach as observer
        self.valueRange = maximum - minimum
        self.thresholds = {}
        self.previousValue = self.simVar.value
        self.dictOfMappedValues = dictOfMappedValues or {}
        self.orientation = orientation.lower()
        self.colorRanges = colorRanges or []  # list of tuples (minVal, maxVal, QColor)
        self._size_x = None
        self._size_y = None
        self.init_ui()

    def init_ui(self):
        """Initialize the gauge's UI layout and style."""
        # Main layout: always vertical so the label is on top
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        # Title label setup
        self.title_label = QtWidgets.QLabel(self.title, self)
        self.title_label.setAlignment(Qt.AlignCenter)
        font = self.title_label.font()
        font.setPointSize(font.pointSize() + 1)
        self.title_label.setFont(font)

        # Progress bar setup
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setMinimum(self.minimum)
        self.progress_bar.setMaximum(self.maximum)
        self.progress_bar.setFormat(f"{int(self.simVar.value)}")

        # Configure orientation
        if self.orientation == "vertical":
            self.progress_bar.setOrientation(Qt.Vertical)
            # Create a horizontal layout to center the vertical bar
            h_center_layout = QtWidgets.QHBoxLayout()
            h_center_layout.addStretch(1)
            h_center_layout.addWidget(self.progress_bar)
            h_center_layout.addStretch(1)

            self.layout.addWidget(self.title_label)
            self.layout.addLayout(h_center_layout, stretch=1)
            # self.layout.addWidget(self.progress_bar, stretch=1)

        else:
            self.progress_bar.setOrientation(Qt.Horizontal)
            self.layout.addWidget(self.title_label)
            self.layout.addWidget(self.progress_bar)

        # Apply layout
        self.setLayout(self.layout)
        self.setWindowTitle(self.title)

        # Set initial mapped value
        self.progress_bar.setValue(int(self.getMappedValue(str(self.simVar.value))))

        # Compute and apply default size
        default_x, default_y = self._compute_default_size()
        self._size_x, self._size_y = default_x, default_y
        self.resize(default_x, default_y)

        # Show the gauge
        self.show()

    def _compute_default_size(self):
        """Compute default width and height based on orientation and title length."""
        if self.orientation == "vertical":
            width = max(80, len(self.title) * 8)
            height = 160
        else:
            width = 180
            height = 65
        return width, height

    def paintEvent(self, event):
        """Custom paint event to draw the background and border."""
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QBrush(self.backgroundColor, Qt.SolidPattern))
        painter.setPen(QPen(self.borderColor, 1))
        self.setMinimumSize(self.getSizeXGlobal() + 3, self.getSizeYGlobal() + 3)
        painter.drawRect(0, 0, self.getSizeXGlobal(), self.getSizeYGlobal())
        painter.end()

    def checkAndUpdate(self):
        """Refresh the progress bar display."""
        self.updateProgressBar()

    def updateProgressBar(self):
        """Update the progress bar value and apply dynamic color if needed."""
        newValue = self.simVar.value
        mappedValue = self.getMappedValue(str(newValue))
        self.progress_bar.setValue(int(mappedValue))
        self.progress_bar.setFormat(f"{newValue}")

        # Apply dynamic color ranges if configured
        self.applyColorForValue(newValue)

        self.checkThresholds(newValue)

    def applyColorForValue(self, value):
        """Change progress bar color depending on the value range."""
        for minVal, maxVal, color in self.colorRanges:
            if minVal <= value <= maxVal:
                # Style using stylesheet to change chunk color
                self.progress_bar.setStyleSheet(
                    f"QProgressBar::chunk {{ background-color: {color.name()}; }}"
                )
                return
        # Reset to default if no range matches
        self.progress_bar.setStyleSheet("")

    def setThresholdValue(self, thresholdValue, onCrossUp=None, onCrossDown=None):
        """Add a threshold with optional up/down crossing callbacks."""
        self.thresholds[thresholdValue] = [onCrossUp, onCrossDown]

    def checkThresholds(self, newValue):
        """Check threshold crossings and trigger associated callbacks."""
        for threshold, (crossUp, crossDown) in self.thresholds.items():
            if newValue >= int(threshold) and (self.previousValue is None or self.previousValue < int(threshold)):
                if crossUp:
                    crossUp()
            elif newValue < int(threshold) and (self.previousValue is None or self.previousValue >= int(threshold)):
                if crossDown:
                    crossDown()
        self.previousValue = newValue

    def setDictOfMappedValues(self, aDictOfMappedValues):
        """Set mapping dictionary for simulation variable to progress bar value."""
        self.dictOfMappedValues = aDictOfMappedValues

    def getMappedValue(self, key):
        """Get mapped progress bar value for a simulation variable value."""
        value = self.dictOfMappedValues.get(key)
        if value is not None:
            return value
        else:
            # If no mapping, scale linearly within min/max range
            try:
                numeric_key = float(key)
                normalized = (numeric_key - self.minimum) / (self.maximum - self.minimum)
                return normalized * 100
            except ValueError:
                return 0

    # Methods for global size retrieval
    def getSizeXGlobal(self):
        return self._size_x if self._size_x is not None else self._compute_default_size()[0]

    def getSizeYGlobal(self):
        return self._size_y if self._size_y is not None else self._compute_default_size()[1]
