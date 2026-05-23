import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from mainClasses.SGGraphController import SGGraphController


_TITLES = {
    "linear":    "Diagramme d'évolution linéaire",
    "hist":      "Histogramme",
    "pie":       "Diagramme Circulaire",
    "stackplot": "Diagramme Stack Plot",
}


class SGBaseGraphWindow(QMainWindow):
    """
    Single parameterized graph window replacing the four near-identical classes
    SGGraphLinear / SGGraphHistogram / SGGraphCircular / SGGraphStackPlot.

    Usage (internal, via SGGraphWindow factory or SGModel):
        w = SGBaseGraphWindow(model, "linear")
        w.show()
    """

    def __init__(self, model, graph_type):
        super().__init__()
        self.model = model
        self.graph_type = graph_type

        self.setWindowTitle(_TITLES.get(graph_type, "Graph"))
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = SGGraphController(self.canvas, self, model, graph_type)

        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.toolbar.set_data()

    def closeEvent(self, event):
        if self in self.model.openedGraphs:
            self.model.openedGraphs.remove(self)
        super().closeEvent(event)
