from mainClasses.SGEntity import SGEntity
from mainClasses.SGCell import SGCell
from mainClasses.SGAgent import SGAgent
from mainClasses.SGEntityView import SGEntityView
from mainClasses.SGCellView import SGCellView
from mainClasses.SGAgentView import SGAgentView

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
        grid_parent = cell.classDef.grid if hasattr(cell, 'classDef') and hasattr(cell.classDef, 'grid') else None
        
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
    
    
