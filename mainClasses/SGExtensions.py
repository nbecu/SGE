"""
SGExtensions.py
Ce fichier regroupe toutes les extensions de classes (Qt ou non) utilisées dans le projet.
Exemple : méthodes ajoutées dynamiquement à QPainter, QWidget, list, dict, etc.
"""

from PyQt5.QtGui import QFontMetrics, QFont, QPainter
from PyQt5.QtCore import QRectF

def drawTextAutoSized(self, aleft, atop, text, font=None, align=0, padding_width=0, padding_height=0):
    """
    Draws the given text at position (aleft, atop) inside a rectangle automatically sized to fit the text.
    - Computes the required width and height using QFontMetrics.
    - Applies the specified font and alignment.
    - Optionally adds horizontal and vertical padding.

    :param self: QPainter instance
    :param aleft: x position (left) of the rectangle
    :param atop: y position (top) of the rectangle
    :param text: text to draw
    :param font: QFont to use (optional, default Verdana 8)
    :param align: Qt alignment flag (e.g., Qt.AlignLeft)
    :param padding_width: extra width to add (in pixels)
    :param padding_height: extra height to add (in pixels)
    :return: (width, height) of the rectangle used
    """
    if font is None:
        font = QFont("Verdana", 8)
    self.setFont(font)
    metrics = QFontMetrics(font)
    width = metrics.width(text) + padding_width
    height = metrics.height() + padding_height
    rect = QRectF(aleft, atop, width, height)
    self.drawText(rect, align, text)
    return width, height

# Attach the method to QPainter for direct usage everywhere in the project
QPainter.drawTextAutoSized = drawTextAutoSized

# Utilities

def first_value(d, default=None):
    """
    Return the first value of a dictionary according to insertion order.
    - Does not materialize a list (O(1) extra memory).
    - Returns `default` if the dictionary is empty.

    :param d: dictionary to read from
    :param default: value to return if dict is empty (default: None)
    :return: the first value or `default` if empty
    """
    return next(iter(d.values()), default)


def first_key(d, default=None):
    """
    Return the first key of a dictionary according to insertion order.
    - O(1) extra memory.
    - Returns `default` if the dictionary is empty.

    :param d: dictionary to read from
    :param default: value to return if dict is empty (default: None)
    :return: the first key or `default` if empty
    """
    return next(iter(d), default)


def first_item(d, default=None):
    """
    Return the first (key, value) pair of a dictionary according to insertion order.
    - O(1) extra memory.
    - Returns `default` if the dictionary is empty.

    :param d: dictionary to read from
    :param default: value to return if dict is empty (default: None)
    :return: the first (key, value) tuple or `default` if empty
    """
    return next(iter(d.items()), default)


