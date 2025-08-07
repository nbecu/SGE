from PyQt5.QtGui import QFontMetrics, QFont

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
