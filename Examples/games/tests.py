# from PyQt5.QtWidgets import QApplication, QLabel, QToolTip
# from PyQt5.QtGui import QPixmap, QCursor
# from PyQt5.QtCore import Qt, QPoint

# class MyWidget(QLabel):
#     def __init__(self):
#         super().__init__()
#         self.setText("Hover over me to see an image tooltip!")
#         self.resize(300, 100)
#         self.image_path = "./icon/solutre/touriste.png"  # Remplacez par votre image

#     def enterEvent(self, event):
#         """Affiche une infobulle avec une image."""
#         pixmap = QPixmap(self.image_path)
#         if pixmap.isNull():
#             QToolTip.showText(QCursor.pos(), "Image not found!", self)
#             return
        
#         # Convertir l'image en HTML pour ToolTip
#         html = f"<img src='{self.image_path}' style='max-width: 200px; max-height: 200px;'>"
#         QToolTip.showText(QCursor.pos(), html, self)

#     def leaveEvent(self, event):
#         """Cache l'infobulle."""
#         QToolTip.hideText()

# # Lancer l'application
# app = QApplication([])
# window = MyWidget()
# window.show()
# app.exec_()


import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar, QPushButton
from PyQt5.QtCore import Qt, QTimer


class ProgressBarExample(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Créer une mise en page
        self.layout = QVBoxLayout()
        
        # Créer une barre de progression
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)  # Valeur minimale
        self.progress_bar.setMaximum(100)  # Valeur maximale
        self.progress_bar.setAlignment(Qt.AlignCenter)  # Centrer le texte
        
        # Ajouter la barre à la mise en page
        self.layout.addWidget(self.progress_bar)
        
        # Créer un bouton pour démarrer
        self.start_button = QPushButton("Démarrer", self)
        self.start_button.clicked.connect(self.start_progress)
        self.layout.addWidget(self.start_button)
        
        # Configurer la fenêtre principale
        self.setLayout(self.layout)
        self.setWindowTitle("Exemple de ProgressBar")
        self.resize(300, 150)
    
    def start_progress(self):
        # Utiliser un QTimer pour simuler une progression
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.value = 0
        self.timer.start(100)  # Met à jour toutes les 100 ms

    def update_progress(self):
        # Incrémenter la valeur de la barre de progression
        self.value += 1
        self.progress_bar.setValue(self.value)
        
        if self.value >= 100:
            self.timer.stop()  # Arrêter le timer lorsque la progression atteint 100


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProgressBarExample()
    window.show()
    sys.exit(app.exec_())
