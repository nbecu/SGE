#!/usr/bin/env python3
"""
Test suite for Model-View alternative methods in SGEntityDef

This test validates all the new WithModelView methods that were added to
SGCellDef and SGAgentDef to support the Model-View architecture.
"""

import sys
import os
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mainClasses.SGModel import SGModel
from mainClasses.SGEntityDef import SGCellDef, SGAgentDef


class TestModelViewAlternatives(unittest.TestCase):
    """Test suite for Model-View alternative methods"""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment once for all tests"""
        # Create QApplication instance for PyQt5
        cls.app = QApplication([])
        
        # Create a test model with proper parameters
        cls.model = SGModel(800, 600, name="TestModel")
        
        # Create cells using the model's newCellsOnGrid method
        cls.cell_def = cls.model.newCellsOnGrid(
            columns=5, 
            rows=5, 
            format="square", 
            size=50, 
            gap=5, 
            name="test_grid"
        )
        
        # Create agent definition
        cls.agent_def = SGAgentDef(
            cls.model,
            "test_agent",
            "circle",
            30,
            entDefAttributesAndValues={"health": 100, "energy": 50},
            defaultColor=Qt.blue,
            locationInEntity="center"
        )
        
        # Create cells using the new Model-View method
        cls.cells = {}
        for x in range(1, 4):  # 3x3 grid
            for y in range(1, 4):
                cell_model, cell_view = cls.cell_def.newCellWithModelView(x, y)
                cls.cells[(x, y)] = cell_model

    def setUp(self):
        """Set up each test"""
        # Clear existing agents before each test
        # Use a safer approach to avoid conflicts with old architecture
        agents_to_remove = []
        for agent in self.agent_def.entities:
            if hasattr(agent, 'cell') and agent.cell is not None:
                # This is a new Model-View agent
                if hasattr(agent.cell, 'removeAgent'):
                    agent.cell.removeAgent(agent)
            agents_to_remove.append(agent)
        
        for agent in agents_to_remove:
            if agent in self.agent_def.entities:
                self.agent_def.entities.remove(agent)

    def test_newCellWithModelView(self):
        """Test newCellWithModelView method"""
        # Create a new cell
        cell_model, cell_view = self.cell_def.newCellWithModelView(4, 4)
        
        # Verify the cell was created
        self.assertIsNotNone(cell_model)
        self.assertIsNotNone(cell_view)
        
        # Verify the cell is in the entities list
        self.assertIn(cell_model, self.cell_def.entities)
        
        # Verify the cell has the correct coordinates
        self.assertEqual(cell_model.xCoord, 4)
        self.assertEqual(cell_model.yCoord, 4)
        
        # Verify the model and view are linked
        self.assertEqual(cell_model.getView(), cell_view)
        self.assertEqual(cell_view.entity_model, cell_model)

    def test_newAgentOnCellWithModelView(self):
        """Test newAgentOnCellWithModelView method"""
        # Get a test cell
        test_cell = self.cells[(1, 1)]
        
        # Create an agent on the cell
        agent_model, agent_view = self.agent_def.newAgentOnCellWithModelView(
            test_cell, 
            {"health": 80, "energy": 60}
        )
        
        # Verify the agent was created
        self.assertIsNotNone(agent_model)
        self.assertIsNotNone(agent_view)
        
        # Verify the agent is in the entities list
        self.assertIn(agent_model, self.agent_def.entities)
        
        # Verify the agent is in the cell
        self.assertIn(agent_model, test_cell.agents)
        
        # Verify the agent has the correct attributes
        self.assertEqual(agent_model.value("health"), 80)
        self.assertEqual(agent_model.value("energy"), 60)
        
        # Verify the model and view are linked
        self.assertEqual(agent_model.getView(), agent_view)
        self.assertEqual(agent_view.agent_model, agent_model)

    def test_newAgentsOnCellWithModelView(self):
        """Test newAgentsOnCellWithModelView method"""
        # Get a test cell
        test_cell = self.cells[(2, 2)]
        
        # Create multiple agents on the cell
        agents = self.agent_def.newAgentsOnCellWithModelView(
            3, 
            test_cell, 
            {"health": 90, "energy": 70}
        )
        
        # Verify the correct number of agents were created
        self.assertEqual(len(agents), 3)
        
        # Verify each agent was created correctly
        for agent_model, agent_view in agents:
            self.assertIsNotNone(agent_model)
            self.assertIsNotNone(agent_view)
            self.assertIn(agent_model, self.agent_def.entities)
            self.assertIn(agent_model, test_cell.agents)
            self.assertEqual(agent_model.value("health"), 90)
            self.assertEqual(agent_model.value("energy"), 70)

    def test_newAgentAtCoordsWithModelView(self):
        """Test newAgentAtCoordsWithModelView method"""
        # Create an agent at specific coordinates
        agent_model, agent_view = self.agent_def.newAgentAtCoordsWithModelView(
            xCoord=2, 
            yCoord=3, 
            attributesAndValues={"health": 75, "energy": 45}
        )
        
        # Verify the agent was created
        self.assertIsNotNone(agent_model)
        self.assertIsNotNone(agent_view)
        
        # Verify the agent is in the correct cell
        self.assertEqual(agent_model.cell.xCoord, 2)
        self.assertEqual(agent_model.cell.yCoord, 3)
        
        # Verify the agent has the correct attributes
        self.assertEqual(agent_model.value("health"), 75)
        self.assertEqual(agent_model.value("energy"), 45)

    def test_newAgentAtCoordsWithModelView_tuple_coords(self):
        """Test newAgentAtCoordsWithModelView with tuple coordinates"""
        # Create an agent using tuple coordinates
        agent_model, agent_view = self.agent_def.newAgentAtCoordsWithModelView(
            (3, 1), 
            attributesAndValues={"health": 85, "energy": 55}
        )
        
        # Verify the agent was created
        self.assertIsNotNone(agent_model)
        self.assertIsNotNone(agent_view)
        
        # Verify the agent is in the correct cell
        self.assertEqual(agent_model.cell.xCoord, 3)
        self.assertEqual(agent_model.cell.yCoord, 1)

    def test_newAgentsAtCoordsWithModelView(self):
        """Test newAgentsAtCoordsWithModelView method"""
        # Create multiple agents at specific coordinates
        agents = self.agent_def.newAgentsAtCoordsWithModelView(
            2, 
            xCoord=1, 
            yCoord=2, 
            attributesAndValues={"health": 95, "energy": 65}
        )
        
        # Verify the correct number of agents were created
        self.assertEqual(len(agents), 2)
        
        # Verify each agent was created correctly
        for agent_model, agent_view in agents:
            self.assertIsNotNone(agent_model)
            self.assertIsNotNone(agent_view)
            self.assertEqual(agent_model.cell.xCoord, 1)
            self.assertEqual(agent_model.cell.yCoord, 2)
            self.assertEqual(agent_model.value("health"), 95)
            self.assertEqual(agent_model.value("energy"), 65)

    def test_newAgentAtRandomWithModelView(self):
        """Test newAgentAtRandomWithModelView method"""
        # Create an agent at random location
        agent_model, agent_view = self.agent_def.newAgentAtRandomWithModelView(
            attributesAndValues={"health": 70, "energy": 40}
        )
        
        # Verify the agent was created
        self.assertIsNotNone(agent_model)
        self.assertIsNotNone(agent_view)
        
        # Verify the agent is in a valid cell
        self.assertIsNotNone(agent_model.cell)
        self.assertIn(agent_model, agent_model.cell.agents)
        
        # Verify the agent has the correct attributes
        self.assertEqual(agent_model.value("health"), 70)
        self.assertEqual(agent_model.value("energy"), 40)

    def test_newAgentAtRandomWithModelView_dict_attributes(self):
        """Test newAgentAtRandomWithModelView with dict as first argument"""
        # Create an agent using dict as first argument
        agent_model, agent_view = self.agent_def.newAgentAtRandomWithModelView(
            {"health": 65, "energy": 35}
        )
        
        # Verify the agent was created
        self.assertIsNotNone(agent_model)
        self.assertIsNotNone(agent_view)
        
        # Verify the agent has the correct attributes
        self.assertEqual(agent_model.value("health"), 65)
        self.assertEqual(agent_model.value("energy"), 35)

    def test_newAgentsAtRandomWithModelView(self):
        """Test newAgentsAtRandomWithModelView method"""
        # Create multiple agents at random locations
        agents = self.agent_def.newAgentsAtRandomWithModelView(
            3, 
            attributesAndValues={"health": 88, "energy": 58}
        )
        
        # Verify the correct number of agents were created
        self.assertEqual(len(agents), 3)
        
        # Verify each agent was created correctly
        for agent_model, agent_view in agents:
            self.assertIsNotNone(agent_model)
            self.assertIsNotNone(agent_view)
            self.assertIsNotNone(agent_model.cell)
            self.assertIn(agent_model, agent_model.cell.agents)
            self.assertEqual(agent_model.value("health"), 88)
            self.assertEqual(agent_model.value("energy"), 58)

    def test_newAgentsAtRandomWithModelView_dict_attributes(self):
        """Test newAgentsAtRandomWithModelView with dict as second argument"""
        # Create multiple agents using dict as second argument
        agents = self.agent_def.newAgentsAtRandomWithModelView(
            2, 
            {"health": 92, "energy": 62}
        )
        
        # Verify the correct number of agents were created
        self.assertEqual(len(agents), 2)
        
        # Verify each agent has the correct attributes
        for agent_model, agent_view in agents:
            self.assertEqual(agent_model.value("health"), 92)
            self.assertEqual(agent_model.value("energy"), 62)

    def test_error_handling_invalid_cell(self):
        """Test error handling when cell is None"""
        # Try to create an agent with None cell
        result = self.agent_def.newAgentOnCellWithModelView(None)
        
        # Should return None instead of crashing
        self.assertIsNone(result)

    def test_error_handling_invalid_coordinates(self):
        """Test error handling when coordinates are invalid"""
        # Try to create an agent at invalid coordinates
        result = self.agent_def.newAgentAtCoordsWithModelView(xCoord=10, yCoord=10)
        
        # Should return None instead of crashing
        self.assertIsNone(result)

    def test_error_handling_no_cell_def(self):
        """Test error handling when no cell definition is available"""
        # Create a new agent definition without any cell definitions
        empty_agent_def = SGAgentDef(
            self.model,
            "empty_agent",
            "circle",
            30,
            entDefAttributesAndValues={"health": 100},
            defaultColor=Qt.red
        )
        
        # Try to create an agent at random (no cell definitions available)
        # Since we have cell definitions in setUpClass, we need to test with a condition
        # that no cell will satisfy
        result = empty_agent_def.newAgentAtRandomWithModelView(
            condition=lambda cell: False  # No cell will satisfy this condition
        )
        
        # Should return None instead of crashing
        # Note: getRandomEntity returns False when no cell satisfies the condition,
        # which causes newAgentAtRandomWithModelView to return None
        self.assertIsNone(result)

    def test_model_view_linking(self):
        """Test that models and views are properly linked"""
        # Create a cell and agent
        cell_model, cell_view = self.cell_def.newCellWithModelView(5, 5)
        agent_model, agent_view = self.agent_def.newAgentOnCellWithModelView(
            cell_model, 
            {"health": 100}
        )
        
        # Test cell model-view linking
        self.assertEqual(cell_model.getView(), cell_view)
        self.assertEqual(cell_view.entity_model, cell_model)
        
        # Test agent model-view linking
        self.assertEqual(agent_model.getView(), agent_view)
        self.assertEqual(agent_view.agent_model, agent_model)
        
        # Test that the view can update the model
        agent_model.setValue("health", 50)
        self.assertEqual(agent_model.value("health"), 50)

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        # Clean up the QApplication
        cls.app.quit()


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
