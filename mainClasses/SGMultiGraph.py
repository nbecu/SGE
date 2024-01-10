import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class SGMultiGraph():
    def __init__(self):
        #super(SGMultiGraph, self).__init__()

        self.fig, self.axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 8))
        self.fig.suptitle('', fontsize=16)
        # Créer une figure Matplotlib
        self.createView()

    def createView(self):
        # Définir des données fictives
        x = np.linspace(0, 10, 100)
        y_linear = x
        y_stackplot_1 = np.sin(x)
        y_stackplot_2 = np.cos(x)
        y_stackplot_3 = np.sin(x+180)
        y_bar = [3, 7, 2, 5, 8]
        labels_pie = ['', '', '']
        sizes_pie = [15, 40, 35]
        # Créer une fenêtre personnalisable
        # Diagramme linéaire
        #self.figure, axes = plt.subplots()
        x = np.arange(0, 10, 0.1)
        y1 = np.sin(x)
        y2 = np.sin(x + 90)
        self.axes[0, 0].plot(x, y1, label='')
        self.axes[0, 0].plot(x, y2, label='')
        self.axes[0, 0].set_title('')
        self.axes[0, 0].legend()

        # Stackplot
        self.axes[0, 1].stackplot(x, y_stackplot_1, y_stackplot_2, y_stackplot_3, labels=['', '', ''], colors=['orange', 'green', 'blue'])
        self.axes[0, 1].set_title('')
        self.axes[0, 1].set_xlabel('')
        self.axes[0, 1].set_ylabel('')
        self.axes[0, 1].legend()

        # Diagramme en barres
        self.axes[1, 0].bar(range(len(y_bar)), y_bar, color='blue')
        self.axes[1, 0].set_title('')
        self.axes[1, 0].set_xlabel('')
        self.axes[1, 0].set_ylabel('')

        # Diagramme circulaire (Pie Chart)
        self.axes[1, 1].pie(sizes_pie, labels=labels_pie, autopct='%1.1f%%', startangle=90,
                       colors=['red', 'yellow', 'green'])
        self.axes[1, 1].set_title('')

        # Ajuster l'espacement entre les sous-graphiques
        self.fig.tight_layout(rect=[0, 0, 1, 0.96])

        # Créer un canevas Matplotlib pour la figure
        self.canvas = FigureCanvas(self.fig)
        # Ajouter le canevas à la fenêtre principale
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        # Créer un widget pour le canevas
        widget = QWidget()
        widget.setLayout(layout)
        #self.setCentralWidget(widget)

        icon = QIcon('./icon/linear_diagram.png')

        # Définir l'icône de la fenêtre principale
        #self.setWindowIcon(icon)
        # Définir le titre de la fenêtre Qt
        #self.setWindowTitle("Multi Graphique")

        # Afficher les graphiques
        #plt.show()
    def display(self):
        plt.show()

"""if __name__ == '__main__':
    app = QApplication([])
    window = SGMultiGraph()
    window.show()
    app.exec_()"""

