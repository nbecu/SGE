import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QDialog, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QColor, QPainter

class ImagePopup(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.image_label = QLabel(self)
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap)
        
        # Ajuste la taille de la fenêtre contextuelle à la taille de l'image
        self.setFixedSize(pixmap.size())
        
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)

class HoverWidget(QWidget):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.popup = None
        self.setFixedSize(100, 100)  # Définir un carré de 100x100 pixels
    
    def paintEvent(self, event):
        # Remplit le widget avec une couleur noire
        painter = QPainter(self)
        painter.setBrush(QColor(0, 0, 0))  # Couleur noire
        painter.drawRect(self.rect())

    def enterEvent(self, event):
        # Affiche la fenêtre contextuelle à la position de la souris
        self.popup = ImagePopup(self.image_path, self)
        self.popup.move(self.mapToGlobal(QPoint(self.width(), 0)))
        self.popup.show()

    def leaveEvent(self, event):
        # Ferme la fenêtre contextuelle quand on quitte le widget
        if self.popup:
            self.popup.close()
            self.popup = None

app = QApplication(sys.argv)

main_window = QWidget()
main_layout = QVBoxLayout(main_window)

hover_widget = HoverWidget("./icon/solutre/N1.png")
main_layout.addWidget(hover_widget)

main_window.setLayout(main_layout)
main_window.setGeometry(100, 100, 400, 400)
main_window.show()

sys.exit(app.exec_())
