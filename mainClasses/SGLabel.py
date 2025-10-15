from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGAspect import SGAspect
import re

class SGLabel(SGGameSpace):
    def __init__(self, parent, text, textStyle_specs="", borderStyle_specs="", backgroundColor_specs="",  alignement= "Left", fixedWidth=None, fixedHeight=None):
        # Parse background color from specs for base constructor
        bg_color = self._extract_background_color(backgroundColor_specs)
        super().__init__(parent, 0, 60, 0, 0, true, bg_color if bg_color is not None else Qt.transparent)
        self.model = parent
        self.moveable = True
        self.isDisplay = True
        self._textStyle_specs = textStyle_specs or ""
        self._borderStyle_specs = borderStyle_specs or ""
        self._backgroundColor_specs = backgroundColor_specs or ""

        # Content label
        self.label = QtWidgets.QLabel(text, self)
        if fixedWidth is not None:
            self.label.setFixedWidth(fixedWidth)
            self.label.setWordWrap(True)
        if fixedHeight is not None:
            self.label.setFixedHeight(fixedHeight)
        try:
            self.label.setAlignment(getattr(Qt, "Align"+alignement))
        except Exception:
            self.label.setAlignment(Qt.AlignLeft)

        # Parse legacy CSS specs into gs_aspect/text aspect (backward compatibility)
        try:
            self._apply_specs_to_aspects(self._textStyle_specs, self._borderStyle_specs, self._backgroundColor_specs)
        except Exception:
            pass

        # Layout and sizing
        self.layout = QtWidgets.QVBoxLayout()
        try:
            self.layout.setContentsMargins(4, 0, self.rightMargin, self.verticalGapBetweenLabels)
            self.layout.setSpacing(self.verticalGapBetweenLabels)
        except Exception:
            pass
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        # Apply text aspects and compute size
        try:
            self.onTextAspectsChanged()
        except Exception:
            pass
        self._resize_to_layout_or_label()

    def _resize_to_layout_or_label(self):
        try:
            if hasattr(self, 'layout') and self.layout is not None:
                self.updateSizeFromLayout(self.layout)
            else:
                self.label.adjustSize()
                self.setMinimumSize(self.label.geometry().size())
        except Exception:
            pass

    def _extract_background_color(self, bg_specs: str):
        if not bg_specs:
            return None
        try:
            items = [p.strip() for p in bg_specs.split(';') if p.strip()]
            for it in items:
                if it.lower().startswith('background-color'):
                    val = it.split(':', 1)[1].strip()
                    # return raw string; parsing handled by SGAspect.getBackgroundColorValue
                    return val
        except Exception:
            return None
        return None

    def _apply_specs_to_aspects(self, text_specs: str, border_specs: str, bg_specs: str):
        # Text specs
        if text_specs:
            kv = self._parse_css_kv(text_specs)
            if 'font-family' in kv:
                self.text1_aspect.font = kv['font-family']
            if 'font-size' in kv:
                try:
                    self.text1_aspect.size = int(str(kv['font-size']).replace('px','').strip())
                except Exception:
                    pass
            if 'color' in kv:
                self.text1_aspect.color = kv['color']
            if 'text-decoration' in kv:
                self.text1_aspect.text_decoration = kv['text-decoration']
            if 'font-weight' in kv:
                self.text1_aspect.font_weight = kv['font-weight']
            if 'font-style' in kv:
                self.text1_aspect.font_style = kv['font-style']

        # Border specs (expect unified 'border: size style color')
        if border_specs:
            kv = self._parse_css_kv(border_specs)
            val = kv.get('border')
            if val:
                # Regex: border: <size>px <style> <color...>
                m = re.match(r"^\s*(\d+)px\s+([a-zA-Z]+)\s+(.+?)\s*$", val)
                if m:
                    try:
                        self.gs_aspect.border_size = int(m.group(1))
                    except Exception:
                        pass
                    st = m.group(2).lower()
                    if st in ('solid','dotted','dashed','double','groove','ridge','inset'):
                        self.gs_aspect.border_style = st
                    color_str = m.group(3)
                    # Preserve full rgb()/rgba()/hex/name string
                    self.gs_aspect.border_color = color_str
                else:
                    # Fallback old splitter (may fail on rgba but better than nothing)
                    parts = [x.strip() for x in val.split(' ') if x.strip()]
                    for part in parts:
                        if part.endswith('px'):
                            try:
                                self.gs_aspect.border_size = int(part.replace('px',''))
                            except Exception:
                                pass
                        elif part.lower() in ('solid','dotted','dashed','double','groove','ridge','inset'):
                            self.gs_aspect.border_style = part.lower()
                        else:
                            self.gs_aspect.border_color = part

        # Background color
        bg = self._extract_background_color(bg_specs)
        if bg is not None:
            self.gs_aspect.background_color = bg

    def _parse_css_kv(self, css: str):
        res = {}
        try:
            items = [x.strip() for x in css.split(';') if x.strip()]
            for it in items:
                if ':' in it:
                    k, v = it.split(':', 1)
                    res[k.strip().lower()] = v.strip()
        except Exception:
            return res
        return res

    # =========================
    # STYLE/APPLY HOOKS
    # =========================
    def applyContainerAspectStyle(self):
        """Avoid QSS cascade; rely on paintEvent for container rendering."""
        pass

    def onTextAspectsChanged(self):
        # Apply text1_aspect to internal label
        f = self.label.font()
        if self.text1_aspect.font:
            f.setFamily(self.text1_aspect.font)
        if self.text1_aspect.size:
            try:
                f.setPixelSize(int(self.text1_aspect.size))
            except Exception:
                pass
        try:
            self.applyFontWeightToQFont(f, getattr(self.text1_aspect, 'font_weight', None))
        except Exception:
            pass
        if self.text1_aspect.font_style:
            s = str(self.text1_aspect.font_style).lower()
            f.setItalic(s in ('italic', 'oblique'))
        self.label.setFont(f)
        css_parts = []
        if self.text1_aspect.color:
            try:
                css_color = SGAspect()._qt_color_to_css(self.text1_aspect.color)
            except Exception:
                css_color = QColor(self.text1_aspect.color).name()
            if css_color:
                css_parts.append(f"color: {css_color}")
        td = getattr(self.text1_aspect, 'text_decoration', None)
        css_parts.append(f"text-decoration: {td}" if td and str(td).lower() != 'none' else "text-decoration: none")
        self.label.setStyleSheet("; ".join(css_parts))
        self._resize_to_layout_or_label()

    # =========================
    # RENDERING
    # =========================
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # Background with transparency
        bg = self.gs_aspect.getBackgroundColorValue()
        if bg.alpha() == 0:
            painter.setBrush(Qt.NoBrush)
        else:
            painter.setBrush(QBrush(bg, Qt.SolidPattern))
        # Border with style mapping
        pen = QPen(self.gs_aspect.getBorderColorValue(), self.gs_aspect.getBorderSize())
        style_map = {
            'solid': Qt.SolidLine,
            'dotted': Qt.DotLine,
            'dashed': Qt.DashLine,
            'double': Qt.SolidLine,
            'groove': Qt.SolidLine,
            'ridge': Qt.SolidLine,
            'inset': Qt.SolidLine,
        }
        bs = getattr(self.gs_aspect, 'border_style', None)
        if isinstance(bs, str) and bs.lower() in style_map:
            pen.setStyle(style_map[bs.lower()])
        painter.setPen(pen)
        width = max(0, getattr(self, 'sizeXGlobal', self.width()) - 1)
        height = max(0, getattr(self, 'sizeYGlobal', self.height()) - 1)
        radius = getattr(self.gs_aspect, 'border_radius', None) or 0
        if radius > 0:
            painter.drawRoundedRect(0, 0, width, height, radius, radius)
        else:
            painter.drawRect(0, 0, width, height)
 
  



  

