import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt

# Import from your project
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGExtensions import generate_color_gradient


def create_gradient_label(colors, text):
    """Create a QLabel showing the gradient colors."""
    label = QLabel(text)
    pixmap = QPixmap(len(colors) * 30, 30)
    pixmap.fill(Qt.white)
    painter = QPainter(pixmap)
    for i, color in enumerate(colors):
        painter.fillRect(i * 30, 0, 30, 30, color)
    painter.end()
    label.setPixmap(pixmap)
    return label


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("generate_color_gradient() - Test Modes")
    layout = QVBoxLayout(window)

    # 1️⃣ Simple mode with steps
    layout.addWidget(create_gradient_label(
        generate_color_gradient("green", "blue", steps=8),
        "Basic gradient (steps)"
    ))

    # 2️⃣ Mapping mode with as_dict (two colors)
    mapping_dict = generate_color_gradient(
        "red", "blue",
        mapping={"values": list(range(0, 110, 10)), "value_min": 0, "value_max": 100},
        as_dict=True
    )
    layout.addWidget(create_gradient_label(
        list(mapping_dict.values()),
        "Mapping mode (two colors, as_dict)"
    ))

    # 3️⃣ Mapping mode with as_ranges (two colors)
    mapping_ranges = generate_color_gradient(
        "green", "yellow",
        mapping={"values": [1, 3, 5, 6, 7], "value_min": 0, "value_max": 7},
        as_ranges=True
    )
    layout.addWidget(create_gradient_label(
        [c for _, _, c in mapping_ranges],
        "Mapping mode (two colors, as_ranges)"
    ))

    # 4️⃣ Mapping mode with one color (as_dict)
    mapping_one_color_dict = generate_color_gradient(
        "purple",
        mapping={"values": list(range(0, 110, 10)), "value_min": 0, "value_max": 100},
        as_dict=True
    )
    layout.addWidget(create_gradient_label(
        list(mapping_one_color_dict.values()),
        "Mapping mode (one color, as_dict)"
    ))

    # 5️⃣ Mapping mode with one color (as_ranges)
    mapping_one_color_ranges = generate_color_gradient(
        "orange",
        mapping={"values": [1, 3, 5, 6, 7], "value_min": 0, "value_max": 7},
        as_ranges=True
    )
    layout.addWidget(create_gradient_label(
        [c for _, _, c in mapping_one_color_ranges],
        "Mapping mode (one color, as_ranges)"
    ))

    window.show()
    sys.exit(app.exec_())
