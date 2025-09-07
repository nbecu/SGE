from PyQt5.QtWidgets import QCheckBox, QHBoxLayout, QLabel
from mainClasses.SGGameSpace import SGGameSpace
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true


class SGUserSelector(SGGameSpace):
    def __init__(self, parent, users):
        super().__init__(parent, 0, 60, 0, 0, true)
        self.model = parent
        self.users = users
        self.id = 'userSelector'
        self.initUI()

    def initUI(self):
        self.userLayout = QHBoxLayout()
        self.checkboxes = []
        title = QLabel("User Selector")
        font = QFont()
        font.setBold(True)
        title.setFont(font)
        self.userLayout.addWidget(title)
        self.updateUI(self.userLayout)
        self.setLayout(self.userLayout)
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
        
        # Fallback: calculate based on number of users
        if hasattr(self, 'users') and self.users:
            # Estimate width based on number of users and checkbox width
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
                # For horizontal layout, use layout height directly (no vertical gap needed)
                return max(size_hint.height(), 25)  # Reduced minimum height
        
        # Fallback: calculate based on checkbox height
        if hasattr(self, 'checkboxes') and self.checkboxes:
            # Use actual checkbox height if available
            checkbox_height = self.checkboxes[0].sizeHint().height() if self.checkboxes else 18
            return max(checkbox_height, 25)  # Reduced minimum height
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
        painter.setBrush(QBrush(self.gs_aspect.getBackgroundColorValue(), Qt.SolidPattern))
        painter.setPen(QPen(self.gs_aspect.getBorderColorValue(), self.gs_aspect.getBorderSize()))

        # Draw the corner of the US
        self.setMinimumSize(self.getSizeXGlobal()+15, self.getSizeYGlobal()+5)  # Reduced vertical padding
        painter.drawRect(0, 0, self.getSizeXGlobal(), self.getSizeYGlobal())

        painter.end()
