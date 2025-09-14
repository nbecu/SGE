from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from mainClasses.layout.SGAbstractLayout import SGAbstractLayout


class SGEnhancedGridLayout(SGAbstractLayout):
    """
    Enhanced Grid Layout (EGL) for SGE gameSpaces
    
    This layout implements a staggered column-based organization system that:
    1. Organizes gameSpaces in columns automatically
    2. Records calculated positions
    3. Releases the structured layout
    4. Allows free positioning while maintaining organization capability
    
    Based on the EGL architecture from the external project, adapted for SGE.
    """
    
    def __init__(self, num_columns=3):
        super().__init__()
        self.num_columns = num_columns
        # Structure: list of columns, each column contains gameSpaces
        self.widgets = [[] for _ in range(num_columns)]
        # Track column widths for proper sizing
        self.column_widths = [0] * num_columns
        
        # EGL layoutOrder system
        self.next_layoutOrder = 1  # Counter for auto-increment
        self.used_layoutOrders = set()  # Track used layoutOrders for validation
    
    def assignPID(self, gameSpace, layoutOrder=None):
        """
        Assign a layoutOrder to a gameSpace
        
        Args:
            gameSpace: The gameSpace to assign layoutOrder to
            layoutOrder: Manual layoutOrder (if None, auto-increment)
        """
        if layoutOrder is None:
            # Auto-increment: find next available layoutOrder
            while self.next_layoutOrder in self.used_layoutOrders:
                self.next_layoutOrder += 1
            gameSpace.layoutOrder = self.next_layoutOrder
            gameSpace._egl_pid_manual = False
        else:
            # Manual layoutOrder: find closest available if already used
            original_layoutOrder = layoutOrder
            while layoutOrder in self.used_layoutOrders:
                layoutOrder += 1
            gameSpace.layoutOrder = layoutOrder
            gameSpace._egl_pid_manual = True
            
            # Inform user if layoutOrder was changed
            if layoutOrder != original_layoutOrder:
                print(f"Warning: layoutOrder {original_layoutOrder} already used. Assigned layoutOrder {layoutOrder} instead.")
        
        self.used_layoutOrders.add(gameSpace.layoutOrder)
        self.next_layoutOrder = max(self.next_layoutOrder, gameSpace.layoutOrder) + 1
    
    def removePID(self, gameSpace):
        """Remove layoutOrder from tracking when gameSpace is removed"""
        if gameSpace.layoutOrder is not None:
            self.used_layoutOrders.discard(gameSpace.layoutOrder)
    
    def reorderByPID(self, model_gameSpaces=None):
        """Reorder gameSpaces according to their layoutOrder"""
        # Clear all columns
        for column in self.widgets:
            column.clear()
        
        # Use provided gameSpaces or fallback to self.GameSpaces
        gameSpaces_to_sort = model_gameSpaces if model_gameSpaces is not None else self.GameSpaces
        
        # Sort gameSpaces by layoutOrder (ignore manual_position)
        sorted_gameSpaces = sorted(gameSpaces_to_sort, 
                                 key=lambda gs: gs.layoutOrder if isinstance(gs.layoutOrder, int) else 999999)
        
        # Reorganize according to new layoutOrder order
        for gameSpace in sorted_gameSpaces:
            if gameSpace.layoutOrder is not None and gameSpace.layoutOrder != "manual_position":
                column_index = (gameSpace.layoutOrder - 1) % self.num_columns
                self.widgets[column_index].append(gameSpace)
        
        # Recalculate positions
        print("layoutOrders after reorganization:")
        for gs in self.GameSpaces:
            print(f"  {gs.id}: layoutOrder = {gs.layoutOrder}")
        print("rearrangeWithLayoutThenReleaseLayout in reorderByPID")
        self.rearrangeWithLayoutThenReleaseLayout()
    
    def reorganizePIDsSequentially(self):
        """
        Reorganize layoutOrders to eliminate gaps while preserving order
        
        This method reassigns layoutOrders to gameSpaces to ensure sequential numbering
        (1, 2, 3, 4...) while maintaining the relative order of gameSpaces.
        
        Example: (1, 3, 4, 9) becomes (1, 2, 3, 4)
        """
        # Get all gameSpaces with numeric layoutOrders (exclude manual_position and positioned by modeler)
        gameSpaces_with_pids = []
        for gs in self.GameSpaces:
            if isinstance(gs.layoutOrder, int) and not gs.isPositionDefineByModeler():
                gameSpaces_with_pids.append(gs)
        
        if not gameSpaces_with_pids:
            return
        
        # Sort by current layoutOrder to preserve order
        gameSpaces_with_pids.sort(key=lambda gs: gs.layoutOrder)
        
        # Clear used_layoutOrders tracking
        self.used_layoutOrders.clear()
        
        # Reassign sequential layoutOrders starting from 1
        for i, gameSpace in enumerate(gameSpaces_with_pids):
            new_pid = i + 1
            old_pid = gameSpace.layoutOrder
            
            # Update layoutOrder
            gameSpace.layoutOrder = new_pid
            gameSpace._egl_pid_manual = False  # Mark as auto-assigned
            
            # Update tracking
            self.used_layoutOrders.add(new_pid)
            
            print(f"Reorganized: {gameSpace.id} layoutOrder {old_pid} → {new_pid}")
        
        # Update next_layoutOrder counter
        self.next_layoutOrder = len(gameSpaces_with_pids) + 1
        
        # Reorganize columns based on new layoutOrders
        self.reorderByPID()
        
        # Apply the new positions immediately
        self.applyCalculatedPositions()
    
    def applyCalculatedPositions(self):
        """
        Apply the calculated positions to all gameSpaces
        """
        for column in self.widgets:
            for gs in column:
                if not gs.isPositionDefineByModeler():
                    if hasattr(gs, '_egl_calculated_position'):
                        gs.move(gs._egl_calculated_position[0], gs._egl_calculated_position[1])
                        print(f"Applied position to {gs.id}: {gs._egl_calculated_position}")
        
    def addGameSpace(self, aGameSpace):
        """
        Add a gameSpace to the layout and return the basic position
        
        Args:
            aGameSpace: The gameSpace to add
            
        Returns:
            tuple: (x, y) position for the gameSpace
        """
        # First, call parent method to maintain inheritance consistency
        super().addGameSpace(aGameSpace)
        
        # Check if gameSpace is positioned by modeler
        if aGameSpace.isPositionDefineByModeler():
            # Set special layoutOrder for fixed position
            aGameSpace.layoutOrder = "manual_position"
            aGameSpace._egl_pid_manual = True
            # Don't add to EGL columns - it's positioned manually
            return (aGameSpace.startXBase, aGameSpace.startYBase)
        
        # Assign layoutOrder if not already assigned (only for EGL-managed gameSpaces)
        if aGameSpace.layoutOrder is None:
            self.assignPID(aGameSpace)
        
        # Calculate which column this gameSpace should go to based on layoutOrder
        column_index = (aGameSpace.layoutOrder - 1) % self.num_columns
        
        # Add to the appropriate column
        self.widgets[column_index].append(aGameSpace)
        
        # Calculate position based on EGL logic
        size = self.calculateSize(aGameSpace)
        return size
    
    def calculateSize(self, aGameSpace):
        """
        Calculate the space needed for a gameSpace using EGL logic
        
        Args:
            aGameSpace: The gameSpace to calculate position for
            
        Returns:
            tuple: (x, y) position coordinates
        """
        # Find which column this gameSpace belongs to
        column_index = self._findGameSpaceColumn(aGameSpace)
        if column_index is None:
            return (self.leftMargin, self.topMargin)
        
        # Calculate X position: sum of widths of previous columns
        sizeX = self.leftMargin
        for i in range(column_index):
            if i < len(self.column_widths):
                sizeX += self.column_widths[i]
                sizeX += self.gapBetweenGameSpaces
        
        # Calculate Y position: sum of heights of previous gameSpaces in same column
        sizeY = self.topMargin
        column_gameSpaces = self.widgets[column_index]
        for gs in column_gameSpaces:
            if gs.id == aGameSpace.id:
                break
            sizeY += gs.getSizeYGlobal()
            sizeY += self.gapBetweenGameSpaces
        
        return (sizeX, sizeY)
    
    def _findGameSpaceColumn(self, aGameSpace):
        """
        Find which column a gameSpace belongs to
        
        Args:
            aGameSpace: The gameSpace to find
            
        Returns:
            int: Column index, or None if not found
        """
        for col_index, column in enumerate(self.widgets):
            for gs in column:
                if gs.id == aGameSpace.id:
                    return col_index
        return None
    
    def _updateColumnWidths(self):
        """
        Update column widths based on the widest gameSpace in each column
        """
        for col_index, column in enumerate(self.widgets):
            max_width = 0
            for gs in column:
                max_width = max(max_width, gs.getSizeXGlobal())
            self.column_widths[col_index] = max_width
    
    def rearrangeWithLayoutThenReleaseLayout(self):
        """
        EGL Core Method: Complete cycle of layout organization
        
        This method implements the EGL workflow:
        1. Organize gameSpaces in structured layout
        2. Record calculated positions
        3. Release the structured layout
        4. Allow free positioning while maintaining organization capability
        """
        # Update column widths before calculating positions
        self._updateColumnWidths()
        
        # Phase 1: Calculate and record positions for all gameSpaces
        for column in self.widgets:
            for gs in column:
                if not gs.isPositionDefineByModeler():
                    # Only process gameSpaces without explicit modeler positioning
                    position = self.calculateSize(gs)
                    gs.setStartXBase(position[0])
                    gs.setStartYBase(position[1])
                    # Record the calculated position for later use
                    gs._egl_calculated_position = position
                    print(f"Calculated position for {gs.id}: {position}")
    
    def reAllocateSpace(self):
        """
        Re-allocate space for all gameSpaces using EGL logic
        
        This method is called by the parent class ordered() method
        """
        # Update column widths
        self._updateColumnWidths()
        
        # Recalculate positions for all gameSpaces
        for column in self.widgets:
            for gs in column:
                if not gs.isPositionDefineByModeler():
                    position = self.calculateSize(gs)
                    gs.setStartXBase(position[0])
                    gs.setStartYBase(position[1])
    
    def ordered(self):
        """
        Order all gameSpaces and re-allocate space
        
        This method maintains compatibility with SGAbstractLayout interface
        """
        # For EGL, ordering is handled by the column structure
        # We just need to re-allocate space
        return self.reAllocateSpace()
    
    def getMax(self):
        """
        Get the maximum dimensions of the layout
        
        Returns:
            tuple: (maxX, maxY) maximum dimensions
        """
        maxX = 0
        maxY = 0
        
        # Calculate total width: sum of all column widths + gaps
        total_width = self.leftMargin
        for i, width in enumerate(self.column_widths):
            total_width += width
            if i < len(self.column_widths) - 1:
                total_width += self.gapBetweenGameSpaces
        
        maxX = total_width
        
        # Calculate maximum height: tallest column
        for column in self.widgets:
            column_height = self.topMargin
            for gs in column:
                column_height += gs.getSizeYGlobal()
                column_height += self.gapBetweenGameSpaces
            maxY = max(maxY, column_height)
        
        return (maxX, maxY)
    
    def getNumberOfAnElement(self, aGameSpace):
        """
        Get the position number of a gameSpace in the layout
        
        Args:
            aGameSpace: The gameSpace to find
            
        Returns:
            int: Position number (1-based)
        """
        count = 1
        for column in self.widgets:
            for gs in column:
                if gs.id == aGameSpace.id:
                    return count
                count += 1
        return count
    
    def applyLayout(self, gameSpaces):
        """
        Apply Enhanced Grid Layout to gameSpaces
        """
        # Trigger the EGL cycle
        print("rearrangeWithLayoutThenReleaseLayout in applyLayout")
        self.rearrangeWithLayoutThenReleaseLayout()
        
        # Apply the calculated positions to gameSpaces
        for aGameSpace in (element for element in gameSpaces if not element.isPositionDefineByModeler()):
            if hasattr(aGameSpace, '_egl_calculated_position'):
                aGameSpace.move(aGameSpace._egl_calculated_position[0], 
                              aGameSpace._egl_calculated_position[1])
            else:
                # Fallback to standard positioning
                aGameSpace.move(aGameSpace.startXBase, aGameSpace.startYBase)
    
    def foundInLayout(self, aGameSpace):
        """
        Find the position of a gameSpace in the layout
        
        Args:
            aGameSpace: The gameSpace to find
            
        Returns:
            tuple: (column_index, row_index) or None if not found
        """
        for col_idx, column in enumerate(self.widgets):
            for row_idx, gs in enumerate(column):
                if gs.id == aGameSpace.id:
                    return (col_idx, row_idx)
        return None
