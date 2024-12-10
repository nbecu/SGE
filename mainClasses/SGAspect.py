from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *


            
class SGAspect():
    def __init__(self):
        """Define the aspect a text and/or a frame -> text, border, background

        Args:
            font (str, optional): Font family. Options include "Times New Roman", "Georgia", "Garamond", "Baskerville", "Arial", "Helvetica", "Verdana", "Tahoma", "Trebuchet MS", "Courier New", "Lucida Console", "Monaco", "Consolas", "Comic Sans MS", "Papyrus", "Impact".
            size (int, optional): Font size in pixels.
            color (str, optional): Text color. Can be specified by name (e.g., "red", "orange", "navy", "gold"), hex code (e.g., "#FF0000", "#AB28F9"), RGB values (e.g., "rgb(127, 12, 0)"), or RGBA values for transparency (e.g., "rgba(154, 20, 8, 0.5)").
            text_decoration (str, optional): Text decoration style. Options include "none", "underline", "overline", "line-through", "blink".
            font_weight (str, optional): Font weight. Options include "normal", "bold", "bolder", "lighter", "100", "200", "300", "400", "500", "600", "700", "800", "900".
            font_style (str, optional): Font style. Options include "normal", "italic", "oblique".
            alignement (str, optional): Text alignment. Options include "Left", "Right, "HCenter", "Top", "Bottom", "VCenter", "Center", "Justify".
            border_style (str, optional): Border style. Options include "solid", "dotted", "dashed", "double", "groove", "ridge", "inset".
            border_size (int, optional): Border size in pixels.
            border_color (str, optional): Same options as color.
            background_color (str, optional): Same options as color.
        """
        # Définition des paramètres de style
        self.font = None
        self.size = None
        self.color = None
        self.text_decoration = "none"
        self.font_weight = "normal"
        self.font_style = "normal"
        self.alignment = "Left"
        self.border_style = None
        self.border_size = None
        self.border_color = None
        self.background_color = None


    @classmethod
    def baseBorder(cls):
        instance = cls()  # Crée une nouvelle instance de SGAspect
        instance.border_style = 'solid'
        instance.border_size = 1
        instance.border_color = 'black'
        return instance  # Retourne l'instance configurée

    @classmethod
    def title1(cls):
        instance = cls()  # Crée une nouvelle instance de SGAspect
        instance.font = 'Arial'
        instance.size = 14
        instance.font_weight = 'bold'
        return instance  # Retourne l'instance configurée

    @classmethod
    def title2(cls):
        instance = cls()  # Crée une nouvelle instance de SGAspect
        instance.font = 'Arial'
        instance.size = 12
        instance.text_decoration = 'underline'
        return instance  # Retourne l'instance configurée

    @classmethod
    def title3(cls):
        instance = cls()  # Crée une nouvelle instance de SGAspect
        instance.font = 'Georgia'
        instance.size = 11
        instance.font_weight = 'bold'
        return instance  # Retourne l'instance configurée

    @classmethod
    def text1(cls):
        instance = cls()  # Crée une nouvelle instance de SGAspect
        instance.font = 'Georgia'
        instance.size = 12
        instance.color = 'black'
        return instance  # Retourne l'instance configurée

    @classmethod
    def text2(cls):
        instance = cls()  # Crée une nouvelle instance de SGAspect
        instance.font = 'Arial'
        instance.size = 12
        instance.color = 'black'
        return instance  # Retourne l'instance configurée

    @classmethod
    def text3(cls):
        instance = cls()  # Crée une nouvelle instance de SGAspect
        instance.font = 'Georgia'
        instance.size = 12
        instance.color = 'black'
        instance.font_style = 'italic'
        return instance  # Retourne l'instance configurée

    # Méthodes pour obtenir les paramètres
    def getFont(self):
        return self.font

    def getSize(self):
        return self.size

    def getColor(self):
        return self.color

    def getTextDecoration(self):
        return self.text_decoration

    def getFontWeight(self):
        return self.font_weight

    def getFontStyle(self):
        return self.font_style

    def getAlignment(self):
        return self.alignment

    def getBorderStyle(self):
        return self.border_style

    def getBorderSize(self):
        return self.border_size

    # def getBorderColor(self):
    #     return self.border_color

    def getBorderColorValue(self):
        return QColor(self.border_color)
    
    # def getBackgroundColor(self):
    #     return self.background_color
    
    def getBackgroundColorValue(self):
        return QColor(self.background_color)

    # Méthodes pour créer les spécifications de style
    def getTextStyle(self):
        textStyle_specs = f"font-family: {self.font}; font-size: {self.size}px; color: {self.color}; text-decoration: {self.text_decoration}; font-weight: {self.font_weight}; font-style: {self.font_style};"
        return textStyle_specs

    def getBorderStyle(self):
        borderStyle_specs = f"border: {self.border_size}px {self.border_style} {self.border_color};"
        return borderStyle_specs

    def getBackgroundStyle(self):
        backgroundColor_specs = f"background-color: {self.background_color};"
        return backgroundColor_specs

    def getCompleteStyle(self):
        textStyle_specs = self.getTextStyle()
        borderStyle_specs = self.getBorderStyle()
        backgroundColor_specs = self.getBackgroundStyle()
        complete_style = f"{backgroundColor_specs}{textStyle_specs}{borderStyle_specs}"
        return complete_style

    