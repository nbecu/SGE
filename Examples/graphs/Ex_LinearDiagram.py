

"""import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class ExamplesWindow(QMainWindow):
    def __init__(self):
        super(ExamplesWindow, self).__init__()

        # Créer une figure Matplotlib
        self.figure, self.ax = plt.subplots()
        x = np.arange(0, 10, 0.1)
        y1 = np.sin(x)
        y2 = np.sin(x + 90)
        self.line1, = self.ax.plot(x, y1, label="")
        self.line2, = self.ax.plot(x, y2, label="")
        self.ax.legend()
        #self.ax.plot([1, 2, 3, 4], [10, 5, 20, 15])  # Exemple de tracé

        # Créer un canevas Matplotlib pour la figure
        self.canvas = FigureCanvas(self.figure)

        # Ajouter le canevas à la fenêtre principale
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        # Créer un widget pour le canevas
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        icon = QIcon('./icon/linear_diagram.png')

        # Définir l'icône de la fenêtre principale
        self.setWindowIcon(icon)
        # Définir le titre de la fenêtre Qt
        self.setWindowTitle("Evolution des données")

if __name__ == '__main__':
    app = QApplication([])
    window = ExamplesWindow()
    window.show()
    app.exec_()"""


"""import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGLinearDiagram import SGLinearDiagram
import numpy as np

# Initialisation des données
x = np.arange(0, 10, 0.1)
y1 = np.sin(x)
y2 = np.sin(x+200)
#title = "Exemple de simulation avec un diagramme d'évolution des données"
label1 = "Fréquence : Model 1"
label2 = "Fréquence : Model 2"

monApp = SGLinearDiagram(x, y1, y2, "", "", "")

monApp.display()

# Très bien cet exemple
# Il y a peut etre une difficulté à anticiper, à savoir que dans le cas de graphiques d'évolution (qui vont utuiliser des LinearDiagram),
# au début de la simulation il y aura des valeurs en abscice à 0 ou à 1 (Tour 0 ou Tour 1), puis au fur et à mesure des tours il y aura des valeurs en abcice à 2, 3, 4, 5... etc....
# Donc, en fait la courbe va "s'étendre" au fur et à mesure  (donc il faudra que le X-max du graphique soit actualiser automatiquement  // pour l'instant ds cet exemple le X-max est fixé à 10 et ne change pas )
# Pour info, il y aura rarement des cas qui iront à plus de 50 ou de 100 Tours ; la plupart du temps ça ira jusqu'à 10 tours
"""