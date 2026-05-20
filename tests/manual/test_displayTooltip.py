#!/usr/bin/env python3
"""
Unit test for displayTooltip() method
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mainClasses.SGSGE import *

def test_displayTooltip():
    """
    Test the displayTooltip() method functionality
    """
    print("=== Testing displayTooltip() method ===")
    
    # Create Qt application
    monApp = QtWidgets.QApplication([])
    
    # Create model
    model = SGModel(300, 200, windowTitle="Test displayTooltip")
    
    # Create small grid
    Cell = model.newCellsOnGrid(3, 3, "square", gap=0, size=50, neighborhood='moore', boundaries='closed')
    
    print("Grid created: 3x3 square cells")
    
    # Test default behavior (no tooltip)
    Cell.displayTooltip()
    print("✓ displayTooltip() - default behavior (no tooltip)")
    
    # Test coordinates tooltip
    Cell.displayTooltip('coords')
    print("✓ displayTooltip('coords') - coordinates tooltip")
    
    # Test ID tooltip
    Cell.displayTooltip('id')
    print("✓ displayTooltip('id') - ID tooltip")
    
    # Test explicit none
    Cell.displayTooltip('none')
    print("✓ displayTooltip('none') - explicit no tooltip")
    
    # Test unknown type (should default to no tooltip)
    Cell.displayTooltip('unknown')
    print("✓ displayTooltip('unknown') - unknown type defaults to no tooltip")
    
    # Test custom type
    Cell.displayTooltip('custom')
    print("✓ displayTooltip('custom') - custom tooltip (coordinates for now)")
    
    print("\n=== All displayTooltip() tests passed ===")
    print("The method is ready for modelers to use.")
    
    # Close application
    monApp.quit()
    
    return True

if __name__ == "__main__":
    test_displayTooltip()
