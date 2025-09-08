#!/usr/bin/env python3
"""
Test for square grid neighborhood functionality
Created by a modeler to verify that square cells have proper neighbor access
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mainClasses.SGSGE import *

def test_square_neighborhood_open():
    """
    Test square grid with open boundaries (toroidal)
    All cells should have exactly 8 neighbors (Moore neighborhood)
    """
    print("=== Testing Square Grid with OPEN Boundaries (Toroidal) ===")
    
    # Create Qt application
    monApp = QtWidgets.QApplication([])
    
    # Create model
    model = SGModel(500, 350, windowTitle="Test Square Neighborhood - Open")
    
    # Create cell definition and grid in one step (like in examples)
    cellDef = model.newCellsOnGrid(8, 7, "square", gap=0, size=40, neighborhood='moore', boundaries='open')
    
    print(f"Grid created: 8 rows x 7 columns")
    print(f"Grid type: square")
    print(f"Neighborhood: moore")
    print(f"Boundaries: open")
    
    print("\n=== Testing All Cells Have 8 Neighbors (Toroidal) ===")
    
    # With boundaries='open' (toroidal), ALL cells should have exactly 8 neighbors
    all_cells_have_8_neighbors = True
    cells_with_wrong_count = []
    
    for cell in cellDef.entities:
        neighbors = cell.getNeighborCells()
        neighbor_count = len(neighbors)
        
        if neighbor_count != 8:
            all_cells_have_8_neighbors = False
            cells_with_wrong_count.append((cell.xCoord, cell.yCoord, neighbor_count))
    
    if all_cells_have_8_neighbors:
        print(f"✓ PASS: All {len(cellDef.entities)} cells have exactly 8 neighbors")
    else:
        print(f"✗ FAIL: {len(cells_with_wrong_count)} cells don't have 8 neighbors:")
        for x, y, count in cells_with_wrong_count:
            print(f"  - Cell ({x}, {y}): {count} neighbors")
    
    print("\n=== Testing Specific Cell Examples ===")
    
    # Test specific cells for detailed verification
    test_cells = [
        (4, 4),  # Center cell
        (1, 1),  # Corner cell
        (8, 7),  # Another corner
        (6, 7),  # Edge cell
    ]
    
    for x, y in test_cells:
        cell = cellDef.getCell(x, y)
        if cell:
            neighbors = cell.getNeighborCells()
            neighbor_count = len(neighbors)
            
            print(f"Cell ({x}, {y}):")
            print(f"  - ID: {cell.getId()}")
            print(f"  - Neighbors count: {neighbor_count}")
            print(f"  - Neighbor coords: {[(n.xCoord, n.yCoord) for n in neighbors]}")
            
            # With toroidal boundaries, ALL cells should have 8 neighbors
            expected = 8
            
            if neighbor_count == expected:
                print(f"  ✓ PASS: Expected {expected} neighbors")
            else:
                print(f"  ✗ FAIL: Expected {expected} neighbors, got {neighbor_count}")
        else:
            print(f"Cell ({x}, {y}): NOT FOUND")
    
    print("\n=== Testing Cell ID Consistency ===")
    
    # Test that cellIdFromCoords and getId return consistent values
    test_coords = [(3, 3), (5, 5), (7, 6)]
    
    for x, y in test_coords:
        cell = cellDef.getCell(x, y)
        if cell:
            cell_id_from_method = cell.getId()
            cell_id_from_coords = cellDef.cellIdFromCoords(x, y)
            
            print(f"Cell ({x}, {y}):")
            print(f"  - getId(): {cell_id_from_method}")
            print(f"  - cellIdFromCoords(): {cell_id_from_coords}")
            
            if cell_id_from_method == cell_id_from_coords:
                print(f"  ✓ PASS: IDs are consistent")
            else:
                print(f"  ✗ FAIL: IDs are inconsistent")
        else:
            print(f"Cell ({x}, {y}): NOT FOUND")
    
    print("\n=== Test Complete ===")

def test_square_neighborhood_closed():
    """
    Test square grid with closed boundaries (finite)
    Cells on edges and corners should have fewer neighbors
    """
    print("\n=== Testing Square Grid with CLOSED Boundaries (Finite) ===")
    
    # Create Qt application
    monApp = QtWidgets.QApplication([])
    
    # Create model
    model = SGModel(500, 350, windowTitle="Test Square Neighborhood - Closed")
    
    # Create cell definition and grid in one step (like in examples)
    cellDef = model.newCellsOnGrid(8, 7, "square", gap=0, size=40, neighborhood='moore', boundaries='closed')
    
    print(f"Grid created: 8 rows x 7 columns")
    print(f"Grid type: square")
    print(f"Neighborhood: moore")
    print(f"Boundaries: closed")
    
    print("\n=== Testing Neighbor Counts by Cell Position ===")
    
    # Test specific cells for neighbor count with closed boundaries
    test_cases = [
        # (x, y, expected_count, description)
        (4, 4, 8, "Center cell"),
        (1, 1, 3, "Corner cell (top-left)"),
        (8, 1, 3, "Corner cell (top-right)"),
        (1, 7, 3, "Corner cell (bottom-left)"),
        (8, 7, 3, "Corner cell (bottom-right)"),
        (4, 1, 5, "Top edge cell"),
        (4, 7, 5, "Bottom edge cell"),
        (1, 4, 5, "Left edge cell"),
        (8, 4, 5, "Right edge cell"),
    ]
    
    all_tests_passed = True
    
    for x, y, expected, description in test_cases:
        cell = cellDef.getCell(x, y)
        if cell:
            neighbors = cell.getNeighborCells()
            neighbor_count = len(neighbors)
            
            print(f"{description} ({x}, {y}):")
            print(f"  - Neighbors count: {neighbor_count}")
            print(f"  - Neighbor coords: {[(n.xCoord, n.yCoord) for n in neighbors]}")
            
            if neighbor_count == expected:
                print(f"  ✓ PASS: Expected {expected} neighbors")
            else:
                print(f"  ✗ FAIL: Expected {expected} neighbors, got {neighbor_count}")
                all_tests_passed = False
        else:
            print(f"Cell ({x}, {y}): NOT FOUND")
            all_tests_passed = False
    
    print(f"\n=== Closed Boundaries Test Result ===")
    if all_tests_passed:
        print("✓ PASS: All closed boundary tests passed")
    else:
        print("✗ FAIL: Some closed boundary tests failed")
    
    print("\n=== Test Complete ===")

def test_square_neighborhood_neumann():
    """
    Test square grid with Neumann neighborhood (4 neighbors)
    """
    print("\n=== Testing Square Grid with NEUMANN Neighborhood ===")
    
    # Create Qt application
    monApp = QtWidgets.QApplication([])
    
    # Create model
    model = SGModel(500, 350, windowTitle="Test Square Neighborhood - Neumann")
    
    # Create cell definition and grid in one step (like in examples)
    cellDef = model.newCellsOnGrid(8, 7, "square", gap=0, size=40, neighborhood='neumann', boundaries='open')
    
    print(f"Grid created: 8 rows x 7 columns")
    print(f"Grid type: square")
    print(f"Neighborhood: neumann")
    print(f"Boundaries: open")
    
    print("\n=== Testing All Cells Have 4 Neighbors (Neumann) ===")
    
    # With Neumann neighborhood, ALL cells should have exactly 4 neighbors
    all_cells_have_4_neighbors = True
    cells_with_wrong_count = []
    
    for cell in cellDef.entities:
        neighbors = cell.getNeighborCells()
        neighbor_count = len(neighbors)
        
        if neighbor_count != 4:
            all_cells_have_4_neighbors = False
            cells_with_wrong_count.append((cell.xCoord, cell.yCoord, neighbor_count))
    
    if all_cells_have_4_neighbors:
        print(f"✓ PASS: All {len(cellDef.entities)} cells have exactly 4 neighbors")
    else:
        print(f"✗ FAIL: {len(cells_with_wrong_count)} cells don't have 4 neighbors:")
        for x, y, count in cells_with_wrong_count:
            print(f"  - Cell ({x}, {y}): {count} neighbors")
    
    print("\n=== Test Complete ===")

def test_square_neighborhood():
    """
    Run all square grid tests
    """
    test_square_neighborhood_open()
    test_square_neighborhood_closed()
    test_square_neighborhood_neumann()

if __name__ == "__main__":
    test_square_neighborhood()
