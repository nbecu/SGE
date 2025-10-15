from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGExtensions import *
from math import inf


#Class who is responsible of creation legend item 
class SGLegendItem(QtWidgets.QWidget):
    def __init__(self,parent,type,text,typeOrShape=None,color=Qt.black,nameOfAttribut="",valueOfAttribut="",isBorderItem=False,borderColorAndWidth=None,gameAction=None):
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
            self.color= self.typeDef.defaultShapeColor
        self.remainNumber=int
        self.gameAction= gameAction

    def event(self, e):
        # Intercept tooltip event to show the number of remaining acions for gameActions
        if e.type() == QEvent.ToolTip:
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

    #Drawing function
    def paintEvent(self,event):
        if self.legend.isLegend or (self.legend.isControlPanel and self.legend.checkDisplay()):
            painter = QPainter() 
            painter.begin(self)
            painter.setBrush(QBrush(self.color, Qt.SolidPattern))
            if self.legend.isControlPanel and self.legend.selected == self :
                painter.setPen(QPen(Qt.red,2))
            if self.isBorderItem:
                painter.setPen(QPen(self.borderColorAndWidth['color'],self.borderColorAndWidth['width']))
                painter.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))
            #Square cell
            if(self.shape=="square") :   
                painter.drawRect(0, 0, 18, 18)
                if self.type == 'delete':
                    # draw a red cross inside
                    pen = QPen(Qt.red, 2)
                    painter.setPen(pen)
                    painter.drawLine(5, 5, 15, 15)
                    painter.drawLine(15, 5, 5, 15)
            #agent
            elif self.shape=="circleAgent":
                painter.drawEllipse(0, 0, 20, 20)
            elif self.shape=="squareAgent":
                painter.drawRect(0, 0, 20, 20)
            elif self.shape=="ellipseAgent1":
                painter.drawEllipse(0, 5, 20, 10)
            elif self.shape=="ellipseAgent2":
                painter.drawEllipse(5, 0, 10, 20)
            elif self.shape=="rectAgent1":
                painter.drawRect(0, 5, 20, 10)
            elif self.shape=="rectAgent2":
                painter.drawRect(5, 0, 10, 20)
            elif self.shape=="triangleAgent1": 
                points = QPolygon([
                QPoint(10,5),
                QPoint(5,15),
                QPoint(15,15)
                ])
                painter.drawPolygon(points)
            elif self.shape=="triangleAgent2": 
                points = QPolygon([           
                QPoint(15,5),
                QPoint(5,5),
                QPoint(10,15)
                ])
                painter.drawPolygon(points)
            elif self.shape=="arrowAgent1": 
                points = QPolygon([
                QPoint(20,7),
                QPoint(15,17),
                QPoint(20,14),
                QPoint(25,17)
                ])
                painter.drawPolygon(points)
            elif self.shape=="arrowAgent2": 
                points = QPolygon([           
                QPoint(25,7),
                QPoint(20,10),
                QPoint(15,7),
                QPoint(20,17)
                ])
                painter.drawPolygon(points)
            #Hexagonal square
            elif self.shape=="hexagonal":
                points = QPolygon([
                QPoint(20,  0),
                QPoint(30,  7),
                QPoint(30,  14),
                QPoint(20, 20),
                QPoint(10, 14),
                QPoint(10,  7)
                ])
                painter.drawPolygon(points)
            
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
            try:
                right_pad = 6
                min_w = int(base_x + max(0, text_w) + right_pad)
            except Exception:
                min_w = 60
            self.setMinimumSize(min_w,10)
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
        



                    

        
    
        
    