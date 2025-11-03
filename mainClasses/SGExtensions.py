"""
SGExtensions.py
This file groups all general utility methods, as well as class extensions (Qt or not) used in the project.
Example: methods dynamically added to QPainter, QWidget, list, dict, etc.
"""

from PyQt5.QtGui import QFontMetrics, QFont, QPainter
from PyQt5.QtCore import QRectF, Qt

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

# Extend Qt with additional colors
def _extend_qt_colors():
    """Add custom colors to Qt namespace"""
    from PyQt5.QtGui import QColor
    
    # Add other useful colors as QColor objects
    Qt.pink = QColor.fromRgb(255, 192, 203)  # Pink
    Qt.orange = QColor.fromRgb(255, 165, 0)  # Orange
    Qt.cyan = QColor.fromRgb(0, 255, 255)    # Cyan
    Qt.lime = QColor.fromRgb(0, 255, 0)      # Lime
    Qt.indigo = QColor.fromRgb(75, 0, 130)   # Indigo
    Qt.violet = QColor.fromRgb(238, 130, 238) # Violet
    Qt.teal = QColor.fromRgb(0, 128, 128)    # Teal
    Qt.amber = QColor.fromRgb(255, 191, 0)   # Amber
    Qt.brown = QColor.fromRgb(165, 42, 42)   # Brown
    Qt.grey = QColor.fromRgb(128, 128, 128)  # Grey
    Qt.gray = QColor.fromRgb(128, 128, 128)  # Alternative spelling
    Qt.lightsteelblue = QColor.fromRgb(176, 196, 222)  # Light Steel Blue
    Qt.tomato = QColor.fromRgb(255, 99, 71)  # Tomato
    Qt.darkgray = QColor.fromRgb(169, 169, 169)  # Dark Gray
    Qt.mediumvioletred = QColor.fromRgb(199, 21, 133)  # Medium Violet Red
    
    # Thematic colors - Blues
    Qt.lightblue = QColor.fromRgb(173, 216, 230)  # Light Blue
    Qt.lightBlue = Qt.lightblue  # CamelCase variant
    Qt.darkblue = QColor.fromRgb(0, 0, 139)  # Dark Blue
    Qt.darkBlue = Qt.darkblue  # CamelCase variant
    
    # Thematic colors - Reds
    Qt.crimson = QColor.fromRgb(220, 20, 60)  # Crimson
    Qt.darkred = QColor.fromRgb(139, 0, 0)  # Dark Red
    Qt.darkRed = Qt.darkred  # CamelCase variant
    Qt.lightcoral = QColor.fromRgb(240, 128, 128)  # Light Coral
    Qt.lightCoral = Qt.lightcoral  # CamelCase variant
    
    # Thematic colors - Greens
    Qt.darkgreen = QColor.fromRgb(0, 100, 0)  # Dark Green
    Qt.darkGreen = Qt.darkgreen  # CamelCase variant
    Qt.lightgreen = QColor.fromRgb(144, 238, 144)  # Light Green
    Qt.lightGreen = Qt.lightgreen  # CamelCase variant
    Qt.forestgreen = QColor.fromRgb(34, 139, 34)  # Forest Green
    Qt.forestGreen = Qt.forestgreen  # CamelCase variant
    Qt.seagreen = QColor.fromRgb(46, 139, 87)  # Sea Green
    Qt.seaGreen = Qt.seagreen  # CamelCase variant
    
    # Thematic colors - Yellows/Oranges
    Qt.gold = QColor.fromRgb(255, 215, 0)  # Gold
    Qt.darkorange = QColor.fromRgb(255, 140, 0)  # Dark Orange
    Qt.darkOrange = Qt.darkorange  # CamelCase variant
    Qt.lightyellow = QColor.fromRgb(255, 255, 224)  # Light Yellow
    Qt.lightYellow = Qt.lightyellow  # CamelCase variant
    Qt.khaki = QColor.fromRgb(240, 230, 140)  # Khaki
    
    # Thematic colors - Violets/Magentas
    Qt.darkviolet = QColor.fromRgb(148, 0, 211)  # Dark Violet
    Qt.darkViolet = Qt.darkviolet  # CamelCase variant
    Qt.plum = QColor.fromRgb(221, 160, 221)  # Plum
    Qt.lavender = QColor.fromRgb(230, 230, 250)  # Lavender
    
    # Thematic colors - Grays
    Qt.lightgray = QColor.fromRgb(211, 211, 211)  # Light Gray
    Qt.lightGray = Qt.lightgray  # CamelCase variant
    Qt.silver = QColor.fromRgb(192, 192, 192)  # Silver
    Qt.slategray = QColor.fromRgb(112, 128, 144)  # Slate Gray
    Qt.slateGray = Qt.slategray  # CamelCase variant
    
    # Missing basic colors
    Qt.purple = QColor.fromRgb(128, 0, 128)  # Purple
    Qt.steelblue = QColor.fromRgb(70, 130, 180)  # Steel Blue
    Qt.steelBlue = Qt.steelblue  # CamelCase variant
    
    # Additional thematic colors - Blues
    Qt.navy = QColor.fromRgb(0, 0, 128)  # Navy
    Qt.royalblue = QColor.fromRgb(65, 105, 225)  # Royal Blue
    Qt.royalBlue = Qt.royalblue  # CamelCase variant
    Qt.skyblue = QColor.fromRgb(135, 206, 235)  # Sky Blue
    Qt.skyBlue = Qt.skyblue  # CamelCase variant
    Qt.powderblue = QColor.fromRgb(176, 224, 230)  # Powder Blue
    Qt.powderBlue = Qt.powderblue  # CamelCase variant
    
    # Additional thematic colors - Reds
    Qt.firebrick = QColor.fromRgb(178, 34, 34)  # Fire Brick
    Qt.fireBrick = Qt.firebrick  # CamelCase variant
    Qt.indianred = QColor.fromRgb(205, 92, 92)  # Indian Red
    Qt.indianRed = Qt.indianred  # CamelCase variant
    Qt.salmon = QColor.fromRgb(250, 128, 114)  # Salmon
    Qt.rosybrown = QColor.fromRgb(188, 143, 143)  # Rosy Brown
    Qt.rosyBrown = Qt.rosybrown  # CamelCase variant
    
    # Additional thematic colors - Greens
    Qt.olive = QColor.fromRgb(128, 128, 0)  # Olive
    Qt.olivedrab = QColor.fromRgb(107, 142, 35)  # Olive Drab
    Qt.oliveDrab = Qt.olivedrab  # CamelCase variant
    Qt.springgreen = QColor.fromRgb(0, 255, 127)  # Spring Green
    Qt.springGreen = Qt.springgreen  # CamelCase variant
    Qt.palegreen = QColor.fromRgb(152, 251, 152)  # Pale Green
    Qt.paleGreen = Qt.palegreen  # CamelCase variant
    
    # Additional thematic colors - Yellows/Oranges
    Qt.peachpuff = QColor.fromRgb(255, 218, 185)  # Peach Puff
    Qt.peachPuff = Qt.peachpuff  # CamelCase variant
    Qt.moccasin = QColor.fromRgb(255, 228, 181)  # Moccasin
    Qt.papayawhip = QColor.fromRgb(255, 239, 213)  # Papaya Whip
    Qt.papayaWhip = Qt.papayawhip  # CamelCase variant
    
    # Additional thematic colors - Purples/Magentas
    Qt.orchid = QColor.fromRgb(218, 112, 214)  # Orchid
    Qt.thistle = QColor.fromRgb(216, 191, 216)  # Thistle
    Qt.mediumorchid = QColor.fromRgb(186, 85, 211)  # Medium Orchid
    Qt.mediumOrchid = Qt.mediumorchid  # CamelCase variant
    Qt.mediumpurple = QColor.fromRgb(147, 112, 219)  # Medium Purple
    Qt.mediumPurple = Qt.mediumpurple  # CamelCase variant
    
    # Additional thematic colors - Grays
    Qt.dimgray = QColor.fromRgb(105, 105, 105)  # Dim Gray
    Qt.dimGray = Qt.dimgray  # CamelCase variant
    Qt.gainsboro = QColor.fromRgb(220, 220, 220)  # Gainsboro
    Qt.whitesmoke = QColor.fromRgb(245, 245, 245)  # White Smoke
    Qt.whiteSmoke = Qt.whitesmoke  # CamelCase variant
    Qt.darkslategray = QColor.fromRgb(47, 79, 79)  # Dark Slate Gray
    Qt.darkSlateGray = Qt.darkslategray  # CamelCase variant
    
    # Additional thematic colors - Browns
    Qt.saddlebrown = QColor.fromRgb(139, 69, 19)  # Saddle Brown
    Qt.saddleBrown = Qt.saddlebrown  # CamelCase variant
    Qt.sienna = QColor.fromRgb(160, 82, 45)  # Sienna
    Qt.chocolate = QColor.fromRgb(210, 105, 30)  # Chocolate
    Qt.peru = QColor.fromRgb(205, 133, 63)  # Peru
    Qt.burlywood = QColor.fromRgb(222, 184, 135)  # Burlywood
    Qt.burlyWood = Qt.burlywood  # CamelCase variant
    Qt.tan = QColor.fromRgb(210, 180, 140)  # Tan
    Qt.wheat = QColor.fromRgb(245, 222, 179)  # Wheat
    Qt.cornsilk = QColor.fromRgb(255, 248, 220)  # Cornsilk
    Qt.cornSilk = Qt.cornsilk  # CamelCase variant
    
    # Red gradient colors
    Qt.maroon = QColor.fromRgb(128, 0, 0)  # Maroon
    Qt.orangered = QColor.fromRgb(255, 69, 0)  # Orange Red
    Qt.orangeRed = Qt.orangered  # CamelCase variant
    Qt.coral = QColor.fromRgb(255, 127, 80)  # Coral
    Qt.lightsalmon = QColor.fromRgb(255, 160, 122)  # Light Salmon
    Qt.lightSalmon = Qt.lightsalmon  # CamelCase variant
    Qt.mistyrose = QColor.fromRgb(255, 228, 225)  # Misty Rose
    Qt.mistyRose = Qt.mistyrose  # CamelCase variant
    
    # Blue gradient colors
    Qt.midnightblue = QColor.fromRgb(25, 25, 112)  # Midnight Blue
    Qt.midnightBlue = Qt.midnightblue  # CamelCase variant
    Qt.mediumblue = QColor.fromRgb(0, 0, 205)  # Medium Blue
    Qt.mediumBlue = Qt.mediumblue  # CamelCase variant
    Qt.cornflowerblue = QColor.fromRgb(100, 149, 237)  # Cornflower Blue
    Qt.cornflowerBlue = Qt.cornflowerblue  # CamelCase variant
    Qt.aliceblue = QColor.fromRgb(240, 248, 255)  # Alice Blue
    Qt.aliceBlue = Qt.aliceblue  # CamelCase variant
    
    # Yellow gradient colors
    Qt.darkgoldenrod = QColor.fromRgb(184, 134, 11)  # Dark Goldenrod
    Qt.darkGoldenrod = Qt.darkgoldenrod  # CamelCase variant
    Qt.goldenrod = QColor.fromRgb(218, 165, 32)  # Goldenrod
    Qt.lemonchiffon = QColor.fromRgb(255, 250, 205)  # Lemon Chiffon
    Qt.lemonChiffon = Qt.lemonchiffon  # CamelCase variant
    Qt.ivory = QColor.fromRgb(255, 255, 240)  # Ivory
    
    # Additional colors
    Qt.turquoise = QColor.fromRgb(64, 224, 208)  # Turquoise
    Qt.hotpink = QColor.fromRgb(255, 105, 180)  # Hot Pink
    Qt.hotPink = Qt.hotpink  # CamelCase variant
    Qt.limegreen = QColor.fromRgb(50, 205, 50)  # Lime Green
    Qt.limeGreen = Qt.limegreen  # CamelCase variant
    Qt.darkorange = QColor.fromRgb(255, 140, 0)  # Dark Orange
    Qt.darkOrange = Qt.darkorange  # CamelCase variant

