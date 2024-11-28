from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPolygon
from PyQt5.QtCore import Qt, QPoint
import sys

class DrawingWidget(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Configuration du QPen pour le contour
        pen = QPen(QColor("blue"), 3)  # couleur bleue et largeur de 3 pixels
        pen.setStyle(Qt.SolidLine)  # Style du trait (plein, pointillé, etc.)
        painter.setPen(pen)

        # Dessiner un rectangle avec un contour personnalisé
        painter.drawRect(50, 50, 100, 50)
        
        # Dessiner un polygone (par exemple un triangle) avec un contour personnalisé
        points = [QPoint(200, 50), QPoint(250, 100), QPoint(150, 100)]
        polygon = QPolygon(points)
        painter.drawPolygon(polygon)
        
        # Dessiner une ellipse avec un contour personnalisé
        painter.drawEllipse(300, 50, 100, 50)

app = QApplication(sys.argv)
window = DrawingWidget()
window.setGeometry(100, 100, 500, 200)
window.show()
sys.exit(app.exec_())
