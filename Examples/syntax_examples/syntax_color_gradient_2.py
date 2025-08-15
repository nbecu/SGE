import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt

# Import from your project
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGExtensions import generate_color_gradient


def create_gradient_label(colors, text):
    """Create a QLabel showing the gradient colors."""
    label = QLabel(text)
    pixmap = QPixmap(len(colors) * 40, 40)
    pixmap.fill(Qt.white)
    painter = QPainter(pixmap)
    for i, color in enumerate(colors):
        painter.fillRect(i * 40, 0, 40, 40, color)
    painter.end()
    label.setPixmap(pixmap)
    return label


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("generate_color_gradient() - Mapping mode comparison")
    layout = QVBoxLayout(window)

    # Same value set for both
    mapping_params = {"values": list(range(0, 110, 10)), "value_min": 0, "value_max": 100}

    # Mapping with two colors
    colors_two = generate_color_gradient(Qt.red, Qt.blue, mapping=mapping_params)
    layout.addWidget(create_gradient_label(colors_two, "Mapping mode: Red → Blue"))

    # Mapping with one color (reference = green)
    colors_one = generate_color_gradient(Qt.green, mapping=mapping_params)
    layout.addWidget(create_gradient_label(colors_one, "Mapping mode: Green (light → green → dark)"))

    window.show()
    sys.exit(app.exec_())