# class SGLabel2(SGLabel):
#     def __init__(self, parent, text, font=None, size=None, color=None, text_decoration="none", font_weight="normal", font_style="normal", alignement= "Left", border_style="solid", border_size=0, border_color=None, background_color=None, fixedWidth=None, fixedHeight=None):
#          # Create the text style
#         textStyle_specs = f"font-family: {font}; font-size: {size}px; color: {color}; text-decoration: {text_decoration}; font-weight: {font_weight}; font-style: {font_style};"
#         # Create the border style
#         borderStyle_specs = f"border: {border_size}px {border_style} {border_color};"     
#         # Create the background style
#         backgroundColor_specs = f"background-color: {background_color};"
        
    
#         super().__init__(parent, text, textStyle_specs, borderStyle_specs, backgroundColor_specs, alignement, fixedWidth, fixedHeight)


# class SGLabel3(QtWidgets.QLabel):
#     def __init__(self, parent, text, font=None, size=None, color=None, text_decoration="none", font_weight="normal", font_style="normal", alignement= "Left", border_style=None, border_size=None, border_color=None, background_color=None, fixedWidth=None, fixedHeight=None):

#         # in case one parameter of border is defined, sets a default value for the other border parameters that are None
#         hasABorder = any(value is not None for value in [border_size, border_color, border_style])
#         if hasABorder:
#             if border_size is None: border_size = 1
#             if border_color is None: border_color = "black"
#             if border_style is None: border_style = "solid"

#          # Create the text style
#         textStyle_specs = f"font-family: {font}; font-size: {size}px; color: {color}; text-decoration: {text_decoration}; font-weight: {font_weight}; font-style: {font_style};"
#         # Create the border style
#         borderStyle_specs = f"border: {border_size}px {border_style} {border_color};"     
#         # Create the background style
#         backgroundColor_specs = f"background-color: {background_color};"
        
    
#         # super().__init__(parent, text, text_specs, border_specs, background_specs, alignement, fixedWidth, fixedHeight)
#         super().__init__()
#         self.setText(text)
#         if fixedWidth is not None:
#             self.setFixedWidth(fixedWidth)
#             self.setWordWrap(True)  # Allow line wrapping if the text is too long

#         if fixedHeight is not None:
#             self.setFixedHeight(fixedHeight)
        
#         self.setAlignment(getattr(Qt, "Align"+alignement)) 

        
#         # Build the complete stylesheet
#         complete_style = f"{backgroundColor_specs}{textStyle_specs}{borderStyle_specs}"
#         self.setStyleSheet(complete_style)
#         # label.setFont(QFont('Arial', 18)) -> Other way to set the Font
        
#         # ajust the size of the label according to its style font and border. Then redefine the size of the widget according to the size of the geometry of the label 
#         self.adjustSize()   
#         self.setFixedSize(self.geometry().size())

        
        
#         self.setParent(parent)
 