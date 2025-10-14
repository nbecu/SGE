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
            self.textWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Show scrollbar when needed
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
            
        # Use actual layout size if available
        if hasattr(self, 'textLayout') and self.textLayout:
            # Force layout to calculate its size
            self.textLayout.activate()
            size_hint = self.textLayout.sizeHint()
            if size_hint and size_hint.isValid():
                return max(size_hint.width() + self.size_manager.right_margin, self.size_manager.min_width)
        
        # Fallback: use size_manager to calculate width based on content
        if hasattr(self, 'textEdit') and self.textEdit:
            if hasattr(self.textEdit, 'toPlainText'):
                text_content = self.textEdit.toPlainText()
            else:
                text_content = self.textEdit.text()
            return self.calculateContentWidth(text_content=text_content)
        return self.size_manager.min_width

    def getSizeYGlobal(self):
        # Use manual size if specified
        if self.sizeY is not None:
            return self.sizeY
        
        # Always use font-based calculation for accurate height
        if hasattr(self, 'textEdit') and self.textEdit:
            if hasattr(self.textEdit, 'toPlainText'):
                text_content = self.textEdit.toPlainText()
            else:
                text_content = self.textEdit.text()
            
            # Get the actual font from the text widget for accurate height calculation
            text_font = self.textEdit.font() if hasattr(self.textEdit, 'font') else None
            calculated_height = self.calculateContentHeight(text_content=text_content, font=text_font)
            
            # Add height for title if it exists
            if hasattr(self, 'labelTitle') and self.labelTitle:
                title_font = self.labelTitle.font()
                # Use QFontMetrics for accurate title height calculation
                title_metrics = QFontMetrics(title_font)
                title_height = title_metrics.height() + self.size_manager.vertical_gap_between_labels
                calculated_height += title_height
            
            # Use higher minimum height for long text
            min_height = self.min_height_for_long_text if len(text_content) > 100 else self.size_manager.min_height
            
            return max(calculated_height, min_height)
        
        return self.size_manager.min_height

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # Background with transparency support
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

        width = max(0, self.getSizeXGlobal() - 1)
        height = max(0, self.getSizeYGlobal() - 1)
        radius = getattr(self.gs_aspect, 'border_radius', None) or 0
        if radius > 0:
            painter.drawRoundedRect(0, 0, width, height, radius, radius)
        else:
            painter.drawRect(0, 0, width, height)
    
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
            if self.title1_aspect.font_weight:
                w = str(self.title1_aspect.font_weight).lower()
                if w == 'bold':
                    f.setBold(True)
                elif w == 'normal':
                    f.setBold(False)
                else:
                    try:
                        f.setWeight(int(self.title1_aspect.font_weight))
                    except Exception:
                        pass
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
                if self.text1_aspect.font_weight:
                    w = str(self.text1_aspect.font_weight).lower()
                    if w == 'bold':
                        f.setBold(True)
                    elif w == 'normal':
                        f.setBold(False)
                    else:
                        try:
                            f.setWeight(int(self.text1_aspect.font_weight))
                        except Exception:
                            pass
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
                if self.text1_aspect.font_weight:
                    w = str(self.text1_aspect.font_weight).lower()
                    if w == 'bold':
                        f.setBold(True)
                    elif w == 'normal':
                        f.setBold(False)
                    else:
                        try:
                            f.setWeight(int(self.text1_aspect.font_weight))
                        except Exception:
                            pass
                if self.text1_aspect.font_style:
                    s = str(self.text1_aspect.font_style).lower()
                    f.setItalic(s in ('italic', 'oblique'))
                target.setFont(f)
                color_css = QColor(self.text1_aspect.color).name() if self.text1_aspect.color else None
                if color_css:
                    target.setStyleSheet(f"QTextEdit {{ border: none; background: transparent; color: {color_css}; }}")
                else:
                    target.setStyleSheet("QTextEdit { border: none; background: transparent; }")

        # Resize based on layout
        if hasattr(self, 'textLayout') and self.textLayout:
            self.updateSizeFromLayout(self.textLayout)
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
