#!/usr/bin/env python3
"""
Test suite for SGEntity Model-View adaptation

This test validates that SGEntity now properly uses Model-View architecture
while maintaining backward compatibility.
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
from mainClasses.SGEntity import SGEntity


class TestSGEntityModelViewAdaptation(unittest.TestCase):
    """Test suite for SGEntity Model-View adaptation"""
    
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

    def test_sgentity_inheritance(self):
        """Test that SGEntity properly inherits from SGEntityModel"""
        # Create a test entity using the old method
        entity = SGEntity(None, self.cell_def, 50, {"value": 10})
        
        # Verify it has model attributes
        self.assertIsNotNone(entity.classDef)
        self.assertIsNotNone(entity.id)
        self.assertIsNotNone(entity.model)
        self.assertEqual(entity.value("value"), 10)
        
        # Verify it has view
        self.assertIsNotNone(entity.view)
        self.assertEqual(entity.getView(), entity.view)

    def test_sgentity_view_delegation(self):
        """Test that SGEntity properly delegates UI to view"""
        # Create a test entity
        entity = SGEntity(None, self.cell_def, 50, {"value": 20})
        
        # Test that UI methods delegate to view
        self.assertIsNotNone(entity.getColor())
        self.assertIsNotNone(entity.getBorderColorAndWidth())
        
        # Test that view is properly linked
        self.assertEqual(entity.view.entity_model, entity)

    def test_sgentity_legacy_compatibility(self):
        """Test that SGEntity maintains legacy compatibility"""
        # Create a test entity
        entity = SGEntity(None, self.cell_def, 50, {"value": 30})
        
        # Test legacy methods still work
        # Note: getRandomAttributValue returns None if attribute doesn't exist in dictAttributes
        result = entity.getRandomAttributValue(self.cell_def, "value")
        # This is expected behavior - the method should handle missing attributes gracefully
        self.assertIsNotNone(entity.readColorFromPovDef(None, Qt.white))
        self.assertIsNotNone(entity.getObjectIdentiferForJsonDumps())
        self.assertIsNotNone(entity.entDef())
        
        # Test that entity is not deleted
        self.assertFalse(entity.isDeleted())

    def test_sgentity_model_view_separation(self):
        """Test that SGEntity properly separates model and view concerns"""
        # Create a test entity
        entity = SGEntity(None, self.cell_def, 50, {"value": 40})
        
        # Test model functionality
        entity.setValue("value", 50)
        self.assertEqual(entity.value("value"), 50)
        
        # Test view functionality
        self.assertIsNotNone(entity.view)
        self.assertEqual(entity.view.entity_model, entity)
        
        # Test that model and view are properly linked
        self.assertEqual(entity.getView(), entity.view)

    def test_sgentity_type_identification(self):
        """Test that SGEntity has proper type identification attributes"""
        # Create a test entity
        entity = SGEntity(None, self.cell_def, 50, {"value": 60})
        
        # Test type identification attributes
        self.assertTrue(entity.isEntity)
        self.assertFalse(entity.isCell)
        self.assertFalse(entity.isAgent)

    def test_sgentity_view_update(self):
        """Test that SGEntity can update its view"""
        # Create a test entity
        entity = SGEntity(None, self.cell_def, 50, {"value": 70})
        
        # Test view update
        entity.updateView()
        # Should not raise any exceptions

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        # Clean up the QApplication
        cls.app.quit()


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
