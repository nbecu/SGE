from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class SGLayoutOrderTableDialog(QDialog):
    """
    Dialog for editing gameSpace layoutOrders in Enhanced Grid Layout
    
    This dialog provides an editable table interface for managing
    layoutOrders of gameSpaces in the EGL system.
    """
    
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.original_layoutOrders = {}  # Store original layoutOrders for cancel functionality
        
        # OPTIMIZATION: Create cache of gameSpaces for O(1) lookup
        self.gameSpaces_cache = {gs.id: gs for gs in self.model.gameSpaces.values()}
        
        self.setupUI()
        self.populateTable()
        
    def setupUI(self):
        """Setup the user interface"""
        self.setWindowTitle("Enhanced Grid Layout - layoutOrder Management")
        self.setModal(True)
        self.resize(600, 400)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Edit the layoutOrder values to reorder gameSpaces in the Enhanced Grid Layout.\n"
            "layoutOrder determines the column and order of gameSpaces.\n"
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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Col", "GameSpace Type", "Name", "Position Type", "Order", "Actions"])
        
        # Configure table
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Col
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # GameSpace Type
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)           # Name
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Position Type
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Order
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Actions
        
        # Set column widths
        self.table.setColumnWidth(0, 60)   # Col
        self.table.setColumnWidth(1, 150)  # GameSpace Type
        self.table.setColumnWidth(3, 120)  # Position Type
        self.table.setColumnWidth(4, 80)   # Order
        self.table.setColumnWidth(5, 150) # Actions
        
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
        
        # Redistribute gameSpaces based on their layoutOrder
        # OPTIMIZATION: Use cache instead of repeated access
        for gs in self.gameSpaces_cache.values():
            if not gs.isPositionDefineByModeler() and gs.layoutOrder is not None:
                column_index = (gs.layoutOrder - 1) % new_count
                self.model.layoutOfModel.widgets[column_index].append(gs)
        
        # Update the table to show which column each gameSpace will be in
        self.updateColumnPreview()
        
    def updateColumnPreview(self):
        """Update the table to show column preview"""
        for row in range(self.table.rowCount()):
            layoutOrder_item = self.table.item(row, 4)  # Order is now column 4
            if layoutOrder_item and layoutOrder_item.text().strip():
                layoutOrder_text = layoutOrder_item.text().strip()
                
                # Skip "Fixed" and other non-numeric values
                if layoutOrder_text == "Fixed" or layoutOrder_text == "":
                    continue
                    
                try:
                    layoutOrder = int(layoutOrder_text)
                    column = (layoutOrder - 1) % self.model.layoutOfModel.num_columns
                    
                    # Update the column number column (column 0)
                    col_item = self.table.item(row, 0)
                    if col_item:
                        col_item.setText(str(column + 1))
                except ValueError:
                    pass
            else:
                # Clear column info for empty layoutOrders
                col_item = self.table.item(row, 0)
                if col_item:
                    col_item.setText("")
        
    def onLayoutOrderChanged(self, item):
        """Handle layoutOrder changes in the table"""
        if item.column() == 4:  # Order column is now column 4
            self.updateColumnPreview()
        
    def populateTable(self):
        """Populate the table with current gameSpaces and their layoutOrders"""
        if self.model.typeOfLayout != "enhanced_grid":
            return
            
        # Get all gameSpaces (including those positioned by modeler)
        # OPTIMIZATION: Use cache instead of repeated access
        gameSpaces = list(self.gameSpaces_cache.values())
        
        self.table.setRowCount(len(gameSpaces))
        
        for row, gameSpace in enumerate(gameSpaces):
            # Initialize enhanced grid manual flag if not set
            if not hasattr(gameSpace, 'is_layout_repositioned'):
                if gameSpace.isPositionDefineByModeler() or gameSpace.layoutOrder == "manual_position":
                    gameSpace.is_layout_repositioned = True
                else:
                    gameSpace.is_layout_repositioned = False
            
            # Column number (calculated from layoutOrder) - Column 0
            column_number = ""
            if gameSpace.layoutOrder is not None and isinstance(gameSpace.layoutOrder, int):
                column_number = str((gameSpace.layoutOrder - 1) % self.model.layoutOfModel.num_columns + 1)
            elif gameSpace.layoutOrder == "manual_position":
                column_number = "Fixed"
            elif gameSpace.isPositionDefineByModeler():
                column_number = "Manual"
            
            col_item = QTableWidgetItem(column_number)
            col_item.setFlags(col_item.flags() & ~Qt.ItemIsEditable)
            col_item.setTextAlignment(Qt.AlignCenter)
            col_item.setBackground(QColor(240, 240, 240))
            self.table.setItem(row, 0, col_item)
            
            # GameSpace Type - Column 1
            type_item = QTableWidgetItem(gameSpace.__class__.__name__)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            type_item.setBackground(QColor(240, 240, 240))
            self.table.setItem(row, 1, type_item)
            
            # Name - Column 2
            name_item = QTableWidgetItem(gameSpace.id)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            name_item.setBackground(QColor(240, 240, 240))
            self.table.setItem(row, 2, name_item)
            
            # Position Type - Column 3
            position_type = self._detectPositionType(gameSpace)
            position_type_item = QTableWidgetItem(position_type)
            position_type_item.setFlags(position_type_item.flags() & ~Qt.ItemIsEditable)
            position_type_item.setTextAlignment(Qt.AlignCenter)
            position_type_item.setBackground(QColor(240, 240, 240))
            
            # Color code position types
            if position_type == "Absolute":
                position_type_item.setBackground(QColor(255, 200, 200))  # Light red
            elif position_type == "Mixed":
                position_type_item.setBackground(QColor(255, 255, 200))  # Light yellow
            else:  # Layout Order
                position_type_item.setBackground(QColor(200, 255, 200))  # Light green
            
            self.table.setItem(row, 3, position_type_item)
            
            # Order - Column 4
            layoutOrder_display = ""
            if position_type == "Absolute":
                layoutOrder_display = "Fixed"
            elif gameSpace.layoutOrder is not None:
                layoutOrder_display = str(gameSpace.layoutOrder)
            
            layoutOrder_item = QTableWidgetItem(layoutOrder_display)
            layoutOrder_item.setTextAlignment(Qt.AlignCenter)
            if position_type == "Absolute":
                layoutOrder_item.setFlags(layoutOrder_item.flags() & ~Qt.ItemIsEditable)
                layoutOrder_item.setBackground(QColor(240, 240, 240))
            self.table.setItem(row, 4, layoutOrder_item)
            
            # Actions - Column 5
            actions_widget = self._createActionsWidget(gameSpace, row)
            self.table.setCellWidget(row, 5, actions_widget)
            
            # Store original layoutOrder for cancel functionality
            self.original_layoutOrders[gameSpace.id] = gameSpace.layoutOrder
            
            # Connect layoutOrder changes to update column preview (only once)
            if row == 0:  # Only connect once
                self.table.itemChanged.connect(self.onLayoutOrderChanged)
            
    def getLayoutOrderChanges(self):
        """Get the layoutOrder changes made in the table"""
        changes = {}
        
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 2)  # Name is column 2
            layoutOrder_item = self.table.item(row, 4)    # Order is column 4
            
            if name_item and layoutOrder_item:
                name = name_item.text()
                try:
                    order_text = layoutOrder_item.text().strip()
                    if order_text == "Fixed":
                        # GameSpace is in absolute mode, no layoutOrder change needed
                        new_layoutOrder = None
                    else:
                        new_layoutOrder = int(order_text) if order_text else None
                    
                    original_layoutOrder = self.original_layoutOrders.get(name)
                    
                    if new_layoutOrder != original_layoutOrder:
                        changes[name] = new_layoutOrder
                except ValueError:
                    # Invalid layoutOrder, will be handled by validation
                    pass
                    
        return changes
        
    def validateLayoutOrderChanges(self, changes):
        """
        Validate all layoutOrder changes together to detect conflicts
        
        Args:
            changes: dict of {name: new_layoutOrder}
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Collect all new layoutOrders
        new_layoutOrders = []
        for name, new_layoutOrder in changes.items():
            if new_layoutOrder is not None:
                new_layoutOrders.append(new_layoutOrder)
        
        # Check for duplicates
        if len(new_layoutOrders) != len(set(new_layoutOrders)):
            return False, "Duplicate layoutOrders detected. Please ensure all layoutOrders are unique."
        
        # Check for conflicts with existing layoutOrders (excluding the ones being changed)
        # OPTIMIZATION: Collect existing layoutOrders in one pass using cache
        existing_layoutOrders = set()
        for gs in self.gameSpaces_cache.values():
            if not gs.isPositionDefineByModeler():
                if gs.id not in changes:  # Not being modified
                    if gs.layoutOrder is not None:
                        existing_layoutOrders.add(gs.layoutOrder)
        
        # Check if any new layoutOrder conflicts with existing ones
        conflicts = set(new_layoutOrders) & existing_layoutOrders
        if conflicts:
            return False, f"layoutOrders {sorted(conflicts)} are already in use by other gameSpaces."
        
        return True, ""
    
    def accept(self):
        """Apply changes and close dialog"""
        changes = self.getLayoutOrderChanges()
        
        # Validate all changes together
        is_valid, error_message = self.validateLayoutOrderChanges(changes)
        if not is_valid:
            QMessageBox.warning(self, "Invalid layoutOrders", error_message)
            return
        
        # Apply changes to gameSpaces (now safe to apply)
        for name, new_layoutOrder in changes.items():
            # OPTIMIZATION: Use cache for O(1) lookup instead of O(n) linear search
            gameSpace = self.gameSpaces_cache.get(name)
            
            if gameSpace:
                if new_layoutOrder is not None:
                    # Direct assignment without conflict checking (already validated)
                    old_layoutOrder = gameSpace.layoutOrder
                    gameSpace.layoutOrder = new_layoutOrder
                    
                    # The is_layout_repositioned flag should already be set correctly
                    # by the switchToLayoutOrder/switchToAbsolute methods
                    # Don't override it here
                    
                    # Update tracking in layout
                    if old_layoutOrder is not None:
                        self.model.layoutOfModel.used_layoutOrders.discard(old_layoutOrder)
                    self.model.layoutOfModel.used_layoutOrders.add(new_layoutOrder)
                else:
                    # Reset to auto-assignment
                    if gameSpace.layoutOrder is not None:
                        self.model.layoutOfModel.used_layoutOrders.discard(gameSpace.layoutOrder)
                    gameSpace.layoutOrder = None
                    gameSpace.is_layout_repositioned = False
        
        # Ensure all gameSpaces that were switched to Absolute mode are properly persisted
        # OPTIMIZATION: Use cache instead of repeated access
        for gameSpace in self.gameSpaces_cache.values():
            if gameSpace.layoutOrder == "manual_position":
                # Ensure positionDefineByModeler is set for absolute mode
                if not hasattr(gameSpace, 'positionDefineByModeler') or gameSpace.positionDefineByModeler is None:
                    # Set current position as the modeler-defined position
                    gameSpace.positionDefineByModeler = [gameSpace.x(), gameSpace.y()]
                
        # Reorder EGL layout
        # Include all gameSpaces that have a numeric layoutOrder (including those switched from manual)
        # OPTIMIZATION: Use cache instead of repeated access
        gameSpaces_to_reorder = [gs for gs in self.gameSpaces_cache.values() 
                                if isinstance(gs.layoutOrder, int)]
        self.model.layoutOfModel.reorderByLayoutOrder(gameSpaces_to_reorder)
        
        # Only apply automatic layout to gameSpaces that are in layoutOrder mode (not mixed or absolute)
        # OPTIMIZATION: Use cache instead of repeated access
        gameSpaces_for_layout = [gs for gs in self.gameSpaces_cache.values() 
                                if gs.getPositionType() == "layoutOrder"]
        self.model.layoutOfModel.applyLayout(gameSpaces_for_layout)
        
        super().accept()
        
    def reject(self):
        """Cancel changes and close dialog"""
        super().reject()
    
    def _detectPositionType(self, gameSpace):
        """
        Get the position type of a gameSpace.
        
        Args:
            gameSpace: The gameSpace to analyze
            
        Returns:
            str: "Absolute", "Mixed", or "Layout Order"
        """
        # Use the explicit state instead of complex detection logic
        position_type = gameSpace.getPositionType()
        
        # Convert to display format
        if position_type == "absolute":
            return "Absolute"
        elif position_type == "mixed":
            return "Mixed"
        else:  # layoutOrder
            return "Layout Order"
    
    
    def _createActionsWidget(self, gameSpace, row):
        """
        Create actions widget for a gameSpace.
        
        Args:
            gameSpace: The gameSpace to create actions for
            row: The table row number
            
        Returns:
            QWidget: Widget containing action buttons
        """
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        
        position_type = self._detectPositionType(gameSpace)
        
        if position_type == "Absolute":
            # Show "Switch to Layout Order" button
            switch_btn = QPushButton("To Layout Order")
            switch_btn.setMaximumHeight(25)
            switch_btn.clicked.connect(lambda: self.switchToLayoutOrder(gameSpace, row))
            layout.addWidget(switch_btn)
        elif position_type == "Layout Order":
            # Show "Switch to Absolute" button
            switch_btn = QPushButton("To Absolute")
            switch_btn.setMaximumHeight(25)
            switch_btn.clicked.connect(lambda: self.switchToAbsolute(gameSpace, row))
            layout.addWidget(switch_btn)
        else:  # Mixed
            # Show both buttons
            to_layout_btn = QPushButton("To Layout Order")
            to_layout_btn.setMaximumHeight(25)
            to_layout_btn.clicked.connect(lambda: self.switchToLayoutOrder(gameSpace, row))
            
            to_absolute_btn = QPushButton("To Absolute")
            to_absolute_btn.setMaximumHeight(25)
            to_absolute_btn.clicked.connect(lambda: self.switchToAbsolute(gameSpace, row))
            
            layout.addWidget(to_layout_btn)
            layout.addWidget(to_absolute_btn)
        
        widget.setLayout(layout)
        return widget
    
    def switchToLayoutOrder(self, gameSpace, row):
        """
        Switch a gameSpace from absolute to layoutOrder positioning.
        
        Args:
            gameSpace: The gameSpace to switch
            row: The table row number
        """
        # For mixed gameSpaces, try to restore their original layoutOrder
        if gameSpace.getPositionType() == "mixed" and isinstance(gameSpace.layoutOrder, int):
            original_order = gameSpace.layoutOrder
            # Check if the original order is still available
            used_orders = set()
            # OPTIMIZATION: Use cache instead of repeated access
            for gs in self.gameSpaces_cache.values():
                if gs != gameSpace and gs.layoutOrder is not None and isinstance(gs.layoutOrder, int):
                    used_orders.add(gs.layoutOrder)
            
            if original_order not in used_orders:
                # Original order is available, restore it
                optimal_order = original_order
            else:
                # Original order is taken, find next available
                optimal_order = self._calculateOptimalLayoutOrder(gameSpace)
        else:
            # For absolute gameSpaces, calculate optimal layoutOrder
            optimal_order = self._calculateOptimalLayoutOrder(gameSpace)
        
        # Set to layout order mode using the new method
        gameSpace.setToLayoutOrder(optimal_order)
        
        # Update the table
        self._updateTableRow(row, gameSpace)
        
        # Update column preview
        self.updateColumnPreview()
    
    def switchToAbsolute(self, gameSpace, row):
        """
        Switch a gameSpace from layoutOrder to absolute positioning.
        
        Args:
            gameSpace: The gameSpace to switch
            row: The table row number
        """
        # Save current position
        current_pos = (gameSpace.x(), gameSpace.y())
        
        # Set to absolute mode using the new method
        gameSpace.setToAbsolute()
        
        # Ensure position is maintained
        gameSpace.move(current_pos[0], current_pos[1])
        
        # Update the table
        self._updateTableRow(row, gameSpace)
    
    def _calculateOptimalLayoutOrder(self, gameSpace):
        """
        Calculate optimal layoutOrder based on current position.
        
        Args:
            gameSpace: The gameSpace to calculate for
            
        Returns:
            int: Optimal layoutOrder
        """
        # Simple heuristic: find next available layoutOrder
        used_orders = set()
        # OPTIMIZATION: Use cache instead of repeated access
        for gs in self.gameSpaces_cache.values():
            if gs.layoutOrder is not None and isinstance(gs.layoutOrder, int):
                used_orders.add(gs.layoutOrder)
        
        # Find next available order
        order = 1
        while order in used_orders:
            order += 1
        
        return order
    
    def _updateTableRow(self, row, gameSpace):
        """
        Update a table row after position type change.
        
        Args:
            row: The table row number
            gameSpace: The gameSpace to update
        """
        # Update column number
        column_number = ""
        if gameSpace.layoutOrder is not None and isinstance(gameSpace.layoutOrder, int):
            column_number = str((gameSpace.layoutOrder - 1) % self.model.layoutOfModel.num_columns + 1)
        elif gameSpace.layoutOrder == "manual_position":
            column_number = "Fixed"
        elif gameSpace.isPositionDefineByModeler():
            column_number = "Manual"
        
        col_item = self.table.item(row, 0)
        if col_item:
            col_item.setText(column_number)
        
        # Update position type
        position_type = self._detectPositionType(gameSpace)
        position_type_item = self.table.item(row, 3)
        if position_type_item:
            position_type_item.setText(position_type)
            
            # Update color
            if position_type == "Absolute":
                position_type_item.setBackground(QColor(255, 200, 200))
            elif position_type == "Mixed":
                position_type_item.setBackground(QColor(255, 255, 200))
            else:
                position_type_item.setBackground(QColor(200, 255, 200))
        
        # Update order
        layoutOrder_display = ""
        if gameSpace.layoutOrder == "manual_position":
            layoutOrder_display = "Fixed"
        elif gameSpace.layoutOrder is not None:
            layoutOrder_display = str(gameSpace.layoutOrder)
        
        layoutOrder_item = self.table.item(row, 4)
        if layoutOrder_item:
            layoutOrder_item.setText(layoutOrder_display)
            if gameSpace.layoutOrder == "manual_position" or gameSpace.isPositionDefineByModeler():
                layoutOrder_item.setFlags(layoutOrder_item.flags() & ~Qt.ItemIsEditable)
                layoutOrder_item.setBackground(QColor(240, 240, 240))
            else:
                layoutOrder_item.setFlags(layoutOrder_item.flags() | Qt.ItemIsEditable)
                layoutOrder_item.setBackground(QColor(255, 255, 255))
        
        # Update actions widget
        actions_widget = self._createActionsWidget(gameSpace, row)
        self.table.setCellWidget(row, 5, actions_widget)
