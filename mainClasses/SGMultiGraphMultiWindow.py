import matplotlib.pyplot as plt
import numpy as np


class SGMultiGraphMultiWindow:
    def __init__(self):
        self.initView()

    def initView(self):
        # Données pour les graphiques
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)
        y3 = np.exp(-x)
        categories = ['Sheeps', 'Forest', 'Grass']
        values = [35, 30, 35]

        # Stackplot
        plt.figure()
        plt.stackplot(x, y1, y2, labels=['Agents', 'Cells'])
        plt.title('Stackplot')
        plt.legend()
        #plt.show()

        # Diagramme circulaire
        plt.figure()
        plt.pie(values, labels=categories, autopct='%1.1f%%')
        plt.title('Diagramme Circulaire')
        #plt.show()

        # Diagramme linéaire
        plt.figure()
        plt.plot(x, y3)
        plt.title('Diagramme Linéaire')
        #plt.show()

        # Diagramme en barres
        plt.figure()
        plt.bar(categories, values)
        plt.title('Diagramme en Barres')
        #plt.show()

        line_chart_window = plt.get_current_fig_manager().window
        line_chart_window.setGeometry(100, 200, 400, 400)

        bar_chart_window = plt.get_current_fig_manager().window
        bar_chart_window.setGeometry(100, 50, 400, 400)

        # Positionner les fenêtres dans les coins de l'écran
        stackplot_window = plt.get_current_fig_manager().window
        stackplot_window.setGeometry(-50, 50, 800, 400)

        pie_chart_window = plt.get_current_fig_manager().window
        pie_chart_window.setGeometry(0, 150, 400, 400)

        plt.show()
