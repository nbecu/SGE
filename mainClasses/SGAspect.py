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
        
        # Extended attributes from SGLabel and SGButton
        self.border_radius = None
        self.min_width = None
        self.min_height = None
        self.padding = None
        self.word_wrap = False
        self.background_image = None
        self.fixed_width = None
        self.fixed_height = None
        
        # Hover states
        self.hover_text_color = None
        self.hover_background_color = None
        self.hover_border_color = None
        
        # Button states
        self.pressed_color = None
        self.disabled_color = None


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

    @classmethod
    def success(cls):
        """Theme for success state (e.g., completed conditions)"""
        instance = cls()
        instance.color = 'darkgreen'
        instance.font_weight = 'bold'
        return instance

    @classmethod
    def inactive(cls):
        """Theme for inactive state (e.g., disabled control panels)"""
        instance = cls()
        instance.background_color = 'darkgray'
        instance.color = 'gray'
        return instance

    @classmethod
    def modern(cls):
        """Modern theme with clean lines and subtle colors"""
        instance = cls()
        instance.background_color = '#f8f9fa'
        instance.border_color = '#dee2e6'
        instance.border_size = 1
        instance.border_style = 'solid'
        instance.color = '#495057'
        instance.font = 'Arial'
        instance.size = 12
        instance.border_radius = 4
        instance.padding = 8
        # Add text_aspects structure for differentiated text styling
        instance._text_aspects = {
            'title1': {'color': '#495057', 'font': 'Arial', 'size': 14, 'font_weight': 'bold'},
            'title2': {'color': '#495057', 'font': 'Arial', 'size': 12},
            'title3': {'color': '#495057', 'font': 'Arial', 'size': 11, 'font_weight': 'bold'},
            'text1': {'color': '#495057', 'font': 'Arial', 'size': 12},
            'text2': {'color': '#495057', 'font': 'Arial', 'size': 12},
            'text3': {'color': '#495057', 'font': 'Arial', 'size': 12, 'font_style': 'italic'}
        }
        return instance

    @classmethod
    def minimal(cls):
        """Minimal theme with no borders and clean typography"""
        instance = cls()
        instance.background_color = 'white'
        instance.border_size = 0
        instance.color = '#212529'
        instance.font = 'Arial'
        instance.size = 12
        instance.padding = 4
        # Add text_aspects structure for differentiated text styling
        instance._text_aspects = {
            'title1': {'color': '#212529', 'font': 'Arial', 'size': 14, 'font_weight': 'bold'},
            'title2': {'color': '#212529', 'font': 'Arial', 'size': 12},
            'title3': {'color': '#212529', 'font': 'Arial', 'size': 11, 'font_weight': 'bold'},
            'text1': {'color': '#212529', 'font': 'Arial', 'size': 12},
            'text2': {'color': '#212529', 'font': 'Arial', 'size': 12},
            'text3': {'color': '#212529', 'font': 'Arial', 'size': 12, 'font_style': 'italic'}
        }
        return instance

    @classmethod
    def colorful(cls):
        """Colorful theme with vibrant colors"""
        instance = cls()
        instance.background_color = '#e3f2fd'
        instance.border_color = '#2196f3'
        instance.border_size = 2
        instance.border_style = 'solid'
        instance.color = '#1976d2'
        instance.font = 'Arial'
        instance.size = 12
        instance.font_weight = 'bold'
        instance.border_radius = 6
        instance.padding = 10
        # Add text_aspects structure for differentiated text styling
        instance._text_aspects = {
            'title1': {'color': '#1976d2', 'font': 'Arial', 'size': 14, 'font_weight': 'bold'},
            'title2': {'color': '#1976d2', 'font': 'Arial', 'size': 12, 'font_weight': 'bold'},
            'title3': {'color': '#1976d2', 'font': 'Arial', 'size': 11, 'font_weight': 'bold'},
            'text1': {'color': '#1976d2', 'font': 'Arial', 'size': 12, 'font_weight': 'bold'},
            'text2': {'color': '#1976d2', 'font': 'Arial', 'size': 12, 'font_weight': 'bold'},
            'text3': {'color': '#1976d2', 'font': 'Arial', 'size': 12, 'font_weight': 'bold', 'font_style': 'italic'}
        }
        return instance

    @classmethod
    def blue(cls):
        """Blue theme with blue tones"""
        instance = cls()
        instance.background_color = '#e1f5fe'
        instance.border_color = '#0277bd'
        instance.border_size = 1
        instance.border_style = 'solid'
        instance.color = '#01579b'
        instance.font = 'Arial'
        instance.size = 12
        instance.border_radius = 3
        instance.padding = 6
        # Add text_aspects structure for differentiated text styling
        instance._text_aspects = {
            'title1': {'color': '#01579b', 'font': 'Arial', 'size': 14, 'font_weight': 'bold'},
            'title2': {'color': '#01579b', 'font': 'Arial', 'size': 12},
            'title3': {'color': '#01579b', 'font': 'Arial', 'size': 11, 'font_weight': 'bold'},
            'text1': {'color': '#01579b', 'font': 'Arial', 'size': 12},
            'text2': {'color': '#01579b', 'font': 'Arial', 'size': 12},
            'text3': {'color': '#01579b', 'font': 'Arial', 'size': 12, 'font_style': 'italic'}
        }
        return instance

    @classmethod
    def green(cls):
        """Green theme with green tones"""
        instance = cls()
        instance.background_color = '#e8f5e8'
        instance.border_color = '#388e3c'
        instance.border_size = 1
        instance.border_style = 'solid'
        instance.color = '#1b5e20'
        instance.font = 'Arial'
        instance.size = 12
        instance.border_radius = 3
        instance.padding = 6
        # Add text_aspects structure for differentiated text styling
        instance._text_aspects = {
            'title1': {'color': '#1b5e20', 'font': 'Arial', 'size': 14, 'font_weight': 'bold'},
            'title2': {'color': '#1b5e20', 'font': 'Arial', 'size': 12},
            'title3': {'color': '#1b5e20', 'font': 'Arial', 'size': 11, 'font_weight': 'bold'},
            'text1': {'color': '#1b5e20', 'font': 'Arial', 'size': 12},
            'text2': {'color': '#1b5e20', 'font': 'Arial', 'size': 12},
            'text3': {'color': '#1b5e20', 'font': 'Arial', 'size': 12, 'font_style': 'italic'}
        }
        return instance

    @classmethod
    def gray(cls):
        """Gray theme with gray tones"""
        instance = cls()
        instance.background_color = '#f5f5f5'
        instance.border_color = '#757575'
        instance.border_size = 1
        instance.border_style = 'solid'
        instance.color = '#424242'
        instance.font = 'Arial'
        instance.size = 12
        instance.border_radius = 3
        instance.padding = 6
        # Add text_aspects structure for differentiated text styling
        instance._text_aspects = {
            'title1': {'color': '#424242', 'font': 'Arial', 'size': 14, 'font_weight': 'bold'},
            'title2': {'color': '#424242', 'font': 'Arial', 'size': 12},
            'title3': {'color': '#424242', 'font': 'Arial', 'size': 11, 'font_weight': 'bold'},
            'text1': {'color': '#424242', 'font': 'Arial', 'size': 12},
            'text2': {'color': '#424242', 'font': 'Arial', 'size': 12},
            'text3': {'color': '#424242', 'font': 'Arial', 'size': 12, 'font_style': 'italic'}
        }
        return instance
    # ------------------------------------------------------------------------------------------------
   

    # Methods to get the parameters
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
        return self._css_to_qcolor(self.border_color)
    
    # def getBackgroundColor(self):
    #     return self.background_color
    
    def getBackgroundColorValue(self):
        if self.background_color is None:
            return QColor(Qt.transparent)
        if isinstance(self.background_color, str) and self.background_color.lower() == 'transparent':
            c = QColor(0, 0, 0)
            c.setAlpha(0)
            return c
        return self._css_to_qcolor(self.background_color)
    
    def getBackgroundColorValue_whenDisactivated(self):
        return QColor(QColor(100, 100, 100)) #Gray color
    
    def getBrushPattern_whenDisactivated(self):
        return Qt.DiagCrossPattern
                # Qt.NoBrush  # Pas de remplissage
                # Qt.Dense1Pattern  # Motif dense
                # Qt.Dense3Pattern  # Motif moins dense
                # Qt.HorPattern    # Lignes horizontales
                # Qt.VerPattern    # Lignes verticales
                # Qt.CrossPattern  # Motif en croix
                # Qt.DiagCrossPattern # Motif en croix diagonale

    # Méthodes pour créer les spécifications de style
    def getTextStyle(self):
        css_color = self._qt_color_to_css(self.color)
        textStyle_specs = f"font-family: {self.font}; font-size: {self.size}px; color: {css_color}; text-decoration: {self.text_decoration}; font-weight: {self.font_weight}; font-style: {self.font_style};"
        return textStyle_specs

    def getBorderStyle(self):
        css_color = self._qt_color_to_css(self.border_color)
        borderStyle_specs = f"border: {self.border_size}px {self.border_style} {css_color};"
        return borderStyle_specs

    def getBackgroundStyle(self):
        css_color = self._qt_color_to_css(self.background_color)
        backgroundColor_specs = f"background-color: {css_color};"
        return backgroundColor_specs

    def getCompleteStyle(self):
        textStyle_specs = self.getTextStyle()
        borderStyle_specs = self.getBorderStyle()
        backgroundColor_specs = self.getBackgroundStyle()
        complete_style = f"{backgroundColor_specs}{textStyle_specs}{borderStyle_specs}"
        return complete_style

    # Extended getter methods for new attributes
    def getBorderRadius(self):
        return self.border_radius

    def getMinWidth(self):
        return self.min_width

    def getMinHeight(self):
        return self.min_height

    def getPadding(self):
        return self.padding

    def getWordWrap(self):
        return self.word_wrap

    def getBackgroundImage(self):
        return self.background_image

    def getFixedWidth(self):
        return self.fixed_width

    def getFixedHeight(self):
        return self.fixed_height

    def getHoverTextColor(self):
        return self.hover_text_color

    def getHoverBackgroundColor(self):
        return self.hover_background_color

    def getHoverBorderColor(self):
        return self.hover_border_color

    def getPressedColor(self):
        return self.pressed_color

    def getDisabledColor(self):
        return self.disabled_color

    # Extended style methods
    def _qt_color_to_css(self, color):
        """Convert Qt color to CSS format"""
        if color is None:
            return None
        try:
            # Explicit transparent support
            if isinstance(color, str) and color.lower() == 'transparent':
                return 'transparent'
            # If it's already a QColor, get its name
            if hasattr(color, 'name'):
                return color.name()
            # If it's a Qt color constant, convert to QColor first
            elif hasattr(color, 'value'):
                qcolor = QColor(color)
                return qcolor.name()
            # Handle Qt color constants directly
            else:
                qcolor = QColor(color)
                if qcolor.isValid():
                    return qcolor.name()
                else:
                    return str(color)
        except:
            return str(color)
    
    def _css_to_qcolor(self, value):
        """Convert CSS-like color strings (e.g., rgb(), rgba()) or Qt color values to QColor."""
        try:
            # Direct QColor
            if hasattr(value, 'isValid'):
                return value if value.isValid() else QColor()
            if value is None:
                return QColor()
            if isinstance(value, str):
                s = value.strip().lower()
                if s == 'transparent':
                    c = QColor(0, 0, 0)
                    c.setAlpha(0)
                    return c
                if s.startswith('rgba(') and s.endswith(')'):
                    inner = s[5:-1]
                    parts = [p.strip() for p in inner.split(',')]
                    if len(parts) == 4:
                        r = int(float(parts[0]))
                        g = int(float(parts[1]))
                        b = int(float(parts[2]))
                        a_part = parts[3]
                        # alpha may be 0-1 or 0-255
                        a = float(a_part)
                        if a <= 1:
                            a = int(round(a * 255))
                        else:
                            a = int(round(a))
                        c = QColor(r, g, b, max(0, min(255, a)))
                        return c
                if s.startswith('rgb(') and s.endswith(')'):
                    inner = s[4:-1]
                    parts = [p.strip() for p in inner.split(',')]
                    if len(parts) == 3:
                        r = int(float(parts[0]))
                        g = int(float(parts[1]))
                        b = int(float(parts[2]))
                        return QColor(r, g, b)
                # Fallback to QColor parser (names, hex, etc.)
                qc = QColor(value)
                if qc.isValid():
                    return qc
                return QColor()
            # Fallback any type
            return QColor(value)
        except Exception:
            try:
                qc = QColor(value)
                return qc if qc.isValid() else QColor()
            except Exception:
                return QColor()
    
    def getExtendedStyle(self):
        """Get complete style including extended attributes"""
        style_parts = []
        
        # Background
        if self.background_color:
            css_color = self._qt_color_to_css(self.background_color)
            style_parts.append(f"background-color: {css_color}")
        if self.background_image:
            style_parts.append(f"background-image: url({self.background_image})")
        
        # Text
        if self.font:
            style_parts.append(f"font-family: {self.font}")
        if self.size:
            style_parts.append(f"font-size: {self.size}px")
        if self.color:
            css_color = self._qt_color_to_css(self.color)
            style_parts.append(f"color: {css_color}")
        if self.text_decoration != "none":
            style_parts.append(f"text-decoration: {self.text_decoration}")
        if self.font_weight != "normal":
            style_parts.append(f"font-weight: {self.font_weight}")
        if self.font_style != "normal":
            style_parts.append(f"font-style: {self.font_style}")
        
        # Border
        if self.border_size and self.border_style and self.border_color:
            css_color = self._qt_color_to_css(self.border_color)
            style_parts.append(f"border: {self.border_size}px {self.border_style} {css_color}")
        if self.border_radius:
            style_parts.append(f"border-radius: {self.border_radius}px")
        
        # Dimensions
        if self.min_width:
            style_parts.append(f"min-width: {self.min_width}px")
        if self.min_height:
            style_parts.append(f"min-height: {self.min_height}px")
        if self.padding:
            style_parts.append(f"padding: {self.padding}px")
        
        return "; ".join(style_parts)

    def getHoverStyle(self):
        """Get hover state style"""
        if not any([self.hover_text_color, self.hover_background_color, self.hover_border_color]):
            return ""
        
        style_parts = []
        if self.hover_text_color:
            css_color = self._qt_color_to_css(self.hover_text_color)
            style_parts.append(f"color: {css_color}")
        if self.hover_background_color:
            css_color = self._qt_color_to_css(self.hover_background_color)
            style_parts.append(f"background-color: {css_color}")
        if self.hover_border_color:
            css_color = self._qt_color_to_css(self.hover_border_color)
            style_parts.append(f"border-color: {css_color}")
        
        return "; ".join(style_parts)

    def getButtonStatesStyle(self):
        """Get button states style (pressed, disabled)"""
        states = []
        
        if self.pressed_color:
            css_color = self._qt_color_to_css(self.pressed_color)
            states.append(f"QPushButton:pressed {{ background-color: {css_color} }}")
        if self.disabled_color:
            css_color = self._qt_color_to_css(self.disabled_color)
            states.append(f"QPushButton:disabled {{ background-color: {css_color} }}")
        
        return " ".join(states)

    