def generate_color_gradient(color1, color2=None, steps: int = 10, reverse_gradient=False, mapping=None, as_dict=False):
    """
    Generate a list or dict of QColor objects representing a color gradient.

    Parameters
    ----------
    color1 : QColor, tuple, str, int (Qt.GlobalColor)
        First color or reference color in single-color mode.
    color2 : QColor, tuple, str, int (Qt.GlobalColor), optional
        Second color for two-color interpolation. If None, single-color mode is used.
    steps : int
        Number of colors in normal mode (ignored in mapping mode).
    reverse_gradient : bool
        Reverse the generated colors.
    mapping : dict, optional
        If provided, switches to mapping mode.
        Expected keys:
            - "values": list of numeric values to map
            - "value_min": minimum possible value
            - "value_max": maximum possible value
    as_dict : bool
        If True and mapping mode is used, returns a dict {value: QColor}.

    Returns
    -------
    list[QColor] or dict
        List of QColor objects, or dict if mapping mode with as_dict=True.
    """
    from PyQt5.QtGui import QColor
    from PyQt5.QtCore import Qt

    def to_qcolor(value) -> QColor:
        if isinstance(value, QColor):
            return value
        if value is None:
            return None
        if isinstance(value, str):
            q = QColor(value)
            if q.isValid():
                return q
        if isinstance(value, (tuple, list)):
            return QColor(*value)
        try:
            return QColor(Qt.GlobalColor(int(value)))
        except Exception:
            pass
        try:
            q = QColor(value)
            if q.isValid():
                return q
        except Exception:
            pass
        raise TypeError(f"Unsupported color type: {type(value)} ({value!r})")

    color1 = to_qcolor(color1)
    color2 = to_qcolor(color2) if color2 is not None else None

    # === MAPPING MODE ===
    if mapping is not None:
        values = mapping.get("values")
        vmin = mapping.get("value_min")
        vmax = mapping.get("value_max")

        if not isinstance(values, (list, tuple)):
            raise ValueError("mapping['values'] must be a list or tuple")
        if vmin is None or vmax is None:
            raise ValueError("mapping must contain 'value_min' and 'value_max'")

        colors = []

        if color2 is not None:
            # Two-color mapping
            for v in values:
                val = max(min(v, vmax), vmin)
                proportion = 0.0 if vmax == vmin else (val - vmin) / (vmax - vmin)
                r = color1.red()   + (color2.red()   - color1.red())   * proportion
                g = color1.green() + (color2.green() - color1.green()) * proportion
                b = color1.blue()  + (color2.blue()  - color1.blue())  * proportion
                colors.append(QColor(int(r), int(g), int(b)))
        else:
            # Single-color mapping (light -> color -> dark)
            extra_steps = 256  # large for smoothness
            mid_index = extra_steps // 2
            gradient_full = []

            for i in range(mid_index):
                r = 255 + (color1.red() - 255) * i / (mid_index - 1)
                g = 255 + (color1.green() - 255) * i / (mid_index - 1)
                b = 255 + (color1.blue() - 255) * i / (mid_index - 1)
                gradient_full.append(QColor(int(r), int(g), int(b)))
            for i in range(mid_index, extra_steps):
                r = color1.red() * (1 - (i - mid_index) / (extra_steps - mid_index - 1))
                g = color1.green() * (1 - (i - mid_index) / (extra_steps - mid_index - 1))
                b = color1.blue() * (1 - (i - mid_index) / (extra_steps - mid_index - 1))
                gradient_full.append(QColor(int(r), int(g), int(b)))

            gradient_full = gradient_full[1:-1]  # remove pure white/black

            for v in values:
                val = max(min(v, vmax), vmin)
                proportion = 0.0 if vmax == vmin else (val - vmin) / (vmax - vmin)
                index = int(proportion * (len(gradient_full) - 1))
                colors.append(gradient_full[index])

        if reverse_gradient:
            colors.reverse()

        return dict(zip(values, colors)) if as_dict else colors

    # === NORMAL MODE ===
    if steps < 2:
        raise ValueError("Number of steps must be at least 2.")

    gradient = []
    if color2 is None:
        extra_steps = steps + 2
        mid_index = extra_steps // 2
        for i in range(mid_index):
            r = 255 + (color1.red() - 255) * i / (mid_index - 1)
            g = 255 + (color1.green() - 255) * i / (mid_index - 1)
            b = 255 + (color1.blue() - 255) * i / (mid_index - 1)
            gradient.append(QColor(int(r), int(g), int(b)))
        for i in range(mid_index, extra_steps):
            r = color1.red() * (1 - (i - mid_index) / (extra_steps - mid_index - 1))
            g = color1.green() * (1 - (i - mid_index) / (extra_steps - mid_index - 1))
            b = color1.blue() * (1 - (i - mid_index) / (extra_steps - mid_index - 1))
            gradient.append(QColor(int(r), int(g), int(b)))
        gradient = gradient[1:-1]
    else:
        for i in range(steps):
            t = i / (steps - 1)
            r = color1.red()   + (color2.red()   - color1.red())   * t
            g = color1.green() + (color2.green() - color1.green()) * t
            b = color1.blue()  + (color2.blue()  - color1.blue())  * t
            gradient.append(QColor(int(r), int(g), int(b)))

    if reverse_gradient:
        gradient.reverse()

    return gradient
