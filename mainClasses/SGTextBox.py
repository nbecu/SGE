from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
from PyQt5.QtWidgets import QMenu, QAction

from mainClasses.SGGameSpace import SGGameSpace


class SGTextBox(SGGameSpace):
    """
    A text display widget for SGE games that can show titles and text content.
    
    SGTextBox provides a flexible text display solution that automatically adapts
    its widget type based on content length:
    - Short texts (≤100 chars): Uses QLabel for compact display
    - Long texts (>100 chars): Uses QTextEdit for better text handling
    
    Features:
    - Dynamic sizing based on content using SGGameSpaceSizeManager
    - Automatic layout management with QVBoxLayout
    - Context menu support (Inspect, Close)
    - Text history tracking
    - Customizable styling through gs_aspect system
    
    Args:
        parent: The parent widget/model
        textToWrite (str): Initial text content to display
        title (str): Title displayed above the text content
        sizeX (int, optional): Manual width override
        sizeY (int, optional): Manual height override  
        borderColor (QColor): Border color (default: Qt.black)
        backgroundColor (QColor): Background color (default: Qt.lightGray)
    """
    def __init__(self, parent, textToWrite, title, sizeX=None, sizeY=None, borderColor=Qt.black, backgroundColor=Qt.lightGray, titleAlignment='left'):
        super().__init__(parent, 0, 60, 0, 0, true, backgroundColor)
        self._resize_in_progress = False  # Flag to prevent infinite loops in resize
        self.title = title
        self.id = title
        self.model = parent
        # Configure border using gs_aspect instead of self.borderColor
        self.gs_aspect.border_color = borderColor
        self.gs_aspect.border_size = 1
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.min_height_for_long_text = 150  # Minimum height for text longer than 100 characters
        self.titleAlignment = titleAlignment
        self.y1 = 0
        self.labels = 0
        self.moveable = True
        self.haveToBeClose = False
        self.isDisplay = True
        self.history = []
        self.textToWrite = textToWrite
        self.new_text = None
        self.theLayout = None
        self.initUI()

    def initUI(self):
        # Create a title
        self.labelTitle = QtWidgets.QLabel(self.title)
        # font and styles will be applied from title1_aspect in onTextAspectsChanged()
        
        # Set title alignment
        if self.titleAlignment == 'center':
            self.labelTitle.setAlignment(Qt.AlignCenter)
        elif self.titleAlignment == 'right':
            self.labelTitle.setAlignment(Qt.AlignRight)
        else:  # default to 'left'
            self.labelTitle.setAlignment(Qt.AlignLeft)

        # Create appropriate widget based on text length
        if len(self.textToWrite) > 100:  # Use QTextEdit for long texts
            self.textWidget = QtWidgets.QTextEdit()
            self.textWidget.setPlainText(self.textToWrite)
            self.textWidget.setReadOnly(True)
            # Force word-wrap behavior at widget width
            try:
                self.textWidget.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
                self.textWidget.setWordWrapMode(QTextOption.WordWrap)
                self.textWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                self.textWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            except Exception:
                pass
        else:  # Use QLabel for short texts
            self.textWidget = QtWidgets.QLabel(self.textToWrite)
            self.textWidget.setWordWrap(True)
        
        # Remove hard-coded backgrounds to let container paintEvent manage it
        if len(self.textToWrite) > 100:  # QTextEdit: keep border none; bg transparent handled by container
            self.textWidget.setStyleSheet("QTextEdit { border: none; background: transparent; }")
        else:
            self.textWidget.setStyleSheet("border: none;")
        
        # Store reference for compatibility
        self.textEdit = self.textWidget

        # Create a QVBoxLayout to hold the QTextEdit and QPushButton
        self.textLayout = QtWidgets.QVBoxLayout()
        try:
            # Revenir à une marge basse légère (+2)
            self.textLayout.setContentsMargins(4, 2, self.rightMargin, self.verticalGapBetweenLabels + 2)
            self.textLayout.setSpacing(self.verticalGapBetweenLabels)
        except Exception:
            pass
        self.textLayout.addWidget(self.labelTitle)
        self.textLayout.addWidget(self.textEdit)

        # Set the QVBoxLayout as the main layout for the widget
        self.setLayout(self.textLayout)
        
        # Adjust size after layout configuration
        self.onTextAspectsChanged()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_contextMenu)
        # Store text content for history
        if hasattr(self.textEdit, 'toPlainText'):
            self.history.append(self.textEdit.toPlainText())
        else:
            self.history.append(self.textEdit.text())

    # Function to have the global size of a gameSpace

    def getSizeXGlobal(self):
        # Use manual size if specified
        if self.sizeX is not None:
            return self.sizeX
            
        # First, check if title width requires more space (important for cases 2 and 6 with long titles)
        # This must be done BEFORE layout calculation to ensure title is not cropped
        title_based_width = None
        if hasattr(self, 'labelTitle') and self.labelTitle:
            try:
                # Get title preferred width
                self.labelTitle.adjustSize()
                title_width = self.labelTitle.sizeHint().width()
                if title_width > 0:
                    # Add layout margins, right margin, and border padding
                    m = self.textLayout.contentsMargins() if hasattr(self, 'textLayout') and self.textLayout else None
                    lm_left = m.left() if m else 4
                    lm_right = m.right() if m else 9
                    right_margin = getattr(self.size_manager, 'right_margin', 9)
                    border_padding = getattr(self.size_manager, 'border_padding', 3)
                    title_based_width = title_width + lm_left + lm_right + right_margin + border_padding
            except Exception:
                pass
        
        # Use actual layout size if available
        layout_based_width = None
        if hasattr(self, 'textLayout') and self.textLayout:
            # Force layout to calculate its size
            self.textLayout.activate()
            size_hint = self.textLayout.sizeHint()
            if size_hint and size_hint.isValid() and size_hint.width() > 0:
                # Add right margin and border padding to ensure border is not cropped
                right_margin = getattr(self.size_manager, 'right_margin', 9)
                border_padding = getattr(self.size_manager, 'border_padding', 3)
                layout_based_width = max(size_hint.width() + right_margin + border_padding, self.size_manager.min_width)
                # Sanity check: if width is absurdly large (> 5000px), something went wrong
                if layout_based_width >= 5000:
                    layout_based_width = None
        
        # Use the larger of title-based or layout-based width to ensure nothing is cropped
        if title_based_width is not None and layout_based_width is not None:
            return max(title_based_width, layout_based_width)
        elif title_based_width is not None:
            return title_based_width
        elif layout_based_width is not None:
            return layout_based_width
        
        # For QTextEdit, don't use calculateContentWidth() as it calculates unwrapped width
        # Instead, use widget width if available, or a reasonable default
        if hasattr(self, 'textEdit') and isinstance(self.textEdit, QtWidgets.QTextEdit):
            # If widget has a valid width, use it
            if self.width() > 0 and self.width() < 5000:
                # Add border padding to ensure border is not cropped
                border_padding = getattr(self.size_manager, 'border_padding', 3)
                return self.width() + border_padding
            # Otherwise, use cached sizeXGlobal if it's reasonable
            if hasattr(self, 'sizeXGlobal') and isinstance(self.sizeXGlobal, int) and 0 < self.sizeXGlobal < 5000:
                return self.sizeXGlobal
            # Default reasonable width for text boxes (can be overridden by layout)
            border_padding = getattr(self.size_manager, 'border_padding', 3)
            return 280 + border_padding  # Reasonable default for text boxes
        
        # For QLabel, fallback to size_manager calculation
        if hasattr(self, 'textWidget') and isinstance(self.textWidget, QtWidgets.QLabel):
            if hasattr(self.textWidget, 'text'):
                text_content = self.textWidget.text()
            calculated_width = self.calculateContentWidth(text_content=text_content)
            # Add border padding to ensure border is not cropped
            border_padding = getattr(self.size_manager, 'border_padding', 3)
            return calculated_width + border_padding
        
        # Fallback: minimum width with border padding
        border_padding = getattr(self.size_manager, 'border_padding', 3)
        return self.size_manager.min_width + border_padding

    def getSizeYGlobal(self):
        # Use manual size if specified
        if self.sizeY is not None:
            return self.sizeY
        # Prefer layout-computed global size when available
        if hasattr(self, 'sizeYGlobal') and getattr(self, 'sizeYGlobal', None):
            try:
                return int(self.sizeYGlobal)
            except Exception:
                pass
        
        # Calculate height based on content
        if hasattr(self, 'textEdit') and self.textEdit:
            if hasattr(self.textEdit, 'toPlainText'):
                text_content = self.textEdit.toPlainText()
            else:
                text_content = self.textEdit.text()
            
            # Get the actual font from the text widget for accurate height calculation
            text_font = self.textEdit.font() if hasattr(self.textEdit, 'font') else None
            
            # For QTextEdit with long text, use QTextDocument to calculate wrapped height
            if isinstance(self.textEdit, QtWidgets.QTextEdit) and len(text_content) > 100:
                try:
                    # Calculate available width for wrapping
                    m = self.textLayout.contentsMargins() if hasattr(self, 'textLayout') and self.textLayout else None
                    lm_left = m.left() if m else 4
                    lm_right = m.right() if m else 9
                    right_margin = getattr(self.size_manager, 'right_margin', 9)
                    left_margin = 4
                    border_padding = getattr(self.size_manager, 'border_padding', 3)
                    
                    # Use actual width if widget is already sized, otherwise estimate from getSizeXGlobal
                    if self.width() > 0:
                        avail_w = max(120, self.width() - (lm_left + lm_right + left_margin + border_padding))
                    else:
                        # Estimate width from content or use default
                        estimated_width = self.getSizeXGlobal() if hasattr(self, 'getSizeXGlobal') else 250
                        avail_w = max(120, estimated_width - (lm_left + lm_right + right_margin + left_margin + border_padding))
                    
                    # Use QTextDocument to calculate real wrapped height
                    doc = self.textEdit.document()
                    if doc:
                        # Set document width to enable wrapping calculation
                        doc.setTextWidth(float(avail_w))
                        doc.adjustSize()
                        doc_height = doc.size().height()
                        
                        # Add frame width and margins for QTextEdit
                        frame_w = self.textEdit.frameWidth() if hasattr(self.textEdit, 'frameWidth') else 0
                        margins = self.textEdit.contentsMargins() if hasattr(self.textEdit, 'contentsMargins') else QMargins(0, 0, 0, 0)
                        text_h = int(doc_height + 2 * frame_w + margins.top() + margins.bottom() + 4)  # Small safety margin
                        
                        calculated_height = text_h
                    else:
                        # Fallback to simple calculation if document not available
                        calculated_height = self.calculateContentHeight(text_content=text_content, font=text_font)
                except Exception:
                    # Fallback to simple calculation
                    calculated_height = self.calculateContentHeight(text_content=text_content, font=text_font)
            else:
                # For QLabel or short text, calculate height with word-wrap consideration
                if isinstance(self.textEdit, QtWidgets.QLabel):
                    # QLabel with word-wrap: calculate height using QFontMetrics.boundingRect
                    try:
                        if text_font is None:
                            text_font = self.textEdit.font()
                        
                        # Get available width for wrapping
                        m = self.textLayout.contentsMargins() if hasattr(self, 'textLayout') and self.textLayout else None
                        lm_left = m.left() if m else 4
                        lm_right = m.right() if m else 9
                        right_margin = getattr(self.size_manager, 'right_margin', 9)
                        border_padding = getattr(self.size_manager, 'border_padding', 3)
                        
                        # Use actual width if available, otherwise estimate
                        if self.width() > 0:
                            available_width = max(120, self.width() - (lm_left + lm_right + border_padding))
                        else:
                            estimated_width = self.getSizeXGlobal() if hasattr(self, 'getSizeXGlobal') else 250
                            available_width = max(120, estimated_width - (lm_left + lm_right + right_margin + border_padding))
                        
                        # Calculate wrapped height using QFontMetrics
                        metrics = QFontMetrics(text_font)
                        wrapped_rect = metrics.boundingRect(
                            QRect(0, 0, int(available_width), 10**6),  # Large height for wrapping
                            Qt.TextWordWrap,
                            text_content
                        )
                        calculated_height = wrapped_rect.height()
                    except Exception:
                        # Fallback to standard calculation
                        calculated_height = self.calculateContentHeight(text_content=text_content, font=text_font)
                else:
                    # For other widget types, use standard calculation
                    calculated_height = self.calculateContentHeight(text_content=text_content, font=text_font)
            
            # Add height for title if it exists
            if hasattr(self, 'labelTitle') and self.labelTitle:
                title_font = self.labelTitle.font()
                # Use QFontMetrics for accurate title height calculation
                title_metrics = QFontMetrics(title_font)
                title_height = title_metrics.height() + self.size_manager.vertical_gap_between_labels
                calculated_height += title_height
            
            # Add layout margins and spacing
            if hasattr(self, 'textLayout') and self.textLayout:
                try:
                    m = self.textLayout.contentsMargins()
                    calculated_height += m.top() + m.bottom()
                    calculated_height += self.textLayout.spacing() if hasattr(self.textLayout, 'spacing') else 0
                except Exception:
                    pass
            
            # Add border padding and safety margin to ensure border is not cropped and text doesn't overflow
            border_padding = getattr(self.size_manager, 'border_padding', 3)
            safety_margin = 6  # Extra pixels to prevent text overflow at bottom
            calculated_height += border_padding + safety_margin
            
            # Use higher minimum height for long text
            min_height = self.min_height_for_long_text if len(text_content) > 100 else self.size_manager.min_height
            
            res = max(calculated_height, min_height)
            return res
        
        return self.size_manager.min_height

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # Background: prefer image, else color with transparency support
        bg_pixmap = self.getBackgroundImagePixmap()
        if bg_pixmap is not None:
            rect = QRect(0, 0, self.width(), self.height())
            painter.drawPixmap(rect, bg_pixmap)
        else:
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

        # Use calculated global sizes to ensure border is fully visible
        width = max(0, self.getSizeXGlobal() - 1)
        height = max(0, self.getSizeYGlobal() - 1)
        radius = getattr(self.gs_aspect, 'border_radius', None) or 0
        if radius > 0:
            painter.drawRoundedRect(0, 0, width, height, radius, radius)
        else:
            painter.drawRect(0, 0, width, height)
    
    def resize(self, w, h):
        """
        Override resize to force layout recalculation after resize for QTextEdit widgets.
        This ensures that word-wrap is recalculated with the correct width.
        """
        # Call parent resize
        super().resize(w, h)
        
        # Only recalculate if not already in progress (prevent infinite loops)
        if self._resize_in_progress:
            return
        
        # Force recalculation for QTextEdit after resize
        if hasattr(self, 'textEdit') and isinstance(self.textEdit, QtWidgets.QTextEdit):
            try:
                self._resize_in_progress = True
                
                # Force layout update with new dimensions
                if hasattr(self, 'textLayout') and self.textLayout:
                    # Update QTextEdit document width based on new available width
                    m = self.textLayout.contentsMargins() if hasattr(self.textLayout, 'contentsMargins') else None
                    lm_left = m.left() if m else 4
                    lm_right = m.right() if m else 9
                    left_margin = 4
                    border_padding = getattr(self.size_manager, 'border_padding', 3)
                    
                    avail_w = max(120, w - (lm_left + lm_right + left_margin + border_padding))
                    
                    # Update document width for proper wrapping
                    doc = self.textEdit.document()
                    if doc:
                        doc.setTextWidth(float(avail_w))
                        doc.adjustSize()
                        
                        # Recalculate height
                        doc_height = doc.size().height()
                        frame_w = self.textEdit.frameWidth() if hasattr(self.textEdit, 'frameWidth') else 0
                        margins = self.textEdit.contentsMargins() if hasattr(self.textEdit, 'contentsMargins') else QMargins(0, 0, 0, 0)
                        text_h = int(doc_height + 2 * frame_w + margins.top() + margins.bottom() + 4)
                        
                        # Update minimum size
                        self.textEdit.setMinimumWidth(avail_w)
                        self.textEdit.setMinimumHeight(text_h)
                    
                    # Force layout to recalculate
                    self.textLayout.activate()
                    self.updateGeometry()
                    
            except Exception:
                pass
            finally:
                self._resize_in_progress = False
    
    def adjustSizeAfterLayout(self):
        """
        Adjust widget size after layout configuration.
        """
        if hasattr(self, 'textLayout') and self.textLayout:
            self.updateSizeFromLayout(self.textLayout)

    # contextual menu (opened on a right click)
    def show_contextMenu(self, point):
        menu = QMenu(self)

        option1 = QAction("Inspect", self)
        option1.triggered.connect(lambda: print(
            "One day this will inspected something"))
        menu.addAction(option1)

        option2 = QAction("Close", self)
        option2.triggered.connect(self.close)
        menu.addAction(option2)

        if self.rect().contains(point):
            menu.exec_(self.mapToGlobal(point))

    def addText(self, text, toTheLine=False):
        """
        Add text in a text box.

        args:
            - text (str) : displayed text
            - toTheLine (bool) : if true, skip a line before adding
        """
        self.textForHistory = text
        if toTheLine == True:
            self.new_text = "\n\n"+text
        else:
            self.new_text = text
        self.updateText()

    def updateText(self):
        # Update the text widget content
        if hasattr(self.textEdit, 'toPlainText'):
            newText = self.textEdit.toPlainText() + self.new_text
            self.textEdit.setPlainText(newText)
        else:
            newText = self.textEdit.text() + self.new_text
            self.textEdit.setText(newText)
        # Automatically adjust size to new content
        text_font = self.textEdit.font() if hasattr(self.textEdit, 'font') else None
        self.adjustSizeToContent(text_content=newText, font=text_font)
        #self.history.append(self.textForHistory)

    def setNewText(self, text):
        """
        Replace the text by a new text.

        args :
            - text (str) : new text
        """
        self.new_text = text
        if hasattr(self.textEdit, 'setPlainText'):
            self.textEdit.setPlainText(text)
        else:
            self.textEdit.setText(text)
        # Automatically adjust size to new content
        text_font = self.textEdit.font() if hasattr(self.textEdit, 'font') else None
        self.adjustSizeToContent(text_content=text, font=text_font)

    def setTitle(self, title):
        """
        Replace the title by a new title.

        args:
            -title (str) : new title
        """
        self.title = title

    def setSize(self, x, y):
        self.sizeX = x
        self.sizeY = y

    def setTextFormat(self, fontName='Verdana', size=12):
        """
        Customize the font and the size of the text

        args :
            - fontName (str) : desired font
            - size (int) : desired size of the text
        """
        font = QFont(fontName, size)
        self.textEdit.setFont(font)
        
        # Force layout to recalculate its size with new font
        if hasattr(self, 'textLayout') and self.textLayout:
            self.textLayout.activate()
            # Force widgets to update their size hints
            self.textEdit.updateGeometry()
            self.labelTitle.updateGeometry()
        
        # Recalculate height after font change
        if hasattr(self.textEdit, 'toPlainText'):
            text_content = self.textEdit.toPlainText()
        else:
            text_content = self.textEdit.text()
        
        # Adjust size to new font
        self.adjustSizeToContent(text_content=text_content, font=font)
        
        # Force repaint to update visual appearance
        self.update()

    def setTitleColor(self, color='red'):
        """
        Set the color

        args:
            - color (str) : desired color
        """
        self.labelTitle.setStyleSheet("color: "+color+';')

    def setTitleSize(self, size="20px"):
        """Set the size
        
        args:
            - size (int) : desired size
        """
        self.labelTitle.setStyleSheet("color: "+size+';')

    def deleteTitle(self):
        del self.labelTitle

    def deleteText(self):
        del self.textEdit

    # =========================
    # STYLE/APPLY HOOKS
    # =========================
    def applyContainerAspectStyle(self):
        """Avoid QSS cascade; rely on paintEvent for container rendering."""
        pass

    def onTextAspectsChanged(self):
        """Apply title1_aspect to title and text1_aspect to content, then resize."""
        # Map alignment helper
        def _map_alignment(al):
            if not isinstance(al, str):
                return None
            a = al.lower()
            if a == 'left':
                return Qt.AlignLeft | Qt.AlignVCenter
            if a == 'right':
                return Qt.AlignRight | Qt.AlignVCenter
            if a in ('center', 'hcenter'):
                return Qt.AlignHCenter | Qt.AlignVCenter
            if a == 'top':
                return Qt.AlignTop | Qt.AlignHCenter
            if a == 'bottom':
                return Qt.AlignBottom | Qt.AlignHCenter
            if a == 'vcenter':
                return Qt.AlignVCenter | Qt.AlignHCenter
            if a == 'justify':
                return Qt.AlignJustify
            return None

        # Font weight helper (supports 'bold', 'normal', 'bolder', 'lighter', and numeric strings)
        def _apply_weight_to_font(font_obj: QFont, weight_value):
            # Delegate to SGGameSpace helper
            try:
                self.applyFontWeightToQFont(font_obj, weight_value)
            except Exception:
                pass

        # Title label
        if hasattr(self, 'labelTitle') and self.labelTitle is not None:
            f = self.labelTitle.font()
            if self.title1_aspect.font:
                f.setFamily(self.title1_aspect.font)
            if self.title1_aspect.size:
                try:
                    f.setPixelSize(int(self.title1_aspect.size))
                except Exception:
                    pass
            _apply_weight_to_font(f, getattr(self.title1_aspect, 'font_weight', None))
            if self.title1_aspect.font_style:
                s = str(self.title1_aspect.font_style).lower()
                f.setItalic(s in ('italic', 'oblique'))
            self.labelTitle.setFont(f)
            # alignment
            al = _map_alignment(getattr(self.title1_aspect, 'alignment', None))
            if al is not None:
                self.labelTitle.setAlignment(al)
            # color/decoration
            css_parts = []
            if self.title1_aspect.color:
                css_parts.append(f"color: {QColor(self.title1_aspect.color).name()}")
            td = getattr(self.title1_aspect, 'text_decoration', None)
            css_parts.append(f"text-decoration: {td}" if td and str(td).lower() != 'none' else "text-decoration: none")
            self.labelTitle.setStyleSheet("; ".join(css_parts))

        # Text content
        target = self.textWidget
        if target is not None:
            if isinstance(target, QtWidgets.QLabel):
                f = target.font()
                if self.text1_aspect.font:
                    f.setFamily(self.text1_aspect.font)
                if self.text1_aspect.size:
                    try:
                        f.setPixelSize(int(self.text1_aspect.size))
                    except Exception:
                        pass
                _apply_weight_to_font(f, getattr(self.text1_aspect, 'font_weight', None))
                if self.text1_aspect.font_style:
                    s = str(self.text1_aspect.font_style).lower()
                    f.setItalic(s in ('italic', 'oblique'))
                target.setFont(f)
                al = _map_alignment(getattr(self.text1_aspect, 'alignment', None))
                if al is not None:
                    target.setAlignment(al)
                css_parts = []
                if self.text1_aspect.color:
                    css_parts.append(f"color: {QColor(self.text1_aspect.color).name()}")
                td = getattr(self.text1_aspect, 'text_decoration', None)
                css_parts.append(f"text-decoration: {td}" if td and str(td).lower() != 'none' else "text-decoration: none")
                target.setStyleSheet("; ".join(css_parts))
            else:
                # QTextEdit: apply font and color via stylesheet/palette, background transparent
                f = target.font()
                if self.text1_aspect.font:
                    f.setFamily(self.text1_aspect.font)
                if self.text1_aspect.size:
                    try:
                        f.setPixelSize(int(self.text1_aspect.size))
                    except Exception:
                        pass
                _apply_weight_to_font(f, getattr(self.text1_aspect, 'font_weight', None))
                if self.text1_aspect.font_style:
                    s = str(self.text1_aspect.font_style).lower()
                    f.setItalic(s in ('italic', 'oblique'))
                target.setFont(f)
                color_css = QColor(self.text1_aspect.color).name() if self.text1_aspect.color else None
                if color_css:
                    target.setStyleSheet(f"QTextEdit {{ border: none; background: transparent; color: {color_css}; }}")
                else:
                    target.setStyleSheet("QTextEdit { border: none; background: transparent; }")
                # Ensure wrapping is enforced on runtime changes
                try:
                    target.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
                    target.setWordWrapMode(QTextOption.WordWrap)
                    target.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                except Exception:
                    pass

        # Resize: QLabel -> metrics-based with word-wrap; QTextEdit -> layout-based
        target = getattr(self, 'textWidget', None)
        if isinstance(target, QtWidgets.QLabel) and hasattr(self, 'labelTitle'):
            try:
                # For QLabel with word-wrap, we need to calculate dimensions manually
                # First, ensure widgets have correct sizes
                self.labelTitle.adjustSize()
                target.adjustSize()
                
                # Calculate width: max of title width and text width (considering word-wrap)
                title_width = self.labelTitle.sizeHint().width()
                
                # Get layout margins
                m = self.textLayout.contentsMargins() if hasattr(self, 'textLayout') and self.textLayout else None
                lm_left = m.left() if m else 4
                lm_right = m.right() if m else 9
                right_margin = getattr(self.size_manager, 'right_margin', 9)
                border_padding = getattr(self.size_manager, 'border_padding', 3)
                
                # Calculate text width needed (for word-wrap, we use a reasonable width)
                # But we must ensure title fits - use title width as base if it's longer
                estimated_text_width = 240  # Reasonable default for text
                # If title is longer, use it as the base width (important for cases 2 and 6)
                # Add a small margin to ensure title doesn't get cropped
                title_margin = 5  # Extra pixels to prevent title cropping
                if title_width > estimated_text_width:
                    content_width = title_width + title_margin
                else:
                    content_width = estimated_text_width
                
                # Set text label width to enable word-wrap calculation
                target.setFixedWidth(content_width)
                target.updateGeometry()
                
                # Calculate height using QFontMetrics with word-wrap
                text_font = target.font()
                metrics = QFontMetrics(text_font)
                text_content = target.text()
                wrapped_rect = metrics.boundingRect(
                    QRect(0, 0, content_width, 10**6),
                    Qt.TextWordWrap,
                    text_content
                )
                text_height = wrapped_rect.height()
                
                # Title height
                title_font = self.labelTitle.font()
                title_metrics = QFontMetrics(title_font)
                title_height = title_metrics.height()
                
                # Total dimensions
                total_width = content_width + lm_left + lm_right + right_margin + border_padding
                vertical_gap = getattr(self.size_manager, 'vertical_gap_between_labels', 5)
                # Add extra safety margin for text wrapping and border visibility
                safety_margin = 6  # Extra pixels to prevent text overflow and border cropping
                total_height = title_height + vertical_gap + text_height + m.top() + m.bottom() + border_padding + safety_margin
                
                # Update cached sizes
                self.sizeXGlobal = total_width
                self.sizeYGlobal = total_height
                
                # Apply sizes
                self.setMinimumSize(total_width, total_height)
                self.resize(total_width, total_height)
            except Exception:
                # Fallback au layout si nécessaire
                if hasattr(self, 'textLayout') and self.textLayout:
                    self.updateSizeFromLayout(self.textLayout)
        elif hasattr(self, 'textLayout') and self.textLayout:
            # S'assurer que les hints sont à jour avant le calcul layout
            try:
                if hasattr(self, 'labelTitle') and self.labelTitle is not None:
                    self.labelTitle.adjustSize()
                if isinstance(target, QtWidgets.QLabel):
                    target.adjustSize()
            except Exception:
                pass
            self.updateSizeFromLayout(self.textLayout)
            # Après calcul du layout, forcer le word-wrap des QTextEdit à la largeur disponible
            try:
                if isinstance(target, QtWidgets.QTextEdit):
                    # Largeur disponible = largeur cadre - marges/gaps internes
                    m = self.textLayout.contentsMargins() if hasattr(self.textLayout, 'contentsMargins') else None
                    lm_left = m.left() if m else 4
                    lm_right = m.right() if m else 9
                    right_margin = getattr(self.size_manager, 'right_margin', 9)
                    left_margin = 4
                    border_padding = getattr(self.size_manager, 'border_padding', 3)
                    
                    # Calculate available width for wrapping
                    if self.width() > 0 and self.width() < 5000:
                        avail_w = max(120, self.width() - (lm_left + lm_right + left_margin + border_padding))
                    else:
                        # Use a reasonable default instead of calling getSizeXGlobal() recursively
                        # which might return an enormous value from calculateContentWidth()
                        estimated_width = 280  # Reasonable default for text boxes
                        avail_w = max(120, estimated_width - (lm_left + lm_right + right_margin + left_margin + border_padding))
                    
                    # Configure wrapping
                    target.setWordWrapMode(QTextOption.WordWrap)
                    target.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
                    target.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                    target.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                    
                    # Update document width for proper wrapping calculation
                    doc = target.document()
                    if doc:
                        doc.setTextWidth(float(avail_w))
                        doc.adjustSize()
                        # Calculate text height from wrapped document
                        doc_height = doc.size().height()
                        frame_w = target.frameWidth() if hasattr(target, 'frameWidth') else 0
                        margins = target.contentsMargins() if hasattr(target, 'contentsMargins') else QMargins(0, 0, 0, 0)
                        text_h = int(doc_height + 2 * frame_w + margins.top() + margins.bottom() + 4)
                        
                        # Set size policy to allow vertical expansion
                        target.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
                        # Set minimum size to ensure proper layout calculation
                        target.setMinimumWidth(avail_w)
                        target.setMinimumHeight(text_h)
                    
                    # Force layout to recalculate with new text widget sizes
                    self.textLayout.activate()
                    # Get the layout's size hint after all widgets are properly sized
                    layout_size = self.textLayout.sizeHint()
                    if layout_size and layout_size.isValid():
                        # Calculate final widget size including margins
                        right_margin = getattr(self.size_manager, 'right_margin', 9)
                        border_padding = getattr(self.size_manager, 'border_padding', 3)
                        vertical_gap = getattr(self.size_manager, 'vertical_gap_between_labels', 5)
                        
                        # Calculate final dimensions with all margins and padding
                        # Width: layout width + right margin + border padding
                        # Add safety margin for title width (important for cases 2 and 6)
                        safety_margin_width = 5  # Extra pixels to prevent title cropping
                        final_width = layout_size.width() + right_margin + border_padding + safety_margin_width
                        # Height: layout height + vertical gap + border padding (to prevent bottom cropping)
                        # Add safety margin to prevent text overflow
                        safety_margin_height = 6  # Extra pixels to prevent text overflow
                        final_height = layout_size.height() + vertical_gap + border_padding + safety_margin_height
                        
                        # Sanity check: ensure reasonable values
                        if final_width > 5000:
                            final_width = 280  # Fallback to reasonable default
                        if final_height < 50:
                            # Recalculate height using getSizeYGlobal if layout height seems too small
                            calculated_height = self.getSizeYGlobal()
                            if calculated_height > final_height:
                                final_height = calculated_height
                        
                        # Update cached sizes
                        self.sizeXGlobal = final_width
                        self.sizeYGlobal = final_height
                        
                        # Apply the calculated size
                        self.setMinimumSize(final_width, final_height)
                        self.resize(final_width, final_height)
                    else:
                        # Fallback: use getSizeYGlobal() if layout size hint is invalid
                        final_height = self.getSizeYGlobal()
                        final_width = max(280, self.width() if self.width() < 5000 else 280)
                        self.sizeXGlobal = final_width
                        self.sizeYGlobal = final_height
                        self.setMinimumSize(final_width, final_height)
                        self.resize(final_width, final_height)
            except Exception:
                pass
        self.update()

    # ============================================================================
    # MODELER METHODS
    # ============================================================================
    
    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================
    
    def setBorderColor(self, color):
        """
        Set the border color of the text box.
        
        Args:
            color (QColor or Qt.GlobalColor): The border color
        """
        self.gs_aspect.border_color = color
        
    def setBorderSize(self, size):
        """
        Set the border size of the text box.
        
        Args:
            size (int): The border size in pixels
        """
        self.gs_aspect.border_size = size
