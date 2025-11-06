from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGAspect import SGAspect


class SGButton(SGGameSpace):
    def __init__(self, parent, method, text, 
                 background_color='white',
                 background_image=None,
                 border_size=1,
                 border_style='solid',
                 border_color='lightgray',
                 border_radius=4,
                 text_color=None,
                 font_family=None,
                 font_size=None,
                 font_weight=None,
                 min_width=None,
                 min_height=None,
                 padding=None,
                 hover_text_color=None,
                 hover_background_color='#c6eff7',
                 hover_border_color='#6bd8ed',
                 pressed_color=None,
                 disabled_color=None,
                 word_wrap=False,
                 fixed_width=None):
        # Initialize as a GameSpace; use provided background_color for container
        super().__init__(parent, 0, 60, 0, 0, true, background_color if background_color is not None else Qt.transparent)
        self.model = parent
        self.moveable = True
        self.isDisplay = True
        # Hover state/colors for container-level rendering
        self._hovered = False
        self._hover_background_color = hover_background_color
        self._hover_border_color = hover_border_color

        # Map legacy parameters to aspects
        self.gs_aspect.background_color = background_color
        if background_image is not None:
            self.setBackgroundImage(background_image)
        self.gs_aspect.border_size = border_size
        self.gs_aspect.border_style = border_style
        self.gs_aspect.border_color = border_color
        self.gs_aspect.border_radius = border_radius
        if min_width is not None:
            self.gs_aspect.min_width = min_width
        if min_height is not None:
            self.gs_aspect.min_height = min_height
        if padding is not None:
            self.gs_aspect.padding = padding
        # Text aspect
        if text_color is not None:
            self.text1_aspect.color = text_color
        if font_family is not None:
            self.text1_aspect.font = font_family
        if font_size is not None:
            self.text1_aspect.size = font_size
        if font_weight is not None:
            self.text1_aspect.font_weight = font_weight

        # Internal QPushButton (content), transparent to avoid container style leakage
        self.button = QtWidgets.QPushButton(text, self)
        from mainClasses.gameAction.SGAbstractAction import SGAbstractAction
        if isinstance(method, SGAbstractAction):
            self.button.clicked.connect(lambda: method.perform_with(method.model))
        else:
            self.button.clicked.connect(lambda: method())
        # Transparent background/border; text style applied via onTextAspectsChanged
        base_style = ["QPushButton { background: transparent; border: none; }"]
        # Hover: only text color on QPushButton; background/border handled by container paintEvent
        if hover_text_color is not None:
            base_style.append(f"QPushButton:hover {{ color: {hover_text_color}; }}")
        if pressed_color is not None:
            base_style.append(f"QPushButton:pressed {{ background-color: {pressed_color} }}")
        if disabled_color is not None:
            base_style.append(f"QPushButton:disabled {{ background-color: {disabled_color} }}")
        self.button.setStyleSheet("\n".join(base_style))

        # Word wrap support: emulate with QLabel if requested
        if word_wrap or fixed_width is not None:
            if word_wrap:
                from PyQt5.QtWidgets import QLabel, QHBoxLayout
                label = QLabel(text)
                label.setWordWrap(True)
                label.setAlignment(Qt.AlignCenter)
                label.setTextInteractionFlags(Qt.NoTextInteraction)
                label.setMouseTracking(False)
                layout_btn = QHBoxLayout(self.button)
                layout_btn.addWidget(label)
                layout_btn.setSpacing(0)
                layout_btn.setContentsMargins(0, 0, 0, 0)
                self.button.setText("")
                self._text_label = label
                # sizing handled below via _recompute_wrapped_size
            if fixed_width is not None:
                self.button.setFixedWidth(fixed_width)
            # Initial sizing for wrapped content
            try:
                wrap_width = None
                if fixed_width is not None:
                    wrap_width = int(fixed_width)
                elif getattr(self.gs_aspect, 'min_width', None):
                    wrap_width = int(self.gs_aspect.min_width)
                self._recompute_wrapped_size(wrap_width)
            except Exception:
                pass

        # Layout
        v = QtWidgets.QVBoxLayout()
        v.setContentsMargins(4, 0, self.rightMargin, self.verticalGapBetweenLabels)
        v.setSpacing(self.verticalGapBetweenLabels)
        v.addWidget(self.button)
        self.setLayout(v)

        # Apply aspects to content and size the widget
        try:
            self.onTextAspectsChanged()
        except Exception:
            pass
        self.updateSizeFromLayout(v)

    # =========================
    # STYLE HOOKS
    # =========================
    def applyContainerAspectStyle(self):
        # Avoid cascading QSS; container rendering is done in paintEvent
        pass

    def onTextAspectsChanged(self):
        """Apply text1_aspect to button text (QPushButton - needs special handling)."""
        from mainClasses.SGExtensions import mapAlignmentStringToQtFlags
        
        # Apply font properties (use helper for basic font, but handle text_decoration specially)
        f = self.button.font()
        self.text1_aspect.applyToQFont(f, self)
        
        # text_decoration: underline/overline/line-through/none (special handling for QPushButton)
        try:
            dec = getattr(self.text1_aspect, 'text_decoration', None)
            # reset all first
            f.setUnderline(False)
            f.setOverline(False)
            f.setStrikeOut(False)
            if isinstance(dec, str) and dec:
                d = dec.strip().lower()
                if d == 'underline':
                    f.setUnderline(True)
                elif d == 'overline':
                    f.setOverline(True)
                elif d in ('line-through', 'linethrough', 'strike', 'strikethrough'):
                    f.setStrikeOut(True)
                else:
                    # 'none' or unsupported like 'blink' => keep all False
                    pass
        except Exception:
            pass
        self.button.setFont(f)
        # If a wrapped QLabel is used, mirror the font (incl. decoration)
        if hasattr(self, '_text_label'):
            try:
                self._text_label.setFont(f)
            except Exception:
                pass

        # Build stylesheet for text color and alignment
        css_parts = ["QPushButton { background: transparent; border: none; }"]
        # Color from aspect
        stylesheet_color = self.text1_aspect.getStyleSheetForColorAndDecoration()
        if stylesheet_color:
            # Extract color part (remove text-decoration)
            color_part = stylesheet_color.split(';')[0] if ';' in stylesheet_color else stylesheet_color
            if 'color:' in color_part:
                css_parts.append(f"QPushButton {{ {color_part}; }}")
        # Alignment
        al = getattr(self.text1_aspect, 'alignment', None)
        if isinstance(al, str) and al:
            a = al.lower()
            if a in ('left', 'right', 'center', 'hcenter'):
                # Map to CSS text-align
                ta = 'center' if a in ('center', 'hcenter') else a
                css_parts.append(f"QPushButton {{ text-align: {ta}; }}")
        # If wrapped QLabel exists, also mirror color/alignment on the label
        if hasattr(self, '_text_label'):
            try:
                # color
                if self.text1_aspect.color:
                    try:
                        css_color = SGAspect()._qt_color_to_css(self.text1_aspect.color)
                    except Exception:
                        css_color = QColor(self.text1_aspect.color).name()
                    if css_color:
                        self._text_label.setStyleSheet(f"QLabel {{ color: {css_color}; background: transparent; }}")
                # alignment
                if isinstance(al, str) and al:
                    qt_alignment = mapAlignmentStringToQtFlags(al)
                    if qt_alignment is not None:
                        self._text_label.setAlignment(qt_alignment)
            except Exception:
                pass
        # Preserve existing hover/pressed/disabled rules (append after base)
        existing_rules = self.button.styleSheet().split('\n') if self.button.styleSheet() else []
        # Re-apply combining base + existing pseudo-state rules
        final_style = []
        # Keep only pseudo-state rules from existing
        for rule in existing_rules:
            if ':hover' in rule or ':pressed' in rule or ':disabled' in rule:
                final_style.append(rule)
        self.button.setStyleSheet("\n".join(css_parts + final_style))

        # Resize from layout
        self.updateSizeFromLayout(self.layout())
        # If wrapped label exists, recompute size to avoid cropping after font change
        if hasattr(self, '_text_label'):
            try:
                wrap_width = None
                if hasattr(self.button, 'width') and self.button.width() > 0:
                    wrap_width = int(self.button.width())
                elif getattr(self.gs_aspect, 'min_width', None):
                    wrap_width = int(self.gs_aspect.min_width)
                self._recompute_wrapped_size(wrap_width)
            except Exception:
                pass

    # =========================
    # RENDERING
    # =========================
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # Background: prefer image, else color (use hover color if hovered)
        bg_pixmap = self.getBackgroundImagePixmap()
        if bg_pixmap is not None:
            rect = QRect(0, 0, self.width(), self.height())
            painter.drawPixmap(rect, bg_pixmap)
        else:
            bg = self.gs_aspect.getBackgroundColorValue()
            if self._hovered and isinstance(self._hover_background_color, str):
                try:
                    bg = SGAspect()._css_to_qcolor(self._hover_background_color)
                except Exception:
                    pass
            if bg.alpha() == 0:
                painter.setBrush(Qt.NoBrush)
            else:
                painter.setBrush(QBrush(bg, Qt.SolidPattern))
        # Border
        pen_color = self.gs_aspect.getBorderColorValue()
        if self._hovered and isinstance(self._hover_border_color, str):
            try:
                pen_color = SGAspect()._css_to_qcolor(self._hover_border_color)
            except Exception:
                pass
        pen = QPen(pen_color, self.gs_aspect.getBorderSize())
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

    # =========================
    # EVENTS
    # =========================
    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    # =========================
    # SIZE GETTERS
    # =========================
    def getSizeXGlobal(self):
        try:
            if hasattr(self, 'sizeXGlobal') and isinstance(self.sizeXGlobal, int):
                return self.sizeXGlobal
        except Exception:
            pass
        try:
            w = self.sizeHint().width()
            return int(w) if w is not None else int(self.width())
        except Exception:
            return int(self.width())

    def getSizeYGlobal(self):
        try:
            if hasattr(self, 'sizeYGlobal') and isinstance(self.sizeYGlobal, int):
                return self.sizeYGlobal
        except Exception:
            pass
        try:
            h = self.sizeHint().height()
            return int(h) if h is not None else int(self.height())
        except Exception:
            return int(self.height())

    # =========================
    # INTERNAL SIZING HELPERS
    # =========================
    def _recompute_wrapped_size(self, wrap_width=None):
        """Recompute size when using word_wrap or fixed/min widths to avoid text cropping.

        Args:
            wrap_width (int|None): Width to wrap text. If None, tries current button width.
        """
        if not hasattr(self, '_text_label'):
            return
        try:
            label = self._text_label
            # Determine wrapping width
            if wrap_width is None or wrap_width <= 0:
                wrap_width = max(1, int(self.button.width()))
            label.setFixedWidth(int(wrap_width))
            # Compute height using font metrics with wrapping
            fm = label.fontMetrics()
            text = label.text()
            # Large height for boundingRect to compute wrapped height
            br = fm.boundingRect(QRect(0, 0, int(wrap_width), 10**6), Qt.TextWordWrap, text)
            content_height = max(label.sizeHint().height(), br.height())
            # Add a small vertical padding so glyphs (descenders) aren't clipped
            extra = 8
            self.button.setFixedWidth(int(wrap_width))
            self.button.setFixedHeight(int(content_height + extra))
            # Now resize the container from layout
            if self.layout():
                self.updateSizeFromLayout(self.layout())
        except Exception:
            pass

