import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QComboBox, QWidget
from PyQt5.QtCore import pyqtSignal

from mainClasses.layout.SGToolBar import SGToolBar


class SGDiagramCircular(QMainWindow):
    update_data_signal = pyqtSignal()
    def __init__(self, parent=None):
        super(SGDiagramCircular, self).__init__(parent)
        self.parent = parent

        self.setWindowTitle("Diagramme Circulaire")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        #self.figure = plt.figure()
        self.figure, self.ax = plt.subplots()

        #self.xValue = []

        self.canvas = FigureCanvas(self.figure)
        self.toolbar = SGToolBar(self.canvas, self, parent, 'pie')

        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

        #self.data = self.getAllHistoryData()
        self.toolbar.set_data({'cell': 0, 'agent': 1})
        self.toolbar.update_plot()

    def getAllHistoryData(self):
        historyData = []
        for aEntity in self.parent.getAllEntities():
            h = aEntity.getHistoryDataJSON()
            historyData.append(h)
        return historyData


    def update_data(self):
        data = self.getAllHistoryData()
        phases = set(entry['phase'] for entry in data)
        rounds = set(entry['round'] for entry in data)
        #self.xValue = [r * len(phases) + p for r in rounds for p in phases]



"""import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import pyqtSignal
import numpy as np
import matplotlib.pyplot as plt

from mainClasses.layout.SGToolBar import SGToolBar


class SGDiagramCircular(QMainWindow):
    update_data_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(SGDiagramCircular, self).__init__(parent)
        self.parent = parent
        self.cell_data = []
        self.agent_data = []

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        self.toolbar = SGToolBar(self.canvas, self, "pie")

        #self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

        self.update_button = QPushButton('Mettre à jour le diagramme', self)
        self.update_button.clicked.connect(self.update_plot)
        self.layout.addWidget(self.update_button)

        self.update_data_signal.connect(self.update_plot)

        self.getAllData()

        self.plot()


    def getAllHistoryData(self):
        historyData = []
        for aEntity in self.parent.getAllEntities():
            h = aEntity.getHistoryDataJSON()
            historyData.append(h)
        return historyData

    def getAllData(self):
        data = self.getAllHistoryData()
        phases = set(entry['phase'] for entry in data)
        rounds = set(entry['round'] for entry in data)
        self.cell_data = [
            sum(1 for entry in data if entry['round'] == r and entry['phase'] == p and entry['entityDef'] == 'Cell')
            for r in rounds for p in phases]
        self.agent_data = [
            sum(1 for entry in data if entry['round'] == r and entry['phase'] == p and entry['entityDef'] == 'Agent')
            for r in rounds for p in phases]

    def update_plot(self):
        self.getAllData()
        self.ax.clear()

        labels = ['Cell', 'Agent']
        sizes = [sum(self.cell_data), sum(self.agent_data)]

        self.ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        self.ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        self.canvas.draw()
        print("Update ok")
        print("sizes :: ", sizes)

    def plot(self):
        self.getAllData()
        self.ax.clear()

        labels = ['Cell', 'Agent']
        sizes = [sum(self.cell_data), sum(self.agent_data)]

        self.ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        self.ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        self.canvas.draw()
"""