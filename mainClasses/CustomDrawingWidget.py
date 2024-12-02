from PyQt5 import QtWidgets, QtGui, QtCore
import math

class SGShapeWidget(QtWidgets.QWidget):
    def __init__(self, shape=None, size=None, position=(0,0), parent=None):
        super().__init__(parent)
        self.shape = shape
        self.size = size
        self.position = position
        self.setGeometry(0,0,410, 510)  # Set geometry for visibility
        # self.setGeometry(position[0], position[1], 400, 400)  # Set geometry for visibility
        self.update()  # Redraw the widget

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        shape_type = self.shape
        size = self.size
       
       
        x, y = self.position
        if shape_type == "square":
            painter.drawRect(x, y, size, size)  # size is the side length
        elif shape_type == "rectangle1":
            painter.drawRect(x, y, size, round(size/2))  # size[0] is width, size[1] is height
        elif shape_type == "rectangle2":
            painter.drawRect(x, y, round(size/2), size)  # size[0] is width, size[1] is height
        elif shape_type == "circle":
            painter.drawEllipse(x, y, size, size)  # size is the diameter        
        elif shape_type == "ellipse1":
            painter.drawEllipse(x, y, size, round(size/2))
        elif shape_type == "ellipse2":
            painter.drawEllipse(x, y, round(size/2), size)
        elif shape_type == "triangle1":
            points = QtGui.QPolygon([
                QtCore.QPoint(round(size / 2), 0),
                QtCore.QPoint(0, size),
                QtCore.QPoint(size, size)
            ])
            painter.drawPolygon(points.translated(x, y))
        elif shape_type == "triangle2":
            points = QtGui.QPolygon([
                QtCore.QPoint(0, 0),
                QtCore.QPoint(size, 0),
                QtCore.QPoint(round(size / 2), size)
            ])
            painter.drawPolygon(points.translated(x, y))
        elif shape_type == "triangle3":
            points = QtGui.QPolygon([
                QtCore.QPoint(0, 0),                # Top left vertex
                QtCore.QPoint(0, size),             # Bottom left vertex
                QtCore.QPoint(size, round(size/2))           # Bottom right vertex
            ])
            painter.drawPolygon(points.translated(x, y))
        elif shape_type == "triangle4":
            points = QtGui.QPolygon([
                QtCore.QPoint(size, 0),             # Top right vertex
                QtCore.QPoint(size, size),          # Bottom right vertex
                QtCore.QPoint(0, round(size/2))               # Bottom left vertex
            ])
            painter.drawPolygon(points.translated(x, y))
        elif shape_type == "triangle5":
            points = QtGui.QPolygon([
                QtCore.QPoint(0, 0),                # Top left vertex
                QtCore.QPoint(0, size),             # Bottom left vertex
                QtCore.QPoint(size, size)           # Bottom right vertex
            ])
            painter.drawPolygon(points.translated(x, y))
        elif shape_type == "triangle6":
            points = QtGui.QPolygon([
                QtCore.QPoint(size, 0),             # Top right vertex
                QtCore.QPoint(size, size),          # Bottom right vertex
                QtCore.QPoint(0, size)               # Bottom left vertex
            ])
            painter.drawPolygon(points.translated(x, y))
        elif shape_type == "triangle7":
            points = QtGui.QPolygon([
                QtCore.QPoint(0, 0),                # Top left vertex
                QtCore.QPoint(0, size),             # Bottom left vertex
                QtCore.QPoint(size, 0)           # Bottom right vertex
            ])
            painter.drawPolygon(points.translated(x, y))
        elif shape_type == "triangle8":
            points = QtGui.QPolygon([
                QtCore.QPoint(0, 0),
                QtCore.QPoint(size, 0),             # Top right vertex
                QtCore.QPoint(size, size)          # Bottom right vertex
                
            ])
            painter.drawPolygon(points.translated(x, y))
        elif shape_type == "arrow1":
            points = QtGui.QPolygon([
                QtCore.QPoint(round(size / 2), 0),
                QtCore.QPoint(0, size),
                QtCore.QPoint(round(size / 2), round(size / 3) * 2),
                QtCore.QPoint(size, size)
            ])
            painter.drawPolygon(points.translated(x, y))
        elif shape_type == "arrow2":
            points = QtGui.QPolygon([
                QtCore.QPoint(0, 0),
                QtCore.QPoint(round(size / 2), round(size / 3)),
                QtCore.QPoint(size, 0),
                QtCore.QPoint(round(size / 2), size)
            ])
            painter.drawPolygon(points.translated(x, y))
            
        elif shape_type == "hexagon1":
            r = size / 2
            h = round(r * (3 ** 0.5)) + 10  # Height of the equilateral hexagon
            points = QtGui.QPolygon([
                QtCore.QPoint(round(size / 2), 0),                # Top vertex
                QtCore.QPoint(size, round(h / 4)),           # Top right corner
                QtCore.QPoint(size, round(3 * h / 4)),       # Bottom right corner
                QtCore.QPoint(round(size / 2), h),           # Bottom vertex
                QtCore.QPoint(0, round(3 * h / 4)),         # Bottom left corner
                QtCore.QPoint(0, round(h / 4))                # Top left corner
            ])
            painter.drawPolygon(points.translated(x, y))
        elif shape_type == "hexagon2":
            r = size / 2  # Rayon du cercle inscrit
            h = round(r * (3 ** 0.5) / 2)  # Calculer une fois la valeur de sqrt(3)/2
            points = QtGui.QPolygon([
                QtCore.QPoint(size, round(r)),  # A1
                QtCore.QPoint(round(r *1.5), h + round(r)),  # A2
                QtCore.QPoint(round(r/2), h + round(r)),  # A3
                QtCore.QPoint(0, round(r)),  # A4
                QtCore.QPoint(round(r/2), round(-h + r)),  # A5
                QtCore.QPoint(round(r *1.5), round(-h + r))   # A6
            ])
            painter.drawPolygon(points.translated(x,y))
            

        painter.end()

    

# Example usage
if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    window = QtWidgets.QWidget()
    window.setGeometry(0, 0, 400, 510)  # Set the main window size

    widgets = []

    # Add shapes directly
    widgets.append(SGShapeWidget("circle", 50, (0, 0), window))  # Circle with diameter 50
    widgets.append(SGShapeWidget("circle", 100, (0, 0), window))  # Circle with diameter 50
    widgets.append(SGShapeWidget("square", 100, (100, 0), window))  # Square with side length 50
    widgets.append(SGShapeWidget("square", 40, (150, 50), window))  # Square with side length 50
    widgets.append(SGShapeWidget("rectangle1", 100, (200, 00), window))
    widgets.append(SGShapeWidget("rectangle1", 40, (210, 10), window))
    widgets.append(SGShapeWidget("rectangle2", 100, (300, 00), window))
    widgets.append(SGShapeWidget("rectangle2", 40, (310, 10), window))
    widgets.append(SGShapeWidget("ellipse1", 100, (0, 100), window))
    widgets.append(SGShapeWidget("ellipse1", 50, (10, 120), window))
    widgets.append(SGShapeWidget("ellipse2", 100, (100, 100), window))
    widgets.append(SGShapeWidget("ellipse2", 50, (110, 120), window))
    widgets.append(SGShapeWidget("hexagon1", 100, (200, 100), window))
    widgets.append(SGShapeWidget("hexagon1", 50, (225, 125), window))
    widgets.append(SGShapeWidget("hexagon2", 100, (300, 100), window))
    widgets.append(SGShapeWidget("hexagon2", 50, (326, 126), window))

    widgets.append(SGShapeWidget("triangle1", 100, (0, 200), window))
    widgets.append(SGShapeWidget("triangle1", 50, (0, 200), window))
    widgets.append(SGShapeWidget("triangle2", 100, (100, 200), window))
    widgets.append(SGShapeWidget("triangle2", 50, (100, 200), window))
    widgets.append(SGShapeWidget("triangle3", 100, (200, 200), window))
    widgets.append(SGShapeWidget("triangle3", 50, (230, 200), window))
    widgets.append(SGShapeWidget("triangle4", 100, (300, 200), window))
    widgets.append(SGShapeWidget("triangle4", 50, (330, 200), window))
    widgets.append(SGShapeWidget("triangle5", 100, (0, 300), window))
    widgets.append(SGShapeWidget("triangle5", 50, (0, 300), window))
    widgets.append(SGShapeWidget("triangle6", 100, (100, 300), window))
    widgets.append(SGShapeWidget("triangle6", 50, (100, 300), window))
    widgets.append(SGShapeWidget("triangle7", 100, (200, 300), window))
    widgets.append(SGShapeWidget("triangle7", 50, (210, 310), window))
    widgets.append(SGShapeWidget("triangle8", 100, (300, 300), window))
    widgets.append(SGShapeWidget("triangle8", 50, (340, 310), window))

    widgets.append(SGShapeWidget("arrow1", 100, (0, 400), window))
    widgets.append(SGShapeWidget("arrow1", 50, (0, 400), window))
    widgets.append(SGShapeWidget("arrow2", 100, (100, 400), window))
    widgets.append(SGShapeWidget("arrow2", 50, (100, 400), window))
    for aWidget in widgets:
        aWidget.show()  # Show each shape widget

    window.show()  # Show the main window
    app.exec_()