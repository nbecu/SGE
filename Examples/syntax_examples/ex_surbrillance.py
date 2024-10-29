import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtGui import QColor, QPolygon, QPainter
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QGraphicsColorizeEffect

class PolygonWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Surbrillance d'un polygone")
        
        # Configuration du bouton
        self.button = QPushButton("Activer/Désactiver la surbrillance", self)
        self.button.clicked.connect(self.toggleHighlight)
        
        # Création du layout et ajout du bouton
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        
        # Taille du widget de polygone
        self.setFixedSize(200, 200)
        
        # Création de l'effet de surbrillance
        self.highlightEffect = None
        self.isHighlighted = False

    def toggleHighlight(self):
        if self.isHighlighted:
            # Désactiver la surbrillance
            self.setGraphicsEffect(None)
        else:
            # Créer et appliquer un effet de surbrillance
            self.highlightEffect = QGraphicsColorizeEffect()
            self.highlightEffect.setColor(QColor("red"))
            self.setGraphicsEffect(self.highlightEffect)
        
        # Alterner l'état de surbrillance
        self.isHighlighted = not self.isHighlighted

    def paintEvent(self, event):
        # Dessiner le polygone
        polygon = QPolygon([
            QPoint(100, 10),
            QPoint(150, 110),
            QPoint(50, 110)
        ])
        
        painter = QPainter(self)
        painter.setBrush(QColor("lightblue"))
        painter.drawPolygon(polygon)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exemple avec QPolygon")
        
        # Instancier le widget de polygone et le bouton de contrôle
        self.polygon_widget = PolygonWidget()
        
        # Disposer le widget dans la fenêtre principale
        layout = QVBoxLayout()
        layout.addWidget(self.polygon_widget)
        self.setLayout(layout)

# Lancer l'application
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
