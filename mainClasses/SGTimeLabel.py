from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true

from mainClasses.SGGameSpace import SGGameSpace


class SGTimeLabel(SGGameSpace):
    def __init__(self, parent, title, backgroundColor=Qt.white, borderColor=Qt.black, textColor=Qt.black,
                 roundNumberFormat="Round Number : {roundNumber}",
                 phaseNumberFormat="Phase Number : {phaseNumber}",
                 phaseNameFormat="{phaseName}",
                 displayRoundNumber=None,
                 displayPhaseNumber=None,
                 displayPhaseName=None):
        super().__init__(parent, 0, 60, 0, 0, true, backgroundColor)
        self.id = title
        self.timeManager = self.model.timeManager
        self.gs_aspect.border_color = borderColor
        self.setTitlesAndTextsColor(textColor)
        self.moveable = True
        self.textTitle  = title
        self.displayTitle = self.textTitle is not None
        
        # Stocker les formats de template
        self.roundNumberFormat = roundNumberFormat
        self.phaseNumberFormat = phaseNumberFormat
        self.phaseNameFormat = phaseNameFormat
        
        # Définir les valeurs par défaut pour l'affichage si non spécifiées
        if displayRoundNumber is None:
            self.displayRoundNumber = True
        else:
            self.displayRoundNumber = displayRoundNumber
            
        if displayPhaseNumber is None:
            self.displayPhaseNumber = self.timeManager.numberOfPhases() >= 2
        else:
            self.displayPhaseNumber = displayPhaseNumber
            
        if displayPhaseName is None:
            self.displayPhaseName = self.timeManager.numberOfPhases() >= 2
        else:
            self.displayPhaseName = displayPhaseName
        
        # Si le format est None ou vide, ne pas afficher le label correspondant
        if not self.roundNumberFormat or self.roundNumberFormat.strip() == "":
            self.displayRoundNumber = False
        if not self.phaseNumberFormat or self.phaseNumberFormat.strip() == "":
            self.displayPhaseNumber = False
        if not self.phaseNameFormat or self.phaseNameFormat.strip() == "":
            self.displayPhaseName = False

        self.initLabels()

    
    def initLabels(self):
        self.labels =[]
 
        if self.displayTitle:
            self.labelTitle = QtWidgets.QLabel(self)
            self.labelTitle.setText(self.textTitle)
            self.labels.append(self.labelTitle)
        if self.displayRoundNumber:
            self.labelRoundNumber = QtWidgets.QLabel(self)
            self.labelRoundNumber.setText('Not yet started')
            self.labels.append(self.labelRoundNumber)
        if self.displayPhaseNumber:
            self.labelPhaseNumber = QtWidgets.QLabel(self)
            self.labels.append(self.labelPhaseNumber)
        if self.displayPhaseName:
            self.labelPhaseName = QtWidgets.QLabel(self)
            self.labels.append(self.labelPhaseName)

        for aLabel in self.labels:
            aLabel.setStyleSheet(self.text1_aspect.getTextStyle())
        if self.displayTitle:
            self.labelTitle.setStyleSheet(self.title1_aspect.getTextStyle())

        # Créer un layout vertical
        layout = QtWidgets.QVBoxLayout()
        for aLabel in self.labels:
            layout.addWidget(aLabel)
        self.setLayout(layout)

        self.show()
        self.updateLabelsandWidgetSize()


    def paintEvent(self, event):
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
        # Pen with style
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
        # Rounded rect if radius provided
        radius = getattr(self.gs_aspect, 'border_radius', None) or 0
        w = max(0, self.getSizeXGlobal() - 1)
        h = max(0, self.getSizeYGlobal() - 1)
        if radius > 0:
            painter.drawRoundedRect(0, 0, w, h, radius, radius)
        else:
            painter.drawRect(0, 0, w, h)

    def onTextAspectsChanged(self):
        """Reapply text styles from current aspects to labels and resize."""
        from mainClasses.SGExtensions import mapAlignmentStringToQtFlags
        
        # Apply text1_aspect to non-title labels
        for aLabel in getattr(self, 'labels', []) or []:
            # Apply font properties
            f = aLabel.font()
            self.text1_aspect.applyToQFont(f, self)
            aLabel.setFont(f)
            # Apply stylesheet for color and text decoration
            stylesheet = self.text1_aspect.getStyleSheetForColorAndDecoration()
            if stylesheet:
                aLabel.setStyleSheet(stylesheet)
            # Alignment from text1_aspect
            al = getattr(self.text1_aspect, 'alignment', None)
            if isinstance(al, str) and al:
                qt_alignment = mapAlignmentStringToQtFlags(al)
                if qt_alignment is not None:
                    aLabel.setAlignment(qt_alignment)
        # Apply title1_aspect to title if present
        if getattr(self, 'displayTitle', False) and hasattr(self, 'labelTitle') and self.labelTitle:
            # Apply font properties
            f = self.labelTitle.font()
            self.title1_aspect.applyToQFont(f, self)
            self.labelTitle.setFont(f)
            # Apply stylesheet for color and text decoration
            stylesheet = self.title1_aspect.getStyleSheetForColorAndDecoration()
            if stylesheet:
                self.labelTitle.setStyleSheet(stylesheet)
            # Alignment from title1_aspect
            al = getattr(self.title1_aspect, 'alignment', None)
            if isinstance(al, str) and al:
                qt_alignment = mapAlignmentStringToQtFlags(al)
                if qt_alignment is not None:
                    self.labelTitle.setAlignment(qt_alignment)
        self.updateLabelsandWidgetSize()
        self.update()

    # Override to prevent container QSS from interfering; rely solely on paintEvent
    def applyContainerAspectStyle(self):
        pass

    def updateTimeLabel(self):
        # Obtenir les valeurs actuelles
        current_round = self.timeManager.currentRoundNumber
        current_phase_number = self.timeManager.currentPhaseNumber
        current_phase_name = self.timeManager.getCurrentPhase().name
        
        # Mettre à jour le label du round number
        if self.displayRoundNumber and hasattr(self, 'labelRoundNumber') and self.labelRoundNumber:
            try:
                text = self.roundNumberFormat.format(
                    roundNumber=current_round,
                    phaseNumber=current_phase_number,
                    phaseName=current_phase_name
                )
                self.labelRoundNumber.setText(text)
            except (KeyError, ValueError) as e:
                # En cas d'erreur de formatage, utiliser un format simple
                self.labelRoundNumber.setText(str(current_round))
        
        # Mettre à jour le label du phase number
        if self.displayPhaseNumber and hasattr(self, 'labelPhaseNumber') and self.labelPhaseNumber:
            try:
                text = self.phaseNumberFormat.format(
                    roundNumber=current_round,
                    phaseNumber=current_phase_number,
                    phaseName=current_phase_name
                )
                self.labelPhaseNumber.setText(text)
            except (KeyError, ValueError) as e:
                # En cas d'erreur de formatage, utiliser un format simple
                self.labelPhaseNumber.setText(str(current_phase_number))
        
        # Mettre à jour le label du phase name
        if self.displayPhaseName and hasattr(self, 'labelPhaseName') and self.labelPhaseName:
            try:
                text = self.phaseNameFormat.format(
                    roundNumber=current_round,
                    phaseNumber=current_phase_number,
                    phaseName=current_phase_name
                )
                self.labelPhaseName.setText(text)
            except (KeyError, ValueError) as e:
                # En cas d'erreur de formatage, utiliser le nom de la phase directement
                self.labelPhaseName.setText(current_phase_name)

        self.updateLabelsandWidgetSize()


    def updateLabelsandWidgetSize(self):
        # Recalculer les dimensions en fonction du texte et du styleSheet utilisé dans les QLabel
        for aLabel in self.labels:
            aLabel.setFixedWidth(aLabel.fontMetrics().boundingRect(aLabel.text()).width())
            aLabel.setFixedHeight(aLabel.fontMetrics().boundingRect(aLabel.text()).height())
            aLabel.adjustSize()
        
        max_right = max(aLabel.geometry().right() for aLabel in self.labels)
        max_bottom = max(aLabel.geometry().bottom() for aLabel in self.labels)
        
        self.sizeXGlobal = max_right +self.rightMargin
        self.setFixedSize(QSize(self.getSizeXGlobal() , self.getSizeYGlobal()))
    

    def getSizeXGlobal(self):
        return self.sizeXGlobal
    
    
    def getSizeYGlobal(self):
        somme = 10
        for label in self.labels:
            somme += label.height()  + self.verticalGapBetweenLabels
        return somme

    # ============================================================================
    # MODELER METHODS
    # ============================================================================
    
    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================
    
    def setTitleText(self, text):
        """
        Set the title text of the time label.
        
        Args:
            text (str): The title text
        """
        self.textTitle = text
        if hasattr(self, 'labelTitle') and self.labelTitle:
            self.labelTitle.setText(text)
            self.labelTitle.adjustSize()
        self.updateLabelsandWidgetSize()
        self.update()
        
    def setDisplayTitle(self, display):
        """
        Set whether to display the title.
        
        Args:
            display (bool): Whether to display the title
        """
        self.displayTitle = display
        if hasattr(self, 'labelTitle') and self.labelTitle:
            self.labelTitle.setVisible(display)
        self.updateLabelsandWidgetSize()
        self.update()
        
    def setDisplayRoundNumber(self, display):
        """
        Set whether to display the round number.
        
        Args:
            display (bool): Whether to display the round number
        """
        self.displayRoundNumber = display
        if hasattr(self, 'labelRoundNumber') and self.labelRoundNumber:
            self.labelRoundNumber.setVisible(display)
        self.updateLabelsandWidgetSize()
        self.update()
        
    def setDisplayPhaseNumber(self, display):
        """
        Set whether to display the phase number.
        
        Args:
            display (bool): Whether to display the phase number
        """
        self.displayPhaseNumber = display
        if hasattr(self, 'labelPhaseNumber') and self.labelPhaseNumber:
            self.labelPhaseNumber.setVisible(display)
        self.updateLabelsandWidgetSize()
        self.update()
        
    def setDisplayPhaseName(self, display):
        """
        Set whether to display the phase name.
        
        Args:
            display (bool): Whether to display the phase name
        """
        self.displayPhaseName = display
        if hasattr(self, 'labelPhaseName') and self.labelPhaseName:
            self.labelPhaseName.setVisible(display)
        self.updateLabelsandWidgetSize()
        self.update()
        
    def setLabelStyle(self, style_dict):
        """
        Set the style of all labels.
        
        Args:
            style_dict (dict): Dictionary of style properties for labels
        """
        for label in self.labels:
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
                label.setStyleSheet("; ".join(style_parts))
        self.updateLabelsandWidgetSize()
        self.update()
    
    def setRoundNumberFormat(self, format_string):
        """
        Set the format template for the round number label.
        
        Args:
            format_string (str): Format string using placeholders {roundNumber}, {phaseNumber}, {phaseName}
                                If None or empty, the round number label will be hidden.
        """
        self.roundNumberFormat = format_string
        if not format_string or format_string.strip() == "":
            self.setDisplayRoundNumber(False)
        else:
            # Si le label n'existe pas encore mais qu'on veut l'afficher maintenant
            if not hasattr(self, 'labelRoundNumber') or not self.labelRoundNumber:
                self.displayRoundNumber = True
                # Il faudrait recréer les labels, mais pour l'instant on attend updateTimeLabel
            self.updateTimeLabel()
    
    def setPhaseNumberFormat(self, format_string):
        """
        Set the format template for the phase number label.
        
        Args:
            format_string (str): Format string using placeholders {roundNumber}, {phaseNumber}, {phaseName}
                                If None or empty, the phase number label will be hidden.
        """
        self.phaseNumberFormat = format_string
        if not format_string or format_string.strip() == "":
            self.setDisplayPhaseNumber(False)
        else:
            # Si le label n'existe pas encore mais qu'on veut l'afficher maintenant
            if not hasattr(self, 'labelPhaseNumber') or not self.labelPhaseNumber:
                self.displayPhaseNumber = True
            self.updateTimeLabel()
    
    def setPhaseNameFormat(self, format_string):
        """
        Set the format template for the phase name label.
        
        Args:
            format_string (str): Format string using placeholders {roundNumber}, {phaseNumber}, {phaseName}
                                If None or empty, the phase name label will be hidden.
        """
        self.phaseNameFormat = format_string
        if not format_string or format_string.strip() == "":
            self.setDisplayPhaseName(False)
        else:
            # Si le label n'existe pas encore mais qu'on veut l'afficher maintenant
            if not hasattr(self, 'labelPhaseName') or not self.labelPhaseName:
                self.displayPhaseName = True
            self.updateTimeLabel()