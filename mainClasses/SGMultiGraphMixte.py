import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QBoxLayout, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np


class SGMultiGraphMixte():
    def __init__(self):
        self.initView()

    def initView(self):
        # Données pour les graphiques
        x = np.linspace(0, 10, 100)
        y_linear = x
        y_stackplot1 = np.sin(x)
        y_stackplot2 = np.cos(x)
        bar_labels = ['Catégorie 1', 'Catégorie 2', 'Catégorie 3']
        bar_values = [3, 5, 2]
        pie_labels = ['Partie 1', 'Partie 2', 'Partie 3']
        pie_values = [2, 4, 3]

        # Stackplot
        plt.figure(1)
        plt.stackplot(x, y_stackplot1, y_stackplot2, labels=['Sin(x)', 'Cos(x)'])
        plt.title('Stackplot')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.legend()

        # Diagramme circulaire
        plt.figure(2)
        plt.pie(pie_values, labels=pie_labels, autopct='%1.1f%%')
        plt.title('Diagramme Circulaire')

        # Diagramme en barres
        plt.figure(3)
        plt.bar(bar_labels, bar_values)
        plt.title('Diagramme en Barres')

        # Diagramme linéaire
        #plt.figure(4)
        plt.plot(x, y_linear)
        plt.title('Diagramme Linéaire')
        plt.xlabel('X')
        plt.ylabel('Y')



        # Afficher les fenêtres
        #plt.show()

        line_chart_window = plt.get_current_fig_manager().window
        line_chart_window.setGeometry(100, 200, 400, 400)

        bar_chart_window = plt.get_current_fig_manager().window
        bar_chart_window.setGeometry(100, 50, 400, 400)

        # Positionner les fenêtres dans les coins de l'écran
        stackplot_window = plt.get_current_fig_manager().window
        stackplot_window.setGeometry(-50, 50, 800, 400)

        #pie_chart_window = plt.get_current_fig_manager().window
        #pie_chart_window.setGeometry(0, 150, 400, 400)

        plt.show()
