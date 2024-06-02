import sys

import numpy as np
from PyQt5.QtWidgets import QApplication, QMessageBox, QLabel, QWidget, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

#from mainClasses.SGDiagram import SGDiagram
from mainClasses.SGGraphCircular import SGGraphCircular
from mainClasses.SGGraphHistogram import SGGraphHistogram
from mainClasses.SGGraphLinear import SGGraphLinear
from mainClasses.SGGraphStackPlot import SGGraphStackPlot
from mainClasses.SGMultiGraphMultiWindow import SGMultiGraphMultiWindow



class SGGraphWindow(QWidget):
    def __init__(self, model):
        super(SGGraphWindow, self).__init__()
        layout = QGridLayout(self)
        self.model = model


    def showErrorMessage(self):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Warning)
        error_dialog.setWindowTitle("Unable to display the window")
        error_dialog.setText("Please start by playing two rounds or two phases before selecting the type of graph.\n\n"
                             "Example: Click the play button (>) at least twice")
        error_dialog.setStandardButtons(QMessageBox.Ok)
        error_dialog.exec_()

    def open_graph_type(self, graph_type):
        graph_classes = {
            'linear': SGGraphLinear,
            'circular': SGGraphCircular,
            'stackplot': SGGraphStackPlot,
            'histogram': SGGraphHistogram
        }
        graph_class = graph_classes.get(graph_type)
        if graph_class:
            if len(self.model.dataRecorder.getStats_ofEntities()) > 2:
                graph = graph_class(self.model)
                graph.show()
                return graph
            else:
                self.showErrorMessage()
                return None
