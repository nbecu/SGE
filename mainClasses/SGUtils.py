from PyQt5.QtGui import QFontMetrics, QFont, QPainter
from PyQt5.QtCore import QRectF

class SGUtils:
    @staticmethod
    def compute_text_size(text, font=None, padding_width=0, padding_height=0):
        """
        Calcule dynamiquement la largeur et la hauteur nécessaires pour afficher un texte avec la police donnée.
        :param text: Texte à mesurer
        :param font: QFont à utiliser (optionnel, par défaut Verdana 8)
        :param padding_width: marge à ajouter à la largeur (en pixels)
        :param padding_height: marge à ajouter à la hauteur (en pixels)
        :return: (largeur totale, hauteur totale) (tuple d'int)
        """
        if font is None:
            font = QFont("Verdana", 8)
        metrics = QFontMetrics(font)
        width = metrics.width(text) + padding_width
        height = metrics.height() + padding_height
        return width, height


# Ajout de la méthode à QPainter pour un usage direct
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

QPainter.drawTextAutoSized = drawTextAutoSized
