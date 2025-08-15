import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor
from collections import defaultdict
from mainClasses.SGProgressGauge import SGProgressGauge  
from PyQt5.QtCore import Qt
import random
import time

# ======= SimulationVariable de test =======
class SimVariable:
    def __init__(self, name, value=0):
        self.name = name
        self.value = value
        self.watchers = []

    def addWatcher(self, watcher):
        self.watchers.append(watcher)

    def setValue(self, new_value):
        self.value = new_value
        for watcher in self.watchers:
            watcher.checkAndUpdate()

# ======= Test direct avec SGProgressGauge modifié =======
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer

class MyModel(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.gameSpaces = {}

    def newProgressGauge(self, simVar, title, maximum, minimum, 
                         orientation="horizontal", colorRanges=None):
        gauge = SGProgressGauge(self, simVar, title, maximum, minimum,
                                orientation=orientation, colorRanges=colorRanges)
        self.gameSpaces[title] = gauge
        self.layout.addWidget(gauge)
        return gauge

# ======= Version adaptée de SGProgressGauge (simplifiée pour test) =======
from PyQt5.QtWidgets import QProgressBar, QLabel, QVBoxLayout
from PyQt5.QtGui import QPainter, QBrush, QPen

class SGProgressGauge(QWidget):
    def __init__(self, parent, simVar, title, maximum, minimum, 
                 borderColor=Qt.black, backgroundColor=Qt.lightGray,
                 orientation="horizontal", colorRanges=None):
        super().__init__(parent)
        self.title = title
        self.simVar = simVar
        self.maximum = maximum
        self.minimum = minimum
        self.borderColor = borderColor
        self.backgroundColor = backgroundColor
        self.orientation = orientation
        self.colorRanges = colorRanges or []
        self.simVar.addWatcher(self)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(self.minimum)
        self.progress_bar.setMaximum(self.maximum)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        if self.orientation.lower() == "vertical":
            self.progress_bar.setOrientation(Qt.Vertical)

        layout.addWidget(self.progress_bar)
        self.setLayout(layout)
        self.updateProgressBar()

    def checkAndUpdate(self):
        self.updateProgressBar()

    def updateProgressBar(self):
        newValue = self.simVar.value
        self.progress_bar.setValue(int(newValue))
        self.progress_bar.setFormat(f"{newValue:.1f}")

        # Appliquer couleur en fonction de plage
        for min_val, max_val, color in self.colorRanges:
            if min_val <= newValue <= max_val:
                self.progress_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")
                break

# ======= MAIN : Création des jauges =======
def run_test():
    app = QApplication(sys.argv)
    model = MyModel()

    # Variables de simulation avec ranges différents
    temperature = SimVariable("Température", 15)  # range: -30 → 50
    vitesse = SimVariable("Vitesse", 80)          # range: 0 → 200
    satisfaction = SimVariable("Satisfaction", 50) # range: 0 → 100

    # Ajout des jauges
    model.newProgressGauge(
        temperature, "Température", 50, -30,
        orientation="horizontal",
        colorRanges=[(-30, 0, "blue"), (0, 25, "green"), (25, 50, "red")]
    )

    model.newProgressGauge(
        vitesse, "Vitesse", 200, 0,
        orientation="vertical",
        colorRanges=[(0, 50, "green"), (50, 150, "orange"), (150, 200, "red")]
    )

    model.newProgressGauge(
        satisfaction, "Satisfaction", 100, 0,
        orientation="horizontal",
        colorRanges=[(0, 40, "red"), (40, 70, "yellow"), (70, 100, "green")]
    )

    # Timer pour faire varier les valeurs automatiquement
    def update_values():
        temperature.setValue(random.randint(-30, 50))
        vitesse.setValue(random.randint(0, 200))
        satisfaction.setValue(random.randint(0, 100))

    timer = QTimer()
    timer.timeout.connect(update_values)
    timer.start(1000)

    model.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_test()