# Initialize the color extensions
_extend_qt_colors()

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


def normalize_type_name(type_name):
    """
    Normalize a agent or cell type name to a string, handling both string and SGAgentType or SGCellType inputs.
    
    This utility method extracts the entity name from SGAgentType or SGCellType objects
    or returns the string as-is for string inputs.
    
    :param type_name: Either a string type name or an SGAgentType or SGCellType object
    :return: The normalized agent or cell type name as a string
    """
    from mainClasses.SGEntityType import SGAgentType, SGCellType
    if isinstance(type_name, SGAgentType) or isinstance(type_name, SGCellType):
        return type_name.name
    return type_name


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

        # PyQt5: Qt.GlobalColor as int (e.g., Qt.red == 7)
        # PyQt6: real enum; QColor(value) usually handles it
        try:
            return QColor(Qt.GlobalColor(int(value)))
        except Exception:
            pass

        # Last resort: try QColor(value) (QRgb/int)
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
            # Add one color with mapping mode functionality
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

            # remove pure white and pure black
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
        # Single color mode – attenuated extremes (white → color1 → black), then remove pure white/black
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

        gradient = gradient[1:-1]  # remove pure white & pure black
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


def serialize_any_object(obj):
    """
    Serialize any object safely for JSON/CSV export.
    
    This function handles any object type by converting it to a string representation.
    
    :param obj: Object to serialize (can be any type)
    :return: Serialized representation of the object
    """
    if hasattr(obj, '__dict__'):
        # For SGE objects, use their own serialization method
        if hasattr(obj, 'getObjectIdentiferForExport'):
            return obj.getObjectIdentiferForExport()
        elif hasattr(obj, 'id'):
            # Fallback for objects with id but no getObjectIdentiferForExport method
            return f"{obj.__class__.__name__}_id_{obj.id}"
        else:
            return str(obj)
    elif isinstance(obj, (list, tuple)):
        return [serialize_any_object(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: serialize_any_object(value) for key, value in obj.items()}
    else:
        return str(obj)


def position_dialog_to_right(dialog, parent=None):
    """
    Position a dialog to the right of a parent window.
    
    This utility function positions a dialog window to the right edge of a parent window,
    with automatic adjustment if the dialog would overflow the screen boundaries.
    
    :param dialog: The dialog widget to position (QDialog, QColorDialog, etc.)
    :param parent: The parent window to position relative to. If None, attempts to find parent
                   from dialog.parent() or dialog.model (if available). If still None, no positioning is done.
    """
    from PyQt5.QtWidgets import QWidget, QApplication
    
    try:
        # Try to get parent from various sources
        if parent is None:
            parent = dialog.parent() if isinstance(dialog.parent(), QWidget) else None
        if parent is None and hasattr(dialog, 'model') and isinstance(dialog.model, QWidget):
            parent = dialog.model
        if parent is None:
            return
        
        # Parent frame geometry is already in global coords
        pg = parent.frameGeometry() if hasattr(parent, 'frameGeometry') else parent.geometry()
        
        # Compute desired to-the-right position
        target_x = pg.right()
        target_y = pg.top()
        
        # Fit inside available screen geometry of the parent's screen
        desk = QApplication.desktop()
        try:
            screen_num = desk.screenNumber(parent)
            available = desk.availableGeometry(screen_num)
        except Exception:
            available = desk.availableGeometry()
        
        w = dialog.width()
        h = dialog.height()
        
        # Adjust if overflowing to the right/bottom
        if target_x + w > available.right():
            target_x = max(available.left(), available.right() - w)
        if target_y + h > available.bottom():
            target_y = max(available.top(), available.bottom() - h)
        
        dialog.move(target_x, target_y)
    except Exception:
        pass