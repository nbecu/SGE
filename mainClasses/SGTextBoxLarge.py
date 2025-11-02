from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
from PyQt5.QtWidgets import QMenu, QAction
from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGAspect import SGAspect


class SGTextBoxLarge(SGGameSpace):
    """
    A text display widget optimized for long texts with scrollable content.
    
    SGTextBoxLarge provides a simpler and more reliable implementation for displaying
    long texts with the following features:
    - Default width and height (400x300 pixels)
    - Automatic width adjustment if title is wider than default width
    - Automatic word-wrapping for text content
    - Vertical scrolling when text exceeds height (via mouse wheel and scrollbar)
    - User-configurable width and height
    
    Args:
        parent: The parent widget/model
        textToWrite (str): Initial text content to display
        title (str): Title displayed above the text content
            width (int, optional): Custom width in pixels (default: 250)
            height (int, optional): Custom height in pixels (default: 150)
        borderColor (QColor): Border color (default: Qt.black)
        backgroundColor (QColor): Background color (default: Qt.lightGray)
        titleAlignment (str): Title alignment - 'left', 'center', or 'right' (default: 'left')
    """
    
    def __init__(self, parent, textToWrite, title, width=None, height=None, 
                 borderColor=Qt.black, backgroundColor=Qt.lightGray, titleAlignment='left'):
        super().__init__(parent, 0, 60, 0, 0, true, backgroundColor)
        
        self.title = title
        self.id = title
        self.model = parent
        self.textToWrite = textToWrite
        
        # Configure border using gs_aspect
        self.gs_aspect.border_color = borderColor
        self.gs_aspect.border_size = 1
        
        # Default dimensions
        self.default_width = 250
        self.default_height = 150
        
        # User-specified dimensions (if None, use defaults)
        self.custom_width = width
        self.custom_height = height
        
        self.titleAlignment = titleAlignment
        
        # Initialize history for text tracking (compatibility with SGModel.getTextBoxHistory)
        self.history = []
        if textToWrite:
            self.history.append(textToWrite)
        
        # Initialize UI
        self.initUI()
        
        # Apply title alignment using setter from SGGameSpace
        if titleAlignment:
            self.setTitleAlignment(titleAlignment)
        
        # Apply text aspects styling (this will call updateSize() at the end)
        self.onTextAspectsChanged()
        
        # Recalculate size after styles are applied to ensure title width is accurate
        # This is important because font changes can affect title width
        self.updateSize()
        
        # Set context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_contextMenu)
    
    def initUI(self):
        """Initialize the UI components: title label and text edit widget."""
        # Create title label
        self.labelTitle = QtWidgets.QLabel(self.title)
        self.labelTitle.setWordWrap(False)  # Title on single line
        
        # Set title alignment
        if self.titleAlignment == 'center':
            self.labelTitle.setAlignment(Qt.AlignCenter)
        elif self.titleAlignment == 'right':
            self.labelTitle.setAlignment(Qt.AlignRight)
        else:  # default to 'left'
            self.labelTitle.setAlignment(Qt.AlignLeft)
        
        # Create text widget (always QTextEdit for long texts)
        self.textWidget = QtWidgets.QTextEdit()
        self.textWidget.setPlainText(self.textToWrite)
        self.textWidget.setReadOnly(True)
        
        # Configure word-wrap and scrolling
        self.textWidget.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        self.textWidget.setWordWrapMode(QTextOption.WordWrap)
        self.textWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # No horizontal scroll
        self.textWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Vertical scroll when needed
        
        # Mouse wheel scrolling is enabled by default in QTextEdit
        
        # Remove borders and set transparent background (container will paint background)
        self.textWidget.setStyleSheet("QTextEdit { border: none; background: transparent; }")
        
        # Create layout
        self.textLayout = QtWidgets.QVBoxLayout()
        self.textLayout.setContentsMargins(4, 2, 9, 7)  # left, top, right, bottom
        self.textLayout.setSpacing(5)
        self.textLayout.addWidget(self.labelTitle)
        self.textLayout.addWidget(self.textWidget)
        
        self.setLayout(self.textLayout)
        
        # Calculate and set initial size
        self.updateSize()
    
    def updateSize(self):
        """
        Calculate and set the widget size based on:
        1. User-specified width/height
        2. Title width (if title is wider than specified/default width)
        3. Default dimensions
        """
        # Start with user-specified or default dimensions
        final_width = self.custom_width if self.custom_width is not None else self.default_width
        final_height = self.custom_height if self.custom_height is not None else self.default_height
        
        # Calculate title width if labelTitle exists
        if hasattr(self, 'labelTitle') and self.labelTitle:
            # Method 1: Try to get actual width from labelTitle after it's been sized
            # This is more accurate as it takes into account the actual font and styles applied
            try:
                # Force label to calculate its size
                self.labelTitle.adjustSize()
                actual_title_width = self.labelTitle.sizeHint().width()
                # If we get a valid width, use it
                if actual_title_width > 0:
                    title_width = actual_title_width
                else:
                    # Fallback to manual calculation
                    raise ValueError("Size hint not available")
            except:
                # Method 2: Manual calculation using QFontMetrics
                # Apply font from title1_aspect to get accurate width
                if hasattr(self, 'title1_aspect') and self.title1_aspect.font:
                    temp_font = QFont(self.title1_aspect.font)
                    if self.title1_aspect.size:
                        try:
                            temp_font.setPixelSize(int(self.title1_aspect.size))
                        except Exception:
                            pass
                    font_metrics = QFontMetrics(temp_font)
                else:
                    font_metrics = QFontMetrics(self.labelTitle.font())
                
                # Use horizontalAdvance for more accurate width calculation
                # horizontalAdvance is more precise than boundingRect().width()
                try:
                    title_width = font_metrics.horizontalAdvance(self.title)
                except AttributeError:
                    # Fallback for older PyQt5 versions
                    title_width = font_metrics.boundingRect(self.title).width()
            
            # Calculate total width needed: title width + layout margins + size_manager margins
            layout_left = 4  # Layout left margin
            layout_right = 9  # Layout right margin
            right_margin = getattr(self.size_manager, 'right_margin', 9)  # Size manager right margin
            border_padding = getattr(self.size_manager, 'border_padding', 3)  # Border padding
            
            # Add safety margin to prevent text clipping (empirical adjustment)
            safety_margin = 5  # Extra pixels to prevent clipping
            
            # Total width = title text width + all margins and paddings + safety margin
            title_total_width = title_width + layout_left + layout_right + right_margin + border_padding + safety_margin
            
            # Adjust width if title is wider
            if title_total_width > final_width:
                final_width = title_total_width
        
        # Store calculated sizes
        self.sizeXGlobal = final_width
        self.sizeYGlobal = final_height
        
        # Set minimum and actual size
        self.setMinimumSize(final_width, final_height)
        self.resize(final_width, final_height)
        
        # Update text widget width for proper wrapping
        # Available width = total width - left margin (4) - right margin (9) - border padding (3)
        avail_text_width = final_width - 4 - 9 - 3
        if avail_text_width > 0:
            # Set document text width for proper wrapping
            doc = self.textWidget.document()
            if doc:
                doc.setTextWidth(float(avail_text_width))
    
    def getSizeXGlobal(self):
        """Return the calculated width."""
        if hasattr(self, 'sizeXGlobal'):
            return self.sizeXGlobal
        return self.default_width
    
    def getSizeYGlobal(self):
        """Return the calculated height."""
        if hasattr(self, 'sizeYGlobal'):
            return self.sizeYGlobal
        return self.default_height
    
    def setWidth(self, width):
        """
        Set custom width for the text box.
        
        Args:
            width (int): Width in pixels
        """
        self.custom_width = width
        self.updateSize()
    
    def setHeight(self, height):
        """
        Set custom height for the text box.
        
        Args:
            height (int): Height in pixels
        """
        self.custom_height = height
        self.updateSize()
    
    def setSize(self, width, height):
        """
        Set custom width and height for the text box.
        
        Args:
            width (int): Width in pixels
            height (int): Height in pixels
        """
        self.custom_width = width
        self.custom_height = height
        self.updateSize()
    
    def resizeEvent(self, event):
        """Override resize event to update text widget width for proper wrapping."""
        super().resizeEvent(event)
        new_width = event.size().width()
        # Update text widget document width for proper wrapping
        avail_text_width = new_width - 4 - 9 - 3  # Account for margins
        if avail_text_width > 0:
            doc = self.textWidget.document()
            if doc:
                doc.setTextWidth(float(avail_text_width))
    
    def onTextAspectsChanged(self):
        """
        Apply text styling from aspects (title1_aspect and text1_aspect).
        This is called automatically when aspects change.
        """
        # Font weight helper
        def _apply_weight_to_font(font_obj: QFont, weight_value):
            try:
                self.applyFontWeightToQFont(font_obj, weight_value)
            except Exception:
                pass
        
        # Alignment mapping helper
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
        
        # Apply title styling
        if hasattr(self, 'labelTitle') and self.labelTitle:
            f = self.labelTitle.font()
            if hasattr(self, 'title1_aspect') and self.title1_aspect:
                # Font family
                if self.title1_aspect.font:
                    f.setFamily(self.title1_aspect.font)
                # Font size
                if self.title1_aspect.size:
                    try:
                        f.setPixelSize(int(self.title1_aspect.size))
                    except Exception:
                        pass
                # Font weight
                _apply_weight_to_font(f, getattr(self.title1_aspect, 'font_weight', None))
                # Font style (italic/oblique)
                if self.title1_aspect.font_style:
                    s = str(self.title1_aspect.font_style).lower()
                    f.setItalic(s in ('italic', 'oblique'))
                self.labelTitle.setFont(f)
                
                # Alignment: use title1_aspect.alignment (set via setTitleAlignment or directly)
                aspect_alignment = getattr(self.title1_aspect, 'alignment', None)
                if aspect_alignment:
                    al = _map_alignment(aspect_alignment)
                    if al is not None:
                        self.labelTitle.setAlignment(al)
                # Fallback to titleAlignment parameter if aspect alignment not set
                elif hasattr(self, 'titleAlignment') and self.titleAlignment:
                    if self.titleAlignment == 'center':
                        self.labelTitle.setAlignment(Qt.AlignCenter)
                    elif self.titleAlignment == 'right':
                        self.labelTitle.setAlignment(Qt.AlignRight)
                    else:  # 'left' or default
                        self.labelTitle.setAlignment(Qt.AlignLeft)
                
                # Color and text decoration via stylesheet
                css_parts = []
                if self.title1_aspect.color:
                    css_parts.append(f"color: {QColor(self.title1_aspect.color).name()}")
                td = getattr(self.title1_aspect, 'text_decoration', None)
                css_parts.append(f"text-decoration: {td}" if td and str(td).lower() != 'none' else "text-decoration: none")
                if css_parts:
                    self.labelTitle.setStyleSheet("; ".join(css_parts))
        
        # Apply text styling
        if hasattr(self, 'textWidget') and self.textWidget:
            f = self.textWidget.font()
            if hasattr(self, 'text1_aspect') and self.text1_aspect:
                # Font family
                if self.text1_aspect.font:
                    f.setFamily(self.text1_aspect.font)
                # Font size
                if self.text1_aspect.size:
                    try:
                        f.setPixelSize(int(self.text1_aspect.size))
                    except Exception:
                        pass
                # Font weight
                _apply_weight_to_font(f, getattr(self.text1_aspect, 'font_weight', None))
                # Font style (italic/oblique)
                if self.text1_aspect.font_style:
                    s = str(self.text1_aspect.font_style).lower()
                    f.setItalic(s in ('italic', 'oblique'))
                self.textWidget.setFont(f)
                
                # Alignment for QTextEdit
                al = _map_alignment(getattr(self.text1_aspect, 'alignment', None))
                if al is not None:
                    self.textWidget.setAlignment(al)
                
                # Color and text decoration via stylesheet
                css_parts = []
                if self.text1_aspect.color:
                    css_parts.append(f"color: {QColor(self.text1_aspect.color).name()}")
                td = getattr(self.text1_aspect, 'text_decoration', None)
                if td and str(td).lower() != 'none':
                    css_parts.append(f"text-decoration: {td}")
                # QTextEdit base styles
                css_base = "QTextEdit { border: none; background: transparent; "
                if css_parts:
                    css_base += "; ".join(css_parts) + "; "
                css_base += "}"
                self.textWidget.setStyleSheet(css_base)
        
        # Recalculate size in case title width changed
        self.updateSize()
    
    def paintEvent(self, event):
        """Paint the background, border, and content."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        # Background: prefer image, else color
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
        
        # Border
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
        
        width = max(0, self.getSizeXGlobal() - 1)
        height = max(0, self.getSizeYGlobal() - 1)
        radius = getattr(self.gs_aspect, 'border_radius', None) or 0
        if radius > 0:
            painter.drawRoundedRect(0, 0, width, height, radius, radius)
        else:
            painter.drawRect(0, 0, width, height)
    
    def show_contextMenu(self, position):
        """Show context menu with Inspect and Close options."""
        menu = QMenu(self)
        
        inspect_action = QAction("Inspect", self)
        inspect_action.triggered.connect(self.show_inspect_dialog)
        menu.addAction(inspect_action)
        
        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close)
        menu.addAction(close_action)
        
        menu.exec_(self.mapToGlobal(position))
    
    def setText(self, text):
        """
        Replace the text by a new text.
        
        Args:
            text (str): New text to display
        """
        self.textToWrite = text
        if hasattr(self, 'textWidget') and self.textWidget:
            self.textWidget.setPlainText(text)
        # Add to history for tracking
        if hasattr(self, 'history'):
            self.history.append(text)
    
    def setTitle(self, title):
        """
        Replace the title by a new title.
        
        Args:
            title (str): New title
        """
        self.title = title
        if hasattr(self, 'labelTitle') and self.labelTitle:
            self.labelTitle.setText(title)
        # Recalculate size as title width may have changed
        self.updateSize()
    
    def setTextFormat(self, fontName='Verdana', size=12):
        """
        Customize the font and the size of the text.
        
        Args:
            fontName (str): Desired font name (default: 'Verdana')
            size (int): Desired font size in pixels (default: 12)
        """
        # Update text1_aspect
        if hasattr(self, 'text1_aspect') and self.text1_aspect:
            self.text1_aspect.font = fontName
            self.text1_aspect.size = size
        
        # Apply the font immediately
        if hasattr(self, 'textWidget') and self.textWidget:
            font = QFont(fontName)
            try:
                font.setPixelSize(int(size))
            except Exception:
                font.setPointSize(int(size))
            self.textWidget.setFont(font)
    
    def setTitleFormat(self, fontName='Verdana', size=14):
        """
        Customize the font and the size of the title.
        
        Args:
            fontName (str): Desired font name (default: 'Verdana')
            size (int): Desired font size in pixels (default: 14)
        """
        # Update title1_aspect
        if hasattr(self, 'title1_aspect') and self.title1_aspect:
            self.title1_aspect.font = fontName
            self.title1_aspect.size = size
        
        # Apply the font immediately
        if hasattr(self, 'labelTitle') and self.labelTitle:
            font = QFont(fontName)
            try:
                font.setPixelSize(int(size))
            except Exception:
                font.setPointSize(int(size))
            self.labelTitle.setFont(font)
        
        # Recalculate size as title width may have changed
        self.updateSize()
    
    def show_inspect_dialog(self):
        """Show inspection dialog with widget information."""
        from PyQt5.QtWidgets import QMessageBox
        info = f"Widget ID: {self.id}\n"
        info += f"Title: {self.title}\n"
        info += f"Size: {self.getSizeXGlobal()}x{self.getSizeYGlobal()}\n"
        info += f"Text length: {len(self.textToWrite)} characters"
        QMessageBox.information(self, "Inspect", info)

