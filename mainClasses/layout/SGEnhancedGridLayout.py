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
        
    def addGameSpace(self, aGameSpace):
        """
        Add a gameSpace to the layout and return the basic position
        
        Args:
            aGameSpace: The gameSpace to add
            
        Returns:
            tuple: (x, y) position for the gameSpace
        """
        self.count = self.count + 1
        
        # Calculate which column this gameSpace should go to
        column_index = (self.count - 1) % self.num_columns
        
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
