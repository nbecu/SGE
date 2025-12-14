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
    
    # @CATEGORY: GET
    def size(self) -> int:
        """
        Get the number of tiles in the stack
        
        Returns:
            int: Number of tiles
        """
        return len(self.tiles)
    
    # @CATEGORY: GET
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
    
    
    # @CATEGORY: GET
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
    
    # @CATEGORY: GET
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
    
    # @CATEGORY: GET
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
    
    # @CATEGORY: GET
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
    
    # @CATEGORY: IS
    def isEmpty(self) -> bool:
        """
        Check if the stack is empty
        
        Returns:
            bool: True if the stack is empty, False otherwise
        """
        return len(self.tiles) == 0
    
    # @CATEGORY: IS
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
    
    # @CATEGORY: DO
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
    
    # @CATEGORY: DO
    def setTileAtLayer(self, tile: 'SGTile', target_layer: int):
        """
        Position a tile at a specific layer in the stack.
        
        This method handles two cases:
        1. If the tile is already in the stack: moves it to the target layer and
           reorganizes other tiles to maintain a continuous layer sequence (1 to N).
        2. If the tile is not in the stack: moves it to this stack's cell and
           positions it at the target layer, reorganizing all tiles accordingly.
        
        Args:
            tile: The tile to position
            target_layer: The target layer number (1-based, where 1 is bottom)
            
        Returns:
            self: The stack (for chaining operations)
            
        Raises:
            ValueError: If target_layer is not a positive integer
            ValueError: If tile type doesn't match the stack's tile type
            
        Example:
            # Move a tile to layer 5 in the stack
            stack.setTileAtLayer(my_tile, 5)
            
            # Position a tile in the last 10 tiles (e.g., layer = size - 9)
            ending_tile = SeaTile.getEntities_withValue("tile_name", "maree_basse")[0]
            stack.setTileAtLayer(ending_tile, max(1, stack.size() - 9))
        """
        if not isinstance(target_layer, int) or target_layer < 1:
            raise ValueError(f"target_layer must be a positive integer, got: {target_layer}")
        
        # Check if tile type matches
        if tile.type != self.tileType:
            raise ValueError(f"Tile type {tile.type.name} does not match stack type {self.tileType.name}")
        
        # Check if tile is already in the stack
        tile_in_stack = self.contains(tile)
        
        # If tile is not in the stack, move it to this stack's cell first
        if not tile_in_stack:
            tile.moveTo(self.cell)
        
        # Get all tiles in the stack (including the tile we're positioning)
        tiles_list = self.tiles
        
        if not tiles_list:
            # Stack is empty, just set the layer
            tile.setLayer(1)
            return self
        
        # Remove the tile we're positioning from the list temporarily
        tiles_without_target = [t for t in tiles_list if t != tile]
        
        # Calculate the actual target layer (ensure it's within valid range)
        max_layer = len(tiles_list)  # After adding our tile
        actual_target_layer = min(target_layer, max_layer)
        
        # Reorganize layers:
        # - Tiles below target_layer keep their layers (shifted if needed)
        # - Target tile gets target_layer
        # - Tiles at/above target_layer get shifted up
        
        # Build new layer assignments
        new_layers = {}
        
        # Assign layers to tiles below target position
        for i, t in enumerate(tiles_without_target, start=1):
            if i < actual_target_layer:
                new_layers[t] = i
            else:
                # Tiles at/above target position get shifted up by 1
                new_layers[t] = i + 1
        
        # Assign target layer to our tile
        new_layers[tile] = actual_target_layer
        
        # Apply all layer changes
        for t, new_layer in new_layers.items():
            t.setLayer(new_layer)
        
        return self
    
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
            'visibleFaceOfTopTileOfStack': visibleFaceOfTopTileOfStack if visibleFaceOfTopTileOfStack in ("front", "back") else None,
            'last_slots_filled': 0  # Will be updated by refillAvailableSlots()
        }
        
        # Create and return a ModelAction that calls refillAvailableSlots
        from mainClasses.SGModelAction import SGModelAction
        model_action = SGModelAction(
            self.cell.model,
            actions=lambda: self.refillAvailableSlots()  )
        return model_action
    
    def getLastSlotsFilled(self):
        """
        Get the number of slots that were filled during the last call to refillAvailableSlots().
        
        This is useful for feedbacks that need to know how many slots were filled.
        
        Returns:
            int: The number of slots filled during the last refill, or 0 if refillAvailableSlots() hasn't been called yet.
        
        Example:
            refill_action = stack.setOpenDrafting(slots, visibleFace="front")
            refill_action.addFeedback(lambda: print(f"{stack.getLastSlotsFilled()} slots filled"))
        """
        if self._open_drafting_config is None:
            return 0
        return self._open_drafting_config.get('last_slots_filled', 0)
    
    # @CATEGORY: DO
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
        
        Returns:
            int: The number of slots that were filled.
        
        Raises:
            ValueError: If setOpenDrafting() has not been called first.
        
        Example:
            # Direct execution
            slots_filled = stack.refillAvailableSlots()
            
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
        slots_filled = 0
        for slot in slots:
            if slot.isEmpty() and not self.isEmpty():
                top_tile = self.topTile()
                if top_tile:
                    top_tile.moveTo(slot)
                    # Flip to show the requested face if specified
                    if visibleFace is not None and top_tile.face != visibleFace:
                        top_tile.flip()
                    slots_filled += 1

        # Flip the top tile to show the requested face if specified
        if visibleFaceOfTopTileOfStack is not None and not self.isEmpty() and self.topTile().face != visibleFaceOfTopTileOfStack:
            self.topTile().flip()
        
        # Store the number of slots filled for potential use in feedbacks
        self._open_drafting_config['last_slots_filled'] = slots_filled
        
        return slots_filled
        

