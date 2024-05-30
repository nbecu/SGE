import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QComboBox, QWidget, QSlider, QLabel, QPushButton, QLineEdit
from PyQt5.QtCore import pyqtSignal

from mainClasses.SGDiagramController import SGDiagramController
from PyQt5.QtCore import Qt

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
        self.toolbar = SGDiagramController(self.canvas, self, parent, 'plot')

        self.layout.addWidget(self.toolbar)

        #self.layout = QVBoxLayout()
        #self.central_widget.setLayout(self.layout)
        self.layout.addWidget(self.canvas)

        self.toolbar.set_data()
        # self.toolbar.update_plot() Commenté car c'est déjà appellé dans set_data()

    def add_interval(self):
        start = self.start_line_edit.text()
        end = self.end_line_edit.text()

        try:
            start = float(start)
            end = float(end)
            interval = (start, end)
            print("Intervalle ajouté:", interval)
            # Vous pouvez ajouter ici le code pour stocker cet intervalle dans une liste ou un autre conteneur.
        except ValueError:
            print("Veuillez entrer des nombres valides pour le début et la fin de l'intervalle.")

    def closeEvent(self, *args, **kwargs):
        self.parent.openedGraphs.remove(self)
        super(QMainWindow, self).closeEvent(*args, **kwargs)
        