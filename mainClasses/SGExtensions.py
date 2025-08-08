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
