import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt

# Import from your project structure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGExtensions import generate_color_gradient

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("generate_color_gradient() - Syntax Tests")
    layout = QVBoxLayout(window)

    # Helper to add a gradient to the layout
    def add_gradient(colors, text):
        label = QLabel(text)
        pixmap = QPixmap(len(colors) * 30, 30)
        pixmap.fill(Qt.white)
        painter = QPainter(pixmap)
        for i, color in enumerate(colors):
            painter.fillRect(i * 30, 0, 30, 30, color)
        painter.end()
        label.setPixmap(pixmap)
        layout.addWidget(label)

    # === Tests for all syntaxes ===
    # --- MODE NORMAL (steps) ---
    add_gradient(generate_color_gradient("green", steps=8), "Single color (name) white → color → black")
    add_gradient(generate_color_gradient("green", steps=8, reverse_gradient=True), "Single color (name) black → color → white")
    add_gradient(generate_color_gradient("red", "blue", steps=8), "Two named colors")
    add_gradient(generate_color_gradient("#FF0000", "#0000FF", steps=8), "Two hex colors")
    add_gradient(generate_color_gradient((255, 128, 0), (0, 128, 255), steps=8), "Two RGB tuples")
    add_gradient(generate_color_gradient(QColor(0, 255, 0), QColor(0, 0, 255), steps=8), "Two QColor objects")
    add_gradient(generate_color_gradient((100, 200, 50), steps=8), "Single color (tuple) white → color → black")
    add_gradient(generate_color_gradient("#00AA88", steps=8), "Single color (hex) white → color → black")
    # --- MODE MAPPING ---
    values = [0, 10, 33, 50, 75, 90, 100]
    mapping_dict = {"values": values, "value_min": 0, "value_max": 100}
    add_gradient(generate_color_gradient("red", "green", mapping=mapping_dict),
        f"Mapping mode: values={values}"
    )
    values = [0, 10, 33, 50, 75]
    mapping_dict = {"values": values, "value_min": 0, "value_max": 100}
    add_gradient(generate_color_gradient("red", "green", mapping=mapping_dict),
        f"Mapping mode: values={values}"
    )


    window.show()
    sys.exit(app.exec_())
