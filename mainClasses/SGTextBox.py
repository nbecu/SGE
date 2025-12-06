from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
from PyQt5.QtWidgets import QMenu, QAction
from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGAspect import SGAspect


class SGTextBox(SGGameSpace):
    """
    A text display widget that allows long texts with scrollable content and shrinked functionality.
    
    It provides a flexible text display solution that can adapt to long text or to shorter one with a shrinked functionality.

    SGTextBox provides a simpler and more reliable implementation for displaying
    long texts with the following features:
    - Default width and height (250x150 pixels)
    - Automatic width adjustment if title is wider than default width and shrinked functionality
    - Automatic word-wrapping for text content
    - Vertical scrolling when text exceeds height (via mouse wheel and scrollbar)
    - User-configurable width and height and shrinked functionality
    
    Args:
        parent: The parent widget/model
        textToWrite (str): Initial text content to display
        title (str): Title displayed above the text content
        width (int, optional): Custom width in pixels (default: 250)
        height (int, optional): Custom height in pixels (default: 150)
        shrinked (bool, optional): If True, the text box will be shrinked to fit content (default: True)
        borderColor (QColor): Border color (default: Qt.black)
        backgroundColor (QColor): Background color (default: Qt.lightGray)
        titleAlignment (str): Title alignment - 'left', 'center', or 'right' (default: 'left')
    """
    
    def __init__(self, parent, textToWrite, title, width=None, height=None, shrinked=True,
                 borderColor=Qt.black, backgroundColor=Qt.lightGray, titleAlignment='left', chronologicalOrder=True):
        super().__init__(parent, 0, 60, 0, 0, true, backgroundColor)
        
        self.title = title
        self.id = title
        self.model = parent
        self.textToWrite = textToWrite
        self.chronologicalOrder = chronologicalOrder  # If True, addText() adds at bottom (chronological). If False, adds at top (reverse chronological).
        
        # Configure border using gs_aspect
        self.gs_aspect.border_color = borderColor
        self.gs_aspect.border_size = 1
        
        # Default dimensions
        self.default_width = 250
        self.default_height = 150
        
        # User-specified dimensions (if None, use defaults)
        self.custom_width = width
        self.custom_height = height
        # Compatibility attributes (for backward compatibility with SGTextBox API)
        self.sizeX = width  # Alias for custom_width
        self.sizeY = height  # Alias for custom_height
        
        # Shrinked mode configuration
        self.shrinked = shrinked
        self.max_width_default = 250  # Default maximum width when shrinked=True (only applies if width not specified)
        self.max_height_default = 150  # Default maximum height when shrinked=True
        self.min_width = 100  # Minimum width when shrinked=True
        self.min_height = 50  # Minimum height when shrinked=True
        
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
    
    def _calculateTitleWidth(self):
        """Calculate the width needed for the title."""
        if not hasattr(self, 'labelTitle') or not self.labelTitle:
            return 0
        
        try:
            # Force label to calculate its size
            self.labelTitle.adjustSize()
            actual_title_width = self.labelTitle.sizeHint().width()
            if actual_title_width > 0:
                return actual_title_width
        except:
            pass
        
        # Fallback: Manual calculation using QFontMetrics
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
        
        try:
            return font_metrics.horizontalAdvance(self.title)
        except AttributeError:
            return font_metrics.boundingRect(self.title).width()
    
    def _calculateMinTextWidth(self):
        """
        Calculate the absolute minimum width needed for the text content.
        This finds the longest line in the text (considering line breaks) without word-wrap.
        
        Returns:
            int: Minimum width needed for the text (longest line width)
        """
        if not hasattr(self, 'textWidget') or not self.textWidget:
            return 0
        
        try:
            # Get text content
            text_content = self.textWidget.toPlainText()
            if not text_content:
                return 0
            
            # Get font from text widget
            text_font = self.textWidget.font()
            metrics = QFontMetrics(text_font)
            
            # Split by line breaks and find the longest line
            lines = text_content.split('\n')
            max_line_width = 0
            
            for line in lines:
                if line.strip():  # Skip empty lines
                    line_width = metrics.horizontalAdvance(line) if hasattr(metrics, 'horizontalAdvance') else metrics.boundingRect(line).width()
                    max_line_width = max(max_line_width, line_width)
            
            return max_line_width
        except Exception:
            # Fallback: estimate based on text length
            try:
                text_content = self.textWidget.toPlainText()
                text_font = self.textWidget.font()
                metrics = QFontMetrics(text_font)
                # Estimate: average character width * text length / 2 (rough estimate)
                avg_char_width = metrics.horizontalAdvance('M') if hasattr(metrics, 'horizontalAdvance') else metrics.boundingRect('M').width()
                estimated_width = int(avg_char_width * len(text_content) / 2)
                return max(estimated_width, 50)  # Minimum 50px
            except Exception:
                return 100  # Default fallback
    
    def _calculateTextHeight(self, available_width):
        """
        Calculate the exact height needed for the text content after word-wrap.
        
        Args:
            available_width (int): Available width for text wrapping
            
        Returns:
            int: Height needed for the wrapped text
        """
        if not hasattr(self, 'textWidget') or not self.textWidget:
            return 0
        
        try:
            # Get document and set width for wrapping calculation
            doc = self.textWidget.document()
            if not doc:
                return 0
            
            # Set document width to enable wrapping calculation
            doc.setTextWidth(float(available_width))
            doc.adjustSize()
            
            # Get document height
            doc_height = doc.size().height()
            
            # Add frame width and margins for QTextEdit
            frame_w = self.textWidget.frameWidth() if hasattr(self.textWidget, 'frameWidth') else 0
            margins = self.textWidget.contentsMargins() if hasattr(self.textWidget, 'contentsMargins') else QMargins(0, 0, 0, 0)
            text_h = int(doc_height + 2 * frame_w + margins.top() + margins.bottom())
            
            return text_h
        except Exception:
            # Fallback: estimate using font metrics
            try:
                text_content = self.textWidget.toPlainText()
                text_font = self.textWidget.font()
                metrics = QFontMetrics(text_font)
                wrapped_rect = metrics.boundingRect(
                    QRect(0, 0, available_width, 10**6),
                    Qt.TextWordWrap,
                    text_content
                )
                return wrapped_rect.height()
            except Exception:
                return 100  # Default fallback height
    
    def updateSize(self):
        """
        Calculate and set the widget size.
        
        Behavior depends on shrinked mode:
        - If shrinked=False: Use fixed dimensions (custom or default)
        - If shrinked=True: Calculate dynamic dimensions based on content
        """
        # Get layout margins
        layout_left = 4  # Layout left margin
        layout_right = 9  # Layout right margin
        layout_top = 2  # Layout top margin
        layout_bottom = 7  # Layout bottom margin
        layout_spacing = 5  # Layout spacing between title and text
        right_margin = getattr(self.size_manager, 'right_margin', 9)
        border_padding = getattr(self.size_manager, 'border_padding', 3)
        
        if not self.shrinked:
            # Standard mode: fixed dimensions
            # Check sizeX/sizeY first for compatibility, then custom_width/custom_height
            final_width = self.sizeX if (hasattr(self, 'sizeX') and self.sizeX is not None) else (self.custom_width if self.custom_width is not None else self.default_width)
            final_height = self.sizeY if (hasattr(self, 'sizeY') and self.sizeY is not None) else (self.custom_height if self.custom_height is not None else self.default_height)
            
            # Adjust width if title is wider
            title_width = self._calculateTitleWidth()
            title_total_width = title_width + layout_left + layout_right + right_margin + border_padding + 5
            if title_total_width > final_width:
                final_width = title_total_width
        else:
            # Shrinked mode: dynamic dimensions
            # Determine maximum height (check sizeY first for compatibility, then custom_height)
            max_height = self.sizeY if (hasattr(self, 'sizeY') and self.sizeY is not None) else (self.custom_height if self.custom_height is not None else self.max_height_default)
            
            # Check sizeX first for compatibility, then custom_width
            width_specified = self.sizeX if (hasattr(self, 'sizeX') and self.sizeX is not None) else self.custom_width
            
            if width_specified is not None:
                # Width is fixed by user
                final_width = width_specified
                # Title will be cropped if it exceeds this width (no word-wrap for title)
                
                # Calculate available width for text
                avail_text_width = final_width - layout_left - layout_right - border_padding
                
                # Calculate height needed
                title_height = 0
                if hasattr(self, 'labelTitle') and self.labelTitle:
                    title_font = self.labelTitle.font()
                    title_metrics = QFontMetrics(title_font)
                    title_height = title_metrics.height()
                
                text_height = self._calculateTextHeight(avail_text_width)
                
                # Total height = title + spacing + text + layout margins + border padding
                calculated_height = title_height + layout_spacing + text_height + layout_top + layout_bottom + border_padding
                
                # Apply minimum and maximum
                final_height = max(self.min_height, min(calculated_height, max_height))
                
                # Configure scrollbar based on whether height exceeds max
                # Only if textWidget exists
                if hasattr(self, 'textWidget') and self.textWidget:
                    if calculated_height > max_height:
                        # Need scrollbar
                        self.textWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                    else:
                        # No scrollbar needed
                        self.textWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            else:
                # Width is dynamic: calculate minimum needed
                title_width = self._calculateTitleWidth()
                
                # Calculate minimum text width needed (longest line in text)
                min_text_width = self._calculateMinTextWidth()
                
                # Final content width = max(title_width, min_text_width)
                # This is the minimum width needed for content
                content_width = max(title_width, min_text_width)
                
                # Final width = content width + all margins and paddings
                final_width = content_width + layout_left + layout_right + right_margin + border_padding + 5
                final_width = max(final_width, self.min_width)  # Apply minimum
                final_width = min(final_width, self.max_width_default)  # Apply maximum (250px)
                
                # Calculate available width for text wrapping
                avail_text_width = final_width - layout_left - layout_right - border_padding
                
                # Calculate height needed
                title_height = 0
                if hasattr(self, 'labelTitle') and self.labelTitle:
                    title_font = self.labelTitle.font()
                    title_metrics = QFontMetrics(title_font)
                    title_height = title_metrics.height()
                
                text_height = self._calculateTextHeight(avail_text_width)
                
                # Total height = title + spacing + text + layout margins + border padding
                calculated_height = title_height + layout_spacing + text_height + layout_top + layout_bottom + border_padding
                
                # Apply minimum and maximum
                final_height = max(self.min_height, min(calculated_height, max_height))
                
                # Configure scrollbar based on whether height exceeds max
                # Only if textWidget exists
                if hasattr(self, 'textWidget') and self.textWidget:
                    if calculated_height > max_height:
                        # Need scrollbar
                        self.textWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                    else:
                        # No scrollbar needed
                        self.textWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Store calculated sizes
        self.sizeXGlobal = final_width
        self.sizeYGlobal = final_height
        
        # Set minimum and actual size
        self.setMinimumSize(final_width, final_height)
        self.resize(final_width, final_height)
        
        # Update text widget width for proper wrapping
        # Only if textWidget exists
        if hasattr(self, 'textWidget') and self.textWidget:
            avail_text_width = final_width - layout_left - layout_right - border_padding
            if avail_text_width > 0:
                # Set document text width for proper wrapping
                doc = self.textWidget.document()
                if doc:
                    doc.setTextWidth(float(avail_text_width))
    
    def resizeEvent(self, event):
        """Override resize event to update text widget width for proper wrapping."""
        super().resizeEvent(event)
        # Only update if textWidget exists
        if not hasattr(self, 'textWidget') or not self.textWidget:
            return
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
        from mainClasses.SGExtensions import mapAlignmentStringToQtFlags
        
        # Apply title styling (QLabel - can use helper)
        if hasattr(self, 'labelTitle') and self.labelTitle:
            if hasattr(self, 'title1_aspect') and self.title1_aspect:
                # Use helper for font, color, decoration
                self._applyAspectToLabel(self.labelTitle, self.title1_aspect)
                
                # Fallback to titleAlignment parameter if aspect alignment not set
                aspect_alignment = getattr(self.title1_aspect, 'alignment', None)
                if not aspect_alignment and hasattr(self, 'titleAlignment') and self.titleAlignment:
                    if self.titleAlignment == 'center':
                        self.labelTitle.setAlignment(Qt.AlignCenter)
                    elif self.titleAlignment == 'right':
                        self.labelTitle.setAlignment(Qt.AlignRight)
                    else:  # 'left' or default
                        self.labelTitle.setAlignment(Qt.AlignLeft)
        
        # Apply text styling (QTextEdit - needs special handling)
        if hasattr(self, 'textWidget') and self.textWidget:
            if hasattr(self, 'text1_aspect') and self.text1_aspect:
                # Apply font properties
                f = self.textWidget.font()
                self.text1_aspect.applyToQFont(f, self)
                self.textWidget.setFont(f)
                
                # Alignment for QTextEdit
                al = getattr(self.text1_aspect, 'alignment', None)
                if al:
                    qt_alignment = mapAlignmentStringToQtFlags(al)
                    if qt_alignment is not None:
                        self.textWidget.setAlignment(qt_alignment)
                
                # Color and text decoration via stylesheet (with QTextEdit base styles)
                css_parts = []
                stylesheet = self.text1_aspect.getStyleSheetForColorAndDecoration()
                if stylesheet:
                    css_parts.append(stylesheet)
                # QTextEdit base styles
                css_base = "QTextEdit { border: none; background: transparent; "
                if css_parts:
                    css_base += "; ".join(css_parts) + "; "
                css_base += "}"
                self.textWidget.setStyleSheet(css_base)
        
        # Recalculate size in case title width or text height changed
        # (especially important in shrinked mode)
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
        
        # Use actual widget size (self.width/height) with fallback to getSizeX/YGlobal
        # This ensures the border is drawn within the actual widget bounds
        # even if the layout has resized the widget differently than calculated
        width = max(0, getattr(self, 'sizeXGlobal', self.width()) - 1)
        height = max(0, getattr(self, 'sizeYGlobal', self.height()) - 1)
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
    
    def _recreateTextWidget(self):
        """
        Recreate the text widget if it was deleted.
        This is a safety method in case the widget is somehow missing.
        """
        # Create text widget (same configuration as in initUI)
        self.textWidget = QtWidgets.QTextEdit()
        self.textWidget.setPlainText(self.textToWrite)
        self.textWidget.setReadOnly(True)
        
        # Configure word-wrap and scrolling
        self.textWidget.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        self.textWidget.setWordWrapMode(QTextOption.WordWrap)
        self.textWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Remove borders and set transparent background
        self.textWidget.setStyleSheet("QTextEdit { border: none; background: transparent; }")
        
        # Add to layout (after title if title exists, otherwise at index 0)
        if hasattr(self, 'textLayout') and self.textLayout:
            if hasattr(self, 'labelTitle') and self.labelTitle:
                # Insert after title
                self.textLayout.addWidget(self.textWidget)
            else:
                # No title, add at beginning
                self.textLayout.insertWidget(0, self.textWidget)
        
        # Apply text aspects if they exist
        if hasattr(self, 'text1_aspect') and self.text1_aspect:
            self.onTextAspectsChanged()
    
    def getSizeXGlobal(self):
        """Return the calculated width."""
        # Use manual size if specified (compatibility with SGTextBox API)
        if hasattr(self, 'sizeX') and self.sizeX is not None:
            return self.sizeX
        # Use custom_width if specified
        if self.custom_width is not None:
            return self.custom_width
        # Use calculated size if available
        if hasattr(self, 'sizeXGlobal'):
            return self.sizeXGlobal
        return self.default_width
    
    def getSizeYGlobal(self):
        """Return the calculated height."""
        # Use manual size if specified (compatibility with SGTextBox API)
        if hasattr(self, 'sizeY') and self.sizeY is not None:
            return self.sizeY
        # Use custom_height if specified
        if self.custom_height is not None:
            return self.custom_height
        # Use calculated size if available
        if hasattr(self, 'sizeYGlobal'):
            return self.sizeYGlobal
        return self.default_height
    
    def show_inspect_dialog(self):
        """Show inspection dialog with widget information."""
        from PyQt5.QtWidgets import QMessageBox
        info = f"Widget ID: {self.id}\n"
        info += f"Title: {self.title}\n"
        info += f"Size: {self.getSizeXGlobal()}x{self.getSizeYGlobal()}\n"
        info += f"Text length: {len(self.textToWrite)} characters"
        QMessageBox.information(self, "Inspect", info)
    
    # ============================================================================
    # MODELER METHODS
    # ============================================================================
    
    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================
    
    def setText(self, text):
        """
        Replace the text by a new text.
        
        Args:
            text (str): New text to display
        """
        # Recreate textWidget if it was deleted
        if not hasattr(self, 'textWidget') or not self.textWidget:
            self._recreateTextWidget()
        
        self.textToWrite = text
        self.textWidget.setPlainText(text)
        # Add to history for tracking
        if hasattr(self, 'history'):
            self.history.append(text)
        # Recalculate size if in shrinked mode
        if self.shrinked:
            self.updateSize()
    
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
        # (especially important in shrinked mode)
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
        
        # Recalculate size if in shrinked mode (font change affects height)
        if self.shrinked:
            self.updateSize()
    
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
        # (especially important in shrinked mode)
        self.updateSize()
    
    def setWidth(self, width):
        """
        Set custom width for the text box.
        
        Args:
            width (int): Width in pixels
        """
        self.custom_width = width
        # Update compatibility attribute
        self.sizeX = width
        # Recalculate size (especially important in shrinked mode)
        self.updateSize()
    
    def setHeight(self, height):
        """
        Set custom height for the text box.
        
        Args:
            height (int): Height in pixels
        """
        self.custom_height = height
        # Update compatibility attribute
        self.sizeY = height
        # Recalculate size (especially important in shrinked mode where height becomes max)
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
        # Update compatibility attributes
        self.sizeX = width
        self.sizeY = height
        # Recalculate size (especially important in shrinked mode)
        self.updateSize()
    
    def addText(self, text, toTheLine=True):
        """
        Add text to the text box.
        
        Args:
            text (str): Text to add
            toTheLine (bool): If True, skip a line before adding (only if there's existing text)
        """
        # Recreate textWidget if it was deleted
        if not hasattr(self, 'textWidget') or not self.textWidget:
            self._recreateTextWidget()
        
        # Get current text first
        current_text = self.textWidget.toPlainText()
        
        # If toTheLine is True, add line break only if there's existing text
        if toTheLine and current_text.strip():
            separator = "\n"
        else:
            separator = ""
        
        # Add text based on chronologicalOrder setting
        if self.chronologicalOrder:
            # Add text at the bottom (chronological order - oldest at top, newest at bottom)
            if separator:
                new_full_text = current_text + separator + text
            else:
                new_full_text = current_text + text
        else:
            # Add text at the top (reverse chronological order - newest at top, oldest at bottom)
            if separator:
                new_full_text = text + separator + current_text
            else:
                new_full_text = text + current_text
        self.textWidget.setPlainText(new_full_text)
        # Update textToWrite
        self.textToWrite = new_full_text
        # Add to history
        if hasattr(self, 'history'):
            self.history.append(text)
        # Recalculate size if in shrinked mode
        if self.shrinked:
            self.updateSize()
    
    
    def setTitleColor(self, color='red'):
        """
        Set the color of the title.
        
        Args:
            color (str or QColor): Desired color (can be color name string or QColor)
        """
        if hasattr(self, 'title1_aspect') and self.title1_aspect:
            # Convert string color to QColor if needed
            if isinstance(color, str):
                # Try to get QColor from string (e.g., 'red', '#FF0000')
                try:
                    qcolor = QColor(color)
                    if qcolor.isValid():
                        self.title1_aspect.color = qcolor
                    else:
                        # Fallback: set via stylesheet
                        if hasattr(self, 'labelTitle') and self.labelTitle:
                            self.labelTitle.setStyleSheet(f"color: {color};")
                except Exception:
                    # Fallback: set via stylesheet
                    if hasattr(self, 'labelTitle') and self.labelTitle:
                        self.labelTitle.setStyleSheet(f"color: {color};")
            else:
                # It's already a QColor
                self.title1_aspect.color = color
            # Apply the change
            self.onTextAspectsChanged()
        else:
            # Fallback: set via stylesheet
            if hasattr(self, 'labelTitle') and self.labelTitle:
                self.labelTitle.setStyleSheet(f"color: {color};")
    
    def setTitleSize(self, size="20px"):
        """
        Set the size of the title.
        
        Args:
            size (str or int): Desired size (e.g., "20px" or 20)
        """
        # Extract numeric value from string if needed
        if isinstance(size, str):
            # Remove 'px' if present
            size_str = size.replace('px', '').strip()
            try:
                size_int = int(size_str)
            except ValueError:
                size_int = 20  # Default fallback
        else:
            size_int = int(size)
        
        # Use setTitleFormat to set the size (preserving current font)
        current_font = "Verdana"  # Default
        if hasattr(self, 'title1_aspect') and self.title1_aspect and self.title1_aspect.font:
            current_font = self.title1_aspect.font
        
        self.setTitleFormat(fontName=current_font, size=size_int)
    
    def setBorderColor(self, color):
        """
        Set the border color of the text box.
        
        Args:
            color (QColor or Qt.GlobalColor): The border color
        """
        self.gs_aspect.border_color = color
        self.update()  # Force repaint
    
    def setBorderSize(self, size):
        """
        Set the border size of the text box.
        
        Args:
            size (int): The border size in pixels
        """
        self.gs_aspect.border_size = size
        self.update()  # Force repaint
    
    # ============================================================================
    # DELETE METHODS
    # ============================================================================
    
    def deleteTitle(self):
        """
        Delete the title.
        Note: This removes the title label from the widget.
        """
        if hasattr(self, 'labelTitle') and self.labelTitle:
            # Remove from layout
            if hasattr(self, 'textLayout') and self.textLayout:
                self.textLayout.removeWidget(self.labelTitle)
            # Delete the widget
            self.labelTitle.deleteLater()
            self.labelTitle = None
            # Recalculate size if in shrinked mode
            if self.shrinked:
                self.updateSize()
    
    def eraseText(self):
        """
        Erase the text content.
        Note: This clears the text but keeps the widget intact.
        """
        # Clear text content
        self.textToWrite = ""
        # Update widget if it exists
        if hasattr(self, 'textWidget') and self.textWidget:
            self.textWidget.setPlainText("")
        # Recalculate size if in shrinked mode
        if self.shrinked:
            self.updateSize()
    
    # ============================================================================
    # DO/DISPLAY METHODS
    # ============================================================================
    
    def updateText(self):
        """
        Update the text widget content.
        This method is called by addText() but can also be called directly.
        """
        # Force size update if in shrinked mode
        if self.shrinked:
            self.updateSize()
