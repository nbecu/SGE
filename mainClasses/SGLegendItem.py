from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QToolTip
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from mainClasses.SGExtensions import *
from math import inf


#Class who is responsible of creation legend item 
class SGLegendItem(QtWidgets.QWidget):
    def __init__(self,parent,type,text,typeOrShape=None,color=Qt.black,nameOfAttribut="",valueOfAttribut="",isBorderItem=False,borderColorAndWidth=None,gameAction=None,gradient_colors=None,gradient_min_value=None,gradient_max_value=None):
        super().__init__(parent)
        #Basic initialize
        self.legend=parent
        self.type=type
        self.posY=self.legend.posYOfItems
        self.legend.posYOfItems +=1
        self.text=str(text)
        if typeOrShape == 'square' or typeOrShape is None:
            self.shape= typeOrShape
        else:
            self.typeDef=typeOrShape
            self.shape=self.typeDef.shape
        self.color=color
        self.nameOfAttribut=nameOfAttribut
        self.valueOfAttribut=valueOfAttribut
        self.isBorderItem=isBorderItem
        if self.isBorderItem:
            self.borderColorAndWidth=borderColorAndWidth
            default_aspect = self.typeDef.get_default_aspect()
            self.color = default_aspect.background_color if default_aspect else self.typeDef.defaultShapeColor
        self.remainNumber=int
        self.gameAction= gameAction
        # Gradient bar support (Phase 3)
        self.gradient_colors = gradient_colors  # List of QColor for gradient bar
        self.gradient_min_value = gradient_min_value  # Min value for gradient label
        self.gradient_max_value = gradient_max_value  # Max value for gradient label
        self.is_gradient_bar = gradient_colors is not None

    def event(self, e):
        # Intercept tooltip event to show the number of remaining acions for gameActions
        if e.type() == QEvent.Type.ToolTip:
            if self.gameAction is not None:
                # Dynamically update tooltip
                aNumber = self.gameAction.getNbRemainingActions()
                if aNumber == inf:
                    text = f"∞ actions"
                else:
                    text = f"{self.gameAction.getNbRemainingActions()} actions remaining"
                QToolTip.showText(e.globalPos(), text, self)
            return True  # event handled
        return super().event(e)
    

    def isSelectable(self):
        # Title1 and Title2 items are not selectable
        # For SGLegend (pure legend), items should not be selectable unless they have a gameAction
        # For SGControlPanel (controller), items should be selectable if they have a gameAction
        if self.type in ['Title1','Title2']:
            return False
        # If this is a pure legend item (no gameAction), it should not be selectable
        if self.gameAction is None:
            return False
        # If this is a control panel item (has gameAction), it should be selectable
        return True
    
    def isSymbolOnCell(self):
        return self.type == 'symbol' and self.typeDef.category() == 'Cell'#self.shape in ["square","hexagonal"]

    def isSymbolOnAgent(self):
        return self.type == 'symbol' and self.typeDef.category() =='Agent' # in ("circleAgent","squareAgent", "ellipseAgent1","ellipseAgent2", "rectAgent1","rectAgent2", "triangleAgent1","triangleAgent2", "arrowAgent1","arrowAgent2")

    def _getSymbolRectWidth(self):
        scale = getattr(self.legend, "symbolScale", 1.0)
        try:
            scale = float(scale)
        except Exception:
            scale = 1.0
        if self.shape == "hexagonal":
            return int(30 * scale)
        if self.shape in (
            "circleAgent", "squareAgent", "ellipseAgent1", "ellipseAgent2",
            "rectAgent1", "rectAgent2", "triangleAgent1", "triangleAgent2",
            "arrowAgent1", "arrowAgent2"
        ):
            return int(20 * scale)
        if self.shape in ("circleTile", "ellipseTile"):
            return int(18 * scale)
        return int(18 * scale)

    def _fontFromAspect(self, aspect):
        font = QFont()
        if getattr(aspect, "font", None):
            font.setFamily(aspect.font)
        if getattr(aspect, "size", None):
            try:
                font.setPixelSize(int(aspect.size))
            except Exception:
                pass
        try:
            if hasattr(self.legend, "applyFontWeightToQFont"):
                self.legend.applyFontWeightToQFont(font, getattr(aspect, "font_weight", None))
        except Exception:
            pass
        return font

    def getRequiredWidth(self):
        # Special case: gradient bar (Phase 3)
        if self.is_gradient_bar:
            return 150 + 40  # Bar width + generous label padding

        text = "" if self.text is None else str(self.text)
        if self.type == "Title1":
            aspect = getattr(self.legend, "title1_aspect", None)
            base_x = 15
        elif self.type in ("Title2", "None"):
            aspect = getattr(self.legend, "title2_aspect", None)
            base_x = 15
        else:
            aspect = getattr(self.legend, "text1_aspect", None)
            if self.type == "symbol":
                base_x = self._getSymbolRectWidth() + 10
            else:
                base_x = 30
        try:
            font = self._fontFromAspect(aspect if aspect is not None else type("x", (), {})())
            fm = QFontMetrics(font)
            text_w = fm.boundingRect(text).width()
        except Exception:
            text_w = 0
        if self.type == "symbol" and text == "":
            base_x = self._getSymbolRectWidth() + 2
            right_pad = 2
        else:
            right_pad = 6
        return int(base_x + max(0, text_w) + right_pad)

    #Drawing function
    def paintEvent(self,event):
        if self.legend.isLegend or (self.legend.isControlPanel and self.legend.checkDisplay()):
            painter = QPainter() 
            painter.begin(self)
            is_pixmap = isinstance(self.color, QPixmap)
            if not is_pixmap:
                painter.setBrush(QBrush(self.color, Qt.SolidPattern))
            if (self.legend.isControlPanel and self.legend.selected == self and
                getattr(self.legend, "showSelectionBorder", True)):
                painter.setPen(QPen(Qt.red,2))
            if self.isBorderItem:
                painter.setPen(QPen(self.borderColorAndWidth['color'],self.borderColorAndWidth['width']))
                painter.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))

            def _pixmap_rect_for_shape(shape):
                scale = getattr(self.legend, "symbolScale", 1.0)
                try:
                    scale = float(scale)
                except Exception:
                    scale = 1.0
                def _s(v):
                    return max(1, int(v * scale))
                if shape == "hexagonal":
                    return QRect(0, 0, _s(30), _s(20))
                if shape in (
                    "circleAgent", "squareAgent", "ellipseAgent1", "ellipseAgent2",
                    "rectAgent1", "rectAgent2", "triangleAgent1", "triangleAgent2",
                    "arrowAgent1", "arrowAgent2"
                ):
                    return QRect(0, 0, _s(20), _s(20))
                if shape in ("circleTile", "ellipseTile"):
                    return QRect(0, 0, _s(18), _s(18))
                return QRect(0, 0, _s(18), _s(18))

            def _draw_pixmap(rect):
                if not is_pixmap:
                    return False
                if self.color is None or self.color.isNull():
                    return True
                pix = self.color.scaled(
                    rect.width(),
                    rect.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                x = rect.x() + int((rect.width() - pix.width()) / 2)
                y = rect.y() + int((rect.height() - pix.height()) / 2)
                painter.drawPixmap(x, y, pix)
                if (self.legend.isControlPanel and self.legend.selected == self and
                    getattr(self.legend, "showSelectionBorder", True)):
                    painter.setPen(QPen(Qt.red, 2))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawRect(rect.x(), rect.y(), rect.width() - 1, rect.height() - 1)
                return True

            # GRADIENT BAR (Phase 3) - Draw before symbols
            if self.is_gradient_bar and self.gradient_colors:
                # Draw gradient bar: 150px wide, 20px tall
                bar_width = 150
                bar_height = 20
                bar_rect = QRect(0, 0, bar_width, bar_height)

                # Create linear gradient
                gradient = QLinearGradient(0, 0, bar_width, 0)
                num_colors = len(self.gradient_colors)
                for i, color in enumerate(self.gradient_colors):
                    position = i / (num_colors - 1) if num_colors > 1 else 0
                    gradient.setColorAt(position, color)

                # Draw gradient bar
                painter.setBrush(gradient)
                painter.setPen(QPen(Qt.black, 1))
                painter.drawRect(bar_rect)

                # Draw min/max labels using full widget width
                font = QFont("Arial", 8)
                painter.setFont(font)
                painter.setPen(QPen(Qt.black, 1))

                min_text = f"{self.gradient_min_value:.0f}" if self.gradient_min_value is not None else "Min"
                max_text = f"{self.gradient_max_value:.0f}" if self.gradient_max_value is not None else "Max"

                # Use full widget width for labels (not just bar width)
                widget_width = self.width()
                labels_rect = QRect(0, bar_height + 2, widget_width, 18)
                painter.drawText(labels_rect, Qt.AlignLeft, min_text)
                painter.drawText(labels_rect, Qt.AlignRight, max_text)

                # Position the gradient bar properly
                painter.end()
                left_pad = getattr(self.legend, 'leftPadding', 10)
                top_pad = getattr(self.legend, 'topPadding', 0)
                self.move(left_pad, top_pad + self.posY * self.legend.heightOfLabels)
                return

            # Draw normal symbol (not a gradient bar)
            scale = getattr(self.legend, "symbolScale", 1.0)
            try:
                scale = float(scale)
            except Exception:
                scale = 1.0

            def _s(v):
                return max(1, int(v * scale))

            symbol_rect = _pixmap_rect_for_shape(self.shape)

            #Square cell
            if(self.shape=="square") :   
                if not _draw_pixmap(symbol_rect):
                    painter.drawRect(0, 0, _s(18), _s(18))
                if self.type == 'delete':
                    # draw a red cross inside
                    pen = QPen(Qt.red, 2)
                    painter.setPen(pen)
                    painter.drawLine(_s(5), _s(5), _s(15), _s(15))
                    painter.drawLine(_s(15), _s(5), _s(5), _s(15))
            #agent
            elif self.shape=="circleAgent":
                if not _draw_pixmap(symbol_rect):
                    painter.drawEllipse(0, 0, _s(20), _s(20))
            elif self.shape=="squareAgent":
                if not _draw_pixmap(symbol_rect):
                    painter.drawRect(0, 0, _s(20), _s(20))
            elif self.shape=="ellipseAgent1":
                if not _draw_pixmap(symbol_rect):
                    painter.drawEllipse(0, _s(5), _s(20), _s(10))
            elif self.shape=="ellipseAgent2":
                if not _draw_pixmap(symbol_rect):
                    painter.drawEllipse(_s(5), 0, _s(10), _s(20))
            elif self.shape=="rectAgent1":
                if not _draw_pixmap(symbol_rect):
                    painter.drawRect(0, _s(5), _s(20), _s(10))
            elif self.shape=="rectAgent2":
                if not _draw_pixmap(symbol_rect):
                    painter.drawRect(_s(5), 0, _s(10), _s(20))
            elif self.shape=="triangleAgent1": 
                points = QPolygon([
                QPoint(_s(10), _s(5)),
                QPoint(_s(5), _s(15)),
                QPoint(_s(15), _s(15))
                ])
                if not _draw_pixmap(symbol_rect):
                    painter.drawPolygon(points)
            elif self.shape=="triangleAgent2": 
                points = QPolygon([           
                QPoint(_s(15), _s(5)),
                QPoint(_s(5), _s(5)),
                QPoint(_s(10), _s(15))
                ])
                if not _draw_pixmap(symbol_rect):
                    painter.drawPolygon(points)
            elif self.shape=="arrowAgent1": 
                points = QPolygon([
                QPoint(_s(20), _s(7)),
                QPoint(_s(15), _s(17)),
                QPoint(_s(20), _s(14)),
                QPoint(_s(25), _s(17))
                ])
                if not _draw_pixmap(symbol_rect):
                    painter.drawPolygon(points)
            elif self.shape=="arrowAgent2": 
                points = QPolygon([           
                QPoint(_s(25), _s(7)),
                QPoint(_s(20), _s(10)),
                QPoint(_s(15), _s(7)),
                QPoint(_s(20), _s(17))
                ])
                if not _draw_pixmap(symbol_rect):
                    painter.drawPolygon(points)
            #Hexagonal square
            elif self.shape=="hexagonal":
                points = QPolygon([
                QPoint(_s(20),  0),
                QPoint(_s(30),  _s(7)),
                QPoint(_s(30),  _s(14)),
                QPoint(_s(20), _s(20)),
                QPoint(_s(10), _s(14)),
                QPoint(_s(10),  _s(7))
                ])
                if not _draw_pixmap(symbol_rect):
                    painter.drawPolygon(points)
            #Tiles
            elif self.shape=="rectTile" or self.shape=="imageTile":
                if not _draw_pixmap(symbol_rect):
                    painter.drawRect(0, 0, _s(18), _s(18))
            elif self.shape=="circleTile":
                if not _draw_pixmap(symbol_rect):
                    painter.drawEllipse(0, 0, _s(18), _s(18))
            elif self.shape=="ellipseTile":
                if not _draw_pixmap(symbol_rect):
                    painter.drawEllipse(0, _s(3), _s(18), _s(9))
            
            # Text styling derived from legend's gs_aspect text aspects
            def apply_font_from_aspect(font: QFont, aspect):
                if getattr(aspect, 'font', None):
                    font.setFamily(aspect.font)
                if getattr(aspect, 'size', None):
                    try:
                        font.setPixelSize(int(aspect.size))
                    except Exception:
                        pass
                try:
                    # delegate to parent helper if available
                    if hasattr(self.legend, 'applyFontWeightToQFont'):
                        self.legend.applyFontWeightToQFont(font, getattr(aspect, 'font_weight', 'normal'))
                except Exception:
                    pass
                s = str(getattr(aspect, 'font_style', 'normal')).lower()
                font.setItalic(s in ('italic', 'oblique'))
                # Decorations
                td = str(getattr(aspect, 'text_decoration', 'none')).lower()
                font.setUnderline(td == 'underline')
                font.setStrikeOut(td in ('line-through', 'strike', 'strike-through'))
                # Note: overline not directly supported on QFont; ignored
                return font

            # Choose color/aspect based on item type (also apply alignment if provided)
            if self.type == "None":
                # Use title2 as a neutral default with underline
                aFont = QFont()
                aFont = apply_font_from_aspect(aFont, getattr(self.legend, 'title2_aspect', type('x', (), {})()))
                aColor = getattr(getattr(self.legend, 'title2_aspect', None), 'color', None)
                if aColor:
                    painter.setPen(QPen(QColor(aColor)))
                base_x = 15
                align = Qt.AlignLeft
                try:
                    al = getattr(self.legend, 'title2_aspect').alignment
                    if isinstance(al, str):
                        a = al.strip().lower()
                        align_map = {
                            'left': Qt.AlignLeft,
                            'right': Qt.AlignRight,
                            'center': Qt.AlignHCenter,
                            'hcenter': Qt.AlignHCenter,
                            'top': Qt.AlignTop,
                            'bottom': Qt.AlignBottom,
                            'vcenter': Qt.AlignVCenter,
                            'justify': Qt.AlignJustify,
                        }
                        if a in align_map:
                            align = align_map[a]
                except Exception:
                    pass
                painter.drawTextAutoSized(base_x, 0, self.text, aFont, align)
                fm = QFontMetrics(aFont)
                text_w = fm.boundingRect(self.text).width()
            elif self.type == "Title1":
                aFont = QFont()
                aFont = apply_font_from_aspect(aFont, getattr(self.legend, 'title1_aspect', type('x', (), {})()))
                aColor = getattr(getattr(self.legend, 'title1_aspect', None), 'color', None)
                if aColor:
                    painter.setPen(QPen(QColor(aColor)))
                base_x = 15
                align = Qt.AlignLeft
                try:
                    al = getattr(self.legend, 'title1_aspect').alignment
                    if isinstance(al, str):
                        a = al.strip().lower()
                        align_map = {
                            'left': Qt.AlignLeft,
                            'right': Qt.AlignRight,
                            'center': Qt.AlignHCenter,
                            'hcenter': Qt.AlignHCenter,
                            'top': Qt.AlignTop,
                            'bottom': Qt.AlignBottom,
                            'vcenter': Qt.AlignVCenter,
                            'justify': Qt.AlignJustify,
                        }
                        if a in align_map:
                            align = align_map[a]
                except Exception:
                    pass
                painter.drawTextAutoSized(base_x, 0, self.text, aFont, align)
                fm = QFontMetrics(aFont)
                text_w = fm.boundingRect(self.text).width()
            elif self.type == "Title2":
                aFont = QFont()
                aFont = apply_font_from_aspect(aFont, getattr(self.legend, 'title2_aspect', type('x', (), {})()))
                aColor = getattr(getattr(self.legend, 'title2_aspect', None), 'color', None)
                if aColor:
                    painter.setPen(QPen(QColor(aColor)))
                base_x = 10
                align = Qt.AlignLeft
                try:
                    al = getattr(self.legend, 'title2_aspect').alignment
                    if isinstance(al, str):
                        a = al.strip().lower()
                        align_map = {
                            'left': Qt.AlignLeft,
                            'right': Qt.AlignRight,
                            'center': Qt.AlignHCenter,
                            'hcenter': Qt.AlignHCenter,
                            'top': Qt.AlignTop,
                            'bottom': Qt.AlignBottom,
                            'vcenter': Qt.AlignVCenter,
                            'justify': Qt.AlignJustify,
                        }
                        if a in align_map:
                            align = align_map[a]
                except Exception:
                    pass
                painter.drawTextAutoSized(base_x, 0, self.text, aFont, align)
                fm = QFontMetrics(aFont)
                text_w = fm.boundingRect(self.text).width()
            elif self.type =='delete':
                aFont = QFont()
                aFont = apply_font_from_aspect(aFont, getattr(self.legend, 'text1_aspect', type('x', (), {})()))
                if self.type == "symbol":
                    base_x = symbol_rect.width() + 10
                else:
                    base_x = 30
                align = Qt.AlignLeft
                try:
                    al = getattr(self.legend, 'text1_aspect').alignment
                    if isinstance(al, str):
                        a = al.strip().lower()
                        align_map = {
                            'left': Qt.AlignLeft,
                            'right': Qt.AlignRight,
                            'center': Qt.AlignHCenter,
                            'hcenter': Qt.AlignHCenter,
                            'top': Qt.AlignTop,
                            'bottom': Qt.AlignBottom,
                            'vcenter': Qt.AlignVCenter,
                            'justify': Qt.AlignJustify,
                        }
                        if a in align_map:
                            align = align_map[a]
                except Exception:
                    pass
                painter.drawTextAutoSized(base_x, 3, self.text, aFont, align)
                fm = QFontMetrics(aFont)
                text_w = fm.boundingRect(self.text).width()
            else :
                font = QFont()
                font = apply_font_from_aspect(font, getattr(self.legend, 'text1_aspect', type('x', (), {})()))
                aColor = getattr(getattr(self.legend, 'text1_aspect', None), 'color', None)
                if aColor:
                    painter.setPen(QPen(QColor(aColor)))
                if self.type == "symbol":
                    base_x = symbol_rect.width() + 10
                else:
                    base_x = 30
                align = Qt.AlignLeft
                try:
                    al = getattr(self.legend, 'text1_aspect').alignment
                    if isinstance(al, str):
                        a = al.strip().lower()
                        align_map = {
                            'left': Qt.AlignLeft,
                            'right': Qt.AlignRight,
                            'center': Qt.AlignHCenter,
                            'hcenter': Qt.AlignHCenter,
                            'top': Qt.AlignTop,
                            'bottom': Qt.AlignBottom,
                            'vcenter': Qt.AlignVCenter,
                            'justify': Qt.AlignJustify,
                        }
                        if a in align_map:
                            align = align_map[a]
                except Exception:
                    pass
                painter.drawTextAutoSized(base_x, 3, self.text, font, align)
                fm = QFontMetrics(font)
                text_w = fm.boundingRect(self.text).width()
            # Compute minimum width from measured text + base_x and a small padding
            # Special sizing for gradient bars (Phase 3)
            if self.is_gradient_bar:
                # Gradient bar is 150px wide + padding for min/max labels
                min_w = 150 + 40  # Bar width + generous labels padding
                # Height: bar (20px) + text below (18px) + top/bottom margins (12px)
                item_height = 20 + 18 + 12
            else:
                try:
                    if self.type == "symbol" and (self.text is None or str(self.text) == ""):
                        base_x = symbol_rect.width() + 2
                        right_pad = 2
                    else:
                        right_pad = 6
                    min_w = int(base_x + max(0, text_w) + right_pad)
                except Exception:
                    min_w = 60
                # Use heightOfLabels for item height to ensure proper clickable area
                item_height = getattr(self.legend, 'heightOfLabels', 22)

            self.setMinimumSize(min_w, item_height)
            self.resize(min_w, item_height)  # Ensure the widget has the correct size
            # Position items using panel paddings
            left_pad = getattr(self.legend, 'leftPadding', 10)
            top_pad = getattr(self.legend, 'topPadding', 0)
            self.move(left_pad, top_pad + self.posY * self.legend.heightOfLabels) #self.legend.heightOfLabels = 25 de base. mais pour CarbonPolis c'est 20
            painter.end()
            
    
    #Funtion to handle the zoom
    def zoomIn(self):
        self.size=self.parent.size
        self.gap=self.parent.gap
        self.update()
    
    def zoomOut(self):
        self.size=self.parent.size
        self.gap=self.parent.gap
        self.update()
        
    def zoomFit(self):
        self.size=self.parent.size
        self.gap=self.parent.gap
        self.update()
        



                    

        
    
        
    