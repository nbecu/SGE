from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from mainClasses.SGIndicator import SGIndicator
from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell


# Class who is responsible of indicator creation
class SGEndGameCondition(QtWidgets.QWidget):
    def __init__(self, parent, name, entity, method, objective, attribut, color, calcType, isDisplay, delay_rounds=0, final_phase=None):
        super().__init__(parent)
        # Basic initialize
        self.endGameRule = parent
        self.method = method
        self.objective = objective
        self.calcType = calcType
        self.entity = entity
        self.name = name
        self.attribut = attribut
        self.color = color
        self.id = int
        self.checkStatus = False
        self.isDisplay = isDisplay
        # Trigger delay
        self.delay_rounds = delay_rounds  # Number of remaining rounds after the condition is met
        self.final_phase = final_phase  # Final phase: int (phase number), str (phase name or 'last phase'), or phase instance
        self.end_round = None  # Calculated round when the game should end
        self.end_phase = None  # Calculated phase number when the game should end
        self.initUI()

    def initUI(self):
        if self.isDisplay:
            self.conditionLayout = QtWidgets.QHBoxLayout()
            self.conditionLayout.setContentsMargins(0, 0, 0, 0)
            self.conditionLayout.setSpacing(6)
            # Status/check label (initially hidden)
            self.statusLabel = QtWidgets.QLabel("")
            self.statusLabel.setVisible(False)
            self.statusLabel.setStyleSheet("color: #2e7d32; font-weight: bold;")
            self.conditionLayout.addWidget(self.statusLabel)
            # Main text label
            self.label = QtWidgets.QLabel(self.name)
            # Enable word wrap if text is too long
            if len(self.name) > 50:  # Arbitrary threshold to decide on word wrapping
                self.label.setWordWrap(True)
            else:
                self.label.setWordWrap(False)
            # Do not force background on child label; container handles background in paintEvent
            self.label.setStyleSheet("border: none;")
            self.conditionLayout.addWidget(self.label)

    def updateText(self):
        self.verifStatus()
        if self.checkStatus:
            # Indicate validation with a green check mark label on the left
            color = self.endGameRule.success_aspect.color
            self.statusLabel.setText("✓")
            # Apply green from success aspect if available
            self.statusLabel.setStyleSheet(f"color: {color}; font-weight: bold;")
            self.statusLabel.setVisible(True)
        else:
            self.statusLabel.setVisible(False)
        # Ask parent to update its size from layout
        if hasattr(self.endGameRule, 'updateSizeFromLayout'):
            self.endGameRule.updateSizeFromLayout(self.endGameRule.layout)
        self.endGameRule.update()

    def getUpdatePermission(self):
        if self.endGameRule.displayRefresh == 'instantaneous':
            return True
        if self.endGameRule.displayRefresh == 'withButton':
            return True

    def getSizeXGlobal(self):
        # Prefer layout size if available
        if hasattr(self, 'conditionLayout') and self.conditionLayout:
            self.conditionLayout.activate()
            size_hint = self.conditionLayout.sizeHint()
            if size_hint.isValid():
                return size_hint.width() + 10
        # Fallback: include status label + text label
        width = 0
        if hasattr(self, 'statusLabel') and self.statusLabel:
            sh = self.statusLabel.sizeHint()
            if sh.isValid():
                width += sh.width() + 6
        if hasattr(self, 'label') and self.label:
            sh = self.label.sizeHint()
            if sh.isValid():
                width += sh.width()
        return max(width, 100)
    
    def getSizeYGlobal(self):
        # Prefer layout height if available
        if hasattr(self, 'conditionLayout') and self.conditionLayout:
            self.conditionLayout.activate()
            size_hint = self.conditionLayout.sizeHint()
            if size_hint.isValid():
                return size_hint.height() + 6
        # Fallback
        if hasattr(self, 'label') and self.label:
            sh = self.label.sizeHint()
            if sh.isValid():
                return sh.height() + 6
        return 25

    def byCalcType(self):
        condition_met = False
        
        if self.calcType == 'onIndicator':
            if isinstance(self.entity, SGIndicator):
                valueToCheck = self.entity.result
                if self.logicalTests(valueToCheck, self.method, self.objective):
                    condition_met = True
            else:
                print('Error, not an Indicator')
                return
        elif self.calcType == 'onEntity':
            if isinstance(self.entity, SGCell):
                valueToCheck = self.entity.dictAttributes[self.attribut]
                if type(valueToCheck) == str:
                    valueToCheck = int(valueToCheck)
                if self.logicalTests(valueToCheck, self.method, self.objective):
                    condition_met = True
            elif isinstance(self.entity, SGAgent):
                print("To be implemented...")
                return
        elif self.calcType == "onGameRound":
            valueToCheck = self.endGameRule.model.timeManager.currentRoundNumber
            if self.logicalTests(valueToCheck, self.method, self.objective):
                condition_met = True
        elif self.calcType == "onLambda":
            if callable(self.method):
                if self.method():
                    condition_met = True
            else:
                print("Error, method is not callable")
                return
        
        # If the condition is met for the first time, calculate the end round and phase
        if condition_met and self.end_round is None:
            timeManager = self.endGameRule.model.timeManager
            current_round = timeManager.currentRoundNumber
            current_phase = timeManager.currentPhaseNumber
            
            # Calculate end round: current round + delay_rounds
            self.end_round = current_round + self.delay_rounds
            
            # Calculate end phase number from final_phase parameter
            self.end_phase = self._convertFinalPhaseToPhaseNumber(timeManager, current_phase)
        
        # Check if we have reached the end round and phase
        if condition_met:
            if self.delay_rounds > 0:
                # Check if we have reached the calculated end round and phase
                if self.hasReachedEnd():
                    self.checkStatus = True
                else:
                    self.checkStatus = False
            else:
                # No delay, the condition is directly met
                self.checkStatus = True
        else:
            self.checkStatus = False
    
    def _convertFinalPhaseToPhaseNumber(self, timeManager, current_phase):
        """
        Converts final_phase parameter to a phase number.
        
        Args:
            timeManager: The time manager instance
            current_phase: Current phase number (used as default if final_phase is None)
            
        Returns:
            int: Phase number (1-indexed)
        """
        if self.final_phase is None or self.final_phase is False:
            # Default: use current phase
            return current_phase
        
        if isinstance(self.final_phase, int):
            # Direct phase number
            return self.final_phase
        
        if isinstance(self.final_phase, str):
            if self.final_phase.lower() == 'last phase':
                # Last phase of the round
                return timeManager.numberOfPhases()
            else:
                # Phase name: find phase by name
                for i, phase in enumerate(timeManager.phases, start=1):
                    if phase.name == self.final_phase:
                        return i
                # If not found, use current phase as fallback
                print(f"Warning: Phase '{self.final_phase}' not found, using current phase")
                return current_phase
        
        # Phase instance: find its index
        try:
            phase_index = timeManager.phases.index(self.final_phase)
            return phase_index + 1  # Convert to 1-indexed
        except ValueError:
            # If not found, use current phase as fallback
            print(f"Warning: Phase instance not found in phases list, using current phase")
            return current_phase
    
    def hasReachedEnd(self):
        """
        Checks if we have reached the calculated end round and phase.
        Returns True if the end round and phase have been reached, False otherwise.
        """
        if self.end_round is None or self.end_phase is None:
            return False
        
        timeManager = self.endGameRule.model.timeManager
        current_round = timeManager.currentRoundNumber
        current_phase = timeManager.currentPhaseNumber
        
        # Check if we have reached or passed the end round
        if current_round > self.end_round:
            return True
        elif current_round == self.end_round:
            # Same round, check if we have reached or passed the end phase
            return current_phase >= self.end_phase
        else:
            return False

    def logicalTests(self, valueToCheck, logicalTest, objective):
        if logicalTest == 'equal':
            if valueToCheck == objective:
                return True
        elif logicalTest == 'greater':
            if valueToCheck > objective:
                return True
        elif logicalTest == 'less':
            if valueToCheck < objective:
                return True
        elif logicalTest == 'greater or equal':
            if valueToCheck >= objective:
                return True
        elif logicalTest == 'less or equal':
            if valueToCheck <= objective:
                return True
        return False

    def verifStatus(self):
        self.byCalcType()