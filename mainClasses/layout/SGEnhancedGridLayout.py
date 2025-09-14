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
        
        # EGL pID system
        self.next_pID = 1  # Counter for auto-increment
        self.used_pIDs = set()  # Track used pIDs for validation
    
    def assignPID(self, gameSpace, pID=None):
        """
        Assign a pID to a gameSpace
        
        Args:
            gameSpace: The gameSpace to assign pID to
            pID: Manual pID (if None, auto-increment)
        """
        if pID is None:
            # Auto-increment: find next available pID
            while self.next_pID in self.used_pIDs:
                self.next_pID += 1
            gameSpace.pID = self.next_pID
            gameSpace._egl_pid_manual = False
        else:
            # Manual pID: find closest available if already used
            original_pID = pID
            while pID in self.used_pIDs:
                pID += 1
            gameSpace.pID = pID
            gameSpace._egl_pid_manual = True
            
            # Inform user if pID was changed
            if pID != original_pID:
                print(f"Warning: pID {original_pID} already used. Assigned pID {pID} instead.")
        
        self.used_pIDs.add(gameSpace.pID)
        self.next_pID = max(self.next_pID, gameSpace.pID) + 1
    
    def removePID(self, gameSpace):
        """Remove pID from tracking when gameSpace is removed"""
        if gameSpace.pID is not None:
            self.used_pIDs.discard(gameSpace.pID)
    
    def reorderByPID(self, model_gameSpaces=None):
        """Reorder gameSpaces according to their pID"""
        # Clear all columns
        for column in self.widgets:
            column.clear()
        
        # Use provided gameSpaces or fallback to self.GameSpaces
        gameSpaces_to_sort = model_gameSpaces if model_gameSpaces is not None else self.GameSpaces
        
        # Sort gameSpaces by pID (ignore fixed_position)
        sorted_gameSpaces = sorted(gameSpaces_to_sort, 
                                 key=lambda gs: gs.pID if isinstance(gs.pID, int) else 999999)
        
        # Reorganize according to new pID order
        for gameSpace in sorted_gameSpaces:
            if gameSpace.pID is not None and gameSpace.pID != "fixed_position":
                column_index = (gameSpace.pID - 1) % self.num_columns
                self.widgets[column_index].append(gameSpace)
        
        # Recalculate positions
        print("pIDs after reorganization:")
        for gs in self.GameSpaces:
            print(f"  {gs.id}: pID = {gs.pID}")
        print("rearrangeWithLayoutThenReleaseLayout in reorderByPID")
        self.rearrangeWithLayoutThenReleaseLayout()
    
    def reorganizePIDsSequentially(self):
        """
        Reorganize pIDs to eliminate gaps while preserving order
        
        This method reassigns pIDs to gameSpaces to ensure sequential numbering
        (1, 2, 3, 4...) while maintaining the relative order of gameSpaces.
        
        Example: (1, 3, 4, 9) becomes (1, 2, 3, 4)
        """
        # Get all gameSpaces with numeric pIDs (exclude fixed_position and positioned by modeler)
        gameSpaces_with_pids = []
        for gs in self.GameSpaces:
            if isinstance(gs.pID, int) and not gs.isPositionDefineByModeler():
                gameSpaces_with_pids.append(gs)
        
        if not gameSpaces_with_pids:
            return
        
        # Sort by current pID to preserve order
        gameSpaces_with_pids.sort(key=lambda gs: gs.pID)
        
        # Clear used_pIDs tracking
        self.used_pIDs.clear()
        
        # Reassign sequential pIDs starting from 1
        for i, gameSpace in enumerate(gameSpaces_with_pids):
            new_pid = i + 1
            old_pid = gameSpace.pID
            
            # Update pID
            gameSpace.pID = new_pid
            gameSpace._egl_pid_manual = False  # Mark as auto-assigned
            
            # Update tracking
            self.used_pIDs.add(new_pid)
            
            print(f"Reorganized: {gameSpace.id} pID {old_pid} → {new_pid}")
        
        # Update next_pID counter
        self.next_pID = len(gameSpaces_with_pids) + 1
        
        # Reorganize columns based on new pIDs
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
            # Set special pID for fixed position
            aGameSpace.pID = "fixed_position"
            aGameSpace._egl_pid_manual = True
            # Don't add to EGL columns - it's positioned manually
            return (aGameSpace.startXBase, aGameSpace.startYBase)
        
        # Assign pID if not already assigned (only for EGL-managed gameSpaces)
        if aGameSpace.pID is None:
            self.assignPID(aGameSpace)
        
        # Calculate which column this gameSpace should go to based on pID
        column_index = (aGameSpace.pID - 1) % self.num_columns
        
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
