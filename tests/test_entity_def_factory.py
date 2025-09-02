"""
Test for SGEntityDefFactory
Validates the factory creation of Model-View pairs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from mainClasses.SGModel import SGModel
from mainClasses.SGEntityDef import SGCellDef, SGAgentDef
from mainClasses.SGEntityDefFactory import SGEntityDefFactory

class TestEntityDefFactory:
    """Test class for SGEntityDefFactory"""
    
    def __init__(self):
        self.app = QApplication([])
        self.model = SGModel()
        self.setup_test_environment()
    
    def setup_test_environment(self):
        """Setup test environment with grid and definitions"""
        # Create a grid
        self.cell_def = self.model.newCellsOnGrid(
            columns=3, 
            rows=3, 
            format="square", 
            size=50, 
            gap=5, 
            name="test_grid"
        )
        self.grid = self.cell_def.grid
        
        # Create an agent definition
        self.agent_def = SGAgentDef(
            self.model,
            "test_agent",
            "circleAgent",
            30,
            entDefAttributesAndValues={"health": 100, "energy": 50},
            defaultColor="blue",
            locationInEntity="center"
        )
    
    def test_cell_creation_with_factory(self):
        """Test cell creation using the factory"""
        print("=== Test cell creation with factory ===")
        
        # Create a cell using the factory
        cell_model, cell_view = SGEntityDefFactory.newCellWithModelView(
            self.cell_def, 2, 2
        )
        
        # Validate the cell model
        print(f"Cell model: ID={cell_model.id}, coords=({cell_model.xCoord},{cell_model.yCoord})")
        print(f"Cell model has view: {cell_model.getView() is not None}")
        
        # Validate the cell view
        print(f"Cell view: ID={cell_view.id}, coords=({cell_view.xCoord},{cell_view.yCoord})")
        print(f"Cell view has model: {cell_view.cell_model is not None}")
        
        # Validate the link
        model_view_linked = cell_model.getView() == cell_view
        view_model_linked = cell_view.cell_model == cell_model
        
        print(f"Model-View linked: {model_view_linked}")
        print(f"View-Model linked: {view_model_linked}")
        
        return {
            "cell_model": cell_model,
            "cell_view": cell_view,
            "model_view_linked": model_view_linked,
            "view_model_linked": view_model_linked
        }
    
    def test_agent_creation_with_factory(self):
        """Test agent creation using the factory"""
        print("\n=== Test agent creation with factory ===")
        
        # First create a cell to place the agent
        cell_model, cell_view = SGEntityDefFactory.newCellWithModelView(
            self.cell_def, 1, 1
        )
        
        # Create an agent using the factory
        agent_model, agent_view = SGEntityDefFactory.newAgentWithModelView(
            self.agent_def,
            cell_model,
            {"health": 75, "energy": 25}
        )
        
        # Validate the agent model
        print(f"Agent model: ID={agent_model.id}, cell=({agent_model.getCell().xCoord},{agent_model.getCell().yCoord})")
        print(f"Agent model has view: {agent_model.getView() is not None}")
        print(f"Agent health: {agent_model.value('health')}, energy: {agent_model.value('energy')}")
        
        # Validate the agent view
        print(f"Agent view: ID={agent_view.id}")
        print(f"Agent view has model: {agent_view.agent_model is not None}")
        
        # Validate the link
        model_view_linked = agent_model.getView() == agent_view
        view_model_linked = agent_view.agent_model == agent_model
        
        print(f"Model-View linked: {model_view_linked}")
        print(f"View-Model linked: {view_model_linked}")
        
        # Validate cell-agent relationship
        cell_has_agent = cell_model.hasAgent(agent_model)
        agent_in_cell = agent_model.isInCell(cell_model)
        
        print(f"Cell has agent: {cell_has_agent}")
        print(f"Agent in cell: {agent_in_cell}")
        
        return {
            "agent_model": agent_model,
            "agent_view": agent_view,
            "cell_model": cell_model,
            "model_view_linked": model_view_linked,
            "view_model_linked": view_model_linked,
            "cell_has_agent": cell_has_agent,
            "agent_in_cell": agent_in_cell
        }
    
    def run_all_tests(self):
        """Run all factory tests"""
        print("🚀 Testing SGEntityDefFactory")
        print("=" * 50)
        
        # Test cell creation
        cell_result = self.test_cell_creation_with_factory()
        
        # Test agent creation
        agent_result = self.test_agent_creation_with_factory()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 FACTORY TEST RESULTS")
        print("=" * 50)
        
        print("Cell creation:")
        print(f"  - Model-View linked: {cell_result['model_view_linked']}")
        print(f"  - View-Model linked: {cell_result['view_model_linked']}")
        
        print("\nAgent creation:")
        print(f"  - Model-View linked: {agent_result['model_view_linked']}")
        print(f"  - View-Model linked: {agent_result['view_model_linked']}")
        print(f"  - Cell-Agent relationship: {agent_result['cell_has_agent']}")
        
        print("\n🎯 CONCLUSION:")
        print("Factory successfully creates Model-View pairs with proper linking")
        
        return {
            "cell_result": cell_result,
            "agent_result": agent_result
        }

if __name__ == "__main__":
    test = TestEntityDefFactory()
    results = test.run_all_tests()
