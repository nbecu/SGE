import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QComboBox, QWidget
from PyQt5.QtCore import pyqtSignal

from mainClasses.layout.SGToolBar import SGToolBar


class SGDiagramLinear(QMainWindow):
    update_data_signal = pyqtSignal()
    def __init__(self, parent=None):
        super(SGDiagramLinear, self).__init__(parent)
        self.parent = parent

        self.setWindowTitle("Diagramme d'évolution linéaire")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        #self.figure = plt.figure()
        self.figure, self.ax = plt.subplots()

        #self.xValue = []

        self.canvas = FigureCanvas(self.figure)
        self.toolbar = SGToolBar(self.canvas, self, parent, 'plot')

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


