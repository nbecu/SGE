import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QComboBox, QWidget, QSlider, QLabel, QPushButton, QLineEdit
from PyQt5.QtCore import pyqtSignal

from mainClasses.SGGraphController import SGGraphController
from PyQt5.QtCore import Qt

class SGGraphLinear(QMainWindow):
    # update_data_signal = pyqtSignal()
    def __init__(self, parent=None):
        super(SGGraphLinear, self).__init__(parent)
        self.parent = parent

        self.setWindowTitle("Diagramme d'évolution linéaire")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        
        self.figure, self.ax = plt.subplots()

        self.canvas = FigureCanvas(self.figure)
        self.toolbar = SGGraphController(self.canvas, self, parent, 'linear')

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

        self.toolbar.set_data()


    def closeEvent(self, *args, **kwargs):
        self.parent.openedGraphs.remove(self)
        super(QMainWindow, self).closeEvent(*args, **kwargs)
        