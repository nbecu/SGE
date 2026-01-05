import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor
from mainClasses.SGProgressGauge import SGProgressGauge 

# SimVariable simplifiée
class SimVariable:
    def __init__(self, name, value=0):
        self.name = name
        self.value = value
        self.watchers = []

    def addWatcher(self, watcher):
        if watcher not in self.watchers:
            self.watchers.append(watcher)

    def setValue(self, val):
        self.value = val
        for w in self.watchers:
            w.checkAndUpdate()

    def incValue(self, delta):
        self.setValue(self.value + delta)

# Fenêtre de test
class TestTemperature(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Température Four Industriel")
        layout = QVBoxLayout()

        self.temperature = SimVariable("Température", -20)

        self.jaugeTemp = SGProgressGauge(self, self.temperature, -20, 160, "Température four (°C)")
        self.jaugeTemp.setThresholdValue(120, lambda: print("⚠️ Surchauffe détectée !"), None)
        self.jaugeTemp.setThresholdValue(0, None, lambda: print("❄️ Température négative !"))

        layout.addWidget(self.jaugeTemp)

        btn_start = QPushButton("Démarrer simulation")
        btn_start.clicked.connect(self.startSimulation)
        layout.addWidget(btn_start)

        self.setLayout(layout)

    def startSimulation(self):
        self.temp = -20
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTemp)
        self.timer.start(200)  # toutes les 200 ms

    def updateTemp(self):
        self.temperature.setValue(self.temp)
        self.temp += 5
        if self.temp > 160:
            self.timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TestTemperature()
    win.show()
    sys.exit(app.exec_())
