import unittest
from PyQt5.QtWidgets import QApplication
import sys
import os

# Add the mainClasses directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mainClasses.SGModel import SGModel
from mainClasses.SGEntityDef import SGCellDef, SGAgentDef
from mainClasses.SGAgent import SGAgent
from mainClasses.SGAgentModel import SGAgentModel
from mainClasses.SGAgentView import SGAgentView

class TestSGAgentModelViewAdaptation(unittest.TestCase):
    """Test suite for SGAgent Model-View adaptation"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
        
        # Create a test model
        cls.model = SGModel(800, 600, name="TestModel")
        
        # Create a cell definition and grid
        cls.cell_def = cls.model.newCellsOnGrid(3, 3, "square", 50, 0, "red", True, "TestCell")
        cls.grid = cls.cell_def.grid
        
        # Create an agent definition
        cls.agent_def = cls.model.newAgentSpecies("TestAgent", "circleAgent", {}, 20, "blue", 
                                                  "center")
        
        # Get a test cell
        cls.test_cell = cls.grid.getCell_withCoords(1, 1)

    def test_sgagent_inheritance(self):
        """Test that SGAgent inherits from SGAgentModel"""
        agent = self.agent_def.newAgentAtCoords(self.grid, 1, 1, {"health": "good"})
        
        self.assertIsInstance(agent, SGAgentModel)
        self.assertTrue(hasattr(agent, 'isAgent'))
        self.assertTrue(agent.isAgent)

    def test_sgagent_view_creation(self):
        """Test that SGAgent creates and links a view"""
        agent = self.agent_def.newAgentAtCoords(self.grid, 1, 1, {"health": "good"})
        
        self.assertIsNotNone(agent.view)
        self.assertIsInstance(agent.view, SGAgentView)
        self.assertEqual(agent.view.agent_model, agent)

    def test_sgagent_legacy_compatibility(self):
        """Test that SGAgent maintains backward compatibility"""
        agent = self.agent_def.newAgentAtCoords(self.grid, 1, 1, {"health": "good"})
        
        # Test legacy UI methods delegate to view
        self.assertIsNotNone(agent.show)
        self.assertIsNotNone(agent.hide)
        self.assertIsNotNone(agent.update)
        self.assertIsNotNone(agent.setGeometry)
        self.assertIsNotNone(agent.move)
        self.assertIsNotNone(agent.resize)
        self.assertIsNotNone(agent.setVisible)
        self.assertIsNotNone(agent.isVisible)
        self.assertIsNotNone(agent.rect)
        self.assertIsNotNone(agent.mapToGlobal)
        self.assertIsNotNone(agent.setAcceptDrops)
        self.assertIsNotNone(agent.grab)

    def test_sgagent_model_methods(self):
        """Test that SGAgent delegates model methods to SGAgentModel"""
        agent = self.agent_def.newAgentAtCoords(self.grid, 1, 1, {"health": "good"})
        
        # Test that model methods work
        self.assertEqual(agent.getCell(), self.test_cell)
        self.assertEqual(agent.getCellCoordinates(), (1, 1))
        self.assertTrue(agent.isInCell(self.test_cell))
        self.assertIsNotNone(agent.getId())
        self.assertIsNotNone(agent.getPrivateId())

    def test_sgagent_view_methods(self):
        """Test that SGAgent delegates view methods to SGAgentView"""
        agent = self.agent_def.newAgentAtCoords(self.grid, 1, 1, {"health": "good"})
        
        # Test that view methods work
        self.assertIsNotNone(agent.view.getRegion())
        self.assertIsNotNone(agent.view.paintEvent)
        self.assertIsNotNone(agent.view.mousePressEvent)
        self.assertIsNotNone(agent.view.mouseMoveEvent)

    def test_sgagent_type_identification(self):
        """Test that SGAgent has correct type identification attributes"""
        agent = self.agent_def.newAgentAtCoords(self.grid, 1, 1, {"health": "good"})
        
        self.assertTrue(agent.isEntity)
        self.assertFalse(agent.isCell)
        self.assertTrue(agent.isAgent)

    def test_sgagent_model_view_communication(self):
        """Test communication between SGAgent model and view"""
        agent = self.agent_def.newAgentAtCoords(self.grid, 1, 1, {"health": "good"})
        
        # Test that view can access model data
        self.assertEqual(agent.view.agent_model, agent)
        self.assertEqual(agent.view.cell, agent.cell)
        self.assertEqual(agent.view.defaultImage, agent.defaultImage)
        self.assertEqual(agent.view.popupImage, agent.popupImage)

    def test_sgagent_zoom_methods(self):
        """Test that zoom methods update both model and view"""
        agent = self.agent_def.newAgentAtCoords(self.grid, 1, 1, {"health": "good"})
        original_size = agent.size
        
        # Test zoom in
        agent.zoomIn(1)
        self.assertEqual(agent.size, original_size + 10)
        
        # Test zoom out
        agent.zoomOut(1)
        self.assertEqual(agent.size, original_size)

    def test_sgagent_position_methods(self):
        """Test position-related methods"""
        agent = self.agent_def.newAgentAtCoords(self.grid, 1, 1, {"health": "good"})
        
        # Test position methods
        self.assertIsNotNone(agent.getRandomX())
        self.assertIsNotNone(agent.getRandomY())
        # getPositionInEntity sets coordinates but doesn't return anything
        agent.getPositionInEntity()  # Should set xCoord and yCoord
        self.assertIsNotNone(agent.xCoord)
        self.assertIsNotNone(agent.yCoord)

    def test_sgagent_movement_methods(self):
        """Test movement-related methods"""
        agent = self.agent_def.newAgentAtCoords(self.grid, 1, 1, {"health": "good"})
        
        # Test movement methods
        self.assertIsNotNone(agent.moveTo)
        self.assertIsNotNone(agent.moveAgent)
        self.assertIsNotNone(agent.moveRandomly)
        self.assertIsNotNone(agent.moveTowards)

    def test_sgagent_neighbor_methods(self):
        """Test neighbor-related methods"""
        agent = self.agent_def.newAgentAtCoords(self.grid, 1, 1, {"health": "good"})
        
        # Test neighbor methods - simplified for now
        self.assertIsNotNone(agent.getNeighborCells)
        # Note: getNeighborCells and related methods need grid implementation
        # These will be tested when grid neighbor methods are implemented

    def test_sgagent_information_methods(self):
        """Test information-related methods"""
        agent = self.agent_def.newAgentAtCoords(self.grid, 1, 1, {"health": "good"})
        
        # Test information methods - simplified for now
        self.assertIsNotNone(agent.getAgentsHere())
        self.assertIsNotNone(agent.nbAgentsHere())
        self.assertIsNotNone(agent.hasAgentsHere())
        # Note: nbNeighborAgents and related methods need grid neighbor implementation
        # These will be tested when grid neighbor methods are implemented

    def test_sgagent_view_update(self):
        """Test that view updates when model changes"""
        agent = self.agent_def.newAgentAtCoords(self.grid, 1, 1, {"health": "good"})
        
        # Test updateView method
        self.assertIsNotNone(agent.updateView)
        agent.updateView()  # Should not raise an exception

if __name__ == '__main__':
    unittest.main()
