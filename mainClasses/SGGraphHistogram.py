import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QComboBox, QWidget
from PyQt5.QtCore import pyqtSignal

from mainClasses.SGGraphController import SGGraphController


class SGGraphHistogram(QMainWindow):
    # update_data_signal = pyqtSignal()
    def __init__(self, parent=None):
        super(SGGraphHistogram, self).__init__(parent)
        self.parent = parent

        self.setWindowTitle("Histogramme")
        self.setGeometry(100, 100, 800, 600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = SGGraphController(self.canvas, self, parent, 'hist')
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.toolbar.set_data()
