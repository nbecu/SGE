from PyQt5.QtWidgets import QApplication, QLabel, QToolTip
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtCore import Qt, QPoint

class MyWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("Hover over me to see an image tooltip!")
        self.resize(300, 100)
        self.image_path = "./icon/solutre/touriste.png"  # Remplacez par votre image

    def enterEvent(self, event):
        """Affiche une infobulle avec une image."""
        pixmap = QPixmap(self.image_path)
        if pixmap.isNull():
            QToolTip.showText(QCursor.pos(), "Image not found!", self)
            return
        
        # Convertir l'image en HTML pour ToolTip
        html = f"<img src='{self.image_path}' style='max-width: 200px; max-height: 200px;'>"
        QToolTip.showText(QCursor.pos(), html, self)

    def leaveEvent(self, event):
        """Cache l'infobulle."""
        QToolTip.hideText()

# Lancer l'application
app = QApplication([])
window = MyWidget()
window.show()
app.exec_()
