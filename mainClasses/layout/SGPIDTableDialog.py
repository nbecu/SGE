from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class SGPIDTableDialog(QDialog):
    """
    Dialog for editing gameSpace pIDs in Enhanced Grid Layout
    
    This dialog provides an editable table interface for managing
    pIDs of gameSpaces in the EGL system.
    """
    
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.original_pIDs = {}  # Store original pIDs for cancel functionality
        self.setupUI()
        self.populateTable()
        
    def setupUI(self):
        """Setup the user interface"""
        self.setWindowTitle("Enhanced Grid Layout - pID Management")
        self.setModal(True)
        self.resize(600, 400)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Edit the pID values to reorder gameSpaces in the Enhanced Grid Layout.\n"
            "pID determines the column and order of gameSpaces.\n"
            "You can also change the number of columns to reorganize the layout."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { padding: 10px; background-color: #f0f0f0; border-radius: 5px; }")
        layout.addWidget(instructions)
        
        # Column management section
        column_layout = QHBoxLayout()
        column_layout.addWidget(QLabel("Number of columns:"))
        
        self.column_spinbox = QSpinBox()
        self.column_spinbox.setMinimum(1)
        self.column_spinbox.setMaximum(10)
        self.column_spinbox.setValue(self.model.layoutOfModel.num_columns)
        # Don't connect immediately to avoid triggering during initialization
        # self.column_spinbox.valueChanged.connect(self.onColumnCountChanged)
        
        column_layout.addWidget(self.column_spinbox)
        column_layout.addStretch()
        
        layout.addLayout(column_layout)
        
        # Table widget
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Col", "GameSpace Type", "Name", "pID"])
        
        # Configure table
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Col
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # GameSpace Type
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)           # Name
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # pID
        
        # Set column widths
        self.table.setColumnWidth(0, 60)   # Col
        self.table.setColumnWidth(1, 150)  # GameSpace Type
        self.table.setColumnWidth(3, 80)   # pID
        
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Connect the signal after initialization is complete
        self.column_spinbox.valueChanged.connect(self.onColumnCountChanged)
        
    def onColumnCountChanged(self, new_count):
        """
        Handle column count change
        
        Args:
            new_count (int): New number of columns
        """
        # Update the layout's column count
        self.model.layoutOfModel.num_columns = new_count
        
        # Reorganize columns structure
        self.model.layoutOfModel.widgets = [[] for _ in range(new_count)]
        self.model.layoutOfModel.column_widths = [0] * new_count
        
        # Redistribute gameSpaces based on their pID
        for gs in self.model.gameSpaces.values():
            if not gs.isPositionDefineByModeler() and gs.pID is not None:
                column_index = (gs.pID - 1) % new_count
                self.model.layoutOfModel.widgets[column_index].append(gs)
        
        # Update the table to show which column each gameSpace will be in
        self.updateColumnPreview()
        
    def updateColumnPreview(self):
        """Update the table to show column preview"""
        for row in range(self.table.rowCount()):
            pid_item = self.table.item(row, 3)  # pID is now column 3
            if pid_item and pid_item.text().strip():
                try:
                    pid = int(pid_item.text())
                    column = (pid - 1) % self.model.layoutOfModel.num_columns
                    
                    # Update the column number column (column 0)
                    col_item = self.table.item(row, 0)
                    if col_item:
                        col_item.setText(str(column + 1))
                except ValueError:
                    pass
            else:
                # Clear column info for empty pIDs
                col_item = self.table.item(row, 0)
                if col_item:
                    col_item.setText("")
        
    def onPIDChanged(self, item):
        """Handle pID changes in the table"""
        if item.column() == 3:  # pID column is now column 3
            self.updateColumnPreview()
        
    def populateTable(self):
        """Populate the table with current gameSpaces and their pIDs"""
        if self.model.typeOfLayout != "enhanced_grid":
            return
            
        # Get gameSpaces that are not positioned by modeler
        gameSpaces = [gs for gs in self.model.gameSpaces.values() 
                     if not gs.isPositionDefineByModeler()]
        
        self.table.setRowCount(len(gameSpaces))
        
        for row, gameSpace in enumerate(gameSpaces):
            # Column number (calculated from pID) - Column 0
            column_number = ""
            if gameSpace.pID is not None:
                column_number = str((gameSpace.pID - 1) % self.model.layoutOfModel.num_columns + 1)
            
            col_item = QTableWidgetItem(column_number)
            col_item.setFlags(col_item.flags() & ~Qt.ItemIsEditable)
            col_item.setTextAlignment(Qt.AlignCenter)
            col_item.setBackground(QColor(240, 240, 240))
            self.table.setItem(row, 0, col_item)
            
            # GameSpace Type (clean, without column info) - Column 1
            type_item = QTableWidgetItem(gameSpace.__class__.__name__)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            type_item.setBackground(QColor(240, 240, 240))
            self.table.setItem(row, 1, type_item)
            
            # Name - Column 2
            name_item = QTableWidgetItem(gameSpace.id)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            name_item.setBackground(QColor(240, 240, 240))
            self.table.setItem(row, 2, name_item)
            
            # pID (editable) - Column 3
            pid_item = QTableWidgetItem(str(gameSpace.pID or ""))
            pid_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, pid_item)
            
            # Store original pID for cancel functionality
            self.original_pIDs[gameSpace.id] = gameSpace.pID
            
            # Connect pID changes to update column preview (only once)
            if row == 0:  # Only connect once
                self.table.itemChanged.connect(self.onPIDChanged)
            
    def getPIDChanges(self):
        """Get the pID changes made in the table"""
        changes = {}
        
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 2)  # Name is now column 2
            pid_item = self.table.item(row, 3)    # pID is now column 3
            
            if name_item and pid_item:
                name = name_item.text()
                try:
                    new_pid = int(pid_item.text()) if pid_item.text().strip() else None
                    original_pid = self.original_pIDs.get(name)
                    
                    if new_pid != original_pid:
                        changes[name] = new_pid
                except ValueError:
                    # Invalid pID, will be handled by validation
                    pass
                    
        return changes
        
    def validatePIDChanges(self, changes):
        """
        Validate all pID changes together to detect conflicts
        
        Args:
            changes: dict of {name: new_pid}
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Collect all new pIDs
        new_pids = []
        for name, new_pid in changes.items():
            if new_pid is not None:
                new_pids.append(new_pid)
        
        # Check for duplicates
        if len(new_pids) != len(set(new_pids)):
            return False, "Duplicate pIDs detected. Please ensure all pIDs are unique."
        
        # Check for conflicts with existing pIDs (excluding the ones being changed)
        existing_pids = set()
        for gs in self.model.gameSpaces.values():
            if not gs.isPositionDefineByModeler():
                if gs.id not in changes:  # Not being modified
                    if gs.pID is not None:
                        existing_pids.add(gs.pID)
        
        # Check if any new pID conflicts with existing ones
        conflicts = set(new_pids) & existing_pids
        if conflicts:
            return False, f"pIDs {sorted(conflicts)} are already in use by other gameSpaces."
        
        return True, ""
    
    def accept(self):
        """Apply changes and close dialog"""
        changes = self.getPIDChanges()
        
        # Validate all changes together
        is_valid, error_message = self.validatePIDChanges(changes)
        if not is_valid:
            QMessageBox.warning(self, "Invalid pIDs", error_message)
            return
        
        # Apply changes to gameSpaces (now safe to apply)
        for name, new_pid in changes.items():
            # Find gameSpace by id (which is the name in the table)
            gameSpace = None
            for gs in self.model.gameSpaces.values():
                if gs.id == name:
                    gameSpace = gs
                    break
            
            if gameSpace:
                if new_pid is not None:
                    # Direct assignment without conflict checking (already validated)
                    old_pid = gameSpace.pID
                    gameSpace.pID = new_pid
                    gameSpace._egl_pid_manual = True
                    
                    # Update tracking in layout
                    if old_pid is not None:
                        self.model.layoutOfModel.used_pIDs.discard(old_pid)
                    self.model.layoutOfModel.used_pIDs.add(new_pid)
                else:
                    # Reset to auto-assignment
                    if gameSpace.pID is not None:
                        self.model.layoutOfModel.used_pIDs.discard(gameSpace.pID)
                    gameSpace.pID = None
                    gameSpace._egl_pid_manual = False
                
        # Reorder EGL layout
        gameSpaces_to_reorder = [gs for gs in self.model.gameSpaces.values() 
                               if not gs.isPositionDefineByModeler()]
        self.model.layoutOfModel.reorderByPID(gameSpaces_to_reorder)
        self.model.applyEnhancedGridLayout()
        
        super().accept()
        
    def reject(self):
        """Cancel changes and close dialog"""
        super().reject()
