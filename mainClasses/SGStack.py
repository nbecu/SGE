from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from mainClasses.SGCell import SGCell
    from mainClasses.SGTile import SGTile
    from mainClasses.SGEntityType import SGTileType


class SGStack:
    """
    SGStack - Virtual entity representing a stack of tiles
    
    A Stack is a virtual entity that represents all tiles of the same type
    at the same position on a cell. The stack provides methods to query
    and manipulate the tiles without being a physical game object itself.
    
    Important characteristics:
    - No cache: The tiles property is recalculated on each access
    - Immutable for adding/removing: Tiles are added/removed by external operations
    - Layers are always continuous from 1 to N (no gaps)
    """
    
    def __init__(self, cell: 'SGCell', tileType: 'SGTileType'):
        """
        Initialize a Stack
        
        Args:
            cell: The cell containing the stack
            tileType: The tile type that identifies this stack
        """
        self.cell = cell
        self.tileType = tileType
        self.position = tileType.positionOnCell
        self._open_drafting_config = None  # Stores open drafting configuration
    
    @property
    def tiles(self) -> List['SGTile']:
        """
        Get all tiles in the stack, sorted by layer (lowest to highest)
        
        This property is recalculated on each access (no cache).
        
        Returns:
            list: List of tiles sorted by layer
        """
        if self.cell is None:
            return []
        
        # Get tiles at the position for this tile type
        # Safely check for position attribute (tile might be in initialization)
        tiles_at_pos = []
        for tile in self.cell.tiles:
            try:
                if hasattr(tile, 'position') and hasattr(tile, 'type') and tile.position == self.position and tile.type == self.tileType:
                    tiles_at_pos.append(tile)
            except AttributeError:
                # Tile is still being initialized, skip it
                continue
        
        # Sort by layer (lowest to highest)
        # Safely handle tiles that might not have layer attribute yet
        try:
            return sorted(tiles_at_pos, key=lambda t: t.layer if hasattr(t, 'layer') else 0)
        except AttributeError:
            # Fallback: return unsorted if there's still an issue
            return tiles_at_pos

    # ============================================================================
    # MODELER METHODS
    # ============================================================================
    #     
    # ============================================================================
    # GET/NB METHODS
    # ============================================================================
    
    def size(self) -> int:
        """
        Get the number of tiles in the stack
        
        Returns:
            int: Number of tiles
        """
        return len(self.tiles)
    
    def maxLayer(self) -> int:
        """
        Get the maximum layer in the stack
        
        Returns:
            int: Maximum layer (0 if stack is empty)
        """
        tiles_list = self.tiles
        if not tiles_list:
            return 0
        return max(tile.layer for tile in tiles_list)
    
    def minLayer(self) -> int:
        """
        Get the minimum layer in the stack
        
        Returns:
            int: Minimum layer (0 if stack is empty)
        """
        tiles_list = self.tiles
        if not tiles_list:
            return 0
        return min(tile.layer for tile in tiles_list)
    
    def topTile(self) -> Optional['SGTile']:
        """
        Get the tile with the highest layer (top of the stack)
        
        Returns:
            SGTile or None: The top tile, or None if stack is empty
        """
        tiles_list = self.tiles
        if not tiles_list:
            return None
        return max(tiles_list, key=lambda t: t.layer)
    
    def bottomTile(self) -> Optional['SGTile']:
        """
        Get the tile with the lowest layer (bottom of the stack)
        
        Returns:
            SGTile or None: The bottom tile, or None if stack is empty
        """
        tiles_list = self.tiles
        if not tiles_list:
            return None
        return min(tiles_list, key=lambda t: t.layer)
    
    def tileAtLayer(self, layer: int) -> Optional['SGTile']:
        """
        Get the tile at a specific layer
        
        Args:
            layer: The layer number (1-based)
            
        Returns:
            SGTile or None: The tile at the specified layer, or None if not found
        """
        tiles_list = self.tiles
        for tile in tiles_list:
            if tile.layer == layer:
                return tile
        return None
    
    def getTilesWithValue(self, attribute: str, value) -> List['SGTile']:
        """
        Get all tiles in the stack that have a specific attribute value
        
        Args:
            attribute: The attribute name
            value: The value to match
            
        Returns:
            list: List of tiles matching the criteria
        """
        tiles_list = self.tiles
        return [tile for tile in tiles_list 
                if hasattr(tile, 'getValue') and tile.getValue(attribute) == value]
    
    def getTilesWithFace(self, face: str) -> List['SGTile']:
        """
        Get all tiles in the stack that have a specific face
        
        Args:
            face: The face to match ("front" or "back")
            
        Returns:
            list: List of tiles with the specified face
        """
        tiles_list = self.tiles
        return [tile for tile in tiles_list if tile.face == face]
    
    # ============================================================================
    # IS/HAS METHODS
    # ============================================================================
    
    def isEmpty(self) -> bool:
        """
        Check if the stack is empty
        
        Returns:
            bool: True if the stack is empty, False otherwise
        """
        return len(self.tiles) == 0
    
    def contains(self, tile: 'SGTile') -> bool:
        """
        Check if a specific tile is in the stack
        
        Args:
            tile: The tile to check
            
        Returns:
            bool: True if the tile is in the stack, False otherwise
        """
        return tile in self.tiles
    
    # ============================================================================
    # DO METHODS
    # ============================================================================
    
    def shuffle(self):
        """
        Shuffle the tiles in the stack and reassign layers from 1 to N
        
        This method:
        1. Gets all tiles in the stack
        2. Randomly shuffles their order
        3. Reassigns layers from 1 to N in the new order
        
        Since layers represent the order in the stack, shuffling changes
        which tile is on top (highest layer) and which is on bottom (lowest layer).
        """
        import random
        
        tiles_list = self.tiles
        if not tiles_list:
            return
        
        # Shuffle the tiles
        random.shuffle(tiles_list)
        
        # Reassign layers from 1 to N in the new order
        for i, tile in enumerate(tiles_list, start=1):
            tile.setLayer(i)
    
    def setOpenDrafting(self, slots: List['SGCell'], visibleFace: str = None, visibleFaceOfTopTileOfStack: str = None):
        """
        Configure Open Drafting mechanics for this stack.
        
        Open Drafting is a game mechanic where tiles from this stack are automatically
        distributed to fill empty slots (cells) in a river or drafting area.
        
        This method configures which cells should be filled and what face should be
        visible on the drafted tiles. It returns a ModelAction that can be passed to
        newModelPhase() to execute the refill automatically.
        
        Args:
            slots: List of cells (SGCell) that represent the drafting slots to fill.
                   These are typically cells in a "river" or drafting area.
            visibleFace: Optional face to show on drafted tiles ("front" or "back").
                        If None or not "front"/"back", tiles keep their current face.
                        If specified, tiles are flipped to show the requested face.
        visibleFaceOfTopTileOfStack: Optional face to show on the top tile of the stack ("front" or "back").
                        If None or not "front"/"back", the top tile keeps its current face.
                        If specified, the top tile is flipped to show the requested face.
        Returns:
            SGModelAction: A ModelAction that can be passed to newModelPhase() to
                          automatically refill available slots.
        
        Example:
            # Configure drafting for a river with 3 slots
            river_slots = [River.getCell(2,1), River.getCell(3,1), River.getCell(4,1)]
            refill_action = stack.setOpenDrafting(river_slots, visibleFace="front", visibleFaceOfTopTileOfStack="back")
            myModel.newModelPhase(refill_action, name="Refill River")
        """
        if not isinstance(slots, list):
            raise ValueError("slots must be a list of SGCell objects")
        
        # Store configuration
        self._open_drafting_config = {
            'slots': slots,
            'visibleFace': visibleFace if visibleFace in ("front", "back") else None,
            'visibleFaceOfTopTileOfStack': visibleFaceOfTopTileOfStack if visibleFaceOfTopTileOfStack in ("front", "back") else None
        }
        
        # Create and return a ModelAction that calls refillAvailableSlots
        from mainClasses.SGModelAction import SGModelAction
        model_action = SGModelAction(
            self.cell.model,
            actions=lambda: self.refillAvailableSlots()  )
        return model_action
    
    def refillAvailableSlots(self):
        """
        Refill available slots using the Open Drafting configuration.
        
        This method automatically moves tiles from the top of this stack to fill
        empty slots that were configured via setOpenDrafting(). For each empty slot,
        the top tile is moved and flipped if a visibleFace was specified in the
        configuration.
        
        The method iterates through all configured slots and fills each empty one
        until either all slots are filled or the stack is empty.

        After the slots are filled, the top tile of the stack is flipped or not to show the requested face if a visibleFaceOfTopTileOfStack was specified in the configuration.
        
        Raises:
            ValueError: If setOpenDrafting() has not been called first.
        
        Example:
            # Direct execution
            stack.refillAvailableSlots()
            
            # Or via ModelAction (recommended)
            refill_action = stack.setOpenDrafting(slots, visibleFace="front", visibleFaceOfTopTileOfStack="back")
            myModel.newModelPhase(refill_action, name="Refill River")
        """
        if self._open_drafting_config is None:
            raise ValueError("setOpenDrafting() must be called before refillAvailableSlots()")
        
        slots = self._open_drafting_config['slots']
        visibleFace = self._open_drafting_config['visibleFace']
        visibleFaceOfTopTileOfStack = self._open_drafting_config['visibleFaceOfTopTileOfStack']
        
        # Fill each empty slot with a tile from the top of the stack
        for slot in slots:
            if slot.isEmpty() and not self.isEmpty():
                top_tile = self.topTile()
                if top_tile:
                    top_tile.moveTo(slot)
                    # Flip to show the requested face if specified
                    if visibleFace is not None and top_tile.face != visibleFace:
                        top_tile.flip()

        # Flip the top tile to show the requested face if specified
        if visibleFaceOfTopTileOfStack is not None and self.topTile().face != visibleFaceOfTopTileOfStack:
            self.topTile().flip()
        

