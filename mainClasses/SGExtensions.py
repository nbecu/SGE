"""
SGExtensions.py
Ce fichier regroupe toutes les extensions de classes (Qt ou non) utilisées dans le projet, ainsi que des utils générales.
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


def execute_callable_with_entity(callable_func, entity=None):
    """
    Execute a callable function with appropriate arguments based on its signature.
    - If callable has 0 arguments: execute with no arguments
    - If callable has 1 argument: execute with the provided entity
    - If callable has more than 1 argument: raise ValueError
    
    This utility method is used by SGModelAction and SGActivate to handle
    lambda functions with different argument counts.
    
    :param callable_func: The callable function to execute
    :param entity: The entity to pass as argument (if callable expects 1 argument)
    :raises ValueError: If callable has more than 1 argument
    """
    if not callable(callable_func):
        raise TypeError("First argument must be callable")
    
    # Count the number of arguments
    nbArguments = callable_func.__code__.co_argcount
    if nbArguments == 0:
        callable_func()  # Execute with no arguments
    elif nbArguments == 1:
        callable_func(entity)  # Execute with entity argument
    else:
        raise ValueError(f"Callable must have 0 or 1 arguments, got {nbArguments}")


def normalize_species_name(species):
    """
    Normalize a species name to a string, handling both string and SGAgentDef inputs.
    
    This utility method extracts the entity name from SGAgentDef objects
    or returns the string as-is for string inputs.
    
    :param species: Either a string species name or an SGAgentDef object
    :return: The normalized species name as a string
    """
    from mainClasses.SGEntityDef import SGAgentDef
    if isinstance(species, SGAgentDef):
        return species.entityName
    return species


def generate_color_gradient(color1, color2=None, steps: int = 10, reverse_gradient=False, mapping=None, as_dict=False, as_ranges=False):
    """
    Generate a color gradient as a list of QColor objects, a dict (mapping mode), or a list of (start, end, color) ranges.

    Modes
    -----
    1) Basic mode (no mapping):
       - Two colors: gradient from color1 → color2 with `steps` samples.
       - Single color (color2 is None): gradient light → color1 → dark (never pure white/black).
         Extremes are trimmed to keep the reference hue visible.

    2) Mapping mode (with `mapping`):
       - mapping = {"values": [...], "value_min": x, "value_max": y}
       - If two colors: each value is mapped linearly between color1 and color2.
       - If single color: each value is mapped along light → color1 → dark.
       - reverse_gradient flips the mapping (i.e., t → 1-t).

    Output
    ------
    - Default: list[QColor]
    - as_dict=True: dict {value: QColor}  (mapping mode only)
    - as_ranges=True: list[(start, end, QColor)] with the last end = float('inf') (mapping mode only)
      Ranges are: [vmin, v1), [v1, v2), ..., [v_last, inf)

    Accepted color formats
    ----------------------
    QColor, color name ("red"), hex "#RRGGBB[AA]", (R,G,B) or (R,G,B,A), Qt.GlobalColor (e.g., Qt.red)

    Examples
    --------
    generate_color_gradient("green", steps=6)
    generate_color_gradient("red", "blue", steps=8)
    generate_color_gradient("red", "blue", mapping={"values":[0,50,100], "value_min":0, "value_max":100}, as_dict=True)
    generate_color_gradient("green", mapping={"values":[1,3,5], "value_min":0, "value_max":7}, as_ranges=True)
    """
    from PyQt5.QtGui import QColor
    from PyQt5.QtCore import Qt  # <-- important pour Qt.GlobalColor

    # --- robust converter ---
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

        # PyQt5: Qt.GlobalColor sous forme d'int (ex: Qt.red == 7)
        # PyQt6: réelle enum; QColor(value) sait généralement le gérer aussi
        try:
            return QColor(Qt.GlobalColor(int(value)))
        except Exception:
            pass

        # Dernier recours: tenter QColor(value) (QRgb/int)
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
        if color2 is not None:
            colors = []
            for v in ([vmin]+values if as_ranges else values):
                val = max(min(v, vmax), vmin)  # clamp
                proportion = 0.0 if vmax == vmin else (val - vmin) / (vmax - vmin)
                r = color1.red()   + (color2.red()   - color1.red())   * proportion
                g = color1.green() + (color2.green() - color1.green()) * proportion
                b = color1.blue()  + (color2.blue()  - color1.blue())  * proportion
                colors.append(QColor(int(r), int(g), int(b)))
        else:
            #Ajoute la fonctionnalité one color with mapping mode 
            # raise ValueError("one color with mapping mode yet to be implemented")
            # --- One color with mapping mode ---
            n = len(values)
            extra_steps = n + (3 if as_ranges else 2)
            mid_index = extra_steps // 2

            tmp_colors = []
            # white → color1
            for i in range(mid_index):
                r = 255 + (color1.red() - 255) * i / (mid_index - 1)
                g = 255 + (color1.green() - 255) * i / (mid_index - 1)
                b = 255 + (color1.blue() - 255) * i / (mid_index - 1)
                tmp_colors.append(QColor(int(r), int(g), int(b)))

            # color1 → black
            for i in range(mid_index, extra_steps):
                r = color1.red() * (1 - (i - mid_index) / (extra_steps - mid_index - 1))
                g = color1.green() * (1 - (i - mid_index) / (extra_steps - mid_index - 1))
                b = color1.blue() * (1 - (i - mid_index) / (extra_steps - mid_index - 1))
                tmp_colors.append(QColor(int(r), int(g), int(b)))

            # retirer pur blanc et pur noir
            colors = tmp_colors[1:-1]

        if reverse_gradient:
            colors.reverse()

        # return dict(zip(values, colors)) if as_dict else colors
        if as_dict:
            return dict(zip(values, colors))
        elif as_ranges:
            # Build len(values)+1 ranges: [vmin, v1), [v1, v2), ..., [v_last, inf)
            ranges = []
            # prev = vmin
            for i in range(len(values) + 1):
                start = values[i-1] if i > 0 else 0
                end = values[i] if i < len(values) else float('inf')
                ranges.append((start, end, colors[i]))
            return ranges
        else:
            return colors

    # === NORMAL MODE (le reste de ta version) ===
    if steps < 2:
        raise ValueError("Number of steps must be at least 2.")

    gradient = []
    if color2 is None:
        # Single color mode – extrémités atténuées (white → color1 → black), puis on enlève pur blanc/noir
        extra_steps = steps + 2
        mid_index = extra_steps // 2

        # white → color1
        for i in range(mid_index):
            r = 255 + (color1.red() - 255) * i / (mid_index - 1)
            g = 255 + (color1.green() - 255) * i / (mid_index - 1)
            b = 255 + (color1.blue() - 255) * i / (mid_index - 1)
            gradient.append(QColor(int(r), int(g), int(b)))

        # color1 → black
        for i in range(mid_index, extra_steps):
            r = color1.red() * (1 - (i - mid_index) / (extra_steps - mid_index - 1))
            g = color1.green() * (1 - (i - mid_index) / (extra_steps - mid_index - 1))
            b = color1.blue() * (1 - (i - mid_index) / (extra_steps - mid_index - 1))
            gradient.append(QColor(int(r), int(g), int(b)))

        gradient = gradient[1:-1]  # retire pur blanc & pur noir
    else:
        # color1 → color2
        for i in range(steps):
            t = i / (steps - 1)
            r = color1.red()   + (color2.red()   - color1.red())   * t
            g = color1.green() + (color2.green() - color1.green()) * t
            b = color1.blue()  + (color2.blue()  - color1.blue())  * t
            gradient.append(QColor(int(r), int(g), int(b)))

    if reverse_gradient:
        gradient.reverse()

    return gradient