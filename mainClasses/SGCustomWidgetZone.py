from PyQt5 import QtWidgets, QtGui, QtCore
from sqlalchemy import true
# from PyQt5.QtWidgets import QStyleFactory
# from mainClasses.SGGameSpace import SGGameSpace

class SGCustomWidgetZone(QtWidgets.QWidget):
    def __init__(self, parent=None, background_color="white", border_color="black", border_size=1, text_style="", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setAutoFillBackground(True)
        self.set_background_color(background_color)
        self.border_color = border_color
        self.border_size = border_size
        self.text_style = text_style
        self.elements = []  # Liste pour stocker les éléments (texte, images, formes)

    def set_background_color(self, color):
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Background, QtGui.QColor(color))
        self.setPalette(palette)
    
    def set_border_style(self, border_color, border_size, border_style="solid"):
        """Modifie le style de la bordure de la zone."""
        self.border_color = border_color
        self.border_size = border_size
        self.border_style = border_style
        self.update()  # Redessine la zone

    def add_text(self, text, position, color="black"):
        """Ajoute du texte à la zone avec une couleur spécifiée."""
        if isinstance(position, tuple) and len(position) == 2:
            self.elements.append(("text", (position[0], position[1], text, color)))  # (x, y, text, color)
        else:
            raise ValueError("Position must be a tuple of (x, y).")

    def add_image(self, image_path, position, size=None):
        """Ajoute une image à la zone avec une option de redimensionnement."""
        self.elements.append(("image", image_path, position, size))  # (image_path, position, size)

    def add_shape(self, shape_type, position, size):
        """Ajoute une forme à la zone (rectangle ou triangle)."""
        self.elements.append(("shape", shape_type, position, size))

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        # Dessiner la bordure
        painter.setPen(QtGui.QPen(QtGui.QColor(self.border_color), self.border_size))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        # Dessiner les éléments
        for element in self.elements:
            if element[0] == "text":
                if len(element[1]) == 3:
                    x, y, text = element[1]
                    print(f"Drawing text at ({x}, {y}): {text}")  # Debugging line
                    painter.setFont(QtGui.QFont(self.text_style))
                    painter.drawText(int(x), int(y), text)
                else:
                    print(f"Unexpected element format for text: {element[1]}")
            elif element[0] == "image":
                pixmap = QtGui.QPixmap(element[1])
                painter.drawPixmap(int(element[2][0]), int(element[2][1]), pixmap)  # (x, y)
            elif element[0] == "shape":
                if element[1] == "rectangle":
                    painter.drawRect(int(element[2][0]), int(element[2][1]), int(element[3][0]), int(element[3][1]))  # (x, y, width, height)
                elif element[1] == "triangle":
                    points = [QtCore.QPoint(int(element[2][0]), int(element[2][1])),
                              QtCore.QPoint(int(element[2][0] + element[3][0]), int(element[2][1])),
                              QtCore.QPoint(int(element[2][0] + element[3][0] // 2), int(element[2][1] - element[3][1]))]
                    painter.drawPolygon(QtGui.QPolygon(points))

        painter.end()

    def clear_elements(self):
        """Efface tous les éléments de la zone."""
        self.elements.clear()
        self.update()  # Redessine la zone

