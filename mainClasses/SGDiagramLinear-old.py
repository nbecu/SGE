import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QAction
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import pyqtSignal

from mainClasses.layout.SGToolBar import SGToolBar


class SGDiagramLinear(QMainWindow):
    update_data_signal = pyqtSignal()
    def __init__(self, parent=None):
        super(SGDiagramLinear, self).__init__(parent)
        self.parent = parent
        self.data = []
        self.xValue= []
        self.cell_data = []
        self.agent_data = []

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        self.toolbar = SGToolBar(self.canvas, self, "plot")

        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

        self.update_button = QPushButton('Mettre à jour le diagramme', self)
        self.update_button.clicked.connect(self.update_plot)
        self.layout.addWidget(self.update_button)

        self.update_data_signal.connect(self.update_plot)

        self.getAllData()

        self.lines_cell, = self.ax.plot(self.xValue, self.cell_data, label='Cell')
        self.lines_agent, = self.ax.plot(self.xValue, self.agent_data, label='Agent')
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
        self.xValue = [r * len(phases) + p for r in rounds for p in phases]
        self.data = data

    def update_plot(self):
        print("xvalue = ", self.xValue)
        print("agent_data = ", self.agent_data)
        print("cell_data = ", self.cell_data)
        self.getAllData()
        self.ax.clear()
        self.ax.set_xlim(0, max(self.xValue))

        self.lines_cell.set_data(self.xValue, self.cell_data)
        self.lines_agent.set_data(self.xValue, self.agent_data)

        # Redraw the lines
        self.ax.plot(self.xValue, self.cell_data)
        self.ax.plot(self.xValue, self.agent_data)
        self.canvas.draw()
        # Mettez ici le code pour mettre à jour le diagramme
        #self.ax.clear()
        #self.ax.plot(self.xValue, self.cell_data)
        #print("xValue :: ", self.xValue)
        #print("cell_data :: ", self.cell_data)
        #self.canvas.draw()
        #self.canvas.draw()
        print("update ok")
        pass

    def plot(self):
        self.ax.clear()
        self.ax.plot(self.xValue, self.cell_data)
        self.ax.plot(self.xValue, self.agent_data)
        self.ax.set_xlabel('X-axis')
        self.ax.set_ylabel('Y-axis')
        self.canvas.draw()
