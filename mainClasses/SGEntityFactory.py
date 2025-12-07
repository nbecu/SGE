from mainClasses.SGEntity import SGEntity
from mainClasses.SGCell import SGCell
from mainClasses.SGAgent import SGAgent
from mainClasses.SGTile import SGTile
from mainClasses.SGEntityView import SGEntityView
from mainClasses.SGCellView import SGCellView
from mainClasses.SGAgentView import SGAgentView
from mainClasses.SGTileView import SGTileView

class SGEntityFactory:
    """
    Factory class for creating Model-View entity pairs
    Separates entity creation logic from entity definitions
    """
    
    @staticmethod
    def newCellWithModelView(cellDef, x, y):
        """
        Create a cell with Model-View architecture
        
        Args:
            cellDef: The cell definition
            x: X coordinate
            y: Y coordinate
            
        Returns:
            tuple: (cell_model, cell_view)
        """
        # Create the cell model
        cell_model = SGCell(cellDef, x, y, cellDef.defaultImage)
        
        # Create the cell view
        cell_view = SGCellView(cell_model, cellDef.grid)
        
        # Link model and view
        cell_model.setView(cell_view)
        
        return cell_model, cell_view
    
    @staticmethod
    def newAgentWithModelView(agentDef, cell, attributesAndValues=None, image=None, popupImage=None):
        """
        Create an agent with Model-View architecture
        
        Args:
            agentDef: The agent definition
            cell: The cell where the agent will be placed
            attributesAndValues: Initial attributes and values
            image: Default image for the agent
            popupImage: Popup image for the agent
            
        Returns:
            tuple: (agent_model, agent_view)
        """
        if image is None:
            image = agentDef.defaultImage
        if popupImage is None:
            popupImage = agentDef.popupImage
            
        # Create the agent model (using SGAgent which inherits from SGEntity and has isAgent=True)
        agent_model = SGAgent(
            cell, 
            agentDef.defaultsize, 
            attributesAndValues, 
            agentDef.defaultShapeColor, 
            agentDef, 
            image, 
            popupImage
        )
        
        # Create the agent view with grid as parent (not cell)
        grid_parent = cell.type.grid if hasattr(cell, 'type') and hasattr(cell.type, 'grid') else None
        
        agent_view = SGAgentView(agent_model, grid_parent)
        
        # Link model and view
        agent_model.setView(agent_view)
        
        # Note: agent_view.show() will be called later in positionAllAgents()
        
        return agent_model, agent_view
    
    @staticmethod
    def newCell(cellDef, x, y): #todo this method is not used anymore. Consider removing it.
        """
        Create a cell with Model-View architecture (standard method)
        
        Args:
            cellDef: The cell definition
            x: X coordinate
            y: Y coordinate
            
        Returns:
            tuple: (cell_model, cell_view)
        """
        return SGEntityFactory.newCellWithModelView(cellDef, x, y)
    
    @staticmethod
    def newTileWithModelView(tileDef, cell, attributesAndValues=None, face="front",
                             frontImage=None, backImage=None, frontColor=None, backColor=None):
        """
        Create a tile with Model-View architecture.
        The position is fixed by the TileType (positionOnCell) and cannot be overridden.
        
        Args:
            tileDef: The tile definition
            cell: The cell where the tile will be placed
            attributesAndValues: Initial attributes and values
            face: Initial face ("front" or "back")
            frontImage: Image for the front face (optional)
            backImage: Image for the back face (optional)
            frontColor: Color for the front face (optional)
            backColor: Color for the back face (optional)
            
        Returns:
            tuple: (tile_model, tile_view)
        """
        if cell is None:
            return None
        
        # Use fixed position from TileType (cannot be overridden)
        position = tileDef.positionOnCell if hasattr(tileDef, 'positionOnCell') else "center"
        
        # Use defaults from tileDef if not provided
        if frontImage is None:
            frontImage = tileDef.frontImage
        if backImage is None:
            backImage = tileDef.backImage
        if frontColor is None:
            frontColor = tileDef.frontColor
        if backColor is None:
            backColor = tileDef.backColor
        
        # Create the tile model
        tile_model = SGTile(
            cell, 
            tileDef.defaultsize, 
            attributesAndValues, 
            tileDef.defaultShapeColor, 
            tileDef, 
            position,
            face,
            frontImage,
            backImage,
            frontColor,
            backColor
        )
        
        # Create the tile view with grid as parent (not cell)
        grid_parent = cell.type.grid if hasattr(cell, 'type') and hasattr(cell.type, 'grid') else None
        
        tile_view = SGTileView(tile_model, grid_parent)
        
        # Link model and view
        tile_model.setView(tile_view)
        
        # Note: tile_view.show() will be called later in positionAllTiles() or similar
        
        return tile_model, tile_view
    
    
