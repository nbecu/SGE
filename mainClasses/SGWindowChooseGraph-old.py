
import sys

import numpy as np
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QLabel, QVBoxLayout, QWidget, \
    QHBoxLayout, QFrame, QPushButton, QAction, QGraphicsPixmapItem
from PyQt5.QtCore import Qt

from mainClasses.SGLinearDiagram import SGLinearDiagram


class SGWindowChooseGraph(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # Initialisation de l'interface utilisateur de la deuxième fenêtre ici
        #self.setGeometry(200, 200, 400, 300)
        self.setWindowTitle('Choisir le type de données selon le diagramme')
        self.createDiagramme()


    def openNewDiagram(self):
        print("cliekr")
        """x = np.arange(0, 40, 0.1)
        y1 = np.sin(x)
        y2 = np.sin(x)
        title = "Exemple de simulation avec un diagramme d'évolution des données"
        label1 = "Fréquence : Model 1"
        label2 = "Fréquence : Model 2"

        monApp = SGLinearDiagram(x, y1, y2, label1, label2, title)
        monApp.display()"""

    def createDiagramme(self):
        scene = QGraphicsScene(self)
        image_path = "./icon/linear_diagram.png"  # Remplacez ceci par le chemin de votre image
        pixmap_item = QGraphicsPixmapItem(QPixmap(image_path))
        scene.addItem(pixmap_item)

        action = QAction("Votre Action", self)
        action.triggered.connect(self.openNewDiagram)

        scene.addAction(self.action)

        # Configuration de la vue
        view = QGraphicsView(scene)
        self.setCentralWidget(view)


        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Ajouter QAction dans une image')
        self.show()

    """
        def createDiagramme(self):
        layout = QVBoxLayout(self)
        ligne1 = QHBoxLayout()
        ligne2 = QHBoxLayout()

        sp_line = QFrame()
        sp_line.setFrameShadow(QFrame.Sunken)

        vligne1 = QVBoxLayout(self)
        label = QLabel(self)
        histogram = QPixmap("./icon/histogram_diagram.png")
        label.setPixmap(histogram)
        vligne1.addWidget(label)
        bouton1 = QPushButton('Répartition de la population', self)
        bouton2 = QPushButton('Répartition parmi la population des Players', self)

        bouton1.setStyleSheet('QLabel { font-weight: bold }')
        bouton2.setStyleSheet('QLabel { font-weight: bold }')
        vligne1.addWidget(bouton1)
        vligne1.addWidget(bouton2)
        sp_line.setFrameShape(QFrame.HLine)
        vligne1.addWidget(sp_line)
        ligne1.addLayout(vligne1)


        label = QLabel(self)
        vligne1 = QVBoxLayout(self)
        circular = QPixmap("./icon/circular_diagram.png")
        circular.scaledToWidth(50)

        label.setPixmap(circular)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        ligne1.addWidget(label)
        vligne1.addWidget(label)
        bouton1 = QPushButton('Répartition de la population', self)
        bouton2 = QPushButton('Répartition parmi la population des Players', self)

        bouton1.setStyleSheet('QLabel { font-weight: bold }')
        bouton2.setStyleSheet('QLabel { font-weight: bold }')
        vligne1.addWidget(bouton1)
        vligne1.addWidget(bouton2)
        sp_line.setFrameShape(QFrame.HLine)
        vligne1.addWidget(sp_line)
        ligne1.addLayout(vligne1)

        # Diagramme lineaire
        label = QLabel(self)
        vligne1 = QVBoxLayout(self)
        linear = QPixmap("./icon/linear_diagram.png")
        linear.scaledToWidth(50)
        label.setPixmap(linear)
        ligne2.addWidget(label)
        bouton1 = QPushButton('Données des entités SGEntities', self)
        act = QAction("Diagramme d'évolution", self)
        act.triggered.connect(self.openNewDiagram)
        bouton1.addAction(act)
        bouton2 = QPushButton('Données des entités SGEntities et SimVariables', self)
        bouton3 = QPushButton('Données des Players', self)

        bouton1.setStyleSheet('QLabel { font-weight: bold }')
        bouton2.setStyleSheet('QLabel { font-weight: bold }')
        bouton3.setStyleSheet('QLabel { font-weight: bold }')
        vligne1.addWidget(bouton1)
        vligne1.addWidget(bouton2)
        vligne1.addWidget(bouton3)
        sp_line.setFrameShape(QFrame.HLine)
        vligne1.addWidget(sp_line)
        ligne2.addLayout(vligne1)


        label = QLabel(self)
        vligne1 = QVBoxLayout(self)
        stackplot = QPixmap("./icon/stackplot_diagram.png")
        label.setPixmap(stackplot)
        ligne2.addWidget(label)
        bouton1 = QPushButton('Données en temps réelles', self)
        bouton1.setStyleSheet('QLabel { font-weight: bold }')
        vligne1.addWidget(bouton1)
        sp_line.setFrameShape(QFrame.HLine)
        vligne1.addWidget(sp_line)
        ligne2.addLayout(vligne1)


        layout.addLayout(ligne1)
        sp_line = QFrame()
        sp_line.setFrameShape(QFrame.HLine)
        sp_line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(sp_line)
        layout.addLayout(ligne2)
        self.setLayout(layout)
        self.setGeometry(100, 100, 800, 500)
    """
"""
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QBoxLayout, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np

class SGWindowChooseGraph(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Layout principal
        layout = QHBoxLayout(self)
        layoutCol1 = QVBoxLayout(self)
        layoutCol2 = QVBoxLayout(self)

        # Ajouter les graphiques à la fenêtre
        self.addGraph(layoutCol1, self.createLinearGraph(), 'Evolution des Données SGE ')
        self.addGraph(layoutCol1, self.createPieChart(), 'Données SGE des Cells')
        self.addGraph(layoutCol2, self.createBarChart(), 'Evolution des Données SGE avec un histogramme')
        self.addGraph(layoutCol2, self.createStackPlot(), 'Evolution des Données SGE avec un Stack Plot')

        layout.addLayout(layoutCol1)
        layout.addLayout(layoutCol2)
        self.setLayout(layout)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Choose Graph Modal')

    def addGraph(self, layout, figure, title):
        # Créer une toile Matplotlib
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)

        # Ajouter un titre au graphique
        canvas.figure.suptitle(title, fontsize=16)

    def createLinearGraph(self):
        # Exemple de graphique linéaire
        fig, ax = plt.subplots()
        x = np.linspace(0, 10, 100)
        y = x**2
        ax.plot(x, y)
        return fig

    def createPieChart(self):
        # Exemple de graphique en secteurs (pie chart)
        fig, ax = plt.subplots()
        labels = ['Grass ', 'Shrub', 'Forest']
        sizes = [25, 40, 35]
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        return fig

    def createBarChart(self):
        # Exemple de graphique à barres
        fig, ax = plt.subplots()
        categories = ['Admin', 'Player 1', 'Player 2']
        values = [30, 50, 20]
        ax.bar(categories, values)
        return fig

    def createStackPlot(self):
        # Exemple de graphique stackplot
        fig, ax = plt.subplots()
        x = np.linspace(0, 10, 100)
        y1 = x
        y2 = x**2
        y3 = x**3
        ax.set_xlabel('Round ')
        #ax.axis(['Round 1', 'Round 2', 'Round 3'])
        ax.stackplot(x, y1, y2, y3, labels=['Admin', 'Player 1', 'Player 2'])
        ax.legend(loc='upper left')
        return fig

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SGWindowChooseGraph()
    window.show()
    sys.exit(app.exec_())
"""

"""

import sys

import numpy as np
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QLabel, QVBoxLayout, QWidget, \
    QHBoxLayout, QFrame, QPushButton, QAction
from PyQt5.QtCore import Qt

from mainClasses.SGLinearDiagram import SGLinearDiagram


class SGWindowChooseGraphModal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # Initialisation de l'interface utilisateur de la deuxième fenêtre ici
        #self.setGeometry(200, 200, 400, 300)
        self.setWindowTitle('Choisir le type de données selon le diagramme')
        self.createDiagramme()


    def openNewDiagram(self):
        print("cliekr")
        x = np.arange(0, 40, 0.1)
        y1 = np.sin(x)
        y2 = np.sin(x)
        title = "Exemple de simulation avec un diagramme d'évolution des données"
        label1 = "Fréquence : Model 1"
        label2 = "Fréquence : Model 2"

        monApp = SGLinearDiagram(x, y1, y2, label1, label2, title)
        monApp.display()

    def createDiagramme(self):
        layout = QVBoxLayout(self)
        ligne1 = QHBoxLayout()
        ligne2 = QHBoxLayout()

        sp_line = QFrame()
        sp_line.setFrameShadow(QFrame.Sunken)

        vligne1 = QVBoxLayout(self)
        label = QLabel(self)
        histogram = QPixmap("./icon/histogram_diagram.png")
        label.setPixmap(histogram)
        vligne1.addWidget(label)
        bouton1 = QPushButton('Répartition de la population', self)
        bouton2 = QPushButton('Répartition parmi la population des Players', self)

        bouton1.setStyleSheet('QLabel { font-weight: bold }')
        bouton2.setStyleSheet('QLabel { font-weight: bold }')
        vligne1.addWidget(bouton1)
        vligne1.addWidget(bouton2)
        sp_line.setFrameShape(QFrame.HLine)
        vligne1.addWidget(sp_line)
        ligne1.addLayout(vligne1)


        label = QLabel(self)
        vligne1 = QVBoxLayout(self)
        circular = QPixmap("./icon/circular_diagram.png")
        circular.scaledToWidth(50)

        label.setPixmap(circular)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        ligne1.addWidget(label)
        vligne1.addWidget(label)
        bouton1 = QPushButton('Répartition de la population', self)
        bouton2 = QPushButton('Répartition parmi la population des Players', self)

        bouton1.setStyleSheet('QLabel { font-weight: bold }')
        bouton2.setStyleSheet('QLabel { font-weight: bold }')
        vligne1.addWidget(bouton1)
        vligne1.addWidget(bouton2)
        sp_line.setFrameShape(QFrame.HLine)
        vligne1.addWidget(sp_line)
        ligne1.addLayout(vligne1)

        # Diagramme lineaire
        label = QLabel(self)
        vligne1 = QVBoxLayout(self)
        linear = QPixmap("./icon/linear_diagram.png")
        linear.scaledToWidth(50)
        label.setPixmap(linear)
        ligne2.addWidget(label)
        bouton1 = QPushButton('Données des entités SGEntities', self)
        act = QAction("Diagramme d'évolution", self)
        act.triggered.connect(self.openNewDiagram)
        bouton1.addAction(act)
        bouton2 = QPushButton('Données des entités SGEntities et SimVariables', self)
        bouton3 = QPushButton('Données des Players', self)

        bouton1.setStyleSheet('QLabel { font-weight: bold }')
        bouton2.setStyleSheet('QLabel { font-weight: bold }')
        bouton3.setStyleSheet('QLabel { font-weight: bold }')
        vligne1.addWidget(bouton1)
        vligne1.addWidget(bouton2)
        vligne1.addWidget(bouton3)
        sp_line.setFrameShape(QFrame.HLine)
        vligne1.addWidget(sp_line)
        ligne2.addLayout(vligne1)


        label = QLabel(self)
        vligne1 = QVBoxLayout(self)
        stackplot = QPixmap("./icon/stackplot_diagram.png")
        label.setPixmap(stackplot)
        ligne2.addWidget(label)
        bouton1 = QPushButton('Données en temps réelles', self)
        bouton1.setStyleSheet('QLabel { font-weight: bold }')
        vligne1.addWidget(bouton1)
        sp_line.setFrameShape(QFrame.HLine)
        vligne1.addWidget(sp_line)
        ligne2.addLayout(vligne1)


        layout.addLayout(ligne1)
        sp_line = QFrame()
        sp_line.setFrameShape(QFrame.HLine)
        sp_line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(sp_line)
        layout.addLayout(ligne2)
        self.setLayout(layout)
        self.setGeometry(100, 100, 800, 500)

"""
"""

import sys

import numpy as np
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QLabel, QVBoxLayout, QWidget, \
    QHBoxLayout, QFrame, QPushButton, QAction
from PyQt5.QtCore import Qt
from matplotlib import pyplot as plt

from mainClasses.SGLinearDiagram import SGLinearDiagram


class SGWindowChooseGraphModal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # Initialisation de l'interface utilisateur de la deuxième fenêtre ici
        # self.setGeometry(200, 200, 400, 300)
        self.setWindowTitle('Choisir le type de données selon le diagramme')
        self.createDiagramme()
        self.openNewDiagram()

    def createActions(self, title):
        # Créez une action pour ouvrir une nouvelle fenêtre avec le diagramme
        self.newDiagramAction = QAction(title, self)
        self.newDiagramAction.triggered.connect(self.openNewDiagram)

    def openNewDiagram(self):
        print("test")
        testGraph = TestGraphView()
        testGraph.init_graph()
    def createDiagramme(self):
        layout = QVBoxLayout(self)
        ligne1 = QHBoxLayout()
        ligne2 = QHBoxLayout()

        sp_line = QFrame()
        sp_line.setFrameShadow(QFrame.Sunken)

        vligne1 = QVBoxLayout()
        label = QLabel(self)
        histogram = QPixmap("./icon/histogram_diagram.png")
        label.setPixmap(histogram)
        vligne1.addWidget(label)
        bouton1 = QPushButton('Répartition de la population', self)
        bouton2 = QPushButton('Répartition parmi la population des Players', self)

        bouton1.setStyleSheet('QLabel { font-weight: bold }')
        bouton2.setStyleSheet('QLabel { font-weight: bold }')
        vligne1.addWidget(bouton1)
        vligne1.addWidget(bouton2)
        sp_line.setFrameShape(QFrame.HLine)
        vligne1.addWidget(sp_line)
        ligne1.addLayout(vligne1)

        label = QLabel(self)
        vligne1 = QVBoxLayout()
        circular = QPixmap("./icon/circular_diagram.png")
        circular.scaledToWidth(50)

        label.setPixmap(circular)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        ligne1.addWidget(label)
        vligne1.addWidget(label)
        bouton1 = QPushButton('Répartition de la population', self)
        bouton2 = QPushButton('Répartition parmi la population des Players', self)

        bouton1.setStyleSheet('QLabel { font-weight: bold }')
        bouton2.setStyleSheet('QLabel { font-weight: bold }')
        vligne1.addWidget(bouton1)
        vligne1.addWidget(bouton2)
        sp_line.setFrameShape(QFrame.HLine)
        vligne1.addWidget(sp_line)
        ligne1.addLayout(vligne1)

        # Diagramme lineaire
        label = QLabel(self)
        vligne1 = QVBoxLayout()
        linear = QPixmap("./icon/linear_diagram.png")
        linear.scaledToWidth(50)
        label.setPixmap(linear)
        ligne2.addWidget(label)
        bouton1 = QPushButton('Données des entités SGEntities', self)
        bouton2 = QPushButton('Données des entités SGEntities et SimVariables', self)
        bouton3 = QPushButton('Données des Players', self)

        # TestGraphView
        act = QAction("Diagramme d'évolution", self)
        act.triggered.connect(self.openNewDiagram)
        bouton1.addAction(act)

        bouton1.setStyleSheet('QLabel { font-weight: bold }')
        bouton2.setStyleSheet('QLabel { font-weight: bold }')
        bouton3.setStyleSheet('QLabel { font-weight: bold }')
        vligne1.addWidget(bouton1)
        vligne1.addWidget(bouton2)
        vligne1.addWidget(bouton3)
        sp_line.setFrameShape(QFrame.HLine)
        vligne1.addWidget(sp_line)
        ligne2.addLayout(vligne1)

        label = QLabel(self)
        vligne1 = QVBoxLayout()
        stackplot = QPixmap("./icon/stackplot_diagram.png")
        label.setPixmap(stackplot)
        ligne2.addWidget(label)
        bouton1 = QPushButton('Données en temps réelles', self)
        bouton1.setStyleSheet('QLabel { font-weight: bold }')
        vligne1.addWidget(bouton1)
        sp_line.setFrameShape(QFrame.HLine)
        vligne1.addWidget(sp_line)
        ligne2.addLayout(vligne1)

        layout.addLayout(ligne1)
        sp_line = QFrame()
        sp_line.setFrameShape(QFrame.HLine)
        sp_line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(sp_line)
        layout.addLayout(ligne2)
        self.setLayout(layout)
        self.setGeometry(100, 100, 800, 500)
        self.show()



class TestGraphView(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Ajouter des widgets à la deuxième fenêtre
        self.setGeometry(200, 200, 400, 300)
        self.setWindowTitle('Deuxième Fenêtre')
        #self.init_graph()

    def init_graph(self):
        # Initialisation des données
        x = np.arange(0, 40, 0.1)
        y1 = np.sin(x)
        y2 = np.sin(x)
        title = "Exemple de simulation avec un diagramme d'évolution des données"
        label1 = "Fréquence : Model 1"
        label2 = "Fréquence : Model 2"

        monApp = SGLinearDiagram(x, y1, y2, label1, label2, title)
        #monApp.display()
"""