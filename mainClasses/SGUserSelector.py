from PyQt5.QtWidgets import QCheckBox, QHBoxLayout, QVBoxLayout, QLabel
from mainClasses.SGGameSpace import SGGameSpace
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true


class SGUserSelector(SGGameSpace):
    def __init__(self, parent, users, orientation='horizontal'):
        super().__init__(parent, 0, 60, 0, 0, true)
        self.model = parent
        self.users = users
        self.orientation = orientation  # 'horizontal' or 'vertical'
        self.id = 'userSelector'
        self.initUI()

    def initUI(self):
        # Create layout based on orientation
        if self.orientation == 'vertical':
            self.userLayout = QVBoxLayout()
        else:  # horizontal (default)
            self.userLayout = QHBoxLayout()
        # Marges cohérentes et espacement
        try:
            # Augmente les marges haut/bas pour éviter que le contenu colle aux bords
            self.userLayout.setContentsMargins(4, self.verticalGapBetweenLabels, self.rightMargin, self.verticalGapBetweenLabels*2)
            self.userLayout.setSpacing(self.verticalGapBetweenLabels)
        except Exception:
            pass
        
        self.checkboxes = []
        self.titleLabel = QLabel("User Selector")
        self.userLayout.addWidget(self.titleLabel)
        # Espace supplémentaire entre le titre et le premier item
        try:
            self.userLayout.addSpacing(self.verticalGapBetweenLabels)
        except Exception:
            pass
        self.updateUI(self.userLayout)
        self.setLayout(self.userLayout)
        # Appliquer styles textes et dimensionner
        try:
            self.onTextAspectsChanged()
        except Exception:
            pass
        # Adjust size after layout configuration
        self.adjustSizeAfterLayout()

    def updateUI(self, layout):
        for user in self.users:
            checkbox = QCheckBox(user, self)
            checkbox.stateChanged.connect(self.checkboxChecked)
            self.checkboxes.append(checkbox)
            layout.addWidget(checkbox)
            layout.addSpacing(5)
        for checkbox in self.checkboxes:
            if checkbox.text() !="Admin":
                checkbox.setEnabled(False)
                checkbox.setChecked(False)
        # Espace de fond supplémentaire
        try:
            layout.addSpacing(self.verticalGapBetweenLabels*2)
        except Exception:
            pass
        # Espacement bas supplémentaire pour une marge visuelle confortable
        try:
            layout.addSpacing(self.verticalGapBetweenLabels)
        except Exception:
            pass
    
    def updateOnNewPhase(self):
        players=self.getAuthorizedPlayers()
        alreadyChecked=False
        for checkbox in self.checkboxes:
            if checkbox.text() not in [aPlayer.name for aPlayer in players]:
                checkbox.setEnabled(False)
                checkbox.setChecked(False)
            else:
                checkbox.setEnabled(True)
                if not alreadyChecked:
                    checkbox.setChecked(True)
                    alreadyChecked=True
            
    def setCheckboxesWithSelection(self, aUserName):
        for checkbox in self.checkboxes:
            checkbox.setChecked(checkbox.text() == aUserName)


    def checkboxChecked(self, state):
        sender = self.sender()
        if state == 2:
            for checkbox in self.checkboxes:
                if checkbox is not sender:
                    checkbox.setChecked(False)
                else:
                    self.model.setCurrentPlayer(checkbox.text())

        selectedCheckboxText = sender.text() if sender.isChecked() else None

        self.model.setCurrentPlayer(selectedCheckboxText)
        self.model.update()

    def getAuthorizedPlayers(self):
        if self.model.timeManager.isInitialization():
            return self.model.users
        phase = self.model.timeManager.getCurrentPhase()
        return phase.getAuthorizedPlayers()

    # Function to have the global size of a gameSpace
    def getSizeXGlobal(self):
        # Use actual layout size if available
        if hasattr(self, 'userLayout') and self.userLayout:
            # Force layout to calculate its size
            self.userLayout.activate()
            size_hint = self.userLayout.sizeHint()
            if size_hint and size_hint.isValid():
                return max(size_hint.width() + self.size_manager.right_margin, self.size_manager.min_width)
        
        # Fallback: calculate based on orientation and number of users
        if hasattr(self, 'users') and self.users:
            if self.orientation == 'vertical':
                # For vertical layout, width is determined by the widest checkbox
                estimated_width = 150  # Title width + margins
            else:  # horizontal
                # For horizontal layout, width is sum of all checkboxes
                estimated_width = len(self.users) * 80 + 150  # 80px per user + 150px for title
            return max(estimated_width, self.size_manager.min_width)
        return self.size_manager.min_width

    def getSizeYGlobal(self):
        # Use actual layout size if available
        if hasattr(self, 'userLayout') and self.userLayout:
            # Force layout to calculate its size
            self.userLayout.activate()
            size_hint = self.userLayout.sizeHint()
            if size_hint and size_hint.isValid():
                return max(size_hint.height(), 25)  # Reduced minimum height
        
        # Fallback: calculate based on orientation and checkbox height
        if hasattr(self, 'checkboxes') and self.checkboxes:
            checkbox_height = self.checkboxes[0].sizeHint().height() if self.checkboxes else 18
            if self.orientation == 'vertical':
                # For vertical layout, height is sum of all checkboxes + title
                estimated_height = checkbox_height * (len(self.checkboxes) + 1) + self.size_manager.vertical_gap_between_labels * len(self.checkboxes)
            else:  # horizontal
                # For horizontal layout, height is single checkbox height
                estimated_height = checkbox_height
            return max(estimated_height, 25)  # Reduced minimum height
        # Fallback: standard checkbox height
        return 25  # Reduced from min_height
    
    def adjustSizeAfterLayout(self):
        """
        Adjust widget size after layout configuration.
        """
        if hasattr(self, 'userLayout') and self.userLayout:
            # Force layout to calculate its size
            self.userLayout.activate()
            size_hint = self.userLayout.sizeHint()
            if size_hint and size_hint.isValid():
                # Add margins for border
                width = size_hint.width() + self.size_manager.right_margin + self.size_manager.border_padding
                height = size_hint.height() + self.size_manager.vertical_gap_between_labels + self.size_manager.border_padding
                
                # Apply calculated size
                self.setMinimumSize(width, height)
                self.resize(width, height)

    # Drawing the US
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
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

        # Compute sizes and draw
        try:
            if hasattr(self, 'userLayout') and self.userLayout:
                self.updateSizeFromLayout(self.userLayout)
        except Exception:
            pass
        w = max(0, self.getSizeXGlobal() - 1)
        h = max(0, self.getSizeYGlobal() - 1)
        radius = getattr(self.gs_aspect, 'border_radius', None) or 0
        if radius > 0:
            painter.drawRoundedRect(0, 0, w, h, radius, radius)
        else:
            painter.drawRect(0, 0, w, h)

        painter.end()

    # =========================
    # STYLE/APPLY HOOKS
    # =========================
    def applyContainerAspectStyle(self):
        """Avoid QSS cascade; rely on paintEvent for container rendering."""
        pass

    def onTextAspectsChanged(self):
        # Title styling from title1_aspect
        if hasattr(self, 'titleLabel') and self.titleLabel is not None:
            f = self.titleLabel.font()
            if self.title1_aspect.font:
                f.setFamily(self.title1_aspect.font)
            if self.title1_aspect.size:
                try:
                    f.setPixelSize(int(self.title1_aspect.size))
                except Exception:
                    pass
            try:
                self.applyFontWeightToQFont(f, getattr(self.title1_aspect, 'font_weight', None))
            except Exception:
                pass
            if self.title1_aspect.font_style:
                s = str(self.title1_aspect.font_style).lower()
                f.setItalic(s in ('italic', 'oblique'))
            self.titleLabel.setFont(f)
            css_parts = []
            if self.title1_aspect.color:
                css_parts.append(f"color: {QColor(self.title1_aspect.color).name()}")
            td = getattr(self.title1_aspect, 'text_decoration', None)
            css_parts.append(f"text-decoration: {td}" if td and str(td).lower() != 'none' else "text-decoration: none")
            self.titleLabel.setStyleSheet("; ".join(css_parts))

        # Checkboxes styling from text1_aspect
        for checkbox in getattr(self, 'checkboxes', []) or []:
            f = checkbox.font()
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
            checkbox.setFont(f)
            css_parts = []
            if self.text1_aspect.color:
                css_parts.append(f"color: {QColor(self.text1_aspect.color).name()}")
            # text-decoration may not affect QCheckBox text; still set to clear prior styles
            td = getattr(self.text1_aspect, 'text_decoration', None)
            css_parts.append(f"text-decoration: {td}" if td and str(td).lower() != 'none' else "text-decoration: none")
            checkbox.setStyleSheet("; ".join(css_parts))

        # Resize to layout
        if hasattr(self, 'userLayout') and self.userLayout:
            self.updateSizeFromLayout(self.userLayout)
        self.update()

    # ============================================================================
    # MODELER METHODS
    # ============================================================================
    
    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================
    
    def setTitleText(self, text):
        """
        Set the title text of the user selector.
        
        Args:
            text (str): The title text
        """
        if hasattr(self, 'titleLabel') and self.titleLabel is not None:
            self.titleLabel.setText(text)
        elif hasattr(self, 'userLayout') and self.userLayout:
            # Fallback: Find and update the first QLabel
            for i in range(self.userLayout.count()):
                item = self.userLayout.itemAt(i)
                if item and item.widget() and isinstance(item.widget(), QLabel):
                    item.widget().setText(text)
                    break
        self.update()
        
    def setOrientation(self, orientation):
        """
        Set the orientation of the user selector.
        
        Args:
            orientation (str): 'horizontal' or 'vertical'
        """
        if orientation in ['horizontal', 'vertical']:
            self.orientation = orientation
            # Recreate the layout with new orientation
            self.initUI()
        else:
            raise ValueError("Orientation must be 'horizontal' or 'vertical'")
        
    def setCheckboxStyle(self, style_dict):
        """
        Set the style of all checkboxes.
        
        Args:
            style_dict (dict): Dictionary of style properties for checkboxes
        """
        for checkbox in self.checkboxes:
            style_parts = []
            for key, value in style_dict.items():
                if key == 'color':
                    style_parts.append(f"color: {value}")
                elif key == 'font_size':
                    style_parts.append(f"font-size: {value}px")
                elif key == 'font_family':
                    style_parts.append(f"font-family: {value}")
                elif key == 'font_weight':
                    style_parts.append(f"font-weight: {value}")
            
            if style_parts:
                checkbox.setStyleSheet("; ".join(style_parts))
        self.update()